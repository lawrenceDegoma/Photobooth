"""Welcome screen: booth idle state, "Tap to Start"."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class WelcomeScreen(QWidget):
    start_requested = pyqtSignal()

    def __init__(self, booth_name: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(booth_name.upper())
        title.setStyleSheet("font-size: 48px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("\u25c9")
        icon.setStyleSheet("font-size: 96px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
