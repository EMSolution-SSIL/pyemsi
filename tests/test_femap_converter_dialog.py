import os

from PySide6.QtWidgets import QApplication, QMessageBox

from pyemsi.gui.femap_converter_dialog import FemapConverterDialog
from pyemsi.settings import SettingsManager


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_femap_converter_dialog_uses_workspace_and_default_values(tmp_path):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.load_workspace(workspace)

    dialog = FemapConverterDialog(manager)
    try:
        assert dialog.input_dir() == os.path.abspath(os.path.normpath(str(workspace)))
        assert dialog._output_name_edit.text() == "output"
        assert dialog._output_dir_field.value() == ".pyemsi"
        assert dialog._mesh_field.value() == "post_geom"
        assert dialog._displacement_field.value() is None
        assert dialog._electric_field.value() is None
        assert dialog._magnetic_field.value() is None
        assert not dialog._displacement_field.is_active()
        assert not dialog._electric_field.is_active()
        assert not dialog._magnetic_field.is_active()
    finally:
        dialog.close()


def test_femap_converter_dialog_discovers_optional_files_from_input_directory(tmp_path):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    results_dir = workspace / "results"
    results_dir.mkdir()
    (workspace / "disp").write_text("disp", encoding="utf-8")
    (results_dir / "electric").write_text("electric", encoding="utf-8")
    (results_dir / "magnetic").write_text("mag", encoding="utf-8")
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.load_workspace(workspace)

    dialog = FemapConverterDialog(manager)
    try:
        assert dialog._displacement_field.value() == "disp"
        assert dialog._displacement_field.is_active()
        assert dialog._electric_field.value() == os.path.normpath(os.path.join("results", "electric"))
        assert dialog._electric_field.is_active()
        assert dialog._magnetic_field.value() == os.path.normpath(os.path.join("results", "magnetic"))
        assert dialog._magnetic_field.is_active()
        assert dialog._current_field.value() is None
        assert not dialog._current_field.is_active()
    finally:
        dialog.close()


def test_femap_converter_dialog_builds_config_with_optional_channels_disabled(tmp_path, monkeypatch):
    _app()
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "post_geom").write_text("mesh", encoding="utf-8")
    (input_dir / "disp").write_text("disp", encoding="utf-8")
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    dialog = FemapConverterDialog(manager)
    try:
        dialog._input_dir_field.set_value(str(input_dir))
        dialog._displacement_field.set_value("disp")
        dialog._magnetic_field.set_value(None)
        dialog._current_field.set_value(None)
        dialog._electric_field.set_value(None)
        dialog._force_field.set_value(None)
        dialog._force_j_b_field.set_value(None)
        dialog._heat_field.set_value(None)
        monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes)

        dialog._accept_if_valid()

        config = dialog.config()
        assert config is not None
        assert config.input_dir == os.path.abspath(os.path.normpath(str(input_dir)))
        assert config.output_dir == ".pyemsi"
        assert config.mesh == "post_geom"
        assert config.displacement == "disp"
        assert config.magnetic is None
        assert config.current is None
        assert config.electric is None
        assert config.force is None
        assert config.force_J_B is None
        assert config.heat is None
    finally:
        dialog.close()


def test_femap_converter_dialog_allows_current_and_electric_together(tmp_path):
    _app()
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "post_geom").write_text("mesh", encoding="utf-8")
    (input_dir / "current").write_text("current", encoding="utf-8")
    (input_dir / "electric").write_text("electric", encoding="utf-8")
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    dialog = FemapConverterDialog(manager)
    try:
        dialog._input_dir_field.set_value(str(input_dir))
        dialog._magnetic_field.set_value(None)
        dialog._displacement_field.set_value(None)
        dialog._current_field.set_value("current")
        dialog._electric_field.set_value("electric")
        dialog._force_field.set_value(None)
        dialog._force_j_b_field.set_value(None)
        dialog._heat_field.set_value(None)

        config = dialog._build_config()

        assert config is not None
        assert config.current == "current"
        assert config.electric == "electric"
    finally:
        dialog.close()
