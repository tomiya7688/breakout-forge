from dataclasses import dataclass

from breakout_forge.process.model.board import BlockLayer, Board
from breakout_forge.process.processing.collision import BoardCollisionProcessing


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    size: float


def _single_cell_board(*layers: BlockLayer) -> Board:
    board = Board.create_grid(
        columns=1,
        rows=1,
        origin_x=100.0,
        origin_y=100.0,
        cell_width=40.0,
        cell_height=20.0,
    )
    cell = board.cell_at(0, 0)
    for layer in layers:
        cell.push_layer(layer)
    return board


def test_vertical_collision_reflects_and_damages_top_layer() -> None:
    layer = BlockLayer(id="top", hp=2, max_hp=2)
    board = _single_cell_board(layer)
    ball = Ball(x=110.0, y=92.0, vx=0.0, vy=100.0, size=10.0)

    result = BoardCollisionProcessing().resolve(
        ball,
        board,
        previous_x=110.0,
        previous_y=88.0,
    )

    assert result.collided
    assert result.reflected_y
    assert not result.reflected_x
    assert ball.vy == -100.0
    assert layer.hp == 1
    assert result.damage is not None
    assert result.damage.target_layer_id == "top"


def test_horizontal_collision_reflects_x() -> None:
    layer = BlockLayer(id="block")
    board = _single_cell_board(layer)
    ball = Ball(x=95.0, y=105.0, vx=100.0, vy=0.0, size=10.0)

    result = BoardCollisionProcessing().resolve(
        ball,
        board,
        previous_x=88.0,
        previous_y=105.0,
    )

    assert result.collided
    assert result.reflected_x
    assert not result.reflected_y
    assert ball.vx == -100.0
    assert layer.hp == 0


def test_destroyed_top_layer_exposes_lower_layer_for_next_collision() -> None:
    lower = BlockLayer(id="lower")
    upper = BlockLayer(id="upper")
    board = _single_cell_board(lower, upper)
    processing = BoardCollisionProcessing()

    first_ball = Ball(x=110.0, y=92.0, vx=0.0, vy=100.0, size=10.0)
    first = processing.resolve(
        first_ball,
        board,
        previous_x=110.0,
        previous_y=88.0,
    )
    assert first.damage is not None
    assert first.damage.target_layer_id == "upper"
    assert upper.hp == 0
    assert board.cell_at(0, 0).top_collidable_layer() is lower

    second_ball = Ball(x=110.0, y=92.0, vx=0.0, vy=100.0, size=10.0)
    second = processing.resolve(
        second_ball,
        board,
        previous_x=110.0,
        previous_y=88.0,
    )
    assert second.damage is not None
    assert second.damage.target_layer_id == "lower"
    assert lower.hp == 0
    assert board.cell_at(0, 0).empty


def test_non_collidable_layer_is_skipped() -> None:
    decorative = BlockLayer(id="decorative", collidable=False)
    board = _single_cell_board(decorative)
    ball = Ball(x=110.0, y=92.0, vx=0.0, vy=100.0, size=10.0)

    result = BoardCollisionProcessing().resolve(
        ball,
        board,
        previous_x=110.0,
        previous_y=88.0,
    )

    assert not result.collided
    assert decorative.hp == 1
    assert ball.vy == 100.0


def test_only_one_cell_is_damaged_when_ball_overlaps_multiple_cells() -> None:
    board = Board.create_grid(
        columns=2,
        rows=1,
        origin_x=100.0,
        origin_y=100.0,
        cell_width=20.0,
        cell_height=20.0,
    )
    left = BlockLayer(id="left")
    right = BlockLayer(id="right")
    board.cell_at(0, 0).push_layer(left)
    board.cell_at(1, 0).push_layer(right)
    ball = Ball(x=115.0, y=95.0, vx=0.0, vy=100.0, size=10.0)

    result = BoardCollisionProcessing().resolve(
        ball,
        board,
        previous_x=115.0,
        previous_y=90.0,
    )

    assert result.collided
    destroyed = [layer.id for layer in (left, right) if layer.hp == 0]
    assert len(destroyed) == 1


def test_no_overlap_returns_no_collision() -> None:
    layer = BlockLayer(id="block")
    board = _single_cell_board(layer)
    ball = Ball(x=0.0, y=0.0, vx=10.0, vy=10.0, size=10.0)

    result = BoardCollisionProcessing().resolve(
        ball,
        board,
        previous_x=0.0,
        previous_y=0.0,
    )

    assert not result.collided
    assert layer.hp == 1
