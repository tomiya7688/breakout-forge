"""Validate repository-owned external data without starting pygame."""

from __future__ import annotations

import argparse
from pathlib import Path

from breakout_forge.data.processing.mod_processing import discover_mods
from breakout_forge.data.processing.settings_processing import resolve_common_settings
from breakout_forge.data.processing.stage_processing import load_stage_definition


def validate_repository_data(project_root: Path) -> None:
    root = project_root.resolve()
    common = root / "config" / "common.json"
    stages_dir = root / "stages"
    mods_dir = root / "mods"

    resolve_common_settings(common)

    if not stages_dir.is_dir():
        raise FileNotFoundError(f"stages directory not found: {stages_dir}")
    for stage_json in sorted(stages_dir.glob("*/stage.json")):
        stage = load_stage_definition(common, stage_json)
        for layer in stage.layers:
            if layer.image_path is not None and not layer.image_path.is_file():
                raise FileNotFoundError(
                    f"stage image not found: stage={stage.id} layer={layer.id} path={layer.image_path}"
                )

    discover_mods(mods_dir)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    validate_repository_data(args.project_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
