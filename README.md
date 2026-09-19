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
├─ BreakoutForge.exe    # onedir build only
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

## Windows onedir build

Install development dependencies, then run:

```bat
python -m pip install -e ".[dev]"
build.bat
```

The build script:

1. cleans previous `build/` and `dist/BreakoutForge/` output,
2. runs PyInstaller explicitly with `--onedir`,
3. places Python/runtime dependencies under `_internal/`,
4. copies editable `config/`, `assets/`, `stages/`, and `mods/` beside the executable,
5. creates an empty `userdata/`,
6. runs `BreakoutForge.exe --smoke-test` without opening the pygame window.

Result:

```text
dist/
└─ BreakoutForge/
   ├─ BreakoutForge.exe
   ├─ _internal/
   ├─ config/
   ├─ assets/
   ├─ stages/
   ├─ mods/
   └─ userdata/
```

The external directories are deliberately outside `_internal/` so users can edit or replace stages, assets, configuration, and MODs after distribution. Breakout Forge does not use PyInstaller `--onefile`.


## Continuous integration

GitHub Actions runs three responsibility-separated workflows on push and pull request:

- **CI** (`.github/workflows/ci.yml`) — Python 3.12 setup, `compileall`, lightweight Ruff lint, the full pytest suite, and the source `--smoke-test`.
- **Data Check** (`.github/workflows/data-check.yml`) — focused validator tests plus repository validation for common/stage JSON, referenced image existence and decode, supported image format/split rules, layered-image aspect ratios, MOD manifests, MOD imports, and `setup(api)` registration.
- **Build Check** (`.github/workflows/build-check.yml`) — runs `build.bat` on `windows-latest`, executes the packaged smoke test, checks the onedir boundary, and uploads `dist/BreakoutForge/`.

The stable check names are `CI`, `Data Check`, and `Build Check`, so they can later be used directly by branch protection/rulesets. The Windows artifact is named `breakout-forge-windows-onedir` and retained for 14 days.
