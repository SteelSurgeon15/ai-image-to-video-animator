"""Host bootstrap: config load, logging, plugin discovery, registry freeze."""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import structlog

from animator_host.config import HostConfig, load_config
from animator_host.loader.entrypoint_scanner import scan_entrypoints
from animator_host.loader.package_scanner import scan_extensions_dir
from animator_host.registry import PluginRegistry

log = structlog.get_logger(__name__)


def _configure_logging(level: str) -> None:
    logging.basicConfig(stream=sys.stderr, level=level.upper(), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty()),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level.upper())),
    )


async def boot(config_path: Path | None = None) -> tuple[HostConfig, PluginRegistry]:
    cfg = load_config(config_path)
    _configure_logging(cfg.log_level)
    log.info("host.boot", version=cfg.host_version, extensions_dir=str(cfg.extensions_dir))

    registry = PluginRegistry(api_version=cfg.host_api_version)
    for manifest in scan_entrypoints():
        registry.register(manifest)
    for manifest in scan_extensions_dir(cfg.extensions_dir):
        registry.register(manifest)

    await registry.freeze()
    log.info("host.ready", plugins=registry.names())
    return cfg, registry


def main() -> int:
    try:
        asyncio.run(boot())
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())