"""Error screen: friendly, non-technical error display."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class ErrorScreen(QWidget):
    retry_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._title_label = QLabel("Something Went Wrong")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet("font-size: 32px; font-weight: bold;")

        self._message_label = QLabel("")
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message_label.setWordWrap(True)
        self._message_label.setStyleSheet("font-size: 20px;")

        retry_button = QPushButton("RETRY")
        retry_button.setMinimumHeight(80)
        retry_button.setStyleSheet("font-size: 22px; font-weight: bold;")
        retry_button.clicked.connect(self.retry_requested.emit)

        layout.addWidget(self._title_label)
        layout.addWidget(self._message_label)
        layout.addWidget(retry_button)

    def show_error(self, title: str, message: str) -> None:
        self._title_label.setText(title)
        self._message_label.setText(message)
