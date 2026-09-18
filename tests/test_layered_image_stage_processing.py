from pathlib import Path

import pytest

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


def _settings() -> ResolvedStageSettings:
    return ResolvedStageSettings(
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
        stage_size=GridSettings(columns=10, rows=10),
        standard_stage=StandardStageSettings(
            left_margin=20,
            right_margin=20,
            top_margin=30,
            block_area_height=100,
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


def _layer(layer_id: str, hp: int = 1) -> StageLayerDefinition:
    return StageLayerDefinition(
        id=layer_id,
        image_path=Path(f"{layer_id}.png"),
        hp=hp,
        collidable=True,
        destructible=True,
        visible=True,
    )


def test_layers_are_stacked_bottom_to_top_and_top_is_visible() -> None:
    settings = _settings()
    bottom = _layer("bottom")
    top = _layer("top", hp=2)
    stage = ResolvedStageDefinition(
        id="layered",
        name="Layered",
        directory=Path("."),
        settings=settings,
        layers=(bottom, top),
    )
    bottom_asset = PreparedImageAsset(
        id="bottom",
        width=8,
        height=4,
        rgba=bytes(8 * 4 * 4),
        active_tiles=frozenset({(0, 0), (1, 0)}),
    )
    top_asset = PreparedImageAsset(
        id="top",
        width=16,
        height=8,
        rgba=bytes(16 * 8 * 4),
        active_tiles=frozenset({(0, 0), (1, 0)}),
    )

    runtime = ImageStageProcessing(
        stage,
        (bottom, top),
        (bottom_asset, top_asset),
        settings.playfield,
        settings.standard_stage,
    )

    cell = runtime.board.cell_at(0, 0)
    assert [layer.asset_id for layer in cell.layers] == ["bottom", "top"]
    assert cell.top_visible_layer().asset_id == "top"
    assert runtime.block_snapshots()[0].asset_id == "top"


def test_hp_top_layer_reveals_lower_layer_only_after_destroyed() -> None:
    settings = _settings()
    bottom = _layer("bottom")
    top = _layer("top", hp=2)
    stage = ResolvedStageDefinition(
        id="layered",
        name="Layered",
        directory=Path("."),
        settings=settings,
        layers=(bottom, top),
    )
    assets = (
        PreparedImageAsset(
            id="bottom",
            width=8,
            height=4,
            rgba=bytes(8 * 4 * 4),
            active_tiles=frozenset({(0, 0), (1, 0)}),
        ),
        PreparedImageAsset(
            id="top",
            width=16,
            height=8,
            rgba=bytes(16 * 8 * 4),
            active_tiles=frozenset({(0, 0), (1, 0)}),
        ),
    )
    runtime = ImageStageProcessing(
        stage,
        (bottom, top),
        assets,
        settings.playfield,
        settings.standard_stage,
    )
    cell = runtime.board.cell_at(0, 0)
    damage = LayerDamageProcessing()

    first = damage.apply(cell)
    assert not first.layer_destroyed
    assert cell.top_visible_layer().asset_id == "top"

    second = damage.apply(cell)
    assert second.layer_destroyed
    assert cell.top_visible_layer().asset_id == "bottom"
    snapshot = next(item for item in runtime.block_snapshots() if item.column == 0)
    assert snapshot.asset_id == "bottom"


def test_empty_top_tile_exposes_lower_from_start() -> None:
    settings = _settings()
    bottom = _layer("bottom")
    top = _layer("top")
    stage = ResolvedStageDefinition(
        id="layered",
        name="Layered",
        directory=Path("."),
        settings=settings,
        layers=(bottom, top),
    )
    runtime = ImageStageProcessing(
        stage,
        (bottom, top),
        (
            PreparedImageAsset(
                id="bottom",
                width=8,
                height=4,
                rgba=bytes(8 * 4 * 4),
                active_tiles=frozenset({(0, 0), (1, 0)}),
            ),
            PreparedImageAsset(
                id="top",
                width=16,
                height=8,
                rgba=bytes(16 * 8 * 4),
                active_tiles=frozenset({(1, 0)}),
            ),
        ),
        settings.playfield,
        settings.standard_stage,
    )

    assert runtime.board.cell_at(0, 0).top_visible_layer().asset_id == "bottom"
    assert runtime.board.cell_at(1, 0).top_visible_layer().asset_id == "top"


def test_different_resolution_same_aspect_ratio_is_allowed() -> None:
    settings = _settings()
    bottom = _layer("bottom")
    top = _layer("top")
    stage = ResolvedStageDefinition(
        id="layered",
        name="Layered",
        directory=Path("."),
        settings=settings,
        layers=(bottom, top),
    )

    runtime = ImageStageProcessing(
        stage,
        (bottom, top),
        (
            PreparedImageAsset(
                id="bottom",
                width=8,
                height=4,
                rgba=bytes(8 * 4 * 4),
                active_tiles=frozenset({(0, 0), (1, 0)}),
            ),
            PreparedImageAsset(
                id="top",
                width=20,
                height=10,
                rgba=bytes(20 * 10 * 4),
                active_tiles=frozenset({(0, 0), (1, 0)}),
            ),
        ),
        settings.playfield,
        settings.standard_stage,
    )

    bottom_source = runtime.board.cell_at(0, 0).layers[0].source_rect
    top_source = runtime.board.cell_at(0, 0).layers[1].source_rect
    assert bottom_source.width == 4
    assert top_source.width == 10


def test_different_aspect_ratio_is_rejected() -> None:
    settings = _settings()
    bottom = _layer("bottom")
    top = _layer("top")
    stage = ResolvedStageDefinition(
        id="layered",
        name="Layered",
        directory=Path("."),
        settings=settings,
        layers=(bottom, top),
    )

    with pytest.raises(ValueError, match="aspect ratio"):
        ImageStageProcessing(
            stage,
            (bottom, top),
            (
                PreparedImageAsset(
                    id="bottom",
                    width=8,
                    height=4,
                    rgba=bytes(8 * 4 * 4),
                    active_tiles=frozenset({(0, 0), (1, 0)}),
                ),
                PreparedImageAsset(
                    id="top",
                    width=8,
                    height=8,
                    rgba=bytes(8 * 8 * 4),
                    active_tiles=frozenset({(0, 0), (1, 0)}),
                ),
            ),
            settings.playfield,
            settings.standard_stage,
        )


def test_reset_restores_all_layers_and_hp() -> None:
    settings = _settings()
    bottom = _layer("bottom")
    top = _layer("top", hp=2)
    stage = ResolvedStageDefinition(
        id="layered",
        name="Layered",
        directory=Path("."),
        settings=settings,
        layers=(bottom, top),
    )
    runtime = ImageStageProcessing(
        stage,
        (bottom, top),
        (
            PreparedImageAsset(
                id="bottom",
                width=8,
                height=4,
                rgba=bytes(8 * 4 * 4),
                active_tiles=frozenset({(0, 0), (1, 0)}),
            ),
            PreparedImageAsset(
                id="top",
                width=16,
                height=8,
                rgba=bytes(16 * 8 * 4),
                active_tiles=frozenset({(0, 0), (1, 0)}),
            ),
        ),
        settings.playfield,
        settings.standard_stage,
    )
    damage = LayerDamageProcessing()
    cell = runtime.board.cell_at(0, 0)
    damage.apply(cell)
    damage.apply(cell)
    assert cell.top_visible_layer().asset_id == "bottom"

    runtime.reset()
    restored = runtime.board.cell_at(0, 0)
    assert [layer.asset_id for layer in restored.layers] == ["bottom", "top"]
    assert restored.top_visible_layer().asset_id == "top"
    assert restored.top_visible_layer().hp == 2
