"""
Qt-based visualization plotter for pyemsi.

Provides a custom Plotter class that composes PyVista plotting functionality
with Qt interactivity using pyvistaqt.QtInteractor and PySide6 backend.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from collections.abc import Sequence

import pyvista as pv
import numpy as np

# TYPE_CHECKING imports (for type checkers only, not runtime)
if TYPE_CHECKING:
    from pyvistaqt import QtInteractor
    from pyemsi.qt_window import QtPlotterWindow

# Qt imports are optional (only needed for desktop mode)
try:
    from pyvistaqt import QtInteractor
    from pyemsi.qt_window import QtPlotterWindow

    HAS_QT = True
except ImportError:
    HAS_QT = False


class Plotter:
    """
    Custom plotter for interactive 3D visualization in desktop and Jupyter notebook environments.

    This class provides dual-mode support:
    - Desktop mode (default): Uses Qt-based rendering with QtInteractor
    - Notebook mode: Uses PyVista's native Jupyter backend (e.g., Trame)

    Parameters
    ----------
    title : str, optional
        Window title (desktop mode only). Default is "pyemsi Plotter".
    window_size : tuple of int, optional
        Window size as (width, height) in pixels (desktop mode only). Default is (1024, 768).
    position : tuple of int, optional
        Window position as (x, y) in screen coordinates (desktop mode only). If None, uses OS default.
    notebook : bool, optional
        If True, uses PyVista's native notebook backend for Jupyter environments.
        If False, uses Qt-based desktop rendering. Default is False.
    backend : str, optional
        PyVista backend to use in notebook mode (e.g., 'trame', 'static', 'panel').
        If None, PyVista chooses the default. Default is None.
    **kwargs
        Additional keyword arguments passed to the underlying plotter (QtInteractor or pv.Plotter).

    Attributes
    ----------
    plotter : QtInteractor or pv.Plotter
        The internal plotter instance that handles rendering.
    app : QApplication or None
        The Qt application instance (desktop mode only).
    mesh : pv.DataSet or None
        The mesh loaded via set_file(), if any.
    reader : pv.BaseReader or None
        The PyVista reader instance from set_file(), if any.
    notebook : bool
        Whether the plotter is in notebook mode.
    """

    # Type annotations for instance attributes
    _notebook: bool
    _backend: str | None
    _mesh: pv.DataSet | pv.MultiBlock | None
    reader: pv.BaseReader | None
    plotter: "QtInteractor | pv.Plotter"
    _window: "QtPlotterWindow | None"
    _qt_props: dict[str, object]
    _qt_interactor_kwargs: dict[str, object]
    _feature_edges_props: dict[str, object]
    _scalar_props: dict[str, object]
    _vector_props: dict[str, object]
    _contour_props: dict[str, object]
    _block_visibility: dict[str, bool]

    def __init__(
        self,
        filepath: str | Path | None = None,
        title: str = "pyemsi Plotter",
        window_size: tuple[int, int] | None = None,
        position: tuple[int, int] | None = None,
        notebook: bool = False,
        backend: str | None = "html",
        **kwargs,
    ):
        """
        Initialize the plotter in desktop or notebook mode.

        Parameters
        ----------
        filepath : str or Path, optional
            Path to a mesh file to load immediately. If provided, calls set_file() automatically.
        title : str, optional
            Window title (desktop mode only). Default is "pyemsi Plotter".
        window_size : tuple of int or None, optional
            Window size as (width, height) in pixels (desktop mode only). Default is None.
        position : tuple of int or None, optional
            Window position as (x, y) in screen coordinates (desktop mode only). If None, uses OS default.
        notebook : bool, optional
            If True, uses PyVista's native notebook backend for Jupyter environments.
            If False, uses Qt-based desktop rendering. Default is False.
        backend : str, optional
            PyVista backend to use in notebook mode (e.g., 'html', 'trame', 'static', 'panel').
            If None, PyVista chooses the default. Default is 'html'.
        **kwargs
            Additional keyword arguments passed to the underlying plotter (QtInteractor or pv.Plotter).
        """
        self._notebook = notebook
        self._backend = backend
        self._mesh = None
        self.reader = None
        self._qt_props = {"title": title, "window_size": window_size, "position": position}
        self._qt_interactor_kwargs = kwargs
        self._feature_edges_props = {"color": "white", "line_width": 1, "opacity": 1.0}
        self._scalar_props = {}
        self._vector_props = {}
        self._contour_props = {}
        self._block_visibility = {}
        if filepath is not None:
            self.set_file(filepath)
        # Initialize based on mode
        if self._notebook:
            self._init_notebook_mode(**kwargs)
        else:
            self._init_qt_mode(**kwargs)

    def _init_qt_mode(
        self,
        **kwargs,
    ) -> None:
        """Initialize Qt-based desktop mode."""
        if not HAS_QT:
            raise ImportError("Qt dependencies not available. Install with: pip install PySide6 pyvistaqt")

        # Create QtPlotterWindow with stored properties
        self._window = QtPlotterWindow(
            title=self._qt_props.get("title", "pyemsi Plotter"),
            window_size=self._qt_props.get("window_size", None),
            position=self._qt_props.get("position", None),
            parent_plotter=self,
            **self._qt_interactor_kwargs,
        )

        # Extract plotter reference from window
        self.plotter = self._window.plotter

    def _init_notebook_mode(self, **kwargs) -> None:
        """Initialize PyVista native notebook mode."""
        pv.set_jupyter_backend(self._backend)
        self.plotter = pv.Plotter(**kwargs)
        self._window = None

    def set_file(self, filepath: str | Path) -> "Plotter":
        """
        Load a mesh file and display its feature edges.

        This method reads a mesh file using PyVista's reader, stores both the reader
        and the loaded mesh, extracts feature edges, and updates the visualization.

        Parameters
        ----------
        filepath : str or Path
            Path to the mesh file to load. Supports various formats including VTK,
            VTM, STL, OBJ, PLY, and others supported by PyVista.

        Returns
        -------
        Plotter
            Returns self to enable method chaining.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        ValueError
            If the file format is not supported or the file cannot be read.
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Mesh file not found: {filepath}")

        try:
            self.reader = pv.get_reader(str(filepath))
        except Exception as e:
            raise ValueError(f"Failed to read mesh file '{filepath}': {e}") from e

        return self

    def _time_reader(self):
        """Return the underlying TimeReader when available, else None."""
        time_reader_type = getattr(pv, "TimeReader", None)
        if time_reader_type is None:
            return None
        if self.reader is None:
            return None
        return self.reader if isinstance(self.reader, time_reader_type) else None

    @property
    def active_time_point(self) -> int | None:
        """Active time point if the reader is time-aware, otherwise None."""
        time_reader = self._time_reader()
        return None if time_reader is None else time_reader.time_values.index(time_reader.active_time_value)

    @property
    def active_time_value(self) -> float | None:
        """Active time value if the reader is time-aware, otherwise None."""
        time_reader = self._time_reader()
        return None if time_reader is None else time_reader.active_time_value

    @property
    def number_time_points(self) -> int | None:
        """Number of time points if the reader is time-aware, otherwise None."""
        time_reader = self._time_reader()
        return None if time_reader is None else time_reader.number_time_points

    @property
    def time_values(self) -> Sequence[float] | None:
        """Time values if the reader is time-aware, otherwise None."""
        time_reader = self._time_reader()
        return None if time_reader is None else time_reader.time_values

    def set_active_time_point(self, time_point: int) -> None:
        """Set the active time point when time-aware; otherwise silently no-op."""
        time_reader = self._time_reader()
        if time_reader is None:
            return None
        time_reader.set_active_time_point(time_point)
        return None

    def set_active_time_value(self, time_value: float) -> None:
        """Set the active time value when time-aware; otherwise silently no-op."""
        time_reader = self._time_reader()
        if time_reader is None:
            return None
        time_reader.set_active_time_value(time_value)
        return None

    def time_point_value(self, time_point: int) -> float | None:
        """Return the time value for a time point when time-aware; otherwise None."""
        time_reader = self._time_reader()
        return None if time_reader is None else time_reader.time_point_value(time_point)

    @property
    def mesh(self) -> pv.DataSet | pv.MultiBlock | None:
        """Get the current mesh."""
        if self._mesh is None:
            if self.reader is None:
                raise ValueError("No reader available. Call set_file() first.")
            if isinstance(self.reader, pv.PVDReader):
                self._mesh = self.reader.read()[0]
            else:
                self._mesh = self.reader.read()
            # Lazily populate _block_visibility for new blocks
            if isinstance(self._mesh, pv.MultiBlock):
                for idx, block in enumerate(self._mesh):
                    if block is None:
                        continue
                    name = self._mesh.get_block_name(idx)
                    if not name:
                        name = str(idx)
                    if name not in self._block_visibility:
                        self._block_visibility[name] = True
        return self._mesh

    def _iter_blocks(self, skip_empty: bool = True):
        """Yield (index, block, name) for single or MultiBlock meshes."""
        if isinstance(self.mesh, pv.MultiBlock):
            for idx, block in enumerate(self.mesh):
                if block is None:
                    continue
                if skip_empty and getattr(block, "n_points", 0) == 0:
                    continue
                name = self.mesh.get_block_name(idx)
                if not name:
                    name = str(idx)
                yield idx, block, name
        else:
            block = self.mesh
            if block is None:
                return
            if skip_empty and block.n_points == 0:
                return
            yield 0, block, None

    def get_block_names(self) -> list[str]:
        """Return list of block names from the mesh.

        For multi-block meshes, returns all block names (or string indices for
        unnamed blocks). For single meshes, returns empty list.

        Returns
        -------
        list[str]
            List of block name strings.
        """
        block_names = []
        if isinstance(self.mesh, pv.MultiBlock):
            for idx, block, name in self._iter_blocks(skip_empty=False):
                block_names.append(name if name else str(idx))
        return block_names

    def get_block_visibility(self, block_name: str) -> bool:
        """Check if a block is visible.

        Returns the visibility state from the internal visibility dictionary.
        Defaults to True for blocks not yet tracked.

        Parameters
        ----------
        block_name : str
            The name of the block to check.

        Returns
        -------
        bool
            True if block is visible, False otherwise.
        """
        return self._block_visibility.get(block_name, True)

    def set_block_visibility(self, block_name: str, visible: bool) -> None:
        """Set visibility for all actors associated with a block.

        Updates the visibility state in the internal dictionary and applies it
        to all actors (feature edges, scalar field, contours, vector field)
        associated with the specified block, then renders the scene.

        Parameters
        ----------
        block_name : str
            The name of the block to update.
        visible : bool
            True to show the block, False to hide it.
        """
        # Store visibility state in dictionary
        self._block_visibility[block_name] = visible

        # Update visibility for all actor patterns for this block
        actor_patterns = [
            f"feature_edges_block_{block_name}",
            f"scalar_field_block_{block_name}",
            f"contour_block_{block_name}",
            f"vector_field_block_{block_name}",
        ]

        for actor_name in actor_patterns:
            if actor_name in self.plotter.renderer.actors:
                self.plotter.renderer.actors[actor_name].SetVisibility(visible)

        # Render to update display
        self.plotter.render()

    def set_blocks_visibility(self, visibility: dict[str, bool]) -> None:
        """Set visibility for multiple blocks in batch.

        Updates the visibility state for multiple blocks at once, then renders
        the scene. More efficient than calling set_block_visibility repeatedly.
        Works in both desktop and notebook modes.

        Parameters
        ----------
        visibility : dict[str, bool]
            Dictionary mapping block names to visibility states.
            True to show the block, False to hide it.
        """
        # Update visibility states in dictionary
        self._block_visibility.update(visibility)

        # Apply visibility to existing actors
        for block_name, visible in visibility.items():
            actor_patterns = [
                f"feature_edges_block_{block_name}",
                f"scalar_field_block_{block_name}",
                f"contour_block_{block_name}",
                f"vector_field_block_{block_name}",
            ]

            for actor_name in actor_patterns:
                if actor_name in self.plotter.renderer.actors:
                    self.plotter.renderer.actors[actor_name].SetVisibility(visible)

        # Render to update display
        self.plotter.render()

    def set_feature_edges(self, color: str = "white", line_width: int = 1, opacity: float = 1.0, **kwargs) -> "Plotter":
        """
        Set properties for feature edges visualization.

        Feature edges are extracted and displayed when show() is called on a loaded mesh.
        This method stores the visualization properties for later use.

        Parameters
        ----------
        color : str, optional
            Color of the feature edges. Default is "white".
        line_width : int, optional
            Width of the feature edges lines. Default is 1.
        opacity : float, optional
            Opacity of the feature edges (0.0 to 1.0). Default is 1.0.
        **kwargs
            Additional keyword arguments passed to add_mesh() for feature edges.

        Returns
        -------
        Plotter
            Returns self to enable method chaining.
        """
        self._feature_edges_props = {
            "color": color,
            "line_width": line_width,
            "opacity": opacity,
            **kwargs,
        }
        return self

    def _plot_feature_edges(self) -> None:
        """
        Extract and plot feature edges from the stored mesh.

        For MultiBlock datasets, creates separate actors for each block's feature edges.
        For single datasets, creates a single feature edges actor.
        Automatically resets the camera to frame the mesh after plotting.
        Applies visibility settings from _block_visibility to each actor.
        """
        for idx, block, block_name in self._iter_blocks():
            edges = block.extract_feature_edges()
            if edges.n_points == 0:
                continue
            actor_name = f"feature_edges_block_{block_name}" if block_name else "feature_edges"
            actor = self.plotter.add_mesh(edges, name=actor_name, pickable=False, **self._feature_edges_props)
            # Apply visibility from stored state
            if block_name:
                actor.SetVisibility(self.get_block_visibility(block_name))

    def set_scalar(
        self,
        name: Literal[
            "B-Mag (T)",
            "Flux (A/m)",
            "J-Mag (A/m^2)",
            "Loss (W/m^3)",
            "F Nodal-Mag (N/m^3)",
            "F Lorents-Mag (N/m^3)",
            "Heat Density (W/m^3)",
            "Heat (W)",
        ],
        mode: Literal["node", "element"] = "element",
        cell2point: bool = True,
        **kwargs,
    ) -> "Plotter":
        """
        Set properties for scalar field visualization.

        The scalar field is displayed when show() is called on a loaded mesh.
        This method stores the visualization properties for later use.

        Parameters
        ----------
        name : {'B-Mag (T)', 'Flux (A/m)', 'J-Mag (A/m^2)',
                'Loss (W/m^3)', 'F Nodal-Mag (N/m^3)', 'F Lorents-Mag (N/m^3)',
                'Heat Density (W/m^3)', 'Heat (W)'},
            Name of the scalar field to visualize (must exist in mesh arrays).
        mode : {'node', 'element'}, optional
            Whether the scalar field is defined on nodes or elements. Default is 'element'.
        cell2point : bool, optional
            If True and mode is 'element', convert cell data to point data for smoother visualization.
            Default is True.
        **kwargs
            Additional keyword arguments passed to add_mesh() for scalar visualization.
            Common options include: show_edges, edge_color, edge_opacity, cmap, clim.

        Returns
        -------
        Plotter
            Returns self to enable method chaining.
        """
        self._scalar_props["name"] = name
        self._scalar_props["mode"] = mode
        self._scalar_props["cell2point"] = cell2point
        for key, value in kwargs.items():
            self._scalar_props[key] = value
        self._scalar_props["show_edges"] = kwargs.get("show_edges", True)
        self._scalar_props["edge_color"] = kwargs.get("edge_color", "white")
        self._scalar_props["edge_opacity"] = kwargs.get("edge_opacity", 0.25)
        return self

    def _plot_scalar_field(self) -> None:
        """
        Plot the scalar field on the mesh based on the stored scalar properties.

        Applies visibility settings from _block_visibility to each actor.
        """
        if self._scalar_props is None:
            return  # No scalar properties set
        name = self._scalar_props.get("name")
        mode = self._scalar_props.get("mode", "element")
        cell2point = self._scalar_props.get("cell2point", True)
        for idx, block, block_name in self._iter_blocks():
            block_to_plot = block.cell_data_to_point_data() if mode == "element" and cell2point else block
            if name not in block_to_plot.array_names:
                continue
            actor_name = f"scalar_field_block_{block_name}" if block_name else "scalar_field"
            actor = self.plotter.add_mesh(
                block_to_plot,
                scalars=name,
                preference="cell" if mode == "element" else "point",
                name=actor_name,
                pickable=True,
                **{k: v for k, v in self._scalar_props.items() if k not in ["name", "mode", "cell2point"]},
            )
            # Apply visibility from stored state
            if block_name:
                actor.SetVisibility(self.get_block_visibility(block_name))

    def set_contour(
        self,
        name: Literal[
            "B-Mag (T)",
            "Flux (A/m)",
            "J-Mag (A/m^2)",
            "Loss (W/m^3)",
            "F Nodal-Mag (N/m^3)",
            "F Lorents-Mag (N/m^3)",
            "Heat Density (W/m^3)",
            "Heat (W)",
        ] = "Flux (A/m)",
        n_contours: int = 10,
        color: str = "red",
        line_width: int = 3,
        **kwargs,
    ) -> "Plotter":
        """
        Set properties for contour visualization.

        Parameters
        ----------
        name : {'B-Mag (T)', 'Flux (A/m)', 'J-Mag (A/m^2)',
                'Loss (W/m^3)', 'F Nodal-Mag (N/m^3)', 'F Lorents-Mag (N/m^3)',
                'Heat Density (W/m^3)', 'Heat (W)'},
            Name of the scalar field to visualize (must exist in mesh arrays).
        n_contours : int, optional
            Number of contour levels to generate. Default is 10.
        color : str, optional
            Color of the contour lines/surfaces. Default is "red".
        line_width : int, optional
            Width of the contour lines. Default is 3.
        **kwargs
            Additional keyword arguments passed to add_mesh() when rendering the contours.

        Returns
        -------
        Plotter
            Returns self to enable method chaining.
        """
        self._contour_props["name"] = name
        self._contour_props["n_contours"] = n_contours
        self._contour_props["color"] = color
        self._contour_props["line_width"] = line_width
        for key, value in kwargs.items():
            self._contour_props[key] = value

        return self

    def _plot_contours(self) -> None:
        """
        Plot contour lines/surfaces for the configured scalar field.
        """
        if self._contour_props is None:
            return

        name = self._contour_props.get("name")
        n_contours = max(1, int(self._contour_props.get("n_contours", 10)))
        color = self._contour_props.get("color", "red")
        line_width = self._contour_props.get("line_width", 3)
        contour_kwargs = {
            k: v for k, v in self._contour_props.items() if k not in ["name", "n_contours", "color", "line_width"]
        }

        # Collect prepared blocks and global scalar range
        global_min: float | None = None
        global_max: float | None = None

        iter_blocks = list(self._iter_blocks())

        for idx, block, _ in iter_blocks:
            if name not in block.array_names:
                continue
            values = block[name]
            if values.size == 0:
                continue
            block_min = float(np.min(values))
            block_max = float(np.max(values))
            global_min = block_min if global_min is None else min(global_min, block_min)
            global_max = block_max if global_max is None else max(global_max, block_max)

        if global_min is None or global_max is None:
            return

        if np.isclose(global_min, global_max):
            levels = np.array([global_min])
        else:
            levels = np.linspace(global_min, global_max, num=n_contours)

        for idx, block, block_name in iter_blocks:
            if name not in block.array_names:
                continue
            contours = block.contour(isosurfaces=levels, scalars=name)
            if contours.n_points == 0:
                continue
            actor_name = f"contour_block_{block_name}" if block_name else "contour"
            actor = self.plotter.add_mesh(
                contours, name=actor_name, color=color, line_width=line_width, **contour_kwargs
            )
            # Apply visibility from stored state
            if block_name:
                actor.SetVisibility(self.get_block_visibility(block_name))

    def set_vector(
        self,
        name: Literal[
            "B-Mag (T)",
            "B-Vec (T)",
            "Flux (A/m)",
            "J-Mag (A/m^2)",
            "J-Vec (A/m^2)",
            "Loss (W/m^3)",
            "F Nodal-Mag (N/m^3)",
            "F Nodal-Vec (N/m^3)",
            "F Lorents-Mag (N/m^3)",
            "F Lorents-Vec (N/m^3)",
            "Heat Density (W/m^3)",
            "Heat (W)",
        ],
        scale: str | bool | None = None,
        glyph_type: str = "arrow",
        factor: float = 1.0,
        tolerance: float | None = None,
        color_mode: str = "scale",
        **kwargs,
    ) -> "Plotter":
        """
        Set properties for vector field visualization using glyphs.

        Vector fields are displayed as glyphs (arrows, cones, or spheres) when show() is called.
        Each glyph is oriented along the vector direction and optionally scaled by magnitude.

        Parameters
        ----------
        name : {'B-Mag (T)', 'B-Vec (T)', 'Flux (A/m)',
                'J-Mag (A/m^2)', 'J-Vec (A/m^2)', 'Loss (W/m^3)',
                'F Nodal-Mag (N/m^3)', 'F Nodal-Vec (N/m^3)',
                'F Lorents-Mag (N/m^3)', 'F Lorents-Vec (N/m^3)',
                'Heat Density (W/m^3)', 'Heat (W)'},
            Name of the vector field to visualize (must exist in mesh arrays as 3-component array).
        scale : str, bool, or None, optional
            Controls glyph scaling:
            - None (default): Scale by vector magnitude (uses `name` field)
            - str: Scale by the specified scalar array name
            - False: Uniform glyph size (no scaling)
        glyph_type : {'arrow', 'cone', 'sphere'}, optional
            Type of glyph geometry to use. Default is 'arrow'.
        factor : float, optional
            Global scale multiplier for glyph size. Default is 1.0.
        tolerance : float, optional
            Fraction of bounding box (0-1) for reducing glyph density.
            None means show all glyphs. Default is None.
        color_mode : {'scale', 'scalar', 'vector'}, optional
            How to color the glyphs:
            - 'scale': Color by the scaling array (default)
            - 'scalar': Color by scalar values
            - 'vector': Color by vector magnitude
            Default is 'scale'.
        **kwargs
            Additional keyword arguments passed to add_mesh() for glyph visualization.
            Common options include: cmap, clim, opacity.

        Returns
        -------
        Plotter
            Returns self to enable method chaining.

        Raises
        ------
        ValueError
            If glyph_type is not one of 'arrow', 'cone', or 'sphere'.
        """
        valid_types = {"arrow", "cone", "sphere"}
        if glyph_type not in valid_types:
            raise ValueError(f"glyph_type must be one of {valid_types}, got '{glyph_type}'")

        # Default scale to name (vector magnitude) if not specified
        if scale is None:
            scale = name

        self._vector_props["name"] = name
        self._vector_props["scale"] = scale
        self._vector_props["glyph_type"] = glyph_type
        self._vector_props["factor"] = factor
        self._vector_props["tolerance"] = tolerance
        self._vector_props["color_mode"] = color_mode
        for key, value in kwargs.items():
            self._vector_props[key] = value
        return self

    def _plot_vector_field(self) -> None:
        """
        Plot vector field glyphs based on the stored vector properties.

        Creates oriented glyphs (arrows, cones, or spheres) at each point/cell
        in the mesh, with optional scaling and density control.
        """
        if self._vector_props is None:
            return  # No vector properties set

        name = self._vector_props.get("name")
        scale = self._vector_props.get("scale", name)
        glyph_type = self._vector_props.get("glyph_type", "arrow")
        factor = self._vector_props.get("factor", 1.0)
        tolerance = self._vector_props.get("tolerance")
        color_mode = self._vector_props.get("color_mode", "scale")

        # Create glyph geometry based on type
        if glyph_type == "arrow":
            geom = pv.Arrow()
        elif glyph_type == "cone":
            geom = pv.Cone()
        elif glyph_type == "sphere":
            geom = pv.Sphere()
        else:
            raise ValueError(f"Unknown glyph_type: {glyph_type}")

        vector_kwargs = {
            k: v
            for k, v in self._vector_props.items()
            if k not in ["name", "scale", "glyph_type", "factor", "tolerance", "color_mode"]
        }

        for idx, block, block_name in self._iter_blocks():
            # Validate vector array exists
            if name not in block.array_names:
                continue

            # Validate vector array is 3-component
            vector_array = block[name]
            if vector_array.ndim != 2 or vector_array.shape[1] != 3:
                raise ValueError(
                    f"Vector array '{name}' must be a 3-component array, "
                    f"got shape {vector_array.shape} in block '{block_name or idx}'"
                )

            # Validate scale array exists if specified
            if isinstance(scale, str) and scale != name and scale not in block.array_names:
                raise ValueError(
                    f"Scale array '{scale}' not found in block '{block_name or idx}'. "
                    f"Available arrays: {block.array_names}"
                )

            # Generate glyphs
            try:
                glyphs = block.glyph(
                    orient=name,
                    scale=scale,
                    factor=factor,
                    geom=geom,
                    tolerance=tolerance,
                    absolute=False,
                    color_mode=color_mode,
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to generate glyphs for vector '{name}' in block '{block_name or idx}': {e}"
                ) from e

            if glyphs.n_points == 0:
                continue

            actor_name = f"vector_field_block_{block_name}" if block_name else "vector_field"
            actor = self.plotter.add_mesh(glyphs, name=actor_name, **vector_kwargs)
            # Apply visibility from stored state
            if block_name:
                actor.SetVisibility(self.get_block_visibility(block_name))

    def show(self):
        """
        Display the plotter.

        If a mesh was loaded via set_file() or the filepath parameter, this method:
        1. Plots scalar fields (if set_scalar() was called)
        2. Plots contours (if set_contour() was called)
        3. Plots vector fields (if set_vector() was called)
        4. Extracts and plots feature edges (automatically)
        5. Resets the camera to frame the mesh

        In desktop mode, shows the QMainWindow and starts the Qt event loop (blocking).
        In notebook mode, returns the interactive widget for display in Jupyter.

        Returns
        -------
        None or widget
            In notebook mode, returns the interactive widget. In desktop mode, returns None.
        """
        # Re-initialize if window was closed
        if not self._notebook and self._window is not None and self._window.is_closed:
            self._init_qt_mode()

        if self.reader is not None:
            self._mesh = None  # Reset mesh to ensure fresh load
            self._plot_scalar_field()
            self._plot_contours()
            self._plot_vector_field()
            self._plot_feature_edges()

        if self._notebook:
            # Notebook mode: return the widget for Jupyter display
            return self.plotter.show()
        else:
            # Desktop mode: show window and start Qt event loop
            self._window.show()

    def export(
        self,
        filename: str | Path,
        transparent_background: bool = False,
        window_size: tuple[int, int] = (800, 600),
        scale: float | None = None,
    ) -> "Plotter":
        """
        Export the current plot to an image file.

        This method captures a screenshot of the current visualization and saves it to the
        specified file. If a reader is available, the mesh is reset and plot elements
        (scalar fields, contours, vector fields, and feature edges) are refreshed before
        exporting to ensure a clean render.

        Parameters
        ----------
        filename : str | Path
            The path and filename where the screenshot will be saved. Can be a string or
            pathlib.Path object. Supported formats include '.png', '.jpeg', '.jpg', '.bmp', '.tif', '.tiff'.
        transparent_background : bool, optional
            If True, the background will be transparent in the exported image. Default is False.
        window_size : tuple[int, int], optional
            The width and height of the export window in pixels. Default is (800, 600).
        scale : float | None, optional
            Scaling factor for the image resolution. If None, uses the default scale.
            Default is None.

        Returns
        -------
        Plotter
            Returns the Plotter instance to allow method chaining.
        """
        # Re-initialize if window was closed
        if not self._notebook and self._window is not None and self._window.is_closed:
            self._init_qt_mode()

        if self.reader is not None:
            self._mesh = None  # Reset mesh to ensure fresh load
            self._plot_scalar_field()
            self._plot_contours()
            self._plot_vector_field()
            self._plot_feature_edges()
            self.plotter.reset_camera()

        self.plotter.screenshot(
            filename=str(filename), transparent_background=transparent_background, window_size=window_size, scale=scale
        )
        return self

    def render(self) -> None:
        """
        Re-render the current scene without reopening the plot window.

        When a reader is available, this method resets the mesh and re-plots all
        visualization elements (scalar fields, contours, vector fields, and feature
        edges) before triggering a render on the underlying PyVista/Qt plotter.

        Unlike :meth:`show`, which is responsible for displaying the plot window
        (or notebook view) and starting the interactive session, :meth:`render`
        is intended for refreshing an already-initialized visualization, for
        example after data or settings have changed or prior to exporting.

        This method takes no parameters and returns nothing.
        """
        if self.reader is not None:
            self.plotter.suppress_rendering = True
            self._mesh = None  # Reset mesh to ensure fresh load
            self._plot_scalar_field()
            self._plot_contours()
            self._plot_vector_field()
            self._plot_feature_edges()
            self.plotter.suppress_rendering = False
            self.plotter.render()

    def _on_window_closed(self, _) -> None:
        """
        Close the plotter and clean up resources.

        In desktop mode, closes the QtInteractor plotter (window cleanup handled by QtPlotterWindow).
        In notebook mode, closes the PyVista plotter.
        """
        if hasattr(self, "plotter") and self.plotter is not None:
            self.plotter.close()

    def _find_block_by_name(self, block_name: str | None) -> tuple[int, pv.DataSet, str | None]:
        """
        Locate a block by name in the mesh.

        For MultiBlock meshes, finds the block matching the given name.
        For single meshes, returns the mesh if block_name is None.
        """
        if self.reader is None:
            raise ValueError("No reader available. Call set_file() first.")

        mesh = self.mesh
        if isinstance(mesh, pv.MultiBlock):
            if block_name is None:
                # Default to first non-empty block
                for idx, block in enumerate(mesh):
                    if block is not None and getattr(block, "n_points", 0) > 0:
                        name = mesh.get_block_name(idx) or str(idx)
                        return idx, block, name
                raise ValueError("No valid blocks found in MultiBlock mesh.")
            # Find block by name using MultiBlock API
            if block_name in mesh.keys():
                idx = mesh.get_index_by_name(block_name)
                block = mesh[block_name]
                if block is None:
                    raise ValueError(f"Block '{block_name}' is None.")
                return idx, block, block_name
            raise ValueError(f"Block '{block_name}' not found. Available: {list(mesh.keys())}")
        else:
            if block_name is not None:
                raise ValueError("block_name must be None for single-block meshes.")
            return 0, mesh, None

    def _append_temporal_value(self, data_dict: dict, key: str, time_val: float, value) -> None:
        """
        Append a temporal value to the data dictionary.

        For vectors (3-component), stores as x_value, y_value, z_value.
        For scalars, stores as value.
        """
        is_vector = isinstance(value, list) and len(value) == 3

        if key not in data_dict:
            if is_vector:
                data_dict[key] = {"time": [], "x_value": [], "y_value": [], "z_value": []}
            else:
                data_dict[key] = {"time": [], "value": []}

        data_dict[key]["time"].append(time_val)
        if is_vector:
            data_dict[key]["x_value"].append(value[0])
            data_dict[key]["y_value"].append(value[1])
            data_dict[key]["z_value"].append(value[2])
        else:
            data_dict[key]["value"].append(value)

    def query_point(
        self,
        point_id: int,
        block_name: str | None = None,
        time_value: float | None = None,
    ) -> dict:
        """
        Query point data for a single point.

        For temporal datasets, sweeps all time points unless time_value is specified.
        For static datasets, returns values directly.

        See full documentation at docs/api/Plotter/query_point.md
        """
        _, block, _ = self._find_block_by_name(block_name)

        # Validate point_id
        if point_id < 0 or point_id >= block.n_points:
            raise ValueError(f"point_id {point_id} out of range [0, {block.n_points - 1}].")

        data: dict = {}

        time_reader = self._time_reader()
        if time_reader is not None and time_reader.number_time_points > 0:
            # Temporal dataset: use specific time_value or sweep all time points
            original_time_value = self.active_time_value
            try:
                if time_value is not None:
                    # Query specific time value
                    time_reader.set_active_time_value(time_value)
                    self._mesh = None  # Clear cache to force re-read
                    _, current_block, _ = self._find_block_by_name(block_name)
                    time_val = self.active_time_value

                    for key in current_block.point_data.keys():
                        arr = current_block.point_data[key]
                        value = arr[point_id]
                        if hasattr(value, "tolist"):
                            value = value.tolist()
                        self._append_temporal_value(data, key, time_val, value)
                else:
                    # Sweep all time points
                    for tp in range(time_reader.number_time_points):
                        self.set_active_time_point(tp)
                        self._mesh = None  # Clear cache to force re-read
                        _, current_block, _ = self._find_block_by_name(block_name)
                        time_val = self.active_time_value

                        for key in current_block.point_data.keys():
                            arr = current_block.point_data[key]
                            value = arr[point_id]
                            # Convert numpy types to Python types for scalars
                            if hasattr(value, "tolist"):
                                value = value.tolist()
                            self._append_temporal_value(data, key, time_val, value)
            finally:
                time_reader.set_active_time_value(original_time_value)
                self._mesh = None  # Reset to original state
        else:
            # Static dataset
            for key in block.point_data.keys():
                arr = block.point_data[key]
                value = arr[point_id]
                if hasattr(value, "tolist"):
                    value = value.tolist()
                self._append_temporal_value(data, key, 0, value)

        return data

    def query_points(
        self,
        point_ids: list[int],
        block_names: list[str] | str | None = None,
        time_value: float | None = None,
        progress_callback: callable | None = None,
    ) -> list[dict]:
        """
        Query point data for multiple points.

        For temporal datasets, sweeps all time points unless time_value is specified.
        For static datasets, returns values directly.

        Parameters
        ----------
        progress_callback : callable | None, optional
            Callback function for progress updates. Called with (current, total).
            Should return True to continue or False to cancel.

        See full documentation at docs/api/Plotter/query_points.md
        """
        if block_names is None:
            block_name_list = [None] * len(point_ids)
        elif isinstance(block_names, str):
            block_name_list = [block_names] * len(point_ids)
        elif isinstance(block_names, list):
            if len(point_ids) != len(block_names):
                raise ValueError("point_ids and block_names lists must have the same length.")
            block_name_list = block_names
        else:
            raise ValueError("block_names must be str, list[str], or None.")

        # Validate all point_ids upfront
        for pid, bn in zip(point_ids, block_name_list):
            _, block, _ = self._find_block_by_name(bn)
            if pid < 0 or pid >= block.n_points:
                raise ValueError(f"point_id {pid} out of range [0, {block.n_points - 1}].")

        # Initialize result list
        results: list[dict] = [{} for _ in point_ids]

        time_reader = self._time_reader()
        if time_reader is not None and time_reader.number_time_points > 0:
            # Temporal dataset: use specific time_value or sweep all time points
            original_time_value = self.active_time_value
            try:
                if time_value is not None:
                    # Query specific time value
                    time_reader.set_active_time_value(time_value)
                    self._mesh = None  # Clear cache to force re-read
                    time_val = self.active_time_value

                    total_ops = len(point_ids)
                    current_op = 0

                    for i, (pid, bn) in enumerate(zip(point_ids, block_name_list)):
                        if progress_callback is not None:
                            if not progress_callback(current_op, total_ops):
                                return []  # Cancelled

                        _, current_block, _ = self._find_block_by_name(bn)
                        for key in current_block.point_data.keys():
                            arr = current_block.point_data[key]
                            value = arr[pid]
                            if hasattr(value, "tolist"):
                                value = value.tolist()
                            self._append_temporal_value(results[i], key, time_val, value)

                        current_op += 1

                    if progress_callback is not None:
                        progress_callback(total_ops, total_ops)
                else:
                    # Sweep all time points
                    total_ops = time_reader.number_time_points * len(point_ids)
                    current_op = 0

                    for tp in range(time_reader.number_time_points):
                        self.set_active_time_point(tp)
                        self._mesh = None  # Clear cache to force re-read
                        time_val = self.active_time_value

                        for i, (pid, bn) in enumerate(zip(point_ids, block_name_list)):
                            if progress_callback is not None:
                                if not progress_callback(current_op, total_ops):
                                    return []  # Cancelled

                            _, current_block, _ = self._find_block_by_name(bn)
                            for key in current_block.point_data.keys():
                                arr = current_block.point_data[key]
                                value = arr[pid]
                                if hasattr(value, "tolist"):
                                    value = value.tolist()
                                self._append_temporal_value(results[i], key, time_val, value)

                            current_op += 1

                    if progress_callback is not None:
                        progress_callback(total_ops, total_ops)
            finally:
                time_reader.set_active_time_value(original_time_value)
                self._mesh = None  # Reset to original state
        else:
            # Static dataset
            total_ops = len(point_ids)
            current_op = 0

            for i, (pid, bn) in enumerate(zip(point_ids, block_name_list)):
                if progress_callback is not None:
                    if not progress_callback(current_op, total_ops):
                        return []  # Cancelled

                _, block, _ = self._find_block_by_name(bn)
                for key in block.point_data.keys():
                    arr = block.point_data[key]
                    value = arr[pid]
                    if hasattr(value, "tolist"):
                        value = value.tolist()
                    self._append_temporal_value(results[i], key, 0, value)

                current_op += 1

            if progress_callback is not None:
                progress_callback(total_ops, total_ops)

        return results

    def query_cell(
        self,
        cell_id: int,
        block_name: str | None = None,
        time_value: float | None = None,
    ) -> dict:
        """
        Query cell data for a single cell.

        For temporal datasets, sweeps all time points unless time_value is specified.
        For static datasets, returns values directly.

        See full documentation at docs/api/Plotter/query_cell.md
        """
        _, block, _ = self._find_block_by_name(block_name)

        # Validate cell_id
        if cell_id < 0 or cell_id >= block.n_cells:
            raise ValueError(f"cell_id {cell_id} out of range [0, {block.n_cells - 1}].")

        data: dict = {}

        time_reader = self._time_reader()
        if time_reader is not None and time_reader.number_time_points > 0:
            # Temporal dataset: use specific time_value or sweep all time points
            original_time_value = self.active_time_value
            try:
                if time_value is not None:
                    # Query specific time value
                    time_reader.set_active_time_value(time_value)
                    self._mesh = None  # Clear cache to force re-read
                    _, current_block, _ = self._find_block_by_name(block_name)
                    time_val = self.active_time_value

                    for key in current_block.cell_data.keys():
                        arr = current_block.cell_data[key]
                        value = arr[cell_id]
                        if hasattr(value, "tolist"):
                            value = value.tolist()
                        self._append_temporal_value(data, key, time_val, value)
                else:
                    # Sweep all time points
                    for tp in range(time_reader.number_time_points):
                        self.set_active_time_point(tp)
                        self._mesh = None  # Clear cache to force re-read
                        _, current_block, _ = self._find_block_by_name(block_name)
                        time_val = self.active_time_value

                        for key in current_block.cell_data.keys():
                            arr = current_block.cell_data[key]
                            value = arr[cell_id]
                            # Convert numpy types to Python types for scalars
                            if hasattr(value, "tolist"):
                                value = value.tolist()
                            self._append_temporal_value(data, key, time_val, value)
            finally:
                time_reader.set_active_time_value(original_time_value)
                self._mesh = None  # Reset to original state
        else:
            # Static dataset
            for key in block.cell_data.keys():
                arr = block.cell_data[key]
                value = arr[cell_id]
                if hasattr(value, "tolist"):
                    value = value.tolist()
                self._append_temporal_value(data, key, 0, value)

        return data

    def query_cells(
        self,
        cell_ids: list[int],
        block_names: list[str] | str | None = None,
        time_value: float | None = None,
        progress_callback: callable | None = None,
    ) -> list[dict]:
        """
        Query cell data for multiple cells.

        For temporal datasets, sweeps all time points unless time_value is specified.
        For static datasets, returns values directly.

        Parameters
        ----------
        cell_ids : list[int]
            List of cell IDs to query.
        block_names : list[str] | str | None, optional
            Block names corresponding to each cell. If None, uses default block.
        time_value : float | None, optional
            Specific time value to query. If None, sweeps all time points.
        progress_callback : callable | None, optional
            Callback function for progress updates. Called with (current, total).
            Should return True to continue or False to cancel.

        Returns
        -------
        list[dict]
            List of dictionaries containing query results for each cell.
            Returns empty list if cancelled via progress_callback.

        See full documentation at docs/api/Plotter/query_cells.md
        """
        if block_names is None:
            block_name_list = [None] * len(cell_ids)
        elif isinstance(block_names, str):
            block_name_list = [block_names] * len(cell_ids)
        elif isinstance(block_names, list):
            if len(cell_ids) != len(block_names):
                raise ValueError("cell_ids and block_names lists must have the same length.")
            block_name_list = block_names
        else:
            raise ValueError("block_names must be str, list[str], or None.")

        # Validate all cell_ids upfront
        for cid, bn in zip(cell_ids, block_name_list):
            _, block, _ = self._find_block_by_name(bn)
            if cid < 0 or cid >= block.n_cells:
                raise ValueError(f"cell_id {cid} out of range [0, {block.n_cells - 1}].")

        # Initialize result list
        results: list[dict] = [{} for _ in cell_ids]

        time_reader = self._time_reader()
        if time_reader is not None and time_reader.number_time_points > 0:
            # Temporal dataset: use specific time_value or sweep all time points
            original_time_value = self.active_time_value
            try:
                if time_value is not None:
                    # Query specific time value
                    time_reader.set_active_time_value(time_value)
                    self._mesh = None  # Clear cache to force re-read
                    time_val = self.active_time_value

                    # Calculate total operations for progress tracking
                    total_ops = len(cell_ids)
                    current_op = 0

                    for i, (cid, bn) in enumerate(zip(cell_ids, block_name_list)):
                        # Check for cancellation
                        if progress_callback is not None:
                            if not progress_callback(current_op, total_ops):
                                return []  # Cancelled

                        _, current_block, _ = self._find_block_by_name(bn)
                        for key in current_block.cell_data.keys():
                            arr = current_block.cell_data[key]
                            value = arr[cid]
                            if hasattr(value, "tolist"):
                                value = value.tolist()
                            self._append_temporal_value(results[i], key, time_val, value)

                        current_op += 1

                    # Final progress update
                    if progress_callback is not None:
                        progress_callback(total_ops, total_ops)

                else:
                    # Sweep all time points
                    # Calculate total operations for progress tracking
                    total_ops = time_reader.number_time_points * len(cell_ids)
                    current_op = 0

                    for tp in range(time_reader.number_time_points):
                        self.set_active_time_point(tp)
                        self._mesh = None  # Clear cache to force re-read
                        time_val = self.active_time_value

                        for i, (cid, bn) in enumerate(zip(cell_ids, block_name_list)):
                            # Check for cancellation
                            if progress_callback is not None:
                                if not progress_callback(current_op, total_ops):
                                    return []  # Cancelled

                            _, current_block, _ = self._find_block_by_name(bn)
                            for key in current_block.cell_data.keys():
                                arr = current_block.cell_data[key]
                                value = arr[cid]
                                if hasattr(value, "tolist"):
                                    value = value.tolist()
                                self._append_temporal_value(results[i], key, time_val, value)

                            current_op += 1

                    # Final progress update
                    if progress_callback is not None:
                        progress_callback(total_ops, total_ops)

            finally:
                time_reader.set_active_time_value(original_time_value)
                self._mesh = None  # Reset to original state
        else:
            # Static dataset
            total_ops = len(cell_ids)
            current_op = 0

            for i, (cid, bn) in enumerate(zip(cell_ids, block_name_list)):
                # Check for cancellation
                if progress_callback is not None:
                    if not progress_callback(current_op, total_ops):
                        return []  # Cancelled

                _, block, _ = self._find_block_by_name(bn)
                for key in block.cell_data.keys():
                    arr = block.cell_data[key]
                    value = arr[cid]
                    if hasattr(value, "tolist"):
                        value = value.tolist()
                    self._append_temporal_value(results[i], key, 0, value)

                current_op += 1

            # Final progress update
            if progress_callback is not None:
                progress_callback(total_ops, total_ops)

        return results

    def _sample_probe(
        self,
        probe: pv.PolyData,
        time_value: float | None = None,
        tolerance: float | None = None,
        progress_callback: callable | None = None,
    ) -> tuple[list[dict], pv.PolyData | None]:
        """
        Sample mesh data onto a probe geometry (internal helper).

        This private method handles the core sampling logic for all sample_* methods.
        It supports both temporal and static datasets, sampling from the entire mesh.

        Parameters
        ----------
        probe : pv.PolyData
            The probe geometry (point cloud, line, arc) to sample onto.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.
        progress_callback : callable | None, optional
            Callback function for progress updates during temporal sweeps.
            Called with (current, total). Should return True to continue or False to cancel.
            Default is None.

        Returns
        -------
        tuple[list[dict], pv.PolyData | None]
            A tuple of (results, last_sampled) where:
            - results: list of dicts (one per probe point) with sampled data
            - last_sampled: the last sampled PolyData (for advanced users)
        """
        # Sample from entire mesh
        target = self.mesh

        n_points = probe.n_points
        results: list[dict] = [{} for _ in range(n_points)]

        # Add probe coordinates to each result dict (static, doesn't change over time)
        coords = probe.points  # (N, 3) array
        for i in range(n_points):
            results[i]["coordinates"] = {
                "x": float(coords[i, 0]),
                "y": float(coords[i, 1]),
                "z": float(coords[i, 2]),
            }

        last_sampled: pv.PolyData | None = None

        # Helper to extract arrays from sampled PolyData
        def extract_arrays(sampled: pv.PolyData, time_val: float) -> None:
            for key in sampled.point_data.keys():
                # Skip internal VTK arrays
                if key in ("vtkValidPointMask", "vtkGhostType"):
                    continue
                arr = sampled.point_data[key]
                for pt_idx in range(n_points):
                    value = arr[pt_idx]
                    if hasattr(value, "tolist"):
                        value = value.tolist()
                    self._append_temporal_value(results[pt_idx], key, time_val, value)

        # Temporal or static sampling
        time_reader = self._time_reader()
        if time_reader is not None and time_reader.number_time_points > 0:
            # Temporal dataset
            original_time_value = self.active_time_value
            try:
                if time_value is not None:
                    # Query specific time value
                    time_reader.set_active_time_value(time_value)
                    self._mesh = None  # Clear cache to force re-read
                    target = self.mesh
                    last_sampled = probe.sample(target, tolerance=tolerance)
                    time_val = self.active_time_value
                    extract_arrays(last_sampled, time_val)
                else:
                    # Sweep all time points
                    total = time_reader.number_time_points
                    for tp in range(total):
                        if progress_callback is not None:
                            if not progress_callback(tp, total):
                                return [], None  # Cancelled
                        self.set_active_time_point(tp)
                        self._mesh = None  # Clear cache to force re-read
                        target = self.mesh
                        last_sampled = probe.sample(target, tolerance=tolerance)
                        time_val = self.active_time_value
                        extract_arrays(last_sampled, time_val)

                    if progress_callback is not None:
                        progress_callback(total, total)
            finally:
                time_reader.set_active_time_value(original_time_value)
                self._mesh = None  # Reset to original state
        else:
            # Static dataset
            last_sampled = probe.sample(target, tolerance=tolerance)
            extract_arrays(last_sampled, 0)

        return results, last_sampled

    def _sample_probe_lines_batch(
        self,
        probes: list[pv.PolyData],
        time_value: float | None = None,
        tolerance: float | None = None,
        progress_callback: callable | None = None,
    ) -> list[list[dict]]:
        """
        Sample mesh data onto multiple line/arc probes with time-step-outer loop.

        Instead of sweeping all time steps per probe (N probes × T time steps =
        N×T expensive ``set_active_time_point`` calls), this method iterates time
        steps in the outer loop and samples every probe against the already-loaded
        mesh in the inner loop, reducing the expensive calls to just T.

        Parameters
        ----------
        probes : list[pv.PolyData]
            List of probe geometries (lines, arcs) to sample.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.
        progress_callback : callable | None, optional
            Callback function for progress updates during temporal sweeps.
            Called with (current_time_step, total_time_steps).
            Should return True to continue or False to cancel. Default is None.

        Returns
        -------
        list[list[dict]]
            One ``list[dict]`` per probe.  Each inner list has one dict per time
            step, containing array names mapped to distance / value entries
            (same structure as the former ``_sample_probe_line``).
        """
        n_probes = len(probes)
        if n_probes == 0:
            return []

        # --- Pre-compute per-probe static geometry data ---
        probe_meta: list[dict] = []
        for probe in probes:
            points = probe.points
            n_points = len(points)

            # Cumulative arc-length distances
            distances = np.zeros(n_points)
            for i in range(1, n_points):
                distances[i] = distances[i - 1] + np.linalg.norm(points[i] - points[i - 1])
            distance_list = distances.tolist()

            # Coordinates
            x_coords = points[:, 0].tolist()
            y_coords = points[:, 1].tolist()
            z_coords = points[:, 2].tolist()

            # Tangent vectors for tangential / normal decomposition
            tangents = np.zeros_like(points)
            for i in range(n_points):
                if i == 0:
                    tangents[i] = points[1] - points[0]
                elif i == n_points - 1:
                    tangents[i] = points[-1] - points[-2]
                else:
                    tangents[i] = points[i + 1] - points[i - 1]
                norm = np.linalg.norm(tangents[i])
                if norm > 1e-10:
                    tangents[i] /= norm

            probe_meta.append(
                {
                    "n_points": n_points,
                    "distance_list": distance_list,
                    "x_coords": x_coords,
                    "y_coords": y_coords,
                    "z_coords": z_coords,
                    "tangents": tangents,
                }
            )

        # --- Per-probe result accumulators ---
        all_results: list[list[dict]] = [[] for _ in range(n_probes)]

        # --- Helper: extract arrays from one sampled PolyData for one time step ---
        def _extract(sampled: pv.PolyData, time_val: float, meta: dict) -> dict:
            n_pts = meta["n_points"]
            dist = meta["distance_list"]
            xc = meta["x_coords"]
            yc = meta["y_coords"]
            zc = meta["z_coords"]
            tng = meta["tangents"]

            time_data: dict = {"time": time_val}
            for key in sampled.point_data.keys():
                if key in ("vtkValidPointMask", "vtkGhostType"):
                    continue
                arr = sampled.point_data[key]
                is_vector = arr.ndim > 1 and arr.shape[1] == 3

                if is_vector:
                    tangential = np.zeros(n_pts)
                    normal = np.zeros(n_pts)
                    for i in range(n_pts):
                        tangential[i] = np.dot(arr[i], tng[i])
                        tangential_vec = tangential[i] * tng[i]
                        normal_vec = arr[i] - tangential_vec
                        normal[i] = np.linalg.norm(normal_vec)
                    time_data[key] = {
                        "distance": dist.copy(),
                        "x_value": arr[:, 0].tolist(),
                        "y_value": arr[:, 1].tolist(),
                        "z_value": arr[:, 2].tolist(),
                        "tangential": tangential.tolist(),
                        "normal": normal.tolist(),
                        "x": xc.copy(),
                        "y": yc.copy(),
                        "z": zc.copy(),
                    }
                else:
                    time_data[key] = {
                        "distance": dist.copy(),
                        "value": arr.tolist() if hasattr(arr, "tolist") else list(arr),
                        "x": xc.copy(),
                        "y": yc.copy(),
                        "z": zc.copy(),
                    }
            return time_data

        def _sample_all_probes(target, time_val: float) -> None:
            """Sample every probe against *target* and append results."""
            for p_idx in range(n_probes):
                sampled = probes[p_idx].sample(target, tolerance=tolerance)
                all_results[p_idx].append(_extract(sampled, time_val, probe_meta[p_idx]))

        # --- Time-aware or static sampling ---
        time_reader = self._time_reader()
        if time_reader is not None and time_reader.number_time_points > 0:
            original_time_value = self.active_time_value
            try:
                if time_value is not None:
                    # Single requested time value
                    time_reader.set_active_time_value(time_value)
                    self._mesh = None
                    target = self.mesh
                    _sample_all_probes(target, self.active_time_value)
                else:
                    # Sweep all time points — outer loop is time, inner is probes
                    total = time_reader.number_time_points
                    for tp in range(total):
                        if progress_callback is not None:
                            if not progress_callback(tp, total):
                                return [[] for _ in range(n_probes)]  # Cancelled
                        self.set_active_time_point(tp)
                        self._mesh = None
                        target = self.mesh
                        _sample_all_probes(target, self.active_time_value)

                    if progress_callback is not None:
                        progress_callback(total, total)
            finally:
                time_reader.set_active_time_value(original_time_value)
                self._mesh = None
        else:
            # Static dataset — load mesh once, sample all probes
            target = self.mesh
            _sample_all_probes(target, 0.0)

        return all_results

    def sample_point(
        self,
        point: Sequence[float],
        time_value: float | None = None,
        tolerance: float | None = None,
    ) -> dict:
        """
        Sample mesh data at a single point coordinate.

        This method creates a probe at the specified 3D coordinate and samples
        the mesh data onto it. For temporal datasets, sweeps all time points
        unless time_value is specified.

        Parameters
        ----------
        point : Sequence[float]
            3D coordinate [x, y, z] to sample at.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.

        Returns
        -------
        dict
            Dictionary with array names as keys. Each value is a dict with
            "time" and "value" keys (for scalars) or "time", "x_value",
            "y_value", "z_value" keys (for vectors). Also includes a
            "coordinates" key with the probe position.

        Raises
        ------
        ValueError
            If point does not have exactly 3 components.

        Examples
        --------
        >>> from pyemsi import Plotter
        >>> p = Plotter("mesh.vtu")
        >>> data = p.sample_point([1.0, 2.0, 3.0])
        >>> print(data["Temperature"]["value"][0])

        See full documentation at docs/api/Plotter/sample_point.md
        """
        if len(point) != 3:
            raise ValueError(f"point must have 3 components, got {len(point)}.")

        probe = pv.PolyData(np.array([point]))
        results, _ = self._sample_probe(probe, time_value, tolerance)
        return results[0]

    def sample_points(
        self,
        points: Sequence[Sequence[float]],
        time_value: float | None = None,
        tolerance: float | None = None,
        progress_callback: callable | None = None,
    ) -> list[dict]:
        """
        Sample mesh data at multiple point coordinates (point cloud).

        This method creates a point cloud probe from the specified coordinates
        and samples the mesh data onto each point. For temporal datasets, sweeps
        all time points unless time_value is specified.

        Parameters
        ----------
        points : Sequence[Sequence[float]]
            List of 3D coordinates [[x, y, z], ...] to sample at.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.
        progress_callback : callable | None, optional
            Callback function for progress updates during temporal sweeps.
            Called with (current, total). Should return True to continue or
            False to cancel. Default is None.

        Returns
        -------
        list[dict]
            List of dictionaries (one per point) with array names as keys.
            Each value is a dict with "time" and "value" keys (for scalars)
            or "time", "x_value", "y_value", "z_value" keys (for vectors).
            Each point dict also includes a "coordinates" key.

        Raises
        ------
        ValueError
            If any point does not have exactly 3 components.

        Examples
        --------
        >>> from pyemsi import Plotter
        >>> p = Plotter("mesh.vtu")
        >>> points = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        >>> data = p.sample_points(points)
        >>> print(data[0]["Temperature"]["value"][0])

        See full documentation at docs/api/Plotter/sample_points.md
        """
        # Validate all points have 3 components
        for i, point in enumerate(points):
            if len(point) != 3:
                raise ValueError(f"points[{i}] must have 3 components, got {len(point)}.")

        probe = pv.PolyData(np.array(points))
        results, _ = self._sample_probe(probe, time_value, tolerance, progress_callback)
        return results

    def sample_line(
        self,
        pointa: Sequence[float],
        pointb: Sequence[float],
        resolution: int = 100,
        time_value: float | None = None,
        tolerance: float | None = None,
    ) -> list[dict]:
        """
        Sample mesh data along a straight line.

        Creates a line probe from pointa to pointb with the specified resolution
        and samples the mesh data onto each point along the line. For temporal
        datasets, sweeps all time points unless time_value is specified.

        Parameters
        ----------
        pointa : Sequence[float]
            Starting point [x, y, z] of the line.
        pointb : Sequence[float]
            Ending point [x, y, z] of the line.
        resolution : int, optional
            Number of segments to divide the line into. The resulting line will
            have resolution + 1 points. Default is 100.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.

        Returns
        -------
        list[dict]
            List of dictionaries (one per time step) with array names as keys.
            Each array has "distance" (distance along line) and "value" keys
            (for scalars) or "distance", "x_value", "y_value", "z_value" keys
            (for vectors). For static datasets, returns a single-element list.

        Raises
        ------
        ValueError
            If resolution < 1.

        Examples
        --------
        >>> from pyemsi import Plotter
        >>> p = Plotter("mesh.vtu")
        >>> data = p.sample_line([0, 0, 0], [1, 1, 1], resolution=50)
        >>> # Plot temperature along line (static dataset)
        >>> temps = data[0]["Temperature"]["value"]
        >>> distances = data[0]["Temperature"]["distance"]

        See full documentation at docs/api/Plotter/sample_line.md
        """
        if resolution < 1:
            raise ValueError(f"resolution must be >= 1, got {resolution}.")

        probe = pv.Line(pointa, pointb, resolution=resolution)
        return self._sample_probe_lines_batch([probe], time_value, tolerance)[0]

    def sample_lines(
        self,
        lines: Sequence[tuple[Sequence[float], Sequence[float]]],
        resolution: int | list[int] = 100,
        time_value: float | None = None,
        tolerance: float | None = None,
        progress_callback: callable | None = None,
    ) -> list[list[dict]]:
        """
        Sample mesh data along multiple straight lines.

        Creates line probes for each (pointa, pointb) pair and samples the mesh
        data onto each line. For temporal datasets, sweeps all time points unless
        time_value is specified.

        Parameters
        ----------
        lines : Sequence[tuple[Sequence[float], Sequence[float]]]
            List of line definitions, each as a tuple (pointa, pointb) where
            pointa and pointb are [x, y, z] coordinates.
        resolution : int or list[int], optional
            Number of segments to divide each line into. Can be a single int
            (applied to all lines) or a list of ints (one per line). Default is 100.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.
        progress_callback : callable | None, optional
            Callback function for progress updates. Called with (current_line, total_lines).
            Should return True to continue or False to cancel. Default is None.

        Returns
        -------
        list[list[dict]]
            List of results (one per line), where each result is a list of
            dictionaries (one per time step) with array names as keys.
            Each array has "distance" and "value" keys (for scalars) or
            "distance", "x_value", "y_value", "z_value" keys (for vectors).

        Raises
        ------
        ValueError
            If resolution is a list and its length doesn't match the number of lines,
            or if any resolution < 1.

        Examples
        --------
        >>> from pyemsi import Plotter
        >>> p = Plotter("mesh.vtu")
        >>> lines = [([0, 0, 0], [1, 0, 0]), ([0, 0, 0], [0, 1, 0])]
        >>> data = p.sample_lines(lines, resolution=50)
        >>> # data[0] is results for first line, data[1] for second line
        >>> # For static dataset: data[0][0] is the single time step
        >>> temps_line0 = data[0][0]["Temperature"]["value"]
        >>> distances_line0 = data[0][0]["Temperature"]["distance"]

        See full documentation at docs/api/Plotter/sample_lines.md
        """
        # Normalize resolution to list
        if isinstance(resolution, int):
            resolution_list = [resolution] * len(lines)
        elif isinstance(resolution, list):
            if len(resolution) != len(lines):
                raise ValueError(
                    f"resolution list length ({len(resolution)}) must match number of lines ({len(lines)})."
                )
            resolution_list = resolution
        else:
            raise ValueError("resolution must be int or list[int].")

        # Validate all resolutions
        for i, res in enumerate(resolution_list):
            if res < 1:
                raise ValueError(f"resolution[{i}] must be >= 1, got {res}.")

        # Build all probes up-front
        probes = [pv.Line(pa, pb, resolution=res) for (pa, pb), res in zip(lines, resolution_list)]

        # Sample all probes in a single time-step sweep
        return self._sample_probe_lines_batch(probes, time_value, tolerance, progress_callback)

    def sample_arc(
        self,
        pointa: Sequence[float],
        pointb: Sequence[float],
        center: Sequence[float],
        resolution: int = 100,
        negative: bool = False,
        time_value: float | None = None,
        tolerance: float | None = None,
    ) -> list[dict]:
        """
        Sample mesh data along a circular arc.

        Creates a circular arc probe from pointa to pointb around center with
        the specified resolution and samples the mesh data onto each point along
        the arc. For temporal datasets, sweeps all time points unless time_value
        is specified.

        Parameters
        ----------
        pointa : Sequence[float]
            Starting point [x, y, z] of the arc.
        pointb : Sequence[float]
            Ending point [x, y, z] of the arc.
        center : Sequence[float]
            Center point [x, y, z] of the circle containing the arc.
        resolution : int, optional
            Number of segments to divide the arc into. The resulting arc will
            have resolution + 1 points. Default is 100.
        negative : bool, optional
            If False (default), the arc spans the positive angle from pointa to
            pointb around center. If True, spans the negative (reflex) angle.
            Default is False.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.

        Returns
        -------
        list[dict]
            List of dictionaries (one per time step) with array names as keys.
            Each array has "distance" (distance along arc) and "value" keys
            (for scalars) or "distance", "x_value", "y_value", "z_value" keys
            (for vectors). For static datasets, returns a single-element list.

        Raises
        ------
        ValueError
            If resolution < 1.

        Examples
        --------
        >>> from pyemsi import Plotter
        >>> p = Plotter("mesh.vtu")
        >>> data = p.sample_arc([1, 0, 0], [0, 1, 0], [0, 0, 0], resolution=50)
        >>> # Plot magnetic field along arc (static dataset)
        >>> b_mag = data[0]["B-Mag (T)"]["value"]
        >>> distances = data[0]["B-Mag (T)"]["distance"]

        See full documentation at docs/api/Plotter/sample_arc.md
        """
        if resolution < 1:
            raise ValueError(f"resolution must be >= 1, got {resolution}.")

        probe = pv.CircularArc(pointa=pointa, pointb=pointb, center=center, resolution=resolution, negative=negative)
        return self._sample_probe_lines_batch([probe], time_value, tolerance)[0]

    def sample_arcs(
        self,
        arcs: Sequence[tuple[Sequence[float], Sequence[float], Sequence[float]]],
        resolution: int | list[int] = 100,
        negative: bool = False,
        time_value: float | None = None,
        tolerance: float | None = None,
        progress_callback: callable | None = None,
    ) -> list[list[dict]]:
        """
        Sample mesh data along multiple circular arcs.

        Creates circular arc probes for each (pointa, pointb, center) tuple and
        samples the mesh data onto each arc. For temporal datasets, sweeps all
        time points unless time_value is specified.

        Parameters
        ----------
        arcs : Sequence[tuple[Sequence[float], Sequence[float], Sequence[float]]]
            List of arc definitions, each as a tuple (pointa, pointb, center)
            where each component is an [x, y, z] coordinate.
        resolution : int or list[int], optional
            Number of segments to divide each arc into. Can be a single int
            (applied to all arcs) or a list of ints (one per arc). Default is 100.
        negative : bool, optional
            If False (default), arcs span the positive angle. If True, span
            the negative (reflex) angle. Applied to all arcs. Default is False.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.
        progress_callback : callable | None, optional
            Callback function for progress updates. Called with (current_arc, total_arcs).
            Should return True to continue or False to cancel. Default is None.

        Returns
        -------
        list[list[dict]]
            List of results (one per arc), where each result is a list of
            dictionaries (one per time step) with array names as keys.
            Each array has "distance" and "value" keys (for scalars) or
            "distance", "x_value", "y_value", "z_value" keys (for vectors).

        Raises
        ------
        ValueError
            If resolution is a list and its length doesn't match the number of arcs,
            or if any resolution < 1.

        Examples
        --------
        >>> from pyemsi import Plotter
        >>> p = Plotter("mesh.vtu")
        >>> arcs = [([1, 0, 0], [0, 1, 0], [0, 0, 0]),
        ...         ([0, 0, 1], [1, 0, 1], [0, 0, 1])]
        >>> data = p.sample_arcs(arcs, resolution=50)
        >>> # data[0] is results for first arc, data[1] for second arc
        >>> # For static dataset: data[0][0] is the single time step
        >>> b_mag_arc0 = data[0][0]["B-Mag (T)"]["value"]
        >>> distances_arc0 = data[0][0]["B-Mag (T)"]["distance"]

        See full documentation at docs/api/Plotter/sample_arcs.md
        """
        # Normalize resolution to list
        if isinstance(resolution, int):
            resolution_list = [resolution] * len(arcs)
        elif isinstance(resolution, list):
            if len(resolution) != len(arcs):
                raise ValueError(f"resolution list length ({len(resolution)}) must match number of arcs ({len(arcs)}).")
            resolution_list = resolution
        else:
            raise ValueError("resolution must be int or list[int].")

        # Validate all resolutions
        for i, res in enumerate(resolution_list):
            if res < 1:
                raise ValueError(f"resolution[{i}] must be >= 1, got {res}.")

        # Build all probes up-front
        probes = [
            pv.CircularArc(pointa=pa, pointb=pb, center=ctr, resolution=res, negative=negative)
            for (pa, pb, ctr), res in zip(arcs, resolution_list)
        ]

        # Sample all probes in a single time-step sweep
        return self._sample_probe_lines_batch(probes, time_value, tolerance, progress_callback)

    def sample_arc_from_normal(
        self,
        center: Sequence[float],
        resolution: int = 100,
        normal: Sequence[float] | None = None,
        polar: Sequence[float] | None = None,
        angle: float | None = None,
        time_value: float | None = None,
        tolerance: float | None = None,
    ) -> list[dict]:
        """
        Sample mesh data along a circular arc defined by a normal vector.

        Creates a circular arc probe defined by a normal to the plane of the arc,
        a polar starting vector, and an angle. The arc is sampled in a
        counterclockwise direction from the polar vector. For temporal datasets,
        sweeps all time points unless time_value is specified.

        Parameters
        ----------
        center : Sequence[float]
            Center point [x, y, z] of the circle that defines the arc.
        resolution : int, optional
            Number of segments to divide the arc into. The resulting arc will
            have resolution + 1 points. Default is 100.
        normal : Sequence[float] | None, optional
            Normal vector [x, y, z] to the plane of the arc. If None, defaults
            to [0, 0, 1] (positive Z direction). Default is None.
        polar : Sequence[float] | None, optional
            Starting point of the arc in polar coordinates [x, y, z]. If None,
            defaults to [1, 0, 0] (positive X direction). Default is None.
        angle : float | None, optional
            Arc length in degrees, beginning at the polar vector in a
            counterclockwise direction. If None, defaults to 90 degrees.
            Default is None.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.

        Returns
        -------
        list[dict]
            List of dictionaries (one per time step) with array names as keys.
            Each array has "distance" (distance along arc), "value" (for scalars),
            or "x_value", "y_value", "z_value" (for vectors), plus "tangential",
            "normal", and "x", "y", "z" (sample point coordinates).
            For static datasets, returns a single-element list.

        Raises
        ------
        ValueError
            If resolution < 1.

        Examples
        --------
        >>> from pyemsi import Plotter
        >>> p = Plotter("mesh.vtu")
        >>> # Quarter arc in XY plane starting from negative X axis
        >>> data = p.sample_arc_from_normal(
        ...     center=[0, 0, 0],
        ...     normal=[0, 0, 1],
        ...     polar=[-1, 0, 0],
        ...     angle=90,
        ...     resolution=50
        ... )
        >>> b_mag = data[0]["B-Mag (T)"]["value"]
        >>> distances = data[0]["B-Mag (T)"]["distance"]

        See full documentation at docs/api/Plotter/sample_arc_from_normal.md
        """
        if resolution < 1:
            raise ValueError(f"resolution must be >= 1, got {resolution}.")

        probe = pv.CircularArcFromNormal(center=center, resolution=resolution, normal=normal, polar=polar, angle=angle)
        return self._sample_probe_lines_batch([probe], time_value, tolerance)[0]

    def sample_arcs_from_normal(
        self,
        arcs: Sequence[tuple[Sequence[float], Sequence[float] | None, Sequence[float] | None, float | None]],
        resolution: int | list[int] = 100,
        time_value: float | None = None,
        tolerance: float | None = None,
        progress_callback: callable | None = None,
    ) -> list[list[dict]]:
        """
        Sample mesh data along multiple circular arcs defined by normal vectors.

        Creates circular arc probes for each (center, normal, polar, angle) tuple
        and samples the mesh data onto each arc. For temporal datasets, sweeps all
        time points unless time_value is specified.

        Parameters
        ----------
        arcs : Sequence[tuple[Sequence[float], Sequence[float] | None, Sequence[float] | None, float | None]]
            List of arc definitions, each as a tuple (center, normal, polar, angle)
            where center is [x, y, z], normal is [x, y, z] or None (defaults to [0, 0, 1]),
            polar is [x, y, z] or None (defaults to [1, 0, 0]), and angle is a float
            in degrees or None (defaults to 90).
        resolution : int or list[int], optional
            Number of segments to divide each arc into. Can be a single int
            (applied to all arcs) or a list of ints (one per arc). Default is 100.
        time_value : float | None, optional
            Query a specific time value instead of sweeping all time points.
            Ignored for static datasets. Default is None.
        tolerance : float | None, optional
            Tolerance for the sample operation. If None, PyVista generates
            a tolerance automatically. Default is None.
        progress_callback : callable | None, optional
            Callback function for progress updates. Called with (current_arc, total_arcs).
            Should return True to continue or False to cancel. Default is None.

        Returns
        -------
        list[list[dict]]
            List of results (one per arc), where each result is a list of
            dictionaries (one per time step) with array names as keys.

        Raises
        ------
        ValueError
            If resolution is a list and its length doesn't match the number of arcs,
            or if any resolution < 1.

        Examples
        --------
        >>> from pyemsi import Plotter
        >>> p = Plotter("mesh.vtu")
        >>> arcs = [
        ...     ([0, 0, 0], [0, 0, 1], [-1, 0, 0], 90),  # Quarter arc in XY
        ...     ([0, 0, 0], [1, 0, 0], [0, 1, 0], 180),  # Half arc in YZ
        ... ]
        >>> data = p.sample_arcs_from_normal(arcs, resolution=50)

        See full documentation at docs/api/Plotter/sample_arcs_from_normal.md
        """
        # Normalize resolution to list
        if isinstance(resolution, int):
            resolution_list = [resolution] * len(arcs)
        elif isinstance(resolution, list):
            if len(resolution) != len(arcs):
                raise ValueError(f"resolution list length ({len(resolution)}) must match number of arcs ({len(arcs)}).")
            resolution_list = resolution
        else:
            raise ValueError("resolution must be int or list[int].")

        # Validate all resolutions
        for i, res in enumerate(resolution_list):
            if res < 1:
                raise ValueError(f"resolution[{i}] must be >= 1, got {res}.")

        # Build all probes up-front
        probes = [
            pv.CircularArcFromNormal(center=ctr, resolution=res, normal=nrm, polar=pol, angle=ang)
            for (ctr, nrm, pol, ang), res in zip(arcs, resolution_list)
        ]

        # Sample all probes in a single time-step sweep
        return self._sample_probe_lines_batch(probes, time_value, tolerance, progress_callback)
