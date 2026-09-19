"""Reject formal releases with unresolved blocker or must-fix bugs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


class ReleaseBlockerError(RuntimeError):
    pass


BLOCKING_SEVERITIES = {"release_blocker", "must_fix"}
ALLOWED_SEVERITIES = BLOCKING_SEVERITIES | {"known_issue"}
ALLOWED_STATUSES = {"open", "fixed", "accepted"}


def check_release_blockers(path: Path, expected_version: str) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseBlockerError(f"failed to read known-issue ledger: {path}") from exc

    if data.get("format_version") != 1:
        raise ReleaseBlockerError("unsupported known-issue format_version")
    if data.get("release_version") != expected_version:
        raise ReleaseBlockerError(
            f"known-issue version mismatch: expected {expected_version}, "
            f"got {data.get('release_version')!r}"
        )

    issues = data.get("issues")
    if not isinstance(issues, list):
        raise ReleaseBlockerError("known-issue issues must be an array")

    blocking: list[str] = []
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ReleaseBlockerError(f"known-issue entry {index} must be an object")
        issue_id = issue.get("id")
        severity = issue.get("severity")
        status = issue.get("status")
        summary = issue.get("summary")
        if not isinstance(issue_id, str) or not issue_id.strip():
            raise ReleaseBlockerError(f"known-issue entry {index} has invalid id")
        if severity not in ALLOWED_SEVERITIES:
            raise ReleaseBlockerError(
                f"known-issue {issue_id} has invalid severity: {severity!r}"
            )
        if status not in ALLOWED_STATUSES:
            raise ReleaseBlockerError(
                f"known-issue {issue_id} has invalid status: {status!r}"
            )
        if not isinstance(summary, str) or not summary.strip():
            raise ReleaseBlockerError(f"known-issue {issue_id} has no summary")
        if severity in BLOCKING_SEVERITIES and status == "open":
            blocking.append(f"{issue_id}: {summary}")

    if blocking:
        raise ReleaseBlockerError(
            "unresolved release blockers/must-fix bugs: " + "; ".join(blocking)
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()
    check_release_blockers(args.ledger, args.expected_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
