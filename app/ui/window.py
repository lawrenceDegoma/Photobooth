"""Main application window: stacks all screens and switches between them
in response to application events / state transitions.
"""
from __future__ import annotations

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QStackedWidget

from app.core.events import EventBus
from app.ui.camera_screen import CameraScreen
from app.ui.countdown_screen import CountdownScreen
from app.ui.error_screen import ErrorScreen
from app.ui.processing_screen import ProcessingScreen
from app.ui.review_screen import ReviewScreen
from app.ui.share_screen import ShareScreen
from app.ui.welcome_screen import WelcomeScreen

logger = logging.getLogger(__name__)


class MainWindow(QStackedWidget):
    def __init__(self, booth_name: str, event_bus: EventBus, get_frame_callback, fullscreen: bool) -> None:
        super().__init__()
        self._events = event_bus

        self.setWindowTitle(booth_name)
        self.resize(720, 1280)

        self.welcome_screen = WelcomeScreen(booth_name)
        self.camera_screen = CameraScreen(get_frame_callback)
        self.countdown_screen = CountdownScreen()
        self.processing_screen = ProcessingScreen()
        self.review_screen = ReviewScreen()
        self.share_screen = ShareScreen()
        self.error_screen = ErrorScreen()

        for screen in (
            self.welcome_screen,
            self.camera_screen,
            self.countdown_screen,
            self.processing_screen,
            self.review_screen,
            self.share_screen,
            self.error_screen,
        ):
            self.addWidget(screen)

        self.welcome_screen.start_requested.connect(
            lambda: self._events.publish("ui_start_requested")
        )
        self.camera_screen.take_photos_requested.connect(
            lambda: self._events.publish("ui_take_photos_requested")
        )
        self.review_screen.retake_requested.connect(
            lambda: self._events.publish("ui_retake_requested")
        )
        self.review_screen.keep_requested.connect(
            lambda: self._events.publish("ui_keep_requested")
        )
        self.share_screen.finish_requested.connect(
            lambda: self._events.publish("ui_finish_requested")
        )
        self.error_screen.retry_requested.connect(
            lambda: self._events.publish("ui_retry_requested")
        )

        if fullscreen:
            self.setCursor(QCursor(Qt.CursorShape.BlankCursor))
            self.showFullScreen()
        else:
            self.show()

    def show_welcome(self) -> None:
        self.camera_screen.stop_updating()
        self.setCurrentWidget(self.welcome_screen)

    def show_camera(self) -> None:
        self.setCurrentWidget(self.camera_screen)
        self.camera_screen.start_updating()

    def show_countdown(self, value: int) -> None:
        self.countdown_screen.set_count(value)
        self.setCurrentWidget(self.countdown_screen)

    def show_flash(self) -> None:
        self.countdown_screen.show_flash()

    def show_processing(self) -> None:
        self.camera_screen.stop_updating()
        self.setCurrentWidget(self.processing_screen)

    def show_review(self, strip_path: str) -> None:
        self.review_screen.show_strip(strip_path)
        self.setCurrentWidget(self.review_screen)

    def show_share(self, qr_path: str) -> None:
        self.share_screen.show_qr(qr_path)
        self.setCurrentWidget(self.share_screen)

    def show_share_error(self, message: str) -> None:
        self.share_screen.show_error(message)

    def show_error(self, title: str, message: str) -> None:
        self.error_screen.show_error(title, message)
        self.setCurrentWidget(self.error_screen)
