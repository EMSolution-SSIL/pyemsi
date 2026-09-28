"""
VSCode-style Explorer dock widget for pyemsi.

Shows directory contents in a QTreeView backed by QFileSystemModel.
Displays an empty-state page with a Ctrl+O hint when no directory is open.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QFile, QItemSelectionModel, QMimeData, QModelIndex, QPoint, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QFileSystemModel,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QStackedWidget,
    QStyle,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from pyemsi.widgets.explorer_icons import MaterialFileIconProvider


_CUT_MIME = "application/x-pyemsi-cut"


def _is_within(path: str | Path, parent: str | Path) -> bool:
    """Return whether *path* is *parent* or one of its descendants."""
    path = os.path.normcase(os.path.realpath(path))
    parent = os.path.normcase(os.path.realpath(parent))
    try:
        return os.path.commonpath((path, parent)) == parent
    except ValueError:  # Different Windows drives.
        return False


def _top_level_paths(paths: list[str]) -> list[str]:
    """Remove duplicates and children whose parent is already selected."""
    result: list[str] = []
    for path in sorted({os.path.abspath(path) for path in paths}, key=lambda value: (len(Path(value).parts), value)):
        if not any(_is_within(path, parent) for parent in result):
            result.append(path)
    return result


def _unique_destination(path: Path, *, copy_label: bool = False) -> Path:
    """Return a non-existing sibling path using normal file-manager naming."""
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    if copy_label:
        candidate = path.with_name(f"{stem} - Copy{suffix}")
        number = 2
        while candidate.exists():
            candidate = path.with_name(f"{stem} - Copy ({number}){suffix}")
            number += 1
        return candidate
    number = 2
    candidate = path.with_name(f"{stem} ({number}){suffix}")
    while candidate.exists():
        number += 1
        candidate = path.with_name(f"{stem} ({number}){suffix}")
    return candidate


class _ExplorerTreeView(QTreeView):
    """Tree view that delegates filesystem drops to :class:`ExplorerWidget`."""

    paths_dropped = Signal(list, str, bool)

    def __init__(self) -> None:
        super().__init__()
        self.root_path = ""

    @staticmethod
    def _local_paths(event) -> list[str]:
        return [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]

    def _drop_directory(self, event) -> str:
        model = self.model()
        if not isinstance(model, QFileSystemModel):
            return ""
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            return self.root_path
        path = model.filePath(index)
        return path if model.isDir(index) else str(Path(path).parent)

    def _drop_action(self, event) -> Qt.DropAction:
        control = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        return Qt.DropAction.CopyAction if event.source() is not self or control else Qt.DropAction.MoveAction

    def dragEnterEvent(self, event) -> None:
        if self._local_paths(event):
            action = self._drop_action(event)
            event.setDropAction(action)
            super().dragEnterEvent(event)
            event.setDropAction(action)
            event.accept()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        if self._local_paths(event) and self._drop_directory(event):
            action = self._drop_action(event)
            event.setDropAction(action)
            super().dragMoveEvent(event)
            event.setDropAction(action)
            event.accept()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event) -> None:
        paths = self._local_paths(event)
        destination = self._drop_directory(event)
        if not paths or not destination:
            event.ignore()
            return
        action = self._drop_action(event)
        self.paths_dropped.emit(paths, destination, action == Qt.DropAction.CopyAction)
        event.setDropAction(action)
        event.accept()


class ExplorerWidget(QWidget):
    """
    VSCode-style file system explorer widget.

    Two states:
    - Empty: hint to open a folder via Ctrl+O or the toolbar button.
    - Tree: QTreeView showing the opened directory.

    Signals:
        file_activated(str): full path of a double-clicked file.
        open_folder_requested(): user wants to open a folder.
    """

    file_activated = Signal(str)
    open_folder_requested = Signal()
    terminal_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_path: str | None = None
        self._model: QFileSystemModel | None = None
        self._context_index = QModelIndex()
        self._context_path: str | None = None
        self._workspace_open = False
        self._create_actions()
        self._setup_ui()
        self._set_actions_enabled(False)
        app = QApplication.instance()
        if app is not None:
            app.clipboard().dataChanged.connect(self._update_paste_action)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_path(self) -> str | None:
        """The currently displayed directory, or None if not set."""
        return self._current_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_directory(self, path: str) -> None:
        """Switch the tree view to display *path*."""
        self._current_path = path

        if self._model is None:
            self._model = QFileSystemModel(self)
            self._model.setReadOnly(False)
            self._icon_provider = MaterialFileIconProvider()
            self._model.setIconProvider(self._icon_provider)
            self._tree.setModel(self._model)
            # Show only the Name column
            for col in range(1, self._model.columnCount()):
                self._tree.hideColumn(col)
            self._tree.doubleClicked.connect(self._on_item_double_clicked)
            self._tree.selectionModel().selectionChanged.connect(self._update_selection_actions)

        root_index = self._model.setRootPath(path)
        self._tree.setRootIndex(root_index)
        self._tree.root_path = path
        self._root_label.setText(Path(path).name.upper() or path.upper())
        self._set_actions_enabled(True)
        self._stack.setCurrentWidget(self._tree_page)

    def clear(self) -> None:
        """Reset the explorer to the empty (no folder) state."""
        self._current_path = None
        if self._model is not None:
            self._tree.setModel(None)
            self._model.deleteLater()
            self._model = None
        self._tree.root_path = ""
        self._root_label.clear()
        self._set_actions_enabled(False)
        self._stack.setCurrentWidget(self._empty_page)

    # ------------------------------------------------------------------
    # Internal setup
    # ------------------------------------------------------------------

    def _create_actions(self) -> None:
        self._new_file_action = QAction(QIcon(":/icons/material/document.svg"), "New File...", self)
        self._new_file_action.setToolTip("New File")
        self._new_file_action.triggered.connect(lambda: self._new_file(self._selected_parent_dir()))

        self._new_folder_action = QAction(QIcon(":/icons/material/folder-base.svg"), "New Folder...", self)
        self._new_folder_action.setToolTip("New Folder")
        self._new_folder_action.triggered.connect(lambda: self._new_folder(self._selected_parent_dir()))

        self._refresh_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Refresh", self
        )
        self._refresh_action.setToolTip("Refresh Explorer")
        self._refresh_action.triggered.connect(self._refresh)

        self._collapse_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp), "Collapse All", self
        )
        self._collapse_action.setToolTip("Collapse All Folders")
        self._collapse_action.triggered.connect(self._collapse_all)

        self._open_action = QAction("Open", self)
        self._open_action.triggered.connect(self._open_context_item)

        self._rename_action = QAction("Rename...", self)
        self._rename_action.setShortcut(QKeySequence("F2"))
        self._rename_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._rename_action.triggered.connect(lambda: self._rename_item(self._context_or_current_index()))
        self.addAction(self._rename_action)

        trash_text = "Move to Recycle Bin" if sys.platform == "win32" else "Move to Trash"
        self._trash_action = QAction(trash_text, self)
        self._trash_action.setShortcut(QKeySequence.StandardKey.Delete)
        self._trash_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._trash_action.triggered.connect(self._trash_selected)
        self.addAction(self._trash_action)

        self._reveal_action = QAction(QIcon(":/icons/FolderOpen.svg"), "Open in File Explorer", self)
        self._reveal_action.triggered.connect(lambda: self._open_in_explorer(self._context_or_root_path()))

        self._terminal_action = QAction(QIcon(":/icons/ExternalTerminal.svg"), "Open in Terminal", self)
        self._terminal_action.triggered.connect(self._open_context_terminal)

        self._copy_relative_action = QAction("Copy Relative Path", self)
        self._copy_relative_action.triggered.connect(lambda: self._copy_relative_path(self._context_or_root_path()))

        self._copy_full_action = QAction("Copy Full Path", self)
        self._copy_full_action.triggered.connect(lambda: self._copy_full_path(self._context_or_root_path()))

        self._cut_action = QAction(QIcon(":/icons/Cut.svg"), "Cut", self)
        self._cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self._cut_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._cut_action.triggered.connect(self._cut_selected)
        self.addAction(self._cut_action)

        self._copy_action = QAction(QIcon(":/icons/Copy.svg"), "Copy", self)
        self._copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self._copy_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._copy_action.triggered.connect(self._copy_selected)
        self.addAction(self._copy_action)

        self._paste_action = QAction(QIcon(":/icons/Paste.svg"), "Paste", self)
        self._paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self._paste_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._paste_action.triggered.connect(self._paste_selected)
        self.addAction(self._paste_action)

        self._duplicate_action = QAction("Duplicate", self)
        self._duplicate_action.setShortcut(QKeySequence("Ctrl+D"))
        self._duplicate_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._duplicate_action.triggered.connect(self._duplicate_selected)
        self.addAction(self._duplicate_action)

    def _set_actions_enabled(self, enabled: bool) -> None:
        self._workspace_open = enabled
        for action in (
            self._new_file_action,
            self._new_folder_action,
            self._refresh_action,
            self._collapse_action,
            self._reveal_action,
            self._terminal_action,
            self._copy_relative_action,
            self._copy_full_action,
        ):
            action.setEnabled(enabled)
        self._update_selection_actions()
        self._update_paste_action()

    def _update_selection_actions(self, *_args) -> None:
        has_selection = self._workspace_open and bool(self._selected_paths())
        for action in (
            self._open_action,
            self._rename_action,
            self._trash_action,
            self._cut_action,
            self._copy_action,
            self._duplicate_action,
        ):
            action.setEnabled(has_selection)

    def _update_paste_action(self, *_args) -> None:
        self._paste_action.setEnabled(self._workspace_open and bool(self._clipboard_paths()))

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        self._empty_page = self._build_empty_page()
        self._stack.addWidget(self._empty_page)

        self._tree_page = self._build_tree_page()
        self._stack.addWidget(self._tree_page)

        self._stack.setCurrentWidget(self._empty_page)

    def _build_empty_page(self) -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.setSpacing(0)

        no_folder = QLabel("No folder opened")
        no_folder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_folder.setStyleSheet("color: palette(mid); font-size: 13px;")
        vl.addWidget(no_folder)

        hint = QLabel("Press <b>Ctrl+O</b> to open a folder\nor click the folder icon above.")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: palette(mid); font-size: 11px;")
        hint.setWordWrap(True)
        vl.addWidget(hint)

        return page

    def _build_tree_page(self) -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        toolbar = QWidget(page)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 3, 4, 3)
        toolbar_layout.setSpacing(1)

        self._root_label = QLabel(toolbar)
        self._root_label.setStyleSheet("font-size: 11px; font-weight: 600;")
        toolbar_layout.addWidget(self._root_label, 1)

        for action in (
            self._new_file_action,
            self._new_folder_action,
            self._refresh_action,
            self._collapse_action,
        ):
            button = QToolButton(toolbar)
            button.setAutoRaise(True)
            button.setIconSize(QSize(18, 18))
            button.setDefaultAction(action)
            toolbar_layout.addWidget(button)
        vl.addWidget(toolbar)

        self._tree = _ExplorerTreeView()
        self._tree.setHeaderHidden(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(12)
        self._tree.setIconSize(QSize(18, 18))
        self._tree.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self._tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tree.setDragEnabled(True)
        self._tree.setAcceptDrops(True)
        self._tree.viewport().setAcceptDrops(True)
        self._tree.setDropIndicatorShown(True)
        self._tree.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self._tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._tree.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self._tree.setStyleSheet("QTreeView::item { padding-top: 1px; padding-bottom: 1px; font-size: 12px; }")
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        self._tree.paths_dropped.connect(
            lambda paths, destination, copy: self._transfer_paths(paths, destination, copy=copy)
        )
        vl.addWidget(self._tree)

        return page

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        if self._model is None or self._model.isDir(index):
            return
        self.file_activated.emit(self._model.filePath(index))

    def _show_context_menu(self, pos: QPoint) -> None:
        """Build and show a context menu depending on what was right-clicked."""
        if self._model is None or self._current_path is None:
            return

        index = self._tree.indexAt(pos)
        menu = QMenu(self)

        self._context_index = index

        if index.isValid():
            selection = self._tree.selectionModel()
            if selection is not None and not selection.isSelected(index):
                selection.setCurrentIndex(
                    index,
                    QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows,
                )
            item_path = self._model.filePath(index)
            self._context_path = item_path
            single_selection = len(self._selected_paths()) == 1
            self._open_action.setEnabled(single_selection)
            self._rename_action.setEnabled(single_selection)

            menu.addAction(self._open_action)
            menu.addSeparator()
            menu.addAction(self._new_file_action)
            menu.addAction(self._new_folder_action)
            menu.addSeparator()
            menu.addAction(self._cut_action)
            menu.addAction(self._copy_action)
            menu.addAction(self._paste_action)
            menu.addAction(self._duplicate_action)
            menu.addSeparator()
            menu.addAction(self._rename_action)
            menu.addAction(self._trash_action)
            menu.addSeparator()
            menu.addAction(self._reveal_action)
            menu.addAction(self._terminal_action)
            menu.addSeparator()
            menu.addAction(self._copy_relative_action)
            menu.addAction(self._copy_full_action)
        else:
            # Empty space — actions apply to root directory
            self._context_path = self._current_path
            menu.addAction(self._new_file_action)
            menu.addAction(self._new_folder_action)
            menu.addAction(self._paste_action)
            menu.addSeparator()
            menu.addAction(self._refresh_action)
            menu.addAction(self._collapse_action)
            menu.addSeparator()
            menu.addAction(self._reveal_action)
            menu.addAction(self._terminal_action)

        menu.exec(self._tree.viewport().mapToGlobal(pos))
        self._context_index = QModelIndex()
        self._context_path = None
        self._update_selection_actions()
        self._update_paste_action()

    def _context_or_current_index(self) -> QModelIndex:
        return self._context_index if self._context_index.isValid() else self._tree.currentIndex()

    def _context_or_root_path(self) -> str:
        return self._context_path or self._current_path or ""

    def _selected_paths(self) -> list[str]:
        if self._model is None:
            return []
        selection = self._tree.selectionModel()
        indexes = selection.selectedRows(0) if selection is not None else []
        if self._context_index.isValid() and self._context_index not in indexes:
            indexes = [self._context_index]
        return _top_level_paths([self._model.filePath(index) for index in indexes if index.isValid()])

    @staticmethod
    def _clipboard_paths() -> list[str]:
        app = QApplication.instance()
        if app is None:
            return []
        return [url.toLocalFile() for url in app.clipboard().mimeData().urls() if url.isLocalFile()]

    def _selected_parent_dir(self) -> str:
        if self._model is None or self._current_path is None:
            return ""
        if self._context_path and not self._context_index.isValid():
            return self._context_path if os.path.isdir(self._context_path) else str(Path(self._context_path).parent)
        index = self._context_or_current_index()
        if not index.isValid():
            return self._current_path
        path = self._model.filePath(index)
        return path if self._model.isDir(index) else str(Path(path).parent)

    def _open_context_item(self) -> None:
        if self._model is None:
            return
        index = self._context_or_current_index()
        if not index.isValid():
            return
        if self._model.isDir(index):
            self._tree.setExpanded(index, not self._tree.isExpanded(index))
        else:
            self.file_activated.emit(self._model.filePath(index))

    def _open_context_terminal(self) -> None:
        path = self._context_or_root_path()
        if path:
            directory = path if os.path.isdir(path) else str(Path(path).parent)
            self.terminal_requested.emit(directory)

    def _collapse_all(self) -> None:
        self._tree.collapseAll()

    def _refresh(self) -> None:
        if self._model is None or self._current_path is None:
            return
        root_index = self._model.setRootPath(self._current_path)
        self._tree.setRootIndex(root_index)
        self._tree.viewport().update()

    # ------------------------------------------------------------------
    # Context menu action implementations
    # ------------------------------------------------------------------

    def _set_file_clipboard(self, paths: list[str], *, cut: bool) -> None:
        app = QApplication.instance()
        if app is None or not paths:
            return
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(path) for path in paths])
        if cut:
            mime.setData(_CUT_MIME, b"1")
        app.clipboard().setMimeData(mime)

    def _cut_selected(self) -> None:
        self._set_file_clipboard(self._selected_paths(), cut=True)

    def _copy_selected(self) -> None:
        self._set_file_clipboard(self._selected_paths(), cut=False)

    def _paste_selected(self) -> None:
        app = QApplication.instance()
        destination = self._selected_parent_dir()
        if app is None or not destination:
            return
        mime = app.clipboard().mimeData()
        paths = self._clipboard_paths()
        cut = mime.hasFormat(_CUT_MIME)
        self._transfer_paths(paths, destination, copy=not cut)
        if cut and not any(Path(path).exists() for path in paths):
            app.clipboard().clear()

    def _duplicate_selected(self) -> None:
        for path in self._selected_paths():
            self._transfer_paths([path], str(Path(path).parent), copy=True, duplicate=True)

    def _ask_conflict(self, source: Path, destination: Path) -> tuple[str, bool]:
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle("File Already Exists")
        box.setText(f"'{destination.name}' already exists in this location.")
        box.setInformativeText(f"Choose what to do with '{source.name}'.")
        replace = box.addButton("Replace", QMessageBox.ButtonRole.AcceptRole)
        keep_both = box.addButton("Keep Both", QMessageBox.ButtonRole.ActionRole)
        skip = box.addButton("Skip", QMessageBox.ButtonRole.DestructiveRole)
        cancel = box.addButton(QMessageBox.StandardButton.Cancel)
        apply_all = QCheckBox("Apply to all conflicts")
        box.setCheckBox(apply_all)
        box.setDefaultButton(keep_both)
        box.setEscapeButton(cancel)
        box.exec()
        choice = {
            replace: "replace",
            keep_both: "keep_both",
            skip: "skip",
            cancel: "cancel",
        }.get(box.clickedButton(), "cancel")
        return choice, apply_all.isChecked()

    def _transfer_paths(
        self,
        paths: list[str],
        destination_dir: str,
        *,
        copy: bool,
        duplicate: bool = False,
    ) -> None:
        destination_root = Path(destination_dir)
        if not destination_root.is_dir():
            return

        errors: list[str] = []
        policy: str | None = None
        cancelled = False

        def transfer(source: Path, destination: Path) -> None:
            nonlocal policy, cancelled
            if cancelled:
                return

            source_is_dir = source.is_dir() and not source.is_symlink()
            if source_is_dir and destination.is_dir() and not destination.is_symlink():
                for child in source.iterdir():
                    transfer(child, destination / child.name)
                if not copy:
                    try:
                        source.rmdir()
                    except OSError:
                        pass  # Skipped children keep the source folder non-empty.
                return

            if destination.exists():
                choice = policy
                if choice is None:
                    choice, apply_all = self._ask_conflict(source, destination)
                    if apply_all and choice != "cancel":
                        policy = choice
                if choice == "cancel":
                    cancelled = True
                    return
                if choice == "skip":
                    return
                if choice == "keep_both":
                    destination = _unique_destination(destination)
                elif not QFile.moveToTrash(str(destination)):
                    raise OSError(f"Could not replace '{destination}'")

            if copy:
                if source_is_dir:
                    shutil.copytree(source, destination, symlinks=True)
                else:
                    shutil.copy2(source, destination, follow_symlinks=False)
            else:
                shutil.move(str(source), str(destination))

        for source_name in _top_level_paths(paths):
            source = Path(source_name)
            if not source.exists():
                continue
            destination = destination_root / source.name
            same_path = os.path.normcase(os.path.realpath(source)) == os.path.normcase(os.path.realpath(destination))
            if same_path:
                if not copy:
                    continue
                destination = _unique_destination(destination, copy_label=True)
            if source.is_dir() and _is_within(destination_root, source):
                errors.append(f"Cannot place '{source.name}' inside itself.")
                continue
            if duplicate:
                destination = _unique_destination(destination, copy_label=True)
            try:
                transfer(source, destination)
            except (OSError, shutil.Error) as exc:
                errors.append(f"{source.name}: {exc}")

        if errors:
            detail = "\n".join(errors[:8])
            if len(errors) > 8:
                detail += f"\n…and {len(errors) - 8} more"
            QMessageBox.critical(self, "File Operation Failed", detail)

    def _new_file(self, parent_dir: str) -> None:
        """Prompt for a file name, create it inside *parent_dir*, and open it."""
        name, ok = QInputDialog.getText(self, "New File", "File name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if os.sep in name or (os.altsep and os.altsep in name):
            QMessageBox.critical(self, "Invalid Name", "File name must not contain path separators.")
            return
        dest = Path(parent_dir) / name
        if dest.exists():
            QMessageBox.critical(self, "Already Exists", f"'{name}' already exists.")
            return
        try:
            dest.touch()
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not create file:\n{exc}")
            return
        self.file_activated.emit(str(dest))

    def _new_folder(self, parent_dir: str) -> None:
        """Prompt for a folder name and create it inside *parent_dir*."""
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if os.sep in name or (os.altsep and os.altsep in name):
            QMessageBox.critical(self, "Invalid Name", "Folder name must not contain path separators.")
            return
        dest = Path(parent_dir) / name
        if dest.exists():
            QMessageBox.critical(self, "Already Exists", f"'{name}' already exists.")
            return
        try:
            dest.mkdir()
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not create folder:\n{exc}")

    def _rename_item(self, index: QModelIndex) -> None:
        """Prompt for a new name and rename the item at *index*."""
        if self._model is None:
            return
        old_path = self._model.filePath(index)
        old_name = self._model.fileName(index)
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()
        if new_name == old_name:
            return
        if os.sep in new_name or (os.altsep and os.altsep in new_name):
            QMessageBox.critical(self, "Invalid Name", "Name must not contain path separators.")
            return
        new_path = str(Path(old_path).parent / new_name)
        if Path(new_path).exists():
            QMessageBox.critical(self, "Already Exists", f"'{new_name}' already exists.")
            return
        try:
            os.rename(old_path, new_path)
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not rename:\n{exc}")

    def _trash_selected(self) -> None:
        """Ask for confirmation then move the selected items to the trash."""
        paths = self._selected_paths()
        if not paths:
            return
        if len(paths) == 1:
            prompt = f"Move '{Path(paths[0]).name}' to the "
        else:
            prompt = f"Move {len(paths)} selected items to the "

        answer = QMessageBox.question(
            self,
            "Move to Recycle Bin" if sys.platform == "win32" else "Move to Trash",
            prompt + ("Recycle Bin?" if sys.platform == "win32" else "Trash?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        failed = [path for path in paths if not QFile.moveToTrash(path)]
        if failed:
            names = "\n".join(Path(path).name for path in failed)
            QMessageBox.critical(self, "Error", f"Could not move these items to trash:\n{names}")

    def _copy_full_path(self, path: str) -> None:
        """Copy the absolute path to the system clipboard."""
        app = QApplication.instance()
        if app is not None:
            app.clipboard().setText(os.path.abspath(path))

    def _copy_relative_path(self, path: str) -> None:
        """Copy the path relative to the current workspace root to the clipboard."""
        app = QApplication.instance()
        if app is not None and self._current_path is not None:
            rel = os.path.relpath(path, self._current_path)
            app.clipboard().setText(rel)

    def _open_in_explorer(self, path: str) -> None:
        """Reveal *path* in the system file manager."""
        abs_path = os.path.abspath(path)
        try:
            if sys.platform == "win32":
                if os.path.isfile(abs_path):
                    # /select,<path> highlights the file in Explorer
                    subprocess.Popen(["explorer", f"/select,{abs_path}"])
                elif os.path.isdir(abs_path):
                    os.startfile(abs_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", abs_path])
            else:
                # For Linux: open the containing folder if it's a file
                target = abs_path if os.path.isdir(abs_path) else str(Path(abs_path).parent)
                subprocess.Popen(["xdg-open", target])
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Could not open file explorer:\n{exc}")
