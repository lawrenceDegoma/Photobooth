"""Explicit application state machine.

Represents the flow described in the README:

BOOTING -> IDLE -> PREVIEW -> COUNTDOWN -> CAPTURE -> (loop) -> PROCESSING
-> REVIEW -> (RETAKE -> PREVIEW | KEEP -> SHARE) -> IDLE

The state machine enforces valid transitions only, so e.g. a user cannot
trigger multiple captures during COUNTDOWN.
"""
from __future__ import annotations

import logging
from enum import Enum, auto
from typing import Callable

logger = logging.getLogger(__name__)


class BoothState(Enum):
    BOOTING = auto()
    IDLE = auto()
    PREVIEW = auto()
    COUNTDOWN = auto()
    CAPTURE = auto()
    PROCESSING = auto()
    REVIEW = auto()
    SHARE = auto()
    ERROR = auto()


# Map of allowed transitions: from_state -> set of valid to_states
_ALLOWED_TRANSITIONS: dict[BoothState, set[BoothState]] = {
    BoothState.BOOTING: {BoothState.IDLE, BoothState.ERROR},
    BoothState.IDLE: {BoothState.PREVIEW, BoothState.ERROR},
    BoothState.PREVIEW: {BoothState.COUNTDOWN, BoothState.IDLE, BoothState.ERROR},
    BoothState.COUNTDOWN: {BoothState.CAPTURE, BoothState.ERROR},
    BoothState.CAPTURE: {
        BoothState.COUNTDOWN,  # more photos in session
        BoothState.PROCESSING,  # session complete
        BoothState.ERROR,
    },
    BoothState.PROCESSING: {BoothState.REVIEW, BoothState.ERROR},
    BoothState.REVIEW: {BoothState.PREVIEW, BoothState.SHARE, BoothState.ERROR},
    BoothState.SHARE: {BoothState.IDLE, BoothState.ERROR},
    BoothState.ERROR: {BoothState.IDLE},
}


class InvalidStateTransition(Exception):
    pass


class StateMachine:
    """A small, dependency-free finite state machine.

    Listeners can subscribe to be notified whenever the state changes.
    """

    def __init__(self, initial: BoothState = BoothState.BOOTING) -> None:
        self._state = initial
        self._listeners: list[Callable[[BoothState, BoothState], None]] = []

    @property
    def state(self) -> BoothState:
        return self._state

    def can_transition(self, to_state: BoothState) -> bool:
        return to_state in _ALLOWED_TRANSITIONS.get(self._state, set())

    def transition(self, to_state: BoothState) -> None:
        if not self.can_transition(to_state):
            raise InvalidStateTransition(
                f"Cannot transition from {self._state.name} to {to_state.name}"
            )
        previous = self._state
        self._state = to_state
        logger.info("State transition: %s -> %s", previous.name, to_state.name)
        for listener in self._listeners:
            listener(previous, to_state)

    def on_change(self, callback: Callable[[BoothState, BoothState], None]) -> None:
        self._listeners.append(callback)
