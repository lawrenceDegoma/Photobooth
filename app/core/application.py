"""Application bootstrap: wires together config, state machine, event bus,
camera, session, storage, processing, sharing, and UI.

This is the composition root — the only place that constructs concrete
services and connects them. Individual modules never reach into each other
directly; they communicate through the EventBus and well-defined interfaces.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from app.camera.camera_service import CameraService
from app.core.config import Config
from app.core.events import EventBus
from app.core.logging_setup import setup_logging
from app.core.qt_utils import run_on_main_thread
from app.core.state import BoothState, StateMachine
from app.hardware.button import PhysicalButton
from app.hardware.lighting import LightingService
from app.processing.image_processor import ImageProcessor
from app.processing.photo_strip import PhotoStrip
from app.session.session import PhotoSession
from app.session.session_manager import SessionManager
from app.sharing.download_manager import DownloadManager, SharedSession
from app.sharing.qr_service import QRService
from app.sharing.server import SharingServer
from app.storage.storage_service import InsufficientStorageError, StorageService
from app.ui.window import MainWindow

logger = logging.getLogger(__name__)

INACTIVITY_TIMEOUT_MS = 60_000


class PhotoBoothApp:
    def __init__(self) -> None:
        self.config = Config.load()
        setup_logging(self.config.logging)
        logger.info("Starting %s", self.config.booth.name)

        self.qt_app = QApplication([])
        self.events = EventBus()
        self.state = StateMachine(initial=BoothState.BOOTING)

        self.camera_service = CameraService(self.config.camera)
        self.storage_service = StorageService(self.config.storage)
        self.image_processor = ImageProcessor()
        self.photo_strip = PhotoStrip()
        self.qr_service = QRService()
        self.download_manager = DownloadManager()
        self.lighting = LightingService()

        self.session_manager = SessionManager(
            config=self.config.session,
            camera_service=self.camera_service,
            state_machine=self.state,
            event_bus=self.events,
            photo_output_dir_factory=self.storage_service.originals_dir,
        )

        self.sharing_server: SharingServer | None = None
        if self.config.sharing.enabled:
            self.sharing_server = SharingServer(
                self.download_manager, host="0.0.0.0", port=self.config.sharing.port
            )

        self.window = MainWindow(
            booth_name=self.config.booth.name,
            event_bus=self.events,
            get_frame_callback=self.camera_service.get_preview_frame,
            fullscreen=self.config.display.fullscreen,
        )

        self.physical_button: PhysicalButton | None = None
        if self.config.hardware.physical_button:
            self.physical_button = PhysicalButton(
                self.config.hardware.button_gpio,
                on_press=lambda: self.events.publish("ui_start_requested"),
            )

        self._inactivity_timer = QTimer()
        self._inactivity_timer.setInterval(INACTIVITY_TIMEOUT_MS)
        self._inactivity_timer.timeout.connect(self._on_inactivity_timeout)

        self._wire_events()

    def _wire_events(self) -> None:
        self.events.subscribe("ui_start_requested", self._on_start_requested)
        self.events.subscribe("ui_take_photos_requested", self._on_take_photos_requested)
        self.events.subscribe("ui_retake_requested", self._on_retake_requested)
        self.events.subscribe("ui_keep_requested", self._on_keep_requested)
        self.events.subscribe("ui_finish_requested", self._on_finish_requested)
        self.events.subscribe("ui_retry_requested", self._on_retry_requested)

        # These are published from the SessionManager's background worker
        # thread, so their handlers (which touch Qt widgets) are marshaled
        # onto the main thread.
        self.events.subscribe(
            "countdown_tick", lambda remaining: run_on_main_thread(self._on_countdown_tick, remaining)
        )
        self.events.subscribe(
            "capture_started", lambda: run_on_main_thread(self._on_capture_started)
        )
        self.events.subscribe(
            "session_complete", lambda session: run_on_main_thread(self._on_session_complete, session)
        )
        self.events.subscribe(
            "session_error", lambda reason: run_on_main_thread(self._on_session_error, reason)
        )

    # --- UI-driven transitions -------------------------------------------------

    def _on_start_requested(self) -> None:
        if self.state.state != BoothState.IDLE:
            return
        self._inactivity_timer.stop()
        self.state.transition(BoothState.PREVIEW)
        self.lighting.preview()
        self.window.show_camera()

    def _on_take_photos_requested(self) -> None:
        if self.state.state != BoothState.PREVIEW:
            return
        try:
            self.storage_service.check_free_space()
        except InsufficientStorageError:
            logger.exception("Storage full at session start")
            self.state.transition(BoothState.ERROR)
            self.window.show_error(
                "Photo Booth Temporarily Unavailable", "Storage needs attention."
            )
            return
        self.session_manager.start_session()

    def _on_retake_requested(self) -> None:
        self.state.transition(BoothState.PREVIEW)
        self.session_manager.reset()
        self.lighting.preview()
        self.window.show_camera()

    def _on_keep_requested(self) -> None:
        self.state.transition(BoothState.SHARE)
        session = self.session_manager.current_session
        if session is None:
            return
        self._publish_share(session)

    def _on_finish_requested(self) -> None:
        self.state.transition(BoothState.IDLE)
        self.session_manager.reset()
        self.lighting.idle()
        self.window.show_welcome()
        self._inactivity_timer.start()

    def _on_retry_requested(self) -> None:
        self.state.transition(BoothState.IDLE)
        self.session_manager.reset()
        self.window.show_welcome()
        self._inactivity_timer.start()

    # --- Session-driven transitions --------------------------------------------

    def _on_countdown_tick(self, remaining: int) -> None:
        self.lighting.countdown()
        self.window.show_countdown(remaining)

    def _on_capture_started(self) -> None:
        self.lighting.capture()
        self.window.show_flash()

    def _on_session_complete(self, session: PhotoSession) -> None:
        self.window.show_processing()
        try:
            processed_dir = self.storage_service.processed_dir(session)
            for i, photo_path in enumerate(session.photos, start=1):
                out_path = str(processed_dir / f"{i:02d}.jpg")
                self.image_processor.process(photo_path, out_path)
                session.add_processed_photo(out_path)

            strip_path = str(self.storage_service.strip_path(session))
            self.photo_strip.generate(
                session.processed_photos,
                strip_path,
                event_name=self.config.booth.name,
                event_date=datetime.now(),
            )
            session.strip_path = strip_path

            self.state.transition(BoothState.REVIEW)
            self.window.show_review(strip_path)
        except InsufficientStorageError:
            logger.exception("Storage full during processing")
            self.state.transition(BoothState.ERROR)
            self.window.show_error(
                "Photo Booth Temporarily Unavailable", "Storage needs attention."
            )
        except Exception:
            logger.exception("Processing failed")
            self.state.transition(BoothState.ERROR)
            self.window.show_error(
                "Processing Error", "We couldn't finish processing your photos."
            )

    def _on_session_error(self, reason: str) -> None:
        self.window.show_error(
            "Camera Error", "We're having trouble with the camera.\n\nPlease try again."
        )

    def _publish_share(self, session: PhotoSession) -> None:
        if self.sharing_server is None or session.strip_path is None:
            self.window.show_share_error("QR sharing is temporarily unavailable.")
            self.window.setCurrentWidget(self.window.share_screen)
            return
        try:
            self.download_manager.register(
                session.share_token,
                SharedSession(
                    session_id=session.id,
                    originals_dir=Path(session.photos[0]).parent if session.photos else Path("."),
                    processed_dir=Path(session.processed_photos[0]).parent
                    if session.processed_photos
                    else Path("."),
                    strip_path=Path(session.strip_path),
                ),
            )
            url = self.sharing_server.url_for_token(
                session.share_token, self.config.sharing.hostname
            )
            qr_path = str(Path(session.strip_path).parent / "qr.png")
            self.qr_service.generate(url, qr_path)
            self.window.show_share(qr_path)
        except Exception:
            logger.exception("Failed to publish share link")
            self.window.show_share_error("QR sharing is temporarily unavailable.")
            self.window.setCurrentWidget(self.window.share_screen)

    def _on_inactivity_timeout(self) -> None:
        if self.state.state in (BoothState.PREVIEW,):
            self.state.transition(BoothState.IDLE)
            self.window.show_welcome()
        self._inactivity_timer.stop()

    def run(self) -> int:
        self.camera_service.initialize()
        self.camera_service.start_preview()

        if self.sharing_server is not None:
            self.sharing_server.start()

        if self.physical_button is not None:
            self.physical_button.start()

        self.state.transition(BoothState.IDLE)
        self.window.show_welcome()
        self._inactivity_timer.start()

        exit_code = self.qt_app.exec()

        self.camera_service.shutdown()
        if self.physical_button is not None:
            self.physical_button.stop()

        return exit_code
