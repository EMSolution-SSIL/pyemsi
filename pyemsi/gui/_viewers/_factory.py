from __future__ import annotations

import os

from PySide6.QtWidgets import QWidget

from pyemsi.widgets.monaco_lsp import MonacoLspWidget
from pyemsi.widgets.monaco_lsp._widget import EXT_TO_LANG

from ._audio import _HAS_MULTIMEDIA
from ._constants import _CATEGORY
from ._image import ImageViewer
from ._markdown import MarkdownViewer
from ._python import PythonViewer
from ._unsupported import UnsupportedViewer

if _HAS_MULTIMEDIA:
    from ._audio import AudioViewer


def create_viewer(path: str, category: str | None = None, parent: QWidget | None = None) -> QWidget:
    """Create the appropriate viewer widget for *path* and load the file.

    Parameters
    ----------
    path : str
        Absolute path to the file.
    category : str, optional
        Force a viewer category (``"text"``, ``"image"``, ``"audio"``).
        When *None* the category is inferred from the file extension.
    parent : QWidget, optional
        Parent widget used when constructing the viewer.
    """
    if category is None:
        ext = os.path.splitext(path)[1].lower()
        category = _CATEGORY.get(ext)

    if category == "markdown":
        viewer = MarkdownViewer(parent=parent)
        viewer.load_file(path)
    elif category == "python":
        viewer = PythonViewer(parent=parent)
        viewer.load_file(path)
    elif category == "text":
        ext = os.path.splitext(path)[1].lower()
        lang = EXT_TO_LANG.get(ext, "plaintext")
        viewer = MonacoLspWidget(language=lang, parent=parent)
        viewer.setTheme("vs")
        viewer.setLanguage(lang)
        viewer.load_file(path)
    elif category == "image":
        viewer = ImageViewer(parent=parent)
        viewer.load_file(path)
    elif category == "audio" and _HAS_MULTIMEDIA:
        viewer = AudioViewer(parent=parent)  # type: ignore[possibly-undefined]
        viewer.load_file(path)
    else:
        viewer = UnsupportedViewer(path, parent=parent)

    return viewer
