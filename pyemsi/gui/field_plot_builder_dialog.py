from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import math
import os

from PySide6.QtCore import QLocale, Qt, Signal
from PySide6.QtGui import QColor, QDoubleValidator, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QFormLayout,
    QGridLayout,
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
from pyemsi.gui._field_file_metadata import FieldFileMetadata, inspect_field_file
from pyemsi.gui.emsolution_output_plot_builder_dialog import GeneratedScriptDialog
from pyemsi.plotter.colormaps import CMAP_CHOICES, cmap_choice_to_name, cmap_name_to_choice
from pyemsi.settings import SettingsManager

GLYPH_TYPE_OPTIONS: tuple[str, ...] = ("arrow", "cone", "sphere")
COLOR_MODE_OPTIONS: tuple[str, ...] = ("scale", "scalar", "vector")
VTK_FIELD_FILE_FILTER = (
    "VTK Field Files "
    "(*.vtk *.vtu *.vtp *.vti *.vtr *.vts *.vtm *.pvd *.pvtu *.pvtp *.pvti *.pvtr *.pvts)"
)
SUPPORTED_VTK_FIELD_SUFFIXES: frozenset[str] = frozenset(
    {
        ".vtk",
        ".vtu",
        ".vtp",
        ".vti",
        ".vtr",
        ".vts",
        ".vtm",
        ".pvd",
        ".pvtu",
        ".pvtp",
        ".pvti",
        ".pvtr",
        ".pvts",
    }
)


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
        self._toggle_button.setCheckable(True)
        self._toggle_button.setChecked(False)
        self._toggle_button.setText(title)
        self._toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self._toggle_button.setStyleSheet(
            "QToolButton { border: none; font-weight: 800; padding: 4px 0; text-align: left; }"
        )
        self._toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._toggle_button.toggled.connect(self.set_expanded)
        if header_widget is not None:
            self._toggle_button.setText("")
            self._toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            self._toggle_button.setFixedWidth(18)
            self._toggle_button.setStyleSheet("QToolButton { border: none; padding: 4px 0; }")

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


def _deformation_names(metadata) -> list[str]:
    # ponytail: cached FEMAP entries carry no point/cell association; offer everything there
    # and let Plotter raise if a cell vector is picked.
    associations = getattr(metadata, "vector_associations", None)
    if associations is None:
        return list(metadata.vector_names)
    return [name for name in metadata.vector_names if "point" in associations.get(name, ())]


@dataclass(slots=True)
class _CachedPlotMetadata:
    relative_path: str
    resolved_path: str
    updated_at_utc: str
    scalar_names: list[str]
    vector_names: list[str]
    scale_names: list[str]
    mesh_length: float
    array_ranges: dict[str, dict[str, float]]
    contour_names: list[str] | None = None
    scalar_associations: dict[str, frozenset[str]] | None = None
    vector_scale_names: dict[str, list[str]] | None = None


class FieldPlotBuilderDialog(QDialog):
    @staticmethod
    def _build_two_column_form(
        rows: list[tuple[tuple[str, QWidget], tuple[str, QWidget] | None]],
        parent: QWidget,
    ) -> QWidget:
        container = QWidget(parent)
        layout = QGridLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(6)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        for row_index, (left, right) in enumerate(rows):
            left_label = QLabel(f"{left[0]}:", container)
            layout.addWidget(left_label, row_index, 0)
            layout.addWidget(left[1], row_index, 1)
            if right is not None:
                right_label = QLabel(f"{right[0]}:", container)
                layout.addWidget(right_label, row_index, 2)
                layout.addWidget(right[1], row_index, 3)
        return container

    def __init__(
        self,
        settings_manager: SettingsManager,
        browse_dir_getter: Callable[[], str | None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings_manager
        self._browse_dir_getter = browse_dir_getter
        self._cached_fields: list[_CachedPlotMetadata] = []
        self._external_field: FieldFileMetadata | None = None

        self.setWindowTitle("Field Plot")
        self.setWindowIcon(QIcon(":/icons/Field.svg"))
        self.resize(720, 560)

        defaults = self._load_defaults()

        self._file_combo = QComboBox(self)
        self._file_combo.setPlaceholderText("Select a cached field file or browse for a VTK file")
        self._browse_button = QPushButton("Browse…", self)
        self._browse_button.setToolTip("Browse for a VTK field file")
        self._title_edit = QLineEdit(defaults["title"], self)
        self._title_edit.setPlaceholderText("Field Plot")

        self._scalar_enabled_checkbox = QCheckBox("Scalar", self)
        self._scalar_enabled_checkbox.setStyleSheet("font-weight: 800;")
        self._scalar_enabled_checkbox.setChecked(defaults["scalar_enabled"])
        self._scalar_name_combo = QComboBox(self)
        self._populate_named_combo(self._scalar_name_combo, [], defaults["scalar_name"])
        self._scalar_mode_combo = QComboBox(self)
        self._scalar_mode_combo.addItem("element", "element")
        self._scalar_mode_combo.addItem("node", "node")
        self._scalar_mode_combo.setCurrentIndex(_combo_index_for_data(self._scalar_mode_combo, defaults["scalar_mode"]))
        self._scalar_cmap_combo = QComboBox(self)
        for choice in CMAP_CHOICES:
            self._scalar_cmap_combo.addItem(choice, choice)
        self._scalar_cmap_combo.setCurrentIndex(_combo_index_for_data(self._scalar_cmap_combo, defaults["scalar_cmap"]))
        self._scalar_show_edges_checkbox = QCheckBox(self)
        self._scalar_show_edges_checkbox.setChecked(bool(defaults["scalar_show_edges"]))
        self._scalar_edge_color_edit = _ColorSelector(str(defaults["scalar_edge_color"]), self)
        self._scalar_edge_opacity_spin = QDoubleSpinBox(self)
        self._scalar_edge_opacity_spin.setRange(0.0, 1.0)
        self._scalar_edge_opacity_spin.setDecimals(2)
        self._scalar_edge_opacity_spin.setSingleStep(0.05)
        self._scalar_edge_opacity_spin.setValue(float(defaults["scalar_edge_opacity"]))
        self._scalar_section = self._build_two_column_form(
            [
                (("Name", self._scalar_name_combo), ("Mode", self._scalar_mode_combo)),
                (("Colormap", self._scalar_cmap_combo), ("Show Edges", self._scalar_show_edges_checkbox)),
                (("Edge Color", self._scalar_edge_color_edit), ("Edge Opacity", self._scalar_edge_opacity_spin)),
            ],
            self,
        )

        self._contour_enabled_checkbox = QCheckBox("Contour", self)
        self._contour_enabled_checkbox.setStyleSheet("font-weight: 800;")
        self._contour_enabled_checkbox.setChecked(defaults["contour_enabled"])
        self._contour_name_combo = QComboBox(self)
        self._populate_named_combo(self._contour_name_combo, [], defaults["contour_name"])
        self._contour_n_contours_spin = QSpinBox(self)
        self._contour_n_contours_spin.setRange(1, 999)
        self._contour_n_contours_spin.setValue(defaults["contour_n_contours"])
        self._contour_color_edit = _ColorSelector(defaults["contour_color"], self)
        self._contour_line_width_spin = QSpinBox(self)
        self._contour_line_width_spin.setRange(1, 100)
        self._contour_line_width_spin.setValue(defaults["contour_line_width"])
        self._contour_section = self._build_two_column_form(
            [
                (("Name", self._contour_name_combo), ("Contours", self._contour_n_contours_spin)),
                (("Color", self._contour_color_edit), ("Line Width", self._contour_line_width_spin)),
            ],
            self,
        )

        self._vector_enabled_checkbox = QCheckBox("Vector", self)
        self._vector_enabled_checkbox.setStyleSheet("font-weight: 800;")
        self._vector_enabled_checkbox.setChecked(defaults["vector_enabled"])
        self._vector_name_combo = QComboBox(self)
        self._populate_named_combo(self._vector_name_combo, [], defaults["vector_name"])
        self._vector_scale_combo = QComboBox(self)
        self._populate_scale_combo(_vector_scale_options_from_names([]), defaults["vector_scale"])
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
        self._suggest_factor_button = QPushButton(self)
        self._suggest_factor_button.setText("Suggest")
        self._suggest_factor_button.setIcon(QIcon(":/icons/Telescope.svg"))
        self._suggest_factor_button.setToolTip("Suggest a vector factor from the discovered field data")
        factor_widget = QWidget(self)
        factor_layout = QHBoxLayout(factor_widget)
        factor_layout.setContentsMargins(0, 0, 0, 0)
        factor_layout.setSpacing(6)
        factor_layout.addWidget(self._vector_factor_edit, 1)
        factor_layout.addWidget(self._suggest_factor_button)
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
        self._vector_section = self._build_two_column_form(
            [
                (("Name", self._vector_name_combo), ("Scale", self._vector_scale_combo)),
                (("Glyph Type", self._vector_glyph_type_combo), ("Factor", factor_widget)),
                (("Tolerance", tolerance_widget), ("Color Mode", self._vector_color_mode_combo)),
            ],
            self,
        )

        file_widget = QWidget(self)
        file_widget_layout = QHBoxLayout(file_widget)
        file_widget_layout.setContentsMargins(0, 0, 0, 0)
        file_widget_layout.setSpacing(6)
        file_widget_layout.addWidget(self._file_combo, 1)
        file_widget_layout.addWidget(self._browse_button)

        file_layout = QFormLayout()
        file_layout.addRow("Field File:", file_widget)
        file_layout.addRow("Title:", self._title_edit)

        helper_label = QLabel(
            "Choose a cached FEMAP field file or browse for a VTK-family file. Browsed files are inspected for "
            "point and cell scalar/vector arrays; Suggest uses the discovered mesh size and array ranges.",
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

        self._feature_edges_enabled_checkbox = QCheckBox("Feature Edges", self)
        self._feature_edges_enabled_checkbox.setStyleSheet("font-weight: 800;")
        self._feature_edges_enabled_checkbox.setChecked(defaults["feature_edges_enabled"])
        self._feature_edges_color_edit = _ColorSelector(defaults["feature_edges_color"], self)
        self._feature_edges_line_width_spin = QSpinBox(self)
        self._feature_edges_line_width_spin.setRange(1, 100)
        self._feature_edges_line_width_spin.setValue(defaults["feature_edges_line_width"])
        self._feature_edges_opacity_spin = QDoubleSpinBox(self)
        self._feature_edges_opacity_spin.setRange(0.0, 1.0)
        self._feature_edges_opacity_spin.setDecimals(2)
        self._feature_edges_opacity_spin.setSingleStep(0.05)
        self._feature_edges_opacity_spin.setValue(defaults["feature_edges_opacity"])
        self._feature_edges_remove_small_loops_checkbox = QCheckBox(self)
        self._feature_edges_remove_small_loops_checkbox.setChecked(defaults["feature_edges_remove_small_loops"])
        self._feature_edges_max_loop_edges_spin = QSpinBox(self)
        self._feature_edges_max_loop_edges_spin.setRange(3, 9999)
        self._feature_edges_max_loop_edges_spin.setValue(defaults["feature_edges_max_loop_edges"])
        self._feature_edges_feature_angle_spin = QDoubleSpinBox(self)
        self._feature_edges_feature_angle_spin.setRange(0.0, 180.0)
        self._feature_edges_feature_angle_spin.setDecimals(1)
        self._feature_edges_feature_angle_spin.setSingleStep(1.0)
        self._feature_edges_feature_angle_spin.setValue(float(defaults["feature_edges_feature_angle"]))
        self._feature_edges_section = self._build_two_column_form(
            [
                (("Color", self._feature_edges_color_edit), ("Line Width", self._feature_edges_line_width_spin)),
                (
                    ("Opacity", self._feature_edges_opacity_spin),
                    ("Feature Angle", self._feature_edges_feature_angle_spin),
                ),
                (
                    ("Remove Small Loops", self._feature_edges_remove_small_loops_checkbox),
                    ("Edge Count Threshold", self._feature_edges_max_loop_edges_spin),
                ),
            ],
            self,
        )
        self._feature_edges_panel = _CollapsibleSection(
            "Feature Edges",
            self,
            header_widget=self._feature_edges_enabled_checkbox,
        )
        self._feature_edges_panel.set_content_widget(self._feature_edges_section)

        self._deformation_enabled_checkbox = QCheckBox("Deformation", self)
        self._deformation_enabled_checkbox.setStyleSheet("font-weight: 800;")
        self._deformation_enabled_checkbox.setChecked(defaults["deformation_enabled"])
        self._deformation_name_combo = QComboBox(self)
        self._populate_named_combo(self._deformation_name_combo, [], defaults["deformation_name"])
        deformation_scale_validator = QDoubleValidator(self)
        deformation_scale_validator.setNotation(QDoubleValidator.Notation.ScientificNotation)
        deformation_scale_validator.setBottom(-1e300)
        deformation_scale_validator.setTop(1e300)
        deformation_scale_validator.setDecimals(1000)
        deformation_scale_validator.setLocale(QLocale.c())
        self._deformation_scale_edit = QLineEdit(_format_float_text(float(defaults["deformation_scale"])), self)
        self._deformation_scale_edit.setValidator(deformation_scale_validator)
        self._deformation_scale_edit.setPlaceholderText("1.0")
        self._suggest_deformation_scale_button = QPushButton(self)
        self._suggest_deformation_scale_button.setText("Suggest")
        self._suggest_deformation_scale_button.setIcon(QIcon(":/icons/Telescope.svg"))
        self._suggest_deformation_scale_button.setToolTip(
            "Suggest a deformation scale from the discovered field data"
        )
        deformation_scale_widget = QWidget(self)
        deformation_scale_layout = QHBoxLayout(deformation_scale_widget)
        deformation_scale_layout.setContentsMargins(0, 0, 0, 0)
        deformation_scale_layout.setSpacing(6)
        deformation_scale_layout.addWidget(self._deformation_scale_edit, 1)
        deformation_scale_layout.addWidget(self._suggest_deformation_scale_button)
        self._deformation_section = self._build_two_column_form(
            [(("Name", self._deformation_name_combo), ("Scale", deformation_scale_widget))],
            self,
        )
        self._deformation_panel = _CollapsibleSection(
            "Deformation",
            self,
            header_widget=self._deformation_enabled_checkbox,
        )
        self._deformation_panel.set_content_widget(self._deformation_section)

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
        sections_layout.addWidget(self._deformation_panel)
        sections_layout.addStretch(1)
        self._sections_scroll_area.setWidget(sections_container)
        layout.addWidget(self._sections_scroll_area, 1)

        button_row = QHBoxLayout()
        self._script_button = QPushButton("Script...", self)
        self._script_button.setIcon(QIcon(":/icons/Code.svg"))
        self._plot_button = QPushButton("Plot", self)
        self._plot_button.setIcon(QIcon(":/icons/Field.svg"))
        self._cancel_button = QPushButton("Cancel", self)
        button_row.addWidget(self._script_button)
        button_row.addStretch()
        button_row.addWidget(self._plot_button)
        button_row.addWidget(self._cancel_button)
        layout.addLayout(button_row)

        self._scalar_enabled_checkbox.toggled.connect(self._on_scalar_enabled_toggled)
        self._contour_enabled_checkbox.toggled.connect(self._on_contour_enabled_toggled)
        self._vector_enabled_checkbox.toggled.connect(self._on_vector_enabled_toggled)
        self._feature_edges_enabled_checkbox.toggled.connect(self._on_feature_edges_enabled_toggled)
        self._deformation_enabled_checkbox.toggled.connect(self._on_deformation_enabled_toggled)
        self._vector_use_tolerance_checkbox.toggled.connect(self._vector_tolerance_spin.setEnabled)
        self._scalar_show_edges_checkbox.toggled.connect(self._on_scalar_show_edges_toggled)
        self._feature_edges_remove_small_loops_checkbox.toggled.connect(
            self._feature_edges_max_loop_edges_spin.setEnabled
        )
        self._scalar_name_combo.currentTextChanged.connect(self._on_scalar_name_changed)
        self._scalar_mode_combo.currentTextChanged.connect(self._update_scalar_panel_summary)
        self._scalar_cmap_combo.currentTextChanged.connect(self._update_scalar_panel_summary)
        self._scalar_show_edges_checkbox.toggled.connect(self._update_scalar_panel_summary)
        self._scalar_edge_color_edit.valueChanged.connect(self._update_scalar_panel_summary)
        self._scalar_edge_opacity_spin.valueChanged.connect(self._update_scalar_panel_summary)
        self._contour_name_combo.currentTextChanged.connect(self._update_contour_panel_summary)
        self._contour_n_contours_spin.valueChanged.connect(self._update_contour_panel_summary)
        self._contour_color_edit.valueChanged.connect(self._update_contour_panel_summary)
        self._vector_name_combo.currentTextChanged.connect(self._on_vector_name_changed)
        self._vector_scale_combo.currentTextChanged.connect(self._update_vector_panel_summary)
        self._vector_glyph_type_combo.currentTextChanged.connect(self._update_vector_panel_summary)
        self._vector_factor_edit.textChanged.connect(self._update_vector_panel_summary)
        self._feature_edges_color_edit.valueChanged.connect(self._update_feature_edges_panel_summary)
        self._feature_edges_line_width_spin.valueChanged.connect(self._update_feature_edges_panel_summary)
        self._feature_edges_opacity_spin.valueChanged.connect(self._update_feature_edges_panel_summary)
        self._feature_edges_remove_small_loops_checkbox.toggled.connect(self._update_feature_edges_panel_summary)
        self._feature_edges_max_loop_edges_spin.valueChanged.connect(self._update_feature_edges_panel_summary)
        self._feature_edges_feature_angle_spin.valueChanged.connect(self._update_feature_edges_panel_summary)
        self._deformation_name_combo.currentTextChanged.connect(self._update_deformation_panel_summary)
        self._deformation_scale_edit.textChanged.connect(self._update_deformation_panel_summary)
        self._file_combo.currentIndexChanged.connect(self._on_field_selection_changed)
        self._browse_button.clicked.connect(self._on_browse_field_file)
        self._suggest_factor_button.clicked.connect(self._on_suggest_vector_factor)
        self._suggest_deformation_scale_button.clicked.connect(self._on_suggest_deformation_scale)
        self._script_button.clicked.connect(self._open_script_dialog)
        self._plot_button.clicked.connect(self._on_plot)
        self._cancel_button.clicked.connect(self.reject)
        self._plot_button.setDefault(True)
        self._plot_button.setFocus()

        self._on_scalar_enabled_toggled(self._scalar_enabled_checkbox.isChecked())
        self._on_contour_enabled_toggled(self._contour_enabled_checkbox.isChecked())
        self._on_vector_enabled_toggled(self._vector_enabled_checkbox.isChecked())
        self._on_feature_edges_enabled_toggled(self._feature_edges_enabled_checkbox.isChecked())
        self._on_deformation_enabled_toggled(self._deformation_enabled_checkbox.isChecked())
        self._update_scalar_panel_summary()
        self._update_contour_panel_summary()
        self._update_vector_panel_summary()
        self._update_feature_edges_panel_summary()
        self._update_deformation_panel_summary()
        self._on_scalar_show_edges_toggled(self._scalar_show_edges_checkbox.isChecked())
        self._vector_tolerance_spin.setEnabled(self._vector_use_tolerance_checkbox.isChecked())
        self._feature_edges_max_loop_edges_spin.setEnabled(self._feature_edges_remove_small_loops_checkbox.isChecked())
        self._reload_cached_fields()

    def _load_defaults(self) -> dict[str, object]:
        return {
            "title": "Field Plot",
            "scalar_enabled": False,
            "scalar_name": None,
            "scalar_mode": "node",
            "scalar_cmap": cmap_name_to_choice("jet"),
            "scalar_show_edges": True,
            "scalar_edge_color": "white",
            "scalar_edge_opacity": 0.25,
            "contour_enabled": False,
            "contour_name": None,
            "contour_n_contours": 20,
            "contour_color": "red",
            "contour_line_width": 3,
            "vector_enabled": False,
            "vector_name": None,
            "vector_scale": None,
            "vector_glyph_type": "arrow",
            "vector_factor": 1.0,
            "vector_tolerance": None,
            "vector_color_mode": "scale",
            "feature_edges_enabled": True,
            "feature_edges_color": "white",
            "feature_edges_line_width": 1,
            "feature_edges_opacity": 1.0,
            "feature_edges_remove_small_loops": True,
            "feature_edges_max_loop_edges": 10,
            "feature_edges_feature_angle": 30.0,
            "deformation_enabled": False,
            "deformation_name": None,
            "deformation_scale": 1.0,
        }

    def showEvent(self, event) -> None:
        self._reload_cached_fields()
        super().showEvent(event)

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

    def _clear_cached_plot_arrays(self) -> None:
        self._populate_named_combo(self._scalar_name_combo, [], None)
        self._populate_named_combo(self._contour_name_combo, [], None)
        self._populate_named_combo(self._vector_name_combo, [], None)
        self._populate_named_combo(self._deformation_name_combo, [], None)
        self._populate_scale_combo(_vector_scale_options_from_names([]), None)

    def _workspace_root(self) -> str | None:
        if self._settings.workspace_path is None:
            return None
        return os.path.abspath(os.path.normpath(os.fspath(self._settings.workspace_path)))

    def _resolve_cached_relative_path(self, relative_path: str) -> str | None:
        workspace_root = self._workspace_root()
        if not workspace_root:
            return None
        return os.path.abspath(os.path.normpath(os.path.join(workspace_root, relative_path)))

    def _selected_relative_path(self) -> str | None:
        data = self._file_combo.currentData()
        if data is None:
            return None
        value = str(data)
        return value if any(entry.relative_path == value for entry in self._cached_fields) else None

    def _selected_field_path(self) -> str | None:
        entry = self._current_cached_field()
        if entry is not None:
            return entry.resolved_path
        if self._external_field is not None and self._file_combo.currentData() == self._external_field.resolved_path:
            return self._external_field.resolved_path
        return None

    def _current_cached_field(self) -> _CachedPlotMetadata | None:
        relative_path = self._selected_relative_path()
        if relative_path is None:
            return None
        for entry in self._cached_fields:
            if entry.relative_path == relative_path:
                return entry
        return None

    def _current_field_metadata(self) -> _CachedPlotMetadata | FieldFileMetadata | None:
        cached_entry = self._current_cached_field()
        if cached_entry is not None:
            return cached_entry
        if self._external_field is not None and self._file_combo.currentData() == self._external_field.resolved_path:
            return self._external_field
        return None

    def _build_cached_plot_metadata(self, entry: dict[str, object]) -> _CachedPlotMetadata | None:
        relative_path = entry.get("relative_path")
        updated_at_utc = entry.get("updated_at_utc")
        mesh_length = entry.get("mesh_length")
        scalar_names = entry.get("scalar_names")
        vector_names = entry.get("vector_names")
        array_ranges = entry.get("ranges")
        if not isinstance(relative_path, str) or not isinstance(updated_at_utc, str):
            return None
        if not isinstance(mesh_length, (int, float)):
            return None
        if not isinstance(scalar_names, list) or not isinstance(vector_names, list) or not isinstance(array_ranges, dict):
            return None

        resolved_path = self._resolve_cached_relative_path(relative_path)
        if resolved_path is None or not os.path.isfile(resolved_path):
            return None

        scalar_name_values = [name for name in scalar_names if isinstance(name, str) and name]
        vector_name_values = [name for name in vector_names if isinstance(name, str) and name]
        normalized_ranges: dict[str, dict[str, float]] = {}
        for name, bounds in array_ranges.items():
            if not isinstance(name, str) or not isinstance(bounds, dict):
                continue
            minimum = bounds.get("min")
            maximum = bounds.get("max")
            if not isinstance(minimum, (int, float)) or not isinstance(maximum, (int, float)):
                continue
            normalized_ranges[name] = {"min": float(minimum), "max": float(maximum)}

        return _CachedPlotMetadata(
            relative_path=relative_path,
            resolved_path=resolved_path,
            updated_at_utc=updated_at_utc,
            scalar_names=scalar_name_values,
            vector_names=vector_name_values,
            scale_names=_unique_names([*scalar_name_values, *vector_name_values]),
            mesh_length=float(mesh_length),
            array_ranges=normalized_ranges,
        )

    def _inspect_external_field(self, filepath: str, *, show_error: bool) -> FieldFileMetadata | None:
        suffix = os.path.splitext(filepath)[1].lower()
        if suffix not in SUPPORTED_VTK_FIELD_SUFFIXES:
            if show_error:
                QMessageBox.critical(
                    self,
                    "Field File Error",
                    f"Unsupported field file type '{suffix or '(none)'}'. Select a VTK-family field file.",
                )
            return None

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        inspection_error: Exception | None = None
        try:
            metadata = inspect_field_file(filepath)
        except Exception as exc:
            metadata = None
            inspection_error = exc
        finally:
            QApplication.restoreOverrideCursor()

        if inspection_error is not None:
            if show_error:
                QMessageBox.critical(self, "Field File Error", str(inspection_error))
            return None
        assert metadata is not None
        if not metadata.scalar_names and not metadata.vector_names:
            if show_error:
                QMessageBox.critical(
                    self,
                    "Field File Error",
                    "The selected file contains no supported one-component scalar or three-component vector arrays.",
                )
            return None
        return metadata

    def _reload_cached_fields(self) -> None:
        if self._settings.workspace_path is not None:
            self._settings.load_workspace(self._settings.workspace_path)
        else:
            self._settings.load()
        cached_entries = self._settings.get_local("tools.field_plot.cached_pvds") or []
        valid_entries: list[_CachedPlotMetadata] = []
        normalized_entries: list[dict[str, object]] = []
        for entry in cached_entries:
            if not isinstance(entry, dict):
                continue
            metadata = self._build_cached_plot_metadata(entry)
            if metadata is None:
                continue
            valid_entries.append(metadata)
            normalized_entries.append(
                {
                    "relative_path": metadata.relative_path,
                    "updated_at_utc": metadata.updated_at_utc,
                    "mesh_length": metadata.mesh_length,
                    "scalar_names": list(metadata.scalar_names),
                    "vector_names": list(metadata.vector_names),
                    "ranges": dict(metadata.array_ranges),
                }
            )

        valid_entries.sort(key=lambda item: (item.updated_at_utc, item.relative_path.lower()), reverse=True)
        self._cached_fields = valid_entries

        selected_relative_path = self._settings.get_local("tools.field_plot.selected_relative_path")
        available_paths = {entry.relative_path for entry in valid_entries}
        selected_relative_path = selected_relative_path if selected_relative_path in available_paths else None

        remembered_filepath = self._settings.get_effective("tools.field_plot.filepath")
        external_field = None
        if selected_relative_path is None and isinstance(remembered_filepath, str) and remembered_filepath:
            normalized_filepath = os.path.abspath(os.path.normpath(remembered_filepath))
            if self._external_field is not None and self._external_field.resolved_path == normalized_filepath:
                external_field = self._external_field
            elif os.path.isfile(normalized_filepath):
                external_field = self._inspect_external_field(normalized_filepath, show_error=False)
        self._external_field = external_field

        if selected_relative_path is None and external_field is None:
            selected_relative_path = valid_entries[0].relative_path if valid_entries else None

        self._file_combo.blockSignals(True)
        self._file_combo.clear()
        for entry in valid_entries:
            self._file_combo.addItem(entry.relative_path, entry.relative_path)
        if external_field is not None:
            external_index = self._file_combo.count()
            self._file_combo.addItem(
                f"{os.path.basename(external_field.resolved_path)} (external)",
                external_field.resolved_path,
            )
            self._file_combo.setItemData(external_index, external_field.resolved_path, Qt.ItemDataRole.ToolTipRole)
        if external_field is not None and selected_relative_path is None:
            self._file_combo.setCurrentIndex(self._file_combo.count() - 1)
        elif selected_relative_path is not None:
            self._file_combo.setCurrentIndex(_combo_index_for_data(self._file_combo, selected_relative_path))
        self._file_combo.setEnabled(bool(valid_entries or external_field is not None))
        self._file_combo.blockSignals(False)

        needs_save = normalized_entries != cached_entries
        selected_filepath = self._selected_field_path()
        if self._settings.get_local("tools.field_plot.selected_relative_path") != selected_relative_path:
            needs_save = True
        if self._settings.get_local("tools.field_plot.filepath") != selected_filepath:
            needs_save = True

        if needs_save and self._settings.workspace_path is not None:
            self._settings.set_local("tools.field_plot.cached_pvds", normalized_entries)
            self._settings.set_local("tools.field_plot.selected_relative_path", selected_relative_path)
            self._settings.set_local("tools.field_plot.filepath", selected_filepath)
            self._settings.save()
        elif needs_save and self._settings.workspace_path is None:
            self._settings.set_global("tools.field_plot.filepath", selected_filepath)
            self._settings.save()

        self._on_field_selection_changed()

    def _vector_scale_names(
        self,
        metadata: _CachedPlotMetadata | FieldFileMetadata,
        vector_name: str | None,
    ) -> list[str]:
        if vector_name and metadata.vector_scale_names is not None:
            return metadata.vector_scale_names.get(vector_name, [])
        return metadata.scale_names

    def _apply_plot_arrays(self, metadata: _CachedPlotMetadata | FieldFileMetadata | None) -> None:
        current_scalar = self._scalar_name_combo.currentData()
        current_contour = self._contour_name_combo.currentData()
        current_vector = self._vector_name_combo.currentData()
        current_deformation = self._deformation_name_combo.currentData()
        current_scale = self._vector_scale_combo.currentData()
        scalar_names = metadata.scalar_names if metadata is not None else []
        contour_names = (
            metadata.contour_names
            if metadata is not None and metadata.contour_names is not None
            else scalar_names
        )
        vector_names = metadata.vector_names if metadata is not None else []
        self._populate_named_combo(self._scalar_name_combo, scalar_names, current_scalar)
        self._populate_named_combo(self._contour_name_combo, contour_names, current_contour)
        self._populate_named_combo(self._vector_name_combo, vector_names, current_vector)
        self._populate_named_combo(
            self._deformation_name_combo,
            _deformation_names(metadata) if metadata is not None else [],
            current_deformation,
        )
        selected_vector = self._vector_name_combo.currentData()
        scale_names = (
            self._vector_scale_names(metadata, str(selected_vector) if selected_vector is not None else None)
            if metadata is not None
            else []
        )
        self._populate_scale_combo(_vector_scale_options_from_names(scale_names), current_scale)
        self._update_scalar_mode_options()

    def _update_scalar_mode_options(self) -> None:
        current_mode = self._scalar_mode_combo.currentData()
        metadata = self._current_field_metadata()
        scalar_name = self._scalar_name_combo.currentData()
        associations = None
        if metadata is not None and metadata.scalar_associations is not None and scalar_name is not None:
            associations = metadata.scalar_associations.get(str(scalar_name))

        options: list[tuple[str, str]] = []
        if not associations or "cell" in associations:
            options.append(("element", "element"))
        if not associations or "point" in associations:
            options.append(("node", "node"))

        self._scalar_mode_combo.blockSignals(True)
        self._scalar_mode_combo.clear()
        for label, data in options:
            self._scalar_mode_combo.addItem(label, data)
        self._scalar_mode_combo.setCurrentIndex(_combo_index_for_data(self._scalar_mode_combo, current_mode))
        self._scalar_mode_combo.setEnabled(len(options) > 1)
        self._scalar_mode_combo.blockSignals(False)

    def _on_field_selection_changed(self, _index: int | None = None) -> None:
        metadata = self._current_field_metadata()
        if metadata is None:
            self._clear_cached_plot_arrays()
        else:
            self._apply_plot_arrays(metadata)
        if self._settings.workspace_path is not None:
            self._settings.set_local("tools.field_plot.selected_relative_path", self._selected_relative_path())
            self._settings.set_local("tools.field_plot.filepath", self._selected_field_path())
        self._update_scalar_panel_summary()
        self._update_contour_panel_summary()
        self._update_vector_panel_summary()
        self._update_deformation_panel_summary()

    def _on_scalar_name_changed(self, _text: str | None = None) -> None:
        self._update_scalar_mode_options()
        self._update_scalar_panel_summary()

    def _on_vector_name_changed(self, _text: str | None = None) -> None:
        current_scale = self._vector_scale_combo.currentData()
        metadata = self._current_field_metadata()
        vector_name = self._vector_name_combo.currentData()
        scale_names = (
            self._vector_scale_names(metadata, str(vector_name) if vector_name is not None else None)
            if metadata is not None
            else []
        )
        self._populate_scale_combo(_vector_scale_options_from_names(scale_names), current_scale)
        self._update_vector_panel_summary()

    def _browse_initial_directory(self) -> str:
        selected_path = self._selected_field_path()
        if selected_path:
            selected_directory = os.path.dirname(selected_path)
            if os.path.isdir(selected_directory):
                return selected_directory

        if self._browse_dir_getter is not None:
            browse_directory = self._browse_dir_getter()
            if browse_directory and os.path.isdir(browse_directory):
                return os.path.abspath(os.path.normpath(browse_directory))

        workspace_root = self._workspace_root()
        if workspace_root and os.path.isdir(workspace_root):
            return workspace_root
        return os.getcwd()

    def _select_external_field(self, metadata: FieldFileMetadata) -> None:
        self._file_combo.blockSignals(True)
        previous_external_path = self._external_field.resolved_path if self._external_field is not None else None
        if previous_external_path is not None and previous_external_path != metadata.resolved_path:
            previous_external_index = self._file_combo.findData(previous_external_path)
            if previous_external_index >= 0:
                self._file_combo.removeItem(previous_external_index)
        self._external_field = metadata

        external_index = self._file_combo.findData(metadata.resolved_path)
        if external_index < 0:
            external_index = self._file_combo.count()
            self._file_combo.addItem(
                f"{os.path.basename(metadata.resolved_path)} (external)",
                metadata.resolved_path,
            )
        self._file_combo.setItemData(external_index, metadata.resolved_path, Qt.ItemDataRole.ToolTipRole)
        self._file_combo.setCurrentIndex(external_index)
        self._file_combo.setEnabled(True)
        self._file_combo.blockSignals(False)
        self._on_field_selection_changed()

        setter = self._settings.set_local if self._settings.workspace_path is not None else self._settings.set_global
        setter("tools.field_plot.filepath", metadata.resolved_path)
        if self._settings.workspace_path is not None:
            self._settings.set_local("tools.field_plot.selected_relative_path", None)
        self._settings.save()

    def _on_browse_field_file(self) -> None:
        selected_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Select VTK Field File",
            self._browse_initial_directory(),
            VTK_FIELD_FILE_FILTER,
        )
        if not selected_path:
            return

        metadata = self._inspect_external_field(selected_path, show_error=True)
        if metadata is not None:
            self._select_external_field(metadata)

    def _on_scalar_enabled_toggled(self, checked: bool) -> None:
        self._set_stage_panel_state(self._scalar_panel, checked)
        self._update_scalar_panel_summary()

    def _on_scalar_show_edges_toggled(self, checked: bool) -> None:
        self._scalar_edge_color_edit.setEnabled(checked)
        self._scalar_edge_opacity_spin.setEnabled(checked)
        self._update_scalar_panel_summary()

    def _on_contour_enabled_toggled(self, checked: bool) -> None:
        self._set_stage_panel_state(self._contour_panel, checked)
        self._update_contour_panel_summary()

    def _on_vector_enabled_toggled(self, checked: bool) -> None:
        self._set_stage_panel_state(self._vector_panel, checked)
        self._update_vector_panel_summary()

    def _on_feature_edges_enabled_toggled(self, checked: bool) -> None:
        self._set_stage_panel_state(self._feature_edges_panel, checked)
        self._update_feature_edges_panel_summary()

    def _on_deformation_enabled_toggled(self, checked: bool) -> None:
        self._set_stage_panel_state(self._deformation_panel, checked)
        self._update_deformation_panel_summary()

    def _update_scalar_panel_summary(self) -> None:
        if not self._scalar_enabled_checkbox.isChecked():
            self._scalar_panel.set_summary("Disabled")
            return
        scalar_name = self._selected_name(self._scalar_name_combo, fallback="Select array")
        show_edges = self._scalar_show_edges_checkbox.isChecked()
        edges_text = (
            f"edges {self._scalar_edge_color_edit.value() or 'white'} @ {self._scalar_edge_opacity_spin.value():.2f}"
            if show_edges
            else "edges off"
        )
        self._scalar_panel.set_summary(
            " | ".join(
                (
                    scalar_name,
                    str(self._scalar_mode_combo.currentData()),
                    self._scalar_cmap_combo.currentText(),
                    edges_text,
                )
            )
        )

    def _update_contour_panel_summary(self) -> None:
        if not self._contour_enabled_checkbox.isChecked():
            self._contour_panel.set_summary("Disabled")
            return
        self._contour_panel.set_summary(
            f"{self._selected_name(self._contour_name_combo, fallback='Select array')} | {self._contour_n_contours_spin.value()} contours | {self._contour_color_edit.value() or 'red'}"
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
                    self._selected_name(self._vector_name_combo, fallback="Select array"),
                    self._vector_scale_summary(),
                    str(self._vector_glyph_type_combo.currentData()),
                    f"x {factor}",
                )
            )
        )

    def _selected_name(self, combo: QComboBox, *, fallback: str = "") -> str:
        data = combo.currentData()
        if data is None:
            return fallback
        return str(data)

    def _update_feature_edges_panel_summary(self) -> None:
        if not self._feature_edges_enabled_checkbox.isChecked():
            self._feature_edges_panel.set_summary("Disabled")
            return
        loop_text = (
            f"loops>={self._feature_edges_max_loop_edges_spin.value()}"
            if self._feature_edges_remove_small_loops_checkbox.isChecked()
            else "loops off"
        )
        self._feature_edges_panel.set_summary(
            " | ".join(
                (
                    self._feature_edges_color_edit.value() or "white",
                    f"{self._feature_edges_line_width_spin.value()} px",
                    f"{self._feature_edges_opacity_spin.value():.2f}",
                    loop_text,
                    f"angle {self._feature_edges_feature_angle_spin.value():.1f}",
                )
                )
            )

    def _update_deformation_panel_summary(self) -> None:
        if not self._deformation_enabled_checkbox.isChecked():
            self._deformation_panel.set_summary("Disabled")
            return
        scale = self._deformation_scale_edit.text().strip() or "1.0"
        self._deformation_panel.set_summary(
            f"{self._selected_name(self._deformation_name_combo, fallback='Select array')} | x {scale}"
        )

    def _update_deformation_scale_from_metadata(
        self,
        metadata: _CachedPlotMetadata | FieldFileMetadata,
    ) -> None:
        if not self._deformation_enabled_checkbox.isChecked():
            return

        deformation_name = self._deformation_name_combo.currentData()
        if deformation_name is None:
            raise ValueError("Select a field file and choose a displacement vector before suggesting a scale.")

        mesh_length = metadata.mesh_length
        if not math.isfinite(mesh_length) or mesh_length <= 0.0:
            raise ValueError("Unable to determine the mesh size for deformation auto-scaling.")

        source_name = str(deformation_name)
        source_range = metadata.array_ranges.get(source_name)
        if source_range is None:
            raise ValueError(f"Unable to determine range data for '{source_name}'.")
        source_max = source_range["max"]
        if not math.isfinite(source_max) or source_max <= 0.0:
            raise ValueError(f"Maximum value for '{source_name}' must be greater than 0.")

        self._deformation_scale_edit.setText(_format_float_text(0.1 * mesh_length / source_max))

    def _update_vector_factor_from_metadata(
        self,
        metadata: _CachedPlotMetadata | FieldFileMetadata,
    ) -> None:
        if not self._vector_enabled_checkbox.isChecked():
            return

        vector_name = self._vector_name_combo.currentData()
        if vector_name is None:
            raise ValueError("Select a field file and choose a vector field before suggesting a factor.")

        mesh_length = metadata.mesh_length
        if not math.isfinite(mesh_length) or mesh_length <= 0.0:
            raise ValueError("Unable to determine the mesh size for vector auto-scaling.")

        scale = self._vector_scale_combo.currentData()
        if scale is False:
            factor = 0.1 * mesh_length
        else:
            source_name = str(vector_name) if scale is None else str(scale)
            source_range = metadata.array_ranges.get(source_name)
            if source_range is None:
                raise ValueError(f"Unable to determine range data for '{source_name}'.")
            source_max = source_range["max"]
            if not math.isfinite(source_max) or source_max <= 0.0:
                raise ValueError(f"Maximum value for '{source_name}' must be greater than 0.")
            factor = 0.1 * mesh_length / source_max

        self._vector_factor_edit.setText(_format_float_text(factor))

    def _has_enabled_stage(self) -> bool:
        return any(
            checkbox.isChecked()
            for checkbox in (
                self._scalar_enabled_checkbox,
                self._contour_enabled_checkbox,
                self._vector_enabled_checkbox,
            )
        )

    def _validate_field_selection(self) -> str | None:
        if self._selected_field_path() is None:
            return "Select a cached field file or browse for a VTK field file."
        return None

    def _validate_for_plot(self) -> str | None:
        field_error = self._validate_field_selection()
        if field_error is not None:
            return field_error
        if not self._has_enabled_stage():
            return "Select at least one plotting stage."
        selection_error = self._validate_stage_selections()
        if selection_error is not None:
            return selection_error
        if self._vector_enabled_checkbox.isChecked():
            try:
                self._vector_factor()
            except ValueError as exc:
                return str(exc)
        if self._deformation_enabled_checkbox.isChecked():
            try:
                self._deformation_scale()
            except ValueError as exc:
                return str(exc)
        return None

    def _validate_stage_selections(self) -> str | None:
        if self._scalar_enabled_checkbox.isChecked() and self._scalar_name_combo.currentData() is None:
            return "Select a field file and choose a scalar field before plotting."
        if self._contour_enabled_checkbox.isChecked() and self._contour_name_combo.currentData() is None:
            return "Select a field file and choose a point-associated scalar field before plotting contours."
        if self._vector_enabled_checkbox.isChecked() and self._vector_name_combo.currentData() is None:
            return "Select a field file and choose a vector field before plotting."
        if self._deformation_enabled_checkbox.isChecked() and self._deformation_name_combo.currentData() is None:
            return "Select a field file and choose a displacement vector before plotting deformation."
        return None

    def _scalar_kwargs(self) -> dict[str, object]:
        return {
            "name": self._selected_name(self._scalar_name_combo),
            "mode": str(self._scalar_mode_combo.currentData()),
            "cmap": cmap_choice_to_name(str(self._scalar_cmap_combo.currentData())),
            "show_edges": self._scalar_show_edges_checkbox.isChecked(),
            "edge_color": self._scalar_edge_color_edit.value() or "white",
            "edge_opacity": float(self._scalar_edge_opacity_spin.value()),
        }

    def _contour_kwargs(self) -> dict[str, object]:
        return {
            "name": self._selected_name(self._contour_name_combo),
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
            "name": self._selected_name(self._vector_name_combo),
            "scale": self._vector_scale_combo.currentData(),
            "glyph_type": str(self._vector_glyph_type_combo.currentData()),
            "factor": self._vector_factor(),
            "tolerance": self._vector_tolerance(),
            "color_mode": str(self._vector_color_mode_combo.currentData()),
        }

    def _deformation_scale(self) -> float:
        text = self._deformation_scale_edit.text().strip()
        if not text:
            raise ValueError("Deformation scale is required.")
        try:
            value = float(text)
        except ValueError as exc:
            raise ValueError("Deformation scale must be a valid number.") from exc
        if not math.isfinite(value):
            raise ValueError("Deformation scale must be finite.")
        return value  # ponytail: zero and negative are valid per set_deformation()

    def _deformation_kwargs(self) -> dict[str, object]:
        return {
            "name": self._selected_name(self._deformation_name_combo),
            "scale": self._deformation_scale(),
        }

    def _feature_edges_kwargs(self) -> dict[str, object]:
        return {
            "color": self._feature_edges_color_edit.value() or "white",
            "line_width": int(self._feature_edges_line_width_spin.value()),
            "opacity": float(self._feature_edges_opacity_spin.value()),
            "remove_small_loops": self._feature_edges_remove_small_loops_checkbox.isChecked(),
            "max_loop_edges": int(self._feature_edges_max_loop_edges_spin.value()),
            "feature_angle": float(self._feature_edges_feature_angle_spin.value()),
        }

    def _persist_settings(self) -> None:
        setter = self._settings.set_local if self._settings.workspace_path is not None else self._settings.set_global

        setter("tools.field_plot.filepath", self._selected_field_path())
        if self._settings.workspace_path is not None:
            self._settings.set_local("tools.field_plot.selected_relative_path", self._selected_relative_path())
        self._settings.save()

    def _generate_script_text(self) -> str:
        filepath = self._selected_field_path() or ""
        lines = [
            "from pyemsi import gui, Plotter",
            "",
            f"field_plot = Plotter({filepath!r})",
        ]
        if self._scalar_enabled_checkbox.isChecked():
            scalar_kwargs = self._scalar_kwargs()
            lines.append(
                "field_plot.set_scalar("
                f"name={scalar_kwargs['name']!r}, mode={scalar_kwargs['mode']!r}, cmap={scalar_kwargs['cmap']!r}, "
                f"show_edges={scalar_kwargs['show_edges']!r}, edge_color={scalar_kwargs['edge_color']!r}, edge_opacity={scalar_kwargs['edge_opacity']!r}"
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
            f"color={fe_kwargs['color']!r}, line_width={fe_kwargs['line_width']!r}, opacity={fe_kwargs['opacity']!r}, remove_small_loops={fe_kwargs['remove_small_loops']!r}, max_loop_edges={fe_kwargs['max_loop_edges']!r}, feature_angle={fe_kwargs['feature_angle']!r}"
            ")"
        )
        if not self._feature_edges_enabled_checkbox.isChecked():
            lines.append("field_plot._feature_edges_props = None")
        if self._deformation_enabled_checkbox.isChecked():
            deformation_kwargs = self._deformation_kwargs()
            lines.append(
                "field_plot.set_deformation("
                f"name={deformation_kwargs['name']!r}, scale={deformation_kwargs['scale']!r}"
                ")"
            )
        lines.extend(["", f"gui.add_field(field_plot, {self._current_title()!r})"])
        return "\n".join(lines)

    def _open_script_dialog(self) -> None:
        error_message = self._validate_field_selection()
        if error_message is not None:
            QMessageBox.warning(self, "Invalid Field Plot", error_message)
            return
        error_message = self._validate_stage_selections()
        if error_message is not None:
            QMessageBox.warning(self, "Invalid Field Plot", error_message)
            return
        dialog = GeneratedScriptDialog(self._generate_script_text(), parent=self)
        dialog.exec()

    def _on_suggest_vector_factor(self) -> None:
        error_message = self._validate_field_selection()
        if error_message is not None:
            QMessageBox.warning(self, "Invalid Field Plot", error_message)
            return

        try:
            metadata = self._current_field_metadata()
            if metadata is None:
                raise ValueError("Select a field file before suggesting a vector factor.")
            self._update_vector_factor_from_metadata(metadata)
        except Exception as exc:
            QMessageBox.critical(self, "Field Plot Analysis Error", str(exc))
            return

    def _on_suggest_deformation_scale(self) -> None:
        error_message = self._validate_field_selection()
        if error_message is not None:
            QMessageBox.warning(self, "Invalid Field Plot", error_message)
            return

        try:
            metadata = self._current_field_metadata()
            if metadata is None:
                raise ValueError("Select a field file before suggesting a deformation scale.")
            self._update_deformation_scale_from_metadata(metadata)
        except Exception as exc:
            QMessageBox.critical(self, "Field Plot Analysis Error", str(exc))
            return

    def _on_plot(self) -> None:
        error_message = self._validate_for_plot()
        if error_message is not None:
            QMessageBox.warning(self, "Invalid Field Plot", error_message)
            return

        filepath = self._selected_field_path()
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
            if self._feature_edges_enabled_checkbox.isChecked():
                plotter.set_feature_edges(**self._feature_edges_kwargs())
            else:
                plotter._feature_edges_props = None
            if self._deformation_enabled_checkbox.isChecked():
                plotter.set_deformation(**self._deformation_kwargs())

            self._persist_settings()

            import pyemsi.gui as gui

            gui.add_field(plotter, self._current_title())
        except Exception as exc:
            if plotter is not None:
                plotter.close()
            QMessageBox.critical(self, "Field Plot Error", str(exc))
            return

        self.accept()
