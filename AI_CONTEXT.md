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

At minimum externalize ball speed, paddle speed/size, stage_size, break_image.split, image load mode/background tolerance, playfield fit, layer HP, and asset paths. stage_size is the whole logical stage size; break_image.split is the destructible source-image split and must not be conflated with stage_size or display resolution. New tunable values should default to external data unless there is a strong reason not to.

## Task Routing
- App window/input/rendering: `src/breakout_forge/ui/`
- Game rules/state/update: `src/breakout_forge/process/`
- File/config/stage/mod persistence and settings merge: `src/breakout_forge/data/`
- Cross-layer contracts: `src/breakout_forge/contracts/`
- Common defaults: `config/common.json`
- Optional user overrides: `userdata/settings.json`
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
A playable standard Breakout path and a single-image destructible stage path exist. Data decodes PNG/JPEG/WebP, optionally removes corner-connected background, and prepares RGBA assets. Process builds the image destruction Board from break_image.split, while UI renders source-rect tiles from the prepared source asset. Multi-layer image stages are implemented: stage layers are bottom-to-top, each Cell shows/collides with the top active layer, and differing image resolutions are allowed only when aspect ratio matches. Python MOD loading is implemented through mods/<mod>/mod.json + entry setup(api), with public event subscriptions and per-MOD/handler error isolation. MODs are unsandboxed and must be treated as trusted code.

External paths are cwd-independent: source execution resolves the repository root from package location, while PyInstaller onedir resolves from the executable directory. userdata is created automatically; settings precedence is common -> user -> stage.

Windows packaging uses build.bat + PyInstaller --onedir. Runtime dependencies belong under dist/BreakoutForge/_internal while config/assets/stages/mods/userdata stay editable beside BreakoutForge.exe. The packaged executable supports --smoke-test for headless layout validation.

CI is split into three workflows with stable check names: CI, Data Check, and Build Check. CI compiles/lints/tests/smoke-tests source; Data Check validates and decodes stage assets plus imports/registers repository MODs and includes negative validator tests; Build Check runs build.bat on Windows and uploads dist/BreakoutForge.

User-facing stage selection is available through `--stage <id|path>`, where a simple id resolves to `stages/<id>/stage.json`. README is the primary user guide for running the game, creating standard/image/layered stages, and installing MODs.

Formal releases must use the separate Release Gate, not ordinary CI alone. It reruns full regression on Linux and Windows, builds the actual onedir artifact, checks machine-readable packaged I/O, re-extracts and retests the ZIP, verifies SHA-256, and only then publishes a tag-triggered GitHub Release. Version SSoT is breakout_forge.__version__.

The repository is intentionally small; do not introduce heavy indexes, generated call graphs, or duplicated AI documentation until repeated lookup cost justifies them.
