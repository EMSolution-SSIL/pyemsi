from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMessageBox, QToolBar, QVBoxLayout, QWidget

import pyemsi.resources.resources  # noqa: F401
from pyemsi.gui.emsolution_output_plot_builder_dialog import EMSolutionOutputPlotBuilderDialog
from pyemsi.widgets.monaco_lsp import MonacoLspWidget


class EMSolutionOutputViewer(QWidget):
    """Monaco-based JSON viewer for EMSolution output files with a Plot button."""

    textChanged = Signal(str)
    dirtyChanged = Signal(bool)
    syncStateChanged = Signal(str)
    externalChangeChanged = Signal(bool)
    fileMissingChanged = Signal(bool)

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

        plot_action = QAction(QIcon(":/icons/Graph.svg"), "Plot", self)
        plot_action.setToolTip("Open the plotting dialog for this EMSolution output")
        plot_action.triggered.connect(self._open_plot_dialog)
        toolbar.addAction(plot_action)
        self._plot_action = plot_action

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

    def _open_plot_dialog(self) -> None:
        file_path = self.file_path
        if not file_path:
            QMessageBox.warning(self, "Missing File Path", "Save this EMSolution output file before plotting it.")
            return

        try:
            dialog = EMSolutionOutputPlotBuilderDialog(file_path, parent=self)
        except Exception as exc:
            QMessageBox.critical(self, "Invalid EMSolution Output", str(exc))
            return

        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        self._plot_dialog = dialog
