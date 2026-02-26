"""
File viewer widgets for opening different file types as tabs.

Provides viewer widgets for text, image, and audio files, plus a factory
function that selects the appropriate viewer based on file extension.
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------------------
# MonacoLspWidget
# ---------------------------------------------------------------------------

from pyemsi.widgets.monaco_lsp import MonacoLspWidget
from pyemsi.widgets.monaco_lsp._widget import EXT_TO_LANG

# ---------------------------------------------------------------------------
# QtMultimedia (optional – needed for AudioViewer)
# ---------------------------------------------------------------------------

_HAS_MULTIMEDIA = False
try:
    from PySide6.QtCore import QUrl
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

    _HAS_MULTIMEDIA = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Extension → category mapping
# ---------------------------------------------------------------------------

_CATEGORY: dict[str, str] = {}

_TEXT_EXTENSIONS = {
    ".txt",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".csv",
    ".md",
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

for _ext in _TEXT_EXTENSIONS:
    _CATEGORY[_ext] = "text"
for _ext in _IMAGE_EXTENSIONS:
    _CATEGORY[_ext] = "image"
for _ext in _AUDIO_EXTENSIONS:
    _CATEGORY[_ext] = "audio"

# ---------------------------------------------------------------------------
# ImageViewer
# ---------------------------------------------------------------------------


class ImageViewer(QScrollArea):
    """Image viewer that scales the image to fit the viewport."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWidget(self._label)
        self.setWidgetResizable(True)
        self._original_pixmap: QPixmap | None = None

    def load_file(self, path: str) -> None:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._label.setText(f"Cannot load image:\n{path}")
            return
        self._original_pixmap = pixmap
        self._fit_pixmap()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._fit_pixmap()

    def _fit_pixmap(self) -> None:
        if self._original_pixmap is None:
            return
        scaled = self._original_pixmap.scaled(
            self.viewport().size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)


# ---------------------------------------------------------------------------
# AudioViewer
# ---------------------------------------------------------------------------

if _HAS_MULTIMEDIA:

    class AudioViewer(QWidget):
        """Audio player with play/pause, seek slider, and time display."""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)

            self._player = QMediaPlayer(self)
            self._audio_output = QAudioOutput(self)
            self._player.setAudioOutput(self._audio_output)

            # -- widgets --
            self._name_label = QLabel()
            self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self._play_btn = QPushButton("Play")
            self._slider = QSlider(Qt.Orientation.Horizontal)
            self._time_label = QLabel("0:00 / 0:00")

            # -- layout --
            controls = QHBoxLayout()
            controls.addWidget(self._play_btn)
            controls.addWidget(self._slider, 1)
            controls.addWidget(self._time_label)

            layout = QVBoxLayout(self)
            layout.addStretch()
            layout.addWidget(self._name_label)
            layout.addLayout(controls)
            layout.addStretch()

            # -- signals --
            self._play_btn.clicked.connect(self._toggle_playback)
            self._player.playbackStateChanged.connect(self._on_state_changed)
            self._player.positionChanged.connect(self._on_position_changed)
            self._player.durationChanged.connect(self._on_duration_changed)
            self._slider.sliderMoved.connect(self._player.setPosition)

        def load_file(self, path: str) -> None:
            self._name_label.setText(os.path.basename(path))
            self._player.setSource(QUrl.fromLocalFile(path))

        # -- private helpers --

        def _toggle_playback(self) -> None:
            if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self._player.pause()
            else:
                self._player.play()

        def _on_state_changed(self, state) -> None:
            if state == QMediaPlayer.PlaybackState.PlayingState:
                self._play_btn.setText("Pause")
            else:
                self._play_btn.setText("Play")

        def _on_position_changed(self, position: int) -> None:
            if not self._slider.isSliderDown():
                self._slider.setValue(position)
            duration = self._player.duration()
            self._time_label.setText(f"{self._format_time(position)} / {self._format_time(duration)}")

        def _on_duration_changed(self, duration: int) -> None:
            self._slider.setRange(0, duration)

        @staticmethod
        def _format_time(ms: int) -> str:
            total_seconds = max(ms, 0) // 1000
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}:{seconds:02d}"

# ---------------------------------------------------------------------------
# UnsupportedViewer
# ---------------------------------------------------------------------------


class UnsupportedViewer(QWidget):
    """Placeholder for file types that cannot be previewed."""

    def __init__(self, path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        label = QLabel(f"Cannot preview this file.\n\n{os.path.basename(path)}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(label)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_viewer(path: str, category: str | None = None) -> QWidget:
    """Create the appropriate viewer widget for *path* and load the file.

    Parameters
    ----------
    path : str
        Absolute path to the file.
    category : str, optional
        Force a viewer category (``"text"``, ``"image"``, ``"audio"``).
        When *None* the category is inferred from the file extension.
    """
    if category is None:
        ext = os.path.splitext(path)[1].lower()
        category = _CATEGORY.get(ext)

    if category == "text":
        ext = os.path.splitext(path)[1].lower()
        lang = EXT_TO_LANG.get(ext, "plaintext")
        viewer = MonacoLspWidget(language=lang)
        viewer.setTheme("vs")
        viewer.setLanguage(lang)
        viewer.load_file(path)
    elif category == "image":
        viewer = ImageViewer()
        viewer.load_file(path)
    elif category == "audio" and _HAS_MULTIMEDIA:
        viewer = AudioViewer()
        viewer.load_file(path)
    else:
        viewer = UnsupportedViewer(path)

    return viewer
