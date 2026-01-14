"""Display settings dialog for PyVista plotter configuration."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyvistaqt import QtInteractor

import pyvista as pv
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from .color_utils import to_hex
from .property_tree_widget import PropertyTreeWidget


class DisplaySettingsDialog(QDialog):
    """
    Dialog for configuring display settings of the PyVista plotter.

    Provides a PropertyTreeWidget for editing display properties with
    Ok, Apply, and Cancel buttons. The dialog is non-modal (non-blocking)
    to allow interaction with the main window while open.

    Parameters
    ----------
    plotter : QtInteractor | pv.Plotter
        The PyVista plotter instance to configure.
    parent : QWidget, optional
        Parent widget for the dialog. Default is None.

    Attributes
    ----------
    plotter : QtInteractor | pv.Plotter
        Reference to the plotter instance.
    tree : PropertyTreeWidget
        The property tree widget for display settings.
    """

    def __init__(self, plotter: "QtInteractor | pv.Plotter", plotter_window="QtPlotterWindow"):
        """
        Initialize the display settings dialog.

        Parameters
        ----------
        plotter : QtInteractor | pv.Plotter
            The PyVista plotter instance to configure.
        plotter_window : QtPlotterWindow
        """
        self.plotter_window = plotter_window
        super().__init__(plotter_window._window)

        # Store plotter reference
        self.plotter = plotter

        # Configure dialog
        self.setWindowTitle("Display Settings")
        self.setWindowIcon(QIcon(":/icons/Settings.svg"))
        self.setModal(False)  # Non-blocking dialog
        self.resize(400, 500)

        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create PropertyTreeWidget
        self.tree = PropertyTreeWidget()
        layout.addWidget(self.tree)

        # Create button box with Ok, Apply, Cancel
        self.button_box = QDialogButtonBox()

        # Add individual buttons
        self.ok_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.apply_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Apply)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)

        # Apply button is always enabled (as per user requirement)
        self.apply_button.setEnabled(True)

        # Connect button signals
        self.ok_button.clicked.connect(self._on_ok)
        self.apply_button.clicked.connect(self._on_apply)
        self.cancel_button.clicked.connect(self._on_cancel)

        layout.addWidget(self.button_box)

        # Store initial settings to allow reset if needed
        if self.plotter.renderer.axes_enabled:
            self.initial_axes_settings = {
                "enabled": self.plotter.renderer.axes_enabled,
                "line_width": self.plotter.renderer.axes_actor.GetXAxisShaftProperty().GetLineWidth(),
                "color": to_hex(
                    self.plotter.renderer.axes_actor.GetXAxisCaptionActor2D().GetCaptionTextProperty().GetColor()
                ),
                "x_color": to_hex(self.plotter.renderer.axes_actor.GetXAxisTipProperty().GetColor()),
                "y_color": to_hex(self.plotter.renderer.axes_actor.GetYAxisTipProperty().GetColor()),
                "z_color": to_hex(self.plotter.renderer.axes_actor.GetZAxisTipProperty().GetColor()),
                "x_label": self.plotter.renderer.axes_actor.GetXAxisLabelText(),
                "y_label": self.plotter.renderer.axes_actor.GetYAxisLabelText(),
                "z_label": self.plotter.renderer.axes_actor.GetZAxisLabelText(),
                "labels_off": self.plotter.renderer.axes_actor.GetAxisLabels() == 0,
            }
        else:
            self.initial_axes_settings = {
                "enabled": False,
            }
        self.populate_axes()

    def populate_axes(self) -> None:
        """Populate the property tree with axes settings from the plotter."""
        group = self.tree.add_checkable_group(
            name="Axes",
            checked=self.initial_axes_settings["enabled"],
        )
        group.setExpanded(True)
        self.tree.add_property(
            name="Line Width",
            value=int(self.initial_axes_settings["line_width"]),
            editor_type="int",
            parent=group,
            min=1,
            max=10,
        )
        self.tree.add_property(
            name="Color",
            value=self.initial_axes_settings["color"],
            editor_type="color",
            parent=group,
        )
        self.tree.add_property(
            name="X Axis Color",
            value=self.initial_axes_settings["x_color"],
            editor_type="color",
            parent=group,
        )
        self.tree.add_property(
            name="Y Axis Color",
            value=self.initial_axes_settings["y_color"],
            editor_type="color",
            parent=group,
        )
        self.tree.add_property(
            name="Z Axis Color",
            value=self.initial_axes_settings["z_color"],
            editor_type="color",
            parent=group,
        )
        self.tree.add_property(
            name="X Axis Label",
            value=self.initial_axes_settings["x_label"],
            editor_type="string",
            parent=group,
        )
        self.tree.add_property(
            name="Y Axis Label",
            value=self.initial_axes_settings["y_label"],
            editor_type="string",
            parent=group,
        )
        self.tree.add_property(
            name="Z Axis Label",
            value=self.initial_axes_settings["z_label"],
            editor_type="string",
            parent=group,
        )
        self.tree.add_property(
            name="Hide Labels",
            value=self.initial_axes_settings["labels_off"],
            editor_type="bool",
            parent=group,
        )

    @property
    def current_axes_settings(self) -> dict:
        """Get current axes settings from the property tree."""
        values = self.tree.get_all_values()
        return {
            "enabled": bool(values["Axes"]),
            "line_width": int(values["Axes:Line Width"]),
            "color": values["Axes:Color"],
            "x_color": values["Axes:X Axis Color"],
            "y_color": values["Axes:Y Axis Color"],
            "z_color": values["Axes:Z Axis Color"],
            "x_label": values["Axes:X Axis Label"],
            "y_label": values["Axes:Y Axis Label"],
            "z_label": values["Axes:Z Axis Label"],
            "labels_off": bool(values["Axes:Hide Labels"]),
        }

    def _on_ok(self) -> None:
        """Handle Ok button click - apply changes and close dialog."""
        self._apply_settings(self.current_axes_settings)
        self.accept()

    def _on_apply(self) -> None:
        """Handle Apply button click - apply changes without closing."""
        self._apply_settings(self.current_axes_settings)

    def _on_cancel(self) -> None:
        """Handle Cancel button click - close dialog without applying changes."""
        self._apply_settings(self.initial_axes_settings)
        self.reject()

    def _apply_settings(self, axes_settings: dict) -> None:
        """
        Apply current settings from property tree to plotter.

        This method is called by both Ok and Apply buttons.
        User can populate this method later or override in subclass.
        """
        if axes_settings["enabled"]:
            self.plotter.show_axes()
            self.plotter_window._axes_action.setChecked(True)
            self.plotter.renderer.axes_actor.GetXAxisShaftProperty().SetLineWidth(axes_settings["line_width"])
            label_color = pv.Color(axes_settings["color"]).float_rgb
            self.plotter.renderer.axes_actor.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(label_color)
            self.plotter.renderer.axes_actor.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetColor(label_color)
            self.plotter.renderer.axes_actor.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetColor(label_color)
            x_color = pv.Color(axes_settings["x_color"]).float_rgb
            self.plotter.renderer.axes_actor.GetXAxisShaftProperty().SetColor(x_color)
            y_color = pv.Color(axes_settings["y_color"]).float_rgb
            self.plotter.renderer.axes_actor.GetYAxisShaftProperty().SetColor(y_color)
            z_color = pv.Color(axes_settings["z_color"]).float_rgb
            self.plotter.renderer.axes_actor.GetZAxisShaftProperty().SetColor(z_color)
            self.plotter.renderer.axes_actor.GetXAxisTipProperty().SetColor(x_color)
            self.plotter.renderer.axes_actor.GetYAxisTipProperty().SetColor(y_color)
            self.plotter.renderer.axes_actor.GetZAxisTipProperty().SetColor(z_color)
            self.plotter.renderer.axes_actor.SetXAxisLabelText(axes_settings["x_label"])
            self.plotter.renderer.axes_actor.SetYAxisLabelText(axes_settings["y_label"])
            self.plotter.renderer.axes_actor.SetZAxisLabelText(axes_settings["z_label"])
            if axes_settings["labels_off"]:
                self.plotter.renderer.axes_actor.SetAxisLabels(0)
            else:
                self.plotter.renderer.axes_actor.SetAxisLabels(1)
        else:
            self.plotter.hide_axes()
            self.plotter_window._axes_action.setChecked(False)
