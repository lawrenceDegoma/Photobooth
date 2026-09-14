"""Share screen: displays QR code for local photo download."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class ShareScreen(QWidget):
    finish_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("SCAN TO DOWNLOAD")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: bold;")

        self._qr_label = QLabel()
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("font-size: 18px; color: #a00;")

        finish_button = QPushButton("FINISH")
        finish_button.setMinimumHeight(80)
        finish_button.setStyleSheet("font-size: 24px; font-weight: bold;")
        finish_button.clicked.connect(self.finish_requested.emit)

        layout.addWidget(title)
        layout.addWidget(self._qr_label)
        layout.addWidget(self._status_label)
        layout.addWidget(finish_button)

    def show_qr(self, qr_path: str) -> None:
        pixmap = QPixmap(qr_path).scaled(
            350, 350, Qt.AspectRatioMode.KeepAspectRatio
        )
        self._qr_label.setPixmap(pixmap)
        self._status_label.setText("")

    def show_error(self, message: str) -> None:
        self._status_label.setText(message)
