from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar, QVBoxLayout, QWidget

from pyemsi.widgets.monaco_lsp import MonacoLspWidget


class PythonViewer(QWidget):
    """Editor widget for Python files with a Run toolbar.

    Embeds a :class:`MonacoLspWidget` (with ``pylsp`` language-server
    support) and exposes a ``run_requested`` signal so the host can
    execute the script in the IPython kernel.
    """

    #: Emitted when the editor content changes; carries the full text.
    textChanged = Signal(str)
    #: Emitted when the dirty state changes.
    dirtyChanged = Signal(bool)
    #: Emitted when the user clicks the Run button; carries the file path.
    run_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # -- inner Monaco editor with Python LSP --
        self.editor = MonacoLspWidget(language="python", parent=self)
        self.editor.setLanguage("python")
        self.editor.setTheme("vs")

        # -- toolbar --
        toolbar = QToolBar(self)
        toolbar.setMovable(False)

        run_act = QAction("▶ Run", self)
        run_act.setToolTip("Save and run this file in the IPython terminal")
        toolbar.addAction(run_act)

        run_act.triggered.connect(self._on_run_clicked)

        # -- layout --
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(self.editor, 1)

        # -- forward signals --
        self.editor.textChanged.connect(self.textChanged)
        self.editor.dirtyChanged.connect(self.dirtyChanged)

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

    def save(self, path: str | None = None) -> None:
        self.editor.save(path)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _on_run_clicked(self) -> None:
        path = self.editor.file_path
        if not path:
            return
        if self.editor.dirty:
            self.editor.save()
        self.run_requested.emit(path)
