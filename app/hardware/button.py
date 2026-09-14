"""Physical capture button support.

Calls the same session start event as the touchscreen button — no separate
capture logic. Uses gpiozero on the Pi; a no-op stub elsewhere.
"""
from __future__ import annotations

import logging
import platform
from typing import Callable

logger = logging.getLogger(__name__)


class PhysicalButton:
    def __init__(self, gpio_pin: int, on_press: Callable[[], None]) -> None:
        self._gpio_pin = gpio_pin
        self._on_press = on_press
        self._button = None

    def start(self) -> None:
        if platform.system() != "Linux":
            logger.info("PhysicalButton: not on Linux, GPIO button disabled")
            return
        try:
            from gpiozero import Button

            self._button = Button(self._gpio_pin)
            self._button.when_pressed = self._on_press
            logger.info("Physical button armed on GPIO%d", self._gpio_pin)
        except Exception:
            logger.exception("Failed to initialize physical button")

    def stop(self) -> None:
        if self._button is not None:
            self._button.close()
            self._button = None
