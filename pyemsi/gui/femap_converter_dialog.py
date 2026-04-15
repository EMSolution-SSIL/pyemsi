from __future__ import annotations

import os
from dataclasses import dataclass

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import pyemsi.resources.resources  # noqa: F401
from pyemsi.settings import SettingsManager


@dataclass(frozen=True)
class FemapConverterDialogConfig:
    input_dir: str
    output_dir: str
    output_name: str
    input_control_file: str | None
    force_2d: bool
    ascii_mode: bool
    mesh: str
    magnetic: str | None
    current: str | None
    electric: str | None
    force: str | None
    force_J_B: str | None
    heat: str | None
    displacement: str | None

    def to_payload(self) -> dict[str, str | bool | None]:
        return {
            "ascii_mode": self.ascii_mode,
            "current": self.current,
            "displacement": self.displacement,
            "electric": self.electric,
            "force": self.force,
            "force_2d": self.force_2d,
            "force_J_B": self.force_J_B,
            "heat": self.heat,
            "input_control_file": self.input_control_file,
            "input_dir": self.input_dir,
            "magnetic": self.magnetic,
            "mesh": self.mesh,
            "output_dir": self.output_dir,
            "output_name": self.output_name,
        }

    def to_settings(self) -> dict[str, str | bool | None]:
        return {
            "tools.femap_converter.ascii_mode": self.ascii_mode,
            "tools.femap_converter.current": self.current,
            "tools.femap_converter.displacement": self.displacement,
            "tools.femap_converter.electric": self.electric,
            "tools.femap_converter.force": self.force,
            "tools.femap_converter.force_2d": self.force_2d,
            "tools.femap_converter.force_J_B": self.force_J_B,
            "tools.femap_converter.heat": self.heat,
            "tools.femap_converter.input_control_file": self.input_control_file,
            "tools.femap_converter.input_dir": self.input_dir,
            "tools.femap_converter.magnetic": self.magnetic,
            "tools.femap_converter.mesh": self.mesh,
            "tools.femap_converter.output_dir": self.output_dir,
            "tools.femap_converter.output_name": self.output_name,
        }


class _PathSelector(QWidget):
    def __init__(
        self,
        text: str = "",
        *,
        select_directory: bool,
        optional: bool = False,
        browse_dir_getter=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._select_directory = select_directory
        self._browse_dir_getter = browse_dir_getter
        self._optional = optional

        self._enabled_checkbox = QCheckBox(self) if optional else None
        if self._enabled_checkbox is not None:
            self._enabled_checkbox.setChecked(bool(text))

        self._line_edit = QLineEdit(text, self)
        self._browse_button = QPushButton("Browse...", self)
        self._browse_button.clicked.connect(self._browse)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if self._enabled_checkbox is not None:
            layout.addWidget(self._enabled_checkbox)
            self._enabled_checkbox.toggled.connect(self._apply_enabled_state)
        layout.addWidget(self._line_edit, 1)
        layout.addWidget(self._browse_button)

        self._apply_enabled_state(self.is_active())

    def is_active(self) -> bool:
        if self._enabled_checkbox is None:
            return True
        return self._enabled_checkbox.isChecked()

    def value(self) -> str | None:
        if not self.is_active():
            return None
        return self._line_edit.text().strip() or None

    def set_value(self, value: str | None) -> None:
        normalized = value or ""
        self._line_edit.setText(normalized)
        if self._enabled_checkbox is not None:
            self._enabled_checkbox.setChecked(bool(value))
        self._apply_enabled_state(self.is_active())

    def line_edit(self) -> QLineEdit:
        return self._line_edit

    def _apply_enabled_state(self, checked: bool) -> None:
        self._line_edit.setEnabled(checked)
        self._browse_button.setEnabled(checked)

    def _browse(self) -> None:
        initial_dir = self._initial_directory()
        if self._select_directory:
            path = QFileDialog.getExistingDirectory(self, "Select Folder", initial_dir, QFileDialog.Option.ShowDirsOnly)
        else:
            path, _selected_filter = QFileDialog.getOpenFileName(self, "Select File", initial_dir, "All Files (*)")
        if not path:
            return
        self._line_edit.setText(os.path.normpath(path))
        if self._enabled_checkbox is not None and not self._enabled_checkbox.isChecked():
            self._enabled_checkbox.setChecked(True)

    def _initial_directory(self) -> str:
        current_value = self._line_edit.text().strip()
        if current_value:
            candidate = current_value
            if not os.path.isabs(candidate) and callable(self._browse_dir_getter):
                base_dir = self._browse_dir_getter()
                if base_dir:
                    candidate = os.path.join(base_dir, candidate)
            if self._select_directory and os.path.isdir(candidate):
                return os.path.normpath(candidate)
            if not self._select_directory:
                if os.path.isfile(candidate):
                    return os.path.normpath(os.path.dirname(candidate))
                if os.path.isdir(candidate):
                    return os.path.normpath(candidate)

        if callable(self._browse_dir_getter):
            base_dir = self._browse_dir_getter()
            if base_dir and os.path.isdir(base_dir):
                return os.path.normpath(base_dir)

        return os.getcwd()


class FemapConverterDialog(QDialog):
    def __init__(self, settings_manager: SettingsManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = settings_manager
        self._config: FemapConverterDialogConfig | None = None

        self.setWindowTitle("Femap Converter")
        self.setWindowIcon(QIcon(":/icons/VTK.svg"))

        defaults = self._load_defaults()

        self._input_dir_field = _PathSelector(defaults["input_dir"], select_directory=True, parent=self)
        self._output_dir_field = _PathSelector(defaults["output_dir"], select_directory=True, parent=self)
        self._output_name_edit = QLineEdit(defaults["output_name"], self)
        self._input_control_file_field = self._build_optional_file_field(defaults["input_control_file"])
        self._mesh_field = _PathSelector(
            defaults["mesh"],
            select_directory=False,
            browse_dir_getter=self.input_dir,
            parent=self,
        )

        self._force_2d_checkbox = QCheckBox(self)
        self._force_2d_checkbox.setChecked(defaults["force_2d"])
        self._ascii_mode_checkbox = QCheckBox(self)
        self._ascii_mode_checkbox.setChecked(defaults["ascii_mode"])

        self._displacement_field = self._build_optional_file_field(defaults["displacement"])
        self._magnetic_field = self._build_optional_file_field(defaults["magnetic"])
        self._current_field = self._build_optional_file_field(defaults["current"])
        self._electric_field = self._build_optional_file_field(defaults["electric"])
        self._force_field = self._build_optional_file_field(defaults["force"])
        self._force_j_b_field = self._build_optional_file_field(defaults["force_J_B"])
        self._heat_field = self._build_optional_file_field(defaults["heat"])

        self._apply_discovered_optional_paths()

        helper_label = QLabel("Relative file and output paths are resolved from the selected input directory.", self)
        helper_label.setWordWrap(True)
        helper_label.setStyleSheet("color: palette(mid);")

        form_layout = QFormLayout()
        form_layout.addRow("Input Directory:", self._input_dir_field)
        form_layout.addRow("Output Directory:", self._output_dir_field)
        form_layout.addRow("Output Name:", self._output_name_edit)
        form_layout.addRow("Input Control:", self._input_control_file_field)
        form_layout.addRow("Mesh File:", self._mesh_field)
        form_layout.addRow("Force 2D:", self._force_2d_checkbox)
        form_layout.addRow("ASCII Mode:", self._ascii_mode_checkbox)
        form_layout.addRow("Displacement:", self._displacement_field)
        form_layout.addRow("Magnetic:", self._magnetic_field)
        form_layout.addRow("Current:", self._current_field)
        form_layout.addRow("Electric:", self._electric_field)
        form_layout.addRow("Force:", self._force_field)
        form_layout.addRow("Force J x B:", self._force_j_b_field)
        form_layout.addRow("Heat:", self._heat_field)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        run_button = self._button_box.button(QDialogButtonBox.StandardButton.Ok)
        if run_button is not None:
            run_button.setText("Run")
        self._button_box.accepted.connect(self._accept_if_valid)
        self._button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(helper_label)
        layout.addWidget(self._button_box)

        self._input_dir_field.line_edit().editingFinished.connect(self._apply_discovered_optional_paths)

    def input_dir(self) -> str | None:
        value = self._input_dir_field.value()
        if value is None:
            return None
        return os.path.abspath(os.path.normpath(value))

    def config(self) -> FemapConverterDialogConfig | None:
        return self._config

    def _build_optional_file_field(self, value: str | None) -> _PathSelector:
        return _PathSelector(
            value or "",
            select_directory=False,
            optional=True,
            browse_dir_getter=self.input_dir,
            parent=self,
        )

    def _apply_discovered_optional_paths(self) -> None:
        input_dir = self.input_dir()
        if not input_dir or not os.path.isdir(input_dir):
            return

        optional_fields = (
            self._input_control_file_field,
            self._displacement_field,
            self._magnetic_field,
            self._current_field,
            self._electric_field,
            self._force_field,
            self._force_j_b_field,
            self._heat_field,
        )
        for field in optional_fields:
            configured_value = field.line_edit().text().strip() or None
            if configured_value is None:
                field.set_value(None)
                continue
            discovered_value = self._discover_optional_file(input_dir, configured_value)
            field.set_value(discovered_value)

    def _load_defaults(self) -> dict[str, str | bool | None]:
        workspace_path = self._settings.workspace_path
        input_dir = self._settings.get_effective("tools.femap_converter.input_dir")
        if input_dir is None and workspace_path is not None:
            input_dir = os.fspath(workspace_path)
        return {
            "ascii_mode": bool(self._settings.get_effective("tools.femap_converter.ascii_mode") or False),
            "current": self._settings.get_effective("tools.femap_converter.current") or "current",
            "displacement": self._settings.get_effective("tools.femap_converter.displacement") or "disp",
            "electric": self._settings.get_effective("tools.femap_converter.electric") or "electric",
            "force": self._settings.get_effective("tools.femap_converter.force") or "force",
            "force_2d": bool(self._settings.get_effective("tools.femap_converter.force_2d") or False),
            "force_J_B": self._settings.get_effective("tools.femap_converter.force_J_B") or "force_J_B",
            "heat": self._settings.get_effective("tools.femap_converter.heat") or "heat",
            "input_control_file": self._settings.get_effective("tools.femap_converter.input_control_file")
            or "input_control.json",
            "input_dir": input_dir or "",
            "magnetic": self._settings.get_effective("tools.femap_converter.magnetic") or "magnetic",
            "mesh": self._settings.get_effective("tools.femap_converter.mesh") or "post_geom",
            "output_dir": self._settings.get_effective("tools.femap_converter.output_dir") or ".pyemsi",
            "output_name": self._settings.get_effective("tools.femap_converter.output_name") or "output",
        }

    def _accept_if_valid(self) -> None:
        config = self._build_config()
        if config is None:
            return
        self._config = config
        self.accept()

    def _build_config(self) -> FemapConverterDialogConfig | None:
        input_dir = self.input_dir()
        if not input_dir:
            QMessageBox.warning(self, "Missing Input Directory", "Input directory is required.")
            return None
        if not os.path.isdir(input_dir):
            QMessageBox.warning(self, "Invalid Input Directory", "Input directory must point to an existing folder.")
            return None

        output_name = self._output_name_edit.text().strip()
        if not output_name:
            QMessageBox.warning(self, "Missing Output Name", "Output name is required.")
            return None

        mesh = self._mesh_field.value()
        if mesh is None:
            QMessageBox.warning(self, "Missing Mesh File", "Mesh file is required.")
            return None
        if not os.path.isfile(self._resolve_path(input_dir, mesh)):
            QMessageBox.warning(
                self, "Missing Mesh File", "Mesh file could not be found from the selected input directory."
            )
            return None

        input_control_file = self._validated_optional_path("Input Control", self._input_control_file_field, input_dir)
        if input_control_file is False:
            return None
        displacement = self._validated_optional_path("Displacement", self._displacement_field, input_dir)
        if displacement is False:
            return None
        magnetic = self._validated_optional_path("Magnetic", self._magnetic_field, input_dir)
        if magnetic is False:
            return None
        current = self._validated_optional_path("Current", self._current_field, input_dir)
        if current is False:
            return None
        electric = self._validated_optional_path("Electric", self._electric_field, input_dir)
        if electric is False:
            return None
        force = self._validated_optional_path("Force", self._force_field, input_dir)
        if force is False:
            return None
        force_j_b = self._validated_optional_path("Force J x B", self._force_j_b_field, input_dir)
        if force_j_b is False:
            return None
        heat = self._validated_optional_path("Heat", self._heat_field, input_dir)
        if heat is False:
            return None

        output_dir = self._output_dir_field.value() or ".pyemsi"
        if not self._confirm_overwrite(input_dir, output_dir, output_name):
            return None

        return FemapConverterDialogConfig(
            input_dir=input_dir,
            output_dir=output_dir,
            output_name=output_name,
            input_control_file=input_control_file,
            force_2d=self._force_2d_checkbox.isChecked(),
            ascii_mode=self._ascii_mode_checkbox.isChecked(),
            mesh=mesh,
            magnetic=magnetic,
            current=current,
            electric=electric,
            force=force,
            force_J_B=force_j_b,
            heat=heat,
            displacement=displacement,
        )

    def _validated_optional_path(self, label: str, field: _PathSelector, input_dir: str) -> str | None | bool:
        value = field.value()
        if value is None:
            return None
        if not os.path.isfile(self._resolve_path(input_dir, value)):
            QMessageBox.warning(
                self, f"Missing {label} File", f"{label} file could not be found from the selected input directory."
            )
            return False
        return value

    def _confirm_overwrite(self, input_dir: str, output_dir: str, output_name: str) -> bool:
        resolved_output_dir = self._resolve_path(input_dir, output_dir)
        pvd_path = os.path.join(resolved_output_dir, f"{output_name}.pvd")
        output_folder = os.path.join(resolved_output_dir, output_name)
        if not os.path.exists(pvd_path) and not os.path.exists(output_folder):
            return True

        answer = QMessageBox.question(
            self,
            "Overwrite Existing Output",
            "Existing converted output was found and will be deleted before the new run starts. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return answer == QMessageBox.StandardButton.Yes

    @staticmethod
    def _discover_optional_file(input_dir: str, configured_value: str) -> str | None:
        direct_match = FemapConverterDialog._resolve_path(input_dir, configured_value)
        if os.path.isfile(direct_match):
            if os.path.isabs(configured_value):
                return direct_match
            return configured_value

        target_name = os.path.basename(configured_value)
        if not target_name:
            return None

        matches: list[str] = []
        target_name_norm = os.path.normcase(target_name)
        for root, _dirs, files in os.walk(input_dir):
            for file_name in files:
                if os.path.normcase(file_name) != target_name_norm:
                    continue
                full_path = os.path.join(root, file_name)
                matches.append(os.path.relpath(full_path, input_dir))

        if not matches:
            return None

        matches.sort(key=lambda candidate: (candidate.count(os.sep), len(candidate), candidate.lower()))
        return os.path.normpath(matches[0])

    @staticmethod
    def _resolve_path(input_dir: str, value: str) -> str:
        candidate = value
        if not os.path.isabs(candidate):
            candidate = os.path.join(input_dir, candidate)
        return os.path.abspath(os.path.normpath(candidate))
