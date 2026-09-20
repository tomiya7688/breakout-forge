import json
from pathlib import Path

import pytest

from scripts.check_release_blockers import (
    ReleaseBlockerError,
    check_release_blockers,
)


def _write(path: Path, issues: list[dict]) -> None:
    path.write_text(
        json.dumps(
            {
                "format_version": 1,
                "release_version": "1.0.0",
                "issues": issues,
            }
        ),
        encoding="utf-8",
    )


def test_open_release_blocker_fails(tmp_path: Path) -> None:
    path = tmp_path / "known.json"
    _write(
        path,
        [
            {
                "id": "BUG-1",
                "severity": "release_blocker",
                "status": "open",
                "summary": "game cannot start",
            }
        ],
    )

    with pytest.raises(ReleaseBlockerError, match="game cannot start"):
        check_release_blockers(path, "1.0.0")


def test_open_must_fix_fails(tmp_path: Path) -> None:
    path = tmp_path / "known.json"
    _write(
        path,
        [
            {
                "id": "BUG-2",
                "severity": "must_fix",
                "status": "open",
                "summary": "restart loses stage data",
            }
        ],
    )

    with pytest.raises(ReleaseBlockerError, match="restart loses stage data"):
        check_release_blockers(path, "1.0.0")


def test_known_issue_may_remain_open(tmp_path: Path) -> None:
    path = tmp_path / "known.json"
    _write(
        path,
        [
            {
                "id": "BUG-3",
                "severity": "known_issue",
                "status": "open",
                "summary": "minor cosmetic issue with workaround",
            }
        ],
    )

    check_release_blockers(path, "1.0.0")


def test_fixed_blocker_does_not_block_release(tmp_path: Path) -> None:
    path = tmp_path / "known.json"
    _write(
        path,
        [
            {
                "id": "BUG-4",
                "severity": "release_blocker",
                "status": "fixed",
                "summary": "fixed crash",
            }
        ],
    )

    check_release_blockers(path, "1.0.0")
