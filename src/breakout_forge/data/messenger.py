"""Data-layer messaging boundary."""

from pathlib import Path

from breakout_forge.contracts.stage import ResolvedStageDefinition
from breakout_forge.data.commander import DataCommander


class DataMessenger:
    """Carry stage-load requests across the Process/Data boundary."""

    def __init__(self, commander: DataCommander) -> None:
        self._commander = commander

    def load_stage(
        self,
        common_path: Path,
        stage_path: Path,
    ) -> ResolvedStageDefinition:
        return self._commander.load_stage(common_path, stage_path)
