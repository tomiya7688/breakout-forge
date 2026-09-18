"""Common Process-stage runtime protocol."""

from __future__ import annotations

from typing import Protocol

from breakout_forge.contracts.gameplay import BlockSnapshot
from breakout_forge.process.model.board import Board
from breakout_forge.process.processing.collision import BoardCollisionResult


class StageRuntime(Protocol):
    @property
    def board(self) -> Board: ...

    @property
    def score(self) -> int: ...

    def reset(self) -> Board: ...

    def register_collisions(self, collisions: tuple[BoardCollisionResult, ...]) -> None: ...

    @property
    def cleared(self) -> bool: ...

    def block_snapshots(self) -> tuple[BlockSnapshot, ...]: ...
