from __future__ import annotations

import json
import os

from PySide6.QtWidgets import QWidget

from pyemsi.widgets.monaco_lsp import MonacoLspWidget
from pyemsi.widgets.monaco_lsp._widget import EXT_TO_LANG

from ._audio import AudioViewer
from ._constants import _CATEGORY
from ._emsolution_json import EMSolutionInputViewer, EMSolutionOutputViewer
from ._image import ImageViewer
from ._markdown import MarkdownViewer
from ._python import PythonViewer
from ._unsupported import UnsupportedViewer

_EMSOLUTION_OUTPUT_KEYS = frozenset({"postDataList", "postData", "timeStep"})
_EMSOLUTION_INPUT_KEYS = frozenset({"0_Release_Number", "1_Execution_Control", "2_Analysis_Type"})


def _matches_signature_keys(payload: object, signature_keys: frozenset[str]) -> bool:
    if not isinstance(payload, dict):
        return False
    return len(signature_keys.intersection(payload)) >= 2


def classify_emsolution_json(path: str) -> str | None:
    """Return the EMSolution JSON kind for *path*, if recognized."""
    if os.path.splitext(path)[1].lower() != ".json":
        return None

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as stream:
            payload = json.load(stream)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return None

    if _matches_signature_keys(payload, _EMSOLUTION_OUTPUT_KEYS):
        return "emsolution-output"
    if _matches_signature_keys(payload, _EMSOLUTION_INPUT_KEYS):
        return "emsolution-input"
    return None


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

    if category == "text":
        json_kind = classify_emsolution_json(path)
        if json_kind == "emsolution-output":
            viewer = EMSolutionOutputViewer(parent=parent)
            viewer.load_file(path)
            return viewer
        if json_kind == "emsolution-input":
            viewer = EMSolutionInputViewer(parent=parent)
            viewer.load_file(path)
            return viewer

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
    elif category == "audio":
        viewer = AudioViewer(parent=parent)
        viewer.load_file(path)
    else:
        viewer = UnsupportedViewer(path, parent=parent)

    return viewer
