from PySide6.QtWidgets import QApplication, QWidget

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

    def set_active_time_point(self, time_point):
        if not 0 <= time_point < self.number_time_points:
            raise IndexError("list index out of range")
        self.active_time_point = time_point

    def render(self):
        self.render_calls += 1


def _make_window(monkeypatch, number_time_points=3, active_time_point=0):
    _app()
    monkeypatch.setattr(qt_window_module, "QtInteractor", _FakeQtInteractor)
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
