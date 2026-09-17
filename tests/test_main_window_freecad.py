from __future__ import annotations

from PySide6.QtWidgets import QApplication, QDockWidget, QMessageBox, QWidget

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
