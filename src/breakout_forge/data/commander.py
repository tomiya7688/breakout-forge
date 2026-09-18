"""Data-layer commander."""

from pathlib import Path

from breakout_forge.contracts.image_asset import PreparedImageAsset
from breakout_forge.contracts.paths import ExternalPaths
from breakout_forge.contracts.settings import BreakImageSettings
from breakout_forge.contracts.stage import ResolvedStageDefinition, StageLayerDefinition
from breakout_forge.data.processing.image_processing import prepare_image_asset
from breakout_forge.data.processing.mod_processing import load_and_register_mods
from breakout_forge.data.processing.path_processing import resolve_external_paths
from breakout_forge.modding.api import ModApi
from breakout_forge.data.processing.stage_processing import load_stage_definition


class DataCommander:
    """Orchestrate data-layer operations without implementing parsing logic."""

    def load_stage(
        self,
        common_path: Path,
        stage_path: Path,
        user_path: Path | None = None,
    ) -> ResolvedStageDefinition:
        return load_stage_definition(common_path, stage_path, user_path)

    def prepare_image(
        self,
        layer: StageLayerDefinition,
        break_image: BreakImageSettings,
    ) -> PreparedImageAsset:
        return prepare_image_asset(layer, break_image)

    def load_mods(self, mods_dir: Path, api: ModApi):
        return load_and_register_mods(mods_dir, api)

    def resolve_paths(self, base_dir: Path | None = None) -> ExternalPaths:
        return resolve_external_paths(base_dir)
