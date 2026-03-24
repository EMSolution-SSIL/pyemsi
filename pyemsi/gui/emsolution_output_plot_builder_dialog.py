from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass, field, replace
from pathlib import Path
import shutil
from typing import Any

from matplotlib import style as mpl_style
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from matplotlib.figure import Figure

import pyemsi.resources.resources  # noqa: F401
import scienceplots  # noqa: F401
from pyemsi.gui._viewers._matplotlib import MatplotlibViewer
from pyemsi.io import EMSolutionOutput, PlotAxisOption, PlotSeriesDescriptor
from pyemsi.widgets.monaco_lsp import MonacoLspWidget


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
    show_title: bool = True
    share_x: bool = True
    x_label: str = ""
    y_label: str = ""
    style_preset: str | list[str] = ""
    legend_mode: str = "upper right"
    grid_mode: str = "both"
    x_log_scale: bool = False
    y_log_scale: bool = False


@dataclass
class PlotSubplotState:
    selected_series_keys: set[tuple[str, ...]] = field(default_factory=set)
    y_label: str = ""


PLOT_STYLE_PRESETS: tuple[tuple[str, str | list[str]], ...] = (
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
    # SciencePlots - Basic
    ("Science (no-latex)", ["science", "no-latex"]),
    ("Science (LaTeX)", ["science"]),
    ("Science + Grid (no-latex)", ["science", "no-latex", "grid"]),
    ("Science + Grid (LaTeX)", ["science", "grid"]),
    ("Science + Scatter (no-latex)", ["science", "no-latex", "scatter"]),
    ("Science + Notebook (no-latex)", ["science", "no-latex", "notebook"]),
    # SciencePlots - Journals
    ("Science + IEEE (no-latex)", ["science", "no-latex", "ieee"]),
    ("Science + IEEE (LaTeX)", ["science", "ieee"]),
    ("Science + Nature (no-latex)", ["science", "no-latex", "nature"]),
    ("Science + Nature (LaTeX)", ["science", "nature"]),
    # SciencePlots - Color cycles
    ("Science + Bright (no-latex)", ["science", "no-latex", "bright"]),
    ("Science + Vibrant (no-latex)", ["science", "no-latex", "vibrant"]),
    ("Science + Muted (no-latex)", ["science", "no-latex", "muted"]),
    ("Science + High-Contrast (no-latex)", ["science", "no-latex", "high-contrast"]),
    ("Science + Light (no-latex)", ["science", "no-latex", "light"]),
    ("Science + High-Vis (no-latex)", ["science", "no-latex", "high-vis"]),
    ("Science + Retro (no-latex)", ["science", "no-latex", "retro"]),
    ("Science + Std-Colors (no-latex)", ["science", "no-latex", "std-colors"]),
) + tuple(
    (f"Science + Discrete Rainbow {n} (no-latex)", ["science", "no-latex", f"discrete-rainbow-{n}"])
    for n in range(1, 24)
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


def _matplotlib_style_context(style_preset: str | list[str]):
    if not style_preset:
        return nullcontext()
    return mpl_style.context(style_preset)


def _indent_lines(lines: list[str], prefix: str) -> list[str]:
    return [f"{prefix}{line}" if line else "" for line in lines]


_LATEX_AVAILABLE: bool | None = None


def _check_latex_available() -> bool:
    global _LATEX_AVAILABLE
    if _LATEX_AVAILABLE is None:
        _LATEX_AVAILABLE = shutil.which("latex") is not None
    return _LATEX_AVAILABLE


def _style_preset_requires_latex(preset: str | list[str]) -> bool:
    if isinstance(preset, list):
        return "no-latex" not in preset
    return False


class GeneratedScriptDialog(QDialog):
    def __init__(self, script_text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Generated Plot Script")
        self.setWindowIcon(QIcon(":/icons/Code.svg"))
        self.resize(900, 700)
        self._script_text = script_text

        self._text_edit = MonacoLspWidget(language="python", parent=self)
        self._text_edit.setLanguage("python")
        self._text_edit.setTheme("vs")
        self._text_edit.setReadOnly(True)
        self._text_edit.setText(script_text)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=self)
        self._copy_button = button_box.addButton("Copy", QDialogButtonBox.ButtonRole.ActionRole)
        self._copy_button.setIcon(QIcon(":/icons/Copy.svg"))
        self._save_button = button_box.addButton("Save As...", QDialogButtonBox.ButtonRole.ActionRole)
        self._save_button.setIcon(QIcon(":/icons/Save-as.svg"))
        self._copy_button.clicked.connect(self._copy_script)
        self._save_button.clicked.connect(self._save_script_as)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self._text_edit, 1)
        layout.addWidget(button_box)

    def script_text(self) -> str:
        return self._script_text

    def _copy_script(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        app.clipboard().setText(self.script_text())

    def _main_window(self) -> QWidget | None:
        window = self.parentWidget()
        while window is not None:
            if hasattr(window, "explorer"):
                return window
            window = window.parentWidget()

        try:
            import pyemsi.gui as gui
        except Exception:
            return None
        return getattr(gui, "_window", None)

    def _default_save_path(self) -> str:
        window = self._main_window()
        explorer = getattr(window, "explorer", None)
        current_path = getattr(explorer, "current_path", None)
        if current_path:
            return str(Path(current_path) / "plot_script.py")
        return "plot_script.py"

    def _save_script_as(self) -> None:
        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Plot Script",
            self._default_save_path(),
            "Python Files (*.py)",
        )
        if not selected_path:
            return

        output_path = Path(selected_path)
        if output_path.suffix.lower() != ".py":
            output_path = output_path.with_suffix(".py")
        output_path.write_text(self.script_text(), encoding="utf-8")


class PlotSettingsDialog(QDialog):
    settingsApplied = Signal(object)
    settingsCanceled = Signal(object)
    subplotYLabelApplied = Signal(str)
    subplotYLabelCanceled = Signal(str)

    def __init__(
        self,
        x_options: dict[str, PlotAxisOption],
        settings: PlotDialogSettings,
        default_title: str,
        default_x_label: str,
        default_y_label: str,
        subplot_y_label: str = "",
        default_subplot_y_label: str = "",
        has_multiple_subplots: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Plot Settings")
        self.setWindowIcon(QIcon(":/icons/Gear.svg"))
        self._original_settings = replace(settings)
        self._original_subplot_y_label = subplot_y_label

        self._x_axis_combo = QComboBox(self)
        for option in x_options.values():
            self._x_axis_combo.addItem(option.axis_label, option.key)
        index = self._x_axis_combo.findData(settings.x_axis_key)
        self._x_axis_combo.setCurrentIndex(max(index, 0))

        self._title_edit = QLineEdit(settings.title, self)
        self._title_edit.setPlaceholderText(default_title)
        self._show_title_checkbox = QCheckBox(self)
        self._show_title_checkbox.setChecked(settings.show_title)
        self._x_label_edit = QLineEdit(settings.x_label, self)
        self._x_label_edit.setPlaceholderText(default_x_label)
        y_label_text = subplot_y_label if subplot_y_label or not settings.y_label else settings.y_label
        y_label_placeholder = default_subplot_y_label or default_y_label
        self._y_label_edit = QLineEdit(y_label_text, self)
        self._y_label_edit.setPlaceholderText(y_label_placeholder)
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
        self._share_x_checkbox = QCheckBox(self)
        self._share_x_checkbox.setChecked(settings.share_x)
        self._share_x_checkbox.setEnabled(has_multiple_subplots)

        form_layout = QFormLayout()
        form_layout.addRow("X Axis:", self._x_axis_combo)
        form_layout.addRow("Show Title:", self._show_title_checkbox)
        form_layout.addRow("Title:", self._title_edit)
        form_layout.addRow("X Label:", self._x_label_edit)
        form_layout.addRow("Y Label:", self._y_label_edit)
        form_layout.addRow("Style Preset:", self._style_preset_combo)
        form_layout.addRow("Legend:", self._legend_mode_combo)
        form_layout.addRow("Grid:", self._grid_mode_combo)
        form_layout.addRow("Log X Axis:", self._x_log_scale_checkbox)
        form_layout.addRow("Log Y Axis:", self._y_log_scale_checkbox)
        form_layout.addRow("Shared X:", self._share_x_checkbox)

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

        self._show_title_checkbox.toggled.connect(self._update_title_edit_state)
        self._update_title_edit_state(self._show_title_checkbox.isChecked())

    def _update_title_edit_state(self, checked: bool) -> None:
        self._title_edit.setEnabled(checked)

    def _on_apply(self) -> None:
        self.settingsApplied.emit(self.settings())
        self.subplotYLabelApplied.emit(self.subplot_y_label())

    def _on_rejected(self) -> None:
        self.settingsCanceled.emit(replace(self._original_settings))
        self.subplotYLabelCanceled.emit(self._original_subplot_y_label)
        self.reject()

    def settings(self) -> PlotDialogSettings:
        x_axis_key = str(self._x_axis_combo.currentData())
        return PlotDialogSettings(
            x_axis_key=x_axis_key,
            title=self._title_edit.text().strip(),
            show_title=self._show_title_checkbox.isChecked(),
            share_x=self._share_x_checkbox.isChecked(),
            x_label=self._x_label_edit.text().strip(),
            y_label=self._y_label_edit.text().strip(),
            style_preset=self._style_preset_combo.currentData() or "",
            legend_mode=str(self._legend_mode_combo.currentData()),
            grid_mode=str(self._grid_mode_combo.currentData()),
            x_log_scale=self._x_log_scale_checkbox.isChecked(),
            y_log_scale=self._y_log_scale_checkbox.isChecked(),
        )

    def subplot_y_label(self) -> str:
        return self._y_label_edit.text().strip()


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


class EMSolutionOutputPlotBuilderDialog(QDialog):
    SERIES_ROLE = Qt.ItemDataRole.UserRole + 1
    SETTINGS_COLUMN = 1
    ADD_SUBPLOT_DATA = "__add_subplot__"

    def __init__(self, source: EMSolutionOutput | str | Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if isinstance(source, EMSolutionOutput):
            result = source
            self._source_file_name = "output.json"
        else:
            source_path = Path(source).expanduser().resolve(strict=False)
            result = EMSolutionOutput.from_file(source_path)
            self._source_file_name = source_path.name

        self._result = result
        self._x_options = {option.key: option for option in result.get_plot_x_options()}
        self._series_descriptors = list(result.get_plot_series())
        self._descriptor_lookup = {descriptor.tree_path: descriptor for descriptor in self._series_descriptors}
        self._series_styles: dict[tuple[str, ...], PlotSeriesStyle] = {}
        self._subplots: list[PlotSubplotState] = [PlotSubplotState()]
        self._active_subplot_index = 0
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

        self._subplot_combo = QComboBox(self)
        self._delete_subplot_button = QPushButton("Delete Subplot", self)

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
        self._warning_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self._warning_label.hide()

        self._preview = MatplotlibViewer(parent=self)

        controls_widget = QWidget(self)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        subplot_row = QHBoxLayout()
        subplot_row.setContentsMargins(0, 0, 0, 0)
        subplot_row.addWidget(QLabel("Subplot:", self))
        subplot_row.addWidget(self._subplot_combo, 1)
        subplot_row.addWidget(self._delete_subplot_button)
        controls_layout.addLayout(subplot_row)
        controls_layout.addWidget(self._tree, 1)

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
        button_row.addWidget(self._plot_settings_button)
        button_row.addWidget(self._script_button)
        button_row.addStretch()
        button_row.addWidget(self._plot_button)
        button_row.addWidget(self._cancel_button)
        layout.addLayout(button_row)

        self._populate_tree()
        self._rebuild_subplot_selector()
        self._tree.expandAll()
        self._apply_subplot_selection_to_tree()
        self._refresh_tree_action_buttons()

        self._tree.itemChanged.connect(self._on_item_changed)
        self._subplot_combo.currentIndexChanged.connect(self._on_subplot_changed)
        self._delete_subplot_button.clicked.connect(self._delete_current_subplot)
        self._plot_settings_button.clicked.connect(self._open_plot_settings_dialog)
        self._script_button.clicked.connect(self._open_script_dialog)
        self._plot_button.clicked.connect(self._on_plot)
        self._cancel_button.clicked.connect(self.reject)

        self._plot_button.setDefault(True)
        self._plot_button.setFocus()

        self._redraw_plot()

    def _populate_tree(self) -> None:
        parent_lookup: dict[tuple[str, ...], QTreeWidgetItem] = {}
        for descriptor in self._series_descriptors:
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
        return self._checked_series_for_subplot(self._current_subplot_state())

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

    def _current_subplot_state(self) -> PlotSubplotState:
        return self._subplots[self._active_subplot_index]

    def _checked_series_for_subplot(self, subplot_state: PlotSubplotState) -> list[PlotSeriesDescriptor]:
        return [
            descriptor
            for descriptor in self._series_descriptors
            if self._style_key(descriptor) in subplot_state.selected_series_keys
        ]

    def _all_checked_series(self) -> list[PlotSeriesDescriptor]:
        selected: list[PlotSeriesDescriptor] = []
        for subplot_state in self._subplots:
            selected.extend(self._checked_series_for_subplot(subplot_state))
        return selected

    def _current_tree_checked_keys(self) -> set[tuple[str, ...]]:
        checked: set[tuple[str, ...]] = set()

        for item in self._iter_tree_items():
            descriptor = self._descriptor_for_item(item)
            if descriptor is not None and item.checkState(0) == Qt.CheckState.Checked:
                checked.add(self._style_key(descriptor))

        return checked

    def _sync_active_subplot_selection_from_tree(self) -> None:
        self._current_subplot_state().selected_series_keys = self._current_tree_checked_keys()

    def _apply_subplot_selection_to_tree(self) -> None:
        selected_keys = self._current_subplot_state().selected_series_keys
        self._tree.blockSignals(True)
        try:
            for item in self._iter_tree_items():
                descriptor = self._descriptor_for_item(item)
                if descriptor is None:
                    continue
                state = (
                    Qt.CheckState.Checked if self._style_key(descriptor) in selected_keys else Qt.CheckState.Unchecked
                )
                item.setCheckState(0, state)
        finally:
            self._tree.blockSignals(False)
        self._refresh_tree_action_buttons()

    def _rebuild_subplot_selector(self) -> None:
        self._subplot_combo.blockSignals(True)
        try:
            self._subplot_combo.clear()
            for index in range(len(self._subplots)):
                self._subplot_combo.addItem(str(index + 1), index)
            self._subplot_combo.addItem("Add New Subplot...", self.ADD_SUBPLOT_DATA)
            self._subplot_combo.setCurrentIndex(self._active_subplot_index)
        finally:
            self._subplot_combo.blockSignals(False)
        self._delete_subplot_button.setEnabled(len(self._subplots) > 1)

    def _set_active_subplot(self, subplot_index: int) -> None:
        self._active_subplot_index = subplot_index
        self._rebuild_subplot_selector()
        self._apply_subplot_selection_to_tree()
        self._redraw_plot()

    def _add_subplot(self) -> None:
        self._sync_active_subplot_selection_from_tree()
        self._subplots.append(PlotSubplotState())
        self._set_active_subplot(len(self._subplots) - 1)

    def _delete_current_subplot(self) -> None:
        if len(self._subplots) <= 1:
            return
        del self._subplots[self._active_subplot_index]
        next_index = min(self._active_subplot_index, len(self._subplots) - 1)
        self._set_active_subplot(next_index)

    def _on_subplot_changed(self, combo_index: int) -> None:
        data = self._subplot_combo.itemData(combo_index)
        if data == self.ADD_SUBPLOT_DATA:
            self._add_subplot()
            return

        subplot_index = int(data)
        if subplot_index == self._active_subplot_index:
            return

        self._sync_active_subplot_selection_from_tree()
        self._set_active_subplot(subplot_index)

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

    def _figure_title(self, selected_series: list[PlotSeriesDescriptor]) -> str:
        return self._plot_settings.title or self._default_title(selected_series)

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
        if not self._plot_settings.show_title:
            return ""
        return self._figure_title(selected_series)

    def _effective_x_label(self) -> str:
        return self._plot_settings.x_label or self._default_x_label()

    def _effective_y_label(
        self,
        selected_series: list[PlotSeriesDescriptor],
        subplot_state: PlotSubplotState | None = None,
    ) -> str:
        state = subplot_state or self._current_subplot_state()
        return state.y_label or self._default_y_label(selected_series)

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

    def _script_source_name(self) -> str:
        return self._source_file_name

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

    def _plotted_series_for_subplot(
        self,
        subplot_state: PlotSubplotState,
        x_option: PlotAxisOption,
    ) -> tuple[list[PlotSeriesDescriptor], list[str], list[str], bool]:
        selected_series = self._checked_series_for_subplot(subplot_state)
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

        return plotted_series, mismatched_series, invalid_y_series, invalid_x

    def _generate_script_text(self) -> str:
        all_selected_series = self._all_checked_series()
        x_option = self._selected_x_option()
        subplot_details = [
            (subplot_state, *self._plotted_series_for_subplot(subplot_state, x_option))
            for subplot_state in self._subplots
        ]

        imports = [
            "from matplotlib.figure import Figure",
            "from pyemsi import EMSolutionOutput, gui",
        ]
        if self._plot_settings.style_preset:
            imports.insert(1, "from matplotlib import style as mpl_style")
        if isinstance(self._plot_settings.style_preset, list):
            imports.insert(1, "import scienceplots")

        lines = [
            *imports,
            "",
            f"result = EMSolutionOutput.from_file({self._script_source_name()!r})",
            f"x_values = {self._script_x_expression()}",
            "",
        ]

        body = [
            "fig = Figure()",
        ]

        if len(subplot_details) > 1:
            body.append(
                f"axes = fig.subplots({len(subplot_details)}, 1, sharex={self._plot_settings.share_x!r}, squeeze=False)"
            )
            for subplot_index in range(1, len(subplot_details) + 1):
                body.append(f"ax_{subplot_index} = axes[{subplot_index - 1}][0]")

        for subplot_index, (subplot_state, plotted_series, mismatched_series, invalid_y_series, invalid_x) in enumerate(
            subplot_details,
            start=1,
        ):
            axis_name = "ax" if len(subplot_details) == 1 else f"ax_{subplot_index}"
            if len(subplot_details) == 1:
                body.append("ax = fig.add_subplot(111)")
            body.append(f"{axis_name}.set_xscale({('log' if self._plot_settings.x_log_scale else 'linear')!r})")
            body.append(f"{axis_name}.set_yscale({('log' if self._plot_settings.y_log_scale else 'linear')!r})")

            if invalid_x:
                body.append("# X-axis log scale requires all X values to be greater than zero.")
            for label in mismatched_series:
                body.append(f"# Skipped series with incompatible lengths: {label}")
            for label in invalid_y_series:
                body.append(f"# Skipped series with non-positive Y values for log scale: {label}")

            for series_index, descriptor in enumerate(plotted_series, start=1):
                if len(subplot_details) == 1:
                    variable_name = f"y_values_{series_index}"
                else:
                    variable_name = f"y_values_{subplot_index}_{series_index}"
                body.append(f"{variable_name} = {self._script_series_expression(descriptor)}")
                body.append(f"{axis_name}.plot(")
                body.append("    x_values,")
                body.append(f"    {variable_name},")
                for key, value in self._script_plot_kwargs(descriptor):
                    body.append(f"    {key}={value!r},")
                body.append(")")

            selected_series = self._checked_series_for_subplot(subplot_state)
            if plotted_series:
                if self._plot_settings.legend_mode != "none":
                    body.append(f"{axis_name}.legend(loc={self._plot_settings.legend_mode!r})")
                if len(x_option.values) > 0:
                    if self._plot_settings.x_log_scale:
                        body.append("positive_x = x_values[x_values > 0]")
                        body.append("if len(positive_x) > 0:")
                        body.append(f"    {axis_name}.set_xlim(positive_x[0], positive_x[-1])")
                    else:
                        body.append(f"{axis_name}.set_xlim(x_values[0], x_values[-1])")
            else:
                empty_message = "Select one or more series to preview."
                if selected_series and (invalid_x or invalid_y_series):
                    empty_message = "No compatible series for the current plot settings."
                body.extend(
                    [
                        f"{axis_name}.text(",
                        "    0.5,",
                        "    0.5,",
                        f"    {empty_message!r},",
                        "    ha='center',",
                        "    va='center',",
                        f"    transform={axis_name}.transAxes,",
                        ")",
                    ]
                )

            grid_mode = self._plot_settings.grid_mode
            if grid_mode == "off":
                body.append(f"{axis_name}.grid(False)")
            elif grid_mode == "major":
                body.append(f"{axis_name}.grid(True, axis='both', which='major')")
            else:
                body.append(f"{axis_name}.grid(True, axis={grid_mode!r})")
            body.append(f"{axis_name}.set_ylabel({self._effective_y_label(selected_series, subplot_state)!r})")

        if len(subplot_details) == 1:
            if self._plot_settings.show_title:
                body.append(f"ax.set_title({self._effective_title(all_selected_series)!r})")
            body.append(f"ax.set_xlabel({self._effective_x_label()!r})")
        else:
            if self._plot_settings.share_x:
                for subplot_index in range(1, len(subplot_details)):
                    body.append(f"ax_{subplot_index}.label_outer()")
            if self._plot_settings.show_title:
                body.append(f"fig.suptitle({self._effective_title(all_selected_series)!r})")
            body.append(f"ax_{len(subplot_details)}.set_xlabel({self._effective_x_label()!r})")

        if self._plot_settings.style_preset:
            lines.append(f"with mpl_style.context({self._plot_settings.style_preset!r}):")
            lines.extend(_indent_lines(body, "    "))
        else:
            lines.extend(body)

        lines.extend(["", f"gui.add_figure(fig, {self._figure_title(all_selected_series)!r})"])
        return "\n".join(lines)

    def _style_button_max_height(self, item: QTreeWidgetItem) -> int:
        item_index = self._tree.indexFromItem(item, 0)
        item_height = self._tree.sizeHintForIndex(item_index).height()
        if item_height > 0:
            return item_height
        return self._tree.fontMetrics().height() + 6

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
            button = QPushButton(QIcon(":/icons/Style.svg"), "", self._tree)
            # button.setIcon(QIcon(":/icons/Style.svg"))
            button.setAutoDefault(False)
            button.setDefault(False)
            button.setMinimumHeight(0)
            button.setStyleSheet("padding-top: 0px; padding-bottom: 0px; border: none;")
            button.clicked.connect(lambda checked=False, tree_item=item: self._open_style_dialog_for_item(tree_item))
            self._tree.setItemWidget(item, self.SETTINGS_COLUMN, button)
        button.setMaximumHeight(self._style_button_max_height(item))

    def _refresh_tree_action_buttons(self) -> None:
        for item in self._iter_tree_items():
            self._refresh_style_button_for_item(item)

    def _apply_plot_settings(self, settings: PlotDialogSettings) -> None:
        self._plot_settings = settings
        self._current_subplot_state().y_label = settings.y_label
        self._redraw_plot()

    def _apply_active_subplot_y_label(self, y_label: str) -> None:
        self._current_subplot_state().y_label = y_label
        self._redraw_plot()

    def _apply_series_style(self, descriptor: PlotSeriesDescriptor, style: PlotSeriesStyle) -> None:
        self._series_styles[self._style_key(descriptor)] = style
        self._redraw_plot()

    def _open_plot_settings_dialog(self) -> None:
        selected_series = self._checked_series()
        dialog = PlotSettingsDialog(
            self._x_options,
            self._plot_settings,
            self._default_title(self._all_checked_series()),
            self._default_x_label(),
            self._default_y_label(selected_series),
            subplot_y_label=self._current_subplot_state().y_label,
            default_subplot_y_label=self._default_y_label(selected_series),
            has_multiple_subplots=len(self._subplots) > 1,
            parent=self,
        )
        dialog.settingsApplied.connect(self._apply_plot_settings)
        dialog.settingsCanceled.connect(self._apply_plot_settings)
        dialog.subplotYLabelApplied.connect(self._apply_active_subplot_y_label)
        dialog.subplotYLabelCanceled.connect(self._apply_active_subplot_y_label)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_plot_settings(dialog.settings())
            self._apply_active_subplot_y_label(dialog.subplot_y_label())

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
        self._sync_active_subplot_selection_from_tree()
        self._refresh_style_button_for_item(item)
        self._redraw_plot()

    def _draw_onto(self, figure: Figure) -> None:
        all_selected_series = self._all_checked_series()
        x_option = self._selected_x_option()
        warning_invalid_y_series: list[str] = []
        invalid_x = False

        with _matplotlib_style_context(self._plot_settings.style_preset):
            figure.clear()
            if len(self._subplots) == 1:
                axes = [figure.add_subplot(111)]
            else:
                axes_array = figure.subplots(
                    len(self._subplots),
                    1,
                    sharex=self._plot_settings.share_x,
                    squeeze=False,
                )
                axes = [axes_array[index][0] for index in range(len(self._subplots))]

            for axis, subplot_state in zip(axes, self._subplots):
                selected_series = self._checked_series_for_subplot(subplot_state)
                plotted_series, _, invalid_y_series, subplot_invalid_x = self._plotted_series_for_subplot(
                    subplot_state,
                    x_option,
                )
                plotted_count = 0
                invalid_x = invalid_x or subplot_invalid_x
                warning_invalid_y_series.extend(invalid_y_series)

                axis.set_xscale("log" if self._plot_settings.x_log_scale else "linear")
                axis.set_yscale("log" if self._plot_settings.y_log_scale else "linear")

                for descriptor in plotted_series:
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
                    axis.plot(x_option.values, descriptor.values, **plot_kwargs)
                    plotted_count += 1

                if plotted_count == 0:
                    empty_message = "Select one or more series to preview."
                    if selected_series and (subplot_invalid_x or invalid_y_series):
                        empty_message = "No compatible series for the current plot settings."
                    axis.text(
                        0.5,
                        0.5,
                        empty_message,
                        ha="center",
                        va="center",
                        transform=axis.transAxes,
                    )
                else:
                    self._apply_legend_mode(axis)
                    if len(x_option.values) > 0:
                        if self._plot_settings.x_log_scale:
                            positive_x = x_option.values[x_option.values > 0]
                            if len(positive_x) > 0:
                                axis.set_xlim(positive_x[0], positive_x[-1])
                        else:
                            axis.set_xlim(x_option.values[0], x_option.values[-1])

                self._apply_grid_mode(axis)
                axis.set_ylabel(self._effective_y_label(selected_series, subplot_state))

            if len(axes) == 1:
                if self._plot_settings.show_title:
                    axes[0].set_title(self._effective_title(all_selected_series))
                axes[0].set_xlabel(self._effective_x_label())
            else:
                if self._plot_settings.share_x:
                    for axis in axes[:-1]:
                        axis.label_outer()
                if self._plot_settings.show_title:
                    figure.suptitle(self._effective_title(all_selected_series))
                axes[-1].set_xlabel(self._effective_x_label())

            if len(axes) > 1 and self._plot_settings.show_title and self._effective_title(all_selected_series):
                figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.97))
            else:
                figure.tight_layout()

        self._set_warning_message(self._log_scale_warning_message(warning_invalid_y_series, invalid_x))

    def _redraw_plot(self) -> None:
        if _style_preset_requires_latex(self._plot_settings.style_preset) and not _check_latex_available():
            self._preview.figure.clear()
            ax = self._preview.figure.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                "This style requires LaTeX, which is not installed.\n"
                "Please choose a '(no-latex)' variant from Plot Settings.",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            self._preview.draw()
            self._set_warning_message(
                "The selected style requires LaTeX, but LaTeX could not be found. "
                "Choose a '(no-latex)' variant or install a LaTeX distribution (e.g. MiKTeX)."
            )
            return
        self._draw_onto(self._preview.figure)
        self._preview.draw()

    def _on_plot(self) -> None:
        if _style_preset_requires_latex(self._plot_settings.style_preset) and not _check_latex_available():
            self._set_warning_message(
                "The selected style requires LaTeX, but LaTeX could not be found. "
                "Choose a '(no-latex)' variant or install a LaTeX distribution (e.g. MiKTeX)."
            )
            return

        import pyemsi.gui as gui

        figure = Figure()
        self._draw_onto(figure)
        title = self._figure_title(self._all_checked_series())
        gui.add_figure(figure, title)
        self.accept()
