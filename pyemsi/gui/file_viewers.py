"""
File viewer widgets for opening different file types as tabs.

Provides viewer widgets for text, image, and audio files, plus a factory
function that selects the appropriate viewer based on file extension.
"""

from __future__ import annotations

from ._viewers._audio import _HAS_MULTIMEDIA
from ._viewers._constants import (
    _AUDIO_EXTENSIONS,
    _CATEGORY,
    _IMAGE_EXTENSIONS,
    _MARKDOWN_EXTENSIONS,
    _PYTHON_EXTENSIONS,
    _TEXT_EXTENSIONS,
)
from ._viewers._factory import create_viewer
from ._viewers._image import ImageViewer
from ._viewers._markdown import MarkdownPreviewViewer, MarkdownViewer
from ._viewers._python import PythonViewer
from ._viewers._unsupported import UnsupportedViewer

if _HAS_MULTIMEDIA:
    from ._viewers._audio import AudioViewer

__all__ = [
    "_CATEGORY",
    "_TEXT_EXTENSIONS",
    "_PYTHON_EXTENSIONS",
    "_MARKDOWN_EXTENSIONS",
    "_IMAGE_EXTENSIONS",
    "_AUDIO_EXTENSIONS",
    "_HAS_MULTIMEDIA",
    "MarkdownViewer",
    "MarkdownPreviewViewer",
    "PythonViewer",
    "ImageViewer",
    "UnsupportedViewer",
    "create_viewer",
]
