import sys
import types

from PySide6.QtWidgets import QApplication, QMainWindow

if "pyemsi.core.femap_parser" not in sys.modules:
    _stub = types.ModuleType("pyemsi.core.femap_parser")

    class _DummyFemapType:  # pragma: no cover - bootstrap only
        pass

    _stub.FEMAPParser = _DummyFemapType
    _stub.FEMAPBlock = _DummyFemapType
    sys.modules["pyemsi.core.femap_parser"] = _stub

import pyemsi.plotter.camera_position_dialog as dialog_module
from pyemsi.plotter.camera_position_dialog import (
    CameraPositionDialog,
    format_camera_position,
    validate_camera_values,
)


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakePlotter:
    def __init__(self, camera_position=None):
        self.camera_position = camera_position or (
            (1.0, 2.0, 3.0),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        self.render_calls = 0

    def render(self):
        self.render_calls += 1


class _FakePlotterWindow:
    def __init__(self):
        self.app = _app()
        self._window = QMainWindow()


def _make_dialog(camera_position=None):
    _app()
    return CameraPositionDialog(_FakePlotter(camera_position), _FakePlotterWindow())


def test_format_camera_position_uses_compact_list_representation():
    values = ((1.23456789, 0.0, -0.000012345), (2.0, 3.0, 4.0), (0.0, 1.0, 0.0))

    assert format_camera_position(values) == "[(1.23457, 0, -1.2345e-05), (2, 3, 4), (0, 1, 0)]"


def test_validate_camera_values_rejects_identical_position_and_focal_point():
    try:
        validate_camera_values(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
    except ValueError as exc:
        assert str(exc) == "Position and focal point cannot be identical."
    else:
        raise AssertionError("validate_camera_values should reject identical position and focal point")


def test_validate_camera_values_rejects_zero_view_up():
    try:
        validate_camera_values(((1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
    except ValueError as exc:
        assert str(exc) == "View Up vector cannot be zero."
    else:
        raise AssertionError("validate_camera_values should reject zero View Up")


def test_line_edit_change_applies_camera_position_and_updates_copy_field():
    dialog = _make_dialog()

    try:
        dialog._line_edits[(0, 0)].setText("5")
        dialog._on_line_edit_finished(0, 0)

        assert dialog.plotter.camera_position == (
            (5.0, 2.0, 3.0),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        assert dialog.plotter.render_calls == 1
        assert dialog._camera_position_edit.text() == "[(5, 2, 3), (0, 0, 0), (0, 1, 0)]"
    finally:
        dialog.close()


def test_line_edit_value_outside_slider_range_recenters_slider():
    dialog = _make_dialog()

    try:
        old_minimum, old_maximum = dialog._slider_ranges[(0, 0)]
        old_half_span = (old_maximum - old_minimum) / 2

        dialog._line_edits[(0, 0)].setText("100")
        dialog._on_line_edit_finished(0, 0)

        minimum, maximum = dialog._slider_ranges[(0, 0)]
        assert minimum == 100.0 - old_half_span
        assert maximum == 100.0 + old_half_span
        assert dialog._sliders[(0, 0)].value() == dialog._SLIDER_STEPS // 2
    finally:
        dialog.close()


def test_slider_change_applies_camera_position():
    dialog = _make_dialog()

    try:
        dialog._sliders[(0, 0)].setValue(750)

        minimum, maximum = dialog._slider_ranges[(0, 0)]
        expected_x = minimum + 0.75 * (maximum - minimum)
        assert dialog.plotter.camera_position[0][0] == expected_x
        assert dialog.plotter.render_calls == 1
    finally:
        dialog.close()


def test_copy_button_updates_clipboard():
    dialog = _make_dialog()

    try:
        dialog._copy_to_clipboard()

        assert _app().clipboard().text() == "[(1, 2, 3), (0, 0, 0), (0, 1, 0)]"
    finally:
        dialog.close()


def test_invalid_line_edit_change_warns_and_reverts(monkeypatch):
    dialog = _make_dialog()
    warnings = []

    try:
        monkeypatch.setattr(
            dialog_module.QMessageBox,
            "warning",
            lambda parent, title, message: warnings.append((parent, title, message)),
        )

        dialog._line_edits[(2, 1)].setText("0")
        dialog._on_line_edit_finished(2, 1)

        assert warnings[0][1] == "Camera Position"
        assert warnings[0][2] == "View Up vector cannot be zero."
        assert dialog.plotter.camera_position == (
            (1.0, 2.0, 3.0),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        assert dialog.plotter.render_calls == 0
        assert dialog._line_edits[(2, 1)].text() == "1"
    finally:
        dialog.close()


def test_refresh_pulls_live_plotter_camera_position():
    dialog = _make_dialog()

    try:
        dialog.plotter.camera_position = ((10.0, 11.0, 12.0), (1.0, 1.0, 1.0), (0.0, 0.0, 1.0))

        dialog._load_camera_position()

        assert dialog._line_edits[(0, 0)].text() == "10"
        assert dialog._camera_position_edit.text() == "[(10, 11, 12), (1, 1, 1), (0, 0, 1)]"
    finally:
        dialog.close()

