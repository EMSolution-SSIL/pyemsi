"""Dialogs for exporting time-step animations from the Qt plotter."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class MovieExportSettings:
    """Settings for a PyVista movie export."""

    filename: str
    framerate: int = 4
    quality: int = 5


@dataclass(frozen=True)
class GifExportSettings:
    """Settings for a PyVista GIF export."""

    filename: str
    fps: float = 10.0
    loop: int = 0
    palettesize: int = 256
    subrectangles: bool = False


class _PathPicker:
    """Small reusable path row for export dialogs."""

    def __init__(self, default_path: str, caption: str, file_filter: str) -> None:
        self.widget = QWidget()
        self.caption = caption
        self.file_filter = file_filter
        self.path_edit = QLineEdit(default_path)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.path_edit, 1)
        layout.addWidget(browse_button)
        self.widget.setLayout(layout)

    def _browse(self) -> None:
        selected_path, _ = QFileDialog.getSaveFileName(
            self.widget,
            self.caption,
            self.path_edit.text(),
            self.file_filter,
        )
        if selected_path:
            self.path_edit.setText(selected_path)

    @property
    def path(self) -> str:
        return self.path_edit.text().strip()


def _two_column_row(
    left_label: str,
    left_widget: QWidget,
    right_label: str,
    right_widget: QWidget,
) -> QWidget:
    """Build a compact two-column label/control row."""
    row = QWidget()
    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setHorizontalSpacing(12)
    layout.addWidget(QLabel(left_label), 0, 0)
    layout.addWidget(left_widget, 0, 1)
    layout.addWidget(QLabel(right_label), 0, 2)
    layout.addWidget(right_widget, 0, 3)
    layout.setColumnStretch(1, 1)
    layout.setColumnStretch(3, 1)
    row.setLayout(layout)
    return row


class MovieExportDialog(QDialog):
    """Dialog for MP4/movie export settings."""

    def __init__(self, default_path: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Save Video")
        self.setMinimumWidth(640)

        self._path_picker = _PathPicker(default_path, "Save Video", "MP4 Files (*.mp4);;All Files (*)")

        self._framerate_input = QSpinBox()
        self._framerate_input.setRange(1, 240)
        self._framerate_input.setValue(4)

        self._quality_input = QSpinBox()
        self._quality_input.setRange(0, 10)
        self._quality_input.setValue(5)

        form = QFormLayout()
        form.addRow("Output file", self._path_picker.widget)
        form.addRow(
            "",
            _two_column_row(
                "Framerate",
                self._framerate_input,
                "Quality",
                self._quality_input,
            ),
        )

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def settings(self) -> MovieExportSettings:
        """Return the selected movie export settings."""
        return MovieExportSettings(
            filename=self._path_picker.path,
            framerate=self._framerate_input.value(),
            quality=self._quality_input.value(),
        )


class GifExportDialog(QDialog):
    """Dialog for GIF export settings."""

    def __init__(self, default_path: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Save GIF")
        self.setMinimumWidth(640)

        self._path_picker = _PathPicker(default_path, "Save GIF", "GIF Files (*.gif);;All Files (*)")

        self._fps_input = QDoubleSpinBox()
        self._fps_input.setRange(0.1, 240.0)
        self._fps_input.setDecimals(2)
        self._fps_input.setValue(10.0)

        self._loop_input = QSpinBox()
        self._loop_input.setRange(0, 1_000_000)
        self._loop_input.setValue(0)

        self._palettesize_input = QSpinBox()
        self._palettesize_input.setRange(2, 256)
        self._palettesize_input.setValue(256)

        self._subrectangles_input = QCheckBox()
        self._subrectangles_input.setChecked(False)

        form = QFormLayout()
        form.addRow("Output file", self._path_picker.widget)
        form.addRow(
            "",
            _two_column_row(
                "FPS",
                self._fps_input,
                "Loop count",
                self._loop_input,
            ),
        )
        form.addRow(
            "",
            _two_column_row(
                "Palette size",
                self._palettesize_input,
                "Subrectangles",
                self._subrectangles_input,
            ),
        )

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def settings(self) -> GifExportSettings:
        """Return the selected GIF export settings."""
        return GifExportSettings(
            filename=self._path_picker.path,
            fps=self._fps_input.value(),
            loop=self._loop_input.value(),
            palettesize=self._palettesize_input.value(),
            subrectangles=self._subrectangles_input.isChecked(),
        )
