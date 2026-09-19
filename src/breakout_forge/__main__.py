"""Breakout Forge executable entry point."""

from __future__ import annotations

import sys

from breakout_forge.app import create_application
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


def main() -> int:
    if "--smoke-test" in sys.argv[1:]:
        return _smoke_test()
    return create_application().run()


if __name__ == "__main__":
    raise SystemExit(main())
