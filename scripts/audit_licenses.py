"""Audit repository assets and required third-party license notices."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path


MEDIA_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico", ".bmp",
    ".wav", ".ogg", ".mp3", ".flac",
    ".ttf", ".otf", ".woff", ".woff2",
}

REQUIRED_LICENSE_FILES = (
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "third_party_licenses/Python-LICENSE.txt",
    "third_party_licenses/Pillow-LICENSE.txt",
    "third_party_licenses/PyInstaller-COPYING.txt",
    "third_party_licenses/pygame-LGPL-2.1.txt",
)

REQUIRED_PYGAME_DEPENDENCY_NOTICES = {
    "LICENSE.FLAC.txt",
    "LICENSE.fluidsynth.txt",
    "LICENSE.freetype.txt",
    "LICENSE.jpeg.txt",
    "LICENSE.modplug.txt",
    "LICENSE.mpg123.txt",
    "LICENSE.numpy.txt",
    "LICENSE.ogg-vorbis.txt",
    "LICENSE.opus.txt",
    "LICENSE.opusfile.txt",
    "LICENSE.png.txt",
    "LICENSE.portmidi.txt",
    "LICENSE.sdl2.txt",
    "LICENSE.sdl2_image.txt",
    "LICENSE.sdl2_mixer.txt",
    "LICENSE.sdl_gfx.txt",
    "LICENSE.sse2neon-h.txt",
    "LICENSE.tiff.txt",
    "LICENSE.webp.txt",
    "LICENSE.zlib.txt",
}


class LicenseAuditError(RuntimeError):
    pass


def _repository_media(project_root: Path) -> set[str]:
    found: set[str] = set()
    for base_name in ("assets", "stages"):
        base = project_root / base_name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS:
                found.add(path.relative_to(project_root).as_posix())
    return found


def audit_repository_licenses(project_root: Path) -> None:
    root = project_root.resolve()

    for relative in REQUIRED_LICENSE_FILES:
        path = root / relative
        if not path.is_file():
            raise LicenseAuditError(f"required license file missing: {relative}")

    project_license = (root / "LICENSE").read_text(encoding="utf-8")
    if not project_license.startswith("MIT License"):
        raise LicenseAuditError("project LICENSE is not the expected MIT License")

    provenance_path = root / "release" / "asset-provenance.json"
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LicenseAuditError("failed to read asset provenance manifest") from exc

    if provenance.get("format_version") != 1:
        raise LicenseAuditError("unsupported asset provenance format_version")
    entries = provenance.get("assets")
    if not isinstance(entries, list):
        raise LicenseAuditError("asset provenance assets must be an array")

    declared: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise LicenseAuditError(f"asset provenance entry {index} must be an object")
        path = entry.get("path")
        origin = entry.get("origin")
        license_name = entry.get("license")
        if not isinstance(path, str) or not path:
            raise LicenseAuditError(f"asset provenance entry {index} has invalid path")
        if not isinstance(origin, str) or not origin:
            raise LicenseAuditError(f"asset provenance entry {index} has no origin")
        if not isinstance(license_name, str) or not license_name:
            raise LicenseAuditError(f"asset provenance entry {index} has no license")
        if path in declared:
            raise LicenseAuditError(f"duplicate asset provenance path: {path}")
        declared.add(path)
        if not (root / path).is_file():
            raise LicenseAuditError(f"declared asset does not exist: {path}")

    actual = _repository_media(root)
    undeclared = sorted(actual - declared)
    stale = sorted(declared - actual)
    if undeclared:
        raise LicenseAuditError(
            "media assets missing provenance declarations: " + ", ".join(undeclared)
        )
    if stale:
        raise LicenseAuditError(
            "provenance entries do not point to distributable media: " + ", ".join(stale)
        )

    pygame_notice_dir = root / "third_party_licenses" / "pygame-dependencies"
    actual_pygame_notices = {
        path.name for path in pygame_notice_dir.glob("LICENSE.*.txt") if path.is_file()
    }
    missing_pygame = sorted(REQUIRED_PYGAME_DEPENDENCY_NOTICES - actual_pygame_notices)
    if missing_pygame:
        raise LicenseAuditError(
            "pygame dependency notices missing: " + ", ".join(missing_pygame)
        )

    # Confirm the release environment has the direct runtime/build packages we audit.
    for distribution in ("pygame", "Pillow", "PyInstaller"):
        try:
            importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError as exc:
            raise LicenseAuditError(
                f"audited distribution is not installed: {distribution}"
            ) from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    audit_repository_licenses(args.project_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
