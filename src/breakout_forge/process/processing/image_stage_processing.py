"""Process-layer runtime for one destructible image stage."""

from __future__ import annotations

from breakout_forge.contracts.gameplay import (
    BlockSnapshot,
    RectSnapshot,
    SourceRectSnapshot,
)
from breakout_forge.contracts.image_asset import PreparedImageAsset
from breakout_forge.contracts.settings import PlayfieldSettings, StandardStageSettings
from breakout_forge.contracts.stage import ResolvedStageDefinition, StageLayerDefinition
from breakout_forge.process.model.board import (
    BlockCell,
    BlockLayer,
    Board,
    RectValue,
    SourceRectValue,
)
from breakout_forge.process.processing.collision import BoardCollisionResult


class ImageStageProcessing:
    """Build a destructible Board from one prepared source image.

    stage_size remains the stage logical world-size setting.
    The destruction grid is intentionally driven by break_image.split.
    """

    def __init__(
        self,
        stage: ResolvedStageDefinition,
        layer: StageLayerDefinition,
        asset: PreparedImageAsset,
        playfield: PlayfieldSettings,
        target_area: StandardStageSettings,
    ) -> None:
        if layer.id != asset.id:
            raise ValueError("image layer and prepared asset id must match")
        self._stage = stage
        self._layer = layer
        self._asset = asset
        self._playfield = playfield
        self._target_area = target_area
        self._score = 0
        self._board: Board
        self.reset()

    @property
    def board(self) -> Board:
        return self._board

    @property
    def score(self) -> int:
        return self._score

    def _destination_image_rect(self) -> RectValue:
        available_x = float(self._target_area.left_margin)
        available_y = float(self._target_area.top_margin)
        available_width = float(
            self._playfield.width
            - self._target_area.left_margin
            - self._target_area.right_margin
        )
        available_height = float(self._target_area.block_area_height)
        if available_width <= 0 or available_height <= 0:
            raise ValueError("image stage target area must be positive")

        source_width = float(self._asset.width)
        source_height = float(self._asset.height)
        fit = self._stage.settings.playfield.fit

        if fit == "stretch":
            return RectValue(
                x=available_x,
                y=available_y,
                width=available_width,
                height=available_height,
            )

        if fit == "contain":
            scale = min(available_width / source_width, available_height / source_height)
        elif fit == "cover":
            scale = max(available_width / source_width, available_height / source_height)
        else:
            raise ValueError(f"unsupported image fit: {fit}")

        width = source_width * scale
        height = source_height * scale
        return RectValue(
            x=available_x + (available_width - width) / 2.0,
            y=available_y + (available_height - height) / 2.0,
            width=width,
            height=height,
        )

    def reset(self) -> Board:
        split = self._stage.settings.break_image.split
        destination = self._destination_image_rect()
        cells: list[BlockCell] = []

        for row in range(split.rows):
            source_y0 = row * self._asset.height // split.rows
            source_y1 = (row + 1) * self._asset.height // split.rows
            dest_y0 = destination.y + destination.height * source_y0 / self._asset.height
            dest_y1 = destination.y + destination.height * source_y1 / self._asset.height

            for column in range(split.columns):
                source_x0 = column * self._asset.width // split.columns
                source_x1 = (column + 1) * self._asset.width // split.columns
                dest_x0 = destination.x + destination.width * source_x0 / self._asset.width
                dest_x1 = destination.x + destination.width * source_x1 / self._asset.width

                cell = BlockCell(
                    column=column,
                    row=row,
                    rect=RectValue(
                        x=dest_x0,
                        y=dest_y0,
                        width=dest_x1 - dest_x0,
                        height=dest_y1 - dest_y0,
                    ),
                )
                if (column, row) in self._asset.active_tiles:
                    source_rect = SourceRectValue(
                        x=source_x0,
                        y=source_y0,
                        width=source_x1 - source_x0,
                        height=source_y1 - source_y0,
                    )
                    cell.push_layer(
                        BlockLayer(
                            id=f"{self._layer.id}:{column}:{row}",
                            hp=self._layer.hp,
                            max_hp=self._layer.hp,
                            asset_id=self._asset.id,
                            source_rect=source_rect,
                            collidable=self._layer.collidable,
                            destructible=self._layer.destructible,
                            visible=self._layer.visible,
                        )
                    )
                cells.append(cell)

        self._board = Board(
            columns=split.columns,
            rows=split.rows,
            cells=cells,
        )
        self._score = 0
        return self._board

    def register_collisions(
        self,
        collisions: tuple[BoardCollisionResult, ...],
    ) -> None:
        for collision in collisions:
            damage = collision.damage
            if damage is not None and damage.layer_destroyed:
                self._score += self._stage.settings.standard_stage.score_per_layer

    @property
    def cleared(self) -> bool:
        return self._board.empty

    def block_snapshots(self) -> tuple[BlockSnapshot, ...]:
        snapshots: list[BlockSnapshot] = []
        for cell in self._board.non_empty_cells():
            layer = cell.top_visible_layer()
            if layer is None:
                continue
            source = layer.source_rect
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
                    asset_id=layer.asset_id,
                    source_rect=(
                        SourceRectSnapshot(
                            x=source.x,
                            y=source.y,
                            width=source.width,
                            height=source.height,
                        )
                        if source is not None
                        else None
                    ),
                )
            )
        return tuple(snapshots)
