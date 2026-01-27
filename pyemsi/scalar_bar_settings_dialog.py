"""Scalar bar settings dialog for PyVista plotter configuration."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyvistaqt import QtInteractor
    from vtk import vtkScalarBarActor

import pyvista as pv
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from .color_utils import to_hex
from .property_tree_widget import PropertyTreeWidget


class ScalarBarSettingsDialog(QDialog):
    """
    Dialog for configuring scalar bar settings of the PyVista plotter.

    Provides buttons to add/remove scalar bars and a PropertyTreeWidget for
    editing scalar bar properties with Ok, Apply, and Cancel buttons. The
    dialog is non-modal (non-blocking) to allow interaction with the main
    window while open.

    Parameters
    ----------
    plotter : QtInteractor | pv.Plotter
        The PyVista plotter instance to configure.
    plotter_window : QtPlotterWindow
        The plotter window instance.

    Attributes
    ----------
    plotter : QtInteractor | pv.Plotter
        Reference to the plotter instance.
    plotter_window : QtPlotterWindow
        Reference to the plotter window instance.
    tree : PropertyTreeWidget
        The property tree widget for scalar bar settings.
    initial_scalar_bars_settings : dict
        Dictionary storing initial settings for each scalar bar.
    """

    def __init__(self, plotter: "QtInteractor | pv.Plotter", plotter_window="QtPlotterWindow"):
        """
        Initialize the scalar bar settings dialog.

        Parameters
        ----------
        plotter : QtInteractor | pv.Plotter
            The PyVista plotter instance to configure.
        plotter_window : QtPlotterWindow
            The plotter window instance.
        """
        self.plotter_window = plotter_window
        super().__init__(plotter_window._window)

        # Store plotter reference
        self.plotter = plotter

        # Configure dialog
        self.setWindowTitle("Scalar Bar Settings")
        self.setWindowIcon(QIcon(":/icons/Settings.svg"))
        self.setModal(False)  # Non-blocking dialog
        self.resize(400, 600)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create PropertyTreeWidget
        self.tree = PropertyTreeWidget()
        main_layout.addWidget(self.tree)

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

        main_layout.addWidget(self.button_box)

        # Store initial settings
        self.initial_scalar_bars_settings = {}

        # Populate tree with current scalar bars
        self._load_initial_settings()
        self.populate_scalar_bars()

    def _load_initial_settings(self) -> None:
        """Load initial settings from current scalar bars in the plotter."""
        self.initial_scalar_bars_settings = {}

        scalar_bar_actor: vtkScalarBarActor
        for scalar_bar_key, scalar_bar_actor in self.plotter.scalar_bars.items():
            settings = {
                "mapper_name": scalar_bar_key,
                "title": scalar_bar_actor.GetTitle() if hasattr(scalar_bar_actor, "GetTitle") else "",
                "position_x": float(scalar_bar_actor.GetPosition()[0]),
                "position_y": float(scalar_bar_actor.GetPosition()[1]),
                "width": float(scalar_bar_actor.GetPosition2()[0]),
                "height": float(scalar_bar_actor.GetPosition2()[1]),
                "title_font_size": int(
                    scalar_bar_actor.GetTitleTextProperty().GetFontSize()
                    if hasattr(scalar_bar_actor.GetTitleTextProperty(), "GetFontSize")
                    else 16
                ),
                "label_font_size": int(
                    scalar_bar_actor.GetLabelTextProperty().GetFontSize()
                    if hasattr(scalar_bar_actor.GetLabelTextProperty(), "GetFontSize")
                    else 12
                ),
                "n_labels": int(scalar_bar_actor.GetNumberOfLabels()),
                "font_family": scalar_bar_actor.GetTitleTextProperty().GetFontFamilyAsString().lower(),
                "color": to_hex(scalar_bar_actor.GetTitleTextProperty().GetColor()),
                "bold": bool(scalar_bar_actor.GetTitleTextProperty().GetBold()),
                "italic": bool(scalar_bar_actor.GetTitleTextProperty().GetItalic()),
                "shadow": bool(scalar_bar_actor.GetTitleTextProperty().GetShadow()),
                "vertical": bool(scalar_bar_actor.GetOrientation() == 1),
            }
            self.initial_scalar_bars_settings[scalar_bar_key] = settings

    def populate_scalar_bars(self) -> None:
        """Populate the property tree with scalar bar settings from the plotter."""
        for mapper_key, settings in self.initial_scalar_bars_settings.items():
            # Create group for this scalar bar
            group = self.tree.add_group(mapper_key)

            # Add properties (no callbacks as changes apply only on Ok/Apply)
            self.tree.add_property(
                name="Mapper Name",
                value=settings["mapper_name"],
                editor_type="string",
                parent=group,
                readonly=True,
            )

            self.tree.add_property(
                name="Title",
                value=settings["title"],
                editor_type="string",
                parent=group,
            )

            self.tree.add_property(
                name="Position X",
                value=settings["position_x"],
                editor_type="slider",
                parent=group,
                min=0.0,
                max=1.0,
                decimals=2,
                steps=100,
            )

            self.tree.add_property(
                name="Position Y",
                value=settings["position_y"],
                editor_type="slider",
                parent=group,
                min=0.0,
                max=1.0,
                decimals=2,
                steps=100,
            )

            self.tree.add_property(
                name="Width",
                value=settings["width"],
                editor_type="slider",
                parent=group,
                min=0.0,
                max=1.0,
                decimals=2,
                steps=100,
            )

            self.tree.add_property(
                name="Height",
                value=settings["height"],
                editor_type="slider",
                parent=group,
                min=0.0,
                max=1.0,
                decimals=2,
                steps=100,
            )

            self.tree.add_property(
                name="Title Font Size",
                value=settings["title_font_size"],
                editor_type="int",
                parent=group,
                min=8,
                max=32,
            )

            self.tree.add_property(
                name="Label Font Size",
                value=settings["label_font_size"],
                editor_type="int",
                parent=group,
                min=8,
                max=32,
            )

            self.tree.add_property(
                name="Number of Labels",
                value=settings["n_labels"],
                editor_type="int",
                parent=group,
                min=2,
                max=20,
            )

            self.tree.add_property(
                name="Font Family",
                value=settings["font_family"],
                editor_type="enum",
                parent=group,
                choices=["courier", "times", "arial"],
            )

            self.tree.add_property(
                name="Color",
                value=settings["color"],
                editor_type="color",
                parent=group,
            )

            self.tree.add_property(
                name="Bold",
                value=settings["bold"],
                editor_type="bool",
                parent=group,
            )

            self.tree.add_property(
                name="Italic",
                value=settings["italic"],
                editor_type="bool",
                parent=group,
            )

            self.tree.add_property(
                name="Shadow",
                value=settings["shadow"],
                editor_type="bool",
                parent=group,
            )

            self.tree.add_property(
                name="Vertical",
                value=settings["vertical"],
                editor_type="bool",
                parent=group,
            )

    def _on_ok(self) -> None:
        """Handle Ok button click - apply changes and close dialog."""
        self._apply_settings()
        self.accept()

    def _on_apply(self) -> None:
        """Handle Apply button click - apply changes without closing."""
        self._apply_settings()

    def _on_cancel(self) -> None:
        """Handle Cancel button click - restore initial settings and close."""
        self._restore_initial_settings()
        self.reject()

    def _apply_settings(self) -> None:
        """Apply settings from the property tree to the plotter."""
        # Get all values from tree
        all_values = self.tree.get_all_values()

        scalar_bar: vtkScalarBarActor
        for scalar_bar_key, scalar_bar in self.plotter.scalar_bars.items():
            scalar_bar.SetTitle(all_values[scalar_bar_key + ":Title"])
            current_orientation = scalar_bar.GetOrientation()
            new_orientation = 1 if all_values[scalar_bar_key + ":Vertical"] else 0
            if current_orientation != new_orientation:
                scalar_bar.SetOrientation(new_orientation)
                theme = self.plotter.theme
                if new_orientation == 1:  # Vertical
                    scalar_bar.SetPosition(theme.colorbar_vertical.position_x, theme.colorbar_vertical.position_y)
                    scalar_bar.SetPosition2(theme.colorbar_vertical.width, theme.colorbar_vertical.height)
                    self.tree.update_property_value(scalar_bar_key + ":Position X", theme.colorbar_vertical.position_x)
                    self.tree.update_property_value(scalar_bar_key + ":Position Y", theme.colorbar_vertical.position_y)
                    self.tree.update_property_value(scalar_bar_key + ":Width", theme.colorbar_vertical.width)
                    self.tree.update_property_value(scalar_bar_key + ":Height", theme.colorbar_vertical.height)
                else:  # Horizontal
                    scalar_bar.SetPosition(theme.colorbar_horizontal.position_x, theme.colorbar_horizontal.position_y)
                    scalar_bar.SetPosition2(theme.colorbar_horizontal.width, theme.colorbar_horizontal.height)
                    self.tree.update_property_value(
                        scalar_bar_key + ":Position X", theme.colorbar_horizontal.position_x
                    )
                    self.tree.update_property_value(
                        scalar_bar_key + ":Position Y", theme.colorbar_horizontal.position_y
                    )
                    self.tree.update_property_value(scalar_bar_key + ":Width", theme.colorbar_horizontal.width)
                    self.tree.update_property_value(scalar_bar_key + ":Height", theme.colorbar_horizontal.height)
            else:
                scalar_bar.SetPosition(
                    float(all_values[scalar_bar_key + ":Position X"]),
                    float(all_values[scalar_bar_key + ":Position Y"]),
                )
                scalar_bar.SetPosition2(
                    float(all_values[scalar_bar_key + ":Width"]),
                    float(all_values[scalar_bar_key + ":Height"]),
                )
            scalar_bar.GetTitleTextProperty().SetFontSize(int(all_values[scalar_bar_key + ":Title Font Size"]))
            scalar_bar.GetLabelTextProperty().SetFontSize(int(all_values[scalar_bar_key + ":Label Font Size"]))
            scalar_bar.SetNumberOfLabels(int(all_values[scalar_bar_key + ":Number of Labels"]))
            font_family = all_values[scalar_bar_key + ":Font Family"].lower()
            if font_family == "courier":
                scalar_bar.GetTitleTextProperty().SetFontFamilyToCourier()
                scalar_bar.GetLabelTextProperty().SetFontFamilyToCourier()
            elif font_family == "times":
                scalar_bar.GetTitleTextProperty().SetFontFamilyToTimes()
                scalar_bar.GetLabelTextProperty().SetFontFamilyToTimes()
            else:  # Default to arial
                scalar_bar.GetTitleTextProperty().SetFontFamilyToArial()
                scalar_bar.GetLabelTextProperty().SetFontFamilyToArial()
            color = pv.Color(all_values[scalar_bar_key + ":Color"]).float_rgb
            scalar_bar.GetTitleTextProperty().SetColor(color)
            scalar_bar.GetLabelTextProperty().SetColor(color)
            scalar_bar.GetTitleTextProperty().SetBold(bool(all_values[scalar_bar_key + ":Bold"]))
            scalar_bar.GetTitleTextProperty().SetItalic(bool(all_values[scalar_bar_key + ":Italic"]))
            scalar_bar.GetTitleTextProperty().SetShadow(bool(all_values[scalar_bar_key + ":Shadow"]))
        self.plotter.render()

    def _restore_initial_settings(self) -> None:
        """Restore initial settings to scalar bars in the plotter."""
        scalar_bar: vtkScalarBarActor
        for scalar_bar_key, scalar_bar in self.plotter.scalar_bars.items():
            settings = self.initial_scalar_bars_settings[scalar_bar_key]

            scalar_bar.SetTitle(settings["title"])
            scalar_bar.SetOrientation(1 if settings["vertical"] else 0)
            scalar_bar.SetPosition(float(settings["position_x"]), float(settings["position_y"]))
            scalar_bar.SetPosition2(float(settings["width"]), float(settings["height"]))

            scalar_bar.GetTitleTextProperty().SetFontSize(int(settings["title_font_size"]))
            scalar_bar.GetLabelTextProperty().SetFontSize(int(settings["label_font_size"]))
            scalar_bar.SetNumberOfLabels(int(settings["n_labels"]))

            font_family = settings["font_family"].lower()
            if font_family == "courier":
                scalar_bar.GetTitleTextProperty().SetFontFamilyToCourier()
                scalar_bar.GetLabelTextProperty().SetFontFamilyToCourier()
            elif font_family == "times":
                scalar_bar.GetTitleTextProperty().SetFontFamilyToTimes()
                scalar_bar.GetLabelTextProperty().SetFontFamilyToTimes()
            else:  # Default to arial
                scalar_bar.GetTitleTextProperty().SetFontFamilyToArial()
                scalar_bar.GetLabelTextProperty().SetFontFamilyToArial()

            color = pv.Color(settings["color"]).float_rgb
            scalar_bar.GetTitleTextProperty().SetColor(color)
            scalar_bar.GetLabelTextProperty().SetColor(color)
            scalar_bar.GetTitleTextProperty().SetBold(bool(settings["bold"]))
            scalar_bar.GetTitleTextProperty().SetItalic(bool(settings["italic"]))
            scalar_bar.GetTitleTextProperty().SetShadow(bool(settings["shadow"]))

            # Update tree values for non-position properties
            self.tree.update_property_value(scalar_bar_key + ":Title", settings["title"])
            self.tree.update_property_value(scalar_bar_key + ":Title Font Size", settings["title_font_size"])
            self.tree.update_property_value(scalar_bar_key + ":Label Font Size", settings["label_font_size"])
            self.tree.update_property_value(scalar_bar_key + ":Number of Labels", settings["n_labels"])
            self.tree.update_property_value(scalar_bar_key + ":Font Family", settings["font_family"])
            self.tree.update_property_value(scalar_bar_key + ":Color", settings["color"])
            self.tree.update_property_value(scalar_bar_key + ":Bold", settings["bold"])
            self.tree.update_property_value(scalar_bar_key + ":Italic", settings["italic"])
            self.tree.update_property_value(scalar_bar_key + ":Shadow", settings["shadow"])
            self.tree.update_property_value(scalar_bar_key + ":Vertical", settings["vertical"])

        self.plotter.render()

    def show(self) -> None:
        super().show()
