from breakout_forge.contracts.frame import FrameRequest
from breakout_forge.contracts.game_state import GameState
from breakout_forge.process.processing.frame_processing import FrameProcessing
from breakout_forge.process.processing.state_processing import StateProcessing


def test_state_starts_ready_and_enters_playing() -> None:
    state = StateProcessing()

    assert state.state is GameState.READY
    assert state.apply_requests(start_requested=True, restart_requested=False) is GameState.PLAYING


def test_clear_and_restart_flow() -> None:
    state = StateProcessing()
    state.apply_requests(start_requested=True, restart_requested=False)

    assert state.mark_clear() is GameState.CLEAR
    assert state.apply_requests(start_requested=False, restart_requested=True) is GameState.READY


def test_game_over_and_restart_flow() -> None:
    state = StateProcessing()
    state.apply_requests(start_requested=True, restart_requested=False)

    assert state.mark_game_over() is GameState.GAME_OVER
    assert state.apply_requests(start_requested=False, restart_requested=True) is GameState.READY


def test_frame_processing_reports_current_state() -> None:
    processing = FrameProcessing()

    ready = processing.execute(FrameRequest(delta_seconds=0.016))
    playing = processing.execute(
        FrameRequest(delta_seconds=0.016, start_requested=True)
    )

    assert ready.state is GameState.READY
    assert playing.state is GameState.PLAYING


def test_negative_delta_is_rejected() -> None:
    processing = FrameProcessing()

    try:
        processing.execute(FrameRequest(delta_seconds=-0.1))
    except ValueError:
        pass
    else:
        raise AssertionError("negative delta_seconds must be rejected")
