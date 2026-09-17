"""UI-layer messaging boundary."""

from breakout_forge.contracts.frame import FrameRequest, FrameResult
from breakout_forge.process.messenger import ProcessMessenger


class UiMessenger:
    """Forward UI-originated requests to the process layer."""

    def __init__(self, process_messenger: ProcessMessenger) -> None:
        self._process_messenger = process_messenger

    def update_frame(
        self,
        delta_seconds: float,
        *,
        start_requested: bool = False,
        restart_requested: bool = False,
        move_axis: float = 0.0,
    ) -> FrameResult:
        return self._process_messenger.update_frame(
            FrameRequest(
                delta_seconds=delta_seconds,
                start_requested=start_requested,
                restart_requested=restart_requested,
                move_axis=move_axis,
            )
        )
