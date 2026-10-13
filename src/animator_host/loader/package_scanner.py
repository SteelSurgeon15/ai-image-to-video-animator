"""Scan a local extensions/ dir for pyproject-declared plugins (dev mode)."""
from __future__ import annotations

import tomllib
from pathlib import Path

import structlog

from animator_host.contracts.plugin import PluginManifest

log = structlog.get_logger(__name__)


def scan_extensions_dir(root: Path) -> list[PluginManifest]:
    if not root.is_dir():
        return []
    out: list[PluginManifest] = []
    for child in sorted(root.iterdir()):
        pyproject = child / "pyproject.toml"
        if not pyproject.is_file() or child.name.startswith(("_", ".")):
            continue
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            meta = data["tool"]["animator"]["plugin"]
        except (KeyError, tomllib.TOMLDecodeError) as exc:
            log.warning("extensions.skip", path=str(child), reason=str(exc))
            continue
        out.append(PluginManifest.model_validate(meta))
    return out