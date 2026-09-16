import os

from PySide6.QtWidgets import QApplication, QDialog, QDockWidget, QWidget

from pyemsi.gui import main_window as main_window_module
from pyemsi.gui.emsolution_run_settings_dialog import EMSolutionRunSettingsDialogConfig
from pyemsi.settings import SettingsManager


class _DummySignal:
    def __init__(self) -> None:
        self._callbacks = []

    def connect(self, callback) -> None:
        self._callbacks.append(callback)

    def emit(self, *args) -> None:
        for callback in list(self._callbacks):
            callback(*args)


class _DummyXterm:
    def __init__(self) -> None:
        self.processFinished = _DummySignal()


class _DummyExternalTerminalDock(QDockWidget):
    def __init__(self, parent=None) -> None:
        super().__init__("External Terminal", parent)
        self.calls = []

    def add_terminal(self, title="Terminal", cmd=None, args=None, cwd=None, env=None):
        self.calls.append({"title": title, "cmd": cmd, "args": args or [], "cwd": cwd, "env": env})
        return _DummyXterm()

    def close_all_terminals(self) -> None:
        return None


class _DummyKernelManager:
    def __init__(self, initial_namespace=None) -> None:
        self.shutdown_calls = 0

    def shutdown_kernel(self) -> None:
        self.shutdown_calls += 1


class _DummyIPythonWidget(QWidget):
    pass


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _stub_ipython_terminal(self) -> None:
    self._ipython_widget = _DummyIPythonWidget(self._ipython_dock)
    self._kernel_manager = _DummyKernelManager()
    self._ipython_dock.setWidget(self._ipython_widget)


def _make_window(tmp_path, monkeypatch):
    global_settings_path = tmp_path / "config" / "settings.json"
    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)
    manager = SettingsManager(global_settings_path=global_settings_path)
    return main_window_module.PyEmsiMainWindow(settings_manager=manager), manager


def test_settings_menu_includes_emsolution_run_settings_action(tmp_path, monkeypatch):
    _app()
    window, _manager = _make_window(tmp_path, monkeypatch)
    try:
        settings_actions = window._settings_menu.actions()
        assert window._open_emsolution_run_settings_action in settings_actions
        assert window._open_emsolution_run_settings_action.text() == "&EMSolution Run Settings..."
    finally:
        window.close()


def test_opening_emsolution_run_settings_dialog_persists_accepted_config(tmp_path, monkeypatch):
    _app()
    window, manager = _make_window(tmp_path, monkeypatch)
    config = EMSolutionRunSettingsDialogConfig(
        backend="executable",
        executable_path=str(tmp_path / "EMSolution.exe"),
        run_style="window",
    )

    class _AcceptedDialog:
        DialogCode = QDialog.DialogCode

        def __init__(self, settings_manager, parent=None) -> None:
            pass

        def exec(self) -> int:
            return QDialog.DialogCode.Accepted

        def config(self):
            return config

    monkeypatch.setattr(main_window_module, "EMSolutionRunSettingsDialog", _AcceptedDialog)

    try:
        window._open_emsolution_run_settings_dialog()

        assert manager.get_global("tools.emsolution_run.backend") == "executable"
        assert manager.get_global("tools.emsolution_run.executable_path") == os.path.abspath(
            os.path.normpath(str(tmp_path / "EMSolution.exe"))
        )
        assert manager.get_global("tools.emsolution_run.run_style") == "window"

        reloaded = SettingsManager(global_settings_path=manager.global_settings_path)
        assert reloaded.get_global("tools.emsolution_run.backend") == "executable"
    finally:
        window.close()


def test_canceling_emsolution_run_settings_dialog_does_not_persist(tmp_path, monkeypatch):
    _app()
    window, manager = _make_window(tmp_path, monkeypatch)

    class _RejectedDialog:
        DialogCode = QDialog.DialogCode

        def __init__(self, settings_manager, parent=None) -> None:
            pass

        def exec(self) -> int:
            return QDialog.DialogCode.Rejected

        def config(self):
            raise AssertionError("config() should not be called when the dialog is rejected")

    monkeypatch.setattr(main_window_module, "EMSolutionRunSettingsDialog", _RejectedDialog)

    try:
        window._open_emsolution_run_settings_dialog()

        assert manager.get_global("tools.emsolution_run.backend") is None
    finally:
        window.close()
