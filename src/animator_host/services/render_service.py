"""Render orchestration: resolve plugin → warmup → render → encode → write."""
from __future__ import annotations

import asyncio
from pathlib import Path

import structlog
from pydantic import BaseModel

from animator_host.contracts.plugin import AnimatorPlugin, FrameBatch, FrameRequest
from animator_host.registry import PluginRegistry
from animator_host.utils.frames import encode_mp4

log = structlog.get_logger(__name__)


class RenderJob(BaseModel):
    source_image: Path
    plugin: str
    frame_count: int
    fps: int = 24
    output: Path
    prompt: str | None = None
    seed: int | None = None


class RenderService:
    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    async def _instantiate(self, name: str) -> AnimatorPlugin:
        manifest = self._registry.get(name)
        module_path, _, attr = manifest.entrypoint.partition(":")
        module = __import__(module_path, fromlist=[attr])
        return getattr(module, attr)()

    async def execute(self, job: RenderJob) -> FrameBatch:
        plugin = await self._instantiate(job.plugin)
        await plugin.warmup()
        try:
            req = FrameRequest(
                source_image=job.source_image,
                frame_count=job.frame_count,
                fps=job.fps,
                prompt=job.prompt,
                seed=job.seed,
            )
            log.info("render.start", plugin=job.plugin, frames=job.frame_count)
            batch = await plugin.render(req)
        finally:
            await plugin.shutdown()

        job.output.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(encode_mp4, batch, job.output)
        log.info("render.done", output=str(job.output), bytes=sum(len(f) for f in batch.frames))
        return batch