from pathlib import Path

import pytest

from breakout_forge.data.processing.settings_processing import (
    SettingsError,
    resolve_stage_settings,
)


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_stage_overrides_only_selected_common_values(tmp_path: Path) -> None:
    common = _write(
        tmp_path / "common.json",
        '''{
          "format_version": 1,
          "gameplay": {
            "ball_speed": 360.0,
            "paddle_speed": 520.0,
            "paddle_size": {"width": 120, "height": 18}
          },
          "stage_size": {"columns": 20, "rows": 15},
          "break_image": {
            "split": {"columns": 20, "rows": 15},
            "load_mode": "keep_background"
          },
          "playfield": {"fit": "contain"}
        }''',
    )
    stage = _write(
        tmp_path / "stage.json",
        '''{
          "format_version": 1,
          "id": "test",
          "name": "Test",
          "settings": {
            "gameplay": {
              "ball_speed": 420.0,
              "paddle_size": {"width": 160}
            },
            "stage_size": {"columns": 24},
            "break_image": {
              "split": {"rows": 18},
              "load_mode": "remove_background"
            }
          }
        }''',
    )

    resolved = resolve_stage_settings(common, stage)

    assert resolved.gameplay.ball_speed == 420.0
    assert resolved.gameplay.paddle_speed == 520.0
    assert resolved.gameplay.paddle_size.width == 160
    assert resolved.gameplay.paddle_size.height == 18
    assert resolved.stage_size.columns == 24
    assert resolved.stage_size.rows == 15
    assert resolved.break_image.split.columns == 20
    assert resolved.break_image.split.rows == 18
    assert resolved.break_image.load_mode == "remove_background"
    assert resolved.playfield.fit == "contain"


def test_stage_without_settings_uses_common_values(tmp_path: Path) -> None:
    common = _write(
        tmp_path / "common.json",
        '''{
          "format_version": 1,
          "gameplay": {
            "ball_speed": 360,
            "paddle_speed": 520,
            "paddle_size": {"width": 120, "height": 18}
          },
          "stage_size": {"columns": 20, "rows": 15},
          "break_image": {
            "split": {"columns": 20, "rows": 15},
            "load_mode": "keep_background"
          },
          "playfield": {"fit": "contain"}
        }''',
    )
    stage = _write(
        tmp_path / "stage.json",
        '{"format_version": 1, "id": "test", "name": "Test"}',
    )

    resolved = resolve_stage_settings(common, stage)

    assert resolved.gameplay.ball_speed == 360.0
    assert resolved.stage_size.columns == 20
    assert resolved.break_image.split.rows == 15
    assert resolved.break_image.load_mode == "keep_background"


def test_invalid_tunable_value_is_rejected(tmp_path: Path) -> None:
    common = _write(
        tmp_path / "common.json",
        '''{
          "format_version": 1,
          "gameplay": {
            "ball_speed": 0,
            "paddle_speed": 520,
            "paddle_size": {"width": 120, "height": 18}
          },
          "stage_size": {"columns": 20, "rows": 15},
          "break_image": {
            "split": {"columns": 20, "rows": 15},
            "load_mode": "keep_background"
          },
          "playfield": {"fit": "contain"}
        }''',
    )
    stage = _write(
        tmp_path / "stage.json",
        '{"format_version": 1, "id": "test", "name": "Test"}',
    )

    with pytest.raises(SettingsError):
        resolve_stage_settings(common, stage)


def test_invalid_break_image_load_mode_is_rejected(tmp_path: Path) -> None:
    common = _write(
        tmp_path / "common.json",
        '''{
          "format_version": 1,
          "gameplay": {
            "ball_speed": 360,
            "paddle_speed": 520,
            "paddle_size": {"width": 120, "height": 18}
          },
          "stage_size": {"columns": 20, "rows": 15},
          "break_image": {
            "split": {"columns": 20, "rows": 15},
            "load_mode": "unknown"
          },
          "playfield": {"fit": "contain"}
        }''',
    )
    stage = _write(
        tmp_path / "stage.json",
        '{"format_version": 1, "id": "test", "name": "Test"}',
    )

    with pytest.raises(SettingsError):
        resolve_stage_settings(common, stage)
