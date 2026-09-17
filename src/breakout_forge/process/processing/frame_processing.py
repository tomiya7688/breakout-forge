"""Pure process-layer work for one frame."""

from breakout_forge.contracts.frame import FrameRequest, FrameResult
from breakout_forge.process.processing.state_processing import StateProcessing


class FrameProcessing:
    """Coordinate process-layer work for one frame.

    Concrete gameplay processing units are added incrementally by later issues.
    """

    def __init__(self, state_processing: StateProcessing | None = None) -> None:
        self._state_processing = state_processing or StateProcessing()

    @property
    def state_processing(self) -> StateProcessing:
        return self._state_processing

    def execute(self, request: FrameRequest) -> FrameResult:
        if request.delta_seconds < 0:
            raise ValueError("delta_seconds must be non-negative")

        state = self._state_processing.apply_requests(
            start_requested=request.start_requested,
            restart_requested=request.restart_requested,
        )
        return FrameResult(running=True, state=state)
