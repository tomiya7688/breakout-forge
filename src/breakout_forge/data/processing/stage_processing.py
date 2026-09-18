"""Load and validate stage metadata, layer definitions, and asset paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from breakout_forge.contracts.stage import ResolvedStageDefinition, StageLayerDefinition
from breakout_forge.data.processing.settings_processing import (
    SettingsError,
    resolve_stage_settings,
)


class StageLoadError(ValueError):
    """Raised when a stage definition cannot be loaded safely."""


def _read_stage_json(stage_path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(stage_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StageLoadError(f"failed to read stage: {stage_path}") from exc
    if not isinstance(raw, dict):
        raise StageLoadError("stage root must be an object")
    if raw.get("format_version") != 1:
        raise StageLoadError("unsupported stage format_version")
    return raw


def _non_empty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StageLoadError(f"{name} must be a non-empty string")
    return value


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise StageLoadError(f"{name} must be a positive integer")
    return value


def _bool(value: Any, name: str, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise StageLoadError(f"{name} must be boolean")
    return value


def _resolve_image_path(stage_dir: Path, value: Any, name: str) -> Path | None:
    if value is None:
        return None
    relative = _non_empty_string(value, name)
    path = (stage_dir / relative).resolve()
    stage_root = stage_dir.resolve()
    try:
        path.relative_to(stage_root)
    except ValueError as exc:
        raise StageLoadError(f"{name} must remain inside the stage directory") from exc
    return path


def load_stage_definition(
    common_path: Path,
    stage_path: Path,
) -> ResolvedStageDefinition:
    """Resolve common/stage settings plus stage metadata and layers."""

    raw = _read_stage_json(stage_path)
    stage_dir = stage_path.parent

    try:
        settings = resolve_stage_settings(common_path, stage_path)
    except SettingsError as exc:
        raise StageLoadError(str(exc)) from exc

    stage_id = _non_empty_string(raw.get("id"), "stage.id")
    name = _non_empty_string(raw.get("name"), "stage.name")

    raw_layers = raw.get("layers", [])
    if not isinstance(raw_layers, list):
        raise StageLoadError("stage.layers must be an array")

    seen_ids: set[str] = set()
    layers: list[StageLayerDefinition] = []
    for index, raw_layer in enumerate(raw_layers):
        if not isinstance(raw_layer, dict):
            raise StageLoadError(f"stage.layers[{index}] must be an object")

        layer_id = _non_empty_string(raw_layer.get("id"), f"stage.layers[{index}].id")
        if layer_id in seen_ids:
            raise StageLoadError(f"duplicate stage layer id: {layer_id}")
        seen_ids.add(layer_id)

        layers.append(
            StageLayerDefinition(
                id=layer_id,
                image_path=_resolve_image_path(
                    stage_dir,
                    raw_layer.get("image"),
                    f"stage.layers[{index}].image",
                ),
                hp=_positive_int(raw_layer.get("hp", 1), f"stage.layers[{index}].hp"),
                collidable=_bool(
                    raw_layer.get("collidable"),
                    f"stage.layers[{index}].collidable",
                    True,
                ),
                destructible=_bool(
                    raw_layer.get("destructible"),
                    f"stage.layers[{index}].destructible",
                    True,
                ),
                visible=_bool(
                    raw_layer.get("visible"),
                    f"stage.layers[{index}].visible",
                    True,
                ),
            )
        )

    return ResolvedStageDefinition(
        id=stage_id,
        name=name,
        directory=stage_dir.resolve(),
        settings=settings,
        layers=tuple(layers),
    )
