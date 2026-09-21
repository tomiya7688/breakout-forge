"""Maintainer/CI-only Windows packaging for Breakout Forge."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

from breakout_forge import __version__
from scripts.prepare_dist import prepare_distribution
from scripts.release_acceptance import verify_release_distribution


def _run(*args: str) -> None:
    subprocess.run(args, check=True)


def build_windows(project_root: Path) -> Path:
    root = project_root.resolve()
    if sys.platform != "win32":
        raise RuntimeError("Windows packaging must run on Windows")

    # Fail before PyInstaller if the build environment itself is incomplete.
    import PIL  # noqa: F401
    import pygame  # noqa: F401

    build_dir = root / "build"
    dist_dir = root / "dist"
    target = dist_dir / "BreakoutForge"
    spec = root / "BreakoutForge.spec"

    shutil.rmtree(build_dir, ignore_errors=True)
    shutil.rmtree(target, ignore_errors=True)
    if spec.exists():
        spec.unlink()

    _run(
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--name",
        "BreakoutForge",
        "--contents-directory",
        "_internal",
        "--paths",
        "src",
        "--collect-all",
        "PIL",
        "--collect-all",
        "pygame",
        str(root / "src" / "breakout_forge" / "__main__.py"),
    )

    prepare_distribution(root, target)

    # This is intentionally stronger than a layout-only smoke test.
    # It starts the packaged EXE repeatedly and loads all image-stage types,
    # which proves Pillow is actually bundled.
    verify_release_distribution(target, __version__)

    if spec.exists():
        spec.unlink()
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    build_windows(args.project_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
