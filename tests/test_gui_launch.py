"""Tests for gui.launch() – splash screen ordering and robustness."""

from __future__ import annotations

import pyemsi.gui as gui_module
from pyemsi.gui import main_window as main_window_module
from PySide6.QtWidgets import QApplication, QSplashScreen, QWidget


# ---------------------------------------------------------------------------
# Helpers shared across tests
# ---------------------------------------------------------------------------


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakeSplash:
    """Records calls to finish() without touching a real QSplashScreen."""

    def __init__(self) -> None:
        self.finish_calls: list = []

    def finish(self, widget) -> None:
        self.finish_calls.append(widget)


class _FakeWindow(QWidget):
    """Minimal stand-in for PyEmsiMainWindow – no heavy Qt subsystems."""

    def setWindowTitle(self, title: str) -> None:  # noqa: N802
        pass

    def should_show_maximized_on_launch(self) -> bool:
        return False

    def push_to_namespace(self, **kwargs) -> None:
        pass

    @property
    def container(self):
        return None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_splash_shown_before_window_constructed(monkeypatch):
    """_create_splash must be called before PyEmsiMainWindow() runs."""
    _ensure_app()
    call_log: list[str] = []
    splash = _FakeSplash()

    def _mock_create_splash(app):
        call_log.append("splash")
        return splash

    class _RecordingWindow(_FakeWindow):
        def __init__(self, parent=None):
            super().__init__(parent)
            call_log.append("window")

    monkeypatch.setattr(gui_module, "_create_splash", _mock_create_splash)
    monkeypatch.setattr(main_window_module, "PyEmsiMainWindow", _RecordingWindow)
    monkeypatch.setattr(gui_module, "_exec_app", lambda app: None)
    monkeypatch.setattr(gui_module, "_window", None)
    monkeypatch.setattr(gui_module, "_app", None)

    gui_module.launch()

    assert "splash" in call_log and "window" in call_log
    assert call_log.index("splash") < call_log.index("window"), (
        "Splash must appear before PyEmsiMainWindow is constructed"
    )


def test_splash_finished_after_window_shown(monkeypatch):
    """splash.finish() must be called after window.show()."""
    _ensure_app()
    call_log: list[str] = []
    splash = _FakeSplash()

    original_finish = splash.finish

    def _recording_finish(widget) -> None:
        call_log.append("finish")
        original_finish(widget)

    splash.finish = _recording_finish

    def _mock_create_splash(app):
        return splash

    class _RecordingWindow(_FakeWindow):
        def show(self) -> None:
            call_log.append("show")
            super().show()

    monkeypatch.setattr(gui_module, "_create_splash", _mock_create_splash)
    monkeypatch.setattr(main_window_module, "PyEmsiMainWindow", _RecordingWindow)
    monkeypatch.setattr(gui_module, "_exec_app", lambda app: None)
    monkeypatch.setattr(gui_module, "_window", None)
    monkeypatch.setattr(gui_module, "_app", None)

    gui_module.launch()

    assert "show" in call_log and "finish" in call_log
    assert call_log.index("show") < call_log.index("finish"), "splash.finish() must be called after window.show()"


def test_splash_finished_with_window_instance(monkeypatch):
    """splash.finish() receives the main window as its argument."""
    _ensure_app()
    splash = _FakeSplash()

    def _mock_create_splash(app):
        return splash

    class _TrackedWindow(_FakeWindow):
        pass

    monkeypatch.setattr(gui_module, "_create_splash", _mock_create_splash)
    monkeypatch.setattr(main_window_module, "PyEmsiMainWindow", _TrackedWindow)
    monkeypatch.setattr(gui_module, "_exec_app", lambda app: None)
    monkeypatch.setattr(gui_module, "_window", None)
    monkeypatch.setattr(gui_module, "_app", None)

    gui_module.launch()

    assert len(splash.finish_calls) == 1
    assert isinstance(splash.finish_calls[0], _TrackedWindow)


def test_launch_handles_no_splash(monkeypatch):
    """launch() completes without error when _create_splash returns None."""
    _ensure_app()

    def _mock_create_splash(app):
        return None

    class _FakeWindow2(_FakeWindow):
        pass

    monkeypatch.setattr(gui_module, "_create_splash", _mock_create_splash)
    monkeypatch.setattr(main_window_module, "PyEmsiMainWindow", _FakeWindow2)
    monkeypatch.setattr(gui_module, "_exec_app", lambda app: None)
    monkeypatch.setattr(gui_module, "_window", None)
    monkeypatch.setattr(gui_module, "_app", None)

    gui_module.launch()  # must not raise

    assert gui_module._window is not None


def test_create_splash_returns_splash_screen():
    """Integration: _create_splash uses the on-disk icon and returns a QSplashScreen."""
    app = _ensure_app()
    splash = gui_module._create_splash(app)
    try:
        assert splash is not None, "_create_splash returned None – is PySide6.QtSvg installed and Icon.svg present?"
        assert isinstance(splash, QSplashScreen)
    finally:
        if splash is not None:
            splash.close()
