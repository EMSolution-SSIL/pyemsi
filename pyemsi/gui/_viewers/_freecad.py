"""Disposable pyemsi tab shell that hosts the shared FreeCAD GUI."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QLabel, QProgressBar, QStackedLayout, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from pyemsi.gui.freecad_session import FreeCADSession

LOGGER = logging.getLogger(__name__)


class FreeCADViewer(QWidget):
    """Tab widget that borrows the native FreeCAD main window from a session.

    The shell is disposable: closing it hands the native window back to the
    session's parking widget. It never deletes the native window itself.
    """

    viewer_kind = "freecad"
    supports_panel_move = False  # honoured by _TabPanel context menu
    dirtyChanged = Signal(bool)

    def __init__(self, session: FreeCADSession, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._current_path: str | None = None
        self._document_name: str | None = None
        self._dirty = False
        self._detached = False
        self._loading = True

        self._stack = QStackedLayout(self)
        self._stack.setContentsMargins(0, 0, 0, 0)

        self._loading_page = QWidget(self)
        loading_layout = QVBoxLayout(self._loading_page)
        loading_layout.addStretch()
        self._loading_label = QLabel("Loading FreeCAD…", self._loading_page)
        self._loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loading_label.setWordWrap(True)
        loading_layout.addWidget(self._loading_label)
        self._loading_bar = QProgressBar(self._loading_page)
        self._loading_bar.setRange(0, 0)
        loading_layout.addWidget(self._loading_bar)
        loading_layout.addStretch()
        self._stack.addWidget(self._loading_page)

        # PySide6 silently drops a bound method of the object being destroyed,
        # so the fallback must be a closure. It only fires if a caller skipped
        # close(); by then Qt has already deleted the shell's children, so this
        # is a last-resort bookkeeping hook, not the real guard (closeEvent is).
        shell = self
        self.destroyed.connect(lambda *_args: shell._detach_session())

        self._dirty_timer = QTimer(self)
        self._dirty_timer.setInterval(250)
        self._dirty_timer.timeout.connect(self._sync_dirty)
        self._dirty_timer.start()

    @property
    def session(self) -> FreeCADSession:
        return self._session

    @property
    def current_path(self) -> str | None:
        """Last path opened through this shell (for tab title purposes)."""
        return self._current_path

    @property
    def dirty(self) -> bool:
        return self._dirty

    @property
    def loading(self) -> bool:
        return self._loading

    def set_loading_message(self, message: str) -> None:
        self._loading_label.setText(message)

    def show_loading_error(self, message: str) -> None:
        self._loading = False
        self._loading_bar.hide()
        self._loading_label.setText(message)

    def open_file(self, path: str) -> str:
        """Open or activate *path* in the shared session; returns the FreeCAD document name."""
        return self._load_file(path, self._session.open_document)

    def create_file(self, path: str) -> str:
        """Create *path* in the shared session; returns the FreeCAD document name."""
        return self._load_file(path, self._session.create_document)

    def _load_file(self, path: str, load) -> str:
        norm_path = os.path.abspath(os.path.normpath(path))
        self._session.attach(self)
        self._stack.setCurrentWidget(self._loading_page)
        name = load(norm_path)
        self._current_path = norm_path
        self._document_name = name
        self._loading = False
        if self._session.main_window is not None:
            self._stack.setCurrentWidget(self._session.main_window)
        self._sync_dirty()
        return name

    def activate(self) -> str | None:
        """Borrow the shared FreeCAD window and show this shell's document."""
        if self._loading or self._current_path is None:
            return None
        self._session.attach(self)
        name = self._session.open_document(self._current_path)
        self._document_name = name
        self._sync_dirty()
        return name

    def save(self) -> None:
        """Save this shell's FreeCAD document through the shared session."""
        if self._document_name is None:
            return
        self._session.save_document(self._document_name)
        self._sync_dirty()

    def _sync_dirty(self) -> None:
        dirty = bool(self._document_name and self._session.is_document_modified(self._document_name))
        if dirty != self._dirty:
            self._dirty = dirty
            self.dirtyChanged.emit(dirty)

    def _detach_session(self, *_args) -> None:
        if self._detached:
            return
        self._detached = True
        LOGGER.info("FreeCAD viewer shell closing")
        self._session.detach(self)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._detach_session()
        super().closeEvent(event)
