# Breakout Forge AI Context

## Goal
Breakout Forge is a small reusable breakout-game foundation. It supports normal stages, image-based stages, layered destruction, external stage data, mods, and PyInstaller `--onedir` distribution.

## Source of Truth
1. `DESIGN.md` — product/game architecture and feature intent.
2. GitHub Issues — implementation units and acceptance criteria.
3. Tests — executable behavior for implemented code.
4. Source code — current implementation details.

Do not treat this file as a replacement for the sources above. It is a routing index.

## Architecture Rules (UPD Commander)
The application is separated into `ui`, `process`, and `data` responsibility areas.

- Commander: orchestration only. It selects/calls processing units; it does not contain game/data/rendering logic.
- Messenger: cross-layer communication only. It must not contain game/data/rendering logic.
- Processing: actual calculation, rendering, conversion, loading, persistence, etc.
- UI must not access Data directly.
- Process must not depend on pygame rendering details or persistence format.
- Data must not know UI or game rules.
- Prefer one module/class/function per responsibility where practical.

## Data-Driven Rule
Values that a stage author or user is likely to tune belong outside the program.

- Defaults: `config/common.json`
- Stage-specific overrides: `stages/<stage>/stage.json`
- Resolution: recursively merge stage settings over common settings.
- Missing stage keys inherit common values.
- Keep normal gameplay tuning out of Python constants.

At minimum externalize ball speed, paddle speed/size, board dimensions, image split dimensions, playfield fit, layer HP, and asset paths. New tunable values should default to external data unless there is a strong reason not to.

## Task Routing
- App window/input/rendering: `src/breakout_forge/ui/`
- Game rules/state/update: `src/breakout_forge/process/`
- File/config/stage/mod persistence and settings merge: `src/breakout_forge/data/`
- Cross-layer contracts: `src/breakout_forge/contracts/`
- Common defaults: `config/common.json`
- Stage overrides/content: `stages/<stage>/stage.json`
- Tests: `tests/`
- Product requirements: `DESIGN.md`

## Change Routing
- UI-only change -> UI processing + focused UI tests.
- Game-rule change -> Process processing + focused process tests.
- File/schema/path/settings change -> Data processing + focused data tests.
- Cross-layer contract change -> inspect both adjacent layers and broader tests.
- Packaging change -> source validation + packaged artifact smoke test.

## AI Working Rules
1. Search first, read second; open only the files needed for the task.
2. Establish Goal / Required / Acceptance from the issue or request.
3. Stop exploration once required evidence is sufficient.
4. Do not mix unrelated refactors into the current task.
5. Use the smallest sufficient validation first; broaden only for shared/public contracts.
6. Report unverified areas explicitly.
7. Ignore generated artifacts, logs and history unless required by the task.

## Current State
Foundation work is in progress. The repository is intentionally small; do not introduce heavy indexes, generated call graphs, or duplicated AI documentation until repeated lookup cost justifies them.
