"""Lighting service abstraction.

Kept separate from application logic so real GPIO-controlled LEDs can be
added later without touching the UI or session flow.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class LightingService:
    def idle(self) -> None:
        logger.debug("Lighting: idle")

    def preview(self) -> None:
        logger.debug("Lighting: preview")

    def countdown(self) -> None:
        logger.debug("Lighting: countdown")

    def capture(self) -> None:
        logger.debug("Lighting: capture (flash)")

    def off(self) -> None:
        logger.debug("Lighting: off")
