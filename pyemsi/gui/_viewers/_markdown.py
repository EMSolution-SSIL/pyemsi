from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import QTextBrowser, QToolBar, QVBoxLayout, QWidget

from pyemsi.widgets.monaco_lsp import MonacoLspWidget


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

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # -- inner Monaco editor --
        self.editor = MonacoLspWidget(language="markdown", parent=self)
        self.editor.setTheme("vs")

        # -- toolbar --
        toolbar = QToolBar(self)
        toolbar.setMovable(False)

        bold_font = QFont()
        bold_font.setBold(True)
        italic_font = QFont()
        italic_font.setItalic(True)

        def _add(label: str, tip: str, font: QFont | None = None) -> QAction:
            act = QAction(label, self)
            act.setToolTip(tip)
            if font is not None:
                act.setFont(font)
            toolbar.addAction(act)
            return act

        _bold_act = _add("B", "Bold — wrap selection with **", bold_font)
        _italic_act = _add("I", "Italic — wrap selection with *", italic_font)
        _head_act = _add("H", "Heading — prefix line with ## ", bold_font)
        _code_act = _add("<>", "Inline code — wrap selection with `")
        _link_act = _add("Link", "Hyperlink — wrap selection as [text](url)")
        toolbar.addSeparator()
        _prev_act = _add("Preview", "Open/focus the rendered preview tab")

        _bold_act.triggered.connect(lambda: self.editor.wrapSelection("**", "**"))
        _italic_act.triggered.connect(lambda: self.editor.wrapSelection("*", "*"))
        _head_act.triggered.connect(lambda: self.editor.wrapSelection("## ", ""))
        _code_act.triggered.connect(lambda: self.editor.wrapSelection("`", "`"))
        _link_act.triggered.connect(lambda: self.editor.wrapSelection("[", "](url)"))
        _prev_act.triggered.connect(self._on_preview_clicked)

        # -- layout --
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolbar)
        layout.addWidget(self.editor, 1)

        # -- forward signals --
        self.editor.textChanged.connect(self.textChanged)
        self.editor.dirtyChanged.connect(self.dirtyChanged)

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

    def save(self, path: str | None = None) -> None:
        self.editor.save(path)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _on_preview_clicked(self) -> None:
        path = self.editor.file_path
        if path:
            self.preview_requested.emit(path)


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

        self._browser = QTextBrowser(self)
        self._browser.setOpenExternalLinks(True)
        self._browser.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._browser)

    def load_file(self, path: str) -> None:
        try:
            with open(path, encoding="utf-8") as fh:
                self.set_markdown(fh.read())
        except OSError:
            self._browser.setPlainText(f"Cannot read file:\n{path}")

    def set_markdown(self, text: str) -> None:
        try:
            import markdown as _md

            html = _md.markdown(text, extensions=["tables", "fenced_code"])
        except ImportError:
            html = f"<pre>{text}</pre>"
        self._browser.setHtml(html)
