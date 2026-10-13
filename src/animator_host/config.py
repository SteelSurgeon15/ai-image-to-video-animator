"""Host config — TOML-backed, pydantic-validated."""
from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "default.toml"


class HostConfig(BaseModel):
    host_version: str = "0.9.2"
    host_api_version: tuple[int, int] = (0, 9)
    log_level: str = Field(default="info", pattern="^(debug|info|warning|error)$")
    extensions_dir: Path = Path("extensions")
    max_workers: int = Field(default=4, ge=1, le=64)
    frame_cache_mb: int = Field(default=2048, ge=128)
    sandbox: bool = False


def load_config(path: Path | None = None) -> HostConfig:
    raw = path or DEFAULT_CONFIG
    if not raw.exists():
        return HostConfig()
    with raw.open("rb") as fh:
        return HostConfig.model_validate(tomllib.load(fh))