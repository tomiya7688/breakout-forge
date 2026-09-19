"""Breakout Forge executable entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from breakout_forge import __version__
from breakout_forge.app import create_application
from breakout_forge.data.commander import DataCommander
from breakout_forge.data.messenger import DataMessenger
from breakout_forge.data.processing.path_processing import (
    require_file,
    resolve_external_paths,
)


def _smoke_test() -> int:
    """Validate the frozen/source external-data layout without opening pygame."""

    paths = resolve_external_paths()
    require_file(paths.common_settings, "common settings")
    if not paths.stages_dir.is_dir():
        raise RuntimeError(f"stages directory not found: {paths.stages_dir}")
    if not paths.mods_dir.is_dir():
        raise RuntimeError(f"mods directory not found: {paths.mods_dir}")
    if not paths.assets_dir.is_dir():
        raise RuntimeError(f"assets directory not found: {paths.assets_dir}")
    if not paths.userdata_dir.is_dir():
        raise RuntimeError(f"userdata directory not found: {paths.userdata_dir}")
    return 0


def _stage_argument(value: str) -> Path:
    candidate = Path(value)
    if candidate.suffix.lower() == ".json" or "/" in value or "\" in value:
        return candidate
    return Path("stages") / value / "stage.json"


def _validate_stage(stage_path: Path) -> int:
    """Load a stage and all referenced images without opening pygame."""

    data = DataMessenger(DataCommander())
    paths = data.resolve_paths()
    stage_file = paths.resolve(stage_path)
    data.require_file(paths.common_settings, "common settings")
    data.require_file(stage_file, "stage definition")

    stage = data.load_stage(
        paths.common_settings,
        stage_file,
        paths.user_settings,
    )
    for layer in stage.layers:
        if layer.image_path is not None:
            data.prepare_image(layer, stage.settings.break_image)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="BreakoutForge")
    parser.add_argument(
        "--stage",
        type=_stage_argument,
        help="Stage id (for stages/<id>/stage.json) or a stage.json path.",
    )
    parser.add_argument(
        "--validate-stage",
        type=_stage_argument,
        help="Load and validate one stage without opening pygame.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Validate the external distribution layout without opening pygame.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args(argv)

    if args.smoke_test:
        return _smoke_test()
    if args.validate_stage is not None:
        return _validate_stage(args.validate_stage)
    return create_application(stage_path=args.stage).run()


if __name__ == "__main__":
    raise SystemExit(main())
