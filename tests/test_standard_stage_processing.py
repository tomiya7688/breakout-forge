from breakout_forge.contracts.frame import FrameRequest
from breakout_forge.contracts.game_state import GameState
from breakout_forge.contracts.layer_damage import LayerDamageResult
from breakout_forge.contracts.settings import (
    GameplaySettings,
    GridSettings,
    PlayfieldSettings,
    SizeSettings,
    StandardStageSettings,
    VectorSettings,
)
from breakout_forge.process.processing.collision import BoardCollisionResult
from breakout_forge.process.processing.frame_processing import FrameProcessing
from breakout_forge.process.processing.paddle_ball_processing import PaddleBallProcessing
from breakout_forge.process.processing.standard_stage_processing import StandardStageProcessing


def _stage(
    *,
    columns: int = 2,
    rows: int = 2,
    block_hp: int = 1,
    score_per_layer: int = 100,
) -> StandardStageProcessing:
    return StandardStageProcessing(
        GridSettings(columns=columns, rows=rows),
        StandardStageSettings(
            left_margin=20,
            right_margin=20,
            top_margin=30,
            block_area_height=80,
            gap_x=2,
            gap_y=2,
            block_hp=block_hp,
            score_per_layer=score_per_layer,
        ),
        PlayfieldSettings(width=400, height=300, fit="contain"),
    )


def test_standard_stage_builds_board_from_stage_size() -> None:
    stage = _stage(columns=3, rows=4, block_hp=2)

    assert stage.board.columns == 3
    assert stage.board.rows == 4
    assert len(stage.board.non_empty_cells()) == 12
    assert all(
        cell.top_layer() is not None and cell.top_layer().hp == 2
        for cell in stage.board.cells()
    )


def test_destroyed_layer_adds_score() -> None:
    stage = _stage(score_per_layer=250)

    stage.register_collisions(
        (
            BoardCollisionResult(
                collided=True,
                column=0,
                row=0,
                damage=LayerDamageResult(
                    column=0,
                    row=0,
                    target_layer_id="standard-0-0",
                    damage_requested=1,
                    damage_applied=1,
                    hp_before=1,
                    hp_after=0,
                    layer_destroyed=True,
                    cell_empty=True,
                    next_layer_id=None,
                ),
            ),
        )
    )

    assert stage.score == 250


def test_reset_restores_blocks_and_score() -> None:
    stage = _stage(columns=1, rows=1)
    cell = stage.board.cell_at(0, 0)
    cell.top_layer().hp = 0
    stage.register_collisions(
        (
            BoardCollisionResult(
                collided=True,
                column=0,
                row=0,
                damage=LayerDamageResult(
                    column=0,
                    row=0,
                    target_layer_id="standard-0-0",
                    damage_requested=1,
                    damage_applied=1,
                    hp_before=1,
                    hp_after=0,
                    layer_destroyed=True,
                    cell_empty=True,
                    next_layer_id=None,
                ),
            ),
        )
    )
    assert stage.cleared
    assert stage.score == 100

    old_board = stage.board
    new_board = stage.reset()

    assert new_board is stage.board
    assert new_board is not old_board
    assert not stage.cleared
    assert stage.score == 0
    assert stage.board.cell_at(0, 0).top_layer().hp == 1


def test_frame_clear_and_restart_rebuild_standard_stage() -> None:
    playfield = PlayfieldSettings(width=400, height=300, fit="contain")
    stage = StandardStageProcessing(
        GridSettings(columns=1, rows=1),
        StandardStageSettings(
            left_margin=190,
            right_margin=180,
            top_margin=220,
            block_area_height=20,
            gap_x=1,
            gap_y=1,
            block_hp=1,
            score_per_layer=100,
        ),
        playfield,
    )
    paddle_ball = PaddleBallProcessing(
        GameplaySettings(
            ball_speed=100.0,
            ball_size=10,
            ball_initial_direction=VectorSettings(x=1.0, y=-1.0),
            paddle_speed=200.0,
            paddle_size=SizeSettings(width=80, height=10),
            paddle_bottom_margin=20,
        ),
        playfield,
        board=stage.board,
    )
    frame = FrameProcessing(
        paddle_ball_processing=paddle_ball,
        stage_processing=stage,
    )

    result = frame.execute(
        FrameRequest(delta_seconds=0.25, start_requested=True)
    )

    assert result.state is GameState.CLEAR
    assert result.gameplay is not None
    assert result.gameplay.score == 100
    assert result.gameplay.blocks == ()

    restarted = frame.execute(
        FrameRequest(delta_seconds=0.0, restart_requested=True)
    )

    assert restarted.state is GameState.READY
    assert restarted.gameplay is not None
    assert restarted.gameplay.score == 0
    assert len(restarted.gameplay.blocks) == 1
