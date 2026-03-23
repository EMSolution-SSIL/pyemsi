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


def test_field_plot_builder_dialog_defaults_to_disabled_stages(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)
    expected_plot_path = os.path.abspath(os.path.normpath(os.fspath(workspace / ".pyemsi" / "output.pvd")))

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    assert dialog.windowTitle() == "Field Plot"
    assert dialog._title_edit.text() == "Field Plot"
    assert dialog._file_field.value() == expected_plot_path
    assert not dialog._scalar_enabled_checkbox.isChecked()
    assert not dialog._contour_enabled_checkbox.isChecked()
    assert not dialog._vector_enabled_checkbox.isChecked()
    assert dialog._scalar_kwargs()["cmap"] == "viridis"


def test_field_plot_builder_dialog_plot_requires_existing_file_and_stage(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    warnings = []

    monkeypatch.setattr(dialog_module.QMessageBox, "warning", lambda *args: warnings.append(args[2]))

    dialog._file_field.set_value(None)
    dialog._on_plot()
    dialog._file_field.set_value(os.fspath(workspace / "missing.pvd"))
    dialog._on_plot()

    assert warnings == [
        "Field file is required.",
        "Select at least one plotting stage.",
    ]


def test_field_plot_builder_dialog_plot_requires_valid_positive_vector_factor(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    warnings = []

    monkeypatch.setattr(dialog_module.QMessageBox, "warning", lambda *args: warnings.append(args[2]))

    dialog._file_field.set_value(os.fspath(workspace / "output.pvd"))
    dialog._vector_enabled_checkbox.setChecked(True)
    dialog._vector_factor_edit.setText("0")

    dialog._on_plot()

    assert warnings == ["Vector factor must be greater than 0."]


class _FakeArray:
    def __init__(self, shape):
        self.shape = shape
        self.ndim = len(shape)


class _FakeAttributes:
    def __init__(self, arrays):
        self._arrays = arrays

    def keys(self):
        return list(self._arrays)

    def __getitem__(self, name):
        return self._arrays[name]


class _FakeBlock:
    def __init__(self, point_arrays=None, cell_arrays=None):
        self.point_data = _FakeAttributes(point_arrays or {})
        self.cell_data = _FakeAttributes(cell_arrays or {})


class _FakeMultiBlock:
    def __init__(self, blocks, names):
        self._blocks = blocks
        self._names = names

    def __iter__(self):
        return iter(self._blocks)

    def get_block_name(self, index):
        return self._names[index]


def test_field_plot_builder_dialog_analyse_requires_field_file(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    warnings = []

    monkeypatch.setattr(dialog_module.QMessageBox, "warning", lambda *args: warnings.append(args[2]))

    dialog._file_field.set_value(None)

    dialog._on_analyse()

    assert warnings == ["Field file is required."]


def test_field_plot_builder_dialog_analyse_repopulates_combos_from_mesh_arrays(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    plot_path = workspace / "output.pvd"
    plot_path.write_text("dummy", encoding="utf-8")
    dialog._file_field.set_value(os.fspath(plot_path))

    calls = []

    class _FakePlotter:
        def __init__(self, filepath) -> None:
            calls.append(("init", filepath))
            self.mesh = _FakeMultiBlock(
                [
                    _FakeBlock(
                        point_arrays={
                            "Point Scalar": _FakeArray((10,)),
                            "Point Vector": _FakeArray((10, 3)),
                            "Tensor": _FakeArray((10, 6)),
                            "vtkOriginalPointIds": _FakeArray((10,)),
                        },
                        cell_arrays={
                            "Cell Scalar": _FakeArray((5,)),
                            "vtkOriginalCellIds": _FakeArray((5,)),
                        },
                    ),
                    _FakeBlock(
                        point_arrays={"Extra Vector": _FakeArray((12, 3))},
                        cell_arrays={"Extra Scalar": _FakeArray((6, 1))},
                    ),
                ],
                ["main", "secondary"],
            )

        def close(self) -> None:
            calls.append(("close", None))

    monkeypatch.setattr(dialog_module, "Plotter", _FakePlotter)

    dialog._scalar_name_combo.setCurrentIndex(
        dialog_module._combo_index_for_data(dialog._scalar_name_combo, "B-Mag (T)")
    )
    dialog._contour_name_combo.setCurrentIndex(
        dialog_module._combo_index_for_data(dialog._contour_name_combo, "Flux (A/m)")
    )
    dialog._vector_name_combo.setCurrentIndex(
        dialog_module._combo_index_for_data(dialog._vector_name_combo, "Point Vector")
    )
    dialog._vector_scale_combo.setCurrentIndex(dialog_module._combo_index_for_data(dialog._vector_scale_combo, False))

    dialog._on_analyse()

    assert calls == [("init", os.fspath(plot_path)), ("close", None)]
    assert [dialog._scalar_name_combo.itemData(index) for index in range(dialog._scalar_name_combo.count())] == [
        "Point Scalar",
        "Cell Scalar",
        "Extra Scalar",
    ]
    assert [dialog._contour_name_combo.itemData(index) for index in range(dialog._contour_name_combo.count())] == [
        "Point Scalar",
        "Cell Scalar",
        "Extra Scalar",
    ]
    assert [dialog._vector_name_combo.itemData(index) for index in range(dialog._vector_name_combo.count())] == [
        "Point Vector",
        "Extra Vector",
    ]
    assert [dialog._vector_scale_combo.itemData(index) for index in range(dialog._vector_scale_combo.count())] == [
        None,
        False,
        "Point Scalar",
        "Cell Scalar",
        "Extra Scalar",
        "Point Vector",
        "Extra Vector",
    ]
    assert dialog._vector_name_combo.currentData() == "Point Vector"
    assert dialog._vector_scale_combo.currentData() is False


def test_field_plot_builder_dialog_analyse_falls_back_to_defaults_when_mesh_has_no_usable_arrays(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    plot_path = workspace / "output.pvd"
    plot_path.write_text("dummy", encoding="utf-8")
    dialog._file_field.set_value(os.fspath(plot_path))

    class _FakePlotter:
        def __init__(self, filepath) -> None:
            self.mesh = _FakeBlock(point_arrays={"Tensor": _FakeArray((8, 9))}, cell_arrays={})

        def close(self) -> None:
            return None

    monkeypatch.setattr(dialog_module, "Plotter", _FakePlotter)

    dialog._on_analyse()

    assert [dialog._scalar_name_combo.itemData(index) for index in range(dialog._scalar_name_combo.count())] == list(
        dialog_module.SCALAR_NAMES
    )
    assert [dialog._vector_name_combo.itemData(index) for index in range(dialog._vector_name_combo.count())] == list(
        dialog_module.VECTOR_NAMES
    )
    assert [dialog._vector_scale_combo.itemData(index) for index in range(dialog._vector_scale_combo.count())] == [
        option[1] for option in dialog_module.VECTOR_SCALE_OPTIONS
    ]


def test_field_plot_builder_dialog_analyse_closes_plotter_and_reports_errors(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    plot_path = workspace / "output.pvd"
    plot_path.write_text("dummy", encoding="utf-8")
    dialog._file_field.set_value(os.fspath(plot_path))
    criticals = []
    calls = []

    class _FakePlotter:
        def __init__(self, filepath) -> None:
            calls.append(("init", filepath))

        @property
        def mesh(self):
            raise RuntimeError("bad mesh")

        def close(self) -> None:
            calls.append(("close", None))

    monkeypatch.setattr(dialog_module, "Plotter", _FakePlotter)
    monkeypatch.setattr(dialog_module.QMessageBox, "critical", lambda *args: criticals.append(args[2]))

    dialog._on_analyse()

    assert calls == [("init", os.fspath(plot_path)), ("close", None)]
    assert criticals == ["bad mesh"]


def test_field_plot_builder_dialog_prefers_explicit_field_plot_path_over_femap_defaults(
    tmp_path,
):
    _app()
    manager, workspace = _make_manager(tmp_path)
    explicit_path = workspace / "saved" / "field.pvd"
    manager.set_local("tools.field_plot.filepath", os.fspath(explicit_path))

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    assert dialog._file_field.value() == os.path.abspath(os.path.normpath(os.fspath(explicit_path)))


def test_field_plot_builder_dialog_initializes_path_from_femap_converter_settings(
    tmp_path,
):
    _app()
    manager, workspace = _make_manager(tmp_path)
    manager.set_local("tools.femap_converter.output_dir", "exports")
    manager.set_local("tools.femap_converter.output_name", "motor")

    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    expected_plot_path = os.path.abspath(os.path.normpath(os.fspath(workspace / "exports" / "motor.pvd")))
    assert dialog._file_field.value() == expected_plot_path


def test_field_plot_builder_dialog_script_uses_widget_state_without_creating_plotter(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    plot_path = workspace / "output.pvd"
    plot_path.write_text("dummy", encoding="utf-8")

    dialog._file_field.set_value(os.fspath(plot_path))
    dialog._title_edit.setText("Rotor Field")
    dialog._scalar_enabled_checkbox.setChecked(True)
    dialog._scalar_mode_combo.setCurrentIndex(dialog_module._combo_index_for_data(dialog._scalar_mode_combo, "element"))
    dialog._vector_enabled_checkbox.setChecked(True)
    dialog._vector_scale_combo.setCurrentIndex(dialog_module._combo_index_for_data(dialog._vector_scale_combo, False))

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
    assert "from pyemsi import gui, Plotter" in script
    assert f"field_plot = Plotter({os.fspath(plot_path)!r})" in script
    assert "field_plot.set_scalar(" in script
    assert "name='B-Mag (T)'" in script
    assert "mode='element'" in script
    assert "cmap='viridis'" in script
    assert "field_plot.set_vector(" in script
    assert "scale=False" in script
    assert "gui.add_field(field_plot, 'Rotor Field')" in script


def test_field_plot_builder_dialog_plot_creates_plotter_and_persists_settings(tmp_path, monkeypatch):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))
    plot_path = workspace / "output.pvd"
    plot_path.write_text("dummy", encoding="utf-8")

    dialog._file_field.set_value(os.fspath(plot_path))
    dialog._title_edit.setText("Field Plot")
    dialog._scalar_enabled_checkbox.setChecked(True)
    dialog._contour_enabled_checkbox.setChecked(True)
    dialog._vector_enabled_checkbox.setChecked(True)
    dialog._vector_factor_edit.setText("1e-30")
    dialog._vector_scale_combo.setCurrentIndex(dialog_module._combo_index_for_data(dialog._vector_scale_combo, None))
    dialog._vector_use_tolerance_checkbox.setChecked(True)
    dialog._vector_tolerance_spin.setValue(0.25)

    calls = []

    class _FakePlotter:
        def __init__(self, filepath) -> None:
            calls.append(("init", filepath))

        def set_scalar(self, **kwargs) -> None:
            calls.append(("set_scalar", kwargs))

        def set_contour(self, **kwargs) -> None:
            calls.append(("set_contour", kwargs))

        def set_vector(self, **kwargs) -> None:
            calls.append(("set_vector", kwargs))

        def close(self) -> None:
            calls.append(("close", None))

    added = {}
    monkeypatch.setattr(dialog_module, "Plotter", _FakePlotter)
    monkeypatch.setattr(
        gui,
        "add_field",
        lambda plotter, title: added.update({"plotter": plotter, "title": title}),
    )

    dialog._on_plot()

    assert calls[0] == ("init", os.fspath(plot_path))
    assert calls[1][0] == "set_scalar"
    assert calls[1][1]["cmap"] == "viridis"
    assert calls[2][0] == "set_contour"
    assert calls[3][0] == "set_vector"
    assert calls[3][1]["factor"] == 1e-30
    assert added["title"] == "Field Plot"
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert manager.get_local("tools.field_plot.filepath") == os.path.abspath(os.path.normpath(os.fspath(plot_path)))
    assert manager.get_local("tools.field_plot.title") is None
    assert manager.get_local("tools.field_plot.scalar_enabled") is None
    assert manager.get_local("tools.field_plot.vector_tolerance") is None


def test_field_plot_builder_dialog_vector_scale_preserves_uniform_option(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    dialog._vector_scale_combo.setCurrentIndex(dialog_module._combo_index_for_data(dialog._vector_scale_combo, False))

    assert dialog._vector_kwargs()["scale"] is False


def test_field_plot_builder_dialog_scalar_colormap_selection_uses_display_settings_choices(tmp_path):
    _app()
    manager, workspace = _make_manager(tmp_path)
    dialog = FieldPlotBuilderDialog(manager, browse_dir_getter=lambda: os.fspath(workspace))

    dialog._scalar_cmap_combo.setCurrentIndex(
        dialog_module._combo_index_for_data(dialog._scalar_cmap_combo, "turbo : miscellaneous")
    )

    assert dialog._scalar_kwargs()["cmap"] == "turbo"
