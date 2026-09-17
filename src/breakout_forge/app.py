"""Application composition root.

This module only wires layer components together. It does not contain UI, game, or data logic.
"""

from pathlib import Path

from breakout_forge.data.processing.settings_processing import resolve_common_settings
from breakout_forge.process.commander import ProcessCommander
from breakout_forge.process.messenger import ProcessMessenger
from breakout_forge.process.processing.frame_processing import FrameProcessing
from breakout_forge.process.processing.paddle_ball_processing import PaddleBallProcessing
from breakout_forge.ui.commander import UiCommander
from breakout_forge.ui.messenger import UiMessenger
from breakout_forge.ui.processing.runtime_processing import RuntimeProcessing


def create_application(common_path: Path | None = None) -> UiCommander:
    settings = resolve_common_settings(common_path or Path("config/common.json"))

    paddle_ball_processing = PaddleBallProcessing(settings.gameplay, settings.playfield)
    frame_processing = FrameProcessing(paddle_ball_processing=paddle_ball_processing)
    process_commander = ProcessCommander(frame_processing)
    process_messenger = ProcessMessenger(process_commander)
    ui_messenger = UiMessenger(process_messenger)
    runtime_processing = RuntimeProcessing(ui_messenger, settings.display)
    return UiCommander(runtime_processing)
