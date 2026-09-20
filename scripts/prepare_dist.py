"""Prepare editable external data beside a PyInstaller onedir executable."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


EXTERNAL_DIRS = ("config", "assets", "stages", "mods", "third_party_licenses")
TOP_LEVEL_FILES = ("README.md", "LICENSE", "THIRD_PARTY_NOTICES.md")


def prepare_distribution(project_root: Path, dist_root: Path) -> None:
    project_root = project_root.resolve()
    dist_root = dist_root.resolve()
    dist_root.mkdir(parents=True, exist_ok=True)

    for name in EXTERNAL_DIRS:
        source = project_root / name
        target = dist_root / name
        if not source.is_dir():
            raise FileNotFoundError(f"required external directory not found: {source}")
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)

    for name in TOP_LEVEL_FILES:
        source = project_root / name
        if not source.is_file():
            raise FileNotFoundError(f"required distribution file not found: {source}")
        shutil.copy2(source, dist_root / name)

    (dist_root / "userdata").mkdir(parents=True, exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--dist-root", type=Path, required=True)
    args = parser.parse_args()
    prepare_distribution(args.project_root, args.dist_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
