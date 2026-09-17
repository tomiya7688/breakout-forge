"""Application composition root.

This module only wires layer components together. It does not contain UI, game, or data logic.
"""

from breakout_forge.process.commander import ProcessCommander
from breakout_forge.process.messenger import ProcessMessenger
from breakout_forge.process.processing.frame_processing import FrameProcessing
from breakout_forge.ui.commander import UiCommander
from breakout_forge.ui.messenger import UiMessenger
from breakout_forge.ui.processing.runtime_processing import RuntimeProcessing


def create_application() -> UiCommander:
    frame_processing = FrameProcessing()
    process_commander = ProcessCommander(frame_processing)
    process_messenger = ProcessMessenger(process_commander)
    ui_messenger = UiMessenger(process_messenger)
    runtime_processing = RuntimeProcessing(ui_messenger)
    return UiCommander(runtime_processing)
