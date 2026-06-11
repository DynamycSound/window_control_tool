"""Entry point: `python -m window_control_tool` or the packaged exe."""

import sys


def main() -> int:
    from .gui import run
    return run()


if __name__ == "__main__":
    sys.exit(main())
