"""
Main application window for the pyemsi GUI.

Provides PyEmsiMainWindow with a SplitContainer central widget and
a bottom dock hosting an embedded IPython terminal.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDockWidget, QMainWindow

import pyemsi.resources.resources  # noqa: F401
from pyemsi.split_container import SplitContainer


class PyEmsiMainWindow(QMainWindow):
    """
    Main application window for the pyemsi GUI.

    Central widget is a SplitContainer (two-panel tabbed area).
    Bottom dock widget hosts an embedded IPython terminal.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("pyemsi")
        self.setWindowIcon(QIcon(":/icons/Icon.svg"))
        self.resize(1400, 900)

        self._container = SplitContainer()
        self.setCentralWidget(self._container)

        self._terminal_dock = QDockWidget("Terminal", self)
        self._terminal_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea
        )
        self._terminal_widget = None
        self._kernel_manager = None

        self._setup_terminal()

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._terminal_dock)

    @property
    def container(self) -> SplitContainer:
        """The SplitContainer (central widget)."""
        return self._container

    @property
    def terminal(self):
        """The embedded IPython RichJupyterWidget."""
        return self._terminal_widget

    def _setup_terminal(self):
        """Create the in-process IPython kernel and terminal widget."""
        from pyemsi.gui.terminal_widget import create_terminal_widget

        self._terminal_widget, self._kernel_manager = create_terminal_widget(namespace=self._build_namespace())
        self._terminal_dock.setWidget(self._terminal_widget)

    def _build_namespace(self) -> dict:
        """Build the initial namespace for the IPython kernel."""
        import pyemsi
        # import pyemsi.gui as gui_module

        return {
            "pyemsi": pyemsi,
            # "gui": gui_module,
            # "window": self,
            # "container": self._container,
        }

    def push_to_namespace(self, **kwargs):
        """Push additional variables into the IPython kernel namespace."""
        if self._kernel_manager is not None:
            self._kernel_manager.kernel.shell.push(kwargs)

    def closeEvent(self, event):
        """Clean up kernel on close."""
        if self._kernel_manager is not None:
            self._kernel_manager.shutdown_kernel()
        super().closeEvent(event)
