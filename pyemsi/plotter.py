"""
Qt-based visualization plotter for pyemsi.

Provides a custom Plotter class that composes PyVista plotting functionality
with Qt interactivity using pyvistaqt.QtInteractor and PySide6 backend.
"""

from typing import Optional, Tuple
import pyvista as pv
from PySide6.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout
from pyvistaqt import QtInteractor


class Plotter(QMainWindow):
    """
    Custom Qt-based plotter for interactive 3D visualization.

    This class inherits from QMainWindow and contains a QtInteractor widget
    that provides PyVista plotting functionality with Qt rendering.

    Parameters
    ----------
    title : str, optional
        Window title. Default is "pyemsi Plotter".
    window_size : tuple of int, optional
        Window size as (width, height) in pixels. Default is (1024, 768).
    position : tuple of int, optional
        Window position as (x, y) in screen coordinates. If None, uses OS default.
    mesh : pv.DataSet, optional
        PyVista mesh to visualize. Accepts single datasets (UnstructuredGrid, PolyData, etc.)
        or MultiBlock datasets. If provided, feature edges are automatically extracted and
        displayed, and the camera is reset to frame the mesh. Default is None.
    **kwargs
        Additional keyword arguments passed to QtInteractor.

    Attributes
    ----------
    plotter : QtInteractor
        The internal QtInteractor instance that handles PyVista plotting and Qt rendering.
    app : QApplication
        The Qt application instance.
    mesh : pv.DataSet or None
        The primary mesh provided during initialization, if any.

    Examples
    --------
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
    >>>
    >>> # Initialize with a mesh (automatically displays feature edges)
    >>> mesh = pv.read("path/to/file.vtk")
    >>> p = Plotter(mesh=mesh)
    >>> p.show()
    """

    def __init__(
        self,
        mesh: Optional[pv.DataSet] = None,
        title: str = "pyemsi Plotter",
        window_size: Tuple[int, int] = (1024, 768),
        position: Optional[Tuple[int, int]] = None,
        **kwargs,
    ):
        """Initialize the Qt-based plotter."""
        # Get or create QApplication instance
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        # Initialize QMainWindow
        super().__init__()

        # Set window properties
        self.setWindowTitle(title)
        self.resize(*window_size)
        if position is not None:
            self.move(*position)

        # Create container frame and layout
        self.frame = QFrame()
        self.vlayout = QVBoxLayout()
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        # Create QtInteractor (the rendering widget that IS the plotter)
        self.plotter = QtInteractor(parent=self.frame, off_screen=False, **kwargs)

        # Add QtInteractor to layout
        self.vlayout.addWidget(self.plotter)
        self.frame.setLayout(self.vlayout)
        self.setCentralWidget(self.frame)

        # Store and plot mesh if provided
        self.mesh = mesh
        if self.mesh is not None:
            self._plot_feature_edges()

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

    def show(self) -> None:
        """
        Display the plotter window and start the Qt event loop.

        This method shows the QMainWindow and starts the Qt application event loop,
        which will block until the window is closed.
        """
        # Show the QMainWindow
        super().show()

        # Start the Qt event loop
        self.app.exec()

    def close(self) -> None:
        """
        Close the plotter window and clean up resources.

        This method properly closes the QtInteractor, releases VTK resources,
        and closes the QMainWindow.
        """
        # Close the QtInteractor and clean up VTK resources
        if hasattr(self, "plotter") and self.plotter is not None:
            self.plotter.close()

        # Close the QMainWindow
        super().close()

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
