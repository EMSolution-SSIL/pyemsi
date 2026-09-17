"""Disposable pyemsi tab shell that hosts the shared FreeCAD GUI."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget

if TYPE_CHECKING:
    from pyemsi.gui.freecad_session import FreeCADSession

LOGGER = logging.getLogger(__name__)


class FreeCADViewer(QWidget):
    """Tab widget that borrows the native FreeCAD main window from a session.

    The shell is disposable: closing it hands the native window back to the
    session's parking widget. It never deletes the native window itself and
    deliberately exposes no ``dirty``/``save`` API; unsaved FreeCAD documents
    are handled by ``PyEmsiMainWindow`` at application exit.
    """

    viewer_kind = "freecad"
    supports_panel_move = False  # honoured by _TabPanel context menu

    def __init__(self, session: FreeCADSession, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._current_path: str | None = None
        self._detached = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._session.attach(self)
        # PySide6 silently drops a bound method of the object being destroyed,
        # so the fallback must be a closure. It only fires if a caller skipped
        # close(); by then Qt has already deleted the shell's children, so this
        # is a last-resort bookkeeping hook, not the real guard (closeEvent is).
        shell = self
        self.destroyed.connect(lambda *_args: shell._detach_session())

    @property
    def session(self) -> FreeCADSession:
        return self._session

    @property
    def current_path(self) -> str | None:
        """Last path opened through this shell (for tab title purposes)."""
        return self._current_path

    def open_file(self, path: str) -> str:
        """Open or activate *path* in the shared session; returns the FreeCAD document name."""
        norm_path = os.path.abspath(os.path.normpath(path))
        name = self._session.open_document(norm_path)
        self._current_path = norm_path
        return name

    def _detach_session(self, *_args) -> None:
        if self._detached:
            return
        self._detached = True
        LOGGER.info("FreeCAD viewer shell closing")
        self._session.detach(self)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._detach_session()
        super().closeEvent(event)
