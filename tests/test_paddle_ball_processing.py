from breakout_forge.contracts.settings import (
    GameplaySettings,
    PlayfieldSettings,
    SizeSettings,
    VectorSettings,
)
from breakout_forge.process.model.board import BlockLayer, Board
from breakout_forge.process.processing.paddle_ball_processing import PaddleBallProcessing


def _processing(board: Board | None = None) -> PaddleBallProcessing:
    return PaddleBallProcessing(
        GameplaySettings(
            ball_speed=100.0,
            ball_size=10,
            ball_initial_direction=VectorSettings(x=1.0, y=-1.0),
            paddle_speed=200.0,
            paddle_size=SizeSettings(width=80, height=10),
            paddle_bottom_margin=20,
        ),
        PlayfieldSettings(width=400, height=300, fit="contain"),
        board=board,
    )


def test_paddle_moves_and_is_clamped_to_playfield() -> None:
    processing = _processing()

    processing.update(10.0, move_axis=1.0)
    snapshot = processing.snapshot()

    assert snapshot.paddle.x == 320.0


def test_ball_moves_while_playing_update_runs() -> None:
    processing = _processing()
    before = processing.snapshot().balls[0]

    processing.update(0.1, move_axis=0.0)
    after = processing.snapshot().balls[0]

    assert (after.x, after.y) != (before.x, before.y)


def test_reset_restores_ball_and_paddle() -> None:
    processing = _processing()
    initial = processing.snapshot()
    processing.update(0.5, move_axis=-1.0)

    processing.reset()

    assert processing.snapshot() == initial


def test_update_routes_ball_collision_damage_to_board() -> None:
    board = Board.create_grid(
        columns=1,
        rows=1,
        origin_x=200.0,
        origin_y=240.0,
        cell_width=30.0,
        cell_height=10.0,
    )
    layer = BlockLayer(id="target", hp=2, max_hp=2)
    board.cell_at(0, 0).push_layer(layer)
    processing = _processing(board)

    processing.update(0.1, move_axis=0.0)

    assert layer.hp == 1
    assert len(processing.last_board_collisions) == 1
    collision = processing.last_board_collisions[0]
    assert collision.column == 0
    assert collision.row == 0
    assert collision.damage is not None
    assert collision.damage.target_layer_id == "target"
