"""A minimal synchronous pub/sub event bus used to decouple subsystems.

UI components, session manager, hardware, etc. can publish and subscribe
to named events without holding direct references to each other.

Note: publish() calls subscribers synchronously on whatever thread called
publish(). Callers that publish from background threads (e.g. the session
manager's countdown/capture worker) and have subscribers that touch Qt
widgets must marshal onto the main thread themselves (see
app.core.qt_utils.run_on_main_thread), since Qt widgets are not thread-safe.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        if callback in self._subscribers.get(event_name, []):
            self._subscribers[event_name].remove(callback)

    def publish(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        for callback in list(self._subscribers.get(event_name, [])):
            try:
                callback(*args, **kwargs)
            except Exception:
                logger.exception("Error handling event '%s'", event_name)
