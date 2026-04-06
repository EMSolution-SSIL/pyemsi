from __future__ import annotations

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget


class UnsupportedViewer(QWidget):
    """Placeholder for file types that cannot be previewed."""

    syncStateChanged = Signal(str)
    externalChangeChanged = Signal(bool)
    fileMissingChanged = Signal(bool)

    def __init__(self, path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = path

        self._stack = QStackedWidget()

        # Page 0: placeholder
        placeholder = QWidget()
        placeholder_layout = QVBoxLayout(placeholder)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(f"Cannot preview this file.\n\n{os.path.basename(path)}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn = QPushButton("Open as Text")
        btn.setFixedWidth(120)
        btn.clicked.connect(self._open_as_text)
        placeholder_layout.addWidget(label)
        placeholder_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Page 1: Monaco text viewer (created lazily)
        self._monaco = None

        self._stack.addWidget(placeholder)  # index 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack)

    def _open_as_text(self) -> None:
        from pyemsi.widgets.monaco_lsp import MonacoLspWidget

        if self._monaco is None:
            self._monaco = MonacoLspWidget(language="plaintext", parent=self)
            self._monaco.setTheme("vs")
            self._monaco.setLanguage("plaintext")
            self._monaco.load_file(self._path)
            if hasattr(self._monaco, "syncStateChanged"):
                self._monaco.syncStateChanged.connect(self.syncStateChanged.emit)
            if hasattr(self._monaco, "externalChangeChanged"):
                self._monaco.externalChangeChanged.connect(self.externalChangeChanged.emit)
            if hasattr(self._monaco, "fileMissingChanged"):
                self._monaco.fileMissingChanged.connect(self.fileMissingChanged.emit)
            self._stack.addWidget(self._monaco)  # index 1

        self._stack.setCurrentIndex(1)

    @property
    def dirty(self) -> bool:
        if self._monaco is None:
            return False
        return self._monaco.dirty

    @property
    def sync_state(self) -> str:
        if self._monaco is None:
            return "clean"
        return self._monaco.sync_state

    @property
    def has_external_change(self) -> bool:
        if self._monaco is None:
            return False
        return self._monaco.has_external_change

    @property
    def file_missing(self) -> bool:
        if self._monaco is None:
            return False
        return self._monaco.file_missing

    def reload_from_disk(self) -> None:
        if self._monaco is not None and self._monaco.file_path:
            self._monaco.load_file(self._monaco.file_path)
