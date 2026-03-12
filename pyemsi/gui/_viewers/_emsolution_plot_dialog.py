from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass, replace
from typing import Any

from matplotlib import style as mpl_style
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon
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
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from matplotlib.figure import Figure

import pyemsi.resources.resources  # noqa: F401
from pyemsi.gui._viewers._matplotlib import MatplotlibViewer
from pyemsi.io import EMSolutionOutput, PlotAxisOption, PlotSeriesDescriptor


@dataclass
class PlotSeriesStyle:
    label: str = ""
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
    style_preset: str = ""
    legend_mode: str = "upper right"
    grid_mode: str = "both"
    x_log_scale: bool = False
    y_log_scale: bool = False


PLOT_STYLE_PRESETS: tuple[tuple[str, str], ...] = (
    ("Default", ""),
    ("Solarize_Light2", "Solarize_Light2"),
    ("bmh", "bmh"),
    ("classic", "classic"),
    ("dark_background", "dark_background"),
    ("fast", "fast"),
    ("fivethirtyeight", "fivethirtyeight"),
    ("ggplot", "ggplot"),
    ("grayscale", "grayscale"),
    ("petroff10", "petroff10"),
    ("seaborn-v0_8", "seaborn-v0_8"),
    ("seaborn-v0_8-bright", "seaborn-v0_8-bright"),
    ("seaborn-v0_8-colorblind", "seaborn-v0_8-colorblind"),
    ("seaborn-v0_8-dark", "seaborn-v0_8-dark"),
    ("seaborn-v0_8-dark-palette", "seaborn-v0_8-dark-palette"),
    ("seaborn-v0_8-darkgrid", "seaborn-v0_8-darkgrid"),
    ("seaborn-v0_8-deep", "seaborn-v0_8-deep"),
    ("seaborn-v0_8-muted", "seaborn-v0_8-muted"),
    ("seaborn-v0_8-notebook", "seaborn-v0_8-notebook"),
    ("seaborn-v0_8-paper", "seaborn-v0_8-paper"),
    ("seaborn-v0_8-pastel", "seaborn-v0_8-pastel"),
    ("seaborn-v0_8-poster", "seaborn-v0_8-poster"),
    ("seaborn-v0_8-talk", "seaborn-v0_8-talk"),
    ("seaborn-v0_8-ticks", "seaborn-v0_8-ticks"),
    ("seaborn-v0_8-white", "seaborn-v0_8-white"),
    ("seaborn-v0_8-whitegrid", "seaborn-v0_8-whitegrid"),
    ("tableau-colorblind10", "tableau-colorblind10"),
)

LEGEND_MODE_PRESETS: tuple[tuple[str, str], ...] = (
    ("Off", "none"),
    ("Best Fit", "best"),
    ("Upper Right", "upper right"),
    ("Upper Left", "upper left"),
    ("Lower Right", "lower right"),
    ("Lower Left", "lower left"),
    ("Center", "center"),
)

GRID_MODE_PRESETS: tuple[tuple[str, str], ...] = (
    ("Off", "off"),
    ("Both Axes", "both"),
    ("X-axis Only", "x"),
    ("Y-axis Only", "y"),
    ("Major Only", "major"),
)


def _matplotlib_style_context(style_preset: str):
    if not style_preset:
        return nullcontext()
    return mpl_style.context(style_preset)


def _indent_lines(lines: list[str], prefix: str) -> list[str]:
    return [f"{prefix}{line}" if line else "" for line in lines]


class GeneratedScriptDialog(QDialog):
    def __init__(self, script_text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Generated Plot Script")
        self.setWindowIcon(QIcon(":/icons/Code.svg"))
        self.resize(900, 700)

        self._text_edit = QPlainTextEdit(self)
        self._text_edit.setReadOnly(True)
        self._text_edit.setPlainText(script_text)
        self._text_edit.setFont(QFont("Courier", 10))

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=self)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self._text_edit, 1)
        layout.addWidget(button_box)

    def script_text(self) -> str:
        return self._text_edit.toPlainText()


class PlotSettingsDialog(QDialog):
    settingsApplied = Signal(object)
    settingsCanceled = Signal(object)

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
        self.setWindowIcon(QIcon(":/icons/Gear.svg"))
        self._original_settings = replace(settings)

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
        self._style_preset_combo = QComboBox(self)
        for label, style_name in PLOT_STYLE_PRESETS:
            self._style_preset_combo.addItem(label, style_name)
        style_index = self._style_preset_combo.findData(settings.style_preset)
        self._style_preset_combo.setCurrentIndex(max(style_index, 0))
        self._legend_mode_combo = QComboBox(self)
        for label, mode in LEGEND_MODE_PRESETS:
            self._legend_mode_combo.addItem(label, mode)
        legend_mode_index = self._legend_mode_combo.findData(settings.legend_mode)
        self._legend_mode_combo.setCurrentIndex(max(legend_mode_index, 0))
        self._grid_mode_combo = QComboBox(self)
        for label, mode in GRID_MODE_PRESETS:
            self._grid_mode_combo.addItem(label, mode)
        grid_mode_index = self._grid_mode_combo.findData(settings.grid_mode)
        self._grid_mode_combo.setCurrentIndex(max(grid_mode_index, 0))
        self._x_log_scale_checkbox = QCheckBox(self)
        self._x_log_scale_checkbox.setChecked(settings.x_log_scale)
        self._y_log_scale_checkbox = QCheckBox(self)
        self._y_log_scale_checkbox.setChecked(settings.y_log_scale)

        form_layout = QFormLayout()
        form_layout.addRow("X Axis:", self._x_axis_combo)
        form_layout.addRow("Title:", self._title_edit)
        form_layout.addRow("X Label:", self._x_label_edit)
        form_layout.addRow("Y Label:", self._y_label_edit)
        form_layout.addRow("Style Preset:", self._style_preset_combo)
        form_layout.addRow("Legend:", self._legend_mode_combo)
        form_layout.addRow("Grid:", self._grid_mode_combo)
        form_layout.addRow("Log X Axis:", self._x_log_scale_checkbox)
        form_layout.addRow("Log Y Axis:", self._y_log_scale_checkbox)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply,
            parent=self,
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self._on_rejected)
        apply_button = self._button_box.button(QDialogButtonBox.StandardButton.Apply)
        if apply_button is not None:
            apply_button.clicked.connect(self._on_apply)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self._button_box)

    def _on_apply(self) -> None:
        self.settingsApplied.emit(self.settings())

    def _on_rejected(self) -> None:
        self.settingsCanceled.emit(replace(self._original_settings))
        self.reject()

    def settings(self) -> PlotDialogSettings:
        x_axis_key = str(self._x_axis_combo.currentData())
        return PlotDialogSettings(
            x_axis_key=x_axis_key,
            title=self._title_edit.text().strip(),
            x_label=self._x_label_edit.text().strip(),
            y_label=self._y_label_edit.text().strip(),
            style_preset=str(self._style_preset_combo.currentData()),
            legend_mode=str(self._legend_mode_combo.currentData()),
            grid_mode=str(self._grid_mode_combo.currentData()),
            x_log_scale=self._x_log_scale_checkbox.isChecked(),
            y_log_scale=self._y_log_scale_checkbox.isChecked(),
        )


class SeriesStyleDialog(QDialog):
    def __init__(self, style: PlotSeriesStyle, default_label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Series Style")
        self.setWindowIcon(QIcon(":/icons/Style.svg"))

        self._label_edit = QLineEdit(self)
        self._label_edit.setPlaceholderText(default_label)
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
        form_layout.addRow("Label:", self._label_edit)
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
        self._label_edit.setText(style.label)
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
            label=self._label_edit.text().strip(),
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
        self.setWindowIcon(QIcon(":/icons/Graph.svg"))
        self.resize(1200, 720)

        self._tree = QTreeWidget(self)
        self._tree.setColumnCount(2)
        self._tree.setHeaderLabels(["Series", ""])
        self._tree.header().setStretchLastSection(False)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.setRootIsDecorated(True)

        self._plot_settings_button = QPushButton("Plot Settings...", self)
        self._plot_settings_button.setIcon(QIcon(":/icons/Gear.svg"))
        self._script_button = QPushButton("Script...", self)
        self._script_button.setIcon(QIcon(":/icons/Code.svg"))
        self._plot_button = QPushButton("Plot", self)
        self._plot_button.setIcon(QIcon(":/icons/Graph.svg"))
        self._cancel_button = QPushButton("Cancel", self)
        self._warning_label = QLabel(self)
        self._warning_label.setWordWrap(True)
        self._warning_label.setStyleSheet("color: #a94442;")
        self._warning_label.hide()

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
        layout.addWidget(self._warning_label)

        button_row = QHBoxLayout()
        button_row.addWidget(self._script_button)
        button_row.addStretch()
        button_row.addWidget(self._plot_button)
        button_row.addWidget(self._cancel_button)
        layout.addLayout(button_row)

        self._populate_tree()
        self._tree.expandAll()
        self._refresh_tree_action_buttons()

        self._tree.itemChanged.connect(self._on_item_changed)
        self._plot_settings_button.clicked.connect(self._open_plot_settings_dialog)
        self._script_button.clicked.connect(self._open_script_dialog)
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

    def _display_label_for_descriptor(self, descriptor: PlotSeriesDescriptor) -> str:
        style = self._style_for_descriptor(descriptor)
        return style.label or descriptor.label

    def _apply_legend_mode(self, ax) -> None:
        if self._plot_settings.legend_mode == "none":
            return
        ax.legend(loc=self._plot_settings.legend_mode)

    def _apply_grid_mode(self, ax) -> None:
        grid_mode = self._plot_settings.grid_mode
        if grid_mode == "off":
            ax.grid(False)
            return
        if grid_mode == "major":
            ax.grid(True, axis="both", which="major")
            return
        ax.grid(True, axis=grid_mode)

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

    def _set_warning_message(self, message: str) -> None:
        self._warning_label.setText(message)
        self._warning_label.setVisible(bool(message))

    def _log_scale_warning_message(self, invalid_series: list[str], invalid_x: bool) -> str:
        parts: list[str] = []
        if invalid_x:
            parts.append("X-axis log scale requires all X values to be greater than zero.")
        if invalid_series:
            labels = ", ".join(invalid_series)
            parts.append(f"Skipped series with non-positive Y values for log scale: {labels}.")
        return " ".join(parts)

    def _script_x_expression(self) -> str:
        if self._plot_settings.x_axis_key == "position":
            return "result.position"
        return "result.time"

    def _find_circuit_series_index(self, group_label: str, serial_num: int) -> int:
        if self._result.circuit is None:
            raise ValueError("No circuit data available for script generation.")
        elements = self._result.circuit.sources if group_label == "Sources" else self._result.circuit.power_sources
        for index, element in enumerate(elements):
            if element.serial_num == serial_num:
                return index
        raise ValueError(f"Could not locate circuit element #{serial_num} in {group_label!r}.")

    def _find_network_series_index(self, element_name: str, element_num: int) -> int:
        if self._result.network is None:
            raise ValueError("No network data available for script generation.")
        for index, element in enumerate(self._result.network.elements):
            if element.element_num == element_num and element.element_name == element_name:
                return index
        raise ValueError(f"Could not locate network element {element_name!r} #{element_num}.")

    def _find_force_entry_index(self, property_num: int) -> int:
        if self._result.force_nodal is None:
            raise ValueError("No force nodal data available for script generation.")
        for index, entry in enumerate(self._result.force_nodal.entries):
            if entry.property_num == property_num:
                return index
        raise ValueError(f"Could not locate force nodal property #{property_num}.")

    def _script_series_expression(self, descriptor: PlotSeriesDescriptor) -> str:
        tree_path = descriptor.tree_path
        section = tree_path[0]

        if section == "Circuit" and len(tree_path) == 4:
            group_label, item_label, quantity = tree_path[1], tree_path[2], tree_path[3]
            _, _, serial_text = item_label.rpartition("#")
            serial_num = int(serial_text)
            element_index = self._find_circuit_series_index(group_label, serial_num)
            group_expr = "result.circuit.sources" if group_label == "Sources" else "result.circuit.power_sources"
            return f"{group_expr}[{element_index}].{quantity.lower()}"

        if section == "Network" and len(tree_path) == 3:
            item_label, quantity = tree_path[1], tree_path[2]
            element_name, _, element_num_text = item_label.rpartition(" #")
            element_num = int(element_num_text)
            element_index = self._find_network_series_index(element_name, element_num)
            return f"result.network.elements[{element_index}].{quantity.lower()}"

        if section == "Force Nodal" and len(tree_path) == 3:
            property_label, quantity = tree_path[1], tree_path[2]
            _, _, property_num_text = property_label.rpartition("#")
            property_num = int(property_num_text)
            entry_index = self._find_force_entry_index(property_num)
            component_map = {
                "Force X": "force_x",
                "Force Y": "force_y",
                "Force Z": "force_z",
                "Moment X": "force_mx",
                "Moment Y": "force_my",
                "Moment Z": "force_mz",
            }
            attr_name = component_map[quantity]
            return f"result.force_nodal.entries[{entry_index}].{attr_name}"

        raise ValueError(f"Unsupported plot series path: {tree_path!r}")

    def _script_plot_kwargs(self, descriptor: PlotSeriesDescriptor) -> list[tuple[str, Any]]:
        style = self._style_for_descriptor(descriptor)
        kwargs: list[tuple[str, Any]] = [
            ("label", self._display_label_for_descriptor(descriptor)),
            ("linestyle", style.line_style),
            ("linewidth", style.line_width),
        ]
        if style.marker != "None":
            kwargs.append(("marker", style.marker))
        if style.color is not None:
            kwargs.append(("color", style.color))
        return kwargs

    def _generate_script_text(self) -> str:
        selected_series = self._checked_series()
        x_option = self._selected_x_option()
        invalid_x = bool(self._plot_settings.x_log_scale and (x_option.values <= 0).any())
        invalid_y_series: list[str] = []
        mismatched_series: list[str] = []
        plotted_series: list[PlotSeriesDescriptor] = []

        for descriptor in selected_series:
            if len(descriptor.values) != len(x_option.values):
                mismatched_series.append(self._display_label_for_descriptor(descriptor))
                continue
            if invalid_x:
                continue
            if self._plot_settings.y_log_scale and (descriptor.values <= 0).any():
                invalid_y_series.append(self._display_label_for_descriptor(descriptor))
                continue
            plotted_series.append(descriptor)

        imports = [
            "from matplotlib.figure import Figure",
            "from pyemsi import EMSolutionOutput, gui",
        ]
        if self._plot_settings.style_preset:
            imports.insert(1, "from matplotlib import style as mpl_style")

        lines = [
            *imports,
            "",
            'result = EMSolutionOutput.from_file("output.json")',
            f"x_values = {self._script_x_expression()}",
            "",
        ]

        body = [
            "fig = Figure()",
            "ax = fig.add_subplot(111)",
            f"ax.set_xscale({('log' if self._plot_settings.x_log_scale else 'linear')!r})",
            f"ax.set_yscale({('log' if self._plot_settings.y_log_scale else 'linear')!r})",
        ]

        if invalid_x:
            body.append("# X-axis log scale requires all X values to be greater than zero.")
        for label in mismatched_series:
            body.append(f"# Skipped series with incompatible lengths: {label}")
        for label in invalid_y_series:
            body.append(f"# Skipped series with non-positive Y values for log scale: {label}")

        for index, descriptor in enumerate(plotted_series, start=1):
            variable_name = f"y_values_{index}"
            body.append(f"{variable_name} = {self._script_series_expression(descriptor)}")
            body.append("ax.plot(")
            body.append("    x_values,")
            body.append(f"    {variable_name},")
            for key, value in self._script_plot_kwargs(descriptor):
                body.append(f"    {key}={value!r},")
            body.append(")")

        if plotted_series:
            if self._plot_settings.legend_mode != "none":
                body.append(f"ax.legend(loc={self._plot_settings.legend_mode!r})")
            if len(x_option.values) > 0:
                if self._plot_settings.x_log_scale:
                    body.append("positive_x = x_values[x_values > 0]")
                    body.append("if len(positive_x) > 0:")
                    body.append("    ax.set_xlim(positive_x[0], positive_x[-1])")
                else:
                    body.append("ax.set_xlim(x_values[0], x_values[-1])")
        else:
            empty_message = "Select one or more series to preview."
            if selected_series and (invalid_x or invalid_y_series):
                empty_message = "No compatible series for the current plot settings."
            body.extend(
                [
                    "ax.text(",
                    "    0.5,",
                    "    0.5,",
                    f"    {empty_message!r},",
                    "    ha='center',",
                    "    va='center',",
                    "    transform=ax.transAxes,",
                    ")",
                ]
            )

        grid_mode = self._plot_settings.grid_mode
        if grid_mode == "off":
            body.append("ax.grid(False)")
        elif grid_mode == "major":
            body.append("ax.grid(True, axis='both', which='major')")
        else:
            body.append(f"ax.grid(True, axis={grid_mode!r})")

        body.extend(
            [
                f"ax.set_title({self._effective_title(selected_series)!r})",
                f"ax.set_xlabel({self._effective_x_label()!r})",
                f"ax.set_ylabel({self._effective_y_label(selected_series)!r})",
            ]
        )

        if self._plot_settings.style_preset:
            lines.append(f"with mpl_style.context({self._plot_settings.style_preset!r}):")
            lines.extend(_indent_lines(body, "    "))
        else:
            lines.extend(body)

        lines.extend(["", f"gui.add_figure(fig, {self._effective_title(selected_series)!r})"])
        return "\n".join(lines)

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
            button.setIcon(QIcon(":/icons/Style.svg"))
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
        dialog.settingsApplied.connect(self._apply_plot_settings)
        dialog.settingsCanceled.connect(self._apply_plot_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_plot_settings(dialog.settings())

    def _open_style_dialog_for_item(self, item: QTreeWidgetItem) -> None:
        descriptor = self._descriptor_for_item(item)
        if descriptor is None or item.checkState(0) != Qt.CheckState.Checked:
            return

        self._tree.setCurrentItem(item)
        dialog = SeriesStyleDialog(self._style_for_descriptor(descriptor), descriptor.label, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_series_style(descriptor, dialog.style())

    def _open_script_dialog(self) -> None:
        dialog = GeneratedScriptDialog(self._generate_script_text(), parent=self)
        dialog.exec()

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 0:
            return
        self._refresh_style_button_for_item(item)
        self._redraw_plot()

    def _draw_onto(self, figure: Figure) -> None:
        selected_series = self._checked_series()
        x_option = self._selected_x_option()
        plotted_count = 0
        invalid_y_series: list[str] = []
        invalid_x = bool(self._plot_settings.x_log_scale and (x_option.values <= 0).any())

        with _matplotlib_style_context(self._plot_settings.style_preset):
            figure.clear()
            ax = figure.add_subplot(111)
            ax.set_xscale("log" if self._plot_settings.x_log_scale else "linear")
            ax.set_yscale("log" if self._plot_settings.y_log_scale else "linear")

            for descriptor in selected_series:
                if len(descriptor.values) != len(x_option.values):
                    continue
                if invalid_x:
                    continue
                if self._plot_settings.y_log_scale and (descriptor.values <= 0).any():
                    invalid_y_series.append(self._display_label_for_descriptor(descriptor))
                    continue

                style = self._style_for_descriptor(descriptor)
                plot_kwargs = {
                    "label": self._display_label_for_descriptor(descriptor),
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
                empty_message = "Select one or more series to preview."
                if selected_series and (invalid_x or invalid_y_series):
                    empty_message = "No compatible series for the current plot settings."
                ax.text(
                    0.5,
                    0.5,
                    empty_message,
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
            else:
                self._apply_legend_mode(ax)
                if len(x_option.values) > 0:
                    if self._plot_settings.x_log_scale:
                        positive_x = x_option.values[x_option.values > 0]
                        if len(positive_x) > 0:
                            ax.set_xlim(positive_x[0], positive_x[-1])
                    else:
                        ax.set_xlim(x_option.values[0], x_option.values[-1])

            self._apply_grid_mode(ax)
            ax.set_title(self._effective_title(selected_series))
            ax.set_xlabel(self._effective_x_label())
            ax.set_ylabel(self._effective_y_label(selected_series))
            figure.tight_layout()

        self._set_warning_message(self._log_scale_warning_message(invalid_y_series, invalid_x))

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
