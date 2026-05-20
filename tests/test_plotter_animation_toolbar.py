import os
import sys
import types

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget

# Test bootstrap: allow importing pyemsi on interpreters without the compiled
# femap_parser extension available.
if "pyemsi.core.femap_parser" not in sys.modules:
    _stub = types.ModuleType("pyemsi.core.femap_parser")

    class _DummyFemapType:  # pragma: no cover - bootstrap only
        pass

    _stub.FEMAPParser = _DummyFemapType
    _stub.FEMAPBlock = _DummyFemapType
    sys.modules["pyemsi.core.femap_parser"] = _stub

from pyemsi.plotter import qt_window as qt_window_module


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakeQtInteractor(QWidget):
    def __init__(self, parent=None, off_screen=False, **_kwargs):
        super().__init__(parent)
        self.off_screen = off_screen
        self.renderer = type("Renderer", (), {"axes_enabled": False, "actors": {}})()
        self.camera_widgets = []
        self.iren = None
        self._closed = False

    def reset_camera(self):
        return None

    def view_isometric(self):
        return None

    def view_xy(self):
        return None

    def view_yx(self, negative=False):
        return negative

    def view_xz(self, negative=False):
        return negative

    def view_yz(self, negative=False):
        return negative

    def render(self):
        return None

    def add_mesh(self, *_args, **_kwargs):
        return None

    def remove_actor(self, *_args, **_kwargs):
        return None

    def close(self):
        self._closed = True


class _FakeParentPlotter:
    def __init__(self, number_time_points=3, active_time_point=0):
        self.number_time_points = number_time_points
        self.active_time_point = active_time_point
        self.time_values = [float(index) for index in range(number_time_points)]
        self.render_calls = 0
        self.mesh = None

    def set_active_time_point(self, time_point):
        if not 0 <= time_point < self.number_time_points:
            raise IndexError("list index out of range")
        self.active_time_point = time_point

    def render(self):
        self.render_calls += 1


def _make_window(monkeypatch, number_time_points=3, active_time_point=0):
    _app()
    fake_pyvistaqt = types.ModuleType("pyvistaqt")
    fake_pyvistaqt.QtInteractor = _FakeQtInteractor
    monkeypatch.setitem(sys.modules, "pyvistaqt", fake_pyvistaqt)
    parent_plotter = _FakeParentPlotter(
        number_time_points=number_time_points,
        active_time_point=active_time_point,
    )
    window = qt_window_module.QtPlotterWindow(parent_plotter=parent_plotter)
    return window, parent_plotter


def test_animation_transport_actions_default_to_pause_and_are_exclusive(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)

    try:
        assert window._pause_action is not None
        assert window._play_action is not None
        assert window._reverse_action is not None
        assert window._pause_action.isChecked()
        assert not window._play_action.isChecked()
        assert not window._reverse_action.isChecked()

        window._play_action.trigger()

        assert window._is_playing
        assert window._animation_direction == 1
        assert window._play_action.isChecked()
        assert not window._pause_action.isChecked()
        assert not window._reverse_action.isChecked()

        window._reverse_action.trigger()

        assert window._is_playing
        assert window._animation_direction == -1
        assert window._reverse_action.isChecked()
        assert not window._pause_action.isChecked()
        assert not window._play_action.isChecked()

        window._pause_action.trigger()

        assert not window._is_playing
        assert window._pause_action.isChecked()
        assert not window._play_action.isChecked()
        assert not window._reverse_action.isChecked()
    finally:
        window.close()


def test_animation_transport_actions_reset_to_pause_when_playback_cannot_start(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch, number_time_points=1)

    try:
        window._play_action.trigger()

        assert not window._is_playing
        assert window._pause_action.isChecked()
        assert not window._play_action.isChecked()
        assert not window._reverse_action.isChecked()

        window._reverse_action.trigger()

        assert not window._is_playing
        assert window._pause_action.isChecked()
        assert not window._play_action.isChecked()
        assert not window._reverse_action.isChecked()
    finally:
        window.close()


def test_animation_transport_actions_reset_to_pause_at_animation_boundary(monkeypatch):
    window, parent_plotter = _make_window(monkeypatch, number_time_points=3, active_time_point=2)

    try:
        window._play_action.trigger()

        assert window._play_action.isChecked()

        window._animation_step()

        assert not window._is_playing
        assert parent_plotter.active_time_point == 2
        assert window._pause_action.isChecked()
        assert not window._play_action.isChecked()
        assert not window._reverse_action.isChecked()
    finally:
        window.close()


def test_forward_step_clamps_at_last_frame(monkeypatch):
    window, parent_plotter = _make_window(monkeypatch, number_time_points=3, active_time_point=2)

    try:
        window.set_time_point(1, relative=True)

        assert parent_plotter.active_time_point == 2
        assert parent_plotter.render_calls == 1
    finally:
        window.close()


def test_back_step_clamps_at_first_frame_and_last_action_uses_last_frame(monkeypatch):
    window, parent_plotter = _make_window(monkeypatch, number_time_points=3, active_time_point=0)

    try:
        window.set_time_point(-1, relative=True)

        assert parent_plotter.active_time_point == 0

        window.set_time_point(-1)

        assert parent_plotter.active_time_point == 2
        assert parent_plotter.render_calls == 2
    finally:
        window.close()


def test_display_toolbar_includes_save_screenshot_action(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)

    try:
        window._create_display_toolbar()

        assert window._save_screenshot_action is not None
        assert window._save_screenshot_action.text() == "Save Screenshot"
        assert window._save_screenshot_action.toolTip() == "Save the current rendered viewport to a PNG file"
    finally:
        window.close()


def test_save_screenshot_uses_explorer_path_as_default(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)
    captured = {}
    explorer_dir = os.getcwd()

    class _Explorer:
        current_path = explorer_dir

    class _Window:
        explorer = _Explorer()

    class _FakePixmap:
        def save(self, _path):
            return True

    try:
        monkeypatch.setattr(window, "_main_window", lambda: _Window())
        monkeypatch.setattr(window, "_capture_screenshot_pixmap", lambda: _FakePixmap())
        monkeypatch.setattr(
            window,
            "_prompt_screenshot_save_path",
            lambda default_path: captured.setdefault("path", default_path) and None,
        )

        window._save_screenshot_to_file()

        assert captured["path"] == os.path.join(explorer_dir, "PyVista Plotter.png")
    finally:
        window.close()


def test_save_screenshot_falls_back_to_cwd_default_path(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)
    captured = {}

    class _FakePixmap:
        def save(self, _path):
            return True

    try:
        monkeypatch.setattr(window, "_main_window", lambda: None)
        monkeypatch.setattr(window, "_capture_screenshot_pixmap", lambda: _FakePixmap())
        monkeypatch.setattr(
            window,
            "_prompt_screenshot_save_path",
            lambda default_path: captured.setdefault("path", default_path) and None,
        )

        window._save_screenshot_to_file()

        assert captured["path"] == os.path.join(os.getcwd(), "PyVista Plotter.png")
    finally:
        window.close()


def test_save_screenshot_auto_appends_png_extension(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)
    temp_dir = os.path.join(os.getcwd(), "_test_screenshot_save")
    os.makedirs(temp_dir, exist_ok=True)
    target_no_ext = os.path.join(temp_dir, "capture")
    saved_file = os.path.join(temp_dir, "capture.png")

    try:
        monkeypatch.setattr(window, "_capture_screenshot_pixmap", lambda: QPixmap(8, 8))
        monkeypatch.setattr(window, "_prompt_screenshot_save_path", lambda _default_path: str(target_no_ext))

        window._save_screenshot_to_file()

        assert os.path.isfile(saved_file)
    finally:
        window.close()
        if os.path.isfile(saved_file):
            os.remove(saved_file)
        if os.path.isdir(temp_dir):
            os.rmdir(temp_dir)


def test_save_screenshot_capture_failure_shows_error(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)
    errors = []

    try:
        monkeypatch.setattr(
            qt_window_module.QMessageBox,
            "critical",
            lambda parent, title, message: errors.append((parent, title, message)),
        )

        window._save_screenshot_to_file()

        assert len(errors) == 1
        assert errors[0][1] == "Screenshot Error"
        assert errors[0][2] == "The rendered viewport is not ready to capture."
    finally:
        window.close()


def test_save_screenshot_save_failure_shows_error(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)
    errors = []

    class _FailingPixmap:
        def save(self, _path):
            return False

    try:
        monkeypatch.setattr(window, "_capture_screenshot_pixmap", lambda: _FailingPixmap())
        monkeypatch.setattr(
            window,
            "_prompt_screenshot_save_path",
            lambda _default_path: os.path.join(os.getcwd(), "will_fail.png"),
        )
        monkeypatch.setattr(
            qt_window_module.QMessageBox,
            "critical",
            lambda parent, title, message: errors.append((parent, title, message)),
        )

        window._save_screenshot_to_file()

        assert len(errors) == 1
        assert errors[0][1] == "Screenshot Error"
        assert errors[0][2] == "Could not save screenshot to file."
    finally:
        window.close()


def test_default_screenshot_filename_uses_tab_title(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)

    try:
        monkeypatch.setattr(window, "_current_tab_title", lambda: "Rotor Angle Plot")
        assert window._default_screenshot_filename() == "Rotor Angle Plot.png"
    finally:
        window.close()


def test_default_screenshot_filename_sanitizes_invalid_characters(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)

    try:
        monkeypatch.setattr(window, "_current_tab_title", lambda: 'Plot: A/B*Test?')
        assert window._default_screenshot_filename() == "Plot_ A_B_Test_.png"
    finally:
        window.close()
