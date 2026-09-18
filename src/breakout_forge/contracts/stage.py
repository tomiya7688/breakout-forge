"""Transport-only resolved stage definition contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from breakout_forge.contracts.settings import ResolvedStageSettings


@dataclass(frozen=True, slots=True)
class StageLayerDefinition:
    id: str
    image_path: Path | None
    hp: int
    collidable: bool
    destructible: bool
    visible: bool


@dataclass(frozen=True, slots=True)
class ResolvedStageDefinition:
    id: str
    name: str
    directory: Path
    settings: ResolvedStageSettings
    layers: tuple[StageLayerDefinition, ...]
