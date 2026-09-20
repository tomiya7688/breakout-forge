"""Cross-layer frame contracts.

Contracts contain transport data only and must not depend on pygame or persistence details.
"""

from dataclasses import dataclass

from breakout_forge.contracts.game_state import GameState
from breakout_forge.contracts.gameplay import GameplaySnapshot


@dataclass(frozen=True, slots=True)
class FrameRequest:
    """Input passed from the UI layer to the process layer for one frame."""

    delta_seconds: float
    start_requested: bool = False
    restart_requested: bool = False
    move_axis: float = 0.0


@dataclass(frozen=True, slots=True)
class FrameResult:
    """Process-layer result returned to the UI layer."""

    running: bool = True
    state: GameState = GameState.READY
    gameplay: GameplaySnapshot | None = None
