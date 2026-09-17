"""Cross-layer game-state contract."""

from enum import StrEnum


class GameState(StrEnum):
    READY = "ready"
    PLAYING = "playing"
    CLEAR = "clear"
    GAME_OVER = "game_over"
