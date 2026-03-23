from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget

if TYPE_CHECKING:
    from pyemsi.plotter import Plotter


class FieldViewer(QWidget):
    """Widget embedding an existing desktop Plotter inside a tab."""

    def __init__(self, plotter: "Plotter", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if getattr(plotter, "notebook", False):
            raise ValueError("FieldViewer requires a desktop Plotter created with notebook=False.")

        plotter_widget = getattr(plotter, "widget", None)
        if plotter_widget is None:
            raise ValueError("FieldViewer requires a Plotter exposing a Qt widget.")

        self._plotter = plotter
        self._plotter_widget = plotter_widget
        self._disposed = False

        self._plotter_widget.setParent(self)
        self._plotter.render()
        self._plotter.plotter.reset_camera()
        self._plotter.plotter.show_axes()
        self._plotter._window._create_display_toolbar()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._plotter_widget, 1)

        self.destroyed.connect(self._dispose_plotter)

    @property
    def plotter(self) -> "Plotter":
        """The embedded Plotter instance."""
        return self._plotter

    @property
    def widget(self) -> QWidget:
        """The Qt widget hosting the field plot."""
        return self._plotter_widget

    def _dispose_plotter(self, *_args) -> None:
        if self._disposed:
            return
        self._disposed = True
        self._plotter.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._dispose_plotter()
        super().closeEvent(event)
