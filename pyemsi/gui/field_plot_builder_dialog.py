from __future__ import annotations

from collections.abc import Callable
import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import pyemsi.resources.resources  # noqa: F401
from pyemsi import Plotter
from pyemsi.gui._viewers._emsolution_plot_dialog import GeneratedScriptDialog
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


def _combo_index_for_data(combo: QComboBox, data) -> int:
    index = combo.findData(data)
    return max(index, 0)


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
        self.setWindowIcon(QIcon(":/icons/Graph.svg"))
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
        for name in SCALAR_NAMES:
            self._scalar_name_combo.addItem(name, name)
        self._scalar_name_combo.setCurrentIndex(_combo_index_for_data(self._scalar_name_combo, defaults["scalar_name"]))
        self._scalar_mode_combo = QComboBox(self)
        self._scalar_mode_combo.addItem("element", "element")
        self._scalar_mode_combo.addItem("node", "node")
        self._scalar_mode_combo.setCurrentIndex(_combo_index_for_data(self._scalar_mode_combo, defaults["scalar_mode"]))
        self._scalar_cell2point_checkbox = QCheckBox(self)
        self._scalar_cell2point_checkbox.setChecked(defaults["scalar_cell2point"])
        self._scalar_cmap_combo = QComboBox(self)
        for choice in CMAP_CHOICES:
            self._scalar_cmap_combo.addItem(choice, choice)
        self._scalar_cmap_combo.setCurrentIndex(_combo_index_for_data(self._scalar_cmap_combo, defaults["scalar_cmap"]))
        self._scalar_section = QWidget(self)
        scalar_layout = QFormLayout(self._scalar_section)
        scalar_layout.addRow("Name:", self._scalar_name_combo)
        scalar_layout.addRow("Mode:", self._scalar_mode_combo)
        scalar_layout.addRow("Cell to Point:", self._scalar_cell2point_checkbox)
        scalar_layout.addRow("Colormap:", self._scalar_cmap_combo)

        self._contour_enabled_checkbox = QCheckBox("Enable Contour", self)
        self._contour_enabled_checkbox.setChecked(defaults["contour_enabled"])
        self._contour_name_combo = QComboBox(self)
        for name in CONTOUR_NAMES:
            self._contour_name_combo.addItem(name, name)
        self._contour_name_combo.setCurrentIndex(
            _combo_index_for_data(self._contour_name_combo, defaults["contour_name"])
        )
        self._contour_n_contours_spin = QSpinBox(self)
        self._contour_n_contours_spin.setRange(1, 999)
        self._contour_n_contours_spin.setValue(defaults["contour_n_contours"])
        self._contour_color_edit = QLineEdit(defaults["contour_color"], self)
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
        for name in VECTOR_NAMES:
            self._vector_name_combo.addItem(name, name)
        self._vector_name_combo.setCurrentIndex(_combo_index_for_data(self._vector_name_combo, defaults["vector_name"]))
        self._vector_scale_combo = QComboBox(self)
        for label, data in VECTOR_SCALE_OPTIONS:
            self._vector_scale_combo.addItem(label, data)
        self._vector_scale_combo.setCurrentIndex(
            _combo_index_for_data(self._vector_scale_combo, defaults["vector_scale"])
        )
        self._vector_glyph_type_combo = QComboBox(self)
        for glyph_type in GLYPH_TYPE_OPTIONS:
            self._vector_glyph_type_combo.addItem(glyph_type, glyph_type)
        self._vector_glyph_type_combo.setCurrentIndex(
            _combo_index_for_data(self._vector_glyph_type_combo, defaults["vector_glyph_type"])
        )
        self._vector_factor_spin = QDoubleSpinBox(self)
        self._vector_factor_spin.setRange(0.001, 1_000_000.0)
        self._vector_factor_spin.setDecimals(6)
        self._vector_factor_spin.setValue(defaults["vector_factor"])
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
        vector_layout.addRow("Factor:", self._vector_factor_spin)
        vector_layout.addRow("Tolerance:", tolerance_widget)
        vector_layout.addRow("Color Mode:", self._vector_color_mode_combo)

        file_layout = QFormLayout()
        file_layout.addRow("Field File:", self._file_field)
        file_layout.addRow("Title:", self._title_edit)

        helper_label = QLabel(
            "Array choices are based on the documented Plotter API and are not inspected from the selected file.",
            self,
        )
        helper_label.setWordWrap(True)
        helper_label.setStyleSheet("color: palette(mid);")

        layout = QVBoxLayout(self)
        layout.addLayout(file_layout)
        layout.addWidget(helper_label)
        layout.addWidget(self._scalar_enabled_checkbox)
        layout.addWidget(self._scalar_section)
        layout.addWidget(self._contour_enabled_checkbox)
        layout.addWidget(self._contour_section)
        layout.addWidget(self._vector_enabled_checkbox)
        layout.addWidget(self._vector_section)

        button_row = QHBoxLayout()
        self._script_button = QPushButton("Script...", self)
        self._script_button.setIcon(QIcon(":/icons/Code.svg"))
        self._plot_button = QPushButton("Plot", self)
        self._plot_button.setIcon(QIcon(":/icons/Graph.svg"))
        self._cancel_button = QPushButton("Cancel", self)
        button_row.addWidget(self._script_button)
        button_row.addStretch()
        button_row.addWidget(self._plot_button)
        button_row.addWidget(self._cancel_button)
        layout.addLayout(button_row)

        self._scalar_enabled_checkbox.toggled.connect(self._scalar_section.setEnabled)
        self._contour_enabled_checkbox.toggled.connect(self._contour_section.setEnabled)
        self._vector_enabled_checkbox.toggled.connect(self._vector_section.setEnabled)
        self._vector_use_tolerance_checkbox.toggled.connect(self._vector_tolerance_spin.setEnabled)
        self._script_button.clicked.connect(self._open_script_dialog)
        self._plot_button.clicked.connect(self._on_plot)
        self._cancel_button.clicked.connect(self.reject)
        self._plot_button.setDefault(True)
        self._plot_button.setFocus()

        self._scalar_section.setEnabled(self._scalar_enabled_checkbox.isChecked())
        self._contour_section.setEnabled(self._contour_enabled_checkbox.isChecked())
        self._vector_section.setEnabled(self._vector_enabled_checkbox.isChecked())
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
            "scalar_mode": "element",
            "scalar_cell2point": True,
            "scalar_cmap": cmap_name_to_choice("viridis"),
            "contour_enabled": False,
            "contour_name": CONTOUR_NAMES[1],
            "contour_n_contours": 10,
            "contour_color": "red",
            "contour_line_width": 3,
            "vector_enabled": False,
            "vector_name": VECTOR_NAMES[1],
            "vector_scale": None,
            "vector_glyph_type": "arrow",
            "vector_factor": 1.0,
            "vector_tolerance": None,
            "vector_color_mode": "scale",
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
        return None

    def _scalar_kwargs(self) -> dict[str, object]:
        return {
            "name": str(self._scalar_name_combo.currentData()),
            "mode": str(self._scalar_mode_combo.currentData()),
            "cell2point": self._scalar_cell2point_checkbox.isChecked(),
            "cmap": cmap_choice_to_name(str(self._scalar_cmap_combo.currentData())),
        }

    def _contour_kwargs(self) -> dict[str, object]:
        return {
            "name": str(self._contour_name_combo.currentData()),
            "n_contours": int(self._contour_n_contours_spin.value()),
            "color": self._contour_color_edit.text().strip() or "red",
            "line_width": int(self._contour_line_width_spin.value()),
        }

    def _vector_tolerance(self) -> float | None:
        if not self._vector_use_tolerance_checkbox.isChecked():
            return None
        return float(self._vector_tolerance_spin.value())

    def _vector_kwargs(self) -> dict[str, object]:
        return {
            "name": str(self._vector_name_combo.currentData()),
            "scale": self._vector_scale_combo.currentData(),
            "glyph_type": str(self._vector_glyph_type_combo.currentData()),
            "factor": float(self._vector_factor_spin.value()),
            "tolerance": self._vector_tolerance(),
            "color_mode": str(self._vector_color_mode_combo.currentData()),
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
                f"name={scalar_kwargs['name']!r}, mode={scalar_kwargs['mode']!r}, cell2point={scalar_kwargs['cell2point']!r}, cmap={scalar_kwargs['cmap']!r}"
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
        lines.extend(["", f"gui.add_field(field_plot, {self._current_title()!r})"])
        return "\n".join(lines)

    def _open_script_dialog(self) -> None:
        dialog = GeneratedScriptDialog(self._generate_script_text(), parent=self)
        dialog.exec()

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

            self._persist_settings()

            import pyemsi.gui as gui

            gui.add_field(plotter, self._current_title())
        except Exception as exc:
            if plotter is not None:
                plotter.close()
            QMessageBox.critical(self, "Field Plot Error", str(exc))
            return

        self.accept()
