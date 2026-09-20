from pathlib import Path

from breakout_forge.__main__ import _stage_argument


def test_stage_argument_expands_simple_stage_id() -> None:
    assert _stage_argument("sample") == Path("stages") / "sample" / "stage.json"


def test_stage_argument_keeps_explicit_json_path() -> None:
    path = Path("custom") / "stage.json"
    assert _stage_argument(str(path)) == path


def test_stage_argument_keeps_path_with_separator() -> None:
    path = Path("stages") / "sample" / "custom-stage"
    assert _stage_argument(str(path)) == path


def test_stage_argument_keeps_windows_separator_path() -> None:
    raw = r"stages\sample\stage.json"
    assert _stage_argument(raw) == Path(raw)
