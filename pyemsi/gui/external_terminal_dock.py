"""Dock widget hosting tabbed external terminal sessions."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QLabel,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QIcon

from pyemsi.widgets.xterm import XtermWidget


class ExternalTerminalDock(QDockWidget):
    """Bottom dock that holds one or more :class:`XtermWidget` tabs.

    Each call to :meth:`add_terminal` creates a new tab backed by its
    own PTY process.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("External Terminal", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        self.setWindowIcon(QIcon(":/icons/ExternalTerminal.svg"))

        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.tabCloseRequested.connect(self._close_tab)
        self._tabs.setTabShape(QTabWidget.TabShape.Rounded)

        self._empty_page = self._build_empty_page()

        self._stack = QStackedWidget()
        self._stack.addWidget(self._empty_page)
        self._stack.addWidget(self._tabs)
        self._stack.setCurrentWidget(self._empty_page)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack)
        self.setWidget(container)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_terminal(
        self,
        title: str = "Terminal",
        cmd: str | None = None,
        args: list[str] | None = None,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> XtermWidget:
        """Create a new terminal tab and start a process in it.

        Returns the :class:`XtermWidget` instance.
        """
        xterm = XtermWidget(parent=self._tabs)
        idx = self._tabs.addTab(xterm, title)
        self._tabs.setCurrentIndex(idx)
        self._stack.setCurrentWidget(self._tabs)

        # Mark tab title when process exits
        xterm.processFinished.connect(lambda code, w=xterm: self._on_process_finished(w, code))

        xterm.start_process(cmd=cmd, args=args, cwd=cwd, env=env)
        return xterm

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _on_process_finished(self, widget: XtermWidget, exitcode: int) -> None:
        idx = self._tabs.indexOf(widget)
        if idx < 0:
            return
        current_title = self._tabs.tabText(idx)
        self._tabs.setTabText(idx, f"{current_title} (exited: {exitcode})")

    def _close_tab(self, index: int) -> None:
        widget: XtermWidget = self._tabs.widget(index)
        if widget is not None:
            widget.kill()
            widget.close()
        self._tabs.removeTab(index)
        if self._tabs.count() == 0:
            self._stack.setCurrentWidget(self._empty_page)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        for i in range(self._tabs.count()):
            widget: XtermWidget = self._tabs.widget(i)
            if widget is not None:
                widget.kill()
        super().closeEvent(event)

    @staticmethod
    def _build_empty_page() -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.setSpacing(0)

        title = QLabel("No running terminals")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: palette(mid); font-size: 13px;")
        vl.addWidget(title)

        hint = QLabel("Open a Python file and click <b>\u25b6 Run External</b>\nto run it in a new terminal tab.")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: palette(mid); font-size: 11px;")
        hint.setWordWrap(True)
        vl.addWidget(hint)

        return page
