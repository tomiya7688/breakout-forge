"""Pure process-layer board, cell, and block-layer domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class RectValue:
    """Framework-neutral rectangle used by process-layer models."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("rect width/height must be positive")


@dataclass(frozen=True, slots=True)
class SourceRectValue:
    """Source rectangle inside an image asset."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("source rect width/height must be positive")


@dataclass(slots=True)
class BlockLayer:
    """One destructible/visible layer stacked inside a board cell."""

    id: str
    hp: int = 1
    max_hp: int = 1
    asset_id: str | None = None
    source_rect: SourceRectValue | None = None
    collidable: bool = True
    destructible: bool = True
    visible: bool = True
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("layer id must not be empty")
        if self.max_hp <= 0:
            raise ValueError("max_hp must be positive")
        if self.hp < 0 or self.hp > self.max_hp:
            raise ValueError("hp must be between 0 and max_hp")

    @property
    def alive(self) -> bool:
        return self.hp > 0


@dataclass(slots=True)
class BlockCell:
    """One logical grid cell containing an ordered stack of layers."""

    column: int
    row: int
    rect: RectValue
    layers: list[BlockLayer] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.column < 0 or self.row < 0:
            raise ValueError("cell coordinates must be non-negative")

    def push_layer(self, layer: BlockLayer) -> None:
        """Push a layer on top of the cell stack."""

        self.layers.append(layer)

    def top_layer(self) -> BlockLayer | None:
        """Return the top alive layer regardless of collision/visibility flags."""

        for layer in reversed(self.layers):
            if layer.alive:
                return layer
        return None

    def top_collidable_layer(self) -> BlockLayer | None:
        """Return the top alive collidable layer."""

        for layer in reversed(self.layers):
            if layer.alive and layer.collidable:
                return layer
        return None

    def top_visible_layer(self) -> BlockLayer | None:
        """Return the top alive visible layer."""

        for layer in reversed(self.layers):
            if layer.alive and layer.visible:
                return layer
        return None

    @property
    def empty(self) -> bool:
        return self.top_layer() is None


class Board:
    """Rectangular grid of BlockCell instances."""

    def __init__(self, columns: int, rows: int, cells: Iterable[BlockCell]) -> None:
        if columns <= 0 or rows <= 0:
            raise ValueError("board columns/rows must be positive")

        self.columns = columns
        self.rows = rows
        self._cells = list(cells)
        if len(self._cells) != columns * rows:
            raise ValueError("cell count must match board dimensions")

        seen: set[tuple[int, int]] = set()
        for cell in self._cells:
            key = (cell.column, cell.row)
            if not (0 <= cell.column < columns and 0 <= cell.row < rows):
                raise ValueError("cell coordinate outside board")
            if key in seen:
                raise ValueError("duplicate cell coordinate")
            seen.add(key)

        if len(seen) != columns * rows:
            raise ValueError("board must contain every grid coordinate")

        self._by_position = {(cell.column, cell.row): cell for cell in self._cells}

    @classmethod
    def create_grid(
        cls,
        *,
        columns: int,
        rows: int,
        origin_x: float,
        origin_y: float,
        cell_width: float,
        cell_height: float,
    ) -> "Board":
        if cell_width <= 0 or cell_height <= 0:
            raise ValueError("cell width/height must be positive")

        cells = [
            BlockCell(
                column=column,
                row=row,
                rect=RectValue(
                    x=origin_x + column * cell_width,
                    y=origin_y + row * cell_height,
                    width=cell_width,
                    height=cell_height,
                ),
            )
            for row in range(rows)
            for column in range(columns)
        ]
        return cls(columns, rows, cells)

    def cell_at(self, column: int, row: int) -> BlockCell:
        try:
            return self._by_position[(column, row)]
        except KeyError as exc:
            raise IndexError("cell coordinate outside board") from exc

    def cells(self) -> tuple[BlockCell, ...]:
        return tuple(self._cells)

    def non_empty_cells(self) -> tuple[BlockCell, ...]:
        return tuple(cell for cell in self._cells if not cell.empty)

    @property
    def empty(self) -> bool:
        return not self.non_empty_cells()
