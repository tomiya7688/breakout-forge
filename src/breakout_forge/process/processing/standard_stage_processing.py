"""Standard data-driven Breakout stage creation and score handling."""

from __future__ import annotations

from breakout_forge.contracts.gameplay import BlockSnapshot, RectSnapshot
from breakout_forge.contracts.settings import (
    GridSettings,
    PlayfieldSettings,
    StandardStageSettings,
)
from breakout_forge.process.model.board import BlockLayer, Board
from breakout_forge.process.processing.collision import BoardCollisionResult


class StandardStageProcessing:
    """Own the standard Board instance and its simple score rule."""

    def __init__(
        self,
        stage_size: GridSettings,
        stage_settings: StandardStageSettings,
        playfield: PlayfieldSettings,
    ) -> None:
        self._stage_size = stage_size
        self._settings = stage_settings
        self._playfield = playfield
        self._board: Board
        self._score = 0
        self.reset()

    @property
    def board(self) -> Board:
        return self._board

    @property
    def score(self) -> int:
        return self._score

    def reset(self) -> Board:
        usable_width = (
            self._playfield.width
            - self._settings.left_margin
            - self._settings.right_margin
        )
        gaps_width = self._settings.gap_x * (self._stage_size.columns - 1)
        gaps_height = self._settings.gap_y * (self._stage_size.rows - 1)
        cell_width = (usable_width - gaps_width) / self._stage_size.columns
        cell_height = (
            self._settings.block_area_height - gaps_height
        ) / self._stage_size.rows
        if cell_width <= 0 or cell_height <= 0:
            raise ValueError("standard stage layout leaves no room for block cells")

        cells = []
        for row in range(self._stage_size.rows):
            for column in range(self._stage_size.columns):
                x = self._settings.left_margin + column * (
                    cell_width + self._settings.gap_x
                )
                y = self._settings.top_margin + row * (
                    cell_height + self._settings.gap_y
                )
                from breakout_forge.process.model.board import BlockCell, RectValue

                cell = BlockCell(
                    column=column,
                    row=row,
                    rect=RectValue(x=x, y=y, width=cell_width, height=cell_height),
                )
                cell.push_layer(
                    BlockLayer(
                        id=f"standard-{column}-{row}",
                        hp=self._settings.block_hp,
                        max_hp=self._settings.block_hp,
                    )
                )
                cells.append(cell)

        self._board = Board(
            columns=self._stage_size.columns,
            rows=self._stage_size.rows,
            cells=cells,
        )
        self._score = 0
        return self._board

    def register_collisions(
        self, collisions: tuple[BoardCollisionResult, ...]
    ) -> None:
        for collision in collisions:
            damage = collision.damage
            if damage is not None and damage.layer_destroyed:
                self._score += self._settings.score_per_layer

    @property
    def cleared(self) -> bool:
        return self._board.empty

    def block_snapshots(self) -> tuple[BlockSnapshot, ...]:
        snapshots: list[BlockSnapshot] = []
        for cell in self._board.non_empty_cells():
            if cell.top_visible_layer() is None:
                continue
            snapshots.append(
                BlockSnapshot(
                    column=cell.column,
                    row=cell.row,
                    rect=RectSnapshot(
                        x=cell.rect.x,
                        y=cell.rect.y,
                        width=cell.rect.width,
                        height=cell.rect.height,
                    ),
                )
            )
        return tuple(snapshots)
