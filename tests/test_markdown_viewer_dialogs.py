from __future__ import annotations

import os
import shutil
import sys
import types
from pathlib import Path
from uuid import uuid4

from PySide6.QtWidgets import QApplication, QWidget

# The local test environment may not have the compiled FEMAP extension.
if "pyemsi.core.femap_parser" not in sys.modules:
    femap_parser_stub = types.ModuleType("pyemsi.core.femap_parser")
    femap_parser_stub.FEMAPParser = object
    femap_parser_stub.FEMAPBlock = object
    sys.modules["pyemsi.core.femap_parser"] = femap_parser_stub

from pyemsi.gui._viewers import _markdown


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _StubSignal:
    def __init__(self) -> None:
        self._callbacks = []

    def connect(self, callback) -> None:
        self._callbacks.append(callback)

    def emit(self, value=None) -> None:
        for callback in list(self._callbacks):
            callback(value)


class _StubMonaco(QWidget):
    def __init__(self, language: str, parent=None) -> None:
        super().__init__(parent)
        self.language = language
        self.textChanged = _StubSignal()
        self.dirtyChanged = _StubSignal()
        self.syncStateChanged = _StubSignal()
        self.externalChangeChanged = _StubSignal()
        self.fileMissingChanged = _StubSignal()
        self.file_path = None
        self.dirty = False
        self.sync_state = "clean"
        self.has_external_change = False
        self.file_missing = False
        self.wrap_calls: list[tuple[str, str]] = []
        self.insert_calls: list[str] = []

    def setTheme(self, theme: str) -> None:
        self.theme = theme

    def wrapSelection(self, prefix: str, suffix: str) -> None:
        self.wrap_calls.append((prefix, suffix))

    def insertAtCursor(self, text: str) -> None:
        self.insert_calls.append(text)


class _StubLinkDialogUseSelection:
    def __init__(self, _parent) -> None:
        pass

    def exec(self) -> int:
        return _markdown.QDialog.DialogCode.Accepted

    def link_url(self) -> str:
        return "https://example.com"

    def link_label(self) -> str:
        return ""


class _StubLinkDialogWithLabel:
    def __init__(self, _parent) -> None:
        pass

    def exec(self) -> int:
        return _markdown.QDialog.DialogCode.Accepted

    def link_url(self) -> str:
        return "https://example.com/docs"

    def link_label(self) -> str:
        return "Docs"


class _StubImageDialogAbsolutePicked:
    def __init__(self, start_dir: str, parent=None) -> None:
        self.start_dir = start_dir
        self.parent = parent

    def exec(self) -> int:
        return _markdown.QDialog.DialogCode.Accepted

    def image_path(self) -> str:
        return self._image_path

    def alt_text(self) -> str:
        return "Logo"

    def selected_via_picker(self) -> bool:
        return True


class _StubImageDialogUnsavedTyped:
    def __init__(self, start_dir: str, parent=None) -> None:
        self.start_dir = start_dir
        self.parent = parent

    def exec(self) -> int:
        return _markdown.QDialog.DialogCode.Accepted

    def image_path(self) -> str:
        return r"images\logo.png"

    def alt_text(self) -> str:
        return "Alt"

    def selected_via_picker(self) -> bool:
        return False


def test_markdown_link_dialog_uses_selection_when_label_is_empty(monkeypatch):
    _app()
    monkeypatch.setattr(_markdown, "MonacoLspWidget", _StubMonaco)
    monkeypatch.setattr(_markdown, "_LinkInsertDialog", _StubLinkDialogUseSelection)

    viewer = _markdown.MarkdownViewer()
    viewer._on_insert_link_clicked()

    assert viewer.editor.wrap_calls == [("[", "](https://example.com)")]
    assert viewer.editor.insert_calls == []


def test_markdown_link_dialog_inserts_explicit_label(monkeypatch):
    _app()
    monkeypatch.setattr(_markdown, "MonacoLspWidget", _StubMonaco)
    monkeypatch.setattr(_markdown, "_LinkInsertDialog", _StubLinkDialogWithLabel)

    viewer = _markdown.MarkdownViewer()
    viewer._on_insert_link_clicked()

    assert viewer.editor.insert_calls == ["[Docs](https://example.com/docs)"]
    assert viewer.editor.wrap_calls == []


def test_markdown_image_dialog_relativizes_picked_absolute_path(monkeypatch):
    _app()
    monkeypatch.setattr(_markdown, "MonacoLspWidget", _StubMonaco)

    root = Path(os.getcwd()) / "tmp_pytest" / f"markdown-dialogs-{uuid4().hex}"
    try:
        markdown_file = root / "docs" / "README.md"
        image_file = root / "docs" / "images" / "logo.png"
        image_file.parent.mkdir(parents=True, exist_ok=True)
        image_file.write_bytes(b"")
        markdown_file.parent.mkdir(parents=True, exist_ok=True)
        markdown_file.write_text("text", encoding="utf-8")

        dialog_cls = _StubImageDialogAbsolutePicked
        dialog_cls._image_path = str(image_file)
        monkeypatch.setattr(_markdown, "_ImageInsertDialog", dialog_cls)

        viewer = _markdown.MarkdownViewer()
        viewer.editor.file_path = str(markdown_file)
        viewer._on_insert_image_clicked()

        assert viewer.editor.insert_calls == ["![Logo](images/logo.png)"]
    finally:
        if root.exists():
            shutil.rmtree(root, ignore_errors=True)


def test_markdown_image_dialog_keeps_unsaved_relative_path_and_normalizes_slashes(monkeypatch):
    _app()
    monkeypatch.setattr(_markdown, "MonacoLspWidget", _StubMonaco)
    monkeypatch.setattr(_markdown, "_ImageInsertDialog", _StubImageDialogUnsavedTyped)

    viewer = _markdown.MarkdownViewer()
    viewer.editor.file_path = None
    viewer._on_insert_image_clicked()

    assert viewer.editor.insert_calls == ["![Alt](images/logo.png)"]
