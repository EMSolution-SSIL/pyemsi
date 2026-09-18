from __future__ import annotations

import os
import types

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QMainWindow,
    QMdiArea,
    QTabBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

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
        self.graphics_widget: QWidget | None = None

    def graphicsView(self):  # noqa: N802
        if self.graphics_widget is None:
            raise AttributeError("no graphics view")
        return self.graphics_widget

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

    def saveAs(self, path):  # noqa: N802
        self.FileName = path.replace("\\", "/")
        self.saved += 1


class _FakeGuiDoc:
    def __init__(self, modified=False):
        self.Modified = modified
        self.ActiveView = _FakeView()


class _FakeParamGroup:
    def __init__(self):
        self.values: dict[str, int] = {}

    def GetInt(self, name, default):  # noqa: N802
        return self.values.get(name, default)

    def SetInt(self, name, value):  # noqa: N802
        self.values[name] = value


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
        self.open_hidden_values: list[bool] = []
        self.param_groups: dict[str, _FakeParamGroup] = {}
        self.main_window = QMainWindow()
        self.main_window.show()

        self.app.listDocuments = lambda: dict(self._docs)
        self.app.getDocument = lambda name: self._docs[name]
        self.app.openDocument = self._open
        self.app.newDocument = self._new
        self.app.closeDocument = self._close
        self.app.setActiveDocument = lambda name: self.active.append(("app", name))
        self.app.ParamGet = lambda path: self.param_groups.setdefault(path, _FakeParamGroup())
        self.gui.showMainWindow = self._show_main_window
        self.gui.getMainWindow = lambda: self.main_window
        self.gui.getDocument = lambda name: self._gui_docs[name]
        self.gui.setActiveDocument = lambda name: self.active.append(("gui", name))

    def _show_main_window(self):
        self.show_main_window_calls += 1

    def _open(self, path, hidden=False):
        if self.open_error is not None:
            raise self.open_error
        self.open_hidden_values.append(hidden)
        name = os.path.splitext(os.path.basename(path))[0]
        doc = _FakeAppDoc(name, path.replace("\\", "/"))  # FreeCAD reports forward slashes
        self._docs[name] = doc
        gui_doc = _FakeGuiDoc()
        gui_doc.ActiveView.graphics_widget = getattr(self, "_pending_graphics_widget", None)
        self._gui_docs[name] = gui_doc
        return doc

    def _new(self):
        name = "Unnamed" if "Unnamed" not in self._docs else f"Unnamed{len(self._docs)}"
        doc = _FakeAppDoc(name, "")
        self._docs[name] = doc
        self._gui_docs[name] = _FakeGuiDoc()
        return doc

    def _close(self, name):
        self._docs.pop(name, None)
        self._gui_docs.pop(name, None)

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


def test_layout_defaults_apply_once_then_preserve_user_changes():
    _app()
    fake = _FakeFreeCAD()
    tasks = QDockWidget("Tasks", fake.main_window)
    tasks.setObjectName("Tasks")
    fake.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tasks)
    tasks.setFloating(True)
    fake.main_window.statusBar().hide()

    toolbars = []
    for name in ("File", *session_module._PART_DESIGN_TOOLBARS):
        toolbar = QToolBar(name, fake.main_window)
        toolbar.setObjectName(name)
        fake.main_window.addToolBar(toolbar)
        toolbar.hide()
        toolbars.append(toolbar)

    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()

    assert not tasks.isFloating()
    assert fake.main_window.dockWidgetArea(tasks) == Qt.DockWidgetArea.RightDockWidgetArea
    assert not fake.main_window.statusBar().isHidden()
    assert all(not toolbar.isHidden() for toolbar in toolbars)

    # Once initialized, later user choices are not forced back to defaults.
    tasks.setFloating(True)
    fake.main_window.statusBar().hide()
    toolbars[0].hide()
    session._apply_layout_defaults()

    assert tasks.isFloating()
    assert fake.main_window.statusBar().isHidden()
    assert toolbars[0].isHidden()


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
    assert fake.open_hidden_values == [False]


def test_open_document_activates_existing_document_instead_of_duplicating(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    path = str(tmp_path / "Motor.FCStd")
    session.open_document(path)
    open_calls: list[str] = []
    fake.app.openDocument = lambda p, hidden=False: open_calls.append((p, hidden))

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


def test_create_document_saves_and_activates_new_document(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    path = str(tmp_path / "NewPart.FCStd")

    name = session.create_document(path)

    assert name == "Unnamed"
    assert fake._docs[name].Label == "NewPart"
    assert fake._docs[name].FileName == path.replace("\\", "/")
    assert fake._docs[name].saved == 1
    assert fake.active == [("app", name), ("gui", name)]


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


def test_is_document_modified_reads_gui_document_flag(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    session.open_document(str(tmp_path / "A.FCStd"))

    assert session.is_document_modified("A") is False
    fake._gui_docs["A"].Modified = True
    assert session.is_document_modified("A") is True


def test_save_document_calls_freecad_save(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    session.open_document(str(tmp_path / "A.FCStd"))

    session.save_document("A")

    assert fake._docs["A"].saved == 1


def test_save_document_clears_gui_modified_flag(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    session.open_document(str(tmp_path / "A.FCStd"))
    fake._gui_docs["A"].Modified = True  # FreeCAD 1.1 keeps this set after App.Document.save()

    session.save_document("A")

    assert fake._gui_docs["A"].Modified is False
    assert session.modified_documents() == []


def test_open_document_raises_its_mdi_subwindow_above_start_page(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    area = QMdiArea()
    fake.main_window.setCentralWidget(area)
    start_page = area.addSubWindow(QWidget())
    start_page.widget().setWindowTitle("Start page")
    view_widget = QWidget()
    inner = QWidget(view_widget)  # graphicsView() returns a nested child in FreeCAD
    doc_window = area.addSubWindow(view_widget)
    area.setActiveSubWindow(start_page)
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    path = str(tmp_path / "Motor.FCStd")
    fake._pending_graphics_widget = inner

    session.open_document(path)

    assert area.activeSubWindow() is doc_window


def test_open_document_hides_freecad_mdi_document_tabs(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    area = QMdiArea()
    area.setViewMode(QMdiArea.ViewMode.TabbedView)
    fake.main_window.setCentralWidget(area)
    area.addSubWindow(QWidget())
    tab_bar = area.findChild(QTabBar)
    assert tab_bar is not None
    tab_bar.show()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()

    session.open_document(str(tmp_path / "Motor.FCStd"))

    assert tab_bar.isHidden()


def test_open_document_tolerates_views_without_graphics_view(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()

    assert session.open_document(str(tmp_path / "Motor.FCStd")) == "Motor"


def test_save_document_refuses_unnamed_document():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    fake._docs["Unnamed"] = _FakeAppDoc("Unnamed", "")
    fake._gui_docs["Unnamed"] = _FakeGuiDoc(modified=True)

    with pytest.raises(session_module.FreeCADDocumentError):
        session.save_document("Unnamed")


def _embedded_host() -> tuple[QMainWindow, QWidget]:
    """A host shell nested inside a top-level main window, like a pyemsi tab."""
    main = QMainWindow()
    central = QWidget()
    QVBoxLayout(central)
    main.setCentralWidget(central)
    host = _host()
    central.layout().addWidget(host)
    return main, host


def test_detach_keeps_native_window_inside_the_hosts_top_level_window():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    main, host = _embedded_host()

    session.attach(host)
    assert fake.main_window.window() is main
    session.detach(host)

    # Parked, hidden, but still under the same top-level window: no GL context change.
    assert fake.main_window.parent() is not host
    assert not fake.main_window.isVisible()
    assert fake.main_window.window() is main


def test_top_level_host_keeps_parking_standalone():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    host = _host()

    session.attach(host)
    session.detach(host)

    assert fake.main_window.window() is not host
    assert fake.main_window.window().parent() is None


def test_prepare_for_application_exit_releases_parking_from_main_window():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    main, host = _embedded_host()
    session.attach(host)

    session.prepare_for_application_exit()

    assert session.attached_host is None
    assert fake.main_window.window() is not main
    assert fake.main_window.window().parent() is None


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


# ----------------------------------------------------------------------
# Report view message forwarding
# ----------------------------------------------------------------------


def _report_view(fake: _FakeFreeCAD):
    from PySide6.QtWidgets import QTextEdit

    edit = QTextEdit(fake.main_window)
    edit.setObjectName("Report view")
    fake.main_window.setCentralWidget(edit)
    return edit


def test_report_view_text_is_forwarded_to_message_listeners():
    _app()
    fake = _FakeFreeCAD()
    edit = _report_view(fake)
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    received: list[str] = []
    session.add_message_listener(received.append)

    edit.append("12:00:00  <PartDesign> skip edge that is not C0 continuous")
    edit.append("12:00:01  Hole: Hole error: Finding axis failed")

    assert "".join(received).splitlines() == [
        "12:00:00  <PartDesign> skip edge that is not C0 continuous",
        "12:00:01  Hole: Hole error: Finding axis failed",
    ]


def test_removed_message_listener_stops_receiving():
    _app()
    fake = _FakeFreeCAD()
    edit = _report_view(fake)
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    received: list[str] = []
    session.add_message_listener(received.append)
    session.remove_message_listener(received.append)
    session.remove_message_listener(received.append)  # idempotent

    edit.append("ignored")

    assert received == []


def test_report_view_clear_does_not_forward_text():
    _app()
    fake = _FakeFreeCAD()
    edit = _report_view(fake)
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    received: list[str] = []
    session.add_message_listener(received.append)
    edit.append("first")
    received.clear()

    edit.clear()

    assert received == []


def test_session_without_report_view_accepts_listeners():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()

    session.add_message_listener(lambda text: None)  # must not raise
