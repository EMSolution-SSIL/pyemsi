import os
import sys
import types

from PySide6.QtWidgets import QApplication, QDialog

sys.modules.setdefault("scienceplots", types.ModuleType("scienceplots"))

import pyemsi.gui as gui
from pyemsi.gui import field_plot_builder_dialog as dialog_module
from pyemsi.gui._field_file_metadata import FieldFileMetadata
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


def _external_metadata(path) -> FieldFileMetadata:
    resolved_path = os.path.abspath(os.path.normpath(os.fspath(path)))
    return FieldFileMetadata(
        resolved_path=resolved_path,
        scalar_names=["Point Scalar", "Cell Scalar", "Both Scalar"],
        contour_names=["Point Scalar", "Both Scalar"],
        vector_names=["Point Vector", "Cell Vector"],
        scale_names=["Point Scalar", "Cell Scalar", "Both Scalar", "Point Vector", "Cell Vector"],
        mesh_length=10.0,
        array_ranges={
            "Point Scalar": {"min": -2.0, "max": 4.0},
            "Cell Scalar": {"min": 1.0, "max": 3.0},
            "Both Scalar": {"min": 0.0, "max": 2.0},
            "Point Vector": {"min": 0.0, "max": 5.0},
            "Cell Vector": {"min": 0.0, "max": 2.0},
        },
        scalar_associations={
            "Point Scalar": frozenset({"point"}),
            "Cell Scalar": frozenset({"cell"}),
            "Both Scalar": frozenset({"point", "cell"}),
        },
        vector_associations={
            "Point Vector": frozenset({"point"}),
            "Cell Vector": frozenset({"cell"}),
        },
        vector_scale_names={
            "Point Vector": ["Point Scalar", "Both Scalar", "Point Vector"],
            "Cell Vector": ["Cell Scalar", "Both Scalar", "Cell Vector"],
        },
    )


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
    manager.save()

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


def test_field_plot_builder_dialog_plot_requires_field_then_stage(tmp_path, monkeypatch):
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
    manager.save()
    dialog._reload_cached_fields()
    dialog._on_plot()

    assert warnings == [
        "Select a cached field file or browse for a VTK field file.",
        "Select at least one plotting stage.",
    ]


def test_field_plot_builder_dialog_suggest_factor_uses_cached_metadata_without_reading_plotter(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    plot_path = workspace / ".pyemsi" / "output.pvd"
    plot_path.parent.mkdir(parents=True)
    plot_path.write_text("dummy", encoding="utf-8")
    manager.set_local("tools.field_plot.cached_pvds", [_cached_entry(os.path.join(".pyemsi", "output.pvd"))])
    manager.save()

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
    manager.save()

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
    manager.save()

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
    manager.save()

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


def test_field_plot_builder_dialog_browse_selects_inspected_file_and_persists_it(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    cached_path = workspace / ".pyemsi" / "output.pvd"
    cached_path.parent.mkdir(parents=True)
    cached_path.write_text("dummy", encoding="utf-8")
    relative_path = os.path.join(".pyemsi", "output.pvd")
    cached_entry = _cached_entry(relative_path)
    manager.set_local("tools.field_plot.cached_pvds", [cached_entry])
    manager.set_local("tools.field_plot.selected_relative_path", relative_path)
    manager.save()

    browse_directory = tmp_path / "browse"
    browse_directory.mkdir()
    external_path = browse_directory / "external.vtu"
    external_path.write_text("dummy", encoding="utf-8")
    captured = {}

    def fake_get_open_file_name(parent, title, initial_directory, file_filter):
        captured.update(
            {
                "parent": parent,
                "title": title,
                "initial_directory": initial_directory,
                "filter": file_filter,
            }
        )
        return os.fspath(external_path), file_filter

    monkeypatch.setattr(dialog_module.QFileDialog, "getOpenFileName", fake_get_open_file_name)
    monkeypatch.setattr(dialog_module, "inspect_field_file", lambda path: _external_metadata(path))

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(browse_directory))
    cached_index = dialog._file_combo.currentIndex()
    dialog._on_browse_field_file()

    resolved_external_path = os.path.abspath(os.path.normpath(os.fspath(external_path)))
    assert captured["parent"] is dialog
    assert captured["title"] == "Select VTK Field File"
    assert captured["initial_directory"] == os.path.dirname(dialog._cached_fields[0].resolved_path)
    assert "*.vtu" in captured["filter"]
    assert "*.pvd" in captured["filter"]
    assert dialog._file_combo.count() == 2
    assert dialog._file_combo.currentData() == resolved_external_path
    assert dialog._selected_relative_path() is None
    assert dialog._selected_field_path() == resolved_external_path
    assert manager.get_local("tools.field_plot.filepath") == resolved_external_path
    assert manager.get_local("tools.field_plot.selected_relative_path") is None
    assert manager.get_local("tools.field_plot.cached_pvds") == [cached_entry]
    assert f"field_plot = Plotter({resolved_external_path!r})" in dialog._generate_script_text()

    dialog._file_combo.setCurrentIndex(cached_index)
    assert dialog._selected_field_path() == os.path.abspath(os.path.normpath(os.fspath(cached_path)))

    second_external_path = browse_directory / "second.vtu"
    second_external_path.write_text("dummy", encoding="utf-8")
    dialog._select_external_field(_external_metadata(second_external_path))
    assert dialog._file_combo.count() == 2
    assert dialog._file_combo.findData(resolved_external_path) == -1


def test_field_plot_builder_dialog_browse_cancel_is_noop(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    monkeypatch.setattr(
        dialog_module.QFileDialog,
        "getOpenFileName",
        lambda *_args: ("", dialog_module.VTK_FIELD_FILE_FILTER),
    )
    monkeypatch.setattr(
        dialog_module,
        "inspect_field_file",
        lambda _path: (_ for _ in ()).throw(AssertionError("cancel must not inspect")),
    )

    dialog._on_browse_field_file()

    assert dialog._file_combo.count() == 0
    assert manager.get_local("tools.field_plot.filepath") is None


def test_field_plot_builder_dialog_external_associations_constrain_controls(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)
    external_path = workspace / "external.vtu"
    external_path.write_text("dummy", encoding="utf-8")
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    dialog._select_external_field(_external_metadata(external_path))
    dialog._scalar_enabled_checkbox.setChecked(True)

    assert [
        dialog._contour_name_combo.itemData(index) for index in range(dialog._contour_name_combo.count())
    ] == ["Point Scalar", "Both Scalar"]
    assert dialog._scalar_mode_combo.count() == 1
    assert dialog._scalar_mode_combo.currentData() == "node"
    assert not dialog._scalar_mode_combo.isEnabled()

    dialog._scalar_name_combo.setCurrentIndex(
        dialog_module._combo_index_for_data(dialog._scalar_name_combo, "Cell Scalar")
    )
    assert dialog._scalar_mode_combo.count() == 1
    assert dialog._scalar_mode_combo.currentData() == "element"
    assert not dialog._scalar_mode_combo.isEnabled()

    dialog._scalar_name_combo.setCurrentIndex(
        dialog_module._combo_index_for_data(dialog._scalar_name_combo, "Both Scalar")
    )
    assert [
        dialog._scalar_mode_combo.itemData(index) for index in range(dialog._scalar_mode_combo.count())
    ] == ["element", "node"]
    assert dialog._scalar_mode_combo.isEnabled()

    assert [
        dialog._vector_scale_combo.itemData(index) for index in range(dialog._vector_scale_combo.count())
    ] == [None, False, "Point Scalar", "Both Scalar", "Point Vector"]
    dialog._vector_name_combo.setCurrentIndex(
        dialog_module._combo_index_for_data(dialog._vector_name_combo, "Cell Vector")
    )
    assert [
        dialog._vector_scale_combo.itemData(index) for index in range(dialog._vector_scale_combo.count())
    ] == [None, False, "Cell Scalar", "Both Scalar", "Cell Vector"]


def test_field_plot_builder_dialog_restores_remembered_external_file(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    external_path = workspace / "remembered.vtu"
    external_path.write_text("dummy", encoding="utf-8")
    resolved_path = os.path.abspath(os.path.normpath(os.fspath(external_path)))
    manager.set_local("tools.field_plot.filepath", resolved_path)
    manager.set_local("tools.field_plot.selected_relative_path", None)
    manager.save()
    inspected = []
    monkeypatch.setattr(
        dialog_module,
        "inspect_field_file",
        lambda path: inspected.append(path) or _external_metadata(path),
    )

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    assert inspected == [resolved_path]
    assert dialog._file_combo.count() == 1
    assert dialog._file_combo.currentData() == resolved_path
    assert dialog._selected_field_path() == resolved_path


def test_field_plot_builder_dialog_missing_remembered_external_falls_back_to_cache(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)
    cached_path = workspace / ".pyemsi" / "output.pvd"
    cached_path.parent.mkdir(parents=True)
    cached_path.write_text("dummy", encoding="utf-8")
    relative_path = os.path.join(".pyemsi", "output.pvd")
    cached_entry = _cached_entry(relative_path)
    manager.set_local("tools.field_plot.cached_pvds", [cached_entry])
    manager.set_local("tools.field_plot.filepath", os.fspath(workspace / "missing.vtu"))
    manager.set_local("tools.field_plot.selected_relative_path", None)
    manager.save()

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    assert dialog._file_combo.count() == 1
    assert dialog._file_combo.currentData() == os.path.normpath(relative_path)
    assert manager.get_local("tools.field_plot.cached_pvds") == [cached_entry]
    assert manager.get_local("tools.field_plot.selected_relative_path") == os.path.normpath(relative_path)
    assert manager.get_local("tools.field_plot.filepath") == os.path.abspath(
        os.path.normpath(os.fspath(cached_path))
    )


def test_field_plot_builder_dialog_browse_failure_preserves_selection(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    cached_path = workspace / ".pyemsi" / "output.pvd"
    cached_path.parent.mkdir(parents=True)
    cached_path.write_text("dummy", encoding="utf-8")
    relative_path = os.path.join(".pyemsi", "output.pvd")
    cached_entry = _cached_entry(relative_path)
    manager.set_local("tools.field_plot.cached_pvds", [cached_entry])
    manager.set_local("tools.field_plot.selected_relative_path", relative_path)
    manager.save()
    invalid_path = workspace / "invalid.vtu"
    invalid_path.write_text("dummy", encoding="utf-8")
    errors = []

    monkeypatch.setattr(
        dialog_module.QFileDialog,
        "getOpenFileName",
        lambda *_args: (os.fspath(invalid_path), dialog_module.VTK_FIELD_FILE_FILTER),
    )
    monkeypatch.setattr(
        dialog_module,
        "inspect_field_file",
        lambda _path: (_ for _ in ()).throw(ValueError("invalid VTK")),
    )
    monkeypatch.setattr(dialog_module.QMessageBox, "critical", lambda *args: errors.append(args[2]))

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    dialog._on_browse_field_file()

    assert errors == ["invalid VTK"]
    assert dialog._file_combo.count() == 1
    assert dialog._file_combo.currentData() == os.path.normpath(relative_path)
    assert manager.get_local("tools.field_plot.cached_pvds") == [cached_entry]


def test_field_plot_builder_dialog_plots_external_selection(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    external_path = workspace / "external.vtu"
    external_path.write_text("dummy", encoding="utf-8")
    resolved_path = os.path.abspath(os.path.normpath(os.fspath(external_path)))
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    dialog._select_external_field(_external_metadata(external_path))
    dialog._scalar_enabled_checkbox.setChecked(True)
    calls = []

    class _FakePlotter:
        def __init__(self, filepath):
            calls.append(("init", filepath))

        def set_scalar(self, **kwargs):
            calls.append(("set_scalar", kwargs))

        def set_feature_edges(self, **kwargs):
            calls.append(("set_feature_edges", kwargs))

        def close(self):
            calls.append(("close", None))

    added = {}
    monkeypatch.setattr(dialog_module, "Plotter", _FakePlotter)
    monkeypatch.setattr(gui, "add_field", lambda plotter, title: added.update({"plotter": plotter, "title": title}))

    dialog._on_plot()

    assert calls[0] == ("init", resolved_path)
    assert calls[1][0] == "set_scalar"
    assert calls[1][1]["name"] == "Point Scalar"
    assert calls[1][1]["mode"] == "node"
    assert added["title"] == "Field Plot"
    assert dialog.result() == QDialog.DialogCode.Accepted
