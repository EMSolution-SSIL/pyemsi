"""Scalar bar range dialog for PyVista plotter configuration."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyvistaqt import QtInteractor

import pyvista as pv
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ScalarBarRangeDialog(QDialog):
    """Dialog for editing scalar bar ranges and auto-filling data bounds."""

    def __init__(self, plotter: "QtInteractor | pv.Plotter", plotter_window="QtPlotterWindow"):
        self.plotter_window = plotter_window
        super().__init__(plotter_window._window)

        self.plotter = plotter
        self._range_inputs: dict[str, dict[str, QDoubleSpinBox]] = {}
        self._auto_buttons: dict[str, QPushButton] = {}

        self.setWindowTitle("Scalar Bar Range")
        self.setWindowIcon(QIcon(":/icons/EditScalarRange.svg"))
        self.setModal(False)
        self.resize(420, 360)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        content_widget = QWidget(self)
        self._content_layout = QVBoxLayout(content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(12)
        main_layout.addWidget(content_widget)

        self.button_box = QDialogButtonBox()
        self.ok_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.apply_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Apply)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)

        self.ok_button.clicked.connect(self._on_ok)
        self.apply_button.clicked.connect(self._on_apply)
        self.cancel_button.clicked.connect(self._on_cancel)
        main_layout.addWidget(self.button_box)

        self.initial_scalar_bar_ranges = self._load_initial_ranges()
        self._populate_scalar_bars()

    def _load_initial_ranges(self) -> dict[str, tuple[float, float]]:
        """Load the live scalar-bar ranges from the plotter."""
        parent_plotter = getattr(self.plotter_window, "parent_plotter", None)
        if parent_plotter is not None and hasattr(parent_plotter, "get_scalar_bar_ranges"):
            return parent_plotter.get_scalar_bar_ranges()

        ranges: dict[str, tuple[float, float]] = {}
        for scalar_bar_name, scalar_bar_actor in self.plotter.scalar_bars.items():
            ranges[scalar_bar_name] = tuple(float(value) for value in scalar_bar_actor.GetLookupTable().GetRange())
        return ranges

    def _populate_scalar_bars(self) -> None:
        """Build range editors for each current scalar bar."""
        if not self.initial_scalar_bar_ranges:
            self._content_layout.addWidget(QLabel("No scalar bars are available."))
            self._content_layout.addStretch(1)
            return

        for scalar_bar_name, (minimum, maximum) in self.initial_scalar_bar_ranges.items():
            group = QGroupBox(scalar_bar_name, self)
            group_layout = QVBoxLayout(group)

            form_layout = QFormLayout()
            identifier_label = QLabel(scalar_bar_name, group)
            identifier_label.setTextInteractionFlags(
                identifier_label.textInteractionFlags() | Qt.TextInteractionFlag.TextSelectableByMouse
            )
            min_spin = self._create_range_spin_box(minimum, group)
            max_spin = self._create_range_spin_box(maximum, group)
            form_layout.addRow("Scalar Bar", identifier_label)
            form_layout.addRow("Minimum", min_spin)
            form_layout.addRow("Maximum", max_spin)
            group_layout.addLayout(form_layout)

            button_row = QHBoxLayout()
            auto_button = QPushButton("Auto From All Time Steps", group)
            auto_button.clicked.connect(lambda _checked=False, key=scalar_bar_name: self._on_auto_range(key))
            button_row.addWidget(auto_button)
            button_row.addStretch(1)
            group_layout.addLayout(button_row)

            self._range_inputs[scalar_bar_name] = {"min": min_spin, "max": max_spin}
            self._auto_buttons[scalar_bar_name] = auto_button
            self._content_layout.addWidget(group)

        self._content_layout.addStretch(1)

    def _create_range_spin_box(self, value: float, parent: QWidget) -> QDoubleSpinBox:
        """Create a numeric editor for scalar bar limits."""
        spin_box = QDoubleSpinBox(parent)
        spin_box.setDecimals(12)
        spin_box.setRange(-1e100, 1e100)
        spin_box.setSingleStep(0.1)
        spin_box.setValue(float(value))
        return spin_box

    def _set_range_values(self, scalar_bar_name: str, minimum: float, maximum: float) -> None:
        """Update the visible min/max editors for a scalar bar."""
        widgets = self._range_inputs[scalar_bar_name]
        widgets["min"].blockSignals(True)
        widgets["max"].blockSignals(True)
        widgets["min"].setValue(float(minimum))
        widgets["max"].setValue(float(maximum))
        widgets["min"].blockSignals(False)
        widgets["max"].blockSignals(False)

    def _scalar_bar_range_values(self, scalar_bar_name: str) -> tuple[float, float]:
        """Read the current min/max values for a scalar bar."""
        widgets = self._range_inputs[scalar_bar_name]
        minimum = widgets["min"].value()
        maximum = widgets["max"].value()
        if minimum > maximum:
            raise ValueError(f"Minimum cannot be greater than maximum for scalar bar '{scalar_bar_name}'.")
        return minimum, maximum

    def _apply_scalar_bar_range(self, scalar_bar_name: str, minimum: float, maximum: float) -> None:
        """Apply one scalar-bar range through the owning plotter when available."""
        parent_plotter = getattr(self.plotter_window, "parent_plotter", None)
        if parent_plotter is not None and hasattr(parent_plotter, "apply_scalar_bar_range"):
            parent_plotter.apply_scalar_bar_range(scalar_bar_name, minimum, maximum)
            return

        self.plotter.update_scalar_bar_range([minimum, maximum], name=scalar_bar_name)
        scalar_bar_actor = self.plotter.scalar_bars[scalar_bar_name]
        scalar_bar_actor.GetLookupTable().SetRange(minimum, maximum)
        self.plotter.render()

    def _apply_settings(self) -> bool:
        """Apply all edited scalar-bar ranges."""
        try:
            for scalar_bar_name in self._range_inputs:
                minimum, maximum = self._scalar_bar_range_values(scalar_bar_name)
                self._apply_scalar_bar_range(scalar_bar_name, minimum, maximum)
        except (RuntimeError, ValueError) as exc:
            QMessageBox.warning(self, "Scalar Bar Range", str(exc))
            return False
        return True

    def _restore_initial_settings(self) -> None:
        """Restore the original scalar-bar ranges."""
        for scalar_bar_name, (minimum, maximum) in self.initial_scalar_bar_ranges.items():
            self._set_range_values(scalar_bar_name, minimum, maximum)
            self._apply_scalar_bar_range(scalar_bar_name, minimum, maximum)

    def _on_auto_range(self, scalar_bar_name: str) -> None:
        """Fill the editors with the visible min/max across all time steps."""
        parent_plotter = getattr(self.plotter_window, "parent_plotter", None)
        if parent_plotter is None or not hasattr(parent_plotter, "compute_scalar_bar_data_range"):
            QMessageBox.warning(self, "Scalar Bar Range", "Automatic range analysis is not available for this plotter.")
            return

        response = QMessageBox.question(
            self,
            "Scalar Bar Range",
            "Determining the range over all time steps can potentially take a long time to complete. "
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if response != QMessageBox.StandardButton.Yes:
            return

        try:
            minimum, maximum = parent_plotter.compute_scalar_bar_data_range(scalar_bar_name)
        except (RuntimeError, ValueError) as exc:
            QMessageBox.warning(self, "Scalar Bar Range", str(exc))
            return

        self._set_range_values(scalar_bar_name, minimum, maximum)

    def _on_ok(self) -> None:
        """Apply the edited ranges and close the dialog."""
        if self._apply_settings():
            self.accept()

    def _on_apply(self) -> None:
        """Apply the edited ranges without closing the dialog."""
        self._apply_settings()

    def _on_cancel(self) -> None:
        """Restore the original ranges and close the dialog."""
        self._restore_initial_settings()
        self.reject()
