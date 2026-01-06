"""
Qt-based visualization plotter for pyemsi.

Provides a custom Plotter class that composes PyVista plotting functionality
with Qt interactivity using pyvistaqt.QtInteractor and PySide6 backend.
"""

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

    def __init__(
        self,
        filepath: str | Path | None = None,
        title: str = "pyemsi Plotter",
        window_size: tuple[int, int] = (1024, 768),
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
        window_size : tuple of int, optional
            Window size as (width, height) in pixels (desktop mode only). Default is (1024, 768).
        position : tuple of int, optional
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
            window_size=self._qt_props.get("window_size", (1024, 768)),
            position=self._qt_props.get("position"),
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
        """
        for idx, block, block_name in self._iter_blocks():
            edges = block.extract_feature_edges()
            if edges.n_points == 0:
                continue
            actor_name = f"feature_edges_block_{block_name}" if block_name else "feature_edges"
            self.plotter.add_mesh(edges, name=actor_name, **self._feature_edges_props)

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
            self.plotter.add_mesh(
                block_to_plot,
                scalars=name,
                preference="cell" if mode == "element" else "point",
                name=actor_name,
                **{k: v for k, v in self._scalar_props.items() if k not in ["name", "mode", "cell2point"]},
            )

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
            self.plotter.add_mesh(contours, name=actor_name, color=color, line_width=line_width, **contour_kwargs)

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
            self.plotter.add_mesh(glyphs, name=actor_name, **vector_kwargs)

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
            self.plotter.reset_camera()

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

    def _on_window_closed(self, _) -> None:
        """
        Close the plotter and clean up resources.

        In desktop mode, closes the QtInteractor plotter (window cleanup handled by QtPlotterWindow).
        In notebook mode, closes the PyVista plotter.
        """
        if hasattr(self, "plotter") and self.plotter is not None:
            self.plotter.close()
