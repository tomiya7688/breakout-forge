from pathlib import Path

from breakout_forge.data.processing.settings_processing import resolve_runtime_settings


COMMON = """{
  "format_version": 1,
  "display": {"width": 800, "height": 600, "fps": 60, "title": "Breakout Forge"},
  "gameplay": {
    "ball_speed": 360.0,
    "ball_size": 14,
    "ball_initial_direction": {"x": 1.0, "y": -1.0},
    "paddle_speed": 520.0,
    "paddle_size": {"width": 120, "height": 18},
    "paddle_bottom_margin": 36,
    "ball_paddle_gap": 4
  },
  "stage_size": {"columns": 20, "rows": 15},
  "standard_stage": {
    "left_margin": 40, "right_margin": 40, "top_margin": 60,
    "block_area_height": 240, "gap_x": 2, "gap_y": 2,
    "block_hp": 1, "score_per_layer": 100
  },
  "break_image": {
    "split": {"columns": 20, "rows": 15},
    "load_mode": "keep_background",
    "background_tolerance": 16
  },
  "playfield": {"width": 800, "height": 600, "fit": "contain"},
  "appearance": {
    "background_rgb": [16, 18, 24],
    "block_rgb": [110, 170, 230],
    "paddle_rgb": [230, 230, 230],
    "ball_rgb": [230, 230, 230],
    "text_rgb": [230, 230, 230],
    "overlay_font_size": 36,
    "score_font_size": 28
  }
}"""


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_runtime_settings_merge_common_user_then_stage(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    user = _write(
        tmp_path / "userdata" / "settings.json",
        """{
          "format_version": 1,
          "settings": {
            "display": {"width": 1280},
            "gameplay": {"ball_speed": 400.0}
          }
        }""",
    )
    stage = _write(
        tmp_path / "stage.json",
        """{
          "format_version": 1,
          "settings": {
            "gameplay": {"ball_speed": 500.0},
            "stage_size": {"columns": 30}
          }
        }""",
    )

    resolved = resolve_runtime_settings(
        common,
        user_path=user,
        stage_path=stage,
    )

    assert resolved.display.width == 1280
    assert resolved.display.height == 600
    assert resolved.gameplay.ball_speed == 500.0
    assert resolved.stage_size.columns == 30
    assert resolved.stage_size.rows == 15


def test_missing_user_settings_file_is_optional(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)

    resolved = resolve_runtime_settings(
        common,
        user_path=tmp_path / "userdata" / "settings.json",
    )

    assert resolved.display.width == 800
    assert resolved.gameplay.ball_speed == 360.0
