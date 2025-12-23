"""
Qt-based visualization plotter for pyemsi.

Provides a custom Plotter class that composes PyVista plotting functionality
with Qt interactivity using pyvistaqt.QtInteractor and PySide6 backend.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pyvista as pv
import numpy as np

# TYPE_CHECKING imports (for type checkers only, not runtime)
if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QVBoxLayout
    from pyvistaqt import QtInteractor

# Qt imports are optional (only needed for desktop mode)
try:
    from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QVBoxLayout
    from pyvistaqt import QtInteractor

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

    Examples
    --------
    Desktop mode:

    >>> import pyvista as pv
    >>> from pyemsi import Plotter
    >>>
    >>> # Create plotter and add a sphere directly
    >>> p = Plotter()
    >>> p.plotter.add_mesh(pv.Sphere())
    >>> p.show()
    >>>
    >>> # Load and visualize a mesh file with scalar field
    >>> p = Plotter("mesh.vtm")
    >>> p.set_scalar("Temperature", mode="element").show()
    >>>
    >>> # Method chaining for complex visualizations
    >>> Plotter("model.pvd").set_scalar("Flux (A/m)", mode="node").show()

    Notebook mode:

    >>> import pyvista as pv
    >>> from pyemsi import Plotter
    >>>
    >>> # Use in Jupyter notebook
    >>> p = Plotter("data.vtu", notebook=True)
    >>> p.set_scalar("B-Mag (T)", mode="element", cell2point=True).show()
    >>>
    >>> # Access time-series data
    >>> p = Plotter("transient.pvd", notebook=True)
    >>> p.reader.set_active_time_point(-1)  # Last time step
    >>> p.plotter.view_xy()
    >>> p.set_scalar("Voltage").show()
    """

    # Type annotations for instance attributes
    notebook: bool
    backend: str | None
    _mesh: pv.DataSet | pv.MultiBlock | None
    reader: pv.BaseReader | None
    plotter: "QtInteractor | pv.Plotter"
    app: "QApplication | None"
    _window: "QMainWindow"
    frame: "QFrame"
    vlayout: "QVBoxLayout"
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
        self.notebook = notebook
        self.backend = backend
        self._mesh = None
        self.reader = None
        self._feature_edges_props = {"color": "white", "line_width": 1, "opacity": 1.0}
        self._scalar_props = {
            "name": None,
            "mode": "element",
            "cell2point": True,
            "show_edges": True,
            "edge_color": "white",
            "edge_opacity": 0.25,
        }
        self._vector_props = {}
        self._contour_props = {"name": None, "n_contours": 10, "color": "red", "line_width": 3}
        if filepath is not None:
            self.set_file(filepath)
        # Initialize based on mode
        if self.notebook:
            self._init_notebook_mode(**kwargs)
        else:
            self._init_qt_mode(title, window_size, position, **kwargs)

    def _init_qt_mode(
        self,
        title: str,
        window_size: tuple[int, int],
        position: tuple[int, int] | None,
        **kwargs,
    ) -> None:
        """Initialize Qt-based desktop mode."""
        if not HAS_QT:
            raise ImportError("Qt dependencies not available. Install with: pip install PySide6 pyvistaqt")

        # Get or create QApplication instance
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        # Create QMainWindow
        self._window = QMainWindow()
        self._window.closeEvent = lambda event: self._on_window_closed(event)

        # Set window properties
        self._window.setWindowTitle(title)
        self._window.resize(*window_size)
        if position is not None:
            self._window.move(*position)

        # Create container frame and layout
        self.frame = QFrame()
        self.vlayout = QVBoxLayout()
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        # Create QtInteractor (the rendering widget that IS the plotter)
        self.plotter = QtInteractor(parent=self.frame, off_screen=False, **kwargs)

        # Add QtInteractor to layout
        self.vlayout.addWidget(self.plotter)
        self.frame.setLayout(self.vlayout)
        self._window.setCentralWidget(self.frame)

    def _init_notebook_mode(self, **kwargs) -> None:
        """Initialize PyVista native notebook mode."""
        pv.set_jupyter_backend(self.backend)
        self.plotter = pv.Plotter(**kwargs)
        self.app = None

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

        Examples
        --------
        >>> p = Plotter()
        >>> p.set_file("mesh.vtm").show()
        >>>
        >>> # Method chaining with scalar field
        >>> p = Plotter()
        >>> p.set_file("model.vtu").set_scalar("Flux (A/m)", mode="node").show()
        >>>
        >>> # Preferred: Use filepath in constructor
        >>> Plotter("model.vtu").set_scalar("Temperature").show()
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Mesh file not found: {filepath}")

        try:
            self.reader = pv.get_reader(str(filepath))
        except Exception as e:
            raise ValueError(f"Failed to read mesh file '{filepath}': {e}") from e

        return self

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

    def set_feature_edges(self, color: str = "black", line_width: int = 1, opacity: float = 1.0, **kwargs) -> "Plotter":
        """
        Set properties for feature edges visualization.

        Feature edges are extracted and displayed when show() is called on a loaded mesh.
        This method stores the visualization properties for later use.

        Parameters
        ----------
        color : str, optional
            Color of the feature edges. Default is "black".
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
        # Handle MultiBlock datasets
        if isinstance(self.mesh, pv.MultiBlock):
            for i, block in enumerate(self.mesh):
                # Skip empty or None blocks silently
                if block is None or block.n_points == 0:
                    continue

                # Extract and plot feature edges for this block
                edges = block.extract_feature_edges()
                if edges.n_points > 0:
                    self.plotter.add_mesh(
                        edges, name=f"feature_edges_block_{self.mesh.get_block_name(i)}", **self._feature_edges_props
                    )
        else:
            # Handle single dataset
            edges = self.mesh.extract_feature_edges()
            if edges.n_points > 0:
                self.plotter.add_mesh(edges, name="feature_edges", **self._feature_edges_props)

    def set_scalar(
        self, name: str, mode: Literal["node", "element"] = "element", cell2point: bool = True, **kwargs
    ) -> "Plotter":
        """
        Set properties for scalar field visualization.

        The scalar field is displayed when show() is called on a loaded mesh.
        This method stores the visualization properties for later use.

        Parameters
        ----------
        name : str
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

        Examples
        --------
        >>> p = Plotter("mesh.vtm")
        >>> p.set_scalar("Temperature", mode="element", cell2point=True).show()
        >>>
        >>> # Customize edge display
        >>> p.set_scalar("Pressure", show_edges=True, edge_color="black").show()
        """
        self._scalar_props["name"] = name
        self._scalar_props["mode"] = mode
        self._scalar_props["cell2point"] = cell2point
        for key, value in kwargs.items():
            self._scalar_props[key] = value
        return self

    def _plot_scalar_field(self) -> None:
        """
        Plot the scalar field on the mesh based on the stored scalar properties.
        """
        if self._scalar_props.get("name") is None:
            return  # No scalar properties set
        name = self._scalar_props.get("name")
        mode = self._scalar_props.get("mode", "element")
        cell2point = self._scalar_props.get("cell2point", True)

        # Handle MultiBlock datasets
        if isinstance(self.mesh, pv.MultiBlock):
            for i, block in enumerate(self.mesh):
                if block is None or block.n_points == 0:
                    continue
                if mode == "element" and cell2point:
                    block = block.cell_data_to_point_data()
                if name in block.array_names:
                    self.plotter.add_mesh(
                        block,
                        scalars=name,
                        preference="cell" if mode == "element" else "point",
                        name=f"scalar_field_block_{self.mesh.get_block_name(i)}",
                        **{k: v for k, v in self._scalar_props.items() if k not in ["name", "mode", "cell2point"]},
                    )
        else:
            # Handle single dataset
            block = self.mesh
            if mode == "element" and cell2point:
                block = block.cell_data_to_point_data()
            if name in block.array_names:
                self.plotter.add_mesh(
                    block,
                    scalars=name,
                    preference="cell" if mode == "element" else "point",
                    name="scalar_field",
                    **{k: v for k, v in self._scalar_props.items() if k not in ["name", "mode", "cell2point"]},
                )

    def set_contour(
        self,
        name: str,
        n_contours: int = 10,
        color: str = "red",
        line_width: int = 3,
        **kwargs,
    ) -> "Plotter":
        """
        Set properties for contour visualization.

        Parameters
        ----------
        name : str
            Name of the scalar field to contour.
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
        if self._contour_props.get("name") is None:
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

        if isinstance(self.mesh, pv.MultiBlock):
            iter_blocks = [
                (i, block, self.mesh.get_block_name(i)) for i, block in enumerate(self.mesh) if block is not None
            ]
        else:
            iter_blocks = [(0, self.mesh, None)]

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

    def show(self):
        """
        Display the plotter.

        If a mesh was loaded via set_file() or the filepath parameter, this method:
        1. Plots scalar fields (if set_scalar() was called)
        2. Extracts and plots feature edges (automatically)
        3. Resets the camera to frame the mesh

        In desktop mode, shows the QMainWindow and starts the Qt event loop (blocking).
        In notebook mode, returns the interactive widget for display in Jupyter.

        Returns
        -------
        None or widget
            In notebook mode, returns the interactive widget. In desktop mode, returns None.

        Examples
        --------
        >>> # Simple visualization
        >>> Plotter("mesh.vtm").show()
        >>>
        >>> # With scalar field
        >>> Plotter("data.vtu").set_scalar("Temperature").show()
        """
        if self.reader is not None:
            self._mesh = None  # Reset mesh to ensure fresh load
            self._plot_scalar_field()
            self._plot_contours()
            self._plot_feature_edges()
            self.plotter.reset_camera()

        if self.notebook:
            # Notebook mode: return the widget for Jupyter display
            return self.plotter.show()
        else:
            # Desktop mode: show window and start Qt event loop
            self._window.show()
            self.app.exec()

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
        specified file. If a reader is available, the mesh is reset and plot elements are
        refreshed before exporting to ensure a clean render.
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
        Examples
        --------
        >>> plotter.export('output.png')
        >>> plotter.export('output.png', transparent_background=True, window_size=(1920, 1080))
        >>> plotter.export('output.png', scale=2.0)
        """

        if self.reader is not None:
            self._mesh = None  # Reset mesh to ensure fresh load
            self._plot_scalar_field()
            self._plot_contours()
            self._plot_feature_edges()
            self.plotter.reset_camera()

        self.plotter.screenshot(
            filename=str(filename), transparent_background=transparent_background, window_size=window_size, scale=scale
        )
        return self

    def _on_window_closed(self, _) -> None:
        """
        Close the plotter and clean up resources.

        In desktop mode, closes both the QtInteractor and QMainWindow.
        In notebook mode, closes the PyVista plotter.
        """
        if self.notebook:
            # Notebook mode: close PyVista plotter
            if hasattr(self, "plotter") and self.plotter is not None:
                self.plotter.close()
        else:
            # Desktop mode: close QtInteractor and QMainWindow
            if hasattr(self, "plotter") and self.plotter is not None:
                self.plotter.close()
            if hasattr(self, "_window") and self._window is not None:
                self._window.close()
