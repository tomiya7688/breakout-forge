"""Process-layer messaging boundary."""

from breakout_forge.contracts.frame import FrameRequest, FrameResult
from breakout_forge.process.commander import ProcessCommander


class ProcessMessenger:
    """Carry requests across the UI/Process boundary."""

    def __init__(self, commander: ProcessCommander) -> None:
        self._commander = commander

    def update_frame(self, request: FrameRequest) -> FrameResult:
        return self._commander.update_frame(request)
