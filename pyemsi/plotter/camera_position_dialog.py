"""Camera position dialog for PyVista plotter configuration."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pyvista as pv
    from pyvistaqt import QtInteractor

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

CameraValues = tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]


def _format_float(value: float) -> str:
    """Format a camera component with compact precision."""
    return f"{float(value):.6g}"


def _format_vector(vector: tuple[float, float, float]) -> str:
    """Format a 3D vector as a tuple-like string."""
    return f"({_format_float(vector[0])}, {_format_float(vector[1])}, {_format_float(vector[2])})"


def format_camera_position(values: CameraValues) -> str:
    """Format camera position values as PyVista's list-style representation."""
    return f"[{_format_vector(values[0])}, {_format_vector(values[1])}, {_format_vector(values[2])}]"


def _parse_float(text: str) -> float:
    """Parse and validate a finite float value."""
    value = float(text.strip())
    if not math.isfinite(value):
        raise ValueError("Camera position values must be finite numbers.")
    return value


def _camera_values_from_object(camera_position) -> CameraValues:
    """Convert a PyVista CameraPosition or tuple-like value into plain tuples."""
    if all(hasattr(camera_position, attr) for attr in ("position", "focal_point", "viewup")):
        raw_values = (camera_position.position, camera_position.focal_point, camera_position.viewup)
    else:
        raw_values = camera_position

    if len(raw_values) != 3:
        raise ValueError("Camera position must contain position, focal point, and view up vectors.")

    values: list[tuple[float, float, float]] = []
    for raw_vector in raw_values:
        if len(raw_vector) != 3:
            raise ValueError("Each camera position vector must contain three components.")
        vector = tuple(_parse_float(str(component)) for component in raw_vector)
        values.append(vector)

    return (values[0], values[1], values[2])


def validate_camera_values(values: CameraValues) -> None:
    """Validate camera vectors before applying them to PyVista."""
    flat_values = [component for vector in values for component in vector]
    if not all(math.isfinite(component) for component in flat_values):
        raise ValueError("Camera position values must be finite numbers.")

    if math.dist(values[0], values[1]) == 0:
        raise ValueError("Position and focal point cannot be identical.")

    if math.dist(values[2], (0.0, 0.0, 0.0)) == 0:
        raise ValueError("View Up vector cannot be zero.")


class CameraPositionDialog(QDialog):
    """Non-modal dialog for inspecting and editing ``plotter.camera_position``."""

    _SLIDER_STEPS = 1000
    _VECTOR_LABELS = ("Position", "Focal Point", "View Up")
    _COMPONENT_LABELS = ("X", "Y", "Z")

    def __init__(self, plotter: "QtInteractor | pv.Plotter", plotter_window) -> None:
        super().__init__(plotter_window._window)
        self.plotter = plotter
        self.plotter_window = plotter_window
        self._values: CameraValues = _camera_values_from_object(self.plotter.camera_position)
        self._line_edits: dict[tuple[int, int], QLineEdit] = {}
        self._sliders: dict[tuple[int, int], QSlider] = {}
        self._slider_ranges: dict[tuple[int, int], tuple[float, float]] = {}
        self._updating_controls = False

        self.setWindowTitle("Camera Position")
        self.setWindowIcon(QIcon(":/icons/CameraPosition.svg"))
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.resize(620, 360)

        self._create_ui()
        self._load_camera_position()

    def _create_ui(self) -> None:
        """Build dialog controls."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        for vector_index, vector_label in enumerate(self._VECTOR_LABELS):
            title = QLabel(vector_label, self)
            title_font = title.font()
            title_font.setBold(True)
            title.setFont(title_font)
            main_layout.addWidget(title)

            for component_index, component_label in enumerate(self._COMPONENT_LABELS):
                row = QHBoxLayout()
                row.setSpacing(8)

                label = QLabel(component_label, self)
                label.setFixedWidth(18)
                row.addWidget(label)

                line_edit = QLineEdit(self)
                line_edit.setFixedWidth(120)
                line_edit.editingFinished.connect(
                    lambda vector_idx=vector_index, component_idx=component_index: self._on_line_edit_finished(
                        vector_idx, component_idx
                    )
                )
                row.addWidget(line_edit)

                slider = QSlider(Qt.Orientation.Horizontal, self)
                slider.setMinimum(0)
                slider.setMaximum(self._SLIDER_STEPS)
                slider.valueChanged.connect(
                    lambda slider_value, vector_idx=vector_index, component_idx=component_index: (
                        self._on_slider_changed(vector_idx, component_idx, slider_value)
                    )
                )
                row.addWidget(slider, 1)

                key = (vector_index, component_index)
                self._line_edits[key] = line_edit
                self._sliders[key] = slider
                main_layout.addLayout(row)

        self._camera_position_edit = QLineEdit(self)
        self._camera_position_edit.setReadOnly(True)
        main_layout.addWidget(QLabel("Camera Position", self))
        main_layout.addWidget(self._camera_position_edit)

        button_row = QHBoxLayout()
        button_row.addStretch(1)

        self._copy_button = QPushButton("Copy", self)
        self._copy_button.clicked.connect(self._copy_to_clipboard)
        button_row.addWidget(self._copy_button)

        self._refresh_button = QPushButton("Refresh", self)
        self._refresh_button.clicked.connect(self._load_camera_position)
        button_row.addWidget(self._refresh_button)

        self._close_button = QPushButton("Close", self)
        self._close_button.clicked.connect(self.close)
        button_row.addWidget(self._close_button)

        main_layout.addLayout(button_row)

    def _load_camera_position(self) -> None:
        """Refresh all controls from the live plotter camera position."""
        self._values = _camera_values_from_object(self.plotter.camera_position)
        self._rebuild_ranges()
        self._sync_controls_from_values()

    def _rebuild_ranges(self) -> None:
        """Rebuild slider ranges around the current values."""
        distance = math.dist(self._values[0], self._values[1])
        position_span = distance if distance > 0 else 1.0

        for vector_index, vector in enumerate(self._values):
            span = 1.0 if vector_index == 2 else position_span
            for component_index, value in enumerate(vector):
                self._set_slider_range(vector_index, component_index, value - span, value + span)

    def _set_slider_range(self, vector_index: int, component_index: int, minimum: float, maximum: float) -> None:
        """Set the numeric range represented by one slider."""
        if maximum <= minimum:
            maximum = minimum + 1.0

        key = (vector_index, component_index)
        self._slider_ranges[key] = (minimum, maximum)
        span = maximum - minimum
        self._sliders[key].setToolTip(
            f"Range: {_format_float(minimum)} to {_format_float(maximum)}; span {_format_float(span)}"
        )

    def _sync_controls_from_values(self) -> None:
        """Update line edits, sliders, and copy field from internal values."""
        self._updating_controls = True
        try:
            for vector_index, vector in enumerate(self._values):
                for component_index, value in enumerate(vector):
                    key = (vector_index, component_index)
                    self._line_edits[key].setText(_format_float(value))
                    self._sliders[key].setValue(self._value_to_slider(vector_index, component_index, value))
            self._camera_position_edit.setText(format_camera_position(self._values))
        finally:
            self._updating_controls = False

    def _value_to_slider(self, vector_index: int, component_index: int, value: float) -> int:
        """Map a numeric value into slider coordinates."""
        minimum, maximum = self._slider_ranges[(vector_index, component_index)]
        if maximum <= minimum:
            return 0
        ratio = (value - minimum) / (maximum - minimum)
        return max(0, min(self._SLIDER_STEPS, round(ratio * self._SLIDER_STEPS)))

    def _slider_to_value(self, vector_index: int, component_index: int, slider_value: int) -> float:
        """Map a slider coordinate into a numeric value."""
        minimum, maximum = self._slider_ranges[(vector_index, component_index)]
        ratio = slider_value / self._SLIDER_STEPS
        return minimum + ratio * (maximum - minimum)

    def _on_line_edit_finished(self, vector_index: int, component_index: int) -> None:
        """Apply a line-edit component change."""
        if self._updating_controls:
            return

        key = (vector_index, component_index)
        try:
            value = _parse_float(self._line_edits[key].text())
        except ValueError:
            self._show_validation_error("Camera position values must be finite numbers.")
            self._sync_controls_from_values()
            return

        next_values = self._candidate_values(vector_index, component_index, value)
        try:
            validate_camera_values(next_values)
        except ValueError as exc:
            self._show_validation_error(str(exc))
            self._sync_controls_from_values()
            return

        minimum, maximum = self._slider_ranges[key]
        if value < minimum or value > maximum:
            span = (maximum - minimum) / 2
            if span <= 0:
                span = 1.0
            self._set_slider_range(vector_index, component_index, value - span, value + span)

        self._set_component(vector_index, component_index, value)

    def _on_slider_changed(self, vector_index: int, component_index: int, slider_value: int) -> None:
        """Apply a slider component change."""
        if self._updating_controls:
            return

        value = self._slider_to_value(vector_index, component_index, slider_value)
        self._set_component(vector_index, component_index, value)

    def _set_component(self, vector_index: int, component_index: int, value: float) -> None:
        """Update one component and apply the resulting camera position."""
        next_values = self._candidate_values(vector_index, component_index, value)

        try:
            validate_camera_values(next_values)
        except ValueError as exc:
            self._show_validation_error(str(exc))
            self._sync_controls_from_values()
            return

        if next_values == self._values:
            self._sync_controls_from_values()
            return

        self._values = next_values
        self._apply_camera_position()
        self._sync_controls_from_values()

    def _candidate_values(self, vector_index: int, component_index: int, value: float) -> CameraValues:
        """Return camera values with one component changed."""
        vector_values = [list(vector) for vector in self._values]
        vector_values[vector_index][component_index] = float(value)
        return (
            tuple(vector_values[0]),
            tuple(vector_values[1]),
            tuple(vector_values[2]),
        )

    def _apply_camera_position(self) -> None:
        """Apply the current camera position values to the PyVista plotter."""
        self.plotter.camera_position = self._values
        self.plotter.render()

    def _copy_to_clipboard(self) -> None:
        """Copy the list-format camera position to the application clipboard."""
        self.plotter_window.app.clipboard().setText(self._camera_position_edit.text())

    def _show_validation_error(self, message: str) -> None:
        """Show a validation warning for invalid camera values."""
        QMessageBox.warning(self, "Camera Position", message)
