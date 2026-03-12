import os

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QDockWidget, QWidget

from pyemsi.gui import main_window as main_window_module
from pyemsi.settings import SettingsManager


class _DummyExternalTerminalDock(QDockWidget):
    def __init__(self, parent=None) -> None:
        super().__init__("External Terminal", parent)


class _DummyKernelManager:
    def __init__(self) -> None:
        self.shutdown_calls = 0

    def shutdown_kernel(self) -> None:
        self.shutdown_calls += 1


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _stub_ipython_terminal(self) -> None:
    self._ipython_widget = QWidget(self._ipython_dock)
    self._kernel_manager = _DummyKernelManager()
    self._ipython_dock.setWidget(self._ipython_widget)


def test_main_window_restores_last_workspace_from_settings(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.set_global("app.last_workspace_path", str(workspace))
    manager.load_workspace(workspace)
    manager.set_local("workbench.window.dock_visibility", {"ipython": True})
    manager.save()

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert window.explorer.current_path == os.path.abspath(os.path.normpath(str(workspace)))
        assert window.windowTitle().endswith("workspace")
        assert not window._ipython_dock.isHidden()
    finally:
        window.close()


def test_main_window_close_event_persists_workspace_state(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)

    manager = SettingsManager(global_settings_path=global_settings_path)
    window = main_window_module.PyEmsiMainWindow(settings_manager=manager)
    window.show()
    window.resize(1200, 700)
    window._set_workspace_path(str(workspace))
    window._ipython_dock.show()
    window.closeEvent(QCloseEvent())

    reloaded = SettingsManager(global_settings_path=global_settings_path)
    reloaded.load_workspace(workspace)

    assert reloaded.get_effective("app.last_workspace_path") == os.path.abspath(os.path.normpath(str(workspace)))
    assert reloaded.get_local("workbench.window.geometry") is not None
    assert reloaded.get_effective("workbench.window.dock_visibility")["ipython"] is True
    assert window._kernel_manager.shutdown_calls == 1
