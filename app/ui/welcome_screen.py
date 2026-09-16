"""Welcome screen: booth idle state, "Tap to Start"."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class WelcomeScreen(QWidget):
    start_requested = pyqtSignal()
    admin_requested = pyqtSignal()

    def __init__(self, booth_name: str, admin_hold_seconds: float = 5.0) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(booth_name.upper())
        title.setStyleSheet("font-size: 48px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("\u25c9")
        icon.setStyleSheet("font-size: 96px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setCursor(Qt.CursorShape.PointingHandCursor)
        icon.mousePressEvent = self._on_logo_pressed
        icon.mouseReleaseEvent = self._on_logo_released
        self._logo_label = icon

        start_button = QPushButton("TAP TO START")
        start_button.setMinimumHeight(90)
        start_button.setStyleSheet("font-size: 28px; font-weight: bold;")
        start_button.clicked.connect(self.start_requested.emit)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(icon)
        layout.addStretch()
        layout.addWidget(start_button)
        layout.addStretch()

        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.setInterval(int(admin_hold_seconds * 1000))
        self._hold_timer.timeout.connect(self.admin_requested.emit)

    def _on_logo_pressed(self, event) -> None:
        self._hold_timer.start()

    def _on_logo_released(self, event) -> None:
        self._hold_timer.stop()

