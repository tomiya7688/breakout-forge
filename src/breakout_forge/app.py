"""Application composition root.

This module only wires layer components together. It does not contain UI, game, or data logic.
"""

from pathlib import Path

from breakout_forge.contracts.image_asset import PreparedImageAsset
from breakout_forge.data.commander import DataCommander
from breakout_forge.data.messenger import DataMessenger
from breakout_forge.data.processing.settings_processing import (
    resolve_runtime_settings,
)
from breakout_forge.modding.api import ModApi
from breakout_forge.process.commander import ProcessCommander
from breakout_forge.process.messenger import ProcessMessenger
from breakout_forge.process.processing.frame_processing import FrameProcessing
from breakout_forge.process.processing.image_stage_processing import ImageStageProcessing
from breakout_forge.process.processing.paddle_ball_processing import PaddleBallProcessing
from breakout_forge.process.processing.standard_stage_processing import StandardStageProcessing
from breakout_forge.ui.commander import UiCommander
from breakout_forge.ui.messenger import UiMessenger
from breakout_forge.ui.processing.runtime_processing import RuntimeProcessing


def create_application(
    common_path: Path | None = None,
    stage_path: Path | None = None,
    mods_dir: Path | None = None,
    *,
    base_dir: Path | None = None,
    user_settings_path: Path | None = None,
) -> UiCommander:
    data_messenger = DataMessenger(DataCommander())
    paths = data_messenger.resolve_paths(base_dir)

    common = paths.resolve(common_path) if common_path is not None else paths.common_settings
    user_settings = (
        paths.resolve(user_settings_path)
        if user_settings_path is not None
        else paths.user_settings
    )
    mods = paths.resolve(mods_dir) if mods_dir is not None else paths.mods_dir
    stage_file = paths.resolve(stage_path) if stage_path is not None else None

    data_messenger.require_file(common, "common settings")
    if stage_file is not None:
        data_messenger.require_file(stage_file, "stage definition")

    mod_api = ModApi()
    data_messenger.load_mods(mods, mod_api)
    prepared_assets: tuple[PreparedImageAsset, ...] = ()

    if stage_file is None:
        settings = resolve_runtime_settings(
            common,
            user_path=user_settings,
        )
        stage_id = "standard"
        stage_name = "Standard Stage"
        stage_processing = StandardStageProcessing(
            settings.stage_size,
            settings.standard_stage,
            settings.playfield,
        )
    else:
        stage = data_messenger.load_stage(
            common,
            stage_file,
            user_settings,
        )
        settings = stage.settings
        stage_id = stage.id
        stage_name = stage.name
        image_layers = tuple(layer for layer in stage.layers if layer.image_path is not None)

        if not image_layers:
            stage_processing = StandardStageProcessing(
                settings.stage_size,
                settings.standard_stage,
                settings.playfield,
            )
        else:
            prepared_assets = tuple(
                data_messenger.prepare_image(layer, settings.break_image)
                for layer in image_layers
            )
            stage_processing = ImageStageProcessing(
                stage,
                image_layers,
                prepared_assets,
                settings.playfield,
                settings.standard_stage,
            )

    paddle_ball_processing = PaddleBallProcessing(
        settings.gameplay,
        settings.playfield,
        board=stage_processing.board,
    )
    frame_processing = FrameProcessing(
        paddle_ball_processing=paddle_ball_processing,
        stage_processing=stage_processing,
        mod_api=mod_api,
    )
    frame_processing.emit_stage_loaded(stage_id, stage_name)
    process_commander = ProcessCommander(frame_processing)
    process_messenger = ProcessMessenger(process_commander)
    ui_messenger = UiMessenger(process_messenger)
    runtime_processing = RuntimeProcessing(
        ui_messenger,
        settings.display,
        settings.appearance,
        prepared_assets=prepared_assets,
    )
    return UiCommander(runtime_processing)
