from __future__ import annotations

_CATEGORY: dict[str, str] = {}

_PYTHON_EXTENSIONS = {
    ".py",
}

_TEXT_EXTENSIONS = {
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".csv",
    ".xml",
    ".html",
    ".htm",
    ".log",
    ".cfg",
    ".ini",
    ".rst",
    ".sh",
    ".bat",
    ".ps1",
    ".js",
    ".ts",
    ".css",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".rs",
    ".go",
    ".rb",
    ".sql",
    ".tex",
}

_MARKDOWN_EXTENSIONS = {
    ".md",
}

_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".svg",
    ".ico",
    ".webp",
    ".tiff",
    ".tif",
}

_AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".ogg",
    ".flac",
    ".aac",
    ".wma",
    ".m4a",
}

for _ext in _PYTHON_EXTENSIONS:
    _CATEGORY[_ext] = "python"
for _ext in _TEXT_EXTENSIONS:
    _CATEGORY[_ext] = "text"
for _ext in _MARKDOWN_EXTENSIONS:
    _CATEGORY[_ext] = "markdown"
for _ext in _IMAGE_EXTENSIONS:
    _CATEGORY[_ext] = "image"
for _ext in _AUDIO_EXTENSIONS:
    _CATEGORY[_ext] = "audio"
