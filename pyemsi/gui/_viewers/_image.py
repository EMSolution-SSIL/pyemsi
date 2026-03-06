from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QScrollArea, QWidget


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
