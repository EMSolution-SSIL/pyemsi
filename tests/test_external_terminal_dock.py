from __future__ import annotations

from PySide6.QtWidgets import QApplication

from pyemsi.gui.external_terminal_dock import ExternalTerminalDock
from pyemsi.widgets.xterm import XtermWidget


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_add_log_tab_creates_process_free_terminal_tab():
    _app()
    dock = ExternalTerminalDock()

    xterm = dock.add_log_tab("FreeCAD messages")

    assert isinstance(xterm, XtermWidget)
    assert xterm.is_alive is False
    assert dock._tabs.count() == 1
    assert dock._tabs.tabText(0) == "FreeCAD messages"
    assert dock._tabs.currentWidget() is xterm
    assert dock._stack.currentWidget() is dock._tabs


def test_closing_log_tab_returns_to_empty_page():
    _app()
    dock = ExternalTerminalDock()
    dock.add_log_tab("FreeCAD messages")

    dock._close_tab(0)

    assert dock._tabs.count() == 0
    assert dock._stack.currentWidget() is dock._empty_page
