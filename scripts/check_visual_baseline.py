"""Fail when deterministic release screenshots differ from the approved visual baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


class VisualRegressionError(RuntimeError):
    pass


def check_visual_baseline(images_dir: Path, baseline_path: Path, expected_version: str) -> None:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    if baseline.get("format_version") != 1:
        raise VisualRegressionError("unsupported visual baseline format_version")
    if baseline.get("release_version") != expected_version:
        raise VisualRegressionError("visual baseline release version mismatch")

    expected = baseline.get("screenshots")
    if not isinstance(expected, dict) or not expected:
        raise VisualRegressionError("visual baseline has no screenshots")

    actual_names = {p.name for p in images_dir.glob("*.png")}
    expected_names = set(expected)
    if actual_names != expected_names:
        raise VisualRegressionError(
            f"visual screenshot set changed: expected={sorted(expected_names)!r} "
            f"actual={sorted(actual_names)!r}"
        )

    changed: list[str] = []
    for name, digest in expected.items():
        actual = hashlib.sha256((images_dir / name).read_bytes()).hexdigest()
        if actual != digest:
            changed.append(f"{name}: expected={digest} actual={actual}")

    if changed:
        raise VisualRegressionError(
            "visual regression detected; review and intentionally update baseline if valid:\n"
            + "\n".join(changed)
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()
    check_visual_baseline(args.images, args.baseline, args.expected_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
