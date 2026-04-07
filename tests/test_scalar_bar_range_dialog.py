import numpy as np
import pyvista as pv
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

import pyemsi.plotter.scalar_bar_range_dialog as dialog_module
from pyemsi.plotter.plotter import Plotter
from pyemsi.plotter.scalar_bar_range_dialog import ScalarBarRangeDialog


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakeLookupTable:
    def __init__(self, minimum, maximum):
        self._range = (float(minimum), float(maximum))

    def GetRange(self):
        return self._range

    def SetRange(self, minimum, maximum):
        self._range = (float(minimum), float(maximum))


class _FakeScalarBarActor:
    def __init__(self, minimum, maximum):
        self._lookup_table = _FakeLookupTable(minimum, maximum)

    def GetLookupTable(self):
        return self._lookup_table


class _FakeQtInteractor:
    def __init__(self, ranges):
        self.scalar_bars = {
            scalar_bar_name: _FakeScalarBarActor(minimum, maximum)
            for scalar_bar_name, (minimum, maximum) in ranges.items()
        }
        self.update_calls = []
        self.render_calls = 0

    def update_scalar_bar_range(self, clim, name=None):
        self.update_calls.append((name, tuple(float(value) for value in clim)))

    def render(self):
        self.render_calls += 1


class _FakeParentPlotter:
    def __init__(self, ranges, auto_ranges=None):
        self._ranges = {name: (float(minimum), float(maximum)) for name, (minimum, maximum) in ranges.items()}
        self._auto_ranges = auto_ranges or {}
        self.apply_calls = []
        self.compute_calls = []

    def get_scalar_bar_ranges(self):
        return dict(self._ranges)

    def apply_scalar_bar_range(self, scalar_bar_name, minimum, maximum):
        minimum = float(minimum)
        maximum = float(maximum)
        self.apply_calls.append((scalar_bar_name, minimum, maximum))
        self._ranges[scalar_bar_name] = (minimum, maximum)

    def compute_scalar_bar_data_range(self, scalar_bar_name):
        self.compute_calls.append(scalar_bar_name)
        return self._auto_ranges[scalar_bar_name]


class _FakePlotterWindow:
    def __init__(self, parent_plotter):
        self._window = QMainWindow()
        self.parent_plotter = parent_plotter


class _FakeTimeReader:
    def __init__(self, time_values, meshes):
        self.time_values = list(time_values)
        self.number_time_points = len(self.time_values)
        self.active_time_value = self.time_values[0]
        self._meshes = list(meshes)

    def set_active_time_value(self, time_value):
        self.active_time_value = time_value

    def set_active_time_point(self, time_point):
        self.active_time_value = self.time_values[time_point]

    def read(self):
        active_index = self.time_values.index(self.active_time_value)
        return self._meshes[active_index]


def _make_range_plotter(mesh, scalar_bar_range=(0.0, 1.0)):
    plotter = Plotter.__new__(Plotter)
    plotter._mesh = mesh
    plotter.reader = None
    plotter._scalar_props = {}
    plotter._vector_props = {}
    plotter._contour_props = {}
    plotter._block_visibility = {}
    plotter._scalar_bar_sources = {"foo": {"array_name": "foo", "association": "point"}}
    plotter.plotter = _FakeQtInteractor({"foo": scalar_bar_range})
    return plotter


def test_plotter_apply_scalar_bar_range_updates_lookup_table_and_plotter_call():
    mesh = pv.Sphere(theta_resolution=8, phi_resolution=8)
    mesh["foo"] = np.linspace(-1.0, 2.0, mesh.n_points)
    plotter = _make_range_plotter(mesh)

    assert plotter.compute_scalar_bar_data_range("foo") == (-1.0, 2.0)

    plotter.apply_scalar_bar_range("foo", -3.0, 4.0)

    assert plotter.plotter.update_calls == [("foo", (-3.0, 4.0))]
    assert plotter.get_scalar_bar_ranges()["foo"] == (-3.0, 4.0)
    assert plotter.plotter.render_calls == 1


def test_plotter_compute_scalar_bar_data_range_scans_all_time_steps_and_restores_active_time():
    mesh0 = pv.Sphere(theta_resolution=8, phi_resolution=8)
    mesh0["foo"] = np.linspace(1.0, 3.0, mesh0.n_points)
    mesh1 = pv.Sphere(theta_resolution=8, phi_resolution=8)
    mesh1["foo"] = np.linspace(-5.0, 4.0, mesh1.n_points)

    plotter = _make_range_plotter(mesh0)
    meshes = [mesh0, mesh1]
    time_reader = _FakeTimeReader([0.0, 1.0], meshes)

    plotter.reader = time_reader
    plotter._time_reader = lambda: time_reader

    computed_range = plotter.compute_scalar_bar_data_range("foo")

    assert computed_range == (-5.0, 4.0)
    assert time_reader.active_time_value == 0.0
    assert plotter._mesh is None


def test_scalar_bar_range_dialog_applies_manual_ranges():
    _app()
    parent_plotter = _FakeParentPlotter({"foo": (0.0, 1.0), "bar": (-2.0, 2.0)})
    dialog = ScalarBarRangeDialog(
        _FakeQtInteractor(parent_plotter.get_scalar_bar_ranges()), _FakePlotterWindow(parent_plotter)
    )

    dialog._range_inputs["foo"]["min"].setValue(-3.5)
    dialog._range_inputs["foo"]["max"].setValue(9.25)
    dialog._on_apply()

    assert parent_plotter.apply_calls == [
        ("foo", -3.5, 9.25),
        ("bar", -2.0, 2.0),
    ]
    dialog.close()


def test_scalar_bar_range_dialog_auto_button_updates_fields(monkeypatch):
    _app()
    parent_plotter = _FakeParentPlotter({"foo": (0.0, 1.0)}, auto_ranges={"foo": (-8.0, 12.0)})
    dialog = ScalarBarRangeDialog(
        _FakeQtInteractor(parent_plotter.get_scalar_bar_ranges()), _FakePlotterWindow(parent_plotter)
    )

    monkeypatch.setattr(dialog_module.QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes)

    dialog._auto_buttons["foo"].click()

    assert dialog._range_inputs["foo"]["min"].value() == -8.0
    assert dialog._range_inputs["foo"]["max"].value() == 12.0
    assert parent_plotter.compute_calls == ["foo"]
    dialog.close()


def test_scalar_bar_range_dialog_auto_button_stops_when_user_declines(monkeypatch):
    _app()
    parent_plotter = _FakeParentPlotter({"foo": (0.0, 1.0)}, auto_ranges={"foo": (-8.0, 12.0)})
    dialog = ScalarBarRangeDialog(
        _FakeQtInteractor(parent_plotter.get_scalar_bar_ranges()), _FakePlotterWindow(parent_plotter)
    )

    monkeypatch.setattr(dialog_module.QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.No)

    dialog._auto_buttons["foo"].click()

    assert dialog._range_inputs["foo"]["min"].value() == 0.0
    assert dialog._range_inputs["foo"]["max"].value() == 1.0
    assert parent_plotter.compute_calls == []
    dialog.close()


def test_scalar_bar_range_dialog_cancel_restores_initial_ranges():
    _app()
    parent_plotter = _FakeParentPlotter({"foo": (1.0, 5.0), "bar": (-1.0, 2.0)})
    dialog = ScalarBarRangeDialog(
        _FakeQtInteractor(parent_plotter.get_scalar_bar_ranges()), _FakePlotterWindow(parent_plotter)
    )

    dialog._range_inputs["foo"]["min"].setValue(-10.0)
    dialog._range_inputs["foo"]["max"].setValue(10.0)
    dialog._on_cancel()

    assert parent_plotter.apply_calls == [
        ("foo", 1.0, 5.0),
        ("bar", -1.0, 2.0),
    ]
    assert dialog.result() == dialog.DialogCode.Rejected
