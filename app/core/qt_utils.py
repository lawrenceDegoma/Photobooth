"""Helper for safely marshaling calls onto the Qt main thread.

The session manager runs countdown/capture on a background thread and
publishes events via EventBus, which invokes subscribers synchronously on
the calling thread. Since Qt widgets may only be touched from the main
thread, any EventBus subscriber that updates the UI should wrap its body
with `run_on_main_thread` (or be invoked from a callback that does).
"""
from __future__ import annotations

from typing import Any, Callable

from PyQt6.QtCore import QCoreApplication, QObject, Qt, QTimer, pyqtSignal


class _MainThreadInvoker(QObject):
    _invoke = pyqtSignal(object, tuple, dict)

    def __init__(self) -> None:
        super().__init__()
        self.moveToThread(QCoreApplication.instance().thread())
        self._invoke.connect(self._handle, Qt.ConnectionType.QueuedConnection)

    def _handle(self, func: Callable[..., None], args: tuple, kwargs: dict) -> None:
        func(*args, **kwargs)

    def call(self, func: Callable[..., None], *args: Any, **kwargs: Any) -> None:
        self._invoke.emit(func, args, kwargs)


_invoker: _MainThreadInvoker | None = None


def run_on_main_thread(func: Callable[..., None], *args: Any, **kwargs: Any) -> None:
    """Schedule func(*args, **kwargs) to run on the Qt main thread."""
    global _invoker
    if _invoker is None:
        _invoker = _MainThreadInvoker()
    _invoker.call(func, *args, **kwargs)
