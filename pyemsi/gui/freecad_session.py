"""Process-wide FreeCAD GUI session shared by every FreeCADViewer shell.

The FreeCAD GUI is a singleton native main window. This session creates it
once, keeps it alive in a hidden *parking* widget while no pyemsi tab shows
it, and lends it to at most one host widget at a time. Tab shells come and
go; the native window and the open documents persist for the process.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Callable

from PySide6.QtCore import QEventLoop
from PySide6.QtWidgets import QApplication, QMdiArea, QMdiSubWindow, QWidget

from pyemsi.gui.freecad_runtime import FreeCADModules, FreeCADRuntimeError, import_freecad

LOGGER = logging.getLogger(__name__)


class FreeCADDocumentError(RuntimeError):
    """A FreeCAD document could not be opened or saved."""


def normalize_document_path(path: str) -> str:
    """Canonical form for comparing document paths (FreeCAD reports forward slashes)."""
    return os.path.normcase(os.path.abspath(os.path.normpath(path)))


class FreeCADSession:
    """Owns the native FreeCAD main window and the document open/activate logic."""

    def __init__(self, loader: Callable[[], FreeCADModules] | None = None) -> None:
        self._loader = loader or import_freecad
        self._modules: FreeCADModules | None = None
        self._main_window: QWidget | None = None
        self._parking: QWidget | None = None
        self._host: QWidget | None = None

    # ------------------------------------------------------------------
    # state
    # ------------------------------------------------------------------

    @property
    def is_initialized(self) -> bool:
        return self._main_window is not None

    @property
    def main_window(self) -> QWidget | None:
        return self._main_window

    @property
    def attached_host(self) -> QWidget | None:
        return self._host

    def _require_initialized(self) -> FreeCADModules:
        if self._modules is None or self._main_window is None:
            raise FreeCADRuntimeError("FreeCAD session is not initialized; call ensure_initialized() first.")
        return self._modules

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    def ensure_initialized(self) -> None:
        """Import FreeCAD, create the native main window once and park it hidden."""
        if self._main_window is not None:
            return
        if QApplication.instance() is None:
            raise FreeCADRuntimeError("A QApplication must exist before the FreeCAD GUI can be initialized.")

        modules = self._loader()
        LOGGER.info("FreeCAD GUI initialization started")
        # showMainWindow() is the only way to create the GUI singleton in
        # FreeCAD 1.1; it briefly shows a top-level window (known flash).
        modules.gui.showMainWindow()
        main_window = modules.gui.getMainWindow()

        parking = QWidget()
        parking.setObjectName("freecad_parking")
        parking.hide()

        self._modules = modules
        self._main_window = main_window
        self._parking = parking
        self._park()
        self._settle_start_page()
        LOGGER.info("FreeCAD GUI initialization complete")

    def _settle_start_page(self, timeout_s: float = 2.0) -> None:
        """Let FreeCAD create its deferred Start page before any document is opened.

        FreeCAD 1.1 adds the Start page as an MDI sub-window from a timer that
        fires shortly after ``showMainWindow()``. If a document view is created
        first, that late Start page lands on top of it and hides the model. The
        wait is bounded and a no-op for main windows without an MDI area.
        """
        assert self._main_window is not None
        area = self._main_window.findChild(QMdiArea)
        app = QApplication.instance()
        if area is None or app is None:
            return
        deadline = time.monotonic() + timeout_s
        while not area.subWindowList() and time.monotonic() < deadline:
            app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 50)

    def _park(self) -> None:
        assert self._main_window is not None and self._parking is not None
        try:
            self._main_window.hide()
            self._main_window.setParent(self._parking)  # resets window flags to Qt.Widget
        except RuntimeError:
            # The host was deleted while still holding the native window. This
            # must never happen (shells detach in closeEvent); log loudly rather
            # than crash inside a destroyed() handler.
            LOGGER.error("FreeCAD native window was destroyed together with its host shell")
            return
        LOGGER.info("FreeCAD native window parked")

    def attach(self, host: QWidget) -> None:
        """Show the native window inside *host* (which must own a layout)."""
        self._require_initialized()
        if self._host is host:
            return
        if self._host is not None:
            self.detach()
        layout = host.layout()
        if layout is None:
            raise ValueError("FreeCADSession.attach() requires a host widget with a layout")
        self._adopt_top_level(host)
        layout.addWidget(self._main_window)  # reparents into host
        self._main_window.show()
        self._host = host
        LOGGER.info("FreeCAD native window attached")

    def _adopt_top_level(self, host: QWidget) -> None:
        """Park under the host's top-level window so re-parenting never crosses windows.

        Moving a QOpenGLWidget to a different top-level window destroys and
        recreates its OpenGL context. FreeCAD's Coin3D viewer keeps GL caches
        bound to the old context and then renders black (seen on Windows
        after closing and re-opening the FreeCAD tab). Keeping the parking
        widget inside the same top-level window as the tab shell avoids the
        context change. Top-level hosts keep a standalone parking widget so
        the native window never dies with its host.
        """
        assert self._parking is not None
        top = host.window()
        if top is host:
            return
        if self._parking.parentWidget() is not top:
            self._parking.setParent(top)
            self._parking.hide()

    def detach(self, host: QWidget | None = None) -> None:
        """Return the native window to parking. No-op if not attached (or attached elsewhere)."""
        if self._main_window is None or self._host is None:
            return
        if host is not None and host is not self._host:
            return
        try:
            layout = self._host.layout()
            if layout is not None:
                layout.removeWidget(self._main_window)
        except RuntimeError:
            # Host's C++ object is already gone (detach reached via QObject.destroyed).
            LOGGER.warning("FreeCAD host shell was destroyed before detach; re-parking native window")
        self._host = None
        self._park()

    def prepare_for_application_exit(self) -> None:
        """Detach from any shell so pyemsi's tab teardown never owns the native window."""
        LOGGER.info("FreeCAD application-shutdown preparation")
        self.detach()
        if self._parking is not None and self._parking.parentWidget() is not None:
            # Give the parking widget back its own top level so pyemsi's main
            # window teardown never deletes the native FreeCAD window.
            self._parking.setParent(None)
            self._parking.hide()

    # ------------------------------------------------------------------
    # documents
    # ------------------------------------------------------------------

    def _documents(self) -> list:
        modules = self._require_initialized()
        return list(modules.app.listDocuments().values())

    def find_document(self, path: str):
        """Return the open FreeCAD document stored at *path*, or ``None``."""
        target = normalize_document_path(path)
        for doc in self._documents():
            file_name = getattr(doc, "FileName", "") or ""
            if file_name and normalize_document_path(file_name) == target:
                return doc
        return None

    def is_document_open(self, path: str) -> bool:
        return self.find_document(path) is not None

    def open_document(self, path: str) -> str:
        """Open *path* (or activate it if already open), fit the view, return the document name."""
        modules = self._require_initialized()
        norm_path = os.path.abspath(os.path.normpath(path))
        LOGGER.info("FreeCAD document open requested: %s", norm_path)

        doc = self.find_document(norm_path)
        newly_opened = doc is None
        if newly_opened:
            try:
                doc = modules.app.openDocument(norm_path)
            except Exception as exc:  # FreeCAD raises OSError / Base.FreeCADError
                LOGGER.error("FreeCAD could not open %s: %s", norm_path, exc)
                raise FreeCADDocumentError(f"FreeCAD could not open {norm_path}:\n{exc}") from exc

        modules.app.setActiveDocument(doc.Name)
        modules.gui.setActiveDocument(doc.Name)

        view = self._active_view(doc.Name)
        if view is not None:
            if newly_opened and hasattr(view, "viewAxonometric"):
                view.viewAxonometric()
            if hasattr(view, "fitAll"):
                view.fitAll()
            self._raise_view(view)
        LOGGER.info("FreeCAD document activated: %s", norm_path)
        return doc.Name

    @staticmethod
    def _raise_view(view) -> None:
        """Make the MDI sub-window that hosts *view* the active one.

        ``Gui.setActiveDocument`` does not reorder FreeCAD's MDI area, so a
        Start page (or another document) created later can stay on top of
        the document the user just opened.
        """
        try:
            widget = view.graphicsView()
        except Exception:
            return
        while widget is not None and not isinstance(widget, QMdiSubWindow):
            widget = widget.parentWidget()
        if widget is None:
            return
        area = widget.mdiArea()
        if area is not None:
            area.setActiveSubWindow(widget)

    def _active_view(self, name: str):
        modules = self._require_initialized()
        try:
            gui_doc = modules.gui.getDocument(name)
        except Exception:
            return None
        return getattr(gui_doc, "ActiveView", None)

    def modified_documents(self) -> list[tuple[str, str]]:
        """Return ``(Name, FileName)`` for every document whose GUI ``Modified`` flag is set."""
        if self._modules is None:
            return []
        result: list[tuple[str, str]] = []
        for doc in self._documents():
            try:
                gui_doc = self._modules.gui.getDocument(doc.Name)
            except Exception:
                continue
            if getattr(gui_doc, "Modified", False):
                result.append((doc.Name, getattr(doc, "FileName", "") or ""))
        return result

    def save_document(self, name: str) -> None:
        """Save document *name* to its existing FileName."""
        modules = self._require_initialized()
        doc = modules.app.getDocument(name)
        if not (getattr(doc, "FileName", "") or ""):
            raise FreeCADDocumentError(
                f"FreeCAD document '{doc.Label}' has never been saved. "
                "Use FreeCAD's File > Save As inside the FreeCAD tab first."
            )
        try:
            doc.save()
        except Exception as exc:
            raise FreeCADDocumentError(f"Could not save {doc.FileName}:\n{exc}") from exc
        # App.Document.save() leaves the GUI document's Modified flag set in
        # FreeCAD 1.1 (only the Std_Save command clears it), so clear it here
        # or the exit prompt would ask again for a document just saved.
        try:
            modules.gui.getDocument(name).Modified = False
        except Exception:
            LOGGER.debug("Could not clear the Modified flag of FreeCAD document %s", name, exc_info=True)


# ----------------------------------------------------------------------
# process singleton
# ----------------------------------------------------------------------

_SESSION: FreeCADSession | None = None


def get_freecad_session() -> FreeCADSession:
    """Return the process-wide session, creating it (uninitialized) on first use."""
    global _SESSION
    if _SESSION is None:
        _SESSION = FreeCADSession()
    return _SESSION


def peek_freecad_session() -> FreeCADSession | None:
    """Return the session if one was ever created, without creating it."""
    return _SESSION
