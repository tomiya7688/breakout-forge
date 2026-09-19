import pytest

from breakout_forge.process.model.board import (
    BlockCell,
    BlockLayer,
    Board,
    RectValue,
    SourceRectValue,
)


def test_board_create_grid_builds_all_cells() -> None:
    board = Board.create_grid(
        columns=3,
        rows=2,
        origin_x=10.0,
        origin_y=20.0,
        cell_width=30.0,
        cell_height=40.0,
    )

    assert len(board.cells()) == 6
    assert board.cell_at(0, 0).rect == RectValue(10.0, 20.0, 30.0, 40.0)
    assert board.cell_at(2, 1).rect == RectValue(70.0, 60.0, 30.0, 40.0)


def test_cell_returns_top_alive_layer() -> None:
    cell = BlockCell(0, 0, RectValue(0, 0, 10, 10))
    bottom = BlockLayer(id="bottom")
    middle = BlockLayer(id="middle", hp=0, max_hp=1)
    top = BlockLayer(id="top", hp=2, max_hp=2)

    cell.push_layer(bottom)
    cell.push_layer(middle)
    cell.push_layer(top)

    assert cell.top_layer() is top

    top.hp = 0
    assert cell.top_layer() is bottom


def test_collidable_and_visible_layers_are_resolved_independently() -> None:
    cell = BlockCell(0, 0, RectValue(0, 0, 10, 10))
    collision_layer = BlockLayer(id="collision", visible=False)
    visual_layer = BlockLayer(id="visual", collidable=False)

    cell.push_layer(collision_layer)
    cell.push_layer(visual_layer)

    assert cell.top_visible_layer() is visual_layer
    assert cell.top_collidable_layer() is collision_layer


def test_empty_cell_ignores_destroyed_layers() -> None:
    cell = BlockCell(
        0,
        0,
        RectValue(0, 0, 10, 10),
        layers=[BlockLayer(id="gone", hp=0, max_hp=1)],
    )

    assert cell.empty is True


def test_layer_supports_asset_reference_and_source_rect_without_pygame() -> None:
    layer = BlockLayer(
        id="image-piece",
        asset_id="portrait.png",
        source_rect=SourceRectValue(32, 64, 16, 16),
        tags=frozenset({"target", "image"}),
        metadata={"custom": 123},
    )

    assert layer.asset_id == "portrait.png"
    assert layer.source_rect == SourceRectValue(32, 64, 16, 16)
    assert "target" in layer.tags


def test_board_rejects_incomplete_or_duplicate_grid() -> None:
    cell = BlockCell(0, 0, RectValue(0, 0, 10, 10))

    with pytest.raises(ValueError):
        Board(2, 1, [cell])

    with pytest.raises(ValueError):
        Board(2, 1, [cell, cell])


def test_board_non_empty_cells_tracks_layer_stack() -> None:
    board = Board.create_grid(
        columns=2,
        rows=1,
        origin_x=0,
        origin_y=0,
        cell_width=10,
        cell_height=10,
    )
    board.cell_at(1, 0).push_layer(BlockLayer(id="target"))

    assert board.empty is False
    assert board.non_empty_cells() == (board.cell_at(1, 0),)

    board.cell_at(1, 0).top_layer().hp = 0  # type: ignore[union-attr]
    assert board.empty is True


def test_invalid_hp_is_rejected() -> None:
    with pytest.raises(ValueError):
        BlockLayer(id="bad", hp=2, max_hp=1)
