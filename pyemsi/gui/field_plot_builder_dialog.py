from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import math
import os

import numpy as np
import pyvista as pv
from PySide6.QtCore import QLocale, Qt, Signal
from PySide6.QtGui import QColor, QDoubleValidator, QIcon, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

import pyemsi.resources.resources  # noqa: F401
from pyemsi import Plotter
from pyemsi.gui.emsolution_output_plot_builder_dialog import GeneratedScriptDialog
from pyemsi.gui.femap_converter_dialog import _PathSelector
from pyemsi.plotter.colormaps import CMAP_CHOICES, cmap_choice_to_name, cmap_name_to_choice
from pyemsi.settings import SettingsManager

SCALAR_NAMES: tuple[str, ...] = (
    "B-Mag (T)",
    "Flux (A/m)",
    "J-Mag (A/m^2)",
    "Loss (W/m^3)",
    "F Nodal-Mag (N/m^3)",
    "F Lorents-Mag (N/m^3)",
    "Heat Density (W/m^3)",
    "Heat (W)",
)

CONTOUR_NAMES: tuple[str, ...] = SCALAR_NAMES

VECTOR_NAMES: tuple[str, ...] = (
    "B-Mag (T)",
    "B-Vec (T)",
    "Flux (A/m)",
    "J-Mag (A/m^2)",
    "J-Vec (A/m^2)",
    "Loss (W/m^3)",
    "F Nodal-Mag (N/m^3)",
    "F Nodal-Vec (N/m^3)",
    "F Lorents-Mag (N/m^3)",
    "F Lorents-Vec (N/m^3)",
    "Heat Density (W/m^3)",
    "Heat (W)",
)

VECTOR_SCALE_OPTIONS: tuple[tuple[str, str | bool | None], ...] = (
    ("Auto", None),
    ("Uniform", False),
    *tuple((name, name) for name in VECTOR_NAMES),
)

GLYPH_TYPE_OPTIONS: tuple[str, ...] = ("arrow", "cone", "sphere")
COLOR_MODE_OPTIONS: tuple[str, ...] = ("scale", "scalar", "vector")
INTERNAL_FIELD_NAMES: frozenset[str] = frozenset({"vtkOriginalCellIds", "vtkOriginalPointIds"})


class _ColorSelector(QWidget):
    """Color input with a swatch button that opens QColorDialog."""

    valueChanged = Signal(str)

    _SWATCH_SIZE = 20

    def __init__(self, initial: str = "white", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._line_edit = QLineEdit(initial, self)
        self._swatch_button = QPushButton(self)
        self._swatch_button.setFixedSize(self._SWATCH_SIZE + 8, self._SWATCH_SIZE + 4)
        self._swatch_button.setToolTip("Pick color…")
        self._swatch_button.clicked.connect(self._pick_color)
        self._line_edit.textChanged.connect(self._refresh_swatch)
        self._line_edit.textChanged.connect(self.valueChanged.emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._line_edit, 1)
        layout.addWidget(self._swatch_button)
        self._refresh_swatch()

    def value(self) -> str:
        return self._line_edit.text().strip()

    def set_value(self, color: str) -> None:
        self._line_edit.setText(color)

    def _refresh_swatch(self, _text: str | None = None) -> None:
        color = QColor(self._line_edit.text().strip())
        if not color.isValid():
            color = QColor("white")
        pixmap = QPixmap(self._SWATCH_SIZE, self._SWATCH_SIZE)
        pixmap.fill(color)
        self._swatch_button.setIcon(QIcon(pixmap))

    def _pick_color(self) -> None:
        current = QColor(self._line_edit.text().strip())
        if not current.isValid():
            current = QColor("white")
        chosen = QColorDialog.getColor(current, self, "Select Color")
        if chosen.isValid():
            self._line_edit.setText(chosen.name())


class _CollapsibleSection(QWidget):
    """Simple expandable section used to keep long forms compact."""

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        header_widget: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._content_widget: QWidget | None = None

        self._toggle_button = QToolButton(self)
        self._toggle_button.setText(title)
        self._toggle_button.setCheckable(True)
        self._toggle_button.setChecked(False)
        self._toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self._toggle_button.setStyleSheet(
            "QToolButton { border: none; font-weight: 600; padding: 4px 0; text-align: left; }"
        )
        self._toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._toggle_button.toggled.connect(self.set_expanded)

        self._summary_label = QLabel(self)
        self._summary_label.setStyleSheet("color: palette(mid);")
        self._summary_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._summary_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        if header_widget is not None:
            header_layout.addWidget(header_widget)
        header_layout.addWidget(self._toggle_button, 1)
        header_layout.addWidget(self._summary_label, 1)

        self._header_line = QFrame(self)
        self._header_line.setFrameShape(QFrame.Shape.HLine)
        self._header_line.setFrameShadow(QFrame.Shadow.Sunken)

        self._content_container = QWidget(self)
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(24, 0, 0, 0)
        self._content_layout.setSpacing(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addLayout(header_layout)
        layout.addWidget(self._header_line)
        layout.addWidget(self._content_container)

        self.set_expanded(False)

    def set_content_widget(self, widget: QWidget) -> None:
        self._content_widget = widget
        self._content_layout.addWidget(widget)

    def set_summary(self, text: str) -> None:
        self._summary_label.setText(text)

    def summary_text(self) -> str:
        return self._summary_label.text()

    def is_expanded(self) -> bool:
        return self._toggle_button.isChecked()

    def set_expanded(self, expanded: bool) -> None:
        self._toggle_button.blockSignals(True)
        self._toggle_button.setChecked(expanded)
        self._toggle_button.blockSignals(False)
        self._toggle_button.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self._content_container.setVisible(expanded)

    def set_content_enabled(self, enabled: bool) -> None:
        self._content_container.setEnabled(enabled)


def _combo_index_for_data(combo: QComboBox, data) -> int:
    index = combo.findData(data)
    return max(index, 0)


def _format_float_text(value: float) -> str:
    return format(value, ".15g")


def _unique_names(names: list[str]) -> list[str]:
    return list(dict.fromkeys(name for name in names if name))


def _vector_scale_options_from_names(names: list[str]) -> list[tuple[str, str | bool | None]]:
    return [
        ("Auto", None),
        ("Uniform", False),
        *[(name, name) for name in names],
    ]


@dataclass(slots=True)
class _PlotAnalysisResult:
    scalar_names: list[str]
    vector_names: list[str]
    scale_names: list[str]
    mesh_length: float
    array_maxima: dict[str, float]


class FieldPlotBuilderDialog(QDialog):
    def __init__(
        self,
        settings_manager: SettingsManager,
        browse_dir_getter: Callable[[], str | None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings_manager
        self._browse_dir_getter = browse_dir_getter

        self.setWindowTitle("Field Plot")
        self.setWindowIcon(QIcon(":/icons/Field.svg"))
        self.resize(720, 560)

        defaults = self._load_defaults()

        self._file_field = _PathSelector(
            defaults["field_file_path"],
            select_directory=False,
            browse_dir_getter=self._browse_dir_getter,
            parent=self,
        )
        self._title_edit = QLineEdit(defaults["title"], self)
        self._title_edit.setPlaceholderText("Field Plot")

        self._scalar_enabled_checkbox = QCheckBox("Enable Scalar", self)
        self._scalar_enabled_checkbox.setChecked(defaults["scalar_enabled"])
        self._scalar_name_combo = QComboBox(self)
        self._populate_named_combo(self._scalar_name_combo, list(SCALAR_NAMES), defaults["scalar_name"])
        self._scalar_mode_combo = QComboBox(self)
        self._scalar_mode_combo.addItem("element", "element")
        self._scalar_mode_combo.addItem("node", "node")
        self._scalar_mode_combo.setCurrentIndex(_combo_index_for_data(self._scalar_mode_combo, defaults["scalar_mode"]))
        self._scalar_cmap_combo = QComboBox(self)
        for choice in CMAP_CHOICES:
            self._scalar_cmap_combo.addItem(choice, choice)
        self._scalar_cmap_combo.setCurrentIndex(_combo_index_for_data(self._scalar_cmap_combo, defaults["scalar_cmap"]))
        self._scalar_section = QWidget(self)
        scalar_layout = QFormLayout(self._scalar_section)
        scalar_layout.addRow("Name:", self._scalar_name_combo)
        scalar_layout.addRow("Mode:", self._scalar_mode_combo)
        scalar_layout.addRow("Colormap:", self._scalar_cmap_combo)

        self._contour_enabled_checkbox = QCheckBox("Enable Contour", self)
        self._contour_enabled_checkbox.setChecked(defaults["contour_enabled"])
        self._contour_name_combo = QComboBox(self)
        self._populate_named_combo(self._contour_name_combo, list(CONTOUR_NAMES), defaults["contour_name"])
        self._contour_n_contours_spin = QSpinBox(self)
        self._contour_n_contours_spin.setRange(1, 999)
        self._contour_n_contours_spin.setValue(defaults["contour_n_contours"])
        self._contour_color_edit = _ColorSelector(defaults["contour_color"], self)
        self._contour_line_width_spin = QSpinBox(self)
        self._contour_line_width_spin.setRange(1, 100)
        self._contour_line_width_spin.setValue(defaults["contour_line_width"])
        self._contour_section = QWidget(self)
        contour_layout = QFormLayout(self._contour_section)
        contour_layout.addRow("Name:", self._contour_name_combo)
        contour_layout.addRow("Contours:", self._contour_n_contours_spin)
        contour_layout.addRow("Color:", self._contour_color_edit)
        contour_layout.addRow("Line Width:", self._contour_line_width_spin)

        self._vector_enabled_checkbox = QCheckBox("Enable Vector", self)
        self._vector_enabled_checkbox.setChecked(defaults["vector_enabled"])
        self._vector_name_combo = QComboBox(self)
        self._populate_named_combo(self._vector_name_combo, list(VECTOR_NAMES), defaults["vector_name"])
        self._vector_scale_combo = QComboBox(self)
        self._populate_scale_combo(list(VECTOR_SCALE_OPTIONS), defaults["vector_scale"])
        self._vector_glyph_type_combo = QComboBox(self)
        for glyph_type in GLYPH_TYPE_OPTIONS:
            self._vector_glyph_type_combo.addItem(glyph_type, glyph_type)
        self._vector_glyph_type_combo.setCurrentIndex(
            _combo_index_for_data(self._vector_glyph_type_combo, defaults["vector_glyph_type"])
        )
        vector_factor_validator = QDoubleValidator(self)
        vector_factor_validator.setNotation(QDoubleValidator.Notation.ScientificNotation)
        vector_factor_validator.setBottom(0.0)
        vector_factor_validator.setTop(1e300)
        vector_factor_validator.setDecimals(1000)
        vector_factor_validator.setLocale(QLocale.c())
        self._vector_factor_edit = QLineEdit(_format_float_text(float(defaults["vector_factor"])), self)
        self._vector_factor_edit.setValidator(vector_factor_validator)
        self._vector_factor_edit.setPlaceholderText("1.0")
        self._vector_use_tolerance_checkbox = QCheckBox(self)
        self._vector_use_tolerance_checkbox.setChecked(defaults["vector_tolerance"] is not None)
        self._vector_tolerance_spin = QDoubleSpinBox(self)
        self._vector_tolerance_spin.setRange(0.0, 1.0)
        self._vector_tolerance_spin.setDecimals(3)
        self._vector_tolerance_spin.setSingleStep(0.01)
        self._vector_tolerance_spin.setValue(
            defaults["vector_tolerance"] if defaults["vector_tolerance"] is not None else 0.1
        )
        tolerance_widget = QWidget(self)
        tolerance_layout = QHBoxLayout(tolerance_widget)
        tolerance_layout.setContentsMargins(0, 0, 0, 0)
        tolerance_layout.addWidget(self._vector_use_tolerance_checkbox)
        tolerance_layout.addWidget(self._vector_tolerance_spin, 1)
        self._vector_color_mode_combo = QComboBox(self)
        for color_mode in COLOR_MODE_OPTIONS:
            self._vector_color_mode_combo.addItem(color_mode, color_mode)
        self._vector_color_mode_combo.setCurrentIndex(
            _combo_index_for_data(self._vector_color_mode_combo, defaults["vector_color_mode"])
        )
        self._vector_section = QWidget(self)
        vector_layout = QFormLayout(self._vector_section)
        vector_layout.addRow("Name:", self._vector_name_combo)
        vector_layout.addRow("Scale:", self._vector_scale_combo)
        vector_layout.addRow("Glyph Type:", self._vector_glyph_type_combo)
        vector_layout.addRow("Factor:", self._vector_factor_edit)
        vector_layout.addRow("Tolerance:", tolerance_widget)
        vector_layout.addRow("Color Mode:", self._vector_color_mode_combo)

        file_layout = QFormLayout()
        file_layout.addRow("Field File:", self._file_field)
        file_layout.addRow("Title:", self._title_edit)

        helper_label = QLabel(
            "Click Analyse to inspect the selected file, refresh the available arrays, and auto-scale vectors to 10% of the mesh size. Until then, documented Plotter defaults are shown.",
            self,
        )
        helper_label.setWordWrap(True)
        helper_label.setStyleSheet("color: palette(mid);")

        self._scalar_panel = _CollapsibleSection("Scalar", self, header_widget=self._scalar_enabled_checkbox)
        self._scalar_panel.set_content_widget(self._scalar_section)
        self._contour_panel = _CollapsibleSection("Contour", self, header_widget=self._contour_enabled_checkbox)
        self._contour_panel.set_content_widget(self._contour_section)
        self._vector_panel = _CollapsibleSection("Vector", self, header_widget=self._vector_enabled_checkbox)
        self._vector_panel.set_content_widget(self._vector_section)

        layout = QVBoxLayout(self)
        layout.addLayout(file_layout)
        layout.addWidget(helper_label)

        self._feature_edges_color_edit = _ColorSelector(defaults["feature_edges_color"], self)
        self._feature_edges_line_width_spin = QSpinBox(self)
        self._feature_edges_line_width_spin.setRange(1, 100)
        self._feature_edges_line_width_spin.setValue(defaults["feature_edges_line_width"])
        self._feature_edges_opacity_spin = QDoubleSpinBox(self)
        self._feature_edges_opacity_spin.setRange(0.0, 1.0)
        self._feature_edges_opacity_spin.setDecimals(2)
        self._feature_edges_opacity_spin.setSingleStep(0.05)
        self._feature_edges_opacity_spin.setValue(defaults["feature_edges_opacity"])
        self._feature_edges_section = QWidget(self)
        feature_edges_layout = QFormLayout(self._feature_edges_section)
        feature_edges_layout.addRow("Color:", self._feature_edges_color_edit)
        feature_edges_layout.addRow("Line Width:", self._feature_edges_line_width_spin)
        feature_edges_layout.addRow("Opacity:", self._feature_edges_opacity_spin)
        self._feature_edges_panel = _CollapsibleSection("Feature Edges", self)
        self._feature_edges_panel.set_content_widget(self._feature_edges_section)

        self._sections_scroll_area = QScrollArea(self)
        self._sections_scroll_area.setWidgetResizable(True)
        self._sections_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._sections_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._sections_scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sections_container = QWidget(self._sections_scroll_area)
        sections_layout = QVBoxLayout(sections_container)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(10)
        sections_layout.addWidget(self._scalar_panel)
        sections_layout.addWidget(self._contour_panel)
        sections_layout.addWidget(self._vector_panel)
        sections_layout.addWidget(self._feature_edges_panel)
        sections_layout.addStretch(1)
        self._sections_scroll_area.setWidget(sections_container)
        layout.addWidget(self._sections_scroll_area, 1)

        button_row = QHBoxLayout()
        self._analyse_button = QPushButton("Analyse", self)
        self._analyse_button.setIcon(QIcon(":/icons/Telescope.svg"))
        self._script_button = QPushButton("Script...", self)
        self._script_button.setIcon(QIcon(":/icons/Code.svg"))
        self._plot_button = QPushButton("Plot", self)
        self._plot_button.setIcon(QIcon(":/icons/Field.svg"))
        self._cancel_button = QPushButton("Cancel", self)
        button_row.addWidget(self._analyse_button)
        button_row.addWidget(self._script_button)
        button_row.addStretch()
        button_row.addWidget(self._plot_button)
        button_row.addWidget(self._cancel_button)
        layout.addLayout(button_row)

        self._scalar_enabled_checkbox.toggled.connect(self._on_scalar_enabled_toggled)
        self._contour_enabled_checkbox.toggled.connect(self._on_contour_enabled_toggled)
        self._vector_enabled_checkbox.toggled.connect(self._on_vector_enabled_toggled)
        self._vector_use_tolerance_checkbox.toggled.connect(self._vector_tolerance_spin.setEnabled)
        self._scalar_name_combo.currentTextChanged.connect(self._update_scalar_panel_summary)
        self._scalar_mode_combo.currentTextChanged.connect(self._update_scalar_panel_summary)
        self._scalar_cmap_combo.currentTextChanged.connect(self._update_scalar_panel_summary)
        self._contour_name_combo.currentTextChanged.connect(self._update_contour_panel_summary)
        self._contour_n_contours_spin.valueChanged.connect(self._update_contour_panel_summary)
        self._contour_color_edit.valueChanged.connect(self._update_contour_panel_summary)
        self._vector_name_combo.currentTextChanged.connect(self._update_vector_panel_summary)
        self._vector_scale_combo.currentTextChanged.connect(self._update_vector_panel_summary)
        self._vector_glyph_type_combo.currentTextChanged.connect(self._update_vector_panel_summary)
        self._vector_factor_edit.textChanged.connect(self._update_vector_panel_summary)
        self._feature_edges_color_edit.valueChanged.connect(self._update_feature_edges_panel_summary)
        self._feature_edges_line_width_spin.valueChanged.connect(self._update_feature_edges_panel_summary)
        self._feature_edges_opacity_spin.valueChanged.connect(self._update_feature_edges_panel_summary)
        self._script_button.clicked.connect(self._open_script_dialog)
        self._analyse_button.clicked.connect(self._on_analyse)
        self._plot_button.clicked.connect(self._on_plot)
        self._cancel_button.clicked.connect(self.reject)
        self._plot_button.setDefault(True)
        self._plot_button.setFocus()

        self._on_scalar_enabled_toggled(self._scalar_enabled_checkbox.isChecked())
        self._on_contour_enabled_toggled(self._contour_enabled_checkbox.isChecked())
        self._on_vector_enabled_toggled(self._vector_enabled_checkbox.isChecked())
        self._feature_edges_panel.set_expanded(False)
        self._update_scalar_panel_summary()
        self._update_contour_panel_summary()
        self._update_vector_panel_summary()
        self._update_feature_edges_panel_summary()
        self._vector_tolerance_spin.setEnabled(self._vector_use_tolerance_checkbox.isChecked())

    def _load_defaults(self) -> dict[str, object]:
        field_file_path = self._settings.get_effective("tools.field_plot.filepath")
        if field_file_path is None:
            field_file_path = self._default_field_file_path()
        return {
            "field_file_path": field_file_path or "",
            "title": "Field Plot",
            "scalar_enabled": False,
            "scalar_name": SCALAR_NAMES[0],
            "scalar_mode": "node",
            "scalar_cmap": cmap_name_to_choice("viridis"),
            "contour_enabled": False,
            "contour_name": CONTOUR_NAMES[1],
            "contour_n_contours": 20,
            "contour_color": "red",
            "contour_line_width": 3,
            "vector_enabled": False,
            "vector_name": VECTOR_NAMES[1],
            "vector_scale": None,
            "vector_glyph_type": "arrow",
            "vector_factor": 1.0,
            "vector_tolerance": None,
            "vector_color_mode": "scale",
            "feature_edges_color": "white",
            "feature_edges_line_width": 1,
            "feature_edges_opacity": 1.0,
        }

    def _default_field_file_path(self) -> str:
        base_dir = self._settings.get_effective("tools.femap_converter.input_dir")
        if base_dir is None and self._settings.workspace_path is not None:
            base_dir = os.fspath(self._settings.workspace_path)

        output_dir = self._settings.get_effective("tools.femap_converter.output_dir") or ".pyemsi"
        output_name = self._settings.get_effective("tools.femap_converter.output_name") or "output"

        if not base_dir:
            return ""

        candidate = output_dir
        if not os.path.isabs(candidate):
            candidate = os.path.join(base_dir, candidate)
        candidate = os.path.join(candidate, f"{output_name}.pvd")
        return os.path.abspath(os.path.normpath(candidate))

    def _current_title(self) -> str:
        return self._title_edit.text().strip() or "Field Plot"

    def _populate_named_combo(self, combo: QComboBox, names: list[str], current_data: object) -> None:
        combo.clear()
        for name in names:
            combo.addItem(name, name)
        combo.setCurrentIndex(_combo_index_for_data(combo, current_data))

    def _populate_scale_combo(
        self,
        options: list[tuple[str, str | bool | None]],
        current_data: object,
    ) -> None:
        self._vector_scale_combo.clear()
        for label, data in options:
            self._vector_scale_combo.addItem(label, data)
        self._vector_scale_combo.setCurrentIndex(_combo_index_for_data(self._vector_scale_combo, current_data))

    def _set_stage_panel_state(self, panel: _CollapsibleSection, enabled: bool) -> None:
        panel.set_content_enabled(enabled)
        panel.set_expanded(enabled)

    def _on_scalar_enabled_toggled(self, checked: bool) -> None:
        self._set_stage_panel_state(self._scalar_panel, checked)
        self._update_scalar_panel_summary()

    def _on_contour_enabled_toggled(self, checked: bool) -> None:
        self._set_stage_panel_state(self._contour_panel, checked)
        self._update_contour_panel_summary()

    def _on_vector_enabled_toggled(self, checked: bool) -> None:
        self._set_stage_panel_state(self._vector_panel, checked)
        self._update_vector_panel_summary()

    def _update_scalar_panel_summary(self) -> None:
        if not self._scalar_enabled_checkbox.isChecked():
            self._scalar_panel.set_summary("Disabled")
            return
        self._scalar_panel.set_summary(
            " | ".join(
                (
                    str(self._scalar_name_combo.currentData()),
                    str(self._scalar_mode_combo.currentData()),
                    self._scalar_cmap_combo.currentText(),
                )
            )
        )

    def _update_contour_panel_summary(self) -> None:
        if not self._contour_enabled_checkbox.isChecked():
            self._contour_panel.set_summary("Disabled")
            return
        self._contour_panel.set_summary(
            f"{self._contour_name_combo.currentData()} | {self._contour_n_contours_spin.value()} contours | {self._contour_color_edit.value() or 'red'}"
        )

    def _vector_scale_summary(self) -> str:
        scale = self._vector_scale_combo.currentData()
        if scale is None:
            return "Auto"
        if scale is False:
            return "Uniform"
        return str(scale)

    def _update_vector_panel_summary(self) -> None:
        if not self._vector_enabled_checkbox.isChecked():
            self._vector_panel.set_summary("Disabled")
            return
        factor = self._vector_factor_edit.text().strip() or "1.0"
        self._vector_panel.set_summary(
            " | ".join(
                (
                    str(self._vector_name_combo.currentData()),
                    self._vector_scale_summary(),
                    str(self._vector_glyph_type_combo.currentData()),
                    f"x {factor}",
                )
            )
        )

    def _update_feature_edges_panel_summary(self) -> None:
        self._feature_edges_panel.set_summary(
            f"{self._feature_edges_color_edit.value() or 'white'} | {self._feature_edges_line_width_spin.value()} px | {self._feature_edges_opacity_spin.value():.2f}"
        )

    def _iter_mesh_blocks(self, mesh: object):
        get_block_name = getattr(mesh, "get_block_name", None)
        if callable(get_block_name):
            for idx, block in enumerate(mesh):
                if block is None:
                    continue
                block_name = get_block_name(idx)
                yield block, block_name if block_name else str(idx)
            return
        yield mesh, None

    def _array_component_count(self, array: object) -> int | None:
        ndim = getattr(array, "ndim", None)
        shape = getattr(array, "shape", None)
        if ndim is None or shape is None:
            return None
        if ndim == 1:
            return 1
        if ndim >= 2 and len(shape) >= 2:
            try:
                return int(shape[1])
            except (TypeError, ValueError):
                return None
        return None

    def _classify_attribute_names(self, attributes: object) -> tuple[list[str], list[str]]:
        scalar_names: list[str] = []
        vector_names: list[str] = []
        for name in getattr(attributes, "keys", lambda: [])():
            if str(name) in INTERNAL_FIELD_NAMES:
                continue
            component_count = self._array_component_count(attributes[name])
            if component_count == 1:
                scalar_names.append(str(name))
            elif component_count == 3:
                vector_names.append(str(name))
        return scalar_names, vector_names

    def _array_max_value(self, array: object) -> float | None:
        try:
            values = np.asarray(array, dtype=float)
        except (TypeError, ValueError):
            return None

        if values.size == 0:
            return None

        component_count = self._array_component_count(array)
        if component_count == 3 and values.ndim >= 2:
            magnitudes = np.linalg.norm(values, axis=1)
        else:
            magnitudes = np.abs(values).reshape(-1)

        finite_magnitudes = magnitudes[np.isfinite(magnitudes)]
        if finite_magnitudes.size == 0:
            return None
        return float(finite_magnitudes.max())

    def _mesh_length(self, mesh: object) -> float:
        length = getattr(mesh, "length", None)
        if isinstance(length, (int, float)) and math.isfinite(length):
            return float(length)

        bounds = getattr(mesh, "bounds", None)
        if bounds is not None and len(bounds) == 6:
            try:
                dx = float(bounds[1]) - float(bounds[0])
                dy = float(bounds[3]) - float(bounds[2])
                dz = float(bounds[5]) - float(bounds[4])
            except (TypeError, ValueError):
                dx = dy = dz = 0.0
            return math.sqrt(dx * dx + dy * dy + dz * dz)

        get_block_name = getattr(mesh, "get_block_name", None)
        if callable(get_block_name):
            block_lengths = [self._mesh_length(block) for block, _block_name in self._iter_mesh_blocks(mesh)]
            finite_lengths = [length for length in block_lengths if math.isfinite(length) and length > 0.0]
            if finite_lengths:
                return max(finite_lengths)
        return 0.0

    def _read_plotter_mesh_snapshot(self, plotter: Plotter):
        reader = getattr(plotter, "reader", None)
        if reader is None:
            return plotter.mesh

        mesh = reader.read()
        if isinstance(reader, pv.PVDReader):
            return mesh[0]
        return mesh

    def _iter_plotter_mesh_snapshots(self, plotter: Plotter):
        time_values = getattr(plotter, "time_values", None)
        if time_values is None:
            yield self._read_plotter_mesh_snapshot(plotter)
            return

        time_values_list = list(time_values)
        if not time_values_list:
            yield self._read_plotter_mesh_snapshot(plotter)
            return

        original_time_value = getattr(plotter, "active_time_value", None)
        try:
            for time_value in time_values_list:
                plotter.set_active_time_value(float(time_value))
                yield self._read_plotter_mesh_snapshot(plotter)
        finally:
            if original_time_value is not None:
                plotter.set_active_time_value(float(original_time_value))

    def _update_attribute_analysis(
        self,
        attributes: object,
        scalar_names: list[str],
        vector_names: list[str],
        array_maxima: dict[str, float],
    ) -> None:
        for name in getattr(attributes, "keys", lambda: [])():
            array_name = str(name)
            if array_name in INTERNAL_FIELD_NAMES:
                continue

            array = attributes[name]
            component_count = self._array_component_count(array)
            if component_count == 1:
                scalar_names.append(array_name)
            elif component_count == 3:
                vector_names.append(array_name)
            else:
                continue

            max_value = self._array_max_value(array)
            if max_value is None:
                continue
            array_maxima[array_name] = max(array_maxima.get(array_name, 0.0), max_value)

    def _discover_plot_arrays(self) -> _PlotAnalysisResult:
        filepath = self._file_field.value()
        assert filepath is not None
        plotter = None
        try:
            plotter = Plotter(filepath)
            scalar_names: list[str] = []
            vector_names: list[str] = []
            mesh_length = 0.0
            array_maxima: dict[str, float] = {}
            for mesh in self._iter_plotter_mesh_snapshots(plotter):
                mesh_length = max(mesh_length, self._mesh_length(mesh))
                for block, _block_name in self._iter_mesh_blocks(mesh):
                    self._update_attribute_analysis(block.point_data, scalar_names, vector_names, array_maxima)
                    self._update_attribute_analysis(block.cell_data, scalar_names, vector_names, array_maxima)
            scalar_names = _unique_names(scalar_names)
            vector_names = _unique_names(vector_names)
            scale_names = _unique_names([*scalar_names, *vector_names])
            return _PlotAnalysisResult(
                scalar_names=scalar_names,
                vector_names=vector_names,
                scale_names=scale_names,
                mesh_length=mesh_length,
                array_maxima=array_maxima,
            )
        finally:
            if plotter is not None:
                plotter.close()

    def _update_vector_factor_from_analysis(self, analysis: _PlotAnalysisResult) -> None:
        if not self._vector_enabled_checkbox.isChecked():
            return

        mesh_length = analysis.mesh_length
        if not math.isfinite(mesh_length) or mesh_length <= 0.0:
            raise ValueError("Unable to determine the mesh size for vector auto-scaling.")

        scale = self._vector_scale_combo.currentData()
        if scale is False:
            factor = 0.1 * mesh_length
        else:
            source_name = str(self._vector_name_combo.currentData()) if scale is None else str(scale)
            source_max = analysis.array_maxima.get(source_name)
            if source_max is None:
                raise ValueError(f"Unable to determine a maximum value for '{source_name}'.")
            if not math.isfinite(source_max) or source_max <= 0.0:
                raise ValueError(f"Maximum value for '{source_name}' must be greater than 0.")
            factor = 0.1 * mesh_length / source_max

        self._vector_factor_edit.setText(_format_float_text(factor))

    def _apply_discovered_plot_arrays(
        self,
        scalar_names: list[str],
        vector_names: list[str],
        scale_names: list[str],
    ) -> None:
        self._populate_named_combo(
            self._scalar_name_combo,
            scalar_names or list(SCALAR_NAMES),
            self._scalar_name_combo.currentData(),
        )
        self._populate_named_combo(
            self._contour_name_combo,
            scalar_names or list(CONTOUR_NAMES),
            self._contour_name_combo.currentData(),
        )
        self._populate_named_combo(
            self._vector_name_combo,
            vector_names or list(VECTOR_NAMES),
            self._vector_name_combo.currentData(),
        )
        self._populate_scale_combo(
            _vector_scale_options_from_names(scale_names or list(VECTOR_NAMES)),
            self._vector_scale_combo.currentData(),
        )

    def _has_enabled_stage(self) -> bool:
        return any(
            checkbox.isChecked()
            for checkbox in (
                self._scalar_enabled_checkbox,
                self._contour_enabled_checkbox,
                self._vector_enabled_checkbox,
            )
        )

    def _validate_for_plot(self) -> str | None:
        filepath = self._file_field.value()
        if not filepath:
            return "Field file is required."
        if not self._has_enabled_stage():
            return "Select at least one plotting stage."
        if self._vector_enabled_checkbox.isChecked():
            try:
                self._vector_factor()
            except ValueError as exc:
                return str(exc)
        return None

    def _validate_for_analysis(self) -> str | None:
        filepath = self._file_field.value()
        if not filepath:
            return "Field file is required."
        return None

    def _scalar_kwargs(self) -> dict[str, object]:
        return {
            "name": str(self._scalar_name_combo.currentData()),
            "mode": str(self._scalar_mode_combo.currentData()),
            "cmap": cmap_choice_to_name(str(self._scalar_cmap_combo.currentData())),
        }

    def _contour_kwargs(self) -> dict[str, object]:
        return {
            "name": str(self._contour_name_combo.currentData()),
            "n_contours": int(self._contour_n_contours_spin.value()),
            "color": self._contour_color_edit.value() or "red",
            "line_width": int(self._contour_line_width_spin.value()),
        }

    def _vector_tolerance(self) -> float | None:
        if not self._vector_use_tolerance_checkbox.isChecked():
            return None
        return float(self._vector_tolerance_spin.value())

    def _vector_factor(self) -> float:
        text = self._vector_factor_edit.text().strip()
        if not text:
            raise ValueError("Vector factor is required.")
        try:
            value = float(text)
        except ValueError as exc:
            raise ValueError("Vector factor must be a valid number.") from exc
        if not math.isfinite(value):
            raise ValueError("Vector factor must be finite.")
        if value <= 0.0:
            raise ValueError("Vector factor must be greater than 0.")
        return value

    def _vector_kwargs(self) -> dict[str, object]:
        return {
            "name": str(self._vector_name_combo.currentData()),
            "scale": self._vector_scale_combo.currentData(),
            "glyph_type": str(self._vector_glyph_type_combo.currentData()),
            "factor": self._vector_factor(),
            "tolerance": self._vector_tolerance(),
            "color_mode": str(self._vector_color_mode_combo.currentData()),
        }

    def _feature_edges_kwargs(self) -> dict[str, object]:
        return {
            "color": self._feature_edges_color_edit.value() or "white",
            "line_width": int(self._feature_edges_line_width_spin.value()),
            "opacity": float(self._feature_edges_opacity_spin.value()),
        }

    def _persist_settings(self) -> None:
        setter = self._settings.set_local if self._settings.workspace_path is not None else self._settings.set_global

        setter("tools.field_plot.filepath", self._file_field.value())
        self._settings.save()

    def _generate_script_text(self) -> str:
        filepath = self._file_field.value() or ""
        lines = [
            "from pyemsi import gui, Plotter",
            "",
            f"field_plot = Plotter({filepath!r})",
        ]
        if self._scalar_enabled_checkbox.isChecked():
            scalar_kwargs = self._scalar_kwargs()
            lines.append(
                "field_plot.set_scalar("
                f"name={scalar_kwargs['name']!r}, mode={scalar_kwargs['mode']!r}, cmap={scalar_kwargs['cmap']!r}"
                ")"
            )
        if self._contour_enabled_checkbox.isChecked():
            contour_kwargs = self._contour_kwargs()
            lines.append(
                "field_plot.set_contour("
                f"name={contour_kwargs['name']!r}, n_contours={contour_kwargs['n_contours']!r}, color={contour_kwargs['color']!r}, line_width={contour_kwargs['line_width']!r}"
                ")"
            )
        if self._vector_enabled_checkbox.isChecked():
            vector_kwargs = self._vector_kwargs()
            lines.append(
                "field_plot.set_vector("
                f"name={vector_kwargs['name']!r}, scale={vector_kwargs['scale']!r}, glyph_type={vector_kwargs['glyph_type']!r}, factor={vector_kwargs['factor']!r}, tolerance={vector_kwargs['tolerance']!r}, color_mode={vector_kwargs['color_mode']!r}"
                ")"
            )
        fe_kwargs = self._feature_edges_kwargs()
        lines.append(
            "field_plot.set_feature_edges("
            f"color={fe_kwargs['color']!r}, line_width={fe_kwargs['line_width']!r}, opacity={fe_kwargs['opacity']!r}"
            ")"
        )
        lines.extend(["", f"gui.add_field(field_plot, {self._current_title()!r})"])
        return "\n".join(lines)

    def _open_script_dialog(self) -> None:
        dialog = GeneratedScriptDialog(self._generate_script_text(), parent=self)
        dialog.exec()

    def _on_analyse(self) -> None:
        error_message = self._validate_for_analysis()
        if error_message is not None:
            QMessageBox.warning(self, "Invalid Field Plot", error_message)
            return

        try:
            analysis = self._discover_plot_arrays()
            self._apply_discovered_plot_arrays(analysis.scalar_names, analysis.vector_names, analysis.scale_names)
            self._update_vector_factor_from_analysis(analysis)
        except Exception as exc:
            QMessageBox.critical(self, "Field Plot Analysis Error", str(exc))
            return

    def _on_plot(self) -> None:
        error_message = self._validate_for_plot()
        if error_message is not None:
            QMessageBox.warning(self, "Invalid Field Plot", error_message)
            return

        filepath = self._file_field.value()
        assert filepath is not None
        plotter = None
        try:
            plotter = Plotter(filepath)
            if self._scalar_enabled_checkbox.isChecked():
                plotter.set_scalar(**self._scalar_kwargs())
            if self._contour_enabled_checkbox.isChecked():
                plotter.set_contour(**self._contour_kwargs())
            if self._vector_enabled_checkbox.isChecked():
                plotter.set_vector(**self._vector_kwargs())
            plotter.set_feature_edges(**self._feature_edges_kwargs())

            self._persist_settings()

            import pyemsi.gui as gui

            gui.add_field(plotter, self._current_title())
        except Exception as exc:
            if plotter is not None:
                plotter.close()
            QMessageBox.critical(self, "Field Plot Error", str(exc))
            return

        self.accept()
