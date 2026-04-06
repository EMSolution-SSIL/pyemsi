from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QLabel, QToolBar, QVBoxLayout, QWidget

from pyemsi.widgets.monaco_lsp import MonacoLspWidget


class PythonViewer(QWidget):
    """Editor widget for Python files with a Run toolbar.

    Embeds a :class:`MonacoLspWidget` (with ``pylsp`` language-server
    support) and exposes a ``run_ipython_requested`` signal so the host can
    execute the script in the IPython kernel.
    """

    #: Emitted when the editor content changes; carries the full text.
    textChanged = Signal(str)
    #: Emitted when the dirty state changes.
    dirtyChanged = Signal(bool)
    #: Emitted when the user clicks the Run button; carries the file path.
    run_ipython_requested = Signal(str)
    #: Emitted when the user clicks Run External; carries the file path.
    run_external_requested = Signal(str)
    #: Emitted when the user clicks Stop External.
    stop_external_requested = Signal()
    #: Emitted when the file-sync state changes.
    syncStateChanged = Signal(str)
    #: Emitted when the external-change flag changes.
    externalChangeChanged = Signal(bool)
    #: Emitted when the backing file becomes missing or available.
    fileMissingChanged = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # -- inner Monaco editor with Python LSP --
        self.editor = MonacoLspWidget(
            language="python",
            parent=self,
            enable_python_semantic_highlighting=True,
        )
        self.editor.setLanguage("python")
        self.editor.setTheme("vs")

        # -- toolbar --
        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        toolbar.addWidget(QLabel("IPython:"))
        run_ipy_act = QAction("Run IPython", self)
        run_ipy_act.setToolTip("Save and run this file in the IPython terminal")
        run_ipy_act.setIcon(QIcon(":/icons/Run.svg"))
        toolbar.addAction(run_ipy_act)

        toolbar.addSeparator()

        toolbar.addWidget(QLabel("External:"))
        self._run_ext_act = QAction("Run External", self)
        self._run_ext_act.setToolTip("Save and run this file in an external terminal")
        self._run_ext_act.setIcon(QIcon(":/icons/Run.svg"))
        toolbar.addAction(self._run_ext_act)

        self._stop_ext_act = QAction("Stop External", self)
        self._stop_ext_act.setToolTip("Terminate the external terminal process")
        self._stop_ext_act.setIcon(QIcon(":/icons/Stop.svg"))
        self._stop_ext_act.setEnabled(False)
        toolbar.addAction(self._stop_ext_act)

        run_ipy_act.triggered.connect(self._on_run_ipython_clicked)
        self._run_ext_act.triggered.connect(self._on_run_external_clicked)
        self._stop_ext_act.triggered.connect(self._on_stop_external_clicked)

        # -- layout --
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(self.editor, 1)

        # -- forward signals --
        self.editor.textChanged.connect(self.textChanged.emit)
        self.editor.dirtyChanged.connect(self.dirtyChanged.emit)
        if hasattr(self.editor, "syncStateChanged"):
            self.editor.syncStateChanged.connect(self.syncStateChanged.emit)
        if hasattr(self.editor, "externalChangeChanged"):
            self.editor.externalChangeChanged.connect(self.externalChangeChanged.emit)
        if hasattr(self.editor, "fileMissingChanged"):
            self.editor.fileMissingChanged.connect(self.fileMissingChanged.emit)

    # ------------------------------------------------------------------
    # Public API — mirrors MonacoLspWidget interface expected by SplitContainer
    # ------------------------------------------------------------------

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
        """Toggle toolbar state: disable Run External while a process is active."""
        self._run_ext_act.setEnabled(not running)
        self._stop_ext_act.setEnabled(running)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _on_run_ipython_clicked(self) -> None:
        path = self.editor.file_path
        if not path:
            return
        if self.editor.dirty:
            self.editor.save()
        self.run_ipython_requested.emit(path)

    def _on_run_external_clicked(self) -> None:
        path = self.editor.file_path
        if not path:
            return
        if self.editor.dirty:
            self.editor.save()
        self.run_external_requested.emit(path)

    def _on_stop_external_clicked(self) -> None:
        self.stop_external_requested.emit()
