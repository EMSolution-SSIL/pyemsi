from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

import pyemsi.resources.resources  # noqa: F401
from pyemsi.gui.femap_converter_dialog import _PathSelector
from pyemsi.settings import SettingsManager

SourceFormat = Literal["atlas", "unv"]

_FIELD_SPECS: tuple[tuple[str, str, str, bool], ...] = (
    ("mesh", "Mesh File", "post_geom", True),
    ("displacement", "Displacement", "displacement", False),
    ("magnetic", "Magnetic", "magnetic", False),
    ("current", "Current", "current", False),
    ("electric", "Electric", "electric", False),
    ("force", "Force", "force", False),
    ("force_J_B", "Force J x B", "force_J_B", False),
    ("heat", "Heat", "heat", False),
)


def _settings_prefix(source_format: SourceFormat) -> str:
    return f"tools.{source_format}_to_femap"


def _resolve_path(input_dir: str, value: str) -> str:
    candidate = value
    if not os.path.isabs(candidate):
        candidate = os.path.join(input_dir, candidate)
    return os.path.abspath(os.path.normpath(candidate))


def _suggest_custom_output_value(source_path: str) -> str:
    normalized = os.path.normpath(source_path)
    parent = os.path.dirname(normalized)
    stem, _suffix = os.path.splitext(os.path.basename(normalized))
    return os.path.join(parent, stem) if parent else stem


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


@dataclass(frozen=True)
class SourceToFemapDialogConfig:
    source_format: SourceFormat
    input_dir: str
    overwrite: bool
    mesh: str
    mesh_output: str
    displacement: str | None
    displacement_output: str | None
    magnetic: str | None
    magnetic_output: str | None
    current: str | None
    current_output: str | None
    electric: str | None
    electric_output: str | None
    force: str | None
    force_output: str | None
    force_J_B: str | None
    force_J_B_output: str | None
    heat: str | None
    heat_output: str | None

    def to_payload(self) -> dict[str, str | bool | None]:
        return {
            "source_format": self.source_format,
            "input_dir": self.input_dir,
            "overwrite": self.overwrite,
            "mesh": self.mesh,
            "mesh_output": self.mesh_output,
            "displacement": self.displacement,
            "displacement_output": self.displacement_output,
            "magnetic": self.magnetic,
            "magnetic_output": self.magnetic_output,
            "current": self.current,
            "current_output": self.current_output,
            "electric": self.electric,
            "electric_output": self.electric_output,
            "force": self.force,
            "force_output": self.force_output,
            "force_J_B": self.force_J_B,
            "force_J_B_output": self.force_J_B_output,
            "heat": self.heat,
            "heat_output": self.heat_output,
        }

    def to_settings(self) -> dict[str, str | bool | None]:
        prefix = _settings_prefix(self.source_format)
        return {
            f"{prefix}.input_dir": self.input_dir,
            f"{prefix}.overwrite": self.overwrite,
            f"{prefix}.mesh": self.mesh,
            f"{prefix}.mesh_output": self.mesh_output,
            f"{prefix}.displacement": self.displacement,
            f"{prefix}.displacement_output": self.displacement_output,
            f"{prefix}.magnetic": self.magnetic,
            f"{prefix}.magnetic_output": self.magnetic_output,
            f"{prefix}.current": self.current,
            f"{prefix}.current_output": self.current_output,
            f"{prefix}.electric": self.electric,
            f"{prefix}.electric_output": self.electric_output,
            f"{prefix}.force": self.force,
            f"{prefix}.force_output": self.force_output,
            f"{prefix}.force_J_B": self.force_J_B,
            f"{prefix}.force_J_B_output": self.force_J_B_output,
            f"{prefix}.heat": self.heat,
            f"{prefix}.heat_output": self.heat_output,
        }


class SourceToFemapDialog(QDialog):
    def __init__(
        self,
        source_format: SourceFormat,
        settings_manager: SettingsManager,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._source_format = source_format
        self._settings = settings_manager
        self._config: SourceToFemapDialogConfig | None = None
        self._fields: dict[str, _PathSelector] = {}
        self._output_fields: dict[str, _PathSelector] = {}

        self.setWindowTitle(f"{self._format_label()} to FEMAP")
        self.setWindowIcon(QIcon(":/icons/VTK.svg"))

        defaults = self._load_defaults()

        self._input_dir_field = _PathSelector(defaults["input_dir"] or "", select_directory=True, parent=self)
        self._overwrite_checkbox = QCheckBox(self)
        self._overwrite_checkbox.setChecked(bool(defaults["overwrite"]))

        for key, _label, _default_name, required in _FIELD_SPECS:
            source_field = _PathSelector(
                defaults[key] or "",
                select_directory=False,
                optional=not required,
                browse_dir_getter=self.input_dir,
                parent=self,
            )
            output_field = _PathSelector(
                defaults[f"{key}_output"] or "",
                select_directory=False,
                browse_dir_getter=self.input_dir,
                parent=self,
            )
            self._fields[key] = source_field
            self._output_fields[key] = output_field
            setattr(self, f"_{key}_field", source_field)
            setattr(self, f"_{key}_output_field", output_field)

        self._apply_discovered_paths()
        self._refresh_output_defaults(force=False)

        helper_label = QLabel(
            f"File paths are resolved from the selected input directory. {self._format_label()} files can be entered by exact filename or full path.",
            self,
        )
        helper_label.setWordWrap(True)
        helper_label.setStyleSheet("color: palette(mid);")

        overwrite_label = QLabel(
            "When checked, converted FEMAP data is written back to the selected source paths.",
            self,
        )
        overwrite_label.setWordWrap(True)
        overwrite_label.setStyleSheet("color: palette(mid);")

        form_layout = QFormLayout()
        form_layout.addRow("Input Directory:", self._input_dir_field)
        form_layout.addRow("Overwrite:", self._overwrite_checkbox)
        for key, label, _default_name, _required in _FIELD_SPECS:
            form_layout.addRow(f"{label}:", self._fields[key])
            form_layout.addRow(f"{label} Output:", self._output_fields[key])

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
        layout.addWidget(overwrite_label)
        layout.addWidget(self._button_box)

        self._input_dir_field.line_edit().editingFinished.connect(self._handle_input_dir_changed)
        self._overwrite_checkbox.toggled.connect(self._handle_overwrite_toggled)
        for key in self._fields:
            field = self._fields[key]
            field.line_edit().editingFinished.connect(self._refresh_output_defaults)
            checkbox = field.enabled_checkbox()
            if checkbox is not None:
                checkbox.toggled.connect(self._refresh_output_field_states)

        self._refresh_output_field_states()

    def input_dir(self) -> str | None:
        value = self._input_dir_field.value()
        if value is None:
            return None
        return os.path.abspath(os.path.normpath(value))

    def config(self) -> SourceToFemapDialogConfig | None:
        return self._config

    def _format_label(self) -> str:
        return "Atlas" if self._source_format == "atlas" else "I-DEAS"

    def _handle_input_dir_changed(self) -> None:
        self._apply_discovered_paths()
        self._refresh_output_defaults(force=False)
        self._refresh_output_field_states()

    def _handle_overwrite_toggled(self) -> None:
        self._refresh_output_defaults(force=False)
        self._refresh_output_field_states()

    def _refresh_output_field_states(self) -> None:
        use_custom_outputs = not self._overwrite_checkbox.isChecked()
        for key, output_field in self._output_fields.items():
            enabled = use_custom_outputs and (key == "mesh" or self._fields[key].is_active())
            output_field.setEnabled(enabled)

    def _refresh_output_defaults(self, force: bool = False) -> None:
        for key, source_field in self._fields.items():
            source_value = source_field.value() or source_field.line_edit().text().strip() or None
            if source_value is None:
                continue
            output_field = self._output_fields[key]
            current_value = output_field.line_edit().text().strip()
            if current_value and not force:
                continue
            output_field.set_value(_suggest_custom_output_value(source_value))

    def _load_defaults(self) -> dict[str, str | bool | None]:
        prefix = _settings_prefix(self._source_format)
        workspace_path = self._settings.workspace_path
        input_dir = self._settings.get_effective(f"{prefix}.input_dir")
        if input_dir is None and workspace_path is not None:
            input_dir = os.fspath(workspace_path)

        defaults: dict[str, str | bool | None] = {
            "input_dir": input_dir or "",
            "overwrite": bool(
                self._settings.get_effective(f"{prefix}.overwrite")
                if self._settings.get_effective(f"{prefix}.overwrite") is not None
                else True
            ),
        }
        for key, _label, default_name, _required in _FIELD_SPECS:
            defaults[key] = self._settings.get_effective(f"{prefix}.{key}") or default_name
            defaults[f"{key}_output"] = self._settings.get_effective(f"{prefix}.{key}_output")
        return defaults

    def _accept_if_valid(self) -> None:
        config = self._build_config()
        if config is None:
            return
        self._config = config
        self.accept()

    def _build_config(self) -> SourceToFemapDialogConfig | None:
        input_dir = self.input_dir()
        if not input_dir:
            QMessageBox.warning(self, "Missing Input Directory", "Input directory is required.")
            return None
        if not os.path.isdir(input_dir):
            QMessageBox.warning(self, "Invalid Input Directory", "Input directory must point to an existing folder.")
            return None

        entries: dict[str, str | None] = {}
        output_entries: dict[str, str | None] = {}
        for key, label, _default_name, required in _FIELD_SPECS:
            resolved_source = self._validated_source_path(label, self._fields[key], input_dir, required=required)
            if resolved_source is False:
                return None
            entries[key] = resolved_source
            resolved_output = self._validated_output_path(
                label,
                self._output_fields[key],
                source_path=resolved_source,
                required=required,
            )
            if resolved_output is False:
                return None
            output_entries[key] = resolved_output

        overwrite_enabled = self._overwrite_checkbox.isChecked()
        resolved_outputs = [
            _resolve_path(input_dir, entries[key] if overwrite_enabled else output_path)
            for key, output_path in output_entries.items()
            if output_path is not None and entries[key] is not None
        ]
        if not self._confirm_overwrite(resolved_outputs):
            return None

        mesh_value = entries["mesh"]
        mesh_output_value = output_entries["mesh"]
        assert mesh_value is not None
        assert mesh_output_value is not None

        return SourceToFemapDialogConfig(
            source_format=self._source_format,
            input_dir=input_dir,
            overwrite=overwrite_enabled,
            mesh=mesh_value,
            mesh_output=mesh_output_value,
            displacement=entries["displacement"],
            displacement_output=output_entries["displacement"],
            magnetic=entries["magnetic"],
            magnetic_output=output_entries["magnetic"],
            current=entries["current"],
            current_output=output_entries["current"],
            electric=entries["electric"],
            electric_output=output_entries["electric"],
            force=entries["force"],
            force_output=output_entries["force"],
            force_J_B=entries["force_J_B"],
            force_J_B_output=output_entries["force_J_B"],
            heat=entries["heat"],
            heat_output=output_entries["heat"],
        )

    def _validated_source_path(
        self,
        label: str,
        field: _PathSelector,
        input_dir: str,
        *,
        required: bool,
    ) -> str | None | bool:
        value = field.value()
        if value is None:
            if required:
                QMessageBox.warning(self, f"Missing {label}", f"{label} is required.")
                return False
            return None

        discovered_value = self._discover_source_file(input_dir, value)
        if discovered_value is None:
            QMessageBox.warning(
                self,
                f"Missing {label}",
                f"{label} could not be found from the selected input directory.",
            )
            return False

        field.set_value(discovered_value)
        return discovered_value

    def _validated_output_path(
        self,
        label: str,
        field: _PathSelector,
        *,
        source_path: str | None,
        required: bool,
    ) -> str | None | bool:
        if source_path is None:
            return None

        value = _normalize_optional_text(field.line_edit().text())
        if value is None:
            value = _suggest_custom_output_value(source_path)
        field.set_value(value)
        if _normalize_optional_text(value) is None:
            QMessageBox.warning(self, f"Missing {label} Output", f"{label} output path is required.")
            return False
        return value

    def _confirm_overwrite(self, resolved_output_paths: list[str]) -> bool:
        existing_outputs = [path for path in resolved_output_paths if os.path.exists(path)]
        if not existing_outputs:
            return True

        answer = QMessageBox.question(
            self,
            "Overwrite Existing Output",
            "Existing FEMAP output files were found and will be overwritten. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return answer == QMessageBox.StandardButton.Yes

    def _apply_discovered_paths(self) -> None:
        input_dir = self.input_dir()
        if not input_dir or not os.path.isdir(input_dir):
            return

        for key, field in self._fields.items():
            configured_value = field.line_edit().text().strip() or None
            if configured_value is None:
                if key != "mesh":
                    field.set_value(None)
                continue
            discovered_value = self._discover_source_file(input_dir, configured_value)
            if discovered_value is None and key != "mesh":
                field.set_value(None)
                continue
            if discovered_value is not None:
                field.set_value(discovered_value)

    def _discover_source_file(self, input_dir: str, configured_value: str) -> str | None:
        direct_match = _resolve_path(input_dir, configured_value)
        if os.path.isfile(direct_match):
            if os.path.isabs(configured_value):
                return direct_match
            return os.path.normpath(configured_value)

        target_name = os.path.basename(configured_value)
        if not target_name:
            return None

        candidate_names = {os.path.normcase(target_name)}

        matches: list[str] = []
        for root, _dirs, files in os.walk(input_dir):
            for file_name in files:
                if os.path.normcase(file_name) not in candidate_names:
                    continue
                full_path = os.path.join(root, file_name)
                matches.append(os.path.relpath(full_path, input_dir))

        if not matches:
            return None

        matches.sort(key=lambda candidate: (candidate.count(os.sep), len(candidate), candidate.lower()))
        return os.path.normpath(matches[0])
