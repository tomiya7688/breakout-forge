"""Cross-layer contracts for resolved external settings."""

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
class VectorSettings:
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class DisplaySettings:
    width: int
    height: int
    fps: int
    title: str


@dataclass(frozen=True, slots=True)
class GameplaySettings:
    ball_speed: float
    ball_size: int
    ball_initial_direction: VectorSettings
    paddle_speed: float
    paddle_size: SizeSettings
    paddle_bottom_margin: int


@dataclass(frozen=True, slots=True)
class BreakImageSettings:
    split: GridSettings
    load_mode: str


@dataclass(frozen=True, slots=True)
class PlayfieldSettings:
    width: int
    height: int
    fit: str


@dataclass(frozen=True, slots=True)
class ResolvedStageSettings:
    display: DisplaySettings
    gameplay: GameplaySettings
    stage_size: GridSettings
    break_image: BreakImageSettings
    playfield: PlayfieldSettings
