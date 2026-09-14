"""Camera screen: live preview + take photos button."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class CameraScreen(QWidget):
    take_photos_requested = pyqtSignal()

    def __init__(self, get_frame_callback) -> None:
        super().__init__()
        self._get_frame_callback = get_frame_callback

        layout = QVBoxLayout(self)

        self._preview_label = QLabel("LIVE PREVIEW")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setStyleSheet("font-size: 24px; background: black; color: white;")
        self._preview_label.setMinimumHeight(500)

        take_photos_button = QPushButton("TAKE PHOTOS")
        take_photos_button.setMinimumHeight(90)
        take_photos_button.setStyleSheet("font-size: 26px; font-weight: bold;")
        take_photos_button.clicked.connect(self.take_photos_requested.emit)

        layout.addWidget(self._preview_label)
        layout.addWidget(take_photos_button)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frame)

    def start_updating(self, interval_ms: int = 66) -> None:
        self._timer.start(interval_ms)

    def stop_updating(self) -> None:
        self._timer.stop()

    def _update_frame(self) -> None:
        frame = self._get_frame_callback()
        if frame is None:
            return
        rgb_image = frame.convert("RGB")
        data = rgb_image.tobytes("raw", "RGB")
        qimage = QImage(
            data, rgb_image.width, rgb_image.height, rgb_image.width * 3, QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qimage).scaled(
            self._preview_label.width(),
            self._preview_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self._preview_label.setPixmap(pixmap)
