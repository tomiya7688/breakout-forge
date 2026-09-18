"""Resolve external paths for source and PyInstaller onedir execution."""

from __future__ import annotations

from pathlib import Path
import sys

from breakout_forge.contracts.paths import ExternalPaths


class ExternalPathError(ValueError):
    """Raised when the external data layout cannot be prepared."""


def resolve_base_dir(
    *,
    frozen: bool | None = None,
    executable: Path | None = None,
    package_file: Path | None = None,
) -> Path:
    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else frozen
    if is_frozen:
        exe = executable or Path(sys.executable)
        return exe.resolve().parent

    source_file = package_file or Path(__file__)
    # src/breakout_forge/data/processing/path_processing.py -> repository root
    return source_file.resolve().parents[4]


def resolve_external_paths(
    base_dir: Path | None = None,
    *,
    create_userdata: bool = True,
) -> ExternalPaths:
    root = (base_dir or resolve_base_dir()).resolve()
    userdata = root / "userdata"
    if create_userdata:
        try:
            userdata.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ExternalPathError(f"failed to create userdata directory: {userdata}") from exc

    return ExternalPaths(
        base_dir=root,
        config_dir=root / "config",
        assets_dir=root / "assets",
        stages_dir=root / "stages",
        mods_dir=root / "mods",
        userdata_dir=userdata,
        common_settings=root / "config" / "common.json",
        user_settings=userdata / "settings.json",
    )


def require_file(path: Path, description: str) -> Path:
    if not path.is_file():
        raise ExternalPathError(f"{description} not found: {path}")
    return path
