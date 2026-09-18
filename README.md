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

The project now includes standard Breakout gameplay, image/layer stages, external stage data, and Python MOD events.

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

## External data layout

Source execution resolves the repository root from the installed package location rather than the current working directory. PyInstaller `--onedir` execution resolves the directory containing the executable.

Both use the same external layout:

```text
BreakoutForge/
├─ breakout-forge.exe   # onedir build only
├─ config/
│  ├─ common.json
│  └─ user.example.json
├─ assets/
├─ stages/
├─ mods/
└─ userdata/
   └─ settings.json     # optional, user-created
```

`userdata/` is created automatically when needed. `userdata/settings.json` is optional and uses the same partial `settings` object shape as stage overrides.

Settings precedence is:

```text
config/common.json
    ↓
userdata/settings.json
    ↓
stages/<stage>/stage.json
```

A stage-specific value therefore overrides a global user value, while missing keys continue to inherit.

Explicit relative paths passed to the application are resolved from the external base directory, not from the process current working directory.

## Distribution direction

Windows distribution uses PyInstaller `--onedir` so `config/`, `assets/`, `stages/`, `mods/` and `userdata/` remain outside the executable and can be replaced or edited. Packaging itself is implemented in the next Issue.
