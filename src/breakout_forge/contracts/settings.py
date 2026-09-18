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
    ball_paddle_gap: int = 4


@dataclass(frozen=True, slots=True)
class StandardStageSettings:
    left_margin: int
    right_margin: int
    top_margin: int
    block_area_height: int
    gap_x: int
    gap_y: int
    block_hp: int
    score_per_layer: int


@dataclass(frozen=True, slots=True)
class AppearanceSettings:
    background_rgb: tuple[int, int, int]
    block_rgb: tuple[int, int, int]
    paddle_rgb: tuple[int, int, int]
    ball_rgb: tuple[int, int, int]
    text_rgb: tuple[int, int, int]
    overlay_font_size: int
    score_font_size: int


@dataclass(frozen=True, slots=True)
class BreakImageSettings:
    split: GridSettings
    load_mode: str
    background_tolerance: int


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
    standard_stage: StandardStageSettings
    appearance: AppearanceSettings
    break_image: BreakImageSettings
    playfield: PlayfieldSettings
