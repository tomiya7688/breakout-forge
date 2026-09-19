import json
from pathlib import Path

import pytest

from scripts.audit_licenses import LicenseAuditError, audit_repository_licenses


def _minimal_license_layout(root: Path) -> None:
    (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    (root / "THIRD_PARTY_NOTICES.md").write_text("notices", encoding="utf-8")
    third = root / "third_party_licenses"
    third.mkdir(parents=True)
    for name in (
        "Python-LICENSE.txt",
        "Pillow-LICENSE.txt",
        "PyInstaller-COPYING.txt",
        "pygame-LGPL-2.1.txt",
    ):
        (third / name).write_text("license", encoding="utf-8")

    pygame = third / "pygame-dependencies"
    pygame.mkdir()
    from scripts.audit_licenses import REQUIRED_PYGAME_DEPENDENCY_NOTICES

    for name in REQUIRED_PYGAME_DEPENDENCY_NOTICES:
        (pygame / name).write_text("license", encoding="utf-8")


def test_license_audit_rejects_undeclared_media(tmp_path: Path, monkeypatch) -> None:
    _minimal_license_layout(tmp_path)
    image = tmp_path / "stages" / "sample" / "main.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"sample")

    release = tmp_path / "release"
    release.mkdir()
    (release / "asset-provenance.json").write_text(
        '{"format_version":1,"assets":[]}',
        encoding="utf-8",
    )

    monkeypatch.setattr("importlib.metadata.version", lambda name: "test")

    with pytest.raises(LicenseAuditError, match="missing provenance"):
        audit_repository_licenses(tmp_path)


def test_license_audit_accepts_declared_media(tmp_path: Path, monkeypatch) -> None:
    _minimal_license_layout(tmp_path)
    image = tmp_path / "stages" / "sample" / "main.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"sample")

    release = tmp_path / "release"
    release.mkdir()
    (release / "asset-provenance.json").write_text(
        json.dumps(
            {
                "format_version": 1,
                "assets": [
                    {
                        "path": "stages/sample/main.png",
                        "origin": "test generated asset",
                        "license": "MIT",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("importlib.metadata.version", lambda name: "test")

    audit_repository_licenses(tmp_path)
