"""Validate recorded AI and manual UI review evidence before formal release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


class UiReviewError(RuntimeError):
    pass


REVIEW_KEYS = (
    "tester_a_visual_regression",
    "tester_b_vision_ux",
    "tester_c_independent_vision",
    "manual_ui_review",
)


def check_ui_review(report_path: Path, expected_version: str) -> None:
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UiReviewError(f"failed to read UI review report: {report_path}") from exc

    if report.get("format_version") != 1:
        raise UiReviewError("unsupported UI review format_version")
    if report.get("release_version") != expected_version:
        raise UiReviewError(
            f"UI review version mismatch: expected {expected_version}, "
            f"got {report.get('release_version')!r}"
        )

    for key in REVIEW_KEYS:
        review = report.get(key)
        if not isinstance(review, dict):
            raise UiReviewError(f"missing UI review section: {key}")
        if review.get("status") != "approved":
            raise UiReviewError(f"UI review is not approved: {key}")
        if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
            raise UiReviewError(f"UI review has no reviewer: {key}")
        if not isinstance(review.get("evidence"), str) or not review["evidence"].strip():
            raise UiReviewError(f"UI review has no evidence reference: {key}")
        blockers = review.get("release_blockers")
        if blockers != []:
            raise UiReviewError(f"UI review has release blockers: {key}: {blockers!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()
    check_ui_review(args.report, args.expected_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
