from __future__ import annotations

import json

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLabel, QMessageBox, QToolBar, QVBoxLayout, QWidget

from pyemsi.io import EMSolutionOutput
from pyemsi.widgets.monaco_lsp import MonacoLspWidget

from ._emsolution_plot_dialog import EMSolutionPlotDialog


class _BaseEMSolutionJsonViewer(QWidget):
    """Shared Monaco-based JSON viewer with an extensible toolbar."""

    textChanged = Signal(str)
    dirtyChanged = Signal(bool)

    toolbar_label = "EMSolution"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.editor = MonacoLspWidget(language="json", parent=self)
        self.editor.setTheme("vs")
        self.editor.setLanguage("json")

        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(QLabel(self.toolbar_label))
        self._toolbar = toolbar
        self._configure_toolbar(toolbar)

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

    def _configure_toolbar(self, toolbar: QToolBar) -> None:
        del toolbar


class EMSolutionOutputViewer(_BaseEMSolutionJsonViewer):
    toolbar_label = "EMSolution Output:"

    def _configure_toolbar(self, toolbar: QToolBar) -> None:
        plot_action = QAction("Plot", self)
        plot_action.setToolTip("Open the plotting dialog for this EMSolution output")
        plot_action.triggered.connect(self._open_plot_dialog)
        toolbar.addAction(plot_action)
        self._plot_action = plot_action

    def _open_plot_dialog(self) -> None:
        try:
            payload = json.loads(self.text())
        except json.JSONDecodeError as exc:
            QMessageBox.critical(self, "Invalid JSON", f"Could not parse the current editor content.\n\n{exc}")
            return

        try:
            result = EMSolutionOutput.from_dict(payload)
        except Exception as exc:
            QMessageBox.critical(self, "Invalid EMSolution Output", str(exc))
            return

        dialog = EMSolutionPlotDialog(result, parent=self)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        self._plot_dialog = dialog


class EMSolutionInputViewer(_BaseEMSolutionJsonViewer):
    toolbar_label = "EMSolution Input:"
