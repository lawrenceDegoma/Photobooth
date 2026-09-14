"""CameraService: the only object the rest of the app talks to for camera access.

Automatically selects PiCamera when running on hardware with picamera2
available, otherwise falls back to MockCamera. Adds basic failure recovery
(retry + reinitialize) on top of whichever CameraInterface is active.
"""
from __future__ import annotations

import logging
import platform

from app.camera.camera_interface import CameraInterface
from app.core.config import CameraConfig

logger = logging.getLogger(__name__)


def _create_camera_backend(config: CameraConfig) -> CameraInterface:
    if platform.system() == "Linux":
        try:
            from app.camera.pi_camera import PiCamera

            return PiCamera(config)
        except Exception:
            logger.warning("picamera2 unavailable, falling back to MockCamera", exc_info=True)

    from app.camera.mock_camera import MockCamera

    return MockCamera(config)


class CameraService:
    MAX_RETRIES = 3

    def __init__(self, config: CameraConfig, camera: CameraInterface | None = None) -> None:
        self._config = config
        self._camera = camera or _create_camera_backend(config)

    def initialize(self) -> None:
        self._camera.initialize()

    def start_preview(self) -> None:
        self._camera.start_preview()

    def get_preview_frame(self):
        return self._camera.get_preview_frame()

    def autofocus(self) -> None:
        self._camera.autofocus()

    def capture(self, output_path: str) -> str:
        last_error: Exception | None = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return self._camera.capture(output_path)
            except Exception as exc:
                last_error = exc
                logger.warning("Capture attempt %d/%d failed: %s", attempt, self.MAX_RETRIES, exc)
                self._recover()
        assert last_error is not None
        raise last_error

    def stop_preview(self) -> None:
        self._camera.stop_preview()

    def shutdown(self) -> None:
        self._camera.shutdown()

    def is_available(self) -> bool:
        return self._camera.is_available()

    def _recover(self) -> None:
        logger.info("Attempting camera recovery")
        try:
            self._camera.shutdown()
            self._camera.initialize()
        except Exception:
            logger.exception("Camera recovery failed")
