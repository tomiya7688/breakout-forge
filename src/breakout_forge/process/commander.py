"""Process-layer commander."""

from breakout_forge.contracts.frame import FrameRequest, FrameResult
from breakout_forge.process.processing.frame_processing import FrameProcessing


class ProcessCommander:
    """Direct process-layer work without implementing game logic itself."""

    def __init__(self, frame_processing: FrameProcessing) -> None:
        self._frame_processing = frame_processing

    def update_frame(self, request: FrameRequest) -> FrameResult:
        return self._frame_processing.execute(request)
