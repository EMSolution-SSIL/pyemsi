import json
import os

import pyemsi
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QDialog, QDockWidget, QToolButton, QWidget

from pyemsi.gui import main_window as main_window_module
from pyemsi.gui.femap_converter_dialog import FemapConverterDialogConfig
from pyemsi.gui.source_to_femap_dialog import SourceToFemapDialogConfig
from pyemsi.gui.update_checker import UpdateInfo
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
        self.calls.append(
            {
                "title": title,
                "cmd": cmd,
                "args": args or [],
                "cwd": cwd,
                "env": env,
            }
        )
        return _DummyXterm()

    def close_all_terminals(self) -> None:
        return None


class _DummyKernelManager:
    def __init__(self, initial_namespace=None) -> None:
        self.shutdown_calls = 0
        self.initial_namespace = dict(initial_namespace or {})
        self.pushed_namespaces = []

        class _DummyShell:
            def __init__(shell_self, owner) -> None:
                shell_self._owner = owner
                shell_self.reset_calls = 0

            def reset(shell_self, new_session=True) -> None:
                shell_self.reset_calls += 1

            def push(shell_self, namespace) -> None:
                shell_self._owner.pushed_namespaces.append(namespace)

        class _DummyKernel:
            def __init__(kernel_self, owner) -> None:
                kernel_self.shell = _DummyShell(owner)

        self.kernel = _DummyKernel(self)

    def shutdown_kernel(self) -> None:
        self.shutdown_calls += 1


class _DummyIPythonWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.reset_calls = []

    def reset(self, clear=False) -> None:
        self.reset_calls.append(clear)


class _DummyUpdateChecker:
    def __init__(self, settings_manager, parent=None) -> None:
        self.settings_manager = settings_manager
        self.parent = parent
        self.check_finished = _DummySignal()
        self.calls = []

    def check_for_updates(self, manual=False) -> bool:
        self.calls.append(manual)
        return True


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _stub_ipython_terminal(self) -> None:
    self._ipython_widget = _DummyIPythonWidget(self._ipython_dock)
    self._kernel_manager = _DummyKernelManager(self._build_namespace())
    self._ipython_dock.setWidget(self._ipython_widget)


def test_main_window_does_not_restore_workspace_from_global_settings(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.add_recent_folder(workspace)
    manager.set_global("workbench.window.geometry", "Zm9v")
    manager.save()

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert window.explorer.current_path is None
        assert window.windowTitle() == "pyemsi"
        assert window.should_show_maximized_on_launch() is False
    finally:
        window.close()


def test_main_window_close_event_persists_workspace_state(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    manager = SettingsManager(global_settings_path=global_settings_path)
    window = main_window_module.PyEmsiMainWindow(settings_manager=manager)
    window.show()
    window.resize(1200, 700)
    window._set_workspace_path(str(workspace))
    window._ensure_ipython_terminal()
    window.closeEvent(QCloseEvent())

    reloaded = SettingsManager(global_settings_path=global_settings_path)
    reloaded.load_workspace(workspace)
    global_payload = json.loads(global_settings_path.read_text(encoding="utf-8"))
    local_payload = json.loads((workspace / ".pyemsi" / "workspace.json").read_text(encoding="utf-8"))

    assert reloaded.get_local("workbench.explorer.root_path") == os.path.abspath(os.path.normpath(str(workspace)))
    assert reloaded.get_global("workbench.window.geometry") is not None
    assert reloaded.get_global("workbench.window.state") is not None
    assert "layout" not in local_payload.get("workbench", {})
    assert "window" not in local_payload.get("workbench", {})
    assert "dock_visibility" not in global_payload.get("workbench", {}).get("window", {})
    assert "maximized" not in global_payload.get("workbench", {}).get("window", {})
    assert window._kernel_manager.shutdown_calls == 1


def test_main_window_close_event_closes_tabs_before_shutdown(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    close_calls = []

    def _close_all_tabs():
        close_calls.append("tabs")
        return True

    window._container.close_all_tabs = _close_all_tabs
    window._ensure_ipython_terminal()
    window.closeEvent(QCloseEvent())

    assert close_calls == ["tabs"]
    assert window._kernel_manager.shutdown_calls == 1


def test_main_window_close_event_aborts_when_tab_close_is_canceled(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )

    def _close_all_tabs():
        return False

    window._container.close_all_tabs = _close_all_tabs
    event = QCloseEvent()
    window.closeEvent(event)

    assert not event.isAccepted()
    assert window._kernel_manager is None


def test_main_window_defers_ipython_terminal_until_first_use(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert window._ipython_widget is None
        assert window._kernel_manager is None

        window.push_to_namespace(answer=42)

        assert window._kernel_manager is None

        window._ensure_ipython_terminal()

        assert isinstance(window._ipython_widget, _DummyIPythonWidget)
        assert isinstance(window._kernel_manager, _DummyKernelManager)
        assert window._kernel_manager.initial_namespace["pyemsi"] is pyemsi
        assert window._kernel_manager.initial_namespace["answer"] == 42
        assert window._kernel_manager.pushed_namespaces == []
    finally:
        window.close()


def test_main_window_view_action_initializes_ipython_terminal(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._ipython_dock.hide()
        _app().processEvents()

        assert window._kernel_manager is None

        window._ipython_dock.toggleViewAction().trigger()
        _app().processEvents()

        assert isinstance(window._ipython_widget, _DummyIPythonWidget)
        assert isinstance(window._kernel_manager, _DummyKernelManager)
    finally:
        window.close()


def test_main_window_open_recent_menu_tracks_unique_folders(tmp_path, monkeypatch):
    _app()
    workspace_a = tmp_path / "workspace_a"
    workspace_b = tmp_path / "workspace_b"
    workspace_a.mkdir()
    workspace_b.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

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
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

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
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert window._explorer_dock.objectName() == "explorer_dock"
        assert window._ipython_dock.objectName() == "ipython_terminal_dock"
        assert window._external_terminal_dock.objectName() == "external_terminal_dock"
    finally:
        window.close()


def test_main_window_file_menu_includes_settings_submenu_between_separators(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        file_actions = window._file_menu.actions()
        action_texts = [action.text() for action in file_actions if not action.isSeparator()]
        converters_actions = window._converters_menu.actions()
        help_actions = window._help_menu.actions()

        assert file_actions[0].text() == "Open &Folder..."
        assert file_actions[1].text() == "Open &Recent"
        assert file_actions[2].isSeparator()
        assert "&Converters" not in action_texts
        assert "Convert &FEMAP" not in action_texts
        assert "&Field Plot" in action_texts
        assert "&Output Plot" in action_texts
        assert "&Settings" in action_texts
        assert "&Save" in action_texts
        assert action_texts.index("&Field Plot") < action_texts.index("&Save")
        assert action_texts.index("&Output Plot") < action_texts.index("&Save")

        assert converters_actions[0] is window._open_femap_converter_action
        assert converters_actions[1].isSeparator()
        assert converters_actions[2] is window._open_atlas_to_femap_action
        assert converters_actions[3] is window._open_unv_to_femap_action

        assert help_actions[0] is window._open_documentation_action
        assert help_actions[1] is window._check_for_updates_action
        assert help_actions[2] is window._open_releases_action
        assert help_actions[3] is window._report_issue_action
        assert help_actions[4].isSeparator()
        assert help_actions[5] is window._open_license_action
        assert help_actions[6].isSeparator()
        assert help_actions[7] is window._open_about_action

        menu_titles = [action.text() for action in window.menuBar().actions()]
        assert "&Converters" in menu_titles
        assert "&Help" in menu_titles
        assert menu_titles[-2] == "&Converters"
        assert menu_titles[-1] == "&Help"
    finally:
        window.close()


def test_main_window_help_actions_open_expected_urls(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    opened_urls = []
    monkeypatch.setattr(
        main_window_module.QDesktopServices,
        "openUrl",
        lambda url: opened_urls.append(url.toString()) or True,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._open_documentation_action.trigger()
        window._open_releases_action.trigger()
        window._report_issue_action.trigger()

        assert opened_urls == [
            "https://emsolution-ssil.github.io/pyemsi/",
            "https://github.com/EMSolution-SSIL/pyemsi/releases",
            "https://github.com/EMSolution-SSIL/pyemsi/issues",
        ]
    finally:
        window.close()


def test_main_window_schedules_startup_update_check_once(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"
    timer_calls = []

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module, "UpdateChecker", _DummyUpdateChecker)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(
        main_window_module.QTimer,
        "singleShot",
        lambda interval, callback: timer_calls.append((interval, callback)),
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert len(timer_calls) == 1
        assert timer_calls[0][0] == 0

        timer_calls[0][1]()

        assert window._update_checker.calls == [False]
    finally:
        window.close()


def test_main_window_manual_update_action_uses_checker(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module, "UpdateChecker", _DummyUpdateChecker)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(main_window_module.QTimer, "singleShot", lambda interval, callback: None)

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._check_for_updates_action.trigger()

        assert window._update_checker.calls == [True]
    finally:
        window.close()


def test_main_window_manual_update_check_shows_latest_message(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"
    info_calls = []

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module, "UpdateChecker", _DummyUpdateChecker)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(main_window_module.QTimer, "singleShot", lambda interval, callback: None)
    monkeypatch.setattr(
        main_window_module.QMessageBox,
        "information",
        lambda parent, title, text: info_calls.append((parent, title, text)),
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._update_checker.check_finished.emit(
            UpdateInfo(available=False, current_version="0.3.0", latest_version="0.3.0"),
            True,
        )

        assert info_calls == [(window, "No Updates Available", "You are using the latest version.")]
    finally:
        window.close()


def test_main_window_manual_update_check_shows_error_message(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"
    warning_calls = []

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module, "UpdateChecker", _DummyUpdateChecker)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(main_window_module.QTimer, "singleShot", lambda interval, callback: None)
    monkeypatch.setattr(
        main_window_module.QMessageBox,
        "warning",
        lambda parent, title, text: warning_calls.append((parent, title, text)),
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._update_checker.check_finished.emit(
            UpdateInfo(available=False, current_version="0.3.0", error="network failure"),
            True,
        )

        assert warning_calls == [(window, "Update Check Failed", "Could not check for updates. Please try again later.")]
    finally:
        window.close()


def test_main_window_update_available_path_opens_release_url(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"
    dialog_calls = []
    opened_urls = []

    class _AcceptedUpdateDialog:
        DialogCode = QDialog.DialogCode

        def __init__(self, update_info, parent=None) -> None:
            dialog_calls.append((update_info, parent))

        def exec(self) -> int:
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module, "UpdateChecker", _DummyUpdateChecker)
    monkeypatch.setattr(main_window_module, "UpdateAvailableDialog", _AcceptedUpdateDialog)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(main_window_module.QTimer, "singleShot", lambda interval, callback: None)
    monkeypatch.setattr(
        main_window_module.QDesktopServices,
        "openUrl",
        lambda url: opened_urls.append(url.toString()) or True,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        info = UpdateInfo(
            available=True,
            current_version="0.3.0",
            latest_version="0.3.1",
            release_url="https://github.com/EMSolution-SSIL/pyemsi/releases/tag/0.3.1",
        )
        window._update_checker.check_finished.emit(info, True)

        assert dialog_calls == [(info, window)]
        assert opened_urls == ["https://github.com/EMSolution-SSIL/pyemsi/releases/tag/0.3.1"]
    finally:
        window.close()


def test_main_window_help_license_action_opens_license_as_text(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"
    license_path = tmp_path / "LICENSE"
    license_path.write_text("GPL", encoding="utf-8")

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        opened = []
        monkeypatch.setattr(window, "_resolve_license_path", lambda: license_path)
        window._container.open_file = lambda path, category=None: opened.append((path, category))

        window._open_license_action.trigger()

        assert opened == [(os.fspath(license_path), "text")]
    finally:
        window.close()


def test_main_window_help_about_action_shows_version_and_company_info(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    about_calls = []
    monkeypatch.setattr(
        main_window_module.QMessageBox,
        "about",
        lambda parent, title, text: about_calls.append((parent, title, text)),
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._open_about_action.trigger()

        assert len(about_calls) == 1
        parent, title, text = about_calls[0]
        assert parent is window
        assert title == "About pyemsi"
        assert f"Version: {pyemsi.__version__}" in text
        assert "Science Solutions International Lab, Inc. (SSIL)" in text
        assert "Email: em_solution@ssil.co.jp" in text
        assert "Copyright (c) 2026 SSIL All rights reserved." in text
    finally:
        window.close()


def test_main_window_file_toolbar_contains_requested_actions_and_dropdowns(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        toolbar = window._file_toolbar
        action_order = []

        assert toolbar.objectName() == "file_toolbar"
        assert window.toolBarArea(toolbar) == main_window_module.Qt.ToolBarArea.TopToolBarArea
        assert toolbar.toolButtonStyle() == main_window_module.Qt.ToolButtonStyle.ToolButtonIconOnly

        for action in toolbar.actions():
            if action.isSeparator():
                action_order.append("separator")
                continue

            widget = toolbar.widgetForAction(action)
            if widget is window._open_recent_tool_button:
                action_order.append("open_recent")
                continue
            if widget is window._settings_tool_button:
                action_order.append("settings")
                continue

            if action is window._open_folder_action:
                action_order.append("open_folder")
            elif action is window._open_femap_converter_action:
                action_order.append("convert_femap")
            elif action is window._open_field_plot_action:
                action_order.append("field_plot")
            elif action is window._open_emsolution_output_plot_action:
                action_order.append("output_plot")

        assert action_order == [
            "open_folder",
            "open_recent",
            "separator",
            "convert_femap",
            "field_plot",
            "output_plot",
            "separator",
            "settings",
        ]
        assert window._open_recent_tool_button.objectName() == "open_recent_tool_button"
        assert window._open_recent_tool_button.menu() is window._recent_menu
        assert window._open_recent_tool_button.popupMode() == QToolButton.ToolButtonPopupMode.InstantPopup
        assert window._settings_tool_button.objectName() == "settings_tool_button"
        assert window._settings_tool_button.menu() is window._settings_menu
        assert window._settings_tool_button.popupMode() == QToolButton.ToolButtonPopupMode.InstantPopup
    finally:
        window.close()


def test_main_window_source_to_femap_actions_track_workspace_state(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert not window._open_atlas_to_femap_action.isEnabled()
        assert not window._open_unv_to_femap_action.isEnabled()

        window._set_workspace_path(str(workspace))

        assert window._open_atlas_to_femap_action.isEnabled()
        assert window._open_unv_to_femap_action.isEnabled()

        window.close_workspace(restart_kernel=False)

        assert not window._open_atlas_to_femap_action.isEnabled()
        assert not window._open_unv_to_femap_action.isEnabled()
    finally:
        window.close()


def test_main_window_femap_converter_action_tracks_workspace_state(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert not window._open_femap_converter_action.isEnabled()

        window._set_workspace_path(str(workspace))

        assert window._open_femap_converter_action.isEnabled()

        window.close_workspace(restart_kernel=False)

        assert not window._open_femap_converter_action.isEnabled()
    finally:
        window.close()


def test_main_window_field_plot_action_tracks_workspace_state(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert not window._open_field_plot_action.isEnabled()

        window._set_workspace_path(str(workspace))

        assert window._open_field_plot_action.isEnabled()

        window.close_workspace(restart_kernel=False)

        assert not window._open_field_plot_action.isEnabled()
    finally:
        window.close()


def test_main_window_emsolution_output_plot_action_tracks_workspace_state(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert not window._open_emsolution_output_plot_action.isEnabled()

        window._set_workspace_path(str(workspace))

        assert window._open_emsolution_output_plot_action.isEnabled()

        window.close_workspace(restart_kernel=False)

        assert not window._open_emsolution_output_plot_action.isEnabled()
    finally:
        window.close()


def test_main_window_opens_field_plot_dialog(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"
    calls = []

    class _FakeFieldPlotDialog:
        def __init__(self, settings_manager, browse_dir_getter=None, parent=None) -> None:
            calls.append(
                {
                    "settings_manager": settings_manager,
                    "browse_dir": browse_dir_getter() if callable(browse_dir_getter) else None,
                    "parent": parent,
                }
            )

        def show(self) -> None:
            calls[-1]["show"] = True

        def raise_(self) -> None:
            calls[-1]["raise"] = True

        def activateWindow(self) -> None:
            calls[-1]["activate"] = True

        def setAttribute(self, attribute, value) -> None:
            calls[-1]["set_attribute"] = (attribute, value)

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(main_window_module, "FieldPlotBuilderDialog", _FakeFieldPlotDialog)

    manager = SettingsManager(global_settings_path=global_settings_path)
    window = main_window_module.PyEmsiMainWindow(settings_manager=manager)
    try:
        window._set_workspace_path(str(workspace))

        window._open_field_plot_dialog()
        window._open_field_plot_dialog()

        assert len(calls) == 2
        for call in calls:
            assert call["settings_manager"] is manager
            assert call["browse_dir"] == os.path.abspath(os.path.normpath(str(workspace)))
            assert call["parent"] is window
            assert call["show"] is True
            assert call["raise"] is True
            assert call["activate"] is True
            assert call["set_attribute"] == (main_window_module.Qt.WidgetAttribute.WA_DeleteOnClose, True)
    finally:
        window.close()


def test_main_window_emsolution_output_plot_action_warns_on_missing_file(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"
    warnings = []

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(main_window_module.QMessageBox, "warning", lambda *args: warnings.append(args[1:]))

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._set_workspace_path(str(workspace))

        window._open_emsolution_output_plot_dialog()

        assert warnings
        assert warnings[0][0] == "Missing EMSolution Output"
    finally:
        window.close()


def test_main_window_opens_emsolution_output_plot_dialog(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    output_path = workspace / "output.json"
    output_path.write_text("{}", encoding="utf-8")
    global_settings_path = tmp_path / "config" / "settings.json"
    calls = {}

    class _FakeEMSolutionOutputPlotBuilderDialog:
        def __init__(self, source, settings_manager=None, parent=None) -> None:
            calls["source"] = source
            calls["settings_manager"] = settings_manager
            calls["parent"] = parent

        def setAttribute(self, attr, value) -> None:
            calls["attribute"] = (attr, value)

        def show(self) -> None:
            calls["show"] = True

        def raise_(self) -> None:
            calls["raise"] = True

        def activateWindow(self) -> None:
            calls["activate"] = True

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(
        main_window_module,
        "EMSolutionOutputPlotBuilderDialog",
        _FakeEMSolutionOutputPlotBuilderDialog,
    )

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._set_workspace_path(str(workspace))

        window._open_emsolution_output_plot_dialog()

        assert calls["source"] == os.path.abspath(os.path.normpath(str(output_path)))
        assert calls["settings_manager"] is window.settings_manager
        assert calls["parent"] is window
        assert calls["show"] is True
        assert calls["raise"] is True
        assert calls["activate"] is True
    finally:
        window.close()


def test_main_window_launches_femap_converter_in_external_terminal(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    input_dir = workspace / "model"
    input_dir.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    config = FemapConverterDialogConfig(
        workspace_path=os.path.abspath(os.path.normpath(str(workspace))),
        input_dir=os.path.abspath(os.path.normpath(str(input_dir))),
        output_dir=".pyemsi",
        output_name="transient",
        input_control_file=None,
        force_2d=True,
        ascii_mode=False,
        mesh="post_geom",
        magnetic=None,
        current=None,
        electric=None,
        force=None,
        force_J_B=None,
        heat=None,
        displacement="disp",
    )

    class _AcceptedDialog:
        DialogCode = QDialog.DialogCode

        def __init__(self, settings_manager, parent=None) -> None:
            self._config = config

        def exec(self) -> int:
            return QDialog.DialogCode.Accepted

        def config(self):
            return self._config

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module, "FemapConverterDialog", _AcceptedDialog)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.load_workspace(workspace)
    window = main_window_module.PyEmsiMainWindow(settings_manager=manager)
    try:
        window._open_femap_converter_dialog()

        assert len(window._external_terminal_dock.calls) == 1
        launch_call = window._external_terminal_dock.calls[0]
        assert launch_call["title"] == "FemapConverter - transient"
        assert launch_call["cwd"] == os.path.abspath(os.path.normpath(str(input_dir)))
        assert launch_call["args"][0].endswith("run_femap_converter.py")
        assert launch_call["args"][1:] and launch_call["args"][1] == "--config"
        assert manager.get_local("tools.femap_converter.output_name") == "transient"
        assert len(window._temp_converter_configs) == 1
    finally:
        window.close()


def test_main_window_launches_source_to_femap_converter_in_external_terminal(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    input_dir = workspace / "model"
    input_dir.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"

    config = SourceToFemapDialogConfig(
        source_format="atlas",
        input_dir=os.path.abspath(os.path.normpath(str(input_dir))),
        overwrite=False,
        mesh="post_geom.atl",
        mesh_output="exports\\post_geom_custom.neu",
        displacement=None,
        displacement_output=None,
        magnetic=None,
        magnetic_output=None,
        current=None,
        current_output=None,
        electric="electric.atl",
        electric_output="electric_custom.neu",
        force=None,
        force_output=None,
        force_J_B=None,
        force_J_B_output=None,
        heat=None,
        heat_output=None,
    )

    class _AcceptedDialog:
        DialogCode = QDialog.DialogCode

        def __init__(self, source_format, settings_manager, parent=None) -> None:
            self._config = config

        def exec(self) -> int:
            return QDialog.DialogCode.Accepted

        def config(self):
            return self._config

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module, "SourceToFemapDialog", _AcceptedDialog)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )

    manager = SettingsManager(global_settings_path=global_settings_path)
    manager.load_workspace(workspace)
    window = main_window_module.PyEmsiMainWindow(settings_manager=manager)
    try:
        window._open_atlas_to_femap_dialog()

        assert len(window._external_terminal_dock.calls) == 1
        launch_call = window._external_terminal_dock.calls[0]
        assert launch_call["title"] == "Atlas -> FEMAP - post_geom.atl"
        assert launch_call["cwd"] == os.path.abspath(os.path.normpath(str(input_dir)))
        assert launch_call["args"][0].endswith("run_source_to_femap.py")
        assert launch_call["args"][1:] and launch_call["args"][1] == "--config"
        assert manager.get_local("tools.atlas_to_femap.mesh") == "post_geom.atl"
        assert manager.get_local("tools.atlas_to_femap.mesh_output") == "exports\\post_geom_custom.neu"
        assert len(window._temp_converter_configs) == 1
    finally:
        window.close()


def test_main_window_global_settings_action_tracks_file_availability(tmp_path, monkeypatch):
    _app()
    global_settings_path = tmp_path / "config" / "settings.json"
    opened_paths = []

    def _capture_open_file(self, path):
        opened_paths.append(path)
        return QWidget()

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(main_window_module.SplitContainer, "open_file", _capture_open_file)

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert window._open_global_settings_action.isEnabled()
        assert global_settings_path.is_file()

        window._open_global_settings_action.trigger()

        assert opened_paths == [os.path.abspath(os.path.normpath(str(global_settings_path)))]
    finally:
        window.close()


def test_main_window_workspace_settings_action_tracks_workspace_state(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"
    local_settings_path = workspace / ".pyemsi" / "workspace.json"
    opened_paths = []

    def _capture_open_file(self, path):
        opened_paths.append(path)
        return QWidget()

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(main_window_module.SplitContainer, "open_file", _capture_open_file)

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        assert not window._open_workspace_settings_action.isEnabled()

        window._set_workspace_path(str(workspace))

        assert not window._open_workspace_settings_action.isEnabled()

        local_settings_path.parent.mkdir(parents=True)
        local_settings_path.write_text('{"schemaVersion": 1}\n', encoding="utf-8")
        window._update_settings_actions()

        assert window._open_workspace_settings_action.isEnabled()

        window._open_workspace_settings_action.trigger()

        assert opened_paths == [os.path.abspath(os.path.normpath(str(local_settings_path)))]
    finally:
        window.close()


def test_main_window_workspace_settings_action_stays_disabled_without_local_file(tmp_path, monkeypatch):
    _app()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    global_settings_path = tmp_path / "config" / "settings.json"
    opened_paths = []

    def _capture_open_file(self, path):
        opened_paths.append(path)
        return QWidget()

    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(
        main_window_module.PyEmsiMainWindow,
        "_setup_ipython_terminal",
        _stub_ipython_terminal,
    )
    monkeypatch.setattr(main_window_module.SplitContainer, "open_file", _capture_open_file)

    window = main_window_module.PyEmsiMainWindow(
        settings_manager=SettingsManager(global_settings_path=global_settings_path)
    )
    try:
        window._set_workspace_path(str(workspace))

        assert not window._open_workspace_settings_action.isEnabled()

        window._open_workspace_settings_action.trigger()

        assert opened_paths == []
    finally:
        window.close()
