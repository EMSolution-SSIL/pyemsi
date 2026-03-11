from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLabel, QToolBar, QVBoxLayout, QWidget

from pyemsi.widgets.monaco_lsp import MonacoLspWidget


class _BaseEMSolutionJsonViewer(QWidget):
    """Shared Monaco-based JSON viewer with a placeholder toolbar action."""

    textChanged = Signal(str)
    dirtyChanged = Signal(bool)

    toolbar_label = "EMSolution"
    dummy_action_text = "Dummy"
    dummy_action_tooltip = "Placeholder action"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.editor = MonacoLspWidget(language="json", parent=self)
        self.editor.setTheme("vs")
        self.editor.setLanguage("json")

        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(QLabel(self.toolbar_label))

        dummy_action = QAction(self.dummy_action_text, self)
        dummy_action.setToolTip(self.dummy_action_tooltip)
        toolbar.addAction(dummy_action)
        self._dummy_action = dummy_action

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(self.editor, 1)

        self.editor.textChanged.connect(self.textChanged)
        self.editor.dirtyChanged.connect(self.dirtyChanged)

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


class EMSolutionOutputViewer(_BaseEMSolutionJsonViewer):
    toolbar_label = "EMSolution Output:"
    dummy_action_text = "Output Dummy"
    dummy_action_tooltip = "Placeholder output action"


class EMSolutionInputViewer(_BaseEMSolutionJsonViewer):
    toolbar_label = "EMSolution Input:"
    dummy_action_text = "Input Dummy"
    dummy_action_tooltip = "Placeholder input action"
