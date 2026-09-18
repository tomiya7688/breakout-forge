from pathlib import Path

import pytest

from breakout_forge.data.processing.path_processing import (
    ExternalPathError,
    require_file,
    resolve_base_dir,
    resolve_external_paths,
)


def test_source_base_dir_is_derived_from_package_location(tmp_path: Path) -> None:
    package_file = (
        tmp_path
        / "project"
        / "src"
        / "breakout_forge"
        / "data"
        / "processing"
        / "path_processing.py"
    )

    resolved = resolve_base_dir(frozen=False, package_file=package_file)

    assert resolved == (tmp_path / "project").resolve()


def test_frozen_base_dir_is_executable_parent(tmp_path: Path) -> None:
    executable = tmp_path / "dist" / "BreakoutForge" / "breakout-forge.exe"

    resolved = resolve_base_dir(frozen=True, executable=executable)

    assert resolved == executable.resolve().parent


def test_external_paths_use_one_shared_base_and_create_userdata(tmp_path: Path) -> None:
    paths = resolve_external_paths(tmp_path / "game")

    assert paths.base_dir == (tmp_path / "game").resolve()
    assert paths.config_dir == paths.base_dir / "config"
    assert paths.assets_dir == paths.base_dir / "assets"
    assert paths.stages_dir == paths.base_dir / "stages"
    assert paths.mods_dir == paths.base_dir / "mods"
    assert paths.userdata_dir == paths.base_dir / "userdata"
    assert paths.common_settings == paths.config_dir / "common.json"
    assert paths.user_settings == paths.userdata_dir / "settings.json"
    assert paths.userdata_dir.is_dir()


def test_stage_json_path_is_rooted_in_external_stages_dir(tmp_path: Path) -> None:
    paths = resolve_external_paths(tmp_path)

    assert paths.stage_json("sample") == tmp_path.resolve() / "stages" / "sample" / "stage.json"


def test_require_file_has_clear_missing_file_error(tmp_path: Path) -> None:
    missing = tmp_path / "config" / "common.json"

    with pytest.raises(ExternalPathError, match="common settings not found"):
        require_file(missing, "common settings")
