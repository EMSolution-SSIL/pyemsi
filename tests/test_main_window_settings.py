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


def test_main_window_does_not_restore_workspace_from_global_settings(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.add_recent_folder(workspace)
    manager.load_workspace(workspace)
    manager.set_local("workbench.window.dock_visibility", {"ipython": True})
    manager.save()

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert window.explorer.current_path is None
        assert window.windowTitle() == "pyemsi"
        assert window._ipython_dock.isHidden()
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

    assert reloaded.get_local("workbench.window.geometry") is not None
    assert reloaded.get_effective("workbench.window.dock_visibility")["ipython"] is True
    assert window._kernel_manager.shutdown_calls == 1


def test_main_window_open_recent_menu_tracks_unique_folders(tmp_path, monkeypatch):
    _app()
    workspace_a = tmp_path / "workspace_a"
    workspace_b = tmp_path / "workspace_b"
    workspace_a.mkdir()
    workspace_b.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._set_workspace_path(str(workspace_a))
        window._set_workspace_path(str(workspace_b))
        window._set_workspace_path(str(workspace_a))

        recent_actions = window._recent_menu.actions()

        assert recent_actions[0].text() == os.path.abspath(os.path.normpath(str(workspace_a)))
        assert recent_actions[1].text() == os.path.abspath(os.path.normpath(str(workspace_b)))
        assert recent_actions[-2].isSeparator()
        assert recent_actions[-1].text() == "Clear Recently Opened"
    finally:
        window.close()


def test_main_window_can_clear_recent_folders(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.add_recent_folder(workspace)
    manager.save()

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._clear_recent_folders()

        reloaded = SettingsManager(global_settings_path=global_settings_path)
        recent_actions = window._recent_menu.actions()

        assert reloaded.get_global("app.recent_folders") == []
        assert len(recent_actions) == 2
        assert recent_actions[0].isSeparator()
        assert recent_actions[1].text() == "Clear Recently Opened"
        assert not recent_actions[1].isEnabled()
    finally:
        window.close()


def test_main_window_assigns_stable_dock_object_names(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert window._explorer_dock.objectName() == "explorer_dock"
        assert window._ipython_dock.objectName() == "ipython_terminal_dock"
        assert window._external_terminal_dock.objectName() == "external_terminal_dock"
    finally:
        window.close()
