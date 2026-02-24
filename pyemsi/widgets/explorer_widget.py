"""
VSCode-style Explorer dock widget for pyemsi.

Shows directory contents in a QTreeView backed by QFileSystemModel.
Displays an empty-state page with a Ctrl+O hint when no directory is open.
"""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtWidgets import (
    QFileSystemModel,
    QLabel,
    QStackedWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


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

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_path: str | None = None
        self._model: QFileSystemModel | None = None
        self._setup_ui()

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
            self._tree.setModel(self._model)
            # Show only the Name column
            for col in range(1, self._model.columnCount()):
                self._tree.hideColumn(col)
            self._tree.doubleClicked.connect(self._on_item_double_clicked)

        root_index = self._model.setRootPath(path)
        self._tree.setRootIndex(root_index)
        self._stack.setCurrentWidget(self._tree_page)

    def refresh(self) -> None:
        """Re-read the current directory."""
        if self._current_path is not None:
            self.set_directory(self._current_path)

    def collapse_all(self) -> None:
        """Collapse all expanded tree nodes."""
        self._tree.collapseAll()

    # ------------------------------------------------------------------
    # Internal setup
    # ------------------------------------------------------------------

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

        self._tree = QTreeView()
        self._tree.setHeaderHidden(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(12)
        self._tree.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self._tree.setStyleSheet("QTreeView::item { padding-top: 1px; padding-bottom: 1px; font-size: 12px; }")
        vl.addWidget(self._tree)

        return page

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        if self._model is None or self._model.isDir(index):
            return
        self.file_activated.emit(self._model.filePath(index))
