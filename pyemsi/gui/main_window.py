"""
Main application window for the pyemsi GUI.

Provides PyEmsiMainWindow with a SplitContainer central widget and
a bottom dock hosting an embedded IPython terminal.
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QDockWidget, QFileDialog, QMainWindow

import pyemsi.resources.resources  # noqa: F401
from pyemsi.widgets.explorer_widget import ExplorerWidget
from pyemsi.widgets.split_container import SplitContainer
from pyemsi.gui.external_terminal_dock import ExternalTerminalDock


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

        self._setup_menu_bar()
        self._setup_explorer()

        self._ipython_dock = QDockWidget("IPython Terminal", self)
        self._ipython_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        self._ipython_widget = None
        self._kernel_manager = None

        self._setup_ipython_terminal()

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._ipython_dock)

        self._external_terminal_dock = ExternalTerminalDock(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._external_terminal_dock)
        self.tabifyDockWidget(self._ipython_dock, self._external_terminal_dock)
        self._ipython_dock.raise_()

        self._setup_view_menu()

    @property
    def container(self) -> SplitContainer:
        """The SplitContainer (central widget)."""
        return self._container

    @property
    def explorer(self) -> ExplorerWidget:
        """The Explorer dock widget."""
        return self._explorer_widget

    @property
    def ipython_terminal(self):
        """The embedded IPython RichJupyterWidget."""
        return self._ipython_widget

    def _setup_menu_bar(self) -> None:
        """Add a File menu with Open Folder (Ctrl+O) and Save (Ctrl+S)."""
        file_menu = self.menuBar().addMenu("&File")
        open_action = QAction("Open &Folder...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.setIcon(QIcon(":/icons/FolderOpen.svg"))
        open_action.triggered.connect(self._open_folder)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self._save_active_tab)
        file_menu.addAction(save_action)

    def _setup_view_menu(self) -> None:
        """Add a View menu with toggles for the Explorer and Terminal docks."""
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self._explorer_dock.toggleViewAction())
        view_menu.addAction(self._ipython_dock.toggleViewAction())
        view_menu.addAction(self._external_terminal_dock.toggleViewAction())

    def _setup_explorer(self) -> None:
        """Create the Explorer dock widget and wire its signals."""
        self._explorer_widget = ExplorerWidget()
        self._explorer_widget.setMinimumWidth(200)
        self._explorer_widget.open_folder_requested.connect(self._open_folder)
        self._explorer_widget.file_activated.connect(self._on_file_activated)

        self._explorer_dock = QDockWidget("Explorer", self)
        self._explorer_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self._explorer_dock.setWidget(self._explorer_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._explorer_dock)

    def _open_folder(self) -> None:
        """Prompt the user to pick a directory and open it in the Explorer."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Open Folder",
            os.getcwd(),
            QFileDialog.Option.ShowDirsOnly,
        )
        if path:
            self._explorer_widget.set_directory(path)
            folder_name = os.path.basename(path) or path
            self.setWindowTitle(f"pyemsi — {folder_name}")

    def _on_file_activated(self, path: str) -> None:
        """Open *path* in a viewer tab, or focus the existing tab if already open."""
        viewer = self._container.open_file(path)

        from pyemsi.gui.file_viewers import PythonViewer

        if isinstance(viewer, PythonViewer):
            # Connect only once – guard via a dynamic attribute.
            if not getattr(viewer, "_run_connected", False):
                viewer.run_requested.connect(self._run_python_file)
                viewer.run_external_requested.connect(self._run_python_file_external)
                viewer._run_connected = True

    def _save_active_tab(self) -> None:
        """Save the currently-focused Monaco editor tab."""
        from pyemsi.gui.file_viewers import MarkdownViewer, PythonViewer
        from pyemsi.widgets.monaco_lsp import MonacoLspWidget

        for panel in (self._container.left_panel, self._container.right_panel):
            widget = panel.currentWidget()
            if isinstance(widget, (MonacoLspWidget, MarkdownViewer, PythonViewer)) and widget.file_path:
                widget.save()
                return

    def _setup_ipython_terminal(self):
        """Create the in-process IPython kernel and terminal widget."""
        from pyemsi.gui.ipython_terminal_widget import create_ipython_terminal

        self._ipython_widget, self._kernel_manager = create_ipython_terminal(namespace=self._build_namespace())
        self._ipython_dock.setWidget(self._ipython_widget)

    def _build_namespace(self) -> dict:
        """Build the initial namespace for the IPython kernel."""
        import pyemsi

        return {"pyemsi": pyemsi}

    def _run_python_file(self, path: str) -> None:
        """Execute a Python file in the embedded IPython terminal."""
        import os

        cwd = self.explorer.current_path
        if cwd and os.path.isdir(cwd):
            self._kernel_manager.kernel.shell.run_cell(f"import os; os.chdir({cwd!r})", silent=True)
        self._ipython_widget.execute(f"%run {path}")

    def _run_python_file_external(self, path: str) -> None:
        """Execute a Python file in a new external terminal tab."""
        import sys

        cwd = self.explorer.current_path or os.path.dirname(path)
        title = os.path.basename(path)

        self._external_terminal_dock.show()
        self._external_terminal_dock.raise_()
        self._external_terminal_dock.add_terminal(
            title=title,
            cmd=sys.executable,
            args=[path],
            cwd=cwd,
        )

    def push_to_namespace(self, **kwargs):
        """Push additional variables into the IPython kernel namespace."""
        if self._kernel_manager is not None:
            self._kernel_manager.kernel.shell.push(kwargs)

    def closeEvent(self, event):
        """Clean up kernel on close."""
        if self._kernel_manager is not None:
            self._kernel_manager.shutdown_kernel()
        super().closeEvent(event)
