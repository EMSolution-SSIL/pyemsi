"""
Qt-based visualization plotter for pyemsi.

Provides a custom Plotter class that composes PyVista plotting functionality
with Qt interactivity using pyvistaqt.QtInteractor and PySide6 backend.
"""

from typing import Optional, Tuple
import pyvista as pv

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
    mesh : pv.DataSet, optional
        PyVista mesh to visualize. Accepts single datasets (UnstructuredGrid, PolyData, etc.)
        or MultiBlock datasets. If provided, feature edges are automatically extracted and
        displayed, and the camera is reset to frame the mesh. Default is None.
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
        The primary mesh provided during initialization, if any.
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
    >>> # Initialize with a mesh (automatically displays feature edges)
    >>> mesh = pv.read("path/to/file.vtp")
    >>> p = Plotter(mesh=mesh, notebook=True, backend='client')
    >>> p.show()
    """

    def __init__(
        self,
        mesh: Optional[pv.DataSet] = None,
        title: str = "pyemsi Plotter",
        window_size: Tuple[int, int] = (1024, 768),
        position: Optional[Tuple[int, int]] = None,
        notebook: bool = False,
        backend: Optional[str] = "client",
        **kwargs,
    ):
        """Initialize the plotter in desktop or notebook mode."""
        self.notebook = notebook
        self.backend = backend

        # Initialize based on mode
        if self.notebook:
            self._init_notebook_mode(**kwargs)
        else:
            self._init_qt_mode(title, window_size, position, **kwargs)

        # Store and plot mesh if provided
        self.mesh = mesh
        if self.mesh is not None:
            self._plot_feature_edges()

    def _init_qt_mode(
        self,
        title: str,
        window_size: Tuple[int, int],
        position: Optional[Tuple[int, int]],
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
