from __future__ import annotations

import os

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget

from pyemsi.gui import freecad_session as session_module
from pyemsi.gui._viewers._constants import _CATEGORY
from pyemsi.gui._viewers._freecad import FreeCADViewer
from pyemsi.gui.freecad_runtime import FreeCADRuntimeError
from pyemsi.widgets import split_container as split_container_module
from pyemsi.widgets.split_container import SplitContainer


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakeSession:
    def __init__(self, *, init_error=None, open_error=None):
        self.init_error = init_error
        self.open_error = open_error
        self.events: list[tuple] = []
        self.host = None

    @property
    def is_initialized(self):
        return any(e[0] == "init" for e in self.events)

    def ensure_initialized(self):
        if self.init_error is not None:
            raise self.init_error
        self.events.append(("init",))

    def attach(self, host):
        self.host = host
        self.events.append(("attach", host))

    def detach(self, host=None):
        self.host = None
        self.events.append(("detach", host))

    def open_document(self, path):
        if self.open_error is not None:
            raise self.open_error
        self.events.append(("open", path))
        return os.path.splitext(os.path.basename(path))[0]


@pytest.fixture
def fake_session(monkeypatch):
    session = _FakeSession()
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    return session


def _open_calls(session):
    return [e[1] for e in session.events if e[0] == "open"]


def test_fcstd_extension_maps_to_freecad_category():
    assert _CATEGORY[".fcstd"] == "freecad"
    assert _CATEGORY[".py"] == "python"
    assert _CATEGORY[".png"] == "image"
    assert ".FCStd".lower() in _CATEGORY


def test_first_fcstd_creates_single_freecad_tab(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    path = str(tmp_path / "Motor.FCStd")

    viewer = container.open_file(path)

    assert isinstance(viewer, FreeCADViewer)
    assert container.left_panel.count() == 1
    assert container.left_panel.tabText(0) == "FreeCAD — Motor.FCStd"
    assert fake_session.events[0] == ("init",)
    assert _open_calls(fake_session) == [os.path.abspath(os.path.normpath(path))]


def test_second_fcstd_reuses_tab_and_passes_new_path(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    first = container.open_file(str(tmp_path / "A.FCStd"))
    other = QWidget()
    container.add_tab(other, "other")

    second = container.open_file(str(tmp_path / "b.fcstd"))

    assert second is first
    assert container.left_panel.count() == 2
    assert container.left_panel.currentWidget() is first
    assert container.left_panel.tabText(container.left_panel.indexOf(first)) == "FreeCAD — b.fcstd"
    assert [os.path.basename(p) for p in _open_calls(fake_session)] == ["A.FCStd", "b.fcstd"]


def test_reopening_same_path_does_not_add_tab(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    path = str(tmp_path / "A.FCStd")
    container.open_file(path)
    container.open_file(path)
    assert container.left_panel.count() == 1
    assert len(_open_calls(fake_session)) == 2  # session decides activate-vs-open


def test_closing_freecad_tab_detaches_before_shell_deletion(fake_session, tmp_path):
    app = _app()
    container = SplitContainer()
    viewer = container.open_file(str(tmp_path / "A.FCStd"))

    assert container.left_panel._close_tab(container.left_panel.indexOf(viewer)) is True
    app.processEvents()

    assert container.left_panel.count() == 0
    assert ("detach", viewer) in fake_session.events
    assert fake_session.host is None


def test_reopen_after_close_creates_new_shell_with_same_session(fake_session, tmp_path):
    app = _app()
    container = SplitContainer()
    first = container.open_file(str(tmp_path / "A.FCStd"))
    container.left_panel._close_tab(container.left_panel.indexOf(first))
    app.processEvents()

    second = container.open_file(str(tmp_path / "A.FCStd"))

    assert isinstance(second, FreeCADViewer)
    assert second is not first
    assert second.session is fake_session
    assert [e[0] for e in fake_session.events].count("init") == 2  # ensure_initialized is idempotent in the real session
    assert fake_session.host is second


def test_runtime_failure_shows_message_and_creates_no_tab(monkeypatch, tmp_path):
    _app()
    session = _FakeSession(
        init_error=FreeCADRuntimeError("FreeCAD could not be initialized in the active pyemsi environment.")
    )
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    shown: list[str] = []
    monkeypatch.setattr(split_container_module.QMessageBox, "critical", lambda parent, title, text, *a: shown.append(text))
    container = SplitContainer()

    result = container.open_file(str(tmp_path / "A.FCStd"))

    assert result is None
    assert container.left_panel.count() == 0
    assert shown and "could not be initialized" in shown[0]


def test_invalid_document_shows_warning_and_keeps_tab(monkeypatch, tmp_path):
    _app()
    session = _FakeSession(
        open_error=session_module.FreeCADDocumentError("FreeCAD could not open bad.FCStd:\nInvalid project file")
    )
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    shown: list[str] = []
    monkeypatch.setattr(split_container_module.QMessageBox, "warning", lambda parent, title, text, *a: shown.append(text))
    container = SplitContainer()

    viewer = container.open_file(str(tmp_path / "bad.FCStd"))

    assert isinstance(viewer, FreeCADViewer)
    assert container.left_panel.count() == 1
    assert shown and "Invalid project file" in shown[0]


def test_non_freecad_files_still_use_generic_path(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    text_file = tmp_path / "notes.txt"
    text_file.write_text("hello", encoding="utf-8")

    viewer = container.open_file(str(text_file))

    assert not isinstance(viewer, FreeCADViewer)
    assert viewer.property("file_path") == str(text_file)
    assert fake_session.events == []


def test_context_menu_hides_move_action_for_freecad_viewer(fake_session, tmp_path, monkeypatch):
    _app()
    container = SplitContainer()
    viewer = container.open_file(str(tmp_path / "A.FCStd"))
    captured: list[list[str]] = []

    class _RecordingMenu(split_container_module.QMenu):
        def exec(self, *args, **kwargs):  # noqa: A003
            captured.append([a.text() for a in self.actions() if not a.isSeparator()])
            return None

    monkeypatch.setattr(split_container_module, "QMenu", _RecordingMenu)
    panel = container.left_panel
    panel.setCurrentWidget(viewer)
    panel._show_context_menu(QPoint(0, 0))  # _tab_index_at falls back to currentIndex()

    assert captured == [["Close Tab", "Close Others", "Close All"]]
