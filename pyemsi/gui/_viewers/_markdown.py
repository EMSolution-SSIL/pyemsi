from __future__ import annotations

import os
import re
from pathlib import Path

from PySide6.QtCore import QSize, QUrl, Signal
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from pyemsi.widgets.monaco_lsp import MonacoLspWidget

class _LinkInsertDialog(QDialog):
    """Dialog that collects hyperlink label and URL for Markdown insertion."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Insert Link")

        self._label_edit = QLineEdit(self)
        self._label_edit.setPlaceholderText("Leave empty to use selected text")
        self._url_edit = QLineEdit(self)
        self._url_edit.setPlaceholderText("https://example.com")

        form = QFormLayout()
        form.addRow("Label:", self._label_edit)
        form.addRow("URL:", self._url_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def link_label(self) -> str:
        return self._label_edit.text()

    def link_url(self) -> str:
        return self._url_edit.text()


class _ImageInsertDialog(QDialog):
    """Dialog that collects alt text and path for Markdown image insertion."""

    def __init__(self, start_dir: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Insert Image")
        self._picked_via_dialog = False
        self._start_dir = start_dir

        self._alt_edit = QLineEdit(self)
        self._alt_edit.setPlaceholderText("Image description")
        self._path_edit = QLineEdit(self)
        self._path_edit.setPlaceholderText("images/example.png")
        self._browse_button = QPushButton("Browse…", self)
        self._browse_button.clicked.connect(self._browse)

        path_row = QHBoxLayout()
        path_row.setContentsMargins(0, 0, 0, 0)
        path_row.addWidget(self._path_edit, 1)
        path_row.addWidget(self._browse_button)

        form = QFormLayout()
        form.addRow("Alt text:", self._alt_edit)
        form.addRow("Path:", path_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _browse(self) -> None:
        selected_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            self._start_dir,
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp);;All Files (*)",
        )
        if selected_path:
            self._picked_via_dialog = True
            self._path_edit.setText(selected_path)

    def alt_text(self) -> str:
        return self._alt_edit.text()

    def image_path(self) -> str:
        return self._path_edit.text()

    def selected_via_picker(self) -> bool:
        return self._picked_via_dialog


# ---------------------------------------------------------------------------
# MarkdownViewer
# ---------------------------------------------------------------------------


class MarkdownViewer(QWidget):
    """Editor widget for Markdown files with a formatting toolbar.

    Embeds a :class:`MonacoLspWidget` for editing and exposes a
    ``preview_requested`` signal so the host can open a paired
    :class:`MarkdownPreviewViewer` tab.
    """

    #: Emitted when the editor content changes; carries the full text.
    textChanged = Signal(str)
    #: Emitted when the dirty state changes.
    dirtyChanged = Signal(bool)
    #: Emitted when the user clicks the Preview button; carries the file path.
    preview_requested = Signal(str)
    #: Emitted when the file-sync state changes.
    syncStateChanged = Signal(str)
    #: Emitted when the external-change flag changes.
    externalChangeChanged = Signal(bool)
    #: Emitted when the backing file becomes missing or available.
    fileMissingChanged = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # -- inner Monaco editor --
        self.editor = MonacoLspWidget(language="markdown", parent=self)
        self.editor.setTheme("vs")

        # -- toolbar --
        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        bold_font = QFont()
        bold_font.setBold(True)
        italic_font = QFont()
        italic_font.setItalic(True)

        def _add(icon: QIcon, tip: str, font: QFont | None = None) -> QAction:
            act = QAction(icon, "", self)
            act.setToolTip(tip)
            if font is not None:
                act.setFont(font)
            toolbar.addAction(act)
            return act

        _bold_act = _add(QIcon(":/icons/Bold.svg"), "Bold — wrap selection with **", bold_font)
        _italic_act = _add(QIcon(":/icons/Italic.svg"), "Italic — wrap selection with *", italic_font)
        _code_act = _add(QIcon(":/icons/Code.svg"), "Inline code — wrap selection with `")
        _link_act = _add(QIcon(":/icons/Link.svg"), "Hyperlink — wrap selection as [text](url)")
        _image_act = _add(QIcon(":/icons/Image.svg"), "Image — wrap selection as ![alt](url)")
        toolbar.addSeparator()
        _prev_act = _add(QIcon(":/icons/Preview.svg"), "Open/focus the rendered preview tab")

        _bold_act.triggered.connect(lambda: self.editor.wrapSelection("**", "**"))
        _italic_act.triggered.connect(lambda: self.editor.wrapSelection("*", "*"))
        _code_act.triggered.connect(lambda: self.editor.wrapSelection("`", "`"))
        _link_act.triggered.connect(self._on_insert_link_clicked)
        _image_act.triggered.connect(self._on_insert_image_clicked)
        _prev_act.triggered.connect(self._on_preview_clicked)

        # -- layout --
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(self.editor, 1)

        # -- forward signals --
        self.editor.textChanged.connect(self.textChanged.emit)
        self.editor.dirtyChanged.connect(self.dirtyChanged.emit)
        if hasattr(self.editor, "syncStateChanged"):
            self.editor.syncStateChanged.connect(self.syncStateChanged.emit)
        if hasattr(self.editor, "externalChangeChanged"):
            self.editor.externalChangeChanged.connect(self.externalChangeChanged.emit)
        if hasattr(self.editor, "fileMissingChanged"):
            self.editor.fileMissingChanged.connect(self.fileMissingChanged.emit)

    # ------------------------------------------------------------------
    # Public API — mirrors MonacoLspWidget interface expected by SplitContainer
    # ------------------------------------------------------------------

    def load_file(self, path: str) -> None:
        self.editor.load_file(path)

    def text(self) -> str:
        return self.editor.text()

    @property
    def file_path(self) -> str | None:
        return self.editor.file_path

    @property
    def dirty(self) -> bool:
        return self.editor.dirty

    @property
    def sync_state(self) -> str:
        return self.editor.sync_state

    @property
    def has_external_change(self) -> bool:
        return self.editor.has_external_change

    @property
    def file_missing(self) -> bool:
        return self.editor.file_missing

    def save(self, path: str | None = None) -> None:
        self.editor.save(path)

    def reload_from_disk(self) -> None:
        if self.editor.file_path:
            self.editor.load_file(self.editor.file_path)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _on_preview_clicked(self) -> None:
        path = self.editor.file_path
        if path:
            self.preview_requested.emit(path)

    def _on_insert_link_clicked(self) -> None:
        dialog = _LinkInsertDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        url = dialog.link_url().strip()
        if not url:
            return

        label = dialog.link_label().strip()
        if label:
            self.editor.insertAtCursor(f"[{label}]({url})")
            return
        self.editor.wrapSelection("[", f"]({url})")

    def _on_insert_image_clicked(self) -> None:
        dialog = _ImageInsertDialog(start_dir=self._image_dialog_start_directory(), parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        path = dialog.image_path().strip()
        if not path:
            return

        alt = dialog.alt_text().strip()
        md_path = self._resolve_markdown_image_path(path, from_picker=dialog.selected_via_picker())
        self.editor.insertAtCursor(f"![{alt}]({md_path})")

    def _image_dialog_start_directory(self) -> str:
        file_path = self.editor.file_path
        if file_path:
            return str(Path(file_path).resolve().parent)
        return os.getcwd()

    def _resolve_markdown_image_path(self, raw_path: str, from_picker: bool) -> str:
        file_path = self.editor.file_path
        should_relativize = from_picker or Path(raw_path).is_absolute()
        if not file_path or not should_relativize:
            return raw_path.replace("\\", "/")

        markdown_dir = Path(file_path).resolve().parent
        candidate = Path(raw_path).expanduser()
        if not candidate.is_absolute():
            candidate = (markdown_dir / candidate).resolve()

        try:
            relative_path = os.path.relpath(str(candidate), str(markdown_dir))
            return relative_path.replace("\\", "/")
        except ValueError:
            # Different Windows drives cannot be relativized.
            return str(candidate).replace("\\", "/")


# ---------------------------------------------------------------------------
# MarkdownPreviewViewer
# ---------------------------------------------------------------------------


class MarkdownPreviewViewer(QWidget):
    """Read-only rendered preview for a Markdown file.

    Use :meth:`set_markdown` to push updated content from the paired
    :class:`MarkdownViewer`.  The conversion uses the *markdown* library
    with ``tables`` and ``fenced_code`` extensions.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._source_file_path: str | None = None
        self._workspace_root: str | None = None
        self._browser = QTextBrowser(self)
        self._browser.setOpenExternalLinks(True)
        self._browser.setReadOnly(True)
        self._browser.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._browser)

    @property
    def source_file_path(self) -> str | None:
        return self._source_file_path

    @property
    def workspace_root(self) -> str | None:
        return self._workspace_root

    def set_context(self, source_file_path: str | None = None, workspace_root: str | None = None) -> None:
        if source_file_path is not None:
            self._source_file_path = os.path.abspath(os.path.normpath(source_file_path))
        if workspace_root is not None:
            self._workspace_root = os.path.abspath(os.path.normpath(workspace_root))

    def load_file(self, path: str) -> None:
        self.set_context(source_file_path=path)
        try:
            with open(path, encoding="utf-8") as fh:
                self.set_markdown(fh.read(), source_file_path=path)
        except OSError:
            self._browser.setPlainText(f"Cannot read file:\n{path}")

    def set_markdown(
        self,
        text: str,
        source_file_path: str | None = None,
        workspace_root: str | None = None,
    ) -> None:
        self.set_context(source_file_path=source_file_path, workspace_root=workspace_root)
        try:
            import markdown as _md

            html = _md.markdown(text, extensions=["tables", "fenced_code"])
        except ImportError:
            html = f"<pre>{text}</pre>"
        html = self._rewrite_root_relative_urls(html)
        html = self._apply_preview_styles(html)
        self._browser.document().setBaseUrl(self._resolve_base_url())
        self._browser.setHtml(html)

    def _resolve_base_url(self) -> QUrl:
        if self._source_file_path:
            source_dir = str(Path(self._source_file_path).parent)
            return QUrl.fromLocalFile(os.path.join(source_dir, ""))
        if self._workspace_root:
            return QUrl.fromLocalFile(os.path.join(self._workspace_root, ""))
        return QUrl()

    def _rewrite_root_relative_urls(self, html: str) -> str:
        if not self._workspace_root:
            return html

        pattern = re.compile(r'(?P<prefix>\b(?:src|href)\s*=\s*)(?P<quote>["\'])(?P<url>.*?)(?P=quote)', re.IGNORECASE)
        workspace_root = Path(self._workspace_root)

        def _replace(match: re.Match[str]) -> str:
            url = match.group("url")
            if not url.startswith("/") or url.startswith("//") or url.startswith("/#"):
                return match.group(0)

            target = workspace_root / url.lstrip("/")
            file_url = QUrl.fromLocalFile(os.path.abspath(os.path.normpath(str(target)))).toString()
            return f"{match.group('prefix')}{match.group('quote')}{file_url}{match.group('quote')}"

        return pattern.sub(_replace, html)

    @staticmethod
    def _apply_preview_styles(html: str) -> str:
        style = (
            "<style>"
            "img { max-width: 100%; height: auto; }"
            "</style>"
        )
        return f"{style}{html}"
