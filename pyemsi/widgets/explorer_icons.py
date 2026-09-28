"""Material file and folder icons used by the Explorer."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFileInfo
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileIconProvider

import pyemsi.resources.resources  # noqa: F401


_RESOURCE_PREFIX = ":/icons/material/"

_FILE_NAMES = {
    ".gitignore": "git",
    ".gitattributes": "git",
    "license": "license",
    "license.md": "license",
    "license.txt": "license",
    "manifest.in": "python-misc",
    "pixi.lock": "python-misc",
    "pyproject.toml": "python-misc",
    "readme": "readme",
    "readme.md": "readme",
    "requirements.txt": "python-misc",
    "setup.py": "python-misc",
}

_EXTENSIONS = {
    ".7z": "zip",
    ".aac": "audio",
    ".bat": "console",
    ".bmp": "image",
    ".cfg": "settings",
    ".csv": "table",
    ".db": "database",
    ".fcstd": "freecad",
    ".flac": "audio",
    ".gif": "image",
    ".gz": "zip",
    ".ico": "image",
    ".ini": "settings",
    ".jpeg": "image",
    ".jpg": "image",
    ".js": "javascript",
    ".json": "json",
    ".jsonc": "json",
    ".log": "console",
    ".m4a": "audio",
    ".markdown": "markdown",
    ".md": "markdown",
    ".mp3": "audio",
    ".neu": "simulink",
    ".ogg": "audio",
    ".png": "image",
    ".ps1": "console",
    ".pvd": "vtk",
    ".py": "python",
    ".pyi": "python",
    ".pyw": "python",
    ".rar": "zip",
    ".rst": "markdown",
    ".sh": "console",
    ".sqlite": "database",
    ".svg": "image",
    ".tar": "zip",
    ".tif": "image",
    ".tiff": "image",
    ".toml": "settings",
    ".ts": "typescript",
    ".tsv": "table",
    ".vtk": "vtk",
    ".vtm": "vtk",
    ".vtu": "vtk",
    ".wav": "audio",
    ".webp": "image",
    ".wma": "audio",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".zip": "zip",
}

_FOLDERS = {
    ".git": "folder-git",
    ".github": "folder-github",
    ".pyemsi": "folder-simulations",
    "__pycache__": "folder-python",
    ".pytest_cache": "folder-test",
    "assets": "folder-resource",
    "build": "folder-dist",
    "dist": "folder-dist",
    "doc": "folder-docs",
    "docs": "folder-docs",
    "examples": "folder-examples",
    "icons": "folder-resource",
    "images": "folder-resource",
    "resources": "folder-resource",
    "src": "folder-python",
    "test": "folder-test",
    "tests": "folder-test",
    "widgets": "folder-python",
}


def icon_name_for_path(path: str, *, is_dir: bool) -> str:
    """Return the resource icon name for *path*."""
    name = Path(path).name.lower()
    if is_dir:
        return _FOLDERS.get(name, "folder-base")
    return _FILE_NAMES.get(name, _EXTENSIONS.get(Path(name).suffix.lower(), "document"))


class MaterialFileIconProvider(QFileIconProvider):
    """Small cached Material icon provider for ``QFileSystemModel``."""

    def __init__(self) -> None:
        super().__init__()
        self._icons: dict[str, QIcon] = {}

    def icon(self, info_or_type):
        if not isinstance(info_or_type, QFileInfo):
            return super().icon(info_or_type)

        name = icon_name_for_path(info_or_type.filePath(), is_dir=info_or_type.isDir())
        icon = self._icons.get(name)
        if icon is None:
            resource = {
                "freecad": ":/icons/FreeCAD.svg",
                "vtk": ":/icons/VTK.svg",
            }.get(name, f"{_RESOURCE_PREFIX}{name}.svg")
            icon = QIcon(resource)
            self._icons[name] = icon
        return icon
