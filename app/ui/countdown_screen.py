"""Countdown screen: big obvious 3 -> 2 -> 1 display."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CountdownScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._number_label = QLabel("3")
        self._number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._number_label.setStyleSheet("font-size: 220px; font-weight: bold;")

        layout.addWidget(self._number_label)

    def set_count(self, value: int) -> None:
        self._number_label.setText(str(value))

    def show_flash(self) -> None:
        self._number_label.setText("\U0001F4F8")
