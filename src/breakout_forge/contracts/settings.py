"""Cross-layer contracts for resolved gameplay settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SizeSettings:
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class GridSettings:
    columns: int
    rows: int


@dataclass(frozen=True, slots=True)
class GameplaySettings:
    ball_speed: float
    paddle_speed: float
    paddle_size: SizeSettings


@dataclass(frozen=True, slots=True)
class BreakImageSettings:
    split: GridSettings
    load_mode: str


@dataclass(frozen=True, slots=True)
class PlayfieldSettings:
    fit: str


@dataclass(frozen=True, slots=True)
class ResolvedStageSettings:
    gameplay: GameplaySettings
    stage_size: GridSettings
    break_image: BreakImageSettings
    playfield: PlayfieldSettings
