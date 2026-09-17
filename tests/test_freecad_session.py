from __future__ import annotations

import os
import types

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from pyemsi.gui import freecad_session as session_module
from pyemsi.gui.freecad_runtime import FreeCADModules, FreeCADRuntimeError


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakeView:
    def __init__(self):
        self.calls: list[str] = []

    def fitAll(self):  # noqa: N802
        self.calls.append("fitAll")

    def viewAxonometric(self):  # noqa: N802
        self.calls.append("viewAxonometric")


class _FakeAppDoc:
    def __init__(self, name, file_name):
        self.Name = name
        self.Label = name
        self.FileName = file_name
        self.saved = 0

    def save(self):
        if not self.FileName:
            raise RuntimeError("no file name")
        self.saved += 1


class _FakeGuiDoc:
    def __init__(self, modified=False):
        self.Modified = modified
        self.ActiveView = _FakeView()


class _FakeFreeCAD:
    """Stands in for FreeCAD (App) + FreeCADGui with the verified 1.1 API surface."""

    def __init__(self, *, open_error=None):
        self.app = types.SimpleNamespace()
        self.gui = types.SimpleNamespace()
        self._docs: dict[str, _FakeAppDoc] = {}
        self._gui_docs: dict[str, _FakeGuiDoc] = {}
        self.active: list[tuple[str, str]] = []
        self.show_main_window_calls = 0
        self.open_error = open_error
        self.main_window = QMainWindow()
        self.main_window.show()

        self.app.listDocuments = lambda: dict(self._docs)
        self.app.getDocument = lambda name: self._docs[name]
        self.app.openDocument = self._open
        self.app.setActiveDocument = lambda name: self.active.append(("app", name))
        self.gui.showMainWindow = self._show_main_window
        self.gui.getMainWindow = lambda: self.main_window
        self.gui.getDocument = lambda name: self._gui_docs[name]
        self.gui.setActiveDocument = lambda name: self.active.append(("gui", name))

    def _show_main_window(self):
        self.show_main_window_calls += 1

    def _open(self, path):
        if self.open_error is not None:
            raise self.open_error
        name = os.path.splitext(os.path.basename(path))[0]
        doc = _FakeAppDoc(name, path.replace("\\", "/"))  # FreeCAD reports forward slashes
        self._docs[name] = doc
        self._gui_docs[name] = _FakeGuiDoc()
        return doc

    def modules(self) -> FreeCADModules:
        return FreeCADModules(app=self.app, gui=self.gui)


def _host() -> QWidget:
    host = QWidget()
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    return host


def test_normalize_document_path_matches_freecad_forward_slash_paths(tmp_path):
    original = str(tmp_path / "Motor.FCStd")
    from_freecad = original.replace("\\", "/")
    assert session_module.normalize_document_path(original) == session_module.normalize_document_path(from_freecad)


def test_ensure_initialized_is_idempotent_and_parks_native_window():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)

    session.ensure_initialized()
    session.ensure_initialized()

    assert fake.show_main_window_calls == 1
    assert session.is_initialized
    assert session.main_window is fake.main_window
    assert not fake.main_window.isVisible()
    assert fake.main_window.parent() is not None  # parked, not top-level


def test_ensure_initialized_wraps_loader_failure():
    _app()

    def _boom():
        raise FreeCADRuntimeError("nope")

    session = session_module.FreeCADSession(loader=_boom)
    with pytest.raises(FreeCADRuntimeError):
        session.ensure_initialized()
    assert not session.is_initialized


def test_attach_and_detach_move_native_window_between_host_and_parking():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    host = _host()

    session.attach(host)
    assert fake.main_window.parent() is host
    assert host.layout().indexOf(fake.main_window) != -1
    assert session.attached_host is host

    session.detach(host)
    assert fake.main_window.parent() is not host
    assert not fake.main_window.isVisible()
    assert session.attached_host is None
    assert fake.main_window.parent() is not None  # back in parking


def test_detach_ignores_foreign_host_and_repeated_calls():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    host, other = _host(), _host()
    session.attach(host)

    session.detach(other)
    assert session.attached_host is host

    session.detach()
    session.detach()  # must not raise
    assert session.attached_host is None


def test_reattach_after_detach_reuses_same_native_window():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    for _ in range(3):
        host = _host()
        session.attach(host)
        assert fake.main_window.parent() is host
        session.detach(host)
    assert fake.show_main_window_calls == 1


def test_open_document_opens_activates_and_fits_new_document(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    path = str(tmp_path / "Motor.FCStd")

    name = session.open_document(path)

    assert name == "Motor"
    assert fake.active == [("app", "Motor"), ("gui", "Motor")]
    assert fake._gui_docs["Motor"].ActiveView.calls == ["viewAxonometric", "fitAll"]
    assert session.is_document_open(path)


def test_open_document_activates_existing_document_instead_of_duplicating(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    path = str(tmp_path / "Motor.FCStd")
    session.open_document(path)
    open_calls: list[str] = []
    fake.app.openDocument = lambda p: open_calls.append(p)

    name = session.open_document(path.upper() if os.name == "nt" else path)

    assert name == "Motor"
    assert open_calls == []
    assert fake._gui_docs["Motor"].ActiveView.calls == ["viewAxonometric", "fitAll", "fitAll"]


def test_open_document_wraps_freecad_errors(tmp_path):
    _app()
    fake = _FakeFreeCAD(open_error=OSError("Invalid project file"))
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()

    with pytest.raises(session_module.FreeCADDocumentError) as excinfo:
        session.open_document(str(tmp_path / "bad.FCStd"))

    assert "Invalid project file" in str(excinfo.value)
    assert "bad.FCStd" in str(excinfo.value)
    assert session.is_initialized  # session survives a bad file


def test_open_document_requires_initialization(tmp_path):
    session = session_module.FreeCADSession(loader=lambda: None)
    with pytest.raises(FreeCADRuntimeError):
        session.open_document(str(tmp_path / "x.FCStd"))


def test_modified_documents_reports_only_dirty_docs(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    a = str(tmp_path / "A.FCStd")
    b = str(tmp_path / "B.FCStd")
    session.open_document(a)
    session.open_document(b)
    fake._gui_docs["B"].Modified = True

    assert session.modified_documents() == [("B", b.replace("\\", "/"))]


def test_modified_documents_is_empty_before_initialization():
    session = session_module.FreeCADSession(loader=lambda: None)
    assert session.modified_documents() == []


def test_save_document_calls_freecad_save(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    session.open_document(str(tmp_path / "A.FCStd"))

    session.save_document("A")

    assert fake._docs["A"].saved == 1


def test_save_document_refuses_unnamed_document():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    fake._docs["Unnamed"] = _FakeAppDoc("Unnamed", "")
    fake._gui_docs["Unnamed"] = _FakeGuiDoc(modified=True)

    with pytest.raises(session_module.FreeCADDocumentError):
        session.save_document("Unnamed")


def test_prepare_for_application_exit_detaches():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    host = _host()  # keep a reference: a collected host would delete the reparented window
    session.attach(host)

    session.prepare_for_application_exit()

    assert session.attached_host is None
    assert fake.main_window.parent() is not host


def test_get_freecad_session_is_a_process_singleton(monkeypatch):
    monkeypatch.setattr(session_module, "_SESSION", None)
    assert session_module.peek_freecad_session() is None
    first = session_module.get_freecad_session()
    assert session_module.get_freecad_session() is first
    assert session_module.peek_freecad_session() is first
