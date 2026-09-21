import json
from pathlib import Path

import pytest

from scripts.capture_release_ui import capture_release_ui
from scripts.check_ui_review import UiReviewError, check_ui_review
from scripts.check_visual_baseline import VisualRegressionError, check_visual_baseline


ROOT = Path(__file__).resolve().parents[1]


def _approved_report(version: str) -> dict:
    def approved(tool: str) -> dict:
        return {
            "tool": tool,
            "status": "approved",
            "reviewer": "release-reviewer",
            "evidence": "artifact://example",
            "release_blockers": [],
        }

    return {
        "format_version": 1,
        "release_version": version,
        "screenshot_manifest": "release-ui/manifest.json",
        "tester_a_visual_regression": approved("Applitools Eyes"),
        "tester_b_vision_ux": approved("Vision AI"),
        "tester_c_independent_vision": approved("Independent Vision AI"),
        "manual_ui_review": approved("Owner"),
    }


def test_ui_review_requires_all_four_approvals(tmp_path: Path) -> None:
    report = _approved_report("1.0.0")
    report["tester_c_independent_vision"]["status"] = "pending"
    path = tmp_path / "review.json"
    path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(UiReviewError, match="not approved"):
        check_ui_review(path, "1.0.0")


def test_ui_review_rejects_release_blocker(tmp_path: Path) -> None:
    report = _approved_report("1.0.0")
    report["tester_b_vision_ux"]["release_blockers"] = ["score overlaps paddle"]
    path = tmp_path / "review.json"
    path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(UiReviewError, match="release blockers"):
        check_ui_review(path, "1.0.0")


def test_ui_review_accepts_complete_evidence(tmp_path: Path) -> None:
    path = tmp_path / "review.json"
    path.write_text(json.dumps(_approved_report("1.0.0")), encoding="utf-8")

    check_ui_review(path, "1.0.0")


def test_release_ui_capture_generates_expected_review_pack(tmp_path: Path) -> None:
    screenshots = capture_release_ui(ROOT, tmp_path)

    expected = {
        "01-ready.png",
        "02-standard-start.png",
        "03-standard-playing.png",
        "04-image-stage.png",
        "05-remove-background.png",
        "06-layered-top.png",
        "07-layered-revealed.png",
        "08-clear.png",
        "09-game-over.png",
    }
    assert {item["file"] for item in screenshots} == expected
    assert expected <= {path.name for path in tmp_path.glob("*.png")}

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["format_version"] == 1
    assert len(manifest["screenshots"]) == 9



def test_manual_only_ui_review_ignores_automated_sections(tmp_path: Path) -> None:
    report = _approved_report("1.0.0")
    report["tester_a_visual_regression"]["status"] = "automatic"
    report["tester_b_vision_ux"]["status"] = "automatic"
    report["tester_c_independent_vision"]["status"] = "automatic"
    path = tmp_path / "review.json"
    path.write_text(json.dumps(report), encoding="utf-8")

    check_ui_review(path, "1.0.0", manual_only=True)


def test_visual_baseline_detects_changed_screenshot(tmp_path: Path) -> None:
    images = tmp_path / "images"
    images.mkdir()
    image = images / "one.png"
    image.write_bytes(b"approved")

    import hashlib

    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "format_version": 1,
                "release_version": "1.0.0",
                "screenshots": {
                    "one.png": hashlib.sha256(b"approved").hexdigest(),
                },
            }
        ),
        encoding="utf-8",
    )

    check_visual_baseline(images, baseline, "1.0.0")

    image.write_bytes(b"changed")
    with pytest.raises(VisualRegressionError, match="visual regression"):
        check_visual_baseline(images, baseline, "1.0.0")
