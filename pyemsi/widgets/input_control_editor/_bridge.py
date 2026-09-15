from __future__ import annotations

import json

from PySide6.QtCore import QObject, Signal, Slot


class InputControlEditorBridge(QObject):
    """QWebChannel object carrying the editor's hosted-mode messages as JSON strings.

    See "Hosted mode" in EMSolutionDocs' InputControlFileEditor README for the contract.
    """

    #: JSON message for the page (``load``).
    messageToEditor = Signal(str)
    #: Decoded message from the page (``ready``, ``changed``, ``saveRequested``).
    messageFromEditor = Signal(object)

    def send(self, message: dict) -> None:
        self.messageToEditor.emit(json.dumps(message))

    @Slot(str)
    def post(self, raw: str) -> None:
        try:
            message = json.loads(raw)
        except (TypeError, ValueError):
            return
        if isinstance(message, dict) and isinstance(message.get("type"), str):
            self.messageFromEditor.emit(message)
