from pathlib import Path

from scripts.validate_data import validate_repository_data


def test_repository_data_validation_accepts_minimal_valid_layout(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "stages" / "plain").mkdir(parents=True)
    (tmp_path / "mods").mkdir()
    (tmp_path / "config" / "common.json").write_text(
        """{
          "format_version": 1,
          "display": {"width": 800, "height": 600, "fps": 60, "title": "Test"},
          "gameplay": {
            "ball_speed": 360,
            "ball_size": 14,
            "ball_initial_direction": {"x": 1, "y": -1},
            "paddle_speed": 520,
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
        }""",
        encoding="utf-8",
    )
    (tmp_path / "stages" / "plain" / "stage.json").write_text(
        '{"format_version":1,"id":"plain","name":"Plain"}',
        encoding="utf-8",
    )

    validate_repository_data(tmp_path)
