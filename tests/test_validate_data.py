from pathlib import Path

import pytest

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


def _write_common(root: Path) -> None:
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config" / "common.json").write_text(
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
            "split": {"columns": 2, "rows": 1},
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
    (root / "mods").mkdir(parents=True, exist_ok=True)


def test_data_validation_rejects_missing_stage_image(tmp_path: Path) -> None:
    _write_common(tmp_path)
    stage = tmp_path / "stages" / "missing"
    stage.mkdir(parents=True)
    (stage / "stage.json").write_text(
        """{
          "format_version": 1,
          "id": "missing",
          "name": "Missing",
          "layers": [{"id": "main", "image": "missing.png"}]
        }""",
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="stage image not found"):
        validate_repository_data(tmp_path)


def test_data_validation_rejects_corrupt_stage_image(tmp_path: Path) -> None:
    _write_common(tmp_path)
    stage = tmp_path / "stages" / "corrupt"
    stage.mkdir(parents=True)
    (stage / "stage.json").write_text(
        """{
          "format_version": 1,
          "id": "corrupt",
          "name": "Corrupt",
          "layers": [{"id": "main", "image": "main.png"}]
        }""",
        encoding="utf-8",
    )
    (stage / "main.png").write_bytes(b"not-a-png")

    with pytest.raises(ValueError, match="failed to load image"):
        validate_repository_data(tmp_path)


def test_data_validation_rejects_mod_that_fails_setup(tmp_path: Path) -> None:
    _write_common(tmp_path)
    stages = tmp_path / "stages"
    stages.mkdir(parents=True)
    mod = tmp_path / "mods" / "broken"
    mod.mkdir(parents=True)
    (mod / "mod.json").write_text(
        '{"format_version":1,"id":"broken","name":"Broken","version":"1.0","entry":"main.py"}',
        encoding="utf-8",
    )
    (mod / "main.py").write_text(
        "def setup(api):\n    raise RuntimeError('broken setup')\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="failed to import or register"):
        validate_repository_data(tmp_path)
