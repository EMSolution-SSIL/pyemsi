"""
Qt-based visualization plotter for pyemsi.

Provides a custom Plotter class that composes PyVista plotting functionality
with Qt interactivity using pyvistaqt.QtInteractor and PySide6 backend.
"""

from typing import TYPE_CHECKING
from pathlib import Path
import pyvista as pv

# TYPE_CHECKING imports (for type checkers only, not runtime)
if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout
    from pyvistaqt import QtInteractor

# Qt imports are optional (only needed for desktop mode)
try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout
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
    >>> # Create plotter and add a sphere
    >>> p = Plotter()
    >>> p.add_mesh(pv.Sphere(), show_edges=True)
    >>> p.show()
    >>>
    >>> # Customize window properties
    >>> p = Plotter(title="My Visualization", window_size=(1200, 900))
    >>> p.add_mesh(pv.Cube(), color='red')
    >>> p.show()

    Notebook mode:

    >>> import pyvista as pv
    >>> from pyemsi import Plotter
    >>>
    >>> # Use in Jupyter notebook with Trame backend
    >>> p = Plotter(notebook=True)
    >>> p.add_mesh(pv.Sphere(), show_edges=True)
    >>> p.show()  # Returns interactive widget
    >>>
    >>> # Load mesh from file (automatically displays feature edges)
    >>> p = Plotter(notebook=True, backend='client')
    >>> p.set_file("path/to/file.vtp").show()
    """

    # Type annotations for instance attributes
    notebook: bool
    backend: str | None
    mesh: pv.DataSet | pv.MultiBlock | None
    reader: pv.BaseReader | None
    plotter: "QtInteractor | pv.Plotter"
    app: "QApplication | None"
    _window: "QMainWindow"
    frame: "QFrame"
    vlayout: "QVBoxLayout"

    def __init__(
        self,
        title: str = "pyemsi Plotter",
        window_size: tuple[int, int] = (1024, 768),
        position: tuple[int, int] | None = None,
        notebook: bool = False,
        backend: str | None = "client",
        **kwargs,
    ):
        """Initialize the plotter in desktop or notebook mode."""
        self.notebook = notebook
        self.backend = backend
        self.mesh = None
        self.reader = None

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
        >>> # Method chaining with additional customization
        >>> p = Plotter(notebook=True)
        >>> p.set_file("model.vtp").add_axes().show()
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Mesh file not found: {filepath}")

        try:
            self.reader = pv.get_reader(str(filepath))
        except Exception as e:
            raise ValueError(f"Failed to read mesh file '{filepath}': {e}") from e

        return self

    def _plot_feature_edges(self) -> None:
        """
        Extract and plot feature edges from the stored mesh.

        For MultiBlock datasets, creates separate actors for each block's feature edges.
        For single datasets, creates a single feature edges actor.
        Automatically resets the camera to frame the mesh after plotting.
        """
        if self.mesh is None:
            return

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
                        edges, name=f"feature_edges_block_{self.mesh.get_block_name(i)}", color="black"
                    )
        else:
            # Handle single dataset
            edges = self.mesh.extract_feature_edges()
            if edges.n_points > 0:
                self.plotter.add_mesh(edges, name="feature_edges", color="black")

        # Reset camera to frame the mesh
        self.plotter.reset_camera()

    def show(self):
        """
        Display the plotter.

        In desktop mode, shows the QMainWindow and starts the Qt event loop (blocking).
        In notebook mode, returns the interactive widget for display in Jupyter.

        Returns
        -------
        None or widget
            In notebook mode, returns the interactive widget. In desktop mode, returns None.
        """
        if isinstance(self.reader, pv.PVDReader):
            self.mesh = self.reader.read()[0]
        else:
            self.mesh = self.reader.read()
        self._plot_feature_edges()
        if self.notebook:
            # Notebook mode: return the widget for Jupyter display
            return self.plotter.show()
        else:
            # Desktop mode: show window and start Qt event loop
            self._window.show()
            self.app.exec()

    def close(self) -> None:
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

    def __getattr__(self, name: str):
        """
        Delegate attribute access to the internal QtInteractor plotter.

        This allows seamless access to all PyVista plotting methods
        (e.g., add_mesh, remove_actor, reset_camera, clear, etc.)
        directly on the Plotter instance.

        Parameters
        ----------
        name : str
            The attribute name to access.

        Returns
        -------
        Any
            The attribute from the QtInteractor instance.

        Raises
        ------
        AttributeError
            If the attribute is not found in either the Plotter or QtInteractor.
        """
        # Avoid infinite recursion for plotter attribute itself
        if name == "plotter":
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        # Delegate to the QtInteractor
        try:
            return getattr(self.plotter, name)
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
