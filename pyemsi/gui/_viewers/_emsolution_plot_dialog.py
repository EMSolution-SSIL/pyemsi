from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from matplotlib.figure import Figure

from pyemsi.gui._viewers._matplotlib import MatplotlibViewer
from pyemsi.io import EMSolutionOutput, PlotAxisOption, PlotSeriesDescriptor


@dataclass
class PlotSeriesStyle:
    line_style: str = "-"
    marker: str = "None"
    line_width: float = 1.5
    color: str | None = None


class EMSolutionPlotDialog(QDialog):
    SERIES_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self, result: EMSolutionOutput, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._result = result
        self._x_options = {option.key: option for option in result.get_plot_x_options()}
        self._series_styles: dict[tuple[str, ...], PlotSeriesStyle] = {}

        self.setWindowTitle("EMSolution Plot")
        self.resize(1200, 720)

        self._tree = QTreeWidget(self)
        self._tree.setHeaderLabel("Series")

        self._x_axis_combo = QComboBox(self)
        for option in self._x_options.values():
            self._x_axis_combo.addItem(option.axis_label, option.key)

        self._title_edit = QLineEdit(self)
        self._x_label_edit = QLineEdit(self)
        self._y_label_edit = QLineEdit(self)
        self._show_legend_checkbox = QCheckBox(self)
        self._show_legend_checkbox.setChecked(True)
        self._show_grid_checkbox = QCheckBox(self)
        self._line_style_combo = QComboBox(self)
        self._line_style_combo.addItem("Solid", "-")
        self._line_style_combo.addItem("Dashed", "--")
        self._line_style_combo.addItem("Dash Dot", "-.")
        self._line_style_combo.addItem("Dotted", ":")
        self._marker_combo = QComboBox(self)
        self._marker_combo.addItem("None", "None")
        self._marker_combo.addItem("Circle", "o")
        self._marker_combo.addItem("Square", "s")
        self._marker_combo.addItem("Triangle", "^")
        self._marker_combo.addItem("Diamond", "D")
        self._marker_combo.addItem("Plus", "+")
        self._marker_combo.addItem("Cross", "x")
        self._line_width_spin = QDoubleSpinBox(self)
        self._line_width_spin.setRange(0.1, 10.0)
        self._line_width_spin.setSingleStep(0.1)
        self._line_width_spin.setDecimals(1)
        self._line_width_spin.setValue(1.5)
        self._color_button = QPushButton("Auto", self)
        self._reset_color_button = QPushButton("Reset", self)
        self._plot_button = QPushButton("Plot", self)
        self._cancel_button = QPushButton("Cancel", self)

        self._preview = MatplotlibViewer(parent=self)

        controls_widget = QWidget(self)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self._tree, 1)

        form_layout = QFormLayout()
        form_layout.addRow("X Axis:", self._x_axis_combo)
        form_layout.addRow("Title:", self._title_edit)
        form_layout.addRow("X Label:", self._x_label_edit)
        form_layout.addRow("Y Label:", self._y_label_edit)
        form_layout.addRow("Show Legend:", self._show_legend_checkbox)
        form_layout.addRow("Show Grid:", self._show_grid_checkbox)

        color_row = QHBoxLayout()
        color_row.setContentsMargins(0, 0, 0, 0)
        color_row.addWidget(self._color_button, 1)
        color_row.addWidget(self._reset_color_button)

        style_layout = QFormLayout()
        style_layout.addRow("Line Style:", self._line_style_combo)
        style_layout.addRow("Marker:", self._marker_combo)
        style_layout.addRow("Width:", self._line_width_spin)
        style_layout.addRow("Color:", color_row)

        controls_layout.addLayout(form_layout)
        controls_layout.addLayout(style_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(controls_widget)
        splitter.addWidget(self._preview)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([360, 840])

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self._plot_button)
        button_row.addWidget(self._cancel_button)
        layout.addLayout(button_row)

        self._populate_tree()
        self._tree.expandAll()
        self._update_placeholder_labels()
        self._set_style_controls_enabled(False)

        self._tree.itemChanged.connect(self._on_item_changed)
        self._tree.currentItemChanged.connect(self._on_current_item_changed)
        self._x_axis_combo.currentIndexChanged.connect(self._on_settings_changed)
        self._title_edit.textChanged.connect(self._redraw_plot)
        self._x_label_edit.textChanged.connect(self._redraw_plot)
        self._y_label_edit.textChanged.connect(self._redraw_plot)
        self._show_legend_checkbox.checkStateChanged.connect(self._redraw_plot)
        self._show_grid_checkbox.checkStateChanged.connect(self._redraw_plot)
        self._line_style_combo.currentIndexChanged.connect(self._on_series_style_changed)
        self._marker_combo.currentIndexChanged.connect(self._on_series_style_changed)
        self._line_width_spin.valueChanged.connect(self._on_series_style_changed)
        self._color_button.clicked.connect(self._choose_series_color)
        self._reset_color_button.clicked.connect(self._reset_series_color)
        self._plot_button.clicked.connect(self._on_plot)
        self._cancel_button.clicked.connect(self.reject)

        self._redraw_plot()

    def _populate_tree(self) -> None:
        parent_lookup: dict[tuple[str, ...], QTreeWidgetItem] = {}
        for descriptor in self._result.get_plot_series():
            parent_item: QTreeWidgetItem | None = None
            current_path: tuple[str, ...] = ()
            for segment in descriptor.tree_path[:-1]:
                current_path += (segment,)
                item = parent_lookup.get(current_path)
                if item is None:
                    item = QTreeWidgetItem([segment])
                    if parent_item is None:
                        self._tree.addTopLevelItem(item)
                    else:
                        parent_item.addChild(item)
                    parent_lookup[current_path] = item
                parent_item = item

            leaf = QTreeWidgetItem([descriptor.tree_path[-1]])
            leaf.setFlags(leaf.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            leaf.setCheckState(0, Qt.CheckState.Unchecked)
            leaf.setData(0, self.SERIES_ROLE, descriptor)
            if parent_item is None:
                self._tree.addTopLevelItem(leaf)
            else:
                parent_item.addChild(leaf)

    def _checked_series(self) -> list[PlotSeriesDescriptor]:
        checked: list[PlotSeriesDescriptor] = []

        def visit(item: QTreeWidgetItem) -> None:
            descriptor = item.data(0, self.SERIES_ROLE)
            if descriptor is not None and item.checkState(0) == Qt.CheckState.Checked:
                checked.append(descriptor)
            for index in range(item.childCount()):
                visit(item.child(index))

        for index in range(self._tree.topLevelItemCount()):
            visit(self._tree.topLevelItem(index))

        return checked

    @staticmethod
    def _style_key(descriptor: PlotSeriesDescriptor) -> tuple[str, ...]:
        return descriptor.tree_path

    def _descriptor_for_item(self, item: QTreeWidgetItem | None) -> PlotSeriesDescriptor | None:
        if item is None:
            return None
        descriptor = item.data(0, self.SERIES_ROLE)
        if not isinstance(descriptor, PlotSeriesDescriptor):
            return None
        return descriptor

    def _current_styled_series(self) -> PlotSeriesDescriptor | None:
        item = self._tree.currentItem()
        descriptor = self._descriptor_for_item(item)
        if descriptor is None:
            return None
        if item.checkState(0) != Qt.CheckState.Checked:
            return None
        return descriptor

    def _style_for_descriptor(self, descriptor: PlotSeriesDescriptor) -> PlotSeriesStyle:
        key = self._style_key(descriptor)
        style = self._series_styles.get(key)
        if style is None:
            style = PlotSeriesStyle()
            self._series_styles[key] = style
        return style

    def _selected_x_option(self) -> PlotAxisOption:
        key = self._x_axis_combo.currentData()
        return self._x_options[str(key)]

    def _default_title(self, selected_series: list[PlotSeriesDescriptor]) -> str:
        if len(selected_series) == 1:
            return selected_series[0].label
        if selected_series:
            return "EMSolution Output Plot"
        return "EMSolution Output"

    def _default_x_label(self) -> str:
        return self._selected_x_option().axis_label

    def _default_y_label(self, selected_series: list[PlotSeriesDescriptor]) -> str:
        if not selected_series:
            return "Value"

        axis_labels = {series.axis_label for series in selected_series}
        if len(axis_labels) == 1:
            return selected_series[0].axis_label

        units = {series.unit for series in selected_series if series.unit}
        if len(units) == 1:
            unit = next(iter(units))
            return f"Value ({unit})"
        return "Value"

    def _update_placeholder_labels(self) -> None:
        selected_series = self._checked_series()
        self._title_edit.setPlaceholderText(self._default_title(selected_series))
        self._x_label_edit.setPlaceholderText(self._default_x_label())
        self._y_label_edit.setPlaceholderText(self._default_y_label(selected_series))

    def _effective_text(self, edit: QLineEdit) -> str:
        return edit.text().strip() or edit.placeholderText()

    def _set_style_controls_enabled(self, enabled: bool) -> None:
        self._line_style_combo.setEnabled(enabled)
        self._marker_combo.setEnabled(enabled)
        self._line_width_spin.setEnabled(enabled)
        self._color_button.setEnabled(enabled)
        self._reset_color_button.setEnabled(enabled)

    def _update_color_button(self, color: str | None) -> None:
        if color is None:
            self._color_button.setText("Auto")
            self._color_button.setStyleSheet("")
            return
        self._color_button.setText(color)
        text_color = "#000000"
        qcolor = QColor(color)
        if qcolor.isValid() and qcolor.lightness() < 128:
            text_color = "#ffffff"
        self._color_button.setStyleSheet(f"QPushButton {{ background-color: {color}; color: {text_color}; }}")

    def _sync_style_editor(self) -> None:
        descriptor = self._current_styled_series()
        if descriptor is None:
            self._set_style_controls_enabled(False)
            with QSignalBlocker(self._line_style_combo):
                self._line_style_combo.setCurrentIndex(0)
            with QSignalBlocker(self._marker_combo):
                self._marker_combo.setCurrentIndex(0)
            with QSignalBlocker(self._line_width_spin):
                self._line_width_spin.setValue(1.5)
            self._update_color_button(None)
            return

        style = self._style_for_descriptor(descriptor)
        self._set_style_controls_enabled(True)
        with QSignalBlocker(self._line_style_combo):
            index = self._line_style_combo.findData(style.line_style)
            self._line_style_combo.setCurrentIndex(max(index, 0))
        with QSignalBlocker(self._marker_combo):
            index = self._marker_combo.findData(style.marker)
            self._marker_combo.setCurrentIndex(max(index, 0))
        with QSignalBlocker(self._line_width_spin):
            self._line_width_spin.setValue(style.line_width)
        self._update_color_button(style.color)

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 0:
            return
        self._sync_style_editor()
        self._on_settings_changed()

    def _on_current_item_changed(self, current: QTreeWidgetItem | None, previous: QTreeWidgetItem | None) -> None:
        del previous
        del current
        self._sync_style_editor()

    def _on_settings_changed(self) -> None:
        self._update_placeholder_labels()
        self._redraw_plot()

    def _on_series_style_changed(self) -> None:
        descriptor = self._current_styled_series()
        if descriptor is None:
            return
        style = self._style_for_descriptor(descriptor)
        style.line_style = str(self._line_style_combo.currentData())
        style.marker = str(self._marker_combo.currentData())
        style.line_width = float(self._line_width_spin.value())
        self._redraw_plot()

    def _choose_series_color(self) -> None:
        descriptor = self._current_styled_series()
        if descriptor is None:
            return
        initial = QColor(self._style_for_descriptor(descriptor).color or "#1f77b4")
        color = QColorDialog.getColor(initial, self, "Select Series Color")
        if not color.isValid():
            return
        style = self._style_for_descriptor(descriptor)
        style.color = color.name()
        self._update_color_button(style.color)
        self._redraw_plot()

    def _reset_series_color(self) -> None:
        descriptor = self._current_styled_series()
        if descriptor is None:
            return
        style = self._style_for_descriptor(descriptor)
        style.color = None
        self._update_color_button(None)
        self._redraw_plot()

    def _draw_onto(self, figure: Figure) -> None:
        figure.clear()
        ax = figure.add_subplot(111)

        selected_series = self._checked_series()
        x_option = self._selected_x_option()
        plotted_count = 0

        for descriptor in selected_series:
            if len(descriptor.values) != len(x_option.values):
                continue
            style = self._style_for_descriptor(descriptor)
            plot_kwargs = {
                "label": descriptor.label,
                "linestyle": style.line_style,
                "linewidth": style.line_width,
            }
            if style.marker != "None":
                plot_kwargs["marker"] = style.marker
            if style.color is not None:
                plot_kwargs["color"] = style.color
            ax.plot(x_option.values, descriptor.values, **plot_kwargs)
            plotted_count += 1

        if plotted_count == 0:
            ax.text(
                0.5,
                0.5,
                "Select one or more series to preview.",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
        else:
            if self._show_legend_checkbox.isChecked():
                ax.legend()
            if len(x_option.values) > 0:
                ax.set_xlim(x_option.values[0], x_option.values[-1])

        ax.grid(self._show_grid_checkbox.isChecked())

        ax.set_title(self._effective_text(self._title_edit))
        ax.set_xlabel(self._effective_text(self._x_label_edit))
        ax.set_ylabel(self._effective_text(self._y_label_edit))
        figure.tight_layout()

    def _redraw_plot(self) -> None:
        self._draw_onto(self._preview.figure)
        self._preview.draw()

    def _on_plot(self) -> None:
        import pyemsi.gui as gui

        figure = Figure()
        self._draw_onto(figure)
        title = self._effective_text(self._title_edit)
        gui.add_figure(figure, title)
        self.accept()
