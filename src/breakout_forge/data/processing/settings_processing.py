"""Load, merge, validate, and convert external gameplay settings."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from breakout_forge.contracts.settings import (
    BreakImageSettings,
    DisplaySettings,
    GameplaySettings,
    GridSettings,
    PlayfieldSettings,
    ResolvedStageSettings,
    SizeSettings,
    StandardStageSettings,
    VectorSettings,
)


class SettingsError(ValueError):
    """Raised when external settings cannot be resolved safely."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SettingsError(f"failed to read settings: {path}") from exc
    if not isinstance(raw, dict):
        raise SettingsError(f"settings root must be an object: {path}")
    return raw


def _recursive_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _recursive_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _positive_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise SettingsError(f"{name} must be a positive number")
    return float(value)


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SettingsError(f"{name} must be a number")
    return float(value)


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise SettingsError(f"{name} must be a positive integer")
    return value


def _non_negative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SettingsError(f"{name} must be a non-negative integer")
    return value


def _require_mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise SettingsError(f"{key} must be an object")
    return value


def _validate_format_version(raw: dict[str, Any], source_name: str) -> None:
    if raw.get("format_version") != 1:
        raise SettingsError(f"unsupported format_version in {source_name}")


def _convert_resolved_settings(merged: dict[str, Any]) -> ResolvedStageSettings:
    display = _require_mapping(merged, "display")
    gameplay = _require_mapping(merged, "gameplay")
    paddle_size = _require_mapping(gameplay, "paddle_size")
    ball_direction = _require_mapping(gameplay, "ball_initial_direction")
    stage_size = _require_mapping(merged, "stage_size")
    standard_stage = _require_mapping(merged, "standard_stage")
    break_image = _require_mapping(merged, "break_image")
    break_image_split = _require_mapping(break_image, "split")
    playfield = _require_mapping(merged, "playfield")

    title = display.get("title")
    if not isinstance(title, str) or not title.strip():
        raise SettingsError("display.title must be a non-empty string")

    fit = playfield.get("fit")
    if fit not in {"contain", "cover", "stretch"}:
        raise SettingsError("playfield.fit must be contain, cover, or stretch")

    load_mode = break_image.get("load_mode")
    if load_mode not in {"keep_background", "remove_background"}:
        raise SettingsError(
            "break_image.load_mode must be keep_background or remove_background"
        )

    direction_x = _number(ball_direction.get("x"), "gameplay.ball_initial_direction.x")
    direction_y = _number(ball_direction.get("y"), "gameplay.ball_initial_direction.y")
    if direction_x == 0 and direction_y == 0:
        raise SettingsError("gameplay.ball_initial_direction must not be zero")

    return ResolvedStageSettings(
        display=DisplaySettings(
            width=_positive_int(display.get("width"), "display.width"),
            height=_positive_int(display.get("height"), "display.height"),
            fps=_positive_int(display.get("fps"), "display.fps"),
            title=title,
        ),
        gameplay=GameplaySettings(
            ball_speed=_positive_number(gameplay.get("ball_speed"), "gameplay.ball_speed"),
            ball_size=_positive_int(gameplay.get("ball_size"), "gameplay.ball_size"),
            ball_initial_direction=VectorSettings(x=direction_x, y=direction_y),
            paddle_speed=_positive_number(gameplay.get("paddle_speed"), "gameplay.paddle_speed"),
            paddle_size=SizeSettings(
                width=_positive_int(paddle_size.get("width"), "gameplay.paddle_size.width"),
                height=_positive_int(paddle_size.get("height"), "gameplay.paddle_size.height"),
            ),
            paddle_bottom_margin=_positive_int(
                gameplay.get("paddle_bottom_margin"), "gameplay.paddle_bottom_margin"
            ),
        ),
        stage_size=GridSettings(
            columns=_positive_int(stage_size.get("columns"), "stage_size.columns"),
            rows=_positive_int(stage_size.get("rows"), "stage_size.rows"),
        ),
        standard_stage=StandardStageSettings(
            left_margin=_non_negative_int(standard_stage.get("left_margin"), "standard_stage.left_margin"),
            right_margin=_non_negative_int(standard_stage.get("right_margin"), "standard_stage.right_margin"),
            top_margin=_non_negative_int(standard_stage.get("top_margin"), "standard_stage.top_margin"),
            block_area_height=_positive_int(
                standard_stage.get("block_area_height"), "standard_stage.block_area_height"
            ),
            gap_x=_non_negative_int(standard_stage.get("gap_x"), "standard_stage.gap_x"),
            gap_y=_non_negative_int(standard_stage.get("gap_y"), "standard_stage.gap_y"),
            block_hp=_positive_int(standard_stage.get("block_hp"), "standard_stage.block_hp"),
            score_per_layer=_non_negative_int(
                standard_stage.get("score_per_layer"), "standard_stage.score_per_layer"
            ),
        ),
        break_image=BreakImageSettings(
            split=GridSettings(
                columns=_positive_int(break_image_split.get("columns"), "break_image.split.columns"),
                rows=_positive_int(break_image_split.get("rows"), "break_image.split.rows"),
            ),
            load_mode=load_mode,
        ),
        playfield=PlayfieldSettings(
            width=_positive_int(playfield.get("width"), "playfield.width"),
            height=_positive_int(playfield.get("height"), "playfield.height"),
            fit=fit,
        ),
    )


def resolve_common_settings(common_path: Path) -> ResolvedStageSettings:
    common = _read_json(common_path)
    _validate_format_version(common, "common settings")
    return _convert_resolved_settings(common)


def resolve_stage_settings(common_path: Path, stage_path: Path) -> ResolvedStageSettings:
    common = _read_json(common_path)
    stage = _read_json(stage_path)
    _validate_format_version(common, "common settings")
    _validate_format_version(stage, "stage settings")
    stage_settings = stage.get("settings", {})
    if not isinstance(stage_settings, dict):
        raise SettingsError("stage.settings must be an object")
    return _convert_resolved_settings(_recursive_merge(common, stage_settings))
