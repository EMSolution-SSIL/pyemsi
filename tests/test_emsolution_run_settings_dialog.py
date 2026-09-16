import os

from PySide6.QtWidgets import QApplication, QMessageBox

from pyemsi.gui import emsolution_run_settings_dialog as dialog_module
from pyemsi.gui.emsolution_run_settings_dialog import EMSolutionRunSettingsDialog
from pyemsi.settings import SettingsManager


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dialog_loads_defaults_from_settings(tmp_path):
    _app()
    manager = SettingsManager(global_settings_path=tmp_path / "config" / "settings.json")
    manager.set_global("tools.emsolution_run.backend", "executable")
    manager.set_global("tools.emsolution_run.executable_path", str(tmp_path / "EMSolution.exe"))
    manager.set_global("tools.emsolution_run.run_style", "window")

    dialog = EMSolutionRunSettingsDialog(manager)
    try:
        assert dialog._backend_combo.currentData() == "executable"
        assert dialog._path_edit.text() == os.path.abspath(os.path.normpath(str(tmp_path / "EMSolution.exe")))
        assert dialog._run_style_combo.currentData() == "window"
    finally:
        dialog.close()


def test_accept_builds_config_with_edited_values(tmp_path):
    _app()
    manager = SettingsManager(global_settings_path=tmp_path / "config" / "settings.json")
    dialog = EMSolutionRunSettingsDialog(manager)
    try:
        dialog._backend_combo.setCurrentIndex(dialog._backend_combo.findData("executable"))
        dialog._path_edit.setText(str(tmp_path / "EMSolution.exe"))
        dialog._run_style_combo.setCurrentIndex(dialog._run_style_combo.findData("window"))

        dialog._accept_if_valid()

        config = dialog.config()
        assert config is not None
        assert config.backend == "executable"
        assert config.executable_path == str(tmp_path / "EMSolution.exe")
        assert config.run_style == "window"
        assert config.to_settings() == {
            "tools.emsolution_run.backend": "executable",
            "tools.emsolution_run.executable_path": str(tmp_path / "EMSolution.exe"),
            "tools.emsolution_run.run_style": "window",
        }
    finally:
        dialog.close()


def test_accept_rejects_executable_backend_without_a_path(tmp_path, monkeypatch):
    _app()
    warnings = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(args[1:]))

    manager = SettingsManager(global_settings_path=tmp_path / "config" / "settings.json")
    dialog = EMSolutionRunSettingsDialog(manager)
    try:
        dialog._backend_combo.setCurrentIndex(dialog._backend_combo.findData("executable"))
        dialog._path_edit.setText("")

        dialog._accept_if_valid()

        assert dialog.config() is None
        assert warnings
        assert warnings[0][0] == "Missing Executable Path"
    finally:
        dialog.close()


def test_check_button_reports_success(tmp_path, monkeypatch):
    _app()
    info_calls = []
    monkeypatch.setattr(dialog_module, "check_executable", lambda path: (True, "ok"))
    monkeypatch.setattr(QMessageBox, "information", lambda *args: info_calls.append(args[1:]))

    manager = SettingsManager(global_settings_path=tmp_path / "config" / "settings.json")
    dialog = EMSolutionRunSettingsDialog(manager)
    try:
        dialog._path_edit.setText(str(tmp_path / "EMSolution.exe"))

        dialog._check()

        assert info_calls == [("Executable Check", "ok")]
    finally:
        dialog.close()


def test_check_executable_reports_failure_for_missing_file(tmp_path):
    ok, message = dialog_module.check_executable(str(tmp_path / "does-not-exist.exe"))

    assert ok is False
    assert message
