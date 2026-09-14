"""Review screen: shows the final photo strip with Retake / Keep options."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class ReviewScreen(QWidget):
    retake_requested = pyqtSignal()
    keep_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        self._strip_label = QLabel()
        self._strip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._strip_label.setMinimumHeight(600)

        button_row = QHBoxLayout()
        retake_button = QPushButton("RETAKE")
        retake_button.setMinimumHeight(80)
        retake_button.setStyleSheet("font-size: 22px;")
        retake_button.clicked.connect(self.retake_requested.emit)

        keep_button = QPushButton("KEEP")
        keep_button.setMinimumHeight(80)
        keep_button.setStyleSheet("font-size: 22px; font-weight: bold;")
        keep_button.clicked.connect(self.keep_requested.emit)

        button_row.addWidget(retake_button)
        button_row.addWidget(keep_button)

        layout.addWidget(self._strip_label)
        layout.addLayout(button_row)

    def show_strip(self, strip_path: str) -> None:
        pixmap = QPixmap(strip_path).scaled(
            self._strip_label.width() or 400,
            self._strip_label.height() or 600,
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self._strip_label.setPixmap(pixmap)
