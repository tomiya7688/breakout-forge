"""Data-layer commander."""

from pathlib import Path

from breakout_forge.contracts.stage import ResolvedStageDefinition
from breakout_forge.data.processing.stage_processing import load_stage_definition


class DataCommander:
    """Orchestrate data-layer operations without implementing parsing logic."""

    def load_stage(
        self,
        common_path: Path,
        stage_path: Path,
    ) -> ResolvedStageDefinition:
        return load_stage_definition(common_path, stage_path)
