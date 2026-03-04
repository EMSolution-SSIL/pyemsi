"""Bridge and page classes for the xterm.js terminal widget."""

from __future__ import annotations

import json

from qtpy.QtCore import QObject, Signal, Slot
from qtpy.QtWebEngineWidgets import QWebEnginePage


class TerminalBridge(QObject):
    """QWebChannel bridge between xterm.js (JS) and the PTY thread (Python).

    JS  → Python:  ``receive_from_js(name, json_value)`` triggers
                    ``dataReceived`` (user keystrokes) or
                    ``resizeRequested`` (terminal resize).
    Python → JS:   ``send_to_js(name, json_value)`` emits ``sendDataChanged``
                    which JS listens to via ``bridge.sendDataChanged.connect(…)``.
    """

    initialized = Signal()
    sendDataChanged = Signal(str, str)

    # Raised when JS sends PTY input (keystrokes)
    dataReceived = Signal(str)
    # Raised when JS reports a resize (cols, rows)
    resizeRequested = Signal(int, int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._active = False
        self._queue: list[tuple[str, object]] = []

    # -- Python → JS -------------------------------------------------------

    def send_to_js(self, name: str, value: object) -> None:
        if self._active:
            self.sendDataChanged.emit(name, json.dumps(value))
        else:
            self._queue.append((name, value))

    # -- JS → Python -------------------------------------------------------

    @Slot(str, str)
    def receive_from_js(self, name: str, value: str) -> None:
        data = json.loads(value)
        if name == "data":
            self.dataReceived.emit(data)
        elif name == "resize":
            cols, rows = data["cols"], data["rows"]
            self.resizeRequested.emit(cols, rows)

    @Slot()
    def init(self) -> None:
        """Called by JS once xterm.js and QWebChannel are both ready."""
        self._active = True
        self.initialized.emit()
        for name, value in self._queue:
            self.send_to_js(name, value)
        self._queue.clear()


class TerminalPage(QWebEnginePage):
    """Suppress noisy console messages from the web engine."""

    def javaScriptConsoleMessage(self, level, message, line, source):  # noqa: D401
        pass
