# Breakout Forge

Breakout Forge is a small extensible breakout-game foundation built with Python and pygame. The project is designed to grow from a simple playable breakout game into image-based stages, layered destruction, external stage definitions and Python mods.

## Development setup

Requires Python 3.12 or later.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
python -m breakout_forge
```

The current foundation opens a minimal pygame window. Gameplay is implemented incrementally by the repository Issues.

## Architecture

Breakout Forge adopts UPD Commander principles:

- `ui/` — input, rendering and presentation
- `process/` — game rules and state transitions
- `data/` — external files, configuration and persistence
- `contracts/` — transport-only values across layer boundaries

Commanders orchestrate, Messengers carry cross-layer requests, and Processing units perform the actual work.

See:

- [`DESIGN.md`](DESIGN.md) — feature/product design
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — UPD layer and responsibility rules
- [`AI_CONTEXT.md`](AI_CONTEXT.md) — compact AI task-routing entry point

## Distribution direction

Windows distribution will use PyInstaller `--onedir` so stages, assets and mods can remain externally replaceable. Packaging is implemented in a later Issue.
