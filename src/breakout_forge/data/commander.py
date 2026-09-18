"""Data-layer commander."""

from pathlib import Path

from breakout_forge.contracts.image_asset import PreparedImageAsset
from breakout_forge.contracts.settings import BreakImageSettings
from breakout_forge.contracts.stage import ResolvedStageDefinition, StageLayerDefinition
from breakout_forge.data.processing.image_processing import prepare_image_asset
from breakout_forge.data.processing.stage_processing import load_stage_definition


class DataCommander:
    """Orchestrate data-layer operations without implementing parsing logic."""

    def load_stage(
        self,
        common_path: Path,
        stage_path: Path,
    ) -> ResolvedStageDefinition:
        return load_stage_definition(common_path, stage_path)

    def prepare_image(
        self,
        layer: StageLayerDefinition,
        break_image: BreakImageSettings,
    ) -> PreparedImageAsset:
        return prepare_image_asset(layer, break_image)
