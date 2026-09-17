"""Pure process-layer work for one frame."""

from breakout_forge.contracts.frame import FrameRequest, FrameResult


class FrameProcessing:
    """Perform current game-state work for a frame.

    Game rules will be added here through smaller processing units in later issues.
    """

    def execute(self, request: FrameRequest) -> FrameResult:
        if request.delta_seconds < 0:
            raise ValueError("delta_seconds must be non-negative")
        return FrameResult(running=True)
