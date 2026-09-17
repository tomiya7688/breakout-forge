"""Pure process-layer work for one frame."""

from breakout_forge.contracts.frame import FrameRequest, FrameResult
from breakout_forge.contracts.game_state import GameState
from breakout_forge.process.processing.paddle_ball_processing import PaddleBallProcessing
from breakout_forge.process.processing.state_processing import StateProcessing


class FrameProcessing:
    """Coordinate process-layer work for one frame."""

    def __init__(
        self,
        state_processing: StateProcessing | None = None,
        paddle_ball_processing: PaddleBallProcessing | None = None,
    ) -> None:
        self._state_processing = state_processing or StateProcessing()
        self._paddle_ball_processing = paddle_ball_processing

    @property
    def state_processing(self) -> StateProcessing:
        return self._state_processing

    def execute(self, request: FrameRequest) -> FrameResult:
        if request.delta_seconds < 0:
            raise ValueError("delta_seconds must be non-negative")

        previous_state = self._state_processing.state
        state = self._state_processing.apply_requests(
            start_requested=request.start_requested,
            restart_requested=request.restart_requested,
        )

        if self._paddle_ball_processing is not None:
            if request.restart_requested or (previous_state is not GameState.READY and state is GameState.READY):
                self._paddle_ball_processing.reset()
            if state is GameState.PLAYING:
                if self._paddle_ball_processing.update(request.delta_seconds, request.move_axis):
                    state = self._state_processing.mark_game_over()
            gameplay = self._paddle_ball_processing.snapshot()
        else:
            gameplay = None

        return FrameResult(running=True, state=state, gameplay=gameplay)
