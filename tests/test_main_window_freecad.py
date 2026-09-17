from __future__ import annotations

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QDockWidget, QMessageBox, QTabWidget, QWidget

from pyemsi.gui import freecad_session as session_module
from pyemsi.gui import main_window as main_window_module
from pyemsi.settings import SettingsManager


class _DummyExternalTerminalDock(QDockWidget):
    def __init__(self, parent=None) -> None:
        super().__init__("External Terminal", parent)

    def add_terminal(self, *args, **kwargs):
        return None

    def close_all_terminals(self) -> None:
        return None


class _DummyKernelManager:
    def shutdown_kernel(self) -> None:
        return None


def _stub_ipython_terminal(self) -> None:
    self._ipython_widget = QWidget(self._ipython_dock)
    self._kernel_manager = _DummyKernelManager()
    self._ipython_dock.setWidget(self._ipython_widget)


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _make_window(tmp_path, monkeypatch):
    _app()
    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)
    manager = SettingsManager(global_settings_path=tmp_path / "config" / "settings.json")
    return main_window_module.PyEmsiMainWindow(settings_manager=manager)


class _FakeSession:
    def __init__(self, modified, *, initialized=True, save_error=None):
        self._modified = modified
        self.is_initialized = initialized
        self.saved: list[str] = []
        self.exit_prepared = 0
        self.save_error = save_error

    def modified_documents(self):
        return list(self._modified)

    def save_document(self, name):
        if self.save_error is not None:
            raise self.save_error
        self.saved.append(name)

    def prepare_for_application_exit(self):
        self.exit_prepared += 1


def _install(monkeypatch, session):
    monkeypatch.setattr(session_module, "peek_freecad_session", lambda: session)


def test_close_without_freecad_session_proceeds(tmp_path, monkeypatch):
    _install(monkeypatch, None)
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
    finally:
        window.deleteLater()


def test_close_with_clean_documents_prepares_session_for_exit(tmp_path, monkeypatch):
    session = _FakeSession([])
    _install(monkeypatch, session)
    asked: list[str] = []
    monkeypatch.setattr(
        main_window_module.QMessageBox,
        "question",
        lambda *a, **k: asked.append(a[2]) or QMessageBox.StandardButton.Discard,
    )
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
        assert asked == []
        assert session.exit_prepared == 1
    finally:
        window.deleteLater()


def test_close_prompts_per_modified_document_and_saves_on_save(tmp_path, monkeypatch):
    session = _FakeSession([("Motor", str(tmp_path / "Motor.FCStd")), ("Coil", "")])
    _install(monkeypatch, session)
    asked: list[str] = []
    monkeypatch.setattr(
        main_window_module.QMessageBox,
        "question",
        lambda *a, **k: asked.append(a[2]) or QMessageBox.StandardButton.Save,
    )
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
        assert asked == ["Save changes to Motor.FCStd?", "Save changes to Coil?"]
        assert session.saved == ["Motor", "Coil"]
        assert session.exit_prepared == 1
    finally:
        window.deleteLater()


def test_close_cancel_keeps_window_open_and_skips_cleanup(tmp_path, monkeypatch):
    session = _FakeSession([("Motor", str(tmp_path / "Motor.FCStd"))])
    _install(monkeypatch, session)
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Cancel)
    close_all_calls: list[int] = []
    window = _make_window(tmp_path, monkeypatch)
    monkeypatch.setattr(window._container, "close_all_tabs", lambda: close_all_calls.append(1) or True)
    try:
        assert window.close() is False
        assert close_all_calls == []
        assert session.exit_prepared == 0
    finally:
        window.deleteLater()


def test_close_discard_does_not_save(tmp_path, monkeypatch):
    session = _FakeSession([("Motor", str(tmp_path / "Motor.FCStd"))])
    _install(monkeypatch, session)
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Discard)
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
        assert session.saved == []
    finally:
        window.deleteLater()


def test_close_save_failure_warns_and_cancels(tmp_path, monkeypatch):
    session = _FakeSession(
        [("Motor", "")],
        save_error=session_module.FreeCADDocumentError("FreeCAD document 'Motor' has never been saved."),
    )
    _install(monkeypatch, session)
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Save)
    warnings: list[str] = []
    monkeypatch.setattr(main_window_module.QMessageBox, "warning", lambda *a, **k: warnings.append(a[2]))
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is False
        assert warnings and "never been saved" in warnings[0]
    finally:
        window.deleteLater()


def test_uninitialized_session_is_ignored(tmp_path, monkeypatch):
    session = _FakeSession([("Motor", "x")], initialized=False)
    _install(monkeypatch, session)
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Cancel)
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
    finally:
        window.deleteLater()


# ----------------------------------------------------------------------
# FreeCAD messages forwarded to the External Terminal dock
# ----------------------------------------------------------------------


class _FakeLogTab(QWidget):
    def __init__(self):
        super().__init__()
        self.written: list[str] = []

    def write(self, text):
        self.written.append(text)


class _LogDock(_DummyExternalTerminalDock):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.log_tabs: list[tuple[str, _FakeLogTab]] = []
        self.shown = 0

    def show(self):
        self.shown += 1
        super().show()

    def add_log_tab(self, title):
        tab = _FakeLogTab()
        self.log_tabs.append((title, tab))
        return tab


class _MessageSession:
    def __init__(self):
        self.listeners: list = []

    def add_message_listener(self, listener):
        self.listeners.append(listener)

    def remove_message_listener(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)

    def emit(self, text):
        for listener in list(self.listeners):
            listener(text)


def _make_window_with_log_dock(tmp_path, monkeypatch):
    _app()
    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _LogDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)
    manager = SettingsManager(global_settings_path=tmp_path / "config" / "settings.json")
    return main_window_module.PyEmsiMainWindow(settings_manager=manager)


def test_freecad_session_init_opens_message_tab_and_forwards_text(tmp_path, monkeypatch):
    window = _make_window_with_log_dock(tmp_path, monkeypatch)
    session = _MessageSession()
    try:
        window._container.freecad_session_initialized.emit(session)

        dock = window._external_terminal_dock
        assert [title for title, _ in dock.log_tabs] == ["FreeCAD messages"]
        assert dock.shown >= 1
        session.emit("Hole: Hole error: Finding axis failed\n")
        assert dock.log_tabs[0][1].written == ["Hole: Hole error: Finding axis failed\n"]
    finally:
        window.deleteLater()


def test_destroyed_message_tab_unregisters_listener(tmp_path, monkeypatch):
    app = _app()
    window = _make_window_with_log_dock(tmp_path, monkeypatch)
    session = _MessageSession()
    try:
        window._container.freecad_session_initialized.emit(session)
        tab = window._external_terminal_dock.log_tabs[0][1]
        assert len(session.listeners) == 1

        tab.deleteLater()
        app.sendPostedEvents(tab, QEvent.Type.DeferredDelete)
        app.processEvents()

        assert session.listeners == []
    finally:
        window.deleteLater()


# ----------------------------------------------------------------------
# Tab bars stay left-aligned under FreeCAD's application stylesheet
# ----------------------------------------------------------------------


def test_tab_bars_stay_left_aligned_under_centering_app_stylesheet(tmp_path, monkeypatch):
    """FreeCAD.qss (applied app-wide on FreeCAD init) centres QTabWidget tab bars.

    The main window's own stylesheet must override that for pyemsi's tabs.
    """
    app = _app()
    previous = app.styleSheet()
    app.setStyleSheet("QTabWidget::tab-bar { alignment: center; }")
    window = None
    try:
        window = _make_window(tmp_path, monkeypatch)
        window.resize(1200, 700)
        panel = window._container.left_panel
        window._container.add_tab(QWidget(), "one")
        window._container.add_tab(QWidget(), "two")
        window.show()
        app.processEvents()

        control = QTabWidget()
        control.addTab(QWidget(), "one")
        control.addTab(QWidget(), "two")
        control.resize(1200, 300)
        control.show()
        app.processEvents()

        assert panel.tabBar().geometry().x() < 10
        assert control.tabBar().geometry().x() > 100  # the app rule really centres plain tab widgets
        control.close()
    finally:
        app.setStyleSheet(previous)
        if window is not None:
            window.close()
            window.deleteLater()
