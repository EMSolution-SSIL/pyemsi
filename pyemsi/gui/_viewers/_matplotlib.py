from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MatplotlibViewer(QWidget):
    """Widget embedding a matplotlib Figure with its navigation toolbar.

    Parameters
    ----------
    figure : Figure, optional
        The matplotlib Figure to display. A new blank Figure is created when
        *None* (the default).
    parent : QWidget, optional
        Parent widget.
    tight_layout : bool, optional
        Whether to enable matplotlib tight layout for the figure during
        initialization. Defaults to *True*.
    """

    def __init__(
        self,
        figure: Figure | None = None,
        parent: QWidget | None = None,
        tight_layout: bool = True,
    ) -> None:
        super().__init__(parent)
        self._figure = figure if figure is not None else Figure()
        if tight_layout:
            self._enable_tight_layout()
        self._canvas = FigureCanvas(self._figure)
        self._toolbar = NavigationToolbar(self._canvas, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._canvas, 1)

    def _enable_tight_layout(self) -> None:
        """Prefer automatic tight layout across supported matplotlib versions."""
        if hasattr(self._figure, "set_layout_engine"):
            self._figure.set_layout_engine("tight")
            return
        self._figure.set_tight_layout(True)

    @property
    def figure(self) -> Figure:
        """The underlying matplotlib Figure."""
        return self._figure

    @property
    def canvas(self) -> FigureCanvas:
        """The FigureCanvas (QWidget) rendering the figure."""
        return self._canvas

    @property
    def toolbar(self) -> NavigationToolbar:
        """The NavigationToolbar2QT controlling this canvas."""
        return self._toolbar

    def draw(self) -> None:
        """Redraw the canvas. Call this after modifying the figure."""
        self._canvas.draw_idle()
