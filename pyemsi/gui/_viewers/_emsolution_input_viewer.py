from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QLabel, QToolBar, QVBoxLayout, QWidget

import pyemsi.resources.resources  # noqa: F401
from pyemsi.widgets.monaco_lsp import MonacoLspWidget


class EMSolutionInputViewer(QWidget):
    """Monaco-based JSON viewer for EMSolution input files with Run/Stop buttons."""

    textChanged = Signal(str)
    dirtyChanged = Signal(bool)
    syncStateChanged = Signal(str)
    externalChangeChanged = Signal(bool)
    fileMissingChanged = Signal(bool)

    #: Emitted when the user clicks the Run button; carries the file path.
    run_external_requested = Signal(str)
    #: Emitted when the user clicks the Stop button.
    stop_external_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.editor = MonacoLspWidget(language="json", parent=self)
        self.editor.setTheme("vs")
        self.editor.setLanguage("json")

        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toolbar = toolbar

        self._run_act = QAction(QIcon(":/icons/Run.svg"), "Run", self)
        self._run_act.setToolTip("Save and run this input file with pyemsol in an external terminal")
        self._run_act.triggered.connect(self._on_run_clicked)
        toolbar.addAction(self._run_act)

        self._stop_act = QAction(QIcon(":/icons/Stop.svg"), "Stop", self)
        self._stop_act.setToolTip("Terminate the running pyemsol process")
        self._stop_act.setEnabled(False)
        self._stop_act.triggered.connect(self._on_stop_clicked)
        toolbar.addAction(self._stop_act)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(self.editor, 1)

        self.editor.textChanged.connect(self.textChanged.emit)
        self.editor.dirtyChanged.connect(self.dirtyChanged.emit)
        if hasattr(self.editor, "syncStateChanged"):
            self.editor.syncStateChanged.connect(self.syncStateChanged.emit)
        if hasattr(self.editor, "externalChangeChanged"):
            self.editor.externalChangeChanged.connect(self.externalChangeChanged.emit)
        if hasattr(self.editor, "fileMissingChanged"):
            self.editor.fileMissingChanged.connect(self.fileMissingChanged.emit)

    def load_file(self, path: str) -> None:
        self.editor.load_file(path)

    def text(self) -> str:
        return self.editor.text()

    @property
    def file_path(self) -> str | None:
        return self.editor.file_path

    @property
    def dirty(self) -> bool:
        return self.editor.dirty

    @property
    def sync_state(self) -> str:
        return self.editor.sync_state

    @property
    def has_external_change(self) -> bool:
        return self.editor.has_external_change

    @property
    def file_missing(self) -> bool:
        return self.editor.file_missing

    def save(self, path: str | None = None) -> None:
        self.editor.save(path)

    def reload_from_disk(self) -> None:
        if self.editor.file_path:
            self.editor.load_file(self.editor.file_path)

    def set_external_running(self, running: bool) -> None:
        """Toggle toolbar state: disable Run while a process is active."""
        self._run_act.setEnabled(not running)
        self._stop_act.setEnabled(running)

    def _on_run_clicked(self) -> None:
        path = self.editor.file_path
        if not path:
            return
        if self.editor.dirty:
            self.editor.save()
        self.run_external_requested.emit(path)

    def _on_stop_clicked(self) -> None:
        self.stop_external_requested.emit()
