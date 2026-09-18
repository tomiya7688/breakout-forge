"""Data-layer messaging boundary."""

from pathlib import Path

from breakout_forge.contracts.image_asset import PreparedImageAsset
from breakout_forge.contracts.settings import BreakImageSettings
from breakout_forge.contracts.stage import ResolvedStageDefinition, StageLayerDefinition
from breakout_forge.data.commander import DataCommander
from breakout_forge.modding.api import ModApi


class DataMessenger:
    """Carry stage-load requests across the Process/Data boundary."""

    def __init__(self, commander: DataCommander) -> None:
        self._commander = commander

    def load_stage(
        self,
        common_path: Path,
        stage_path: Path,
        user_path: Path | None = None,
    ) -> ResolvedStageDefinition:
        return self._commander.load_stage(common_path, stage_path, user_path)

    def prepare_image(
        self,
        layer: StageLayerDefinition,
        break_image: BreakImageSettings,
    ) -> PreparedImageAsset:
        return self._commander.prepare_image(layer, break_image)

    def load_mods(self, mods_dir: Path, api: ModApi):
        return self._commander.load_mods(mods_dir, api)
