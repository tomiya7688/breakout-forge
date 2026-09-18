from pathlib import Path

import pytest

from breakout_forge.data.commander import DataCommander
from breakout_forge.data.messenger import DataMessenger
from breakout_forge.data.processing.stage_processing import StageLoadError, load_stage_definition


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
    "left_margin": 40,
    "right_margin": 40,
    "top_margin": 60,
    "block_area_height": 240,
    "gap_x": 2,
    "gap_y": 2,
    "block_hp": 1,
    "score_per_layer": 100
  },
  "break_image": {
    "split": {"columns": 20, "rows": 15},
    "load_mode": "keep_background"
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


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_load_stage_resolves_common_overrides_and_layers(tmp_path: Path) -> None:
    common = _write(tmp_path / "config" / "common.json", COMMON)
    stage = _write(
        tmp_path / "stages" / "sample" / "stage.json",
        """{
          "format_version": 1,
          "id": "sample",
          "name": "Sample",
          "settings": {
            "gameplay": {"ball_speed": 420.0},
            "stage_size": {"columns": 24},
            "break_image": {"split": {"rows": 18}}
          },
          "layers": [
            {
              "id": "main",
              "image": "main.png",
              "hp": 3,
              "collidable": true,
              "destructible": true,
              "visible": true
            },
            {
              "id": "background",
              "image": "background.png",
              "hp": 1,
              "collidable": false,
              "destructible": false,
              "visible": true
            }
          ]
        }""",
    )

    resolved = load_stage_definition(common, stage)

    assert resolved.id == "sample"
    assert resolved.name == "Sample"
    assert resolved.settings.gameplay.ball_speed == 420.0
    assert resolved.settings.gameplay.paddle_speed == 520.0
    assert resolved.settings.stage_size.columns == 24
    assert resolved.settings.stage_size.rows == 15
    assert resolved.settings.break_image.split.columns == 20
    assert resolved.settings.break_image.split.rows == 18
    assert len(resolved.layers) == 2
    assert resolved.layers[0].hp == 3
    assert resolved.layers[0].image_path == (stage.parent / "main.png").resolve()
    assert resolved.layers[1].collidable is False
    assert resolved.layers[1].destructible is False


def test_layer_defaults_are_applied(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    stage = _write(
        tmp_path / "stage" / "stage.json",
        """{
          "format_version": 1,
          "id": "plain",
          "name": "Plain",
          "layers": [{"id": "main"}]
        }""",
    )

    resolved = load_stage_definition(common, stage)
    layer = resolved.layers[0]

    assert layer.image_path is None
    assert layer.hp == 1
    assert layer.collidable is True
    assert layer.destructible is True
    assert layer.visible is True


def test_data_messenger_routes_stage_load(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    stage = _write(
        tmp_path / "stage" / "stage.json",
        '{"format_version": 1, "id": "routed", "name": "Routed"}',
    )

    resolved = DataMessenger(DataCommander()).load_stage(common, stage)

    assert resolved.id == "routed"


def test_duplicate_layer_ids_are_rejected(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    stage = _write(
        tmp_path / "stage" / "stage.json",
        """{
          "format_version": 1,
          "id": "bad",
          "name": "Bad",
          "layers": [{"id": "same"}, {"id": "same"}]
        }""",
    )

    with pytest.raises(StageLoadError, match="duplicate"):
        load_stage_definition(common, stage)


def test_image_path_cannot_escape_stage_directory(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    stage = _write(
        tmp_path / "stage" / "stage.json",
        """{
          "format_version": 1,
          "id": "bad-path",
          "name": "Bad Path",
          "layers": [{"id": "main", "image": "../outside.png"}]
        }""",
    )

    with pytest.raises(StageLoadError, match="inside the stage directory"):
        load_stage_definition(common, stage)


def test_invalid_layer_hp_is_rejected(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    stage = _write(
        tmp_path / "stage" / "stage.json",
        """{
          "format_version": 1,
          "id": "bad-hp",
          "name": "Bad HP",
          "layers": [{"id": "main", "hp": 0}]
        }""",
    )

    with pytest.raises(StageLoadError, match="positive integer"):
        load_stage_definition(common, stage)


def test_invalid_layer_flag_is_rejected(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    stage = _write(
        tmp_path / "stage" / "stage.json",
        """{
          "format_version": 1,
          "id": "bad-flag",
          "name": "Bad Flag",
          "layers": [{"id": "main", "collidable": "yes"}]
        }""",
    )

    with pytest.raises(StageLoadError, match="boolean"):
        load_stage_definition(common, stage)


def test_unsupported_stage_version_is_rejected(tmp_path: Path) -> None:
    common = _write(tmp_path / "common.json", COMMON)
    stage = _write(
        tmp_path / "stage" / "stage.json",
        '{"format_version": 2, "id": "future", "name": "Future"}',
    )

    with pytest.raises(StageLoadError, match="format_version"):
        load_stage_definition(common, stage)
