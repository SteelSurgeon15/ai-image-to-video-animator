"""Discover plugins via the `animator.plugins` entry-point group."""
from __future__ import annotations

from importlib.metadata import entry_points

import structlog

from animator_host.contracts.plugin import PluginManifest

log = structlog.get_logger(__name__)

GROUP = "animator.plugins"


def scan_entrypoints() -> list[PluginManifest]:
    found: list[PluginManifest] = []
    for ep in entry_points(group=GROUP):
        try:
            factory = ep.load()
            manifest = getattr(factory, "MANIFEST", None) or factory().manifest
        except Exception as exc:  # noqa: BLE001 — plugin isolation
            log.error("entrypoint.load_failed", ep=ep.name, error=str(exc))
            continue
        found.append(manifest)
    return found