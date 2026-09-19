"""Release-gate acceptance checks against the built Windows distribution."""

from __future__ import annotations

import argparse
import json
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
        root / "THIRD_PARTY_NOTICES.md",
        root / "third_party_licenses",
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise ReleaseAcceptanceError("missing release paths: " + ", ".join(missing))

    _run(exe, "--smoke-test")
    _run(exe, "--smoke-test")

    for stage_id in (
        "standard_sample",
        "sample",
        "remove_background_sample",
        "layered_sample",
    ):
        _run(exe, "--validate-stage", stage_id)

    # Explicit-path input must behave the same as stage-id input.
    _run(exe, "--validate-stage", r"stages\sample\stage.json")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        probe_file = temp / "release-probe.json"
        _run(exe, "--release-probe", str(probe_file))
        probe = json.loads(probe_file.read_text(encoding="utf-8"))

        expected_probe = {
            "version": expected_version,
            "base_dir": str(root),
            "smoke_test": "ok",
            "validated_stages": [
                "standard_sample",
                "sample",
                "remove_background_sample",
                "layered_sample",
            ],
            "loaded_mods": ["example_mod"],
            "userdata_exists": True,
        }
        if probe != expected_probe:
            raise ReleaseAcceptanceError(
                f"release probe mismatch:\nexpected={expected_probe!r}\nactual={probe!r}"
            )

        # The packaged executable must not depend on the caller's current directory.
        foreign_cwd = temp / "foreign-cwd"
        foreign_cwd.mkdir()
        foreign_probe = temp / "foreign-release-probe.json"
        _run(exe, "--smoke-test", cwd=foreign_cwd)
        _run(exe, "--validate-stage", "sample", cwd=foreign_cwd)
        _run(exe, "--release-probe", str(foreign_probe), cwd=foreign_cwd)
        foreign = json.loads(foreign_probe.read_text(encoding="utf-8"))
        if foreign != expected_probe:
            raise ReleaseAcceptanceError(
                "release probe changed when launched from a foreign working directory"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist-root", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()

    verify_release_distribution(args.dist_root, args.expected_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
