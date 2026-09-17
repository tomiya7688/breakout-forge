"""Ball/Board collision detection and reflection for the process layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from breakout_forge.contracts.layer_damage import LayerDamageResult
from breakout_forge.process.model.board import BlockCell, Board, RectValue
from breakout_forge.process.processing.layer_damage_processing import LayerDamageProcessing


class MutableBall(Protocol):
    x: float
    y: float
    vx: float
    vy: float
    size: float


@dataclass(frozen=True, slots=True)
class BoardCollisionResult:
    collided: bool
    column: int | None = None
    row: int | None = None
    reflected_x: bool = False
    reflected_y: bool = False
    damage: LayerDamageResult | None = None


class BoardCollisionProcessing:
    """Resolve one stable block collision per ball per frame."""

    def __init__(self, damage_processing: LayerDamageProcessing | None = None) -> None:
        self._damage_processing = damage_processing or LayerDamageProcessing()

    def resolve(
        self,
        ball: MutableBall,
        board: Board,
        *,
        previous_x: float,
        previous_y: float,
        damage: int = 1,
    ) -> BoardCollisionResult:
        candidates = [
            cell
            for cell in board.non_empty_cells()
            if cell.top_collidable_layer() is not None
            and self._intersects(ball, cell.rect)
        ]
        if not candidates:
            return BoardCollisionResult(collided=False)

        cell = min(
            candidates,
            key=lambda candidate: self._penetration_score(ball, candidate.rect),
        )
        reflect_x, reflect_y = self._reflection_axes(
            ball,
            cell.rect,
            previous_x=previous_x,
            previous_y=previous_y,
        )

        if reflect_x:
            ball.vx = -ball.vx
        if reflect_y:
            ball.vy = -ball.vy

        self._separate(
            ball,
            cell.rect,
            previous_x=previous_x,
            previous_y=previous_y,
            reflect_x=reflect_x,
            reflect_y=reflect_y,
        )
        damage_result = self._damage_processing.apply(cell, damage)

        return BoardCollisionResult(
            collided=True,
            column=cell.column,
            row=cell.row,
            reflected_x=reflect_x,
            reflected_y=reflect_y,
            damage=damage_result,
        )

    @staticmethod
    def _intersects(ball: MutableBall, rect: RectValue) -> bool:
        return (
            ball.x < rect.x + rect.width
            and ball.x + ball.size > rect.x
            and ball.y < rect.y + rect.height
            and ball.y + ball.size > rect.y
        )

    @staticmethod
    def _penetration_score(ball: MutableBall, rect: RectValue) -> float:
        overlap_x = min(ball.x + ball.size, rect.x + rect.width) - max(ball.x, rect.x)
        overlap_y = min(ball.y + ball.size, rect.y + rect.height) - max(ball.y, rect.y)
        return min(overlap_x, overlap_y)

    @staticmethod
    def _reflection_axes(
        ball: MutableBall,
        rect: RectValue,
        *,
        previous_x: float,
        previous_y: float,
    ) -> tuple[bool, bool]:
        previous_right = previous_x + ball.size
        previous_bottom = previous_y + ball.size

        if previous_bottom <= rect.y or previous_y >= rect.y + rect.height:
            return False, True
        if previous_right <= rect.x or previous_x >= rect.x + rect.width:
            return True, False

        overlap_x = min(ball.x + ball.size, rect.x + rect.width) - max(ball.x, rect.x)
        overlap_y = min(ball.y + ball.size, rect.y + rect.height) - max(ball.y, rect.y)
        if overlap_x < overlap_y:
            return True, False
        return False, True

    @staticmethod
    def _separate(
        ball: MutableBall,
        rect: RectValue,
        *,
        previous_x: float,
        previous_y: float,
        reflect_x: bool,
        reflect_y: bool,
    ) -> None:
        if reflect_x:
            if previous_x + ball.size <= rect.x:
                ball.x = rect.x - ball.size
            elif previous_x >= rect.x + rect.width:
                ball.x = rect.x + rect.width
        if reflect_y:
            if previous_y + ball.size <= rect.y:
                ball.y = rect.y - ball.size
            elif previous_y >= rect.y + rect.height:
                ball.y = rect.y + rect.height
