"""Resolved external-data paths shared by the composition root."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ExternalPaths:
    base_dir: Path
    config_dir: Path
    assets_dir: Path
    stages_dir: Path
    mods_dir: Path
    userdata_dir: Path
    common_settings: Path
    user_settings: Path

    def stage_json(self, stage_id: str) -> Path:
        return self.stages_dir / stage_id / "stage.json"
