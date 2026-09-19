"""Process-layer game state transitions."""

from breakout_forge.contracts.game_state import GameState


class StateProcessing:
    """Own the current game state and perform valid state transitions."""

    def __init__(self) -> None:
        self._state = GameState.READY

    @property
    def state(self) -> GameState:
        return self._state

    def apply_requests(self, *, start_requested: bool, restart_requested: bool) -> GameState:
        if restart_requested:
            self._state = GameState.READY
        elif start_requested and self._state is GameState.READY:
            self._state = GameState.PLAYING
        return self._state

    def mark_clear(self) -> GameState:
        if self._state is GameState.PLAYING:
            self._state = GameState.CLEAR
        return self._state

    def mark_game_over(self) -> GameState:
        if self._state is GameState.PLAYING:
            self._state = GameState.GAME_OVER
        return self._state
