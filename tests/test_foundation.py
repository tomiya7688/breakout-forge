from breakout_forge.app import create_application
from breakout_forge.contracts.frame import FrameRequest
from breakout_forge.process.processing.frame_processing import FrameProcessing
from breakout_forge.ui.commander import UiCommander


def test_frame_processing_accepts_non_negative_delta() -> None:
    result = FrameProcessing().execute(FrameRequest(delta_seconds=1 / 60))
    assert result.running is True


def test_frame_processing_rejects_negative_delta() -> None:
    try:
        FrameProcessing().execute(FrameRequest(delta_seconds=-0.1))
    except ValueError as exc:
        assert "non-negative" in str(exc)
    else:
        raise AssertionError("negative delta_seconds must be rejected")


def test_application_composition_returns_ui_commander() -> None:
    app = create_application()
    assert isinstance(app, UiCommander)
