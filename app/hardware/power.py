"""Graceful shutdown support.

Coordinates stopping new sessions, flushing disk writes, stopping the
sharing server, releasing the camera, turning off lights, and finally
issuing a Linux shutdown -- only on real hardware.
"""
from __future__ import annotations

import logging
import platform
import subprocess

logger = logging.getLogger(__name__)


class PowerService:
    def shutdown_system(self) -> None:
        if platform.system() != "Linux":
            logger.info("PowerService: not on Linux, skipping system shutdown")
            return
        try:
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        except Exception:
            logger.exception("Failed to issue system shutdown")
