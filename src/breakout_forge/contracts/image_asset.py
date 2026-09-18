"""Prepared image assets shared across Data, Process, and UI boundaries."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PreparedImageAsset:
    id: str
    width: int
    height: int
    rgba: bytes
    active_tiles: frozenset[tuple[int, int]]
