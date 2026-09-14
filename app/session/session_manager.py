"""SessionManager orchestrates the photo capture flow.

It coordinates the CameraService, the application StateMachine, and the
EventBus to drive a session from start through countdown, capture, and
completion — without any UI-specific logic.
"""
from __future__ import annotations

import logging
import threading
import time

from app.camera.camera_service import CameraService
from app.core.config import SessionConfig
from app.core.events import EventBus
from app.core.state import BoothState, StateMachine
from app.session.session import PhotoSession

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(
        self,
        config: SessionConfig,
        camera_service: CameraService,
        state_machine: StateMachine,
        event_bus: EventBus,
        photo_output_dir_factory,
    ) -> None:
        """
        photo_output_dir_factory: Callable[[PhotoSession], Path] that returns
        the directory in which raw photos for a session should be stored
        (provided by StorageService to keep storage layout decisions in one place).
        """
        self._config = config
        self._camera = camera_service
        self._state = state_machine
        self._events = event_bus
        self._photo_output_dir_factory = photo_output_dir_factory

        self._session: PhotoSession | None = None
        self._capture_lock = threading.Lock()
        self._worker: threading.Thread | None = None

    @property
    def current_session(self) -> PhotoSession | None:
        return self._session

    def start_session(self) -> None:
        if self._state.state not in (BoothState.PREVIEW,):
            logger.warning("start_session called from invalid state %s", self._state.state)
            return

        self._session = PhotoSession()
        self._events.publish("session_started", self._session)
        logger.info("Session started: %s", self._session.id)
        self._begin_countdown()

    def _begin_countdown(self) -> None:
        self._state.transition(BoothState.COUNTDOWN)
        self._worker = threading.Thread(target=self._run_countdown_and_capture, daemon=True)
        self._worker.start()

    def _run_countdown_and_capture(self) -> None:
        for remaining in range(self._config.countdown_seconds, 0, -1):
            self._events.publish("countdown_tick", remaining)
            time.sleep(1)

        self._capture_photo()

    def _capture_photo(self) -> None:
        with self._capture_lock:
            if self._session is None:
                return
            self._state.transition(BoothState.CAPTURE)
            self._events.publish("capture_started")

            photo_index = len(self._session.photos) + 1
            output_dir = self._photo_output_dir_factory(self._session)
            output_path = str(output_dir / f"{photo_index:02d}.jpg")

            try:
                self._camera.autofocus()
                self._camera.capture(output_path)
                self._session.add_photo(output_path)
                self._events.publish("photo_captured", output_path, photo_index)
            except Exception:
                logger.exception("Capture failed")
                self._state.transition(BoothState.ERROR)
                self._events.publish("session_error", "capture_failed")
                return

            if self._session.is_complete(self._config.photos_per_session):
                self._state.transition(BoothState.PROCESSING)
                self._events.publish("session_complete", self._session)
            else:
                time.sleep(self._config.delay_between_photos_ms / 1000)
                self._begin_countdown()

    def reset(self) -> None:
        self._session = None
