"""Real Raspberry Pi camera implementation backed by Picamera2.

This module is only importable on the Raspberry Pi (Linux + picamera2
installed). CameraService selects this implementation automatically when
available, falling back to MockCamera otherwise.
"""
from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

from app.camera.camera_interface import CameraInterface
from app.core.config import CameraConfig

logger = logging.getLogger(__name__)


class PiCamera(CameraInterface):
    def __init__(self, config: CameraConfig) -> None:
        self._config = config
        self._picam2 = None
        self._preview_running = False
        self._lock = threading.Lock()
        self._latest_frame = None

    def initialize(self) -> None:
        from picamera2 import Picamera2  # imported lazily; Pi-only dependency

        self._picam2 = Picamera2()
        still_config = self._picam2.create_still_configuration(
            main={"size": (self._config.resolution_width, self._config.resolution_height)},
            lores={"size": (self._config.preview_width, self._config.preview_height)},
            display="lores",
        )
        self._picam2.configure(still_config)
        self._picam2.start()
        logger.info("Pi camera initialized")

    def start_preview(self) -> None:
        self._preview_running = True

    def get_preview_frame(self):
        if not self._preview_running or self._picam2 is None:
            return None
        from PIL import Image

        array = self._picam2.capture_array("lores")
        return Image.fromarray(array)

    def autofocus(self) -> None:
        if self._picam2 is None or not self._config.autofocus:
            return
        try:
            self._picam2.autofocus_cycle()
        except Exception:
            logger.exception("Autofocus failed")

    def capture(self, output_path: str) -> str:
        if self._picam2 is None:
            raise RuntimeError("Camera not initialized")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self._picam2.capture_file(output_path, name="main")
        logger.info("Captured photo to %s", output_path)
        return output_path

    def stop_preview(self) -> None:
        self._preview_running = False

    def shutdown(self) -> None:
        if self._picam2 is not None:
            try:
                self._picam2.stop()
                self._picam2.close()
            except Exception:
                logger.exception("Error shutting down camera")
            self._picam2 = None

    def is_available(self) -> bool:
        return self._picam2 is not None
