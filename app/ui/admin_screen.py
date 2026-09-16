"""Admin screen: hidden status/maintenance panel.

Entered via a long-press on the Welcome screen logo (see WelcomeScreen).
Shows read-only system status and exposes maintenance actions. Kept
intentionally simple for the MVP — no authentication beyond the
long-press gesture, per README §32/§17 (local-only, no remote admin).
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AdminScreen(QWidget):
    close_requested = pyqtSignal()
    restart_app_requested = pyqtSignal()
    shutdown_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("ADMIN MODE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: bold;")
        layout.addWidget(title)

        status_grid = QGridLayout()
        self._storage_value = self._add_status_row(status_grid, 0, "Storage Remaining")
        self._battery_value = self._add_status_row(status_grid, 1, "Battery Status")
        self._camera_value = self._add_status_row(status_grid, 2, "Camera Status")
        self._network_value = self._add_status_row(status_grid, 3, "Network Status")
        self._session_count_value = self._add_status_row(status_grid, 4, "Session Count")
        layout.addLayout(status_grid)

        layout.addStretch()

        button_row = QHBoxLayout()
        restart_button = QPushButton("RESTART APP")
        restart_button.setMinimumHeight(70)
        restart_button.clicked.connect(self.restart_app_requested.emit)

        shutdown_button = QPushButton("SHUTDOWN")
        shutdown_button.setMinimumHeight(70)
        shutdown_button.setStyleSheet("background-color: #a33; color: white; font-weight: bold;")
        shutdown_button.clicked.connect(self.shutdown_requested.emit)

        button_row.addWidget(restart_button)
        button_row.addWidget(shutdown_button)
        layout.addLayout(button_row)

        close_button = QPushButton("CLOSE")
        close_button.setMinimumHeight(60)
        close_button.clicked.connect(self.close_requested.emit)
        layout.addWidget(close_button)

    def _add_status_row(self, grid: QGridLayout, row: int, label_text: str) -> QLabel:
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 18px; color: #555;")
        value = QLabel("—")
        value.setStyleSheet("font-size: 18px; font-weight: bold;")
        value.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid.addWidget(label, row, 0)
        grid.addWidget(value, row, 1)
        return value

    def update_status(
        self,
        storage_text: str,
        battery_text: str,
        camera_text: str,
        network_text: str,
        session_count: int,
    ) -> None:
        self._storage_value.setText(storage_text)
        self._battery_value.setText(battery_text)
        self._camera_value.setText(camera_text)
        self._network_value.setText(network_text)
        self._session_count_value.setText(str(session_count))
