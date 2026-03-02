from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class UnsupportedViewer(QWidget):
    """Placeholder for file types that cannot be previewed."""

    def __init__(self, path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        label = QLabel(f"Cannot preview this file.\n\n{os.path.basename(path)}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(label)
