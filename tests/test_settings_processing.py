from pathlib import Path

import pytest

from breakout_forge.data.processing.settings_processing import (
    SettingsError,
    resolve_common_settings,
    resolve_stage_settings,
)


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


COMMON = '''{
  "format_version": 1,
  "display": {"width": 800, "height": 600, "fps": 60, "title": "Breakout Forge"},
  "gameplay": {
    "ball_speed": 360.0,
    "ball_size": 14,
    "ball_initial_direction": {"x": 0.70710678, "y": -0.70710678},
    "paddle_speed": 520.0,
    "paddle_size": {"width": 120, "height": 18},
    "paddle_bottom_margin": 36
  },
  "stage_size": {"columns": 20, "rows": 15},
  "break_image": {
    "split": {"columns": 20, "rows": 15},
    "load_mode": "keep_background"
  },
  "playfield": {"width": 800, "height": 600, "fit": "contain"}
}'''


def test_stage_overrides_only_selected_common_values(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    stage = _write(
        tmp_path / "stage.json",
        '''{
          "format_version": 1,
          "id": "test",
          "name": "Test",
          "settings": {
            "display": {"width": 1280},
            "gameplay": {
              "ball_speed": 420.0,
              "ball_size": 16,
              "paddle_size": {"width": 160}
            },
            "stage_size": {"columns": 24},
            "break_image": {
              "split": {"rows": 18},
              "load_mode": "remove_background"
            },
            "playfield": {"width": 1000}
          }
        }''',
    )

    resolved = resolve_stage_settings(common, stage)

    assert resolved.display.width == 1280
    assert resolved.display.height == 600
    assert resolved.gameplay.ball_speed == 420.0
    assert resolved.gameplay.ball_size == 16
    assert resolved.gameplay.paddle_speed == 520.0
    assert resolved.gameplay.paddle_size.width == 160
    assert resolved.gameplay.paddle_size.height == 18
    assert resolved.gameplay.paddle_bottom_margin == 36
    assert resolved.stage_size.columns == 24
    assert resolved.stage_size.rows == 15
    assert resolved.break_image.split.columns == 20
    assert resolved.break_image.split.rows == 18
    assert resolved.break_image.load_mode == "remove_background"
    assert resolved.playfield.width == 1000
    assert resolved.playfield.height == 600
    assert resolved.playfield.fit == "contain"


def test_common_settings_are_resolved_without_stage(tmp_path: Path) -> None:
    resolved = resolve_common_settings(_write(tmp_path / "common.json", COMMON))

    assert resolved.display.width == 800
    assert resolved.display.height == 600
    assert resolved.display.fps == 60
    assert resolved.display.title == "Breakout Forge"
    assert resolved.gameplay.ball_size == 14
    assert resolved.gameplay.ball_initial_direction.x > 0
    assert resolved.gameplay.ball_initial_direction.y < 0
    assert resolved.stage_size.columns == 20
    assert resolved.break_image.split.rows == 15
    assert resolved.playfield.width == 800


def test_stage_without_settings_uses_common_values(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    stage = _write(
        tmp_path / "stage.json",
        '{"format_version": 1, "id": "test", "name": "Test"}',
    )

    resolved = resolve_stage_settings(common, stage)

    assert resolved.gameplay.ball_speed == 360.0
    assert resolved.gameplay.ball_size == 14
    assert resolved.stage_size.columns == 20
    assert resolved.break_image.load_mode == "keep_background"


def test_invalid_tunable_value_is_rejected(tmp_path: Path) -> None:
    common = _write(
        tmp_path / "common.json",
        COMMON.replace('"ball_speed": 360.0', '"ball_speed": 0'),
    )
    stage = _write(
        tmp_path / "stage.json",
        '{"format_version": 1, "id": "test", "name": "Test"}',
    )

    with pytest.raises(SettingsError):
        resolve_stage_settings(common, stage)


def test_zero_initial_ball_direction_is_rejected(tmp_path: Path) -> None:
    common = _write(
        tmp_path / "common.json",
        COMMON.replace(
            '"ball_initial_direction": {"x": 0.70710678, "y": -0.70710678}',
            '"ball_initial_direction": {"x": 0, "y": 0}',
        ),
    )

    with pytest.raises(SettingsError):
        resolve_common_settings(common)
