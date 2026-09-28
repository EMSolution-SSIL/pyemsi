"""Focused checks for the Explorer icon and toolbar behavior."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFile, QFileInfo, QMimeData, QModelIndex, QPointF, QSize, Qt, QUrl
from PySide6.QtGui import QDropEvent, QIcon
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QAbstractItemView, QApplication

from pyemsi.widgets.explorer_icons import MaterialFileIconProvider, icon_name_for_path
from pyemsi.widgets.explorer_widget import ExplorerWidget, _top_level_paths, _unique_destination


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _wait_for_index(widget: ExplorerWidget, path: str) -> QModelIndex:
    for _ in range(50):
        QApplication.processEvents()
        index = widget._model.index(path)
        if index.isValid():
            return index
        QTest.qWait(10)
    raise AssertionError(f"Explorer model did not load {path}")


def test_material_icon_associations_cover_pyemsi_formats() -> None:
    assert icon_name_for_path("project/.pyemsi", is_dir=True) == "folder-simulations"
    assert icon_name_for_path("mesh.vtu", is_dir=False) == "vtk"
    assert icon_name_for_path("assembly.FCStd", is_dir=False) == "freecad"
    assert icon_name_for_path("post_geom.neu", is_dir=False) == "simulink"
    assert icon_name_for_path("unknown.bin", is_dir=False) == "document"


def test_material_icon_provider_loads_bundled_icons(tmp_path) -> None:
    app = _app()
    python_file = tmp_path / "model.py"
    python_file.touch()

    provider = MaterialFileIconProvider()

    assert QFile.exists(":/icons/material/python.svg")
    assert QFile.exists(":/icons/FreeCAD.svg")
    icon = provider.icon(QFileInfo(str(python_file)))
    assert isinstance(icon, QIcon)
    assert provider._icons["python"] is icon
    assert app is QApplication.instance()


def test_explorer_uses_18px_icons_and_enables_toolbar(tmp_path) -> None:
    app = _app()
    widget = ExplorerWidget()
    try:
        assert widget._tree.iconSize() == QSize(18, 18)
        assert not widget._new_file_action.isEnabled()

        widget.set_directory(str(tmp_path))

        assert widget._new_file_action.isEnabled()
        assert widget._new_folder_action.isEnabled()
        assert widget._refresh_action.isEnabled()
        assert widget._collapse_action.isEnabled()
        assert widget._root_label.text() == tmp_path.name.upper()
        assert app is QApplication.instance()
    finally:
        widget.close()


def test_explorer_exposes_expected_context_commands_and_terminal_signal(tmp_path) -> None:
    _app()
    widget = ExplorerWidget()
    terminal_paths: list[str] = []
    widget.terminal_requested.connect(terminal_paths.append)
    try:
        widget.set_directory(str(tmp_path))
        widget._context_path = str(tmp_path)
        widget._open_context_terminal()

        assert widget._open_action.text() == "Open"
        assert widget._rename_action.text() == "Rename"
        assert widget._trash_action.text() in {"Move to Recycle Bin", "Move to Trash"}
        assert widget._copy_relative_action.text() == "Copy Relative Path"
        assert widget._copy_full_action.text() == "Copy Full Path"
        assert widget._cut_action.text() == "Cut"
        assert widget._copy_action.text() == "Copy"
        assert widget._paste_action.text() == "Paste"
        assert widget._duplicate_action.text() == "Duplicate"
        assert widget._tree.dragDropMode() == QAbstractItemView.DragDropMode.DragDrop
        assert widget._tree.defaultDropAction() == Qt.DropAction.MoveAction
        assert terminal_paths == [str(tmp_path)]
    finally:
        widget.close()


def test_file_operation_helpers_dedupe_nested_paths_and_name_copies(tmp_path) -> None:
    parent = tmp_path / "folder"
    child = parent / "child.txt"
    child.parent.mkdir()
    child.touch()

    assert _top_level_paths([str(child), str(parent), str(child)]) == [str(parent)]

    original = tmp_path / "model.FCStd"
    original.touch()
    assert _unique_destination(original, copy_label=True).name == "model - Copy.FCStd"
    (tmp_path / "model - Copy.FCStd").touch()
    assert _unique_destination(original, copy_label=True).name == "model - Copy (2).FCStd"


def test_transfer_supports_external_copy_internal_move_and_duplicate(tmp_path) -> None:
    _app()
    workspace = tmp_path / "workspace"
    destination = workspace / "destination"
    external = tmp_path / "external.txt"
    workspace.mkdir()
    destination.mkdir()
    external.write_text("external")

    widget = ExplorerWidget()
    try:
        widget.set_directory(str(workspace))
        widget._transfer_paths([str(external)], str(destination), copy=True)
        assert external.exists()
        assert (destination / "external.txt").read_text() == "external"

        internal = workspace / "internal.txt"
        internal.write_text("internal")
        widget._transfer_paths([str(internal)], str(destination), copy=False)
        assert not internal.exists()
        assert (destination / "internal.txt").read_text() == "internal"

        copied = destination / "external.txt"
        widget._transfer_paths([str(copied)], str(destination), copy=True, duplicate=True)
        assert (destination / "external - Copy.txt").read_text() == "external"
    finally:
        widget.close()


def test_folder_merge_conflict_supports_keep_both_and_apply_to_all(tmp_path, monkeypatch) -> None:
    _app()
    workspace = tmp_path / "workspace"
    incoming = tmp_path / "incoming"
    existing = workspace / "incoming"
    workspace.mkdir()
    incoming.mkdir()
    existing.mkdir()
    for name in ("a.txt", "b.txt"):
        (incoming / name).write_text("new")
        (existing / name).write_text("old")

    widget = ExplorerWidget()
    prompts: list[str] = []
    monkeypatch.setattr(
        widget,
        "_ask_conflict",
        lambda source, _destination: (prompts.append(source.name) or "keep_both", True),
    )
    try:
        widget.set_directory(str(workspace))
        widget._transfer_paths([str(incoming)], str(workspace), copy=True)

        assert prompts == ["a.txt"]
        assert (existing / "a.txt").read_text() == "old"
        assert (existing / "a (2).txt").read_text() == "new"
        assert (existing / "b (2).txt").read_text() == "new"
    finally:
        widget.close()


def test_clipboard_paste_copies_external_files_and_moves_cut_files(tmp_path) -> None:
    app = _app()
    workspace = tmp_path / "workspace"
    destination = workspace / "destination"
    external = tmp_path / "external.txt"
    workspace.mkdir()
    destination.mkdir()
    external.write_text("external")

    widget = ExplorerWidget()
    try:
        widget.set_directory(str(workspace))
        widget._context_path = str(destination)

        widget._set_file_clipboard([str(external)], cut=False)
        widget._paste_selected()
        assert external.exists()
        assert (destination / "external.txt").exists()

        internal = workspace / "internal.txt"
        internal.write_text("internal")
        widget._set_file_clipboard([str(internal)], cut=True)
        widget._paste_selected()
        assert not internal.exists()
        assert (destination / "internal.txt").exists()
        mime = app.clipboard().mimeData()
        assert mime is None or not mime.hasFormat("application/x-pyemsi-cut")
    finally:
        app.clipboard().clear()
        widget.close()


def test_external_drop_always_copies_into_workspace(tmp_path) -> None:
    _app()
    workspace = tmp_path / "workspace"
    external = tmp_path / "external.txt"
    workspace.mkdir()
    external.write_text("external")
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(external))])
    event = QDropEvent(
        QPointF(-1, -1),
        Qt.DropAction.CopyAction | Qt.DropAction.MoveAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    widget = ExplorerWidget()
    try:
        widget.set_directory(str(workspace))
        widget._tree.dropEvent(event)

        assert event.dropAction() == Qt.DropAction.CopyAction
        assert external.exists()
        assert (workspace / "external.txt").read_text() == "external"
    finally:
        widget.close()


def test_inline_file_creation_waits_for_enter_then_opens_file(tmp_path) -> None:
    _app()
    widget = ExplorerWidget()
    opened: list[str] = []
    widget.file_activated.connect(opened.append)
    try:
        widget.set_directory(str(tmp_path))
        widget._begin_inline_create("file")

        assert widget._inline_editor is not None
        assert list(tmp_path.iterdir()) == []

        widget._inline_editor.setText("model.py")
        widget._inline_editor.returnPressed.emit()

        created = tmp_path / "model.py"
        assert created.is_file()
        assert opened == [str(created)]
        assert widget._inline_editor is None
    finally:
        widget.close()


def test_inline_creation_escape_cancels_and_duplicate_name_stays_editable(tmp_path) -> None:
    _app()
    existing = tmp_path / "existing.txt"
    existing.touch()
    widget = ExplorerWidget()
    try:
        widget.set_directory(str(tmp_path))
        widget._begin_inline_create("file")
        editor = widget._inline_editor
        assert editor is not None
        editor.setText(existing.name)
        editor.returnPressed.emit()

        assert widget._inline_editor is editor
        assert "already exists" in editor.toolTip()

        QTest.keyClick(editor, Qt.Key.Key_Escape)
        assert widget._inline_editor is None
        assert [path.name for path in tmp_path.iterdir()] == [existing.name]
    finally:
        widget.close()


def test_inline_rename_selects_stem_only_and_commits(tmp_path) -> None:
    _app()
    original = tmp_path / "model.result.py"
    original.touch()
    widget = ExplorerWidget()
    try:
        widget.set_directory(str(tmp_path))
        index = _wait_for_index(widget, str(original))
        widget._tree.setCurrentIndex(index)
        widget._begin_inline_rename()

        editor = widget._inline_editor
        assert editor is not None
        assert editor.selectedText() == "model.result"

        editor.insert("renamed")
        editor.returnPressed.emit()
        assert not original.exists()
        assert (tmp_path / "renamed.py").is_file()
    finally:
        widget.close()


def test_inline_folder_creation_expands_the_new_folder(tmp_path, monkeypatch) -> None:
    _app()
    widget = ExplorerWidget()
    expanded: list[Path] = []
    try:
        widget.set_directory(str(tmp_path))
        original_expand = widget._tree.expand

        def record_expand(index: QModelIndex) -> None:
            expanded.append(Path(widget._model.filePath(index)))
            original_expand(index)

        monkeypatch.setattr(widget._tree, "expand", record_expand)
        widget._begin_inline_create("folder")
        assert widget._inline_editor is not None
        widget._inline_editor.setText("results")
        widget._inline_editor.returnPressed.emit()

        created = tmp_path / "results"
        assert created.is_dir()
        _wait_for_index(widget, str(created))
        for _ in range(60):
            QApplication.processEvents()
            if created in expanded:
                break
            QTest.qWait(10)
        assert created in expanded
    finally:
        widget.close()
