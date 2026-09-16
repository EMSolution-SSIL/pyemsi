from __future__ import annotations

import sys

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QComboBox, QLabel, QToolBar, QVBoxLayout, QWidget

import pyemsi.resources.resources  # noqa: F401
from pyemsi.widgets.input_control_editor import InputControlEditorWidget


class EMSolutionInputViewer(QWidget):
    """EMSolutionDocs input control file editor with Run/Stop buttons."""

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

        self.editor = InputControlEditorWidget(parent=self)

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

        self._backend_combo = QComboBox(self)
        self._backend_combo.setToolTip("Choose which program runs this input file")
        self._backend_combo.addItem("Pyemsol", "pyemsol")
        if sys.platform.startswith("win"):
            self._backend_combo.addItem("EMSolution.exe", "executable")
        self._backend_combo.currentIndexChanged.connect(self._update_style_combo_state)

        self._style_combo = QComboBox(self)
        self._style_combo.setToolTip("Background: no extra window. Window: also show EMSolution's own progress window.")
        self._style_combo.addItem("Background", "background")
        self._style_combo.addItem("Window", "window")

        self._backend_toolbar_action = toolbar.addWidget(self._backend_combo)
        self._style_toolbar_action = toolbar.addWidget(self._style_combo)
        if not sys.platform.startswith("win"):
            self._backend_toolbar_action.setVisible(False)
        self._update_style_combo_state()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(self.editor, 1)

        self.editor.textChanged.connect(self.textChanged.emit)
        self.editor.dirtyChanged.connect(self.dirtyChanged.emit)
        self.editor.syncStateChanged.connect(self.syncStateChanged.emit)
        self.editor.externalChangeChanged.connect(self.externalChangeChanged.emit)
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

    @property
    def backend(self) -> str:
        return self._backend_combo.currentData()

    @property
    def run_style(self) -> str:
        return self._style_combo.currentData()

    def set_backend_defaults(self, backend: str, run_style: str) -> None:
        """Initialize the Backend/Style combos from global settings defaults."""
        backend_index = self._backend_combo.findData(backend)
        if backend_index >= 0:
            self._backend_combo.setCurrentIndex(backend_index)
        style_index = self._style_combo.findData(run_style)
        if style_index >= 0:
            self._style_combo.setCurrentIndex(style_index)

    def _update_style_combo_state(self) -> None:
        is_executable = self.backend == "executable"
        self._style_combo.setEnabled(is_executable)
        self._style_toolbar_action.setVisible(is_executable)

    def _on_run_clicked(self) -> None:
        path = self.editor.file_path
        if not path:
            return
        if self.editor.dirty:
            self.editor.save()
        self.run_external_requested.emit(path)

    def _on_stop_clicked(self) -> None:
        self.stop_external_requested.emit()
