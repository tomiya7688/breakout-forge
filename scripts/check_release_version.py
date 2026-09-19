"""Verify release tag/version consistency using the package version source of truth."""

from __future__ import annotations

import argparse

from breakout_forge import __version__


def verify_release_version(tag: str) -> None:
    expected_tag = f"v{__version__}"
    if tag != expected_tag:
        raise ValueError(
            f"release tag/version mismatch: tag={tag!r}, expected={expected_tag!r}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    verify_release_version(args.tag)
    print(__version__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
