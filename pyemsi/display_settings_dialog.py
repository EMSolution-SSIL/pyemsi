"""Display settings dialog for PyVista plotter configuration."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyvistaqt import QtInteractor

import pyvista as pv
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from .color_utils import to_hex
from .property_tree_widget import PropertyTreeWidget

GRID_VISIBILITY_DICT = {
    pv.CubeAxesActor.VTK_GRID_LINES_CLOSEST: "all",
    pv.CubeAxesActor.VTK_GRID_LINES_FURTHEST: "back",
    pv.CubeAxesActor.VTK_GRID_LINES_ALL: "front",
}
TICK_LOCATION_DICT = {
    pv.CubeAxesActor.VTK_TICKS_INSIDE: "inside",
    pv.CubeAxesActor.VTK_TICKS_OUTSIDE: "outside",
    pv.CubeAxesActor.VTK_TICKS_BOTH: "both",
}

CMAP_NAMES = {
    # Linear (Sequential)
    "viridis": "linear",
    "haline": "linear",
    "imola": "linear",
    "navia": "linear",
    "davos": "linear",
    "lapaz": "linear",
    "cividis": "linear",
    "nuuk": "linear",
    "lipari": "linear",
    "thermal": "linear",
    "plasma": "linear",
    "bmy": "linear",
    "inferno": "linear",
    "magma": "linear",
    "lajolla": "linear",
    "copper": "linear",
    "gist_heat": "linear",
    "fire": "linear",
    "afmhot": "linear",
    "hot": "linear",
    "solar": "linear",
    "bilbao": "linear",
    "pink": "linear",
    "tokyo": "linear",
    "dimgray": "linear",
    "grayC": "linear",
    "gray": "linear",
    "gist_gray": "linear",
    "bone": "linear",
    "oslo": "linear",
    "ice": "linear",
    "devon": "linear",
    "kbc": "linear",
    "winter": "linear",
    "bmw": "linear",
    "acton": "linear",
    "cubehelix": "linear",
    "batlowW": "linear",
    "batlowK": "linear",
    "batlow": "linear",
    "turku": "linear",
    "bamako": "linear",
    "bgyw": "linear",
    "kbgyw": "linear",
    "gouldian": "linear",
    "bgy": "linear",
    "kgy": "linear",
    "summer": "linear",
    "oxy": "linear",
    "hawaii": "linear",
    "buda": "linear",
    "spring": "linear",
    "autumn": "linear",
    "Wistia": "linear",
    "Oranges": "linear",
    "YlOrBr": "linear",
    "OrRd": "linear",
    "YlOrRd": "linear",
    "Reds": "linear",
    "amp": "linear",
    "PuRd": "linear",
    "RdPu": "linear",
    "matter": "linear",
    "BuPu": "linear",
    "Purples": "linear",
    "dense": "linear",
    "Blues": "linear",
    "PuBu": "linear",
    "PuBuGn": "linear",
    "blues": "linear",
    "GnBu": "linear",
    "YlGnBu": "linear",
    "tempo": "linear",
    "rain": "linear",
    "deep": "linear",
    "gist_yarg": "linear",
    "binary": "linear",
    "Grays": "linear",
    "turbid": "linear",
    "algae": "linear",
    "speed": "linear",
    "YlGn": "linear",
    "Greens": "linear",
    "BuGn": "linear",
    "cool": "linear",
    "glasgow": "linear",
    "kg": "linear",
    "kb": "linear",
    "kr": "linear",
    # Diverging
    "coolwarm": "diverging",
    "bkr": "diverging",
    "bwr": "diverging",
    "seismic": "diverging",
    "balance": "diverging",
    "berlin": "diverging",
    "vik": "diverging",
    "diff": "diverging",
    "bky": "diverging",
    "bwy": "diverging",
    "lisbon": "diverging",
    "bjy": "diverging",
    "broc": "diverging",
    "tofino": "diverging",
    "cork": "diverging",
    "delta": "diverging",
    "PRGn": "diverging",
    "vanimo": "diverging",
    "bam": "diverging",
    "PiYG": "diverging",
    "RdYlGn": "diverging",
    "Spectral": "diverging",
    "BrBG": "diverging",
    "RdYlBu": "diverging",
    "RdBu": "diverging",
    "roma": "diverging",
    "PuOr": "diverging",
    "managua": "diverging",
    "tarn": "diverging",
    "gwv": "diverging",
    "RdGy": "diverging",
    "curl": "diverging",
    "cwr": "diverging",
    # Multi-Sequential
    "topo": "multi-sequential",
    "bukavu": "multi-sequential",
    "oleron": "multi-sequential",
    "fes": "multi-sequential",
    # Cyclic
    "phase": "cyclic",
    "cyclic_isoluminant": "cyclic",
    "colorwheel": "cyclic",
    "hsv": "cyclic",
    "twilight": "cyclic",
    "twilight_shifted": "cyclic",
    "vikO": "cyclic",
    "romaO": "cyclic",
    "bamO": "cyclic",
    "brocO": "cyclic",
    "corkO": "cyclic",
    # Categorical (Qualitative)
    "glasbey": "categorical",
    "glasbey_bw": "categorical",
    "glasbey_cool": "categorical",
    "glasbey_warm": "categorical",
    "glasbey_dark": "categorical",
    "glasbey_light": "categorical",
    "glasbey_category10": "categorical",
    "glasbey_hv": "categorical",
    "grayCS": "categorical",
    "bilbaoS": "categorical",
    "lajollaS": "categorical",
    "batlowWS": "categorical",
    "budaS": "categorical",
    "hawaiiS": "categorical",
    "tokyoS": "categorical",
    "nuukS": "categorical",
    "naviaS": "categorical",
    "davosS": "categorical",
    "lapazS": "categorical",
    "imolaS": "categorical",
    "devonS": "categorical",
    "osloS": "categorical",
    "lipariS": "categorical",
    "actonS": "categorical",
    "turkuS": "categorical",
    "batlowKS": "categorical",
    "batlowS": "categorical",
    "bamakoS": "categorical",
    "glasgowS": "categorical",
    "Accent": "categorical",
    "Dark2": "categorical",
    "Paired": "categorical",
    "Pastel1": "categorical",
    "Pastel2": "categorical",
    "Set1": "categorical",
    "Set2": "categorical",
    "Set3": "categorical",
    "tab10": "categorical",
    "tab20": "categorical",
    "tab20b": "categorical",
    "tab20c": "categorical",
    # Miscellaneous
    "isolum": "miscellaneous",
    "rainbow4": "miscellaneous",
    "rainbow": "miscellaneous",
    "gist_rainbow": "miscellaneous",
    "jet": "miscellaneous",
    "turbo": "miscellaneous",
    "nipy_spectral": "miscellaneous",
    "gist_ncar": "miscellaneous",
    "CMRmap": "miscellaneous",
    "brg": "miscellaneous",
    "gist_stern": "miscellaneous",
    "gnuplot": "miscellaneous",
    "gnuplot2": "miscellaneous",
    "ocean": "miscellaneous",
    "gist_earth": "miscellaneous",
    "terrain": "miscellaneous",
    "prism": "miscellaneous",
    "flag": "miscellaneous",
}


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
        self.initialize_plotter_settings()
        self.initialize_actors_settings()
        self.initialize_axes_settings()
        self.initialize_axes_at_origin_settings()
        self.initialize_grid_settings()

        # Populate the property tree with initial settings
        self.populate_plotter_settings()
        self.populate_axes()
        self.populate_axes_at_origin()
        self.populate_grid()
        self.populate_actors_settings()

    def initialize_plotter_settings(self):
        self.initial_plotter_settings = {
            "background_color": to_hex(self.plotter.renderer.background_color),
        }

    def initialize_actors_settings(self):
        real_actors = [
            actor
            for actor in self.plotter.renderer.actors.values()
            if (isinstance(actor, pv.Actor) and "scalar" in actor.name)
        ]
        # Style
        self.initial_actors_settings = {"style": "surface"}
        actors_styles = [actor.prop.style for actor in real_actors]
        if actors_styles:
            # If all actors have the same style, use it; otherwise, set to 'mixed'
            if all(style == actors_styles[0] for style in actors_styles):
                self.initial_actors_settings["style"] = actors_styles[0]
            else:
                self.initial_actors_settings["style"] = "mixed"
        # Show edges
        show_edges = [actor.prop.show_edges for actor in real_actors]
        if show_edges:
            if all(show for show in show_edges):
                self.initial_actors_settings["show_edges"] = "True"
            elif all(not show for show in show_edges):
                self.initial_actors_settings["show_edges"] = "False"
            else:
                self.initial_actors_settings["show_edges"] = "mixed"
        # Edge color
        edge_colors = [to_hex(actor.prop.edge_color) for actor in real_actors]
        if edge_colors:
            if all(color == edge_colors[0] for color in edge_colors):
                self.initial_actors_settings["edge_color"] = edge_colors[0]
            else:
                self.initial_actors_settings["edge_color"] = "mixed"
        # Edge Opacity
        edge_opacities = [actor.prop.edge_opacity for actor in real_actors]
        if edge_opacities:
            if all(opacity == edge_opacities[0] for opacity in edge_opacities):
                self.initial_actors_settings["edge_opacity"] = edge_opacities[0]
            else:
                self.initial_actors_settings["edge_opacity"] = "mixed"
        # Line Width
        line_widths = [actor.prop.line_width for actor in real_actors]
        if line_widths:
            if all(width == line_widths[0] for width in line_widths):
                self.initial_actors_settings["line_width"] = line_widths[0]
            else:
                self.initial_actors_settings["line_width"] = "mixed"
        # Colormap
        cmaps = [
            actor.mapper.lookup_table.cmap.name for actor in real_actors if (actor.mapper.lookup_table.cmap is not None)
        ]
        if cmaps:
            # If all actors have the same colormap, use it; otherwise, set to 'mixed'
            if all(cmap == cmaps[0] for cmap in cmaps):
                self.initial_actors_settings["colormap"] = f"{cmaps[0]} : {CMAP_NAMES.get(cmaps[0], 'unknown')}"
            else:
                self.initial_actors_settings["colormap"] = "mixed"
        # Opacity
        opacities = [actor.prop.opacity for actor in real_actors]
        if opacities:
            if all(opacity == opacities[0] for opacity in opacities):
                self.initial_actors_settings["opacity"] = opacities[0]
            else:
                self.initial_actors_settings["opacity"] = "mixed"

    def initialize_axes_settings(self):
        if self.plotter_window._axes_action.isChecked():
            self.initial_axes_settings = {
                "enabled": True,
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
                "line_width": 2,
                "color": "#FFFFFF",
                "x_color": to_hex(pv.global_theme.axes.x_color),
                "y_color": to_hex(pv.global_theme.axes.y_color),
                "z_color": to_hex(pv.global_theme.axes.z_color),
                "x_label": "X",
                "y_label": "Y",
                "z_label": "Z",
                "labels_off": False,
            }

    def initialize_grid_settings(self):
        if any(x.__class__.__name__ == "CubeAxesActor" for x in self.plotter.renderer.actors.values()):
            self.initial_grid_settings = {
                "enabled": True,
                "show_xaxis": self.plotter.renderer.cube_axes_actor.GetXAxisVisibility(),
                "show_yaxis": self.plotter.renderer.cube_axes_actor.GetYAxisVisibility(),
                "show_zaxis": self.plotter.renderer.cube_axes_actor.GetZAxisVisibility(),
                "show_xlabels": self.plotter.renderer.cube_axes_actor.x_label_visibility,
                "show_ylabels": self.plotter.renderer.cube_axes_actor.y_label_visibility,
                "show_zlabels": self.plotter.renderer.cube_axes_actor.z_label_visibility,
                "xtitle": self.plotter.renderer.cube_axes_actor.GetXTitle(),
                "ytitle": self.plotter.renderer.cube_axes_actor.GetYTitle(),
                "ztitle": self.plotter.renderer.cube_axes_actor.GetZTitle(),
                "n_xlabels": self.plotter.renderer.cube_axes_actor.n_xlabels,
                "n_ylabels": self.plotter.renderer.cube_axes_actor.n_ylabels,
                "n_zlabels": self.plotter.renderer.cube_axes_actor.n_zlabels,
                "grid": GRID_VISIBILITY_DICT.get(self.plotter.renderer.cube_axes_actor.GetGridLineLocation()),
                "ticks": TICK_LOCATION_DICT.get(self.plotter.renderer.cube_axes_actor.GetTickLocation()),
                "minor_ticks": self.plotter.renderer.cube_axes_actor.x_axis_minor_tick_visibility,
            }
        else:
            self.initial_grid_settings = {
                "enabled": False,
                "show_xaxis": True,
                "show_yaxis": True,
                "show_zaxis": True,
                "show_xlabels": True,
                "show_ylabels": True,
                "show_zlabels": True,
                "xtitle": "X Axis",
                "ytitle": "Y Axis",
                "ztitle": "Z Axis",
                "n_xlabels": 5,
                "n_ylabels": 5,
                "n_zlabels": 5,
                "grid": "back",
                "ticks": "outside",
                "minor_ticks": False,
            }

    def initialize_axes_at_origin_settings(self):
        if self.plotter_window._axes_at_origin_action.isChecked():
            actor = self.plotter_window.get_actor_by_name("AxesAtOriginActor")
            self.initial_axes_at_origin_settings = {
                "enabled": True,
                "line_width": actor.GetXAxisShaftProperty().GetLineWidth(),
                "x_color": to_hex(actor.GetXAxisTipProperty().GetColor()),
                "y_color": to_hex(actor.GetYAxisTipProperty().GetColor()),
                "z_color": to_hex(actor.GetZAxisTipProperty().GetColor()),
                "x_label": actor.GetXAxisLabelText(),
                "y_label": actor.GetYAxisLabelText(),
                "z_label": actor.GetZAxisLabelText(),
                "labels_off": actor.GetAxisLabels() == 0,
            }
        else:
            self.initial_axes_at_origin_settings = {
                "enabled": False,
                "line_width": 2,
                "x_color": to_hex(pv.global_theme.axes.x_color),
                "y_color": to_hex(pv.global_theme.axes.y_color),
                "z_color": to_hex(pv.global_theme.axes.z_color),
                "x_label": "X",
                "y_label": "Y",
                "z_label": "Z",
                "labels_off": False,
            }

    def populate_plotter_settings(self) -> None:
        """Populate the property tree with plotter settings."""
        self.tree.add_property(
            name="Background Color",
            value=self.initial_plotter_settings.get("background_color", "#FFFFFF"),
            editor_type="color",
        )

    @property
    def current_plotter_settings(self) -> dict:
        """Get current plotter settings from the property tree.

        Returns
        -------
        dict
            Dictionary containing all plotter configuration values.
        """
        values = self.tree.get_all_values()
        return {
            "background_color": values["Background Color"],
        }

    def populate_actors_settings(self) -> None:
        """Populate the property tree with all actors settings in the plotter."""
        group = self.tree.add_group(name="Actors")

        self.tree.add_property(
            name="Style",
            value=self.initial_actors_settings.get("style", "surface"),
            editor_type="enum",
            choices=["surface", "wireframe", "points", "mixed"],
            parent=group,
        )

        self.tree.add_property(
            name="Show Edges",
            value=self.initial_actors_settings.get("show_edges", "True"),
            editor_type="enum",
            choices=["True", "False", "mixed"],
            parent=group,
        )

        self.tree.add_property(
            name="Edge Color",
            value=self.initial_actors_settings.get("edge_color", "#FFFFFF"),
            editor_type="color",
            parent=group,
        )

        self.tree.add_property(
            name="Edge Opacity",
            value=self.initial_actors_settings.get("edge_opacity", 0.3),
            editor_type="slider",
            parent=group,
            min=0.0,
            max=1.0,
            decimals=1,
            steps=10,
        )

        self.tree.add_property(
            name="Line Width",
            value=self.initial_actors_settings.get("line_width", 1),
            editor_type="float",
            parent=group,
            min=0.1,
            max=10.0,
            decimals=2,
            steps=100,
        )

        self.tree.add_property(
            name="Colormap",
            value=self.initial_actors_settings.get("colormap", "viridis"),
            editor_type="enum",
            choices=["mixed"] + [f"{n} : {t}" for n, t in CMAP_NAMES.items()],
            parent=group,
        )

        self.tree.add_property(
            name="Opacity",
            value=self.initial_actors_settings.get("opacity", 1.0),
            editor_type="slider",
            parent=group,
            min=0.0,
            max=1.0,
            decimals=1,
            steps=10,
        )

    @property
    def current_actors_settings(self) -> dict:
        """Get current actors settings from the property tree.

        Returns
        -------
        dict
            Dictionary containing all actors configuration values.
        """
        values = self.tree.get_all_values()
        return {
            "style": values["Actors:Style"],
            "show_edges": values["Actors:Show Edges"],
            "edge_color": values["Actors:Edge Color"],
            "edge_opacity": float(values["Actors:Edge Opacity"]),
            "line_width": float(values["Actors:Line Width"]),
            "colormap": values["Actors:Colormap"],
            "opacity": float(values["Actors:Opacity"]),
        }

    def populate_axes(self) -> None:
        """Populate the property tree with axes settings from the plotter.

        Creates a checkable group with properties for line width, colors, labels,
        and visibility options for the axes display.
        """
        group = self.tree.add_checkable_group(
            name="Axes",
            checked=self.initial_axes_settings["enabled"],
        )
        group.setExpanded(self.initial_axes_settings["enabled"])
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
        """Get current axes settings from the property tree.

        Returns
        -------
        dict
            Dictionary containing all axes configuration values.
        """
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

    def populate_axes_at_origin(self) -> None:
        """Populate the property tree with axes at origin settings from the plotter.

        Creates a checkable group with properties for line width, colors, and labels
        for the axes displayed at the coordinate system origin.
        """
        group = self.tree.add_checkable_group(
            name="Axes at Origin",
            checked=self.initial_axes_at_origin_settings["enabled"],
        )
        group.setExpanded(self.initial_axes_at_origin_settings["enabled"])
        self.tree.add_property(
            name="Line Width",
            value=int(self.initial_axes_at_origin_settings["line_width"]),
            editor_type="int",
            parent=group,
            min=1,
            max=100,
        )
        self.tree.add_property(
            name="X Axis Color",
            value=self.initial_axes_at_origin_settings["x_color"],
            editor_type="color",
            parent=group,
        )
        self.tree.add_property(
            name="Y Axis Color",
            value=self.initial_axes_at_origin_settings["y_color"],
            editor_type="color",
            parent=group,
        )
        self.tree.add_property(
            name="Z Axis Color",
            value=self.initial_axes_at_origin_settings["z_color"],
            editor_type="color",
            parent=group,
        )
        self.tree.add_property(
            name="X Axis Label",
            value=self.initial_axes_at_origin_settings["x_label"],
            editor_type="string",
            parent=group,
        )
        self.tree.add_property(
            name="Y Axis Label",
            value=self.initial_axes_at_origin_settings["y_label"],
            editor_type="string",
            parent=group,
        )
        self.tree.add_property(
            name="Z Axis Label",
            value=self.initial_axes_at_origin_settings["z_label"],
            editor_type="string",
            parent=group,
        )
        self.tree.add_property(
            name="Hide Labels",
            value=self.initial_axes_at_origin_settings["labels_off"],
            editor_type="bool",
            parent=group,
        )

    @property
    def current_axes_at_origin_settings(self) -> dict:
        """Get current axes at origin settings from the property tree.

        Returns
        -------
        dict
            Dictionary containing all axes at origin configuration values.
        """
        values = self.tree.get_all_values()
        return {
            "enabled": bool(values["Axes at Origin"]),
            "line_width": int(values["Axes at Origin:Line Width"]),
            "x_color": values["Axes at Origin:X Axis Color"],
            "y_color": values["Axes at Origin:Y Axis Color"],
            "z_color": values["Axes at Origin:Z Axis Color"],
            "x_label": values["Axes at Origin:X Axis Label"],
            "y_label": values["Axes at Origin:Y Axis Label"],
            "z_label": values["Axes at Origin:Z Axis Label"],
            "labels_off": bool(values["Axes at Origin:Hide Labels"]),
        }

    def populate_grid(self) -> None:
        """Populate the property tree with grid settings from the plotter.

        Creates a checkable group with properties for axis visibility, labels, titles,
        grid lines, tick locations, and other grid display options.
        """
        group = self.tree.add_checkable_group(
            name="Grid",
            checked=self.initial_grid_settings["enabled"],
        )
        group.setExpanded(self.initial_grid_settings["enabled"])
        self.tree.add_property(
            name="Show X Axis",
            value=self.initial_grid_settings["show_xaxis"],
            editor_type="bool",
            parent=group,
        )
        self.tree.add_property(
            name="Show Y Axis",
            value=self.initial_grid_settings["show_yaxis"],
            editor_type="bool",
            parent=group,
        )
        self.tree.add_property(
            name="Show Z Axis",
            value=self.initial_grid_settings["show_zaxis"],
            editor_type="bool",
            parent=group,
        )
        self.tree.add_property(
            name="Show X Labels",
            value=self.initial_grid_settings["show_xlabels"],
            editor_type="bool",
            parent=group,
        )
        self.tree.add_property(
            name="Show Y Labels",
            value=self.initial_grid_settings["show_ylabels"],
            editor_type="bool",
            parent=group,
        )
        self.tree.add_property(
            name="Show Z Labels",
            value=self.initial_grid_settings["show_zlabels"],
            editor_type="bool",
            parent=group,
        )
        self.tree.add_property(
            name="X Title",
            value=self.initial_grid_settings["xtitle"],
            editor_type="string",
            parent=group,
        )
        self.tree.add_property(
            name="Y Title",
            value=self.initial_grid_settings["ytitle"],
            editor_type="string",
            parent=group,
        )
        self.tree.add_property(
            name="Z Title",
            value=self.initial_grid_settings["ztitle"],
            editor_type="string",
            parent=group,
        )
        self.tree.add_property(
            name="Number of X Labels",
            value=int(self.initial_grid_settings["n_xlabels"]),
            editor_type="int",
            parent=group,
            min=1,
            max=20,
        )
        self.tree.add_property(
            name="Number of Y Labels",
            value=int(self.initial_grid_settings["n_ylabels"]),
            editor_type="int",
            parent=group,
            min=1,
            max=20,
        )
        self.tree.add_property(
            name="Number of Z Labels",
            value=int(self.initial_grid_settings["n_zlabels"]),
            editor_type="int",
            parent=group,
            min=1,
            max=20,
        )
        self.tree.add_property(
            name="Grid Lines",
            value=self.initial_grid_settings["grid"],
            editor_type="enum",
            parent=group,
            choices=list(GRID_VISIBILITY_DICT.values()),
        )
        self.tree.add_property(
            name="Tick Location",
            value=self.initial_grid_settings["ticks"],
            editor_type="enum",
            parent=group,
            choices=list(TICK_LOCATION_DICT.values()),
        )
        self.tree.add_property(
            name="Minor Ticks",
            value=self.initial_grid_settings["minor_ticks"],
            editor_type="bool",
            parent=group,
        )

    @property
    def current_grid_settings(self) -> dict:
        """Get current grid settings from the property tree.

        Returns
        -------
        dict
            Dictionary containing all grid configuration values.
        """
        values = self.tree.get_all_values()
        return {
            "enabled": bool(values["Grid"]),
            "show_xaxis": bool(values["Grid:Show X Axis"]),
            "show_yaxis": bool(values["Grid:Show Y Axis"]),
            "show_zaxis": bool(values["Grid:Show Z Axis"]),
            "show_xlabels": bool(values["Grid:Show X Labels"]),
            "show_ylabels": bool(values["Grid:Show Y Labels"]),
            "show_zlabels": bool(values["Grid:Show Z Labels"]),
            "xtitle": values["Grid:X Title"],
            "ytitle": values["Grid:Y Title"],
            "ztitle": values["Grid:Z Title"],
            "n_xlabels": int(values["Grid:Number of X Labels"]),
            "n_ylabels": int(values["Grid:Number of Y Labels"]),
            "n_zlabels": int(values["Grid:Number of Z Labels"]),
            "grid": values["Grid:Grid Lines"],
            "ticks": values["Grid:Tick Location"],
            "minor_ticks": bool(values["Grid:Minor Ticks"]),
        }

    def _on_ok(self) -> None:
        """Handle Ok button click - apply changes and close dialog."""
        self._apply_settings(
            self.current_plotter_settings,
            self.current_actors_settings,
            self.current_axes_settings,
            self.current_axes_at_origin_settings,
            self.current_grid_settings,
        )
        self.accept()

    def _on_apply(self) -> None:
        """Handle Apply button click - apply changes without closing."""
        self._apply_settings(
            self.current_plotter_settings,
            self.current_actors_settings,
            self.current_axes_settings,
            self.current_axes_at_origin_settings,
            self.current_grid_settings,
        )

    def _on_cancel(self) -> None:
        """Handle Cancel button click - close dialog without applying changes."""
        self._apply_settings(
            self.initial_plotter_settings,
            self.initial_actors_settings,
            self.initial_axes_settings,
            self.initial_axes_at_origin_settings,
            self.initial_grid_settings,
        )
        self.reject()

    def _apply_settings(
        self,
        plotter_settings: dict,
        actors_settings: dict,
        axes_settings: dict,
        axes_at_origin_settings: dict,
        grid_settings: dict,
    ) -> None:
        """
        Apply settings to the plotter.

        Parameters
        ----------
        axes_settings : dict
            Configuration for the main axes display.
        axes_at_origin_settings : dict
            Configuration for axes at coordinate origin.
        grid_settings : dict
            Configuration for the grid display.

        Notes
        -----
        This method is called by both Ok and Apply buttons.
        """

        # Apply plotter settings
        self.plotter.renderer.background_color = pv.Color(plotter_settings["background_color"]).float_rgb

        # Apply actors settings
        # https://github.com/pyvista/pyvista/blob/main/pyvista/plotting/_property.py
        for actor in self.plotter.renderer.actors.values():
            if not isinstance(actor, pv.Actor):
                continue
            if actors_settings["style"] != "mixed":
                actor.prop.style = actors_settings["style"]
            if actors_settings["show_edges"] != "mixed":
                actor.prop.show_edges = True if actors_settings["show_edges"] == "True" else False
            if actors_settings["edge_color"] != "mixed":
                edge_color = pv.Color(actors_settings["edge_color"]).float_rgb
                actor.prop.edge_color = edge_color
            if actors_settings["edge_opacity"] != "mixed":
                actor.prop.edge_opacity = float(actors_settings["edge_opacity"])
            if actors_settings["line_width"] != "mixed":
                actor.prop.line_width = float(actors_settings["line_width"])
            if actors_settings["colormap"] != "mixed":
                cmap_name = actors_settings["colormap"].split(" : ")[0]
                actor.mapper.lookup_table.cmap = cmap_name
            if actors_settings["opacity"] != "mixed":
                actor.prop.opacity = float(actors_settings["opacity"])

        # Apply axes settings
        if axes_settings["enabled"]:
            self.plotter.show_axes()
            self.plotter_window._axes_action.setChecked(True)
            self.plotter.renderer.axes_actor.GetXAxisShaftProperty().SetLineWidth(axes_settings["line_width"])
            self.plotter.renderer.axes_actor.GetYAxisShaftProperty().SetLineWidth(axes_settings["line_width"])
            self.plotter.renderer.axes_actor.GetZAxisShaftProperty().SetLineWidth(axes_settings["line_width"])
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
                self.plotter.renderer.axes_actor.AxisLabelsOff()
            else:
                self.plotter.renderer.axes_actor.AxisLabelsOn()
        else:
            self.plotter.hide_axes()
            self.plotter_window._axes_action.setChecked(False)

        # Apply axes at origin settings
        if axes_at_origin_settings["enabled"]:
            self.plotter_window._toggle_axes_at_origin(True)
            self.plotter_window._axes_at_origin_action.setChecked(True)
            actor = self.plotter_window.get_actor_by_name("AxesAtOriginActor")
            actor.GetXAxisShaftProperty().SetLineWidth(axes_at_origin_settings["line_width"])
            actor.GetYAxisShaftProperty().SetLineWidth(axes_at_origin_settings["line_width"])
            actor.GetZAxisShaftProperty().SetLineWidth(axes_at_origin_settings["line_width"])
            x_color = pv.Color(axes_at_origin_settings["x_color"]).float_rgb
            y_color = pv.Color(axes_at_origin_settings["y_color"]).float_rgb
            z_color = pv.Color(axes_at_origin_settings["z_color"]).float_rgb
            actor.GetXAxisShaftProperty().SetColor(x_color)
            actor.GetYAxisShaftProperty().SetColor(y_color)
            actor.GetZAxisShaftProperty().SetColor(z_color)
            actor.GetXAxisTipProperty().SetColor(x_color)
            actor.GetYAxisTipProperty().SetColor(y_color)
            actor.GetZAxisTipProperty().SetColor(z_color)
            actor.SetXAxisLabelText(axes_at_origin_settings["x_label"])
            actor.SetYAxisLabelText(axes_at_origin_settings["y_label"])
            actor.SetZAxisLabelText(axes_at_origin_settings["z_label"])
            if axes_at_origin_settings["labels_off"]:
                actor.AxisLabelsOff()
            else:
                actor.AxisLabelsOn()
        else:
            self.plotter_window._toggle_axes_at_origin(False)
            self.plotter_window._axes_at_origin_action.setChecked(False)

        # Apply grid settings
        if grid_settings["enabled"]:
            self.plotter.show_grid(
                show_xaxis=grid_settings["show_xaxis"],
                show_yaxis=grid_settings["show_yaxis"],
                show_zaxis=grid_settings["show_zaxis"],
                show_xlabels=grid_settings["show_xlabels"],
                show_ylabels=grid_settings["show_ylabels"],
                show_zlabels=grid_settings["show_zlabels"],
                xtitle=grid_settings["xtitle"],
                ytitle=grid_settings["ytitle"],
                ztitle=grid_settings["ztitle"],
                n_xlabels=grid_settings["n_xlabels"],
                n_ylabels=grid_settings["n_ylabels"],
                n_zlabels=grid_settings["n_zlabels"],
                grid=grid_settings["grid"],
                ticks=grid_settings["ticks"],
                minor_ticks=grid_settings["minor_ticks"],
            )
            self.plotter_window._grid_action.setChecked(True)
        else:
            self.plotter.remove_bounds_axes()
            self.plotter_window._grid_action.setChecked(False)
