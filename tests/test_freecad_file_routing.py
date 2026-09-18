from __future__ import annotations

import os

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QLabel, QWidget

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
        self.main_window = None
        self.modified_documents: set[str] = set()

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
        if self.main_window is not None:
            host.layout().addWidget(self.main_window)

    def detach(self, host=None):
        self.host = None
        self.events.append(("detach", host))

    def open_document(self, path):
        if self.open_error is not None:
            raise self.open_error
        self.events.append(("open", path))
        return os.path.splitext(os.path.basename(path))[0]

    def create_document(self, path):
        self.events.append(("create", path))
        return os.path.splitext(os.path.basename(path))[0]

    def is_document_modified(self, name):
        return name in self.modified_documents

    def save_document(self, name):
        self.events.append(("save", name))
        self.modified_documents.discard(name)


@pytest.fixture
def fake_session(monkeypatch):
    session = _FakeSession()
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    return session


def _open_calls(session):
    return [e[1] for e in session.events if e[0] == "open"]


def _finish_loading():
    _app().processEvents()
    _app().processEvents()


def test_fcstd_extension_maps_to_freecad_category():
    assert _CATEGORY[".fcstd"] == "freecad"
    assert _CATEGORY[".py"] == "python"
    assert _CATEGORY[".png"] == "image"
    assert ".FCStd".lower() in _CATEGORY


def test_first_fcstd_creates_its_own_freecad_tab(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    path = str(tmp_path / "Motor.FCStd")
    diagnostics_started: list[list[tuple]] = []
    container.freecad_session_starting.connect(lambda session: diagnostics_started.append(list(session.events)))

    viewer = container.open_file(path)

    assert isinstance(viewer, FreeCADViewer)
    assert container.left_panel.count() == 1
    assert container.left_panel.tabText(0) == "Motor.FCStd"
    assert viewer.loading is True
    assert fake_session.events == []
    assert diagnostics_started == [[]]

    _finish_loading()

    assert viewer.loading is False
    assert fake_session.events[0] == ("init",)
    assert _open_calls(fake_session) == [os.path.abspath(os.path.normpath(path))]


def test_second_fcstd_creates_another_tab_with_same_session(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    first = container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()
    other = QWidget()
    container.add_tab(other, "other")

    second = container.open_file(str(tmp_path / "b.fcstd"))

    assert second.loading is True
    assert [os.path.basename(p) for p in _open_calls(fake_session)] == ["A.FCStd"]

    _finish_loading()

    assert second is not first
    assert second.session is first.session
    assert container.left_panel.count() == 3
    assert container.left_panel.currentWidget() is second
    assert container.left_panel.tabText(container.left_panel.indexOf(first)) == "A.FCStd"
    assert container.left_panel.tabText(container.left_panel.indexOf(second)) == "b.fcstd"
    assert [os.path.basename(p) for p in _open_calls(fake_session)] == ["A.FCStd", "b.fcstd"]


def test_new_fcstd_uses_loading_tab_and_shared_session(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    path = str(tmp_path / "NewPart.FCStd")

    viewer = container.create_freecad_file(path)

    assert isinstance(viewer, FreeCADViewer)
    assert viewer.loading is True
    assert container.left_panel.tabText(0) == "NewPart.FCStd"

    _finish_loading()

    assert viewer.loading is False
    assert ("create", os.path.abspath(os.path.normpath(path))) in fake_session.events


def test_reopening_same_path_does_not_add_tab(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    path = str(tmp_path / "A.FCStd")
    container.open_file(path)
    _finish_loading()
    container.open_file(path)
    assert container.left_panel.count() == 1
    assert len(_open_calls(fake_session)) == 2  # session decides activate-vs-open


def test_freecad_dirty_change_updates_outer_tab_title(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    viewer = container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()
    index = container.left_panel.indexOf(viewer)

    fake_session.modified_documents.add("A")
    viewer._sync_dirty()

    assert container.left_panel.tabText(index) == "A.FCStd *"

    fake_session.modified_documents.clear()
    viewer._sync_dirty()

    assert container.left_panel.tabText(index) == "A.FCStd"


def test_switching_freecad_tabs_moves_shared_window_and_activates_file(fake_session, tmp_path):
    _app()
    fake_session.main_window = QWidget()
    container = SplitContainer()
    first = container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()
    second = container.open_file(str(tmp_path / "B.FCStd"))
    _finish_loading()
    fake_session.events.clear()

    container.left_panel.setCurrentWidget(first)

    assert fake_session.host is first
    assert first.layout().currentWidget() is fake_session.main_window
    assert fake_session.events == [
        ("attach", first),
        ("open", first.current_path),
    ]
    assert container.left_panel.currentWidget() is first
    assert second.current_path.endswith("B.FCStd")


def test_closing_freecad_tab_detaches_before_shell_deletion(fake_session, tmp_path):
    app = _app()
    container = SplitContainer()
    viewer = container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()

    assert container.left_panel._close_tab(container.left_panel.indexOf(viewer)) is True
    app.processEvents()

    assert container.left_panel.count() == 0
    assert ("detach", viewer) in fake_session.events
    assert fake_session.host is None


def test_reopen_after_close_creates_new_shell_with_same_session(fake_session, tmp_path):
    app = _app()
    container = SplitContainer()
    first = container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()
    container.left_panel._close_tab(container.left_panel.indexOf(first))
    app.processEvents()

    second = container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()

    assert isinstance(second, FreeCADViewer)
    assert second is not first
    assert second.session is fake_session
    assert [e[0] for e in fake_session.events].count("init") == 2  # ensure_initialized is idempotent in the real session
    assert fake_session.host is second


def test_runtime_failure_is_shown_inside_the_file_tab(monkeypatch, tmp_path):
    _app()
    session = _FakeSession(
        init_error=FreeCADRuntimeError("FreeCAD could not be initialized in the active pyemsi environment.")
    )
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    container = SplitContainer()

    result = container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()

    assert isinstance(result, FreeCADViewer)
    assert container.left_panel.count() == 1
    assert "could not be initialized" in result.findChild(QLabel).text()


def test_invalid_document_error_is_shown_inside_the_file_tab(monkeypatch, tmp_path):
    _app()
    session = _FakeSession(
        open_error=session_module.FreeCADDocumentError("FreeCAD could not open bad.FCStd:\nInvalid project file")
    )
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    container = SplitContainer()

    viewer = container.open_file(str(tmp_path / "bad.FCStd"))
    _finish_loading()

    assert isinstance(viewer, FreeCADViewer)
    assert container.left_panel.count() == 1
    assert "Invalid project file" in viewer.findChild(QLabel).text()


def test_non_freecad_files_still_use_generic_path(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    text_file = tmp_path / "notes.txt"
    text_file.write_text("hello", encoding="utf-8")

    viewer = container.open_file(str(text_file))

    assert not isinstance(viewer, FreeCADViewer)
    assert viewer.property("file_path") == str(text_file)
    assert fake_session.events == []


def test_context_menu_is_disabled_for_freecad_viewer(fake_session, tmp_path, monkeypatch):
    _app()
    container = SplitContainer()
    viewer = container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()
    captured: list[list[str]] = []

    class _RecordingMenu(split_container_module.QMenu):
        def exec(self, *args, **kwargs):  # noqa: A003
            captured.append([a.text() for a in self.actions() if not a.isSeparator()])
            return None

    monkeypatch.setattr(split_container_module, "QMenu", _RecordingMenu)
    panel = container.left_panel
    panel.setCurrentWidget(viewer)
    panel._show_context_menu(QPoint(0, 0))  # _tab_index_at falls back to currentIndex()

    assert captured == []


def test_freecad_session_initialized_signal_fires_once_per_process(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    seen: list[object] = []
    container.freecad_session_initialized.connect(seen.append)

    container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()
    container.open_file(str(tmp_path / "B.FCStd"))
    _finish_loading()

    assert seen == [fake_session]


def test_freecad_session_initialized_signal_not_fired_on_runtime_failure(monkeypatch, tmp_path):
    _app()
    session = _FakeSession(init_error=FreeCADRuntimeError("nope"))
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    monkeypatch.setattr(split_container_module.QMessageBox, "critical", lambda *a, **k: None)
    container = SplitContainer()
    seen: list[object] = []
    container.freecad_session_initialized.connect(seen.append)

    container.open_file(str(tmp_path / "A.FCStd"))
    _finish_loading()

    assert seen == []
