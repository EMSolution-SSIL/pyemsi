"""Settings dialog for the EMSolution.exe run backend."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyemsi.settings import SettingsManager


@dataclass(frozen=True)
class EMSolutionRunSettingsDialogConfig:
    backend: str
    executable_path: str | None
    run_style: str

    def to_settings(self) -> dict[str, str | None]:
        return {
            "tools.emsolution_run.backend": self.backend,
            "tools.emsolution_run.executable_path": self.executable_path,
            "tools.emsolution_run.run_style": self.run_style,
        }


def check_executable(path: str) -> tuple[bool, str]:
    """Run ``<path> -v`` and report whether it launched. Informational only.

    ``-v`` is only documented from the 2024.11 EMSolution release onward, so
    a non-zero exit or missing output does not necessarily mean the path is
    wrong -- this check is a convenience, not a hard gate.
    """
    try:
        result = subprocess.run([path, "-v"], capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired as exc:
        return False, f"{path} -v timed out after {exc.timeout} seconds"
    except OSError as exc:
        return False, f"Could not launch {path}: {exc}"
    if result.returncode != 0:
        return False, f"{path} -v exited with code {result.returncode}"
    output = (result.stdout or result.stderr or "").strip()
    return True, output or "Executable launched successfully."


class EMSolutionRunSettingsDialog(QDialog):
    def __init__(self, settings_manager: SettingsManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = settings_manager
        self._config: EMSolutionRunSettingsDialogConfig | None = None

        self.setWindowTitle("EMSolution Run Settings")

        self._backend_combo = QComboBox(self)
        self._backend_combo.addItem("Pyemsol", "pyemsol")
        self._backend_combo.addItem("EMSolution.exe", "executable")

        self._path_edit = QLineEdit(self)
        browse_button = QPushButton("Browse...", self)
        browse_button.clicked.connect(self._browse)
        check_button = QPushButton("Check", self)
        check_button.clicked.connect(self._check)

        path_row = QHBoxLayout()
        path_row.setContentsMargins(0, 0, 0, 0)
        path_row.addWidget(self._path_edit, 1)
        path_row.addWidget(browse_button)
        path_row.addWidget(check_button)
        path_row_widget = QWidget(self)
        path_row_widget.setLayout(path_row)

        self._run_style_combo = QComboBox(self)
        self._run_style_combo.addItem("Background", "background")
        self._run_style_combo.addItem("Window", "window")

        self._load_defaults()

        form_layout = QFormLayout()
        form_layout.addRow("Backend:", self._backend_combo)
        form_layout.addRow("Executable Path:", path_row_widget)
        form_layout.addRow("Style:", self._run_style_combo)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self._button_box.accepted.connect(self._accept_if_valid)
        self._button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self._button_box)

    def config(self) -> EMSolutionRunSettingsDialogConfig | None:
        return self._config

    def _load_defaults(self) -> None:
        backend = self._settings.get_effective("tools.emsolution_run.backend") or "pyemsol"
        executable_path = self._settings.get_effective("tools.emsolution_run.executable_path")
        run_style = self._settings.get_effective("tools.emsolution_run.run_style") or "background"

        backend_index = self._backend_combo.findData(backend)
        if backend_index >= 0:
            self._backend_combo.setCurrentIndex(backend_index)
        self._path_edit.setText(executable_path or "")
        style_index = self._run_style_combo.findData(run_style)
        if style_index >= 0:
            self._run_style_combo.setCurrentIndex(style_index)

    def _browse(self) -> None:
        path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Select EMSolution.exe",
            self._path_edit.text().strip() or os.getcwd(),
            "Executable Files (*.exe);;All Files (*)",
        )
        if path:
            self._path_edit.setText(os.path.normpath(path))

    def _check(self) -> None:
        path = self._path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "Missing Executable Path", "Enter an executable path first.")
            return
        ok, message = check_executable(path)
        if ok:
            QMessageBox.information(self, "Executable Check", message)
        else:
            QMessageBox.warning(self, "Executable Check", message)

    def _accept_if_valid(self) -> None:
        backend = self._backend_combo.currentData()
        executable_path = self._path_edit.text().strip() or None
        run_style = self._run_style_combo.currentData()

        if backend == "executable" and not executable_path:
            QMessageBox.warning(self, "Missing Executable Path", "Enter the EMSolution.exe path first.")
            return

        self._config = EMSolutionRunSettingsDialogConfig(
            backend=backend,
            executable_path=executable_path,
            run_style=run_style,
        )
        self.accept()
