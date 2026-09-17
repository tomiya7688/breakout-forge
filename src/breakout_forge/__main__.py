"""Breakout Forge executable entry point."""

from breakout_forge.app import create_application


def main() -> int:
    return create_application().run()


if __name__ == "__main__":
    raise SystemExit(main())
