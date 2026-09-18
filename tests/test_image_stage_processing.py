from pathlib import Path

from breakout_forge.contracts.image_asset import PreparedImageAsset
from breakout_forge.contracts.settings import (
    AppearanceSettings,
    BreakImageSettings,
    DisplaySettings,
    GameplaySettings,
    GridSettings,
    PlayfieldSettings,
    ResolvedStageSettings,
    SizeSettings,
    StandardStageSettings,
    VectorSettings,
)
from breakout_forge.contracts.stage import ResolvedStageDefinition, StageLayerDefinition
from breakout_forge.process.processing.image_stage_processing import ImageStageProcessing
from breakout_forge.process.processing.layer_damage_processing import LayerDamageProcessing


def _stage() -> ResolvedStageDefinition:
    settings = ResolvedStageSettings(
        display=DisplaySettings(width=800, height=600, fps=60, title="Test"),
        gameplay=GameplaySettings(
            ball_speed=360.0,
            ball_size=14,
            ball_initial_direction=VectorSettings(x=1.0, y=-1.0),
            paddle_speed=500.0,
            paddle_size=SizeSettings(width=100, height=18),
            paddle_bottom_margin=30,
            ball_paddle_gap=4,
        ),
        stage_size=GridSettings(columns=9, rows=7),
        standard_stage=StandardStageSettings(
            left_margin=20,
            right_margin=20,
            top_margin=30,
            block_area_height=80,
            gap_x=0,
            gap_y=0,
            block_hp=1,
            score_per_layer=100,
        ),
        appearance=AppearanceSettings(
            background_rgb=(0, 0, 0),
            block_rgb=(1, 1, 1),
            paddle_rgb=(2, 2, 2),
            ball_rgb=(3, 3, 3),
            text_rgb=(4, 4, 4),
            overlay_font_size=36,
            score_font_size=28,
        ),
        break_image=BreakImageSettings(
            split=GridSettings(columns=2, rows=1),
            load_mode="keep_background",
            background_tolerance=16,
        ),
        playfield=PlayfieldSettings(width=400, height=300, fit="contain"),
    )
    layer = StageLayerDefinition(
        id="main",
        image_path=Path("main.png"),
        hp=1,
        collidable=True,
        destructible=True,
        visible=True,
    )
    return ResolvedStageDefinition(
        id="image",
        name="Image",
        directory=Path("."),
        settings=settings,
        layers=(layer,),
    )


def test_image_split_is_independent_from_stage_size() -> None:
    stage = _stage()
    layer = stage.layers[0]
    asset = PreparedImageAsset(
        id="main",
        width=8,
        height=4,
        rgba=bytes(8 * 4 * 4),
        active_tiles=frozenset({(0, 0), (1, 0)}),
    )

    runtime = ImageStageProcessing(
        stage,
        (layer,),
        (asset,),
        stage.settings.playfield,
        stage.settings.standard_stage,
    )

    assert stage.settings.stage_size == GridSettings(columns=9, rows=7)
    assert runtime.board.columns == 2
    assert runtime.board.rows == 1

    left = runtime.board.cell_at(0, 0)
    right = runtime.board.cell_at(1, 0)
    assert left.top_layer().source_rect.x == 0
    assert left.top_layer().source_rect.width == 4
    assert right.top_layer().source_rect.x == 4
    assert right.top_layer().source_rect.width == 4


def test_contain_preserves_source_aspect_ratio() -> None:
    stage = _stage()
    layer = stage.layers[0]
    asset = PreparedImageAsset(
        id="main",
        width=8,
        height=4,
        rgba=bytes(8 * 4 * 4),
        active_tiles=frozenset({(0, 0), (1, 0)}),
    )

    runtime = ImageStageProcessing(
        stage,
        (layer,),
        (asset,),
        stage.settings.playfield,
        stage.settings.standard_stage,
    )

    left = runtime.board.cell_at(0, 0).rect
    right = runtime.board.cell_at(1, 0).rect
    assert left.x == 120.0
    assert left.y == 30.0
    assert left.width == 80.0
    assert left.height == 80.0
    assert right.x == 200.0
    assert right.width == 80.0


def test_destroyed_image_tile_disappears_from_render_snapshot() -> None:
    stage = _stage()
    layer = stage.layers[0]
    asset = PreparedImageAsset(
        id="main",
        width=8,
        height=4,
        rgba=bytes(8 * 4 * 4),
        active_tiles=frozenset({(0, 0), (1, 0)}),
    )
    runtime = ImageStageProcessing(
        stage,
        (layer,),
        (asset,),
        stage.settings.playfield,
        stage.settings.standard_stage,
    )

    assert len(runtime.block_snapshots()) == 2
    LayerDamageProcessing().apply(runtime.board.cell_at(0, 0))

    snapshots = runtime.block_snapshots()
    assert len(snapshots) == 1
    assert snapshots[0].column == 1
    assert snapshots[0].asset_id == "main"
    assert snapshots[0].source_rect.x == 4


def test_background_removed_empty_tiles_create_empty_board_cells() -> None:
    stage = _stage()
    layer = stage.layers[0]
    asset = PreparedImageAsset(
        id="main",
        width=8,
        height=4,
        rgba=bytes(8 * 4 * 4),
        active_tiles=frozenset({(1, 0)}),
    )

    runtime = ImageStageProcessing(
        stage,
        (layer,),
        (asset,),
        stage.settings.playfield,
        stage.settings.standard_stage,
    )

    assert runtime.board.cell_at(0, 0).empty
    assert not runtime.board.cell_at(1, 0).empty
    assert len(runtime.block_snapshots()) == 1
