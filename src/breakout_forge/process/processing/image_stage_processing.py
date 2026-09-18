"""Process-layer runtime for destructible single or layered image stages."""

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
    """Build a destructible Board from one or more prepared source images.

    stage.layers are interpreted bottom-to-top. Every image layer uses its own
    source-image dimensions and source rects, while all layers at the same
    (column, row) share one destination Cell.
    """

    def __init__(
        self,
        stage: ResolvedStageDefinition,
        layers: tuple[StageLayerDefinition, ...],
        assets: tuple[PreparedImageAsset, ...],
        playfield: PlayfieldSettings,
        target_area: StandardStageSettings,
    ) -> None:
        if not layers:
            raise ValueError("image stage requires at least one image layer")
        asset_by_id = {asset.id: asset for asset in assets}
        if len(asset_by_id) != len(assets):
            raise ValueError("prepared image asset ids must be unique")
        for layer in layers:
            if layer.id not in asset_by_id:
                raise ValueError(f"missing prepared asset for image layer: {layer.id}")

        self._stage = stage
        self._layers = layers
        self._assets = asset_by_id
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

    def _available_rect(self) -> RectValue:
        width = float(
            self._playfield.width
            - self._target_area.left_margin
            - self._target_area.right_margin
        )
        height = float(self._target_area.block_area_height)
        if width <= 0 or height <= 0:
            raise ValueError("image stage target area must be positive")
        return RectValue(
            x=float(self._target_area.left_margin),
            y=float(self._target_area.top_margin),
            width=width,
            height=height,
        )

    def _destination_rect_for(self, asset: PreparedImageAsset) -> RectValue:
        available = self._available_rect()
        fit = self._stage.settings.playfield.fit

        if fit == "stretch":
            return available

        source_width = float(asset.width)
        source_height = float(asset.height)
        if fit == "contain":
            scale = min(
                available.width / source_width,
                available.height / source_height,
            )
        elif fit == "cover":
            scale = max(
                available.width / source_width,
                available.height / source_height,
            )
        else:
            raise ValueError(f"unsupported image fit: {fit}")

        width = source_width * scale
        height = source_height * scale
        return RectValue(
            x=available.x + (available.width - width) / 2.0,
            y=available.y + (available.height - height) / 2.0,
            width=width,
            height=height,
        )

    def _shared_cell_rect(self, column: int, row: int) -> RectValue:
        split = self._stage.settings.break_image.split
        available = self._available_rect()
        x0 = available.x + available.width * column / split.columns
        x1 = available.x + available.width * (column + 1) / split.columns
        y0 = available.y + available.height * row / split.rows
        y1 = available.y + available.height * (row + 1) / split.rows
        return RectValue(x=x0, y=y0, width=x1 - x0, height=y1 - y0)

    def _source_rect(
        self,
        asset: PreparedImageAsset,
        column: int,
        row: int,
    ) -> SourceRectValue:
        split = self._stage.settings.break_image.split
        x0 = column * asset.width // split.columns
        x1 = (column + 1) * asset.width // split.columns
        y0 = row * asset.height // split.rows
        y1 = (row + 1) * asset.height // split.rows
        return SourceRectValue(
            x=x0,
            y=y0,
            width=x1 - x0,
            height=y1 - y0,
        )

    def reset(self) -> Board:
        split = self._stage.settings.break_image.split
        cells: list[BlockCell] = []

        for row in range(split.rows):
            for column in range(split.columns):
                cell = BlockCell(
                    column=column,
                    row=row,
                    rect=self._shared_cell_rect(column, row),
                )

                for layer in self._layers:
                    asset = self._assets[layer.id]
                    if (column, row) not in asset.active_tiles:
                        continue
                    cell.push_layer(
                        BlockLayer(
                            id=f"{layer.id}:{column}:{row}",
                            hp=layer.hp,
                            max_hp=layer.hp,
                            asset_id=asset.id,
                            source_rect=self._source_rect(asset, column, row),
                            collidable=layer.collidable,
                            destructible=layer.destructible,
                            visible=layer.visible,
                            metadata={
                                "image_destination": self._destination_rect_for(asset),
                            },
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
            destination = layer.metadata.get("image_destination")
            rect = cell.rect if not isinstance(destination, RectValue) else RectValue(
                x=destination.x + destination.width * cell.column / self._board.columns,
                y=destination.y + destination.height * cell.row / self._board.rows,
                width=destination.width / self._board.columns,
                height=destination.height / self._board.rows,
            )
            snapshots.append(
                BlockSnapshot(
                    column=cell.column,
                    row=cell.row,
                    rect=RectSnapshot(
                        x=rect.x,
                        y=rect.y,
                        width=rect.width,
                        height=rect.height,
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
