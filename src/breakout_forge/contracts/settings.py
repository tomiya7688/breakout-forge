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
class DisplaySettings:
    width: int
    height: int
    fps: int
    title: str


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
    display: DisplaySettings
    gameplay: GameplaySettings
    stage_size: GridSettings
    break_image: BreakImageSettings
    playfield: PlayfieldSettings
