from __future__ import annotations

import os

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from pyemsi.gui._viewers._freecad import FreeCADViewer


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _RecordingSession:
    def __init__(self):
        self.events: list[tuple] = []

    def attach(self, host):
        self.events.append(("attach", host))

    def detach(self, host=None):
        self.events.append(("detach", host))

    def open_document(self, path):
        self.events.append(("open", path))
        return os.path.splitext(os.path.basename(path))[0]


def test_viewer_attaches_session_on_construction_and_has_zero_margin_layout():
    _app()
    session = _RecordingSession()

    viewer = FreeCADViewer(session)

    assert session.events == [("attach", viewer)]
    assert viewer.layout() is not None
    assert viewer.layout().contentsMargins().left() == 0
    assert viewer.viewer_kind == "freecad"
    assert viewer.supports_panel_move is False
    assert not hasattr(viewer, "dirty") and not hasattr(viewer, "save")


def test_open_file_delegates_to_session_and_records_normalized_path(tmp_path):
    _app()
    session = _RecordingSession()
    viewer = FreeCADViewer(session)
    raw = str(tmp_path / "sub" / ".." / "Motor.FCStd")

    name = viewer.open_file(raw)

    assert name == "Motor"
    assert session.events[-1] == ("open", os.path.abspath(os.path.normpath(raw)))
    assert viewer.current_path == os.path.abspath(os.path.normpath(raw))


def test_close_detaches_session_exactly_once():
    _app()
    session = _RecordingSession()
    viewer = FreeCADViewer(session)

    viewer.close()
    viewer.close()

    assert session.events == [("attach", viewer), ("detach", viewer)]


def test_delete_without_close_still_detaches_once():
    app = _app()
    session = _RecordingSession()
    viewer = FreeCADViewer(session)

    viewer.deleteLater()
    # processEvents() alone never runs deferred deletes outside a nested loop.
    # Flush only this receiver: a global flush would also destroy widgets
    # left half-torn-down by unrelated tests earlier in the same process.
    app.sendPostedEvents(viewer, QEvent.Type.DeferredDelete)
    app.processEvents()

    detaches = [e for e in session.events if e[0] == "detach"]
    assert len(detaches) == 1
