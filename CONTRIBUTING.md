# Contributing to ai-image-to-video-animator

Thanks for wanting to push pixels. This repo is a Windows desktop plugin
host for AI-driven image-to-video animation. Core host stays small; the
interesting work lives in `extensions/`.

## Dev setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pip install -e extensions\motion_diffusion
pre-commit install
```

## Repo layout

- `src/animator_host/` — the plugin host. Loader, registry, contracts, CLI.
- `extensions/` — drop-in plugin packages. Each owns its own `pyproject.toml`.
- `contracts/` — shared JSON schemas + protobufs for cross-language extensions.
- `tests/` — pytest suites. Plugin authors must add an integration test.

## Adding an extension

1. Copy `extensions/_template/` to `extensions/<your_plugin>/`.
2. Implement `AnimatorPlugin` from `src/animator_host/contracts/plugin.py`.
3. Declare entry point `animator.plugins` in your `pyproject.toml`.
4. Add a fixture image to `tests/fixtures/` and an integration test.

## Style

- `ruff` + `black`, line length 100.
- Type annotations required on public functions.
- No blocking calls in the render loop — use `asyncio.to_thread`.

## PR checklist

- [ ] `pytest -q` green
- [ ] `ruff check .` clean
- [ ] New extension registered in `docs/PLUGIN_MATRIX.md`
- [ ] Changelog entry under `## Unreleased`