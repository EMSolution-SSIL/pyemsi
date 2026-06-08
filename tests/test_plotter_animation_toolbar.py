import os
import sys
import types

from PySide6.QtCore import QPoint
from PySide6.QtGui import QAction, QPixmap
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
        self.widgets = type("Widgets", (), {"camera_widgets": self.camera_widgets})()
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
    def __init__(self, number_time_points=3, active_time_point=0, block_names=None):
        self.number_time_points = number_time_points
        self.active_time_point = active_time_point
        self.time_values = [float(index) for index in range(number_time_points)]
        self.render_calls = 0
        self.mesh = None
        self._block_visibility = {name: True for name in (block_names or [])}
        self.set_block_visibility_calls = []
        self.set_blocks_visibility_calls = []

    def set_active_time_point(self, time_point):
        if not 0 <= time_point < self.number_time_points:
            raise IndexError("list index out of range")
        self.active_time_point = time_point

    def render(self):
        self.render_calls += 1

    def get_block_names(self):
        return list(self._block_visibility)

    def get_block_visibility(self, block_name):
        return self._block_visibility.get(block_name, True)

    def set_block_visibility(self, block_name, visible):
        self._block_visibility[block_name] = visible
        self.set_block_visibility_calls.append((block_name, visible))

    def set_blocks_visibility(self, visibility):
        self._block_visibility.update(visibility)
        self.set_blocks_visibility_calls.append(dict(visibility))


def _make_window(monkeypatch, number_time_points=3, active_time_point=0, block_names=None):
    _app()
    fake_pyvistaqt = types.ModuleType("pyvistaqt")
    fake_pyvistaqt.QtInteractor = _FakeQtInteractor
    monkeypatch.setitem(sys.modules, "pyvistaqt", fake_pyvistaqt)
    parent_plotter = _FakeParentPlotter(
        number_time_points=number_time_points,
        active_time_point=active_time_point,
        block_names=block_names,
    )
    window = qt_window_module.QtPlotterWindow(parent_plotter=parent_plotter)
    return window, parent_plotter


class _FakeMenu:
    selected_text = None
    last_actions = []

    def __init__(self, *_args, **_kwargs):
        type(self).last_actions = []

    def addAction(self, text):
        action = QAction(text, None)
        type(self).last_actions.append(action)
        return action

    def addSeparator(self):
        return None

    def exec(self, _pos):
        for action in type(self).last_actions:
            if action.text() == type(self).selected_text:
                return action
        return None


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


def test_camera_toolbar_includes_camera_position_action(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)

    try:
        matching_actions = [
            action for action in window._camera_toolbar.actions() if action.text() == "Camera Position"
        ]

        assert len(matching_actions) == 1
        assert matching_actions[0].toolTip() == "Open camera position dialog"
        assert not matching_actions[0].icon().isNull()
    finally:
        window.close()


def test_query_toolbar_includes_cursor_pick_action(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)

    try:
        assert window._cursor_pick_action is not None
        assert window._cursor_pick_action.text() == "Cursor"
        assert window._cursor_pick_action.toolTip() == "Toggle block picking for the plotter context menu"
        assert not window._cursor_pick_action.icon().isNull()
    finally:
        window.close()


def test_cursor_pick_toggle_enables_cell_picking_without_history_dialog(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)
    captured = {}

    try:
        monkeypatch.setattr(window, "disable_point_picking_mode", lambda render=False: captured.setdefault("disabled_point", render))

        def _fake_enable_cell_picking_mode(on_picked, picker_tolerance=0.025):
            captured["callback"] = on_picked
            captured["picker_tolerance"] = picker_tolerance

        monkeypatch.setattr(window, "enable_cell_picking_mode", _fake_enable_cell_picking_mode)

        window._cursor_pick_action.trigger()

        assert window._cursor_pick_action.isChecked()
        assert callable(captured["callback"])
        assert captured["picker_tolerance"] == 0.025
        assert captured["disabled_point"] is False
        assert window._pick_result_history_dialog is None
    finally:
        window.close()


def test_plotter_context_menu_uses_custom_context_policy(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch)

    try:
        assert window.plotter.contextMenuPolicy() == qt_window_module.Qt.ContextMenuPolicy.CustomContextMenu
    finally:
        window.close()


def test_plotter_context_menu_shows_global_actions_without_pick_mode(monkeypatch):
    window, _parent_plotter = _make_window(monkeypatch, block_names=["BlockA", "BlockB"])

    try:
        monkeypatch.setattr(qt_window_module, "QMenu", _FakeMenu)
        _FakeMenu.selected_text = None

        window._show_plotter_context_menu(QPoint(0, 0))

        assert [action.text() for action in _FakeMenu.last_actions] == ["Show All Blocks", "Blocks..."]
    finally:
        window.close()


def test_plotter_context_menu_show_all_restores_block_visibility(monkeypatch):
    window, parent_plotter = _make_window(monkeypatch, block_names=["BlockA", "BlockB"])

    try:
        monkeypatch.setattr(qt_window_module, "QMenu", _FakeMenu)
        _FakeMenu.selected_text = "Show All Blocks"
        parent_plotter._block_visibility["BlockA"] = False

        window._show_plotter_context_menu(QPoint(0, 0))

        assert parent_plotter.set_blocks_visibility_calls == [{"BlockA": True, "BlockB": True}]
    finally:
        window.close()


def test_plotter_context_menu_hide_block_updates_cell_pick_state(monkeypatch):
    window, parent_plotter = _make_window(monkeypatch, block_names=["BlockA", "BlockB"])

    try:
        monkeypatch.setattr(qt_window_module, "QMenu", _FakeMenu)
        _FakeMenu.selected_text = 'Hide "BlockA"'
        window._cell_pick_mode_enabled = True
        window._cell_pick_mode_active_cell = ("BlockA", 3)
        window._cell_pick_mode_visible_blocks = [("BlockA", object()), ("BlockB", object())]
        monkeypatch.setattr(
            window,
            "_resolve_cell_pick_mode_candidate",
            lambda: {"block_name": "BlockA", "cell_id": 3, "coordinates": (0.0, 0.0, 0.0), "highlight_mesh": None},
        )

        window._show_plotter_context_menu(QPoint(0, 0))

        assert ('Hide "BlockA"' in [action.text() for action in _FakeMenu.last_actions])
        assert parent_plotter.set_block_visibility_calls == [("BlockA", False)]
        assert [name for name, _block in window._cell_pick_mode_visible_blocks] == ["BlockB"]
        assert window._cell_pick_mode_active_cell is None
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
