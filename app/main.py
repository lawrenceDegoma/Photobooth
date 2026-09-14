"""Entry point: `python -m app.main`."""
from __future__ import annotations

import sys

from app.core.application import PhotoBoothApp


def main() -> int:
    app = PhotoBoothApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
