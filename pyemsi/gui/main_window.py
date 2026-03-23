"""
Main application window for the pyemsi GUI.

Provides PyEmsiMainWindow with a SplitContainer central widget and
a bottom dock hosting an embedded IPython terminal.
"""

from __future__ import annotations

import json
import os
import tempfile

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QDockWidget, QFileDialog, QMainWindow, QMenu, QMessageBox, QToolBar, QToolButton

import pyemsi.resources.resources  # noqa: F401
from pyemsi.gui.emsolution_output_plot_builder_dialog import EMSolutionOutputPlotBuilderDialog
from pyemsi.gui.field_plot_builder_dialog import FieldPlotBuilderDialog
from pyemsi.widgets.explorer_widget import ExplorerWidget
from pyemsi.widgets.split_container import SplitContainer
from pyemsi.gui.external_terminal_dock import ExternalTerminalDock
from pyemsi.gui.femap_converter_dialog import (
    FemapConverterDialog,
    FemapConverterDialogConfig,
)
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

        self.menuBar().setStyleSheet("QMenuBar { padding: 0px; } QMenuBar::item { padding: 2px 8px; }")
        self._setup_file_actions()
        self._setup_menu_bar()
        self._setup_file_toolbar()
        self._setup_edit_menu()
        self._setup_explorer()

        self._ipython_dock = QDockWidget("IPython Terminal", self)
        self._ipython_dock.setObjectName("ipython_terminal_dock")
        self._ipython_dock.setWindowIcon(QIcon(":/icons/IPythonTerminal.svg"))
        self._ipython_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        self._ipython_widget = None
        self._kernel_manager = None
        self._active_external_terminals: dict = {}
        self._temp_converter_configs: set[str] = set()

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

    def _setup_file_actions(self) -> None:
        """Create reusable File-menu actions and submenus."""
        self._open_folder_action = QAction(QIcon(":/icons/FolderOpen.svg"), "Open &Folder...", self)
        self._open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        self._open_folder_action.triggered.connect(self._open_folder)

        self._recent_menu = QMenu("Open &Recent", self)
        self._recent_menu.setIcon(QIcon(":/icons/History.svg"))

        self._open_femap_converter_action = QAction(QIcon(":/icons/VTK.svg"), "Convert &FEMAP", self)
        self._open_femap_converter_action.triggered.connect(self._open_femap_converter_dialog)

        self._open_field_plot_action = QAction(QIcon(":/icons/Field.svg"), "&Field Plot", self)
        self._open_field_plot_action.triggered.connect(self._open_field_plot_dialog)

        self._open_emsolution_output_plot_action = QAction(QIcon(":/icons/Graph.svg"), "&Output Plot", self)
        self._open_emsolution_output_plot_action.triggered.connect(self._open_emsolution_output_plot_dialog)

        self._save_action = QAction(QIcon(":/icons/Save.svg"), "&Save", self)
        self._save_action.setShortcut(QKeySequence("Ctrl+S"))
        self._save_action.triggered.connect(self._save_active_tab)

        self._save_all_action = QAction(QIcon(":/icons/SaveAll.svg"), "Save A&ll", self)
        self._save_all_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self._save_all_action.triggered.connect(self._save_all_tabs)

        self._close_tab_action = QAction("Close &Tab", self)
        self._close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        self._close_tab_action.triggered.connect(self._container.close_current_tab)

        self._close_all_action = QAction("Close &All Tabs", self)
        self._close_all_action.triggered.connect(self._container.close_all_tabs)

        self._close_workspace_action = QAction("Close &Workspace", self)
        self._close_workspace_action.triggered.connect(lambda: self.close_workspace(restart_kernel=True))

        self._settings_menu = QMenu("&Settings", self)
        self._settings_menu.setIcon(QIcon(":/icons/Settings.svg"))

        self._open_global_settings_action = QAction("Open &Global Settings", self)
        self._open_global_settings_action.triggered.connect(self._open_global_settings)
        self._settings_menu.addAction(self._open_global_settings_action)

        self._open_workspace_settings_action = QAction("Open &Workspace Settings", self)
        self._open_workspace_settings_action.triggered.connect(self._open_workspace_settings)
        self._settings_menu.addAction(self._open_workspace_settings_action)

        self._exit_action = QAction("E&xit", self)
        self._exit_action.setShortcut(QKeySequence("Alt+F4"))
        self._exit_action.triggered.connect(self.close)

    def _setup_menu_bar(self) -> None:
        """Add a File menu with Open Folder (Ctrl+O) and Save (Ctrl+S)."""
        self._file_menu = self.menuBar().addMenu("&File")
        self._file_menu.addAction(self._open_folder_action)

        self._file_menu.addMenu(self._recent_menu)
        self._refresh_recent_folders_menu()

        self._file_menu.addSeparator()

        self._file_menu.addAction(self._open_femap_converter_action)

        self._file_menu.addAction(self._open_field_plot_action)

        self._file_menu.addAction(self._open_emsolution_output_plot_action)

        self._file_menu.addSeparator()

        self._file_menu.addAction(self._save_action)

        self._file_menu.addAction(self._save_all_action)

        self._file_menu.addSeparator()

        self._file_menu.addAction(self._close_tab_action)

        self._file_menu.addAction(self._close_all_action)

        self._file_menu.addAction(self._close_workspace_action)

        self._file_menu.addSeparator()

        self._file_menu.addMenu(self._settings_menu)

        self._update_settings_actions()

        self._file_menu.addSeparator()

        self._file_menu.addAction(self._exit_action)

    def _setup_file_toolbar(self) -> None:
        """Add an always-visible toolbar for workspace file actions."""
        self._file_toolbar = QToolBar("File Actions", self)
        self._file_toolbar.setObjectName("file_toolbar")
        self._file_toolbar.setMovable(False)
        self._file_toolbar.setFloatable(False)
        self._file_toolbar.setIconSize(QSize(16, 16))
        self._file_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        self._file_toolbar.addAction(self._open_folder_action)
        self._open_recent_tool_button = self._create_toolbar_menu_button(
            self._recent_menu,
            "Open recent folders",
            "open_recent_tool_button",
        )
        self._file_toolbar.addWidget(self._open_recent_tool_button)
        self._file_toolbar.addSeparator()
        self._file_toolbar.addAction(self._open_femap_converter_action)
        self._file_toolbar.addAction(self._open_field_plot_action)
        self._file_toolbar.addAction(self._open_emsolution_output_plot_action)
        self._file_toolbar.addSeparator()
        self._settings_tool_button = self._create_toolbar_menu_button(
            self._settings_menu,
            "Open settings menu",
            "settings_tool_button",
        )
        self._file_toolbar.addWidget(self._settings_tool_button)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._file_toolbar)

    def _create_toolbar_menu_button(self, menu: QMenu, tooltip: str, object_name: str) -> QToolButton:
        """Create a toolbar button that opens *menu* as a dropdown."""
        button = QToolButton(self)
        button.setObjectName(object_name)
        button.setAutoRaise(True)
        button.setIcon(menu.icon())
        button.setText(menu.title().replace("&", ""))
        button.setToolTip(tooltip)
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        button.setMenu(menu)
        return button

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

    def _setup_edit_menu(self) -> None:
        """Add an Edit menu delegating actions to the active Monaco editor."""
        edit_menu = self.menuBar().addMenu("&Edit")

        _ACTIONS = [
            ("&Undo", "Ctrl+Z", "undo", ":/icons/Undo.svg"),
            ("&Redo", "Ctrl+Y", "redo", ":/icons/Redo.svg"),
            None,
            ("Cu&t", "Ctrl+X", "editor.action.clipboardCutAction", ":/icons/Cut.svg"),
            (
                "&Copy",
                "Ctrl+C",
                "editor.action.clipboardCopyAction",
                ":/icons/Copy.svg",
            ),
            (
                "&Paste",
                "Ctrl+V",
                "editor.action.clipboardPasteAction",
                ":/icons/Paste.svg",
            ),
            None,
            ("&Find", "Ctrl+F", "actions.find", ":/icons/Find.svg"),
            (
                "&Replace",
                "Ctrl+H",
                "editor.action.startFindReplaceAction",
                ":/icons/Replace.svg",
            ),
            None,
            (
                "Toggle &Line Comment",
                "Ctrl+/",
                "editor.action.commentLine",
                ":/icons/Comment.svg",
            ),
            (
                "Toggle &Block Comment",
                "Shift+Alt+A",
                "editor.action.blockComment",
                ":/icons/Code.svg",
            ),
            None,
            (
                "Select &All",
                "Ctrl+A",
                "editor.action.selectAll",
                ":/icons/SelectAll.svg",
            ),
        ]

        for item in _ACTIONS:
            if item is None:
                edit_menu.addSeparator()
                continue
            label, shortcut_hint, action_id, icon_path = item
            action = QAction(QIcon(icon_path), f"{label}\t{shortcut_hint}", self)
            action.triggered.connect(lambda checked=False, _id=action_id: self._dispatch_edit_action(_id))
            edit_menu.addAction(action)

    def _dispatch_edit_action(self, action_id: str) -> None:
        """Send *action_id* to the currently active Monaco editor, if any."""
        editor = self._container.active_monaco_editor()
        if editor is not None:
            editor.execute_editor_action(action_id)

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

        view_menu.addSeparator()

        restart_kernel_action = QAction("Restart IPython &Kernel", self)
        restart_kernel_action.setIcon(QIcon(":/icons/IPythonTerminal.svg"))
        restart_kernel_action.triggered.connect(self._reset_ipython_kernel)
        view_menu.addAction(restart_kernel_action)

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

    def _open_femap_converter_dialog(self) -> None:
        """Open the FEMAP conversion dialog and launch a conversion if accepted."""
        dialog = FemapConverterDialog(self._settings, parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        config = dialog.config()
        if config is None:
            return

        self._persist_femap_converter_settings(config)
        self._run_femap_converter(config)

    def _open_field_plot_dialog(self) -> None:
        """Open the field plot builder dialog."""
        current_path = self.explorer.current_path
        if not current_path or not os.path.isdir(current_path):
            return

        dialog = FieldPlotBuilderDialog(
            self._settings,
            browse_dir_getter=lambda: self.explorer.current_path,
            parent=self,
        )
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _open_emsolution_output_plot_dialog(self) -> None:
        """Open the EMSolution output plot builder for output.json in the current explorer directory."""
        current_path = self.explorer.current_path
        if not current_path or not os.path.isdir(current_path):
            return

        output_path = os.path.join(current_path, "output.json")
        if not os.path.isfile(output_path):
            QMessageBox.warning(
                self,
                "Missing EMSolution Output",
                f"Could not find output.json in:\n\n{current_path}",
            )
            return

        try:
            dialog = EMSolutionOutputPlotBuilderDialog(output_path, parent=self)
        except Exception as exc:
            QMessageBox.critical(self, "Invalid EMSolution Output", str(exc))
            return

        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        self._emsolution_output_plot_dialog = dialog

    def _persist_femap_converter_settings(self, config: FemapConverterDialogConfig) -> None:
        """Persist the last-used FEMAP converter dialog settings."""
        setter = self._settings.set_local if self._settings.workspace_path is not None else self._settings.set_global
        for key, value in config.to_settings().items():
            setter(key, value)
        self._settings.save()

    def _run_femap_converter(self, config: FemapConverterDialogConfig) -> None:
        """Launch the FEMAP converter in an external terminal tab."""
        import sys

        config_path = self._write_femap_converter_config(config)
        run_converter_script = os.path.join(os.path.dirname(__file__), os.pardir, "tools", "run_femap_converter.py")

        self._external_terminal_dock.show()
        self._external_terminal_dock.raise_()
        xterm = self._external_terminal_dock.add_terminal(
            title=f"FemapConverter - {config.output_name}",
            cmd=sys.executable,
            args=[run_converter_script, "--config", config_path],
            cwd=config.input_dir,
        )
        xterm.processFinished.connect(lambda _code, path=config_path: self._cleanup_temp_converter_config(path))

    def _write_femap_converter_config(self, config: FemapConverterDialogConfig) -> str:
        """Serialize a converter launch payload to a temporary JSON file."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            prefix="pyemsi_femap_converter_",
            suffix=".json",
        ) as handle:
            json.dump(config.to_payload(), handle, indent=2, sort_keys=True)
            config_path = os.path.abspath(os.path.normpath(handle.name))
        self._temp_converter_configs.add(config_path)
        return config_path

    def _cleanup_temp_converter_config(self, path: str) -> None:
        """Remove a temporary converter payload file if it still exists."""
        normalized_path = os.path.abspath(os.path.normpath(path))
        self._temp_converter_configs.discard(normalized_path)
        try:
            if os.path.isfile(normalized_path):
                os.unlink(normalized_path)
        except OSError:
            pass

    def close_workspace(self, restart_kernel: bool = False) -> bool:
        """Reset the application to a fresh state.

        Closes all editor tabs, kills external terminals, optionally restarts
        the IPython kernel, clears the file explorer, and unloads workspace
        settings.

        Parameters
        ----------
        restart_kernel:
            When *True* (explicit "Close Workspace" action) the embedded
            IPython kernel is restarted.  Pass *False* when called internally
            from :meth:`_set_workspace_path` to avoid an extra restart cycle.
        """
        if not self._container.close_all_tabs():
            return False
        self._external_terminal_dock.close_all_terminals()

        if restart_kernel:
            self._reset_ipython_kernel()

        self._explorer_widget.clear()
        self._settings.load_workspace(None)
        self._update_settings_actions()
        self.setWindowTitle("pyemsi")
        return True

    def _reset_ipython_kernel(self) -> None:
        """Reset the in-process IPython shell to a clean state."""
        if self._kernel_manager is None:
            return
        self._kernel_manager.kernel.shell.reset(new_session=True)
        self._kernel_manager.kernel.shell.push(self._build_namespace())
        if self._ipython_widget is not None:
            self._ipython_widget.reset(clear=True)

    def _set_workspace_path(self, path: str) -> None:
        """Switch the active workspace path and update persisted context."""
        if not self.close_workspace(restart_kernel=True):
            return
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
        self._open_femap_converter_action.setEnabled(self._settings.workspace_path is not None)
        explorer_widget = getattr(self, "_explorer_widget", None)
        explorer_path = getattr(explorer_widget, "current_path", None) or (
            os.fspath(self._settings.workspace_path) if self._settings.workspace_path is not None else None
        )
        self._open_field_plot_action.setEnabled(bool(explorer_path and os.path.isdir(explorer_path)))
        self._open_emsolution_output_plot_action.setEnabled(bool(explorer_path and os.path.isdir(explorer_path)))
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
        if dock_visibility.get("ipython", False):
            self._ipython_dock.raise_()

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
        if not self._container.close_all_tabs():
            event.ignore()
            return

        self._persist_workspace_state()
        for path in list(self._temp_converter_configs):
            self._cleanup_temp_converter_config(path)
        self._external_terminal_dock.close_all_terminals()
        if self._kernel_manager is not None:
            self._kernel_manager.shutdown_kernel()
        super().closeEvent(event)
