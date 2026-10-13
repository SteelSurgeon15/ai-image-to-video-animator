"""Typer CLI entry: animator run | list | inspect | doctor."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from animator_host import __version__
from animator_host.bootstrap import boot
from animator_host.services.render_service import RenderJob, RenderService

app = typer.Typer(help="ai-image-to-video-animator CLI", no_args_is_help=True)
console = Console()


@app.command()
def version() -> None:
    console.print(f"animator-host {__version__}")


@app.command("list")
def list_plugins() -> None:
    _, registry = asyncio.run(boot())
    table = Table(title="registered plugins")
    table.add_column("name")
    table.add_column("kind")
    table.add_column("api")
    for name in registry.names():
        m = registry.get(name)
        table.add_row(m.name, m.kind, f"{m.api_major}.{m.api_minor}")
    console.print(table)


@app.command()
def run(
    image: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    plugin: Annotated[str, typer.Option("--plugin", "-p")] = "motion_diffusion",
    frames: Annotated[int, typer.Option("--frames", "-f")] = 48,
    out: Annotated[Path, typer.Option("--out", "-o")] = Path("exports/clip.mp4"),
) -> None:
    _, registry = asyncio.run(boot())
    svc = RenderService(registry)
    job = RenderJob(source_image=image, plugin=plugin, frame_count=frames, output=out)
    asyncio.run(svc.execute(job))
    console.print(f"[green]wrote[/] {out}")


if __name__ == "__main__":
    app()