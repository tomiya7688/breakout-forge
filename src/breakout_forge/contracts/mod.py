"""Resolved Python MOD definitions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ModDefinition:
    id: str
    name: str
    version: str
    directory: Path
    entry_path: Path
