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
from pyemsi.settings import SettingsManager


class PyEmsiMainWindow(QMainWindow):
    """
    Main application window for the pyemsi GUI.

    Central widget is a SplitContainer (two-panel tabbed area).
    Bottom dock widget hosts an embedded IPython terminal.
    """

    def __init__(self, parent=None, settings_manager: SettingsManager | None = None):
        super().__init__(parent)
        self._settings = settings_manager or SettingsManager()
        self._show_maximized_on_launch = True
        self.setWindowTitle("pyemsi")
        self.setWindowIcon(QIcon(":/icons/Icon.svg"))
        self.resize(1400, 900)

        self._container = SplitContainer()
        self.setCentralWidget(self._container)

        self._setup_menu_bar()
        self._setup_explorer()

        self._ipython_dock = QDockWidget("IPython Terminal", self)
        self._ipython_dock.setObjectName("ipython_terminal_dock")
        self._ipython_dock.setWindowIcon(QIcon(":/icons/IPythonTerminal.svg"))
        self._ipython_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        self._ipython_widget = None
        self._kernel_manager = None
        self._active_external_terminals: dict = {}

        self._setup_ipython_terminal()

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._ipython_dock)

        self._external_terminal_dock = ExternalTerminalDock(self)
        self._external_terminal_dock.setObjectName("external_terminal_dock")
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._external_terminal_dock)
        self.tabifyDockWidget(self._ipython_dock, self._external_terminal_dock)
        self._ipython_dock.hide()
        self._external_terminal_dock.hide()

        self._setup_view_menu()
        self._apply_window_settings()
        self._refresh_recent_folders_menu()

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

    @property
    def settings_manager(self) -> SettingsManager:
        """The layered settings manager for the GUI."""
        return self._settings

    def should_show_maximized_on_launch(self) -> bool:
        """Return whether the window should start maximized."""
        return self._show_maximized_on_launch

    def _setup_menu_bar(self) -> None:
        """Add a File menu with Open Folder (Ctrl+O) and Save (Ctrl+S)."""
        self._file_menu = self.menuBar().addMenu("&File")
        open_action = QAction("Open &Folder...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.setIcon(QIcon(":/icons/FolderOpen.svg"))
        open_action.triggered.connect(self._open_folder)
        self._file_menu.addAction(open_action)

        self._recent_menu = self._file_menu.addMenu("Open &Recent")
        self._recent_menu.setIcon(QIcon(":/icons/FolderOpen.svg"))
        self._refresh_recent_folders_menu()

        self._file_menu.addSeparator()

        self._settings_menu = self._file_menu.addMenu("&Settings")
        self._settings_menu.setIcon(QIcon(":/icons/Settings.svg"))

        self._open_global_settings_action = QAction("Open &Global Settings", self)
        self._open_global_settings_action.triggered.connect(self._open_global_settings)
        self._settings_menu.addAction(self._open_global_settings_action)

        self._open_workspace_settings_action = QAction("Open &Workspace Settings", self)
        self._open_workspace_settings_action.triggered.connect(self._open_workspace_settings)
        self._settings_menu.addAction(self._open_workspace_settings_action)

        self._update_settings_actions()

        self._file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.setIcon(QIcon(":/icons/Save.svg"))
        save_action.triggered.connect(self._save_active_tab)
        self._file_menu.addAction(save_action)

        save_all_action = QAction("Save A&ll", self)
        save_all_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_all_action.setIcon(QIcon(":/icons/SaveAll.svg"))
        save_all_action.triggered.connect(self._save_all_tabs)
        self._file_menu.addAction(save_all_action)

    def _refresh_recent_folders_menu(self) -> None:
        """Rebuild the Open Recent submenu from global settings."""
        self._recent_menu.clear()
        recent_folders = self._settings.get_global("app.recent_folders") or []

        for path in recent_folders:
            action = QAction(path, self)
            action.triggered.connect(lambda _checked=False, recent_path=path: self._open_recent_folder(recent_path))
            self._recent_menu.addAction(action)

        self._recent_menu.addSeparator()
        clear_action = QAction("Clear Recently Opened", self)
        clear_action.triggered.connect(self._clear_recent_folders)
        clear_action.setEnabled(bool(recent_folders))
        self._recent_menu.addAction(clear_action)

    def _open_recent_folder(self, path: str) -> None:
        """Open a folder from the recent-folders submenu."""
        if os.path.isdir(path):
            self._set_workspace_path(path)

    def _clear_recent_folders(self) -> None:
        """Clear the global recent-folders list and update the menu."""
        self._settings.clear_recent_folders()
        self._settings.save()
        self._refresh_recent_folders_menu()

    def _setup_view_menu(self) -> None:
        """Add a View menu with toggles for the Explorer and Terminal docks."""
        view_menu = self.menuBar().addMenu("&View")

        explorer_action = self._explorer_dock.toggleViewAction()
        explorer_action.setIcon(QIcon(":/icons/Explorer.svg"))
        explorer_action.setShortcut(QKeySequence("Ctrl+E"))
        view_menu.addAction(explorer_action)

        ipython_action = self._ipython_dock.toggleViewAction()
        ipython_action.setIcon(QIcon(":/icons/IPythonTerminal.svg"))
        ipython_action.setShortcut(QKeySequence("Ctrl+I"))
        view_menu.addAction(ipython_action)

        external_action = self._external_terminal_dock.toggleViewAction()
        external_action.setIcon(QIcon(":/icons/ExternalTerminal.svg"))
        external_action.setShortcut(QKeySequence("Ctrl+T"))
        view_menu.addAction(external_action)

    def _setup_explorer(self) -> None:
        """Create the Explorer dock widget and wire its signals."""
        self._explorer_widget = ExplorerWidget()
        self._explorer_widget.setMinimumWidth(200)
        self._explorer_widget.open_folder_requested.connect(self._open_folder)
        self._explorer_widget.file_activated.connect(self._on_file_activated)

        self._explorer_dock = QDockWidget("Explorer", self)
        self._explorer_dock.setObjectName("explorer_dock")
        self._explorer_dock.setWindowIcon(QIcon(":/icons/Explorer.svg"))
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
            self._set_workspace_path(path)

    def _set_workspace_path(self, path: str) -> None:
        """Switch the active workspace path and update persisted context."""
        normalized_path = os.path.abspath(os.path.normpath(path))
        self._settings.add_recent_folder(normalized_path)
        self._settings.load_workspace(normalized_path)
        self._refresh_recent_folders_menu()
        self._update_settings_actions()

        explorer_root = self._settings.get_local("workbench.explorer.root_path") or normalized_path
        self._explorer_widget.set_directory(explorer_root)
        self._settings.set_local("workbench.explorer.root_path", explorer_root)

        self.setWindowTitle(f"pyemsi — {normalized_path}")

    def _update_settings_actions(self) -> None:
        """Refresh settings-menu action state for the current workspace context."""
        global_settings_path = self._settings.global_settings_path
        local_settings_path = self._settings.local_settings_path
        self._open_global_settings_action.setEnabled(global_settings_path.is_file())
        self._open_workspace_settings_action.setEnabled(
            local_settings_path is not None and local_settings_path.is_file()
        )

    def _open_global_settings(self) -> None:
        """Open the global settings file in an editor tab."""
        path = self._settings.global_settings_path
        if not path.is_file():
            return
        self._container.open_file(os.fspath(path))

    def _open_workspace_settings(self) -> None:
        """Open the active workspace settings file in an editor tab."""
        path = self._settings.local_settings_path
        if path is None or not path.is_file():
            return
        self._container.open_file(os.fspath(path))

    def _on_file_activated(self, path: str) -> None:
        """Open *path* in a viewer tab, or focus the existing tab if already open."""
        viewer = self._container.open_file(path)

        from pyemsi.gui.file_viewers import PythonViewer, EMSolutionInputViewer

        if isinstance(viewer, PythonViewer):
            # Connect only once – guard via a dynamic attribute.
            if not getattr(viewer, "_run_connected", False):
                viewer.run_ipython_requested.connect(self._run_python_file_ipython)
                viewer.run_external_requested.connect(self._run_python_file_external)
                viewer.stop_external_requested.connect(self._stop_python_file_external)
                viewer._run_connected = True

        elif isinstance(viewer, EMSolutionInputViewer):
            if not getattr(viewer, "_run_connected", False):
                viewer.run_external_requested.connect(self._run_emsol_external)
                viewer.stop_external_requested.connect(self._stop_emsol_external)
                viewer._run_connected = True

    @staticmethod
    def _is_saveable_viewer(widget) -> bool:
        """
        Return True if *widget* satisfies the editor save contract.

        A widget is considered saveable when it both:
        - exposes a non-empty ``file_path`` attribute, and
        - provides a callable ``save`` attribute (method).
        """
        file_path = getattr(widget, "file_path", None)
        return bool(file_path) and callable(getattr(widget, "save", None))

    def _save_active_tab(self) -> None:
        """Save the currently-focused Monaco editor tab."""
        for panel in (self._container.left_panel, self._container.right_panel):
            widget = panel.currentWidget()
            if self._is_saveable_viewer(widget):
                widget.save()
                return

    def _save_all_tabs(self) -> None:
        """Save all open editor tabs in both panels."""
        for panel in (self._container.left_panel, self._container.right_panel):
            for i in range(panel.count()):
                widget = panel.widget(i)
                if self._is_saveable_viewer(widget):
                    widget.save()

    def _setup_ipython_terminal(self):
        """Create the in-process IPython kernel and terminal widget."""
        from pyemsi.gui.ipython_terminal_widget import create_ipython_terminal

        self._ipython_widget, self._kernel_manager = create_ipython_terminal(namespace=self._build_namespace())
        self._ipython_dock.setWidget(self._ipython_widget)

    def _build_namespace(self) -> dict:
        """Build the initial namespace for the IPython kernel."""
        import pyemsi

        return {"pyemsi": pyemsi}

    def _apply_window_settings(self) -> None:
        """Apply persisted global window preferences."""
        dock_visibility = self._settings.get_effective("workbench.window.dock_visibility") or {}
        self._explorer_dock.setVisible(dock_visibility.get("explorer", True))
        self._ipython_dock.setVisible(dock_visibility.get("ipython", False))
        self._external_terminal_dock.setVisible(dock_visibility.get("external_terminal", False))

        maximized = self._settings.get_global("workbench.window.maximized")
        if maximized is not None:
            self._show_maximized_on_launch = bool(maximized)

    def _persist_workspace_state(self) -> None:
        """Persist global window preferences and workspace-local explorer state."""
        self._settings.set_global("workbench.window.maximized", self.isMaximized())
        self._settings.set_global(
            "workbench.window.dock_visibility",
            {
                "explorer": self._explorer_dock.isVisible(),
                "ipython": self._ipython_dock.isVisible(),
                "external_terminal": self._external_terminal_dock.isVisible(),
            },
        )

        current_workspace = self.explorer.current_path
        if current_workspace and os.path.isdir(current_workspace):
            self._settings.load_workspace(current_workspace)
            self._settings.set_local("workbench.explorer.root_path", current_workspace)

        self._settings.save()

    def _run_python_file_ipython(self, path: str) -> None:
        """Execute a Python file in the embedded IPython terminal."""
        import os

        cwd = self.explorer.current_path
        if cwd and os.path.isdir(cwd):
            self._kernel_manager.kernel.shell.run_cell(f"import os; os.chdir({cwd!r})", silent=True)
        self._ipython_widget.execute(f"%run {path}")

    def _stop_python_file_external(self) -> None:
        """Terminate the external terminal process for the requesting viewer."""
        viewer = self.sender()
        xterm = self._active_external_terminals.get(id(viewer))
        if xterm is not None:
            xterm.kill()

    def _run_python_file_external(self, path: str) -> None:
        """Execute a Python file in a new external terminal tab."""
        import sys

        viewer = self.sender()
        cwd = self.explorer.current_path or os.path.dirname(path)
        title = os.path.basename(path)

        if viewer is not None:
            viewer.set_external_running(True)

        self._external_terminal_dock.show()
        self._external_terminal_dock.raise_()
        xterm = self._external_terminal_dock.add_terminal(
            title=title,
            cmd=sys.executable,
            args=[path],
            cwd=cwd,
        )

        if viewer is not None:
            self._active_external_terminals[id(viewer)] = xterm
            xterm.processFinished.connect(
                lambda _code, v=viewer: (
                    v.set_external_running(False),
                    self._active_external_terminals.pop(id(v), None),
                )
            )

    def _stop_emsol_external(self) -> None:
        """Terminate the external pyemsol process for the requesting viewer."""
        viewer = self.sender()
        xterm = self._active_external_terminals.get(id(viewer))
        if xterm is not None:
            xterm.kill()

    def _run_emsol_external(self, path: str) -> None:
        """Run an EMSolution input file via pyemsol in an external terminal."""
        import sys

        viewer = self.sender()
        cwd = os.path.dirname(path)
        title = f"pyemsol — {os.path.basename(path)}"

        if viewer is not None:
            viewer.set_external_running(True)

        run_emsol_script = os.path.join(os.path.dirname(__file__), os.pardir, "tools", "run_emsol.py")

        self._external_terminal_dock.show()
        self._external_terminal_dock.raise_()
        xterm = self._external_terminal_dock.add_terminal(
            title=title,
            cmd=sys.executable,
            args=[run_emsol_script, path],
            cwd=cwd,
        )

        if viewer is not None:
            self._active_external_terminals[id(viewer)] = xterm
            xterm.processFinished.connect(
                lambda _code, v=viewer: (
                    v.set_external_running(False),
                    self._active_external_terminals.pop(id(v), None),
                )
            )

    def push_to_namespace(self, **kwargs):
        """Push additional variables into the IPython kernel namespace."""
        if self._kernel_manager is not None:
            self._kernel_manager.kernel.shell.push(kwargs)

    def closeEvent(self, event):
        """Clean up kernel on close."""
        self._persist_workspace_state()
        if self._kernel_manager is not None:
            self._kernel_manager.shutdown_kernel()
        super().closeEvent(event)
