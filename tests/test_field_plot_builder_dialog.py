import os

from PySide6.QtWidgets import QApplication, QDialog

import pyemsi.gui as gui
from pyemsi.gui import field_plot_builder_dialog as dialog_module
from pyemsi.gui.field_plot_builder_dialog import FieldPlotBuilderDialog
from pyemsi.settings import SettingsManager


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _make_manager(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    settings_path = tmp_path / "config" / "settings.json"
    manager = SettingsManager(global_settings_path=settings_path)
    manager.load_workspace(workspace)
    return manager, workspace


def _cached_entry(relative_path: str, *, updated_at_utc: str = "2026-06-02T00:00:00Z") -> dict[str, object]:
    return {
        "relative_path": os.path.normpath(relative_path),
        "updated_at_utc": updated_at_utc,
        "mesh_length": 20.0,
        "scalar_names": ["Point Scalar"],
        "vector_names": ["Point Vector"],
        "ranges": {
            "Point Scalar": {"min": -2.0, "max": 4.0},
            "Point Vector": {"min": 0.0, "max": 5.0},
        },
    }


def test_field_plot_builder_dialog_defaults_to_disabled_stages_and_empty_cache(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    assert dialog.windowTitle() == "Field Plot"
    assert dialog._title_edit.text() == "Field Plot"
    assert dialog._file_combo.count() == 0
    assert not dialog._file_combo.isEnabled()
    assert not dialog._scalar_enabled_checkbox.isChecked()
    assert not dialog._contour_enabled_checkbox.isChecked()
    assert not dialog._vector_enabled_checkbox.isChecked()
    assert dialog._feature_edges_enabled_checkbox.isChecked()
    assert dialog._scalar_name_combo.count() == 0
    assert dialog._contour_name_combo.count() == 0
    assert dialog._vector_name_combo.count() == 0
    assert [dialog._vector_scale_combo.itemData(index) for index in range(dialog._vector_scale_combo.count())] == [
        None,
        False,
    ]


def test_field_plot_builder_dialog_populates_from_cached_workspace_metadata(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)
    plot_path = workspace / ".pyemsi" / "output.pvd"
    plot_path.parent.mkdir(parents=True)
    plot_path.write_text("dummy", encoding="utf-8")
    relative_path = os.path.join(".pyemsi", "output.pvd")
    manager.set_local("tools.field_plot.cached_pvds", [_cached_entry(relative_path)])
    manager.set_local("tools.field_plot.selected_relative_path", relative_path)

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    assert dialog._file_combo.count() == 1
    assert dialog._file_combo.currentData() == os.path.normpath(relative_path)
    assert dialog._selected_field_path() == os.path.abspath(os.path.normpath(os.fspath(plot_path)))
    assert [dialog._scalar_name_combo.itemData(index) for index in range(dialog._scalar_name_combo.count())] == [
        "Point Scalar"
    ]
    assert [dialog._vector_name_combo.itemData(index) for index in range(dialog._vector_name_combo.count())] == [
        "Point Vector"
    ]
    assert [dialog._vector_scale_combo.itemData(index) for index in range(dialog._vector_scale_combo.count())] == [
        None,
        False,
        "Point Scalar",
        "Point Vector",
    ]


def test_field_plot_builder_dialog_prunes_stale_cache_and_falls_back_to_latest_valid_entry(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)
    valid_path = workspace / ".pyemsi" / "fresh.pvd"
    valid_path.parent.mkdir(parents=True)
    valid_path.write_text("dummy", encoding="utf-8")
    stale_relative_path = os.path.join(".pyemsi", "stale.pvd")
    valid_relative_path = os.path.join(".pyemsi", "fresh.pvd")
    manager.set_local(
        "tools.field_plot.cached_pvds",
        [
            _cached_entry(stale_relative_path, updated_at_utc="2026-06-01T00:00:00Z"),
            _cached_entry(valid_relative_path, updated_at_utc="2026-06-02T00:00:00Z"),
        ],
    )
    manager.set_local("tools.field_plot.selected_relative_path", stale_relative_path)
    manager.save()

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    assert dialog._file_combo.count() == 1
    assert dialog._file_combo.currentData() == os.path.normpath(valid_relative_path)
    assert manager.get_local("tools.field_plot.cached_pvds") == [
        _cached_entry(valid_relative_path, updated_at_utc="2026-06-02T00:00:00Z")
    ]
    assert manager.get_local("tools.field_plot.selected_relative_path") == os.path.normpath(valid_relative_path)
    assert manager.get_local("tools.field_plot.filepath") == os.path.abspath(os.path.normpath(os.fspath(valid_path)))


def test_field_plot_builder_dialog_reload_sees_cache_written_by_external_process(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)
    plot_path = workspace / ".pyemsi" / "output.pvd"
    plot_path.parent.mkdir(parents=True)
    plot_path.write_text("dummy", encoding="utf-8")

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    assert dialog._file_combo.count() == 0

    external_manager = SettingsManager(global_settings_path=manager.global_settings_path)
    external_manager.load_workspace(workspace)
    external_manager.set_local("tools.field_plot.cached_pvds", [_cached_entry(os.path.join(".pyemsi", "output.pvd"))])
    external_manager.set_local("tools.field_plot.selected_relative_path", os.path.join(".pyemsi", "output.pvd"))
    external_manager.save()

    dialog._reload_cached_fields()

    assert dialog._file_combo.count() == 1
    assert dialog._file_combo.currentData() == os.path.normpath(os.path.join(".pyemsi", "output.pvd"))
    assert dialog._selected_field_path() == os.path.abspath(os.path.normpath(os.fspath(plot_path)))


def test_field_plot_builder_dialog_plot_requires_cached_field_then_stage(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    warnings = []

    monkeypatch.setattr(dialog_module.QMessageBox, "warning", lambda *args: warnings.append(args[2]))

    dialog._on_plot()

    plot_path = workspace / ".pyemsi" / "output.pvd"
    plot_path.parent.mkdir(parents=True)
    plot_path.write_text("dummy", encoding="utf-8")
    manager.set_local("tools.field_plot.cached_pvds", [_cached_entry(os.path.join(".pyemsi", "output.pvd"))])
    dialog._reload_cached_fields()
    dialog._on_plot()

    assert warnings == [
        "Run FEMAP conversion first to create a cached field file.",
        "Select at least one plotting stage.",
    ]


def test_field_plot_builder_dialog_suggest_factor_uses_cached_metadata_without_reading_plotter(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    plot_path = workspace / ".pyemsi" / "output.pvd"
    plot_path.parent.mkdir(parents=True)
    plot_path.write_text("dummy", encoding="utf-8")
    manager.set_local("tools.field_plot.cached_pvds", [_cached_entry(os.path.join(".pyemsi", "output.pvd"))])

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    dialog._vector_enabled_checkbox.setChecked(True)

    class _UnexpectedPlotter:
        def __init__(self, *_args, **_kwargs) -> None:
            raise AssertionError("Plotter should not be created for cached factor suggestions")

    monkeypatch.setattr(dialog_module, "Plotter", _UnexpectedPlotter)

    dialog._on_suggest_vector_factor()

    assert dialog._vector_name_combo.currentData() == "Point Vector"
    assert dialog._vector_factor_edit.text() == dialog_module._format_float_text(0.4)


def test_field_plot_builder_dialog_suggest_factor_uses_uniform_scale_rule_from_cache(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)
    plot_path = workspace / ".pyemsi" / "output.pvd"
    plot_path.parent.mkdir(parents=True)
    plot_path.write_text("dummy", encoding="utf-8")
    manager.set_local("tools.field_plot.cached_pvds", [_cached_entry(os.path.join(".pyemsi", "output.pvd"))])

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    dialog._vector_enabled_checkbox.setChecked(True)
    dialog._vector_scale_combo.setCurrentIndex(dialog_module._combo_index_for_data(dialog._vector_scale_combo, False))

    dialog._on_suggest_vector_factor()

    assert dialog._vector_factor_edit.text() == dialog_module._format_float_text(2.0)


def test_field_plot_builder_dialog_script_uses_cached_selection_without_creating_plotter(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    plot_path = workspace / ".pyemsi" / "output.pvd"
    plot_path.parent.mkdir(parents=True)
    plot_path.write_text("dummy", encoding="utf-8")
    manager.set_local("tools.field_plot.cached_pvds", [_cached_entry(os.path.join(".pyemsi", "output.pvd"))])

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    dialog._title_edit.setText("Rotor Field")
    dialog._scalar_enabled_checkbox.setChecked(True)

    captured = {}

    class _FakeGeneratedScriptDialog:
        def __init__(self, script_text, parent=None) -> None:
            captured["script"] = script_text
            captured["parent"] = parent

        def exec(self) -> int:
            captured["exec"] = True
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(dialog_module, "GeneratedScriptDialog", _FakeGeneratedScriptDialog)

    dialog._open_script_dialog()

    script = captured["script"]
    assert captured["parent"] is dialog
    assert captured["exec"] is True
    assert f"field_plot = Plotter({os.fspath(plot_path)!r})" in script
    assert "field_plot.set_scalar(" in script
    assert "name='Point Scalar'" in script
    assert "gui.add_field(field_plot, 'Rotor Field')" in script


def test_field_plot_builder_dialog_plot_creates_plotter_and_persists_cached_selection(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    plot_path = workspace / ".pyemsi" / "output.pvd"
    plot_path.parent.mkdir(parents=True)
    plot_path.write_text("dummy", encoding="utf-8")
    relative_path = os.path.join(".pyemsi", "output.pvd")
    manager.set_local("tools.field_plot.cached_pvds", [_cached_entry(relative_path)])

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    dialog._scalar_enabled_checkbox.setChecked(True)

    calls = []

    class _FakePlotter:
        def __init__(self, filepath) -> None:
            calls.append(("init", filepath))

        def set_scalar(self, **kwargs) -> None:
            calls.append(("set_scalar", kwargs))

        def set_feature_edges(self, **kwargs) -> None:
            calls.append(("set_feature_edges", kwargs))

        def close(self) -> None:
            calls.append(("close", None))

    added = {}
    monkeypatch.setattr(dialog_module, "Plotter", _FakePlotter)
    monkeypatch.setattr(gui, "add_field", lambda plotter, title: added.update({"plotter": plotter, "title": title}))

    dialog._on_plot()

    assert calls[0] == ("init", os.path.abspath(os.path.normpath(os.fspath(plot_path))))
    assert calls[1][0] == "set_scalar"
    assert calls[1][1]["name"] == "Point Scalar"
    assert calls[2][0] == "set_feature_edges"
    assert added["title"] == "Field Plot"
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert manager.get_local("tools.field_plot.selected_relative_path") == os.path.normpath(relative_path)
    assert manager.get_local("tools.field_plot.filepath") == os.path.abspath(os.path.normpath(os.fspath(plot_path)))
