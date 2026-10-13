"""Plugin registry — name → manifest, version-gated, freeze-once."""
from __future__ import annotations

import asyncio
from collections.abc import Iterable

import structlog

from animator_host.contracts.plugin import PluginManifest

log = structlog.get_logger(__name__)


class PluginConflict(RuntimeError):
    """Raised when two plugins claim the same name or an incompatible API."""


class PluginRegistry:
    def __init__(self, api_version: tuple[int, int]) -> None:
        self._api = api_version
        self._manifests: dict[str, PluginManifest] = {}
        self._frozen = False

    def register(self, manifest: PluginManifest) -> None:
        if self._frozen:
            raise PluginConflict(f"registry frozen; cannot register {manifest.name}")
        if manifest.api_major != self._api[0]:
            log.warning("plugin.api_mismatch", name=manifest.name, plugin_api=manifest.api_major, host_api=self._api[0])
            return
        if manifest.name in self._manifests:
            raise PluginConflict(f"duplicate plugin name: {manifest.name}")
        self._manifests[manifest.name] = manifest

    async def freeze(self) -> None:
        await asyncio.sleep(0)  # yield to allow late imports
        self._frozen = True
        log.info("registry.frozen", count=len(self._manifests))

    def names(self) -> Iterable[str]:
        return tuple(sorted(self._manifests))

    def get(self, name: str) -> PluginManifest:
        try:
            return self._manifests[name]
        except KeyError as exc:
            raise KeyError(f"unknown plugin: {name}") from exc