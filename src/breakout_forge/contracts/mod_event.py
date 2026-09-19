"""Public framework-neutral MOD event contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ModEventName(StrEnum):
    GAME_START = "on_game_start"
    GAME_UPDATE = "on_game_update"
    STAGE_LOADED = "on_stage_loaded"
    BALL_HIT_PADDLE = "on_ball_hit_paddle"
    BLOCK_HIT = "on_block_hit"
    LAYER_DESTROYED = "on_layer_destroyed"
    CELL_DESTROYED = "on_cell_destroyed"
    STAGE_CLEARED = "on_stage_cleared"
    GAME_OVER = "on_game_over"


@dataclass(frozen=True, slots=True)
class ModEvent:
    name: ModEventName
    data: dict[str, Any]
