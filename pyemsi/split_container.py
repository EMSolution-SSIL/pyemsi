"""
split_tab_area.py
=================
A two-panel tab split widget for PySide6.

Layout
------
SplitContainer
 └─ QSplitter (horizontal)
      ├─ _TabPanel (left)   ← always visible; default target for add_tab()
      └─ _TabPanel (right)  ← hidden until first "Move to Right Panel"

Usage
-----
    from PySide6.QtWidgets import QApplication, QLabel
    from pyemsi.split_tab_area import SplitContainer

    app = QApplication([])
    container = SplitContainer()
    container.add_tab(QLabel("Hello"), "tab1")
    container.add_tab(QLabel("World"), "tab2")
    container.show()
    app.exec()

Right-click a tab to:
  • Move to Left Panel  - moves the tab to the left panel (shows it if hidden)
  • Move to Right Panel - moves the tab to the right panel
  • Close Tab
  • Close Others
  • Close All
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


# ---------------------------------------------------------------------------
# _TabPanel
# ---------------------------------------------------------------------------


class _TabPanel(QTabWidget):
    """
    Internal tab panel used by SplitContainer.

    ``tab_move_requested(widget, title, direction)`` is emitted when the user
    chooses to move a tab, where *direction* is ``"left"`` or ``"right"``.
    ``last_tab_closed`` is emitted when the last tab is removed via the close
    button (not when tabs are moved away programmatically).
    """

    tab_move_requested = Signal(QWidget, str, str)  # widget, title, direction
    last_tab_closed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self._close_tab)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Set by SplitContainer to identify which side this panel occupies.
        self._is_left: bool = False

    # ------------------------------------------------------------------
    # private helpers
    # ------------------------------------------------------------------

    def _close_tab(self, index: int) -> None:
        widget = self.widget(index)
        self.removeTab(index)
        if widget is not None:
            widget.deleteLater()
        if self.count() == 0:
            self.last_tab_closed.emit()

    def _tab_index_at(self, local_pos) -> int:
        """Return the tab index under *local_pos*, or currentIndex() as fallback."""
        bar = self.tabBar()
        for i in range(self.count()):
            if bar.tabRect(i).contains(bar.mapFrom(self, local_pos)):
                return i
        return self.currentIndex()

    def _show_context_menu(self, pos) -> None:
        index = self._tab_index_at(pos)
        if index < 0:
            return

        widget = self.widget(index)
        title = self.tabText(index)
        menu = QMenu(self)

        # Show only the action that moves to the *other* panel.
        if not self._is_left:
            move_left = menu.addAction("Move to Left Panel")
            move_left.triggered.connect(lambda: self.tab_move_requested.emit(widget, title, "left"))
        else:
            move_right = menu.addAction("Move to Right Panel")
            move_right.triggered.connect(lambda: self.tab_move_requested.emit(widget, title, "right"))

        menu.addSeparator()

        close_action = menu.addAction("Close Tab")
        close_action.triggered.connect(lambda: self._close_tab(index))

        close_others = menu.addAction("Close Others")
        close_others.triggered.connect(lambda: self._close_others(index))

        close_all = menu.addAction("Close All")
        close_all.triggered.connect(self._close_all)

        menu.exec(self.mapToGlobal(pos))

    def _close_others(self, keep_index: int) -> None:
        # Collect indices first; close high-to-low to avoid index shifting.
        to_close = [i for i in range(self.count()) if i != keep_index]
        for i in sorted(to_close, reverse=True):
            self._close_tab(i)

    def _close_all(self) -> None:
        while self.count():
            self._close_tab(0)


# ---------------------------------------------------------------------------
# SplitContainer
# ---------------------------------------------------------------------------


class SplitContainer(QWidget):
    """
    A widget that holds two _TabPanels side-by-side in a QSplitter.

    The right panel is hidden by default and shown when a tab is first moved
    into it.  It auto-hides again when its last tab is closed or moved away.
    The left panel is always visible and acts as the primary panel.

    Public API
    ----------
    add_tab(widget, title)   Add a tab to the left (primary) panel.
    left_panel               The left (primary) _TabPanel.
    right_panel              The right _TabPanel (always exists, may be hidden).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._splitter.setChildrenCollapsible(False)
        layout.addWidget(self._splitter)

        self._left = _TabPanel(self)
        self._left._is_left = True

        self._right = _TabPanel(self)
        self._right._is_left = False

        self._splitter.addWidget(self._left)
        self._splitter.addWidget(self._right)

        # Right panel starts hidden; it appears on the first move-to-right.
        self._right.hide()

        self._left.tab_move_requested.connect(self._on_tab_move_requested)
        self._right.tab_move_requested.connect(self._on_tab_move_requested)
        self._left.last_tab_closed.connect(self._on_left_emptied)
        self._right.last_tab_closed.connect(self._on_right_emptied)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    @property
    def left_panel(self) -> _TabPanel:
        return self._left

    @property
    def right_panel(self) -> _TabPanel:
        return self._right

    def add_tab(self, widget: QWidget, title: str) -> None:
        """Add *widget* as a new tab in the left (primary) panel."""
        self._left.addTab(widget, title)
        self._left.setCurrentWidget(widget)

    # ------------------------------------------------------------------
    # private helpers
    # ------------------------------------------------------------------

    def _show_panel(self, panel: _TabPanel) -> None:
        """Show *panel* if hidden and equalize splitter sizes."""
        if not panel.isVisible():
            panel.show()
            total = self._splitter.width() or 800
            half = total // 2
            self._splitter.setSizes([half, total - half])

    def _on_tab_move_requested(self, widget: QWidget, title: str, direction: str) -> None:
        if direction == "right":
            idx = self._left.indexOf(widget)
            if idx != -1:
                self._left.removeTab(idx)
            self._right.addTab(widget, title)
            self._right.setCurrentWidget(widget)
            self._show_panel(self._right)
            if self._left.count() == 0:
                self._left.hide()
        else:  # "left"
            idx = self._right.indexOf(widget)
            if idx != -1:
                self._right.removeTab(idx)
            self._left.addTab(widget, title)
            self._left.setCurrentWidget(widget)
            self._show_panel(self._left)
            if self._right.count() == 0:
                self._right.hide()

    def _on_right_emptied(self) -> None:
        """Called when the last tab in the right panel is *closed* by the user."""
        self._right.hide()

    def _on_left_emptied(self) -> None:
        """
        Called when the last tab in the left panel is *closed* by the user.
        Rescue any remaining right-panel tabs by moving them to the left, then
        hide the now-empty right panel.
        """
        while self._right.count():
            w = self._right.widget(0)
            t = self._right.tabText(0)
            self._right.removeTab(0)
            self._left.addTab(w, t)
        self._left.show()
        self._right.hide()


# ---------------------------------------------------------------------------
# Quick demo (python -m pyemsi.split_container)
# ---------------------------------------------------------------------------


def _demo() -> None:
    app = QApplication.instance() or QApplication([])

    win = QMainWindow()
    win.setWindowTitle("SplitContainer demo")
    win.resize(900, 500)

    container = SplitContainer()
    for i in range(1, 6):
        container.add_tab(QLabel(f"Content of tab {i}"), f"Tab {i}")

    win.setCentralWidget(container)
    win.show()
    app.exec()


if __name__ == "__main__":
    _demo()
