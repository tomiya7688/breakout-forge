from pathlib import Path
import tomllib

import pytest

from breakout_forge import __version__
from breakout_forge.__main__ import main
from scripts.check_release_version import verify_release_version


def test_v1_version_source() -> None:
    assert __version__ == "1.0.0"


def test_release_tag_must_match_version() -> None:
    verify_release_version(f"v{__version__}")

    with pytest.raises(ValueError, match="tag/version mismatch"):
        verify_release_version("v9.9.9")


def test_pyproject_uses_dynamic_package_version() -> None:
    pyproject = Path("pyproject.toml")
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    assert "version" not in data["project"]
    assert "version" in data["project"]["dynamic"]
    assert (
        data["tool"]["setuptools"]["dynamic"]["version"]["attr"]
        == "breakout_forge.__version__"
    )


def test_source_version_cli(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])

    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"BreakoutForge {__version__}"
