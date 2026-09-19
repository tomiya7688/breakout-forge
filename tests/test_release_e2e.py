import logging
from pathlib import Path

from breakout_forge.contracts.frame import FrameRequest
from breakout_forge.contracts.game_state import GameState
from breakout_forge.contracts.mod_event import ModEventName
from breakout_forge.contracts.settings import (
    GameplaySettings,
    GridSettings,
    PlayfieldSettings,
    SizeSettings,
    StandardStageSettings,
    VectorSettings,
)
from breakout_forge.data.commander import DataCommander
from breakout_forge.data.messenger import DataMessenger
from breakout_forge.modding.api import ModApi
from breakout_forge.process.processing.frame_processing import FrameProcessing
from breakout_forge.process.processing.image_stage_processing import ImageStageProcessing
from breakout_forge.process.processing.layer_damage_processing import LayerDamageProcessing
from breakout_forge.process.processing.paddle_ball_processing import PaddleBallProcessing
from breakout_forge.process.processing.standard_stage_processing import StandardStageProcessing


ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "config" / "common.json"


def _load_stage(stage_id: str):
    data = DataMessenger(DataCommander())
    stage = data.load_stage(COMMON, ROOT / "stages" / stage_id / "stage.json")
    assets = tuple(
        data.prepare_image(layer, stage.settings.break_image)
        for layer in stage.layers
        if layer.image_path is not None
    )
    return stage, assets


def test_release_e2e_repository_stages_load_through_real_data_pipeline() -> None:
    for stage_id in (
        "standard_sample",
        "sample",
        "remove_background_sample",
        "layered_sample",
    ):
        stage, assets = _load_stage(stage_id)
        assert stage.id == stage_id
        if stage.layers:
            assert assets


def test_release_e2e_remove_background_changes_destructible_tiles() -> None:
    keep_stage, keep_assets = _load_stage("sample")
    remove_stage, remove_assets = _load_stage("remove_background_sample")

    keep = keep_assets[0]
    removed = remove_assets[0]

    assert keep.width == removed.width
    assert keep.height == removed.height
    assert keep_stage.settings.break_image.load_mode == "keep_background"
    assert remove_stage.settings.break_image.load_mode == "remove_background"
    assert len(removed.active_tiles) <= len(keep.active_tiles)


def test_release_e2e_layered_hp_reveal_and_restart() -> None:
    stage, assets = _load_stage("layered_sample")
    layers = tuple(layer for layer in stage.layers if layer.image_path is not None)
    runtime = ImageStageProcessing(
        stage,
        layers,
        assets,
        stage.settings.playfield,
        stage.settings.standard_stage,
    )

    cell = next(
        cell
        for cell in runtime.board.non_empty_cells()
        if len(cell.layers) >= 2
    )
    assert cell.top_visible_layer().asset_id == "top"
    assert cell.top_visible_layer().hp == 2

    damage = LayerDamageProcessing()
    first = damage.apply(cell)
    assert not first.layer_destroyed
    assert cell.top_visible_layer().asset_id == "top"

    second = damage.apply(cell)
    assert second.layer_destroyed
    assert cell.top_visible_layer().asset_id == "bottom"

    runtime.reset()
    restored = runtime.board.cell_at(cell.column, cell.row)
    assert restored.top_visible_layer().asset_id == "top"
    assert restored.top_visible_layer().hp == 2


def test_release_e2e_clear_restart_and_mod_events() -> None:
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
            ball_paddle_gap=4,
        ),
        playfield,
        board=stage.board,
    )
    events: list[ModEventName] = []
    api = ModApi()
    api._enter_registration("release-e2e")
    for event_name in (
        ModEventName.GAME_START,
        ModEventName.BLOCK_HIT,
        ModEventName.LAYER_DESTROYED,
        ModEventName.CELL_DESTROYED,
        ModEventName.STAGE_CLEARED,
    ):
        api.subscribe(event_name, lambda event, events=events: events.append(event.name))
    api._leave_registration()

    frame = FrameProcessing(
        paddle_ball_processing=paddle_ball,
        stage_processing=stage,
        mod_api=api,
    )
    result = frame.execute(FrameRequest(delta_seconds=0.25, start_requested=True))

    assert result.state is GameState.CLEAR
    assert result.gameplay is not None
    assert result.gameplay.score == 100
    assert ModEventName.GAME_START in events
    assert ModEventName.BLOCK_HIT in events
    assert ModEventName.LAYER_DESTROYED in events
    assert ModEventName.CELL_DESTROYED in events
    assert ModEventName.STAGE_CLEARED in events

    restarted = frame.execute(FrameRequest(delta_seconds=0.0, restart_requested=True))
    assert restarted.state is GameState.READY
    assert restarted.gameplay is not None
    assert restarted.gameplay.score == 0
    assert len(restarted.gameplay.blocks) == 1


def test_release_e2e_game_over_and_mod_event() -> None:
    playfield = PlayfieldSettings(width=120, height=100, fit="contain")
    paddle_ball = PaddleBallProcessing(
        GameplaySettings(
            ball_speed=20.0,
            ball_size=6,
            ball_initial_direction=VectorSettings(x=0.2, y=1.0),
            paddle_speed=1000.0,
            paddle_size=SizeSettings(width=8, height=6),
            paddle_bottom_margin=6,
            ball_paddle_gap=2,
        ),
        playfield,
    )
    events: list[ModEventName] = []
    api = ModApi()
    api._enter_registration("release-e2e")
    api.subscribe(
        ModEventName.GAME_OVER,
        lambda event: events.append(event.name),
    )
    api._leave_registration()

    frame = FrameProcessing(
        paddle_ball_processing=paddle_ball,
        mod_api=api,
    )

    result = frame.execute(
        FrameRequest(
            delta_seconds=0.05,
            start_requested=True,
            move_axis=-1.0,
        )
    )
    assert result.state is GameState.PLAYING

    for _ in range(200):
        result = frame.execute(FrameRequest(delta_seconds=0.05))
        if result.state is GameState.GAME_OVER:
            break

    assert result.state is GameState.GAME_OVER
    assert ModEventName.GAME_OVER in events

    restarted = frame.execute(FrameRequest(delta_seconds=0.0, restart_requested=True))
    assert restarted.state is GameState.READY


def test_release_e2e_example_mod_imports_and_registers() -> None:
    data = DataMessenger(DataCommander())
    api = ModApi()
    loaded = data.load_mods(ROOT / "mods", api)

    assert "example_mod" in {mod.id for mod in loaded}



def test_release_e2e_broken_mod_does_not_block_good_mod(
    tmp_path: Path,
    caplog,
) -> None:
    mods = tmp_path / "mods"

    broken = mods / "broken"
    broken.mkdir(parents=True)
    (broken / "mod.json").write_text(
        '{"format_version":1,"id":"broken","name":"Broken","version":"1.0","entry":"main.py"}',
        encoding="utf-8",
    )
    (broken / "main.py").write_text(
        "def setup(api):\n    raise RuntimeError('release e2e broken mod')\n",
        encoding="utf-8",
    )

    good = mods / "good"
    good.mkdir(parents=True)
    (good / "mod.json").write_text(
        '{"format_version":1,"id":"good","name":"Good","version":"1.0","entry":"main.py"}',
        encoding="utf-8",
    )
    (good / "main.py").write_text(
        "def setup(api):\n    api.subscribe('on_game_start', lambda event: None)\n",
        encoding="utf-8",
    )

    caplog.set_level(logging.ERROR, logger="breakout_forge.mods")
    loaded = DataMessenger(DataCommander()).load_mods(mods, ModApi())

    assert [mod.id for mod in loaded] == ["good"]
    assert "MOD load failed" in caplog.text
    assert "release e2e broken mod" in caplog.text
