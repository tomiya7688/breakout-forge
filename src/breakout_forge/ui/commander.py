"""UI-layer commander."""

from breakout_forge.ui.processing.runtime_processing import RuntimeProcessing


class UiCommander:
    """Direct UI-layer processing without performing rendering/input work."""

    def __init__(self, runtime_processing: RuntimeProcessing) -> None:
        self._runtime_processing = runtime_processing

    def run(self) -> int:
        return self._runtime_processing.run()
