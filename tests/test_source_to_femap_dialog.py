import os

from PySide6.QtWidgets import QApplication, QMessageBox

from pyemsi.gui.source_to_femap_dialog import SourceToFemapDialog
from pyemsi.settings import SettingsManager


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_source_to_femap_dialog_uses_workspace_defaults_for_atlas(tmp_path):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.load_workspace(workspace)

    dialog = SourceToFemapDialog("atlas", manager)
    try:
        assert dialog.input_dir() == os.path.abspath(os.path.normpath(str(workspace)))
        assert dialog._overwrite_checkbox.isChecked() is True
        assert dialog._mesh_field.value() == "post_geom"
        assert dialog._displacement_field.value() is None
        assert dialog._mesh_output_field.line_edit().text() == "post_geom"
        assert not dialog._mesh_output_field.isEnabled()
    finally:
        dialog.close()


def test_source_to_femap_dialog_discovers_exact_names_without_extension_fallback(tmp_path):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    results_dir = workspace / "results"
    results_dir.mkdir()
    (workspace / "post_geom").write_text("mesh", encoding="utf-8")
    (workspace / "displacement").write_text("disp", encoding="utf-8")
    (workspace / "current").write_text("current", encoding="utf-8")
    (workspace / "magnetic.atl").write_text("magnetic", encoding="utf-8")
    (results_dir / "electric").write_text("electric", encoding="utf-8")
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.load_workspace(workspace)

    dialog = SourceToFemapDialog("atlas", manager)
    try:
        assert dialog._mesh_field.value() == "post_geom"
        assert dialog._displacement_field.value() == "displacement"
        assert dialog._electric_field.value() == os.path.normpath(os.path.join("results", "electric"))
        assert dialog._current_field.value() == "current"
        assert dialog._magnetic_field.value() is None
    finally:
        dialog.close()


def test_source_to_femap_dialog_builds_config_with_custom_outputs(tmp_path, monkeypatch):
    _app()
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "post_geom.unv").write_text("mesh", encoding="utf-8")
    (input_dir / "current.unv").write_text("current", encoding="utf-8")
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    dialog = SourceToFemapDialog("unv", manager)
    try:
        dialog._input_dir_field.set_value(str(input_dir))
        dialog._mesh_field.set_value("post_geom.unv")
        dialog._apply_discovered_paths()
        dialog._overwrite_checkbox.setChecked(False)
        dialog._refresh_output_field_states()
        dialog._mesh_output_field.set_value(os.path.join("exports", "mesh.neu"))
        dialog._current_field.set_value("current.unv")
        dialog._current_output_field.set_value("custom-current.neu")
        monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes)

        dialog._accept_if_valid()

        config = dialog.config()
        assert config is not None
        assert config.source_format == "unv"
        assert config.overwrite is False
        assert config.mesh == "post_geom.unv"
        assert config.mesh_output == os.path.join("exports", "mesh.neu")
        assert config.current == "current.unv"
        assert config.current_output == "custom-current.neu"
    finally:
        dialog.close()


def test_source_to_femap_dialog_overwrite_confirmation_targets_source_paths(tmp_path, monkeypatch):
    _app()
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "post_geom").write_text("mesh", encoding="utf-8")
    (input_dir / "current").write_text("current", encoding="utf-8")
    global_settings_path = tmp_path / "config" / "settings.json"
    confirmation_calls = []

    def _capture_question(*args, **kwargs):
        confirmation_calls.append(args[2])
        return QMessageBox.StandardButton.Yes

    manager = SettingsManager(global_settings_path=global_settings_path)
    dialog = SourceToFemapDialog("unv", manager)
    try:
        dialog._input_dir_field.set_value(str(input_dir))
        dialog._apply_discovered_paths()
        dialog._mesh_field.set_value("post_geom")
        dialog._current_field.set_value("current")
        monkeypatch.setattr(QMessageBox, "question", _capture_question)

        dialog._accept_if_valid()

        config = dialog.config()
        assert config is not None
        assert config.overwrite is True
        assert config.mesh == "post_geom"
        assert config.current == "current"
        assert confirmation_calls == ["Existing FEMAP output files were found and will be overwritten. Continue?"]
    finally:
        dialog.close()
