"""Shared plugin contract. Every extension implements AnimatorPlugin."""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9_]{2,48}$")
    kind: Literal["motion", "interp", "upscale", "encode", "controller"]
    api_major: int
    api_minor: int
    version: str
    entrypoint: str
    description: str = ""


class FrameRequest(BaseModel):
    source_image: Path
    frame_count: int = Field(ge=1, le=600)
    fps: int = Field(default=24, ge=1, le=120)
    prompt: str | None = None
    seed: int | None = None


class FrameBatch(BaseModel):
    frames: list[bytes]
    width: int
    height: int
    fps: int


@runtime_checkable
class AnimatorPlugin(Protocol):
    manifest: PluginManifest

    async def warmup(self) -> None: ...

    async def render(self, request: FrameRequest) -> FrameBatch: ...

    async def shutdown(self) -> None: ...