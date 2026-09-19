"""Release-gate acceptance checks against the built Windows distribution."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile


class ReleaseAcceptanceError(RuntimeError):
    pass


def _run(
    executable: Path,
    *args: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(executable), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise ReleaseAcceptanceError(
            f"command failed ({result.returncode}): {executable.name} {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def verify_release_distribution(dist_root: Path, expected_version: str) -> None:
    root = dist_root.resolve()
    exe = root / "BreakoutForge.exe"

    required = (
        exe,
        root / "_internal",
        root / "config" / "common.json",
        root / "assets",
        root / "stages",
        root / "mods",
        root / "userdata",
        root / "README.md",
        root / "LICENSE",
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise ReleaseAcceptanceError("missing release paths: " + ", ".join(missing))

    version = _run(exe, "--version")
    expected_line = f"BreakoutForge {expected_version}"
    if version.stdout.strip() != expected_line:
        raise ReleaseAcceptanceError(
            f"version output mismatch: expected {expected_line!r}, got {version.stdout.strip()!r}"
        )

    _run(exe, "--smoke-test")

    for stage_id in ("standard_sample", "sample", "layered_sample"):
        _run(exe, "--validate-stage", stage_id)

    # Explicit-path input must behave the same as stage-id input.
    _run(exe, "--validate-stage", r"stages\sample\stage.json")

    # The packaged executable must not depend on the caller's current directory.
    with tempfile.TemporaryDirectory() as temp_cwd:
        foreign_cwd = Path(temp_cwd)
        _run(exe, "--smoke-test", cwd=foreign_cwd)
        _run(exe, "--validate-stage", "sample", cwd=foreign_cwd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist-root", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()

    verify_release_distribution(args.dist_root, args.expected_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
