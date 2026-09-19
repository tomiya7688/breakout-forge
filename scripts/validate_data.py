"""Validate repository-owned external data without starting pygame."""

from __future__ import annotations

import argparse
from pathlib import Path

from breakout_forge.data.processing.image_processing import prepare_image_asset
from breakout_forge.data.processing.mod_processing import discover_mods, load_and_register_mods
from breakout_forge.modding.api import ModApi
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
        image_assets = []
        for layer in stage.layers:
            if layer.image_path is None:
                continue
            if not layer.image_path.is_file():
                raise FileNotFoundError(
                    f"stage image not found: stage={stage.id} layer={layer.id} path={layer.image_path}"
                )
            image_assets.append(
                prepare_image_asset(layer, stage.settings.break_image)
            )

        if len(image_assets) > 1:
            reference = image_assets[0]
            for asset in image_assets[1:]:
                if asset.width * reference.height != reference.width * asset.height:
                    raise ValueError(
                        "layered stage images must share one aspect ratio: "
                        f"stage={stage.id} base={reference.id} other={asset.id}"
                    )

    discovered_mods = discover_mods(mods_dir)
    loaded_mods = load_and_register_mods(mods_dir, ModApi())
    if [mod.id for mod in loaded_mods] != [mod.id for mod in discovered_mods]:
        raise RuntimeError("one or more repository MODs failed to import or register")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    validate_repository_data(args.project_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
