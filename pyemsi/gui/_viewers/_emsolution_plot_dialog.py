from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
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


@dataclass
class PlotDialogSettings:
    x_axis_key: str
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    show_legend: bool = True
    show_grid: bool = True


class PlotSettingsDialog(QDialog):
    def __init__(
        self,
        x_options: dict[str, PlotAxisOption],
        settings: PlotDialogSettings,
        default_title: str,
        default_x_label: str,
        default_y_label: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Plot Settings")

        self._x_axis_combo = QComboBox(self)
        for option in x_options.values():
            self._x_axis_combo.addItem(option.axis_label, option.key)
        index = self._x_axis_combo.findData(settings.x_axis_key)
        self._x_axis_combo.setCurrentIndex(max(index, 0))

        self._title_edit = QLineEdit(settings.title, self)
        self._title_edit.setPlaceholderText(default_title)
        self._x_label_edit = QLineEdit(settings.x_label, self)
        self._x_label_edit.setPlaceholderText(default_x_label)
        self._y_label_edit = QLineEdit(settings.y_label, self)
        self._y_label_edit.setPlaceholderText(default_y_label)
        self._show_legend_checkbox = QCheckBox(self)
        self._show_legend_checkbox.setChecked(settings.show_legend)
        self._show_grid_checkbox = QCheckBox(self)
        self._show_grid_checkbox.setChecked(settings.show_grid)

        form_layout = QFormLayout()
        form_layout.addRow("X Axis:", self._x_axis_combo)
        form_layout.addRow("Title:", self._title_edit)
        form_layout.addRow("X Label:", self._x_label_edit)
        form_layout.addRow("Y Label:", self._y_label_edit)
        form_layout.addRow("Show Legend:", self._show_legend_checkbox)
        form_layout.addRow("Show Grid:", self._show_grid_checkbox)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

    def settings(self) -> PlotDialogSettings:
        x_axis_key = str(self._x_axis_combo.currentData())
        return PlotDialogSettings(
            x_axis_key=x_axis_key,
            title=self._title_edit.text().strip(),
            x_label=self._x_label_edit.text().strip(),
            y_label=self._y_label_edit.text().strip(),
            show_legend=self._show_legend_checkbox.isChecked(),
            show_grid=self._show_grid_checkbox.isChecked(),
        )


class SeriesStyleDialog(QDialog):
    def __init__(self, style: PlotSeriesStyle, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Series Style")

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

        self._color_button = QPushButton("Auto", self)
        self._reset_color_button = QPushButton("Reset", self)
        self._color: str | None = None

        color_row = QHBoxLayout()
        color_row.setContentsMargins(0, 0, 0, 0)
        color_row.addWidget(self._color_button, 1)
        color_row.addWidget(self._reset_color_button)

        form_layout = QFormLayout()
        form_layout.addRow("Line Style:", self._line_style_combo)
        form_layout.addRow("Marker:", self._marker_combo)
        form_layout.addRow("Width:", self._line_width_spin)
        form_layout.addRow("Color:", color_row)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self._color_button.clicked.connect(self._choose_color)
        self._reset_color_button.clicked.connect(self._reset_color)

        self._set_style(style)

    def _set_style(self, style: PlotSeriesStyle) -> None:
        self._line_style_combo.setCurrentIndex(max(self._line_style_combo.findData(style.line_style), 0))
        self._marker_combo.setCurrentIndex(max(self._marker_combo.findData(style.marker), 0))
        self._line_width_spin.setValue(style.line_width)
        self._color = style.color
        self._update_color_button()

    def _update_color_button(self) -> None:
        if self._color is None:
            self._color_button.setText("Auto")
            self._color_button.setStyleSheet("")
            return

        self._color_button.setText(self._color)
        text_color = "#000000"
        qcolor = QColor(self._color)
        if qcolor.isValid() and qcolor.lightness() < 128:
            text_color = "#ffffff"
        self._color_button.setStyleSheet(f"QPushButton {{ background-color: {self._color}; color: {text_color}; }}")

    def _choose_color(self) -> None:
        initial = QColor(self._color or "#1f77b4")
        color = QColorDialog.getColor(initial, self, "Select Series Color")
        if not color.isValid():
            return
        self._color = color.name()
        self._update_color_button()

    def _reset_color(self) -> None:
        self._color = None
        self._update_color_button()

    def style(self) -> PlotSeriesStyle:
        return PlotSeriesStyle(
            line_style=str(self._line_style_combo.currentData()),
            marker=str(self._marker_combo.currentData()),
            line_width=float(self._line_width_spin.value()),
            color=self._color,
        )


class EMSolutionPlotDialog(QDialog):
    SERIES_ROLE = Qt.ItemDataRole.UserRole + 1
    SETTINGS_COLUMN = 1

    def __init__(self, result: EMSolutionOutput, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._result = result
        self._x_options = {option.key: option for option in result.get_plot_x_options()}
        self._series_styles: dict[tuple[str, ...], PlotSeriesStyle] = {}
        default_x_axis_key = next(iter(self._x_options))
        self._plot_settings = PlotDialogSettings(x_axis_key=default_x_axis_key)

        self.setWindowTitle("EMSolution Plot")
        self.resize(1200, 720)

        self._tree = QTreeWidget(self)
        self._tree.setColumnCount(2)
        self._tree.setHeaderLabels(["Series", ""])
        self._tree.header().setStretchLastSection(False)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.setRootIsDecorated(True)

        self._plot_settings_button = QPushButton("Plot Settings...", self)
        self._plot_button = QPushButton("Plot", self)
        self._cancel_button = QPushButton("Cancel", self)

        self._preview = MatplotlibViewer(parent=self)

        controls_widget = QWidget(self)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self._tree, 1)
        controls_layout.addWidget(self._plot_settings_button)

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
        self._refresh_tree_action_buttons()

        self._tree.itemChanged.connect(self._on_item_changed)
        self._plot_settings_button.clicked.connect(self._open_plot_settings_dialog)
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

    def _iter_tree_items(self) -> list[QTreeWidgetItem]:
        items: list[QTreeWidgetItem] = []

        def visit(item: QTreeWidgetItem) -> None:
            items.append(item)
            for index in range(item.childCount()):
                visit(item.child(index))

        for index in range(self._tree.topLevelItemCount()):
            visit(self._tree.topLevelItem(index))

        return items

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

    def _style_for_descriptor(self, descriptor: PlotSeriesDescriptor) -> PlotSeriesStyle:
        key = self._style_key(descriptor)
        style = self._series_styles.get(key)
        if style is None:
            style = PlotSeriesStyle()
            self._series_styles[key] = style
        return style

    def _selected_x_option(self) -> PlotAxisOption:
        return self._x_options[self._plot_settings.x_axis_key]

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

    def _effective_title(self, selected_series: list[PlotSeriesDescriptor]) -> str:
        return self._plot_settings.title or self._default_title(selected_series)

    def _effective_x_label(self) -> str:
        return self._plot_settings.x_label or self._default_x_label()

    def _effective_y_label(self, selected_series: list[PlotSeriesDescriptor]) -> str:
        return self._plot_settings.y_label or self._default_y_label(selected_series)

    def _refresh_style_button_for_item(self, item: QTreeWidgetItem) -> None:
        descriptor = self._descriptor_for_item(item)
        button = self._tree.itemWidget(item, self.SETTINGS_COLUMN)
        is_checked_leaf = descriptor is not None and item.checkState(0) == Qt.CheckState.Checked

        if not is_checked_leaf:
            if button is not None:
                self._tree.removeItemWidget(item, self.SETTINGS_COLUMN)
                button.deleteLater()
            item.setText(self.SETTINGS_COLUMN, "")
            return

        if button is None:
            button = QPushButton("Style", self._tree)
            button.setAutoDefault(False)
            button.setDefault(False)
            button.clicked.connect(lambda checked=False, tree_item=item: self._open_style_dialog_for_item(tree_item))
            self._tree.setItemWidget(item, self.SETTINGS_COLUMN, button)

    def _refresh_tree_action_buttons(self) -> None:
        for item in self._iter_tree_items():
            self._refresh_style_button_for_item(item)

    def _apply_plot_settings(self, settings: PlotDialogSettings) -> None:
        self._plot_settings = settings
        self._redraw_plot()

    def _apply_series_style(self, descriptor: PlotSeriesDescriptor, style: PlotSeriesStyle) -> None:
        self._series_styles[self._style_key(descriptor)] = style
        self._redraw_plot()

    def _open_plot_settings_dialog(self) -> None:
        selected_series = self._checked_series()
        dialog = PlotSettingsDialog(
            self._x_options,
            self._plot_settings,
            self._default_title(selected_series),
            self._default_x_label(),
            self._default_y_label(selected_series),
            parent=self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_plot_settings(dialog.settings())

    def _open_style_dialog_for_item(self, item: QTreeWidgetItem) -> None:
        descriptor = self._descriptor_for_item(item)
        if descriptor is None or item.checkState(0) != Qt.CheckState.Checked:
            return

        self._tree.setCurrentItem(item)
        dialog = SeriesStyleDialog(self._style_for_descriptor(descriptor), parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_series_style(descriptor, dialog.style())

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 0:
            return
        self._refresh_style_button_for_item(item)
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
            if self._plot_settings.show_legend:
                ax.legend()
            if len(x_option.values) > 0:
                ax.set_xlim(x_option.values[0], x_option.values[-1])

        ax.grid(self._plot_settings.show_grid)

        ax.set_title(self._effective_title(selected_series))
        ax.set_xlabel(self._effective_x_label())
        ax.set_ylabel(self._effective_y_label(selected_series))
        figure.tight_layout()

    def _redraw_plot(self) -> None:
        self._draw_onto(self._preview.figure)
        self._preview.draw()

    def _on_plot(self) -> None:
        import pyemsi.gui as gui

        figure = Figure()
        self._draw_onto(figure)
        title = self._effective_title(self._checked_series())
        gui.add_figure(figure, title)
        self.accept()
