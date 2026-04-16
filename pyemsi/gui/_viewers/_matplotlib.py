from __future__ import annotations

from matplotlib.artist import Artist
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QComboBox, QLabel, QMessageBox, QVBoxLayout, QWidget

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import pyemsi.resources.resources  # noqa: F401


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

    INDICATOR_MODE_OFF = "off"
    INDICATOR_MODE_VERTICAL_LINE = "vertical_line"
    INDICATOR_MODE_MARKERS = "markers"
    INDICATOR_MODE_LINE_AND_MARKERS = "line_and_markers"

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
        self._indicator_mode = self.INDICATOR_MODE_VERTICAL_LINE
        self._indicator_index: int | None = None
        self._indicator_artists: list[Artist] = []
        self._legend_label_backup: dict = {}
        self._indicator_mode_label = QLabel("Indicator:", self)
        self._indicator_mode_combo = QComboBox(self)
        self._indicator_index_label = QLabel("Index:", self)
        self._indicator_index_combo = QComboBox(self)
        self._copy_screenshot_action = QAction(QIcon(":/icons/Screenshot.svg"), "Screenshot to Clipboard", self)
        self._configure_screenshot_action()
        self._configure_indicator_mode_combo()
        self._configure_indicator_index_combo()
        self._refresh_indicator_index_combo()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._canvas, 1)

    def _configure_indicator_mode_combo(self) -> None:
        self._indicator_mode_combo.setObjectName("matplotlibIndicatorModeCombo")
        self._indicator_mode_combo.setToolTip("Select how the sample indicator is rendered")
        self._indicator_mode_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._indicator_mode_combo.addItem("Off", self.INDICATOR_MODE_OFF)
        self._indicator_mode_combo.addItem("Vertical line", self.INDICATOR_MODE_VERTICAL_LINE)
        self._indicator_mode_combo.addItem("Markers", self.INDICATOR_MODE_MARKERS)
        self._indicator_mode_combo.addItem("Line + markers", self.INDICATOR_MODE_LINE_AND_MARKERS)
        self._indicator_mode_combo.setCurrentIndex(0)
        self._indicator_mode_combo.currentIndexChanged.connect(self._on_indicator_mode_changed)
        self._toolbar.addSeparator()
        self._toolbar.addWidget(self._indicator_mode_label)
        self._toolbar.addWidget(self._indicator_mode_combo)

    def _configure_indicator_index_combo(self) -> None:
        self._indicator_index_combo.setObjectName("matplotlibIndicatorIndexCombo")
        self._indicator_index_combo.setToolTip("Select the sample index used by the indicator")
        self._indicator_index_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._indicator_index_combo.currentIndexChanged.connect(self._on_indicator_index_changed)
        self._toolbar.addWidget(self._indicator_index_label)
        self._toolbar.addWidget(self._indicator_index_combo)

    def _configure_screenshot_action(self) -> None:
        self._copy_screenshot_action.setToolTip("Copy the current figure canvas to the clipboard")
        self._copy_screenshot_action.triggered.connect(self._copy_screenshot_to_clipboard)
        insert_before = self._toolbar.actions()[-1] if getattr(self._toolbar, "coordinates", False) else None
        if insert_before is None:
            self._toolbar.addSeparator()
            self._toolbar.addAction(self._copy_screenshot_action)
            return

        self._toolbar.insertSeparator(insert_before)
        self._toolbar.insertAction(insert_before, self._copy_screenshot_action)

    def _copy_screenshot_to_clipboard(self) -> None:
        if not self._canvas.isVisible() or self._canvas.width() <= 0 or self._canvas.height() <= 0:
            QMessageBox.critical(self, "Screenshot Error", "The figure canvas is not ready to capture.")
            return

        self._canvas.draw()
        pixmap = self._canvas.grab()
        if pixmap.isNull():
            QMessageBox.critical(self, "Screenshot Error", "Could not capture the current figure canvas.")
            return

        app = QApplication.instance()
        if app is None:
            QMessageBox.critical(self, "Screenshot Error", "The application clipboard is not available.")
            return

        app.clipboard().setPixmap(pixmap)

    def _enable_tight_layout(self) -> None:
        """Prefer automatic tight layout across supported matplotlib versions."""
        if hasattr(self._figure, "set_layout_engine"):
            self._figure.set_layout_engine("tight")
            return
        self._figure.set_tight_layout(True)

    def _restore_legend_labels(self) -> None:
        for axis, (loc, line_labels) in self._legend_label_backup.items():
            for line, original_label in line_labels:
                line.set_label(original_label)
            axis.legend(loc=loc)
        self._legend_label_backup.clear()

    def _clear_indicator_artists(self) -> None:
        self._restore_legend_labels()
        for artist in self._indicator_artists:
            try:
                artist.remove()
            except (NotImplementedError, ValueError):
                pass
        self._indicator_artists.clear()

    def _visible_data_lines(self, axis) -> list:
        return [
            line
            for line in axis.lines
            if line.get_visible() and line not in self._indicator_artists and len(line.get_xdata()) > 0
        ]

    def _max_visible_data_length(self) -> int:
        max_length = 0
        for axis in self._figure.axes:
            for line in self._visible_data_lines(axis):
                max_length = max(max_length, min(len(line.get_xdata()), len(line.get_ydata())))
        return max_length

    def _representative_x_values(self):
        for axis in self._figure.axes:
            lines = self._visible_data_lines(axis)
            if lines:
                return lines[0].get_xdata()
        return None

    def _refresh_indicator_index_combo(self) -> None:
        max_length = self._max_visible_data_length()
        representative_x_values = self._representative_x_values()
        self._indicator_index_combo.blockSignals(True)
        try:
            self._indicator_index_combo.clear()
            self._indicator_index_combo.setEnabled(max_length > 0)
            if max_length <= 0:
                return

            for index in range(max_length):
                if representative_x_values is not None and index < len(representative_x_values):
                    self._indicator_index_combo.addItem(f"{index:<3} : {representative_x_values[index]:g}", index)
                else:
                    self._indicator_index_combo.addItem(str(index), index)

            if self._indicator_index is not None and 0 <= self._indicator_index < max_length:
                self._indicator_index_combo.setCurrentIndex(self._indicator_index)
            else:
                self._indicator_index_combo.setCurrentIndex(-1)
        finally:
            self._indicator_index_combo.blockSignals(False)

    def _eligible_axis_lines(self, axis) -> list | None:
        if self._indicator_index is None:
            return None
        lines = self._visible_data_lines(axis)
        if not lines:
            return None
        for line in lines:
            if len(line.get_xdata()) <= self._indicator_index or len(line.get_ydata()) <= self._indicator_index:
                return None
        return lines

    def _apply_indicator(self) -> None:
        self._clear_indicator_artists()
        if self._indicator_mode == self.INDICATOR_MODE_OFF or self._indicator_index is None:
            return

        for axis in self._figure.axes:
            lines = self._eligible_axis_lines(axis)
            if not lines:
                continue

            if self._indicator_mode in (
                self.INDICATOR_MODE_VERTICAL_LINE,
                self.INDICATOR_MODE_LINE_AND_MARKERS,
            ):
                x_value = lines[0].get_xdata()[self._indicator_index]
                self._indicator_artists.append(
                    axis.axvline(x_value, color="red", linestyle="--", linewidth=1.0, zorder=10)
                )

            if self._indicator_mode in (
                self.INDICATOR_MODE_MARKERS,
                self.INDICATOR_MODE_LINE_AND_MARKERS,
            ):
                if axis.get_legend() is not None:
                    loc = axis.get_legend()._loc
                    line_labels = [(line, line.get_label()) for line in lines]
                    self._legend_label_backup[axis] = (loc, line_labels)
                    for line in lines:
                        y_value = line.get_ydata()[self._indicator_index]
                        line.set_label(f"{line.get_label()} ({y_value:g})")
                    axis.legend(loc=loc)
                for line in lines:
                    marker_line = axis.plot(
                        [line.get_xdata()[self._indicator_index]],
                        [line.get_ydata()[self._indicator_index]],
                        linestyle="None",
                        marker="o",
                        color=line.get_color(),
                        markersize=6,
                        zorder=11,
                        label="_nolegend_",
                    )[0]
                    self._indicator_artists.append(marker_line)

    def set_indicator_index(self, index: int) -> None:
        """Update the selected sample index for the indicator."""
        if index < 0:
            return
        self._indicator_index = index
        self._refresh_indicator_index_combo()
        self.draw()

    def _on_indicator_index_changed(self, combo_index: int) -> None:
        index = self._indicator_index_combo.itemData(combo_index)
        if not isinstance(index, int):
            return
        if index == self._indicator_index:
            return
        self._indicator_index = index
        self.draw()

    def _on_indicator_mode_changed(self, combo_index: int) -> None:
        mode = self._indicator_mode_combo.itemData(combo_index)
        if not isinstance(mode, str):
            return
        self._indicator_mode = mode
        self.draw()

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
        self._refresh_indicator_index_combo()
        self._apply_indicator()
        self._canvas.draw_idle()
