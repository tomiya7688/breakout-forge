"""Framework-neutral gameplay snapshots shared across layers."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RectSnapshot:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True, slots=True)
class BallSnapshot:
    x: float
    y: float
    size: float


@dataclass(frozen=True, slots=True)
class BlockSnapshot:
    column: int
    row: int
    rect: RectSnapshot


@dataclass(frozen=True, slots=True)
class GameplaySnapshot:
    paddle: RectSnapshot
    balls: tuple[BallSnapshot, ...]
    playfield_width: float
    playfield_height: float
    blocks: tuple[BlockSnapshot, ...] = ()
    score: int = 0
