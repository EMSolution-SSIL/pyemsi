"""
Qt window management for PyVista visualization.

Provides QtPlotterWindow class that encapsulates Qt application and window
management for interactive 3D visualization using pyvistaqt.QtInteractor.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QVBoxLayout
    from pyvistaqt import QtInteractor
    from pyemsi.plotter import Plotter

from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QVBoxLayout, QToolBar
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize, Qt
from pyvistaqt import QtInteractor
import pyemsi.resources.resources  # noqa: F401


class QtPlotterWindow:
    """
    Qt window container for PyVista visualization.

    Manages QApplication, QMainWindow, and QtInteractor lifecycle with minimal
    coupling to visualization logic. Designed for reusability and clean separation
    of concerns.

    Parameters
    ----------
    title : str, optional
        Window title. Default is "PyVista Plotter".
    window_size : tuple of int, optional
        Window size as (width, height) in pixels. Default is (1024, 768).
    position : tuple of int, optional
        Window position as (x, y) in screen coordinates. If None, uses OS default.
    parent_plotter : Plotter or None, optional
        Reference to the parent Plotter instance that owns this window. Default is None.
    **qt_interactor_kwargs
        Additional keyword arguments passed directly to QtInteractor constructor.

    Attributes
    ----------
    app : QApplication
        The Qt application instance (singleton).
    plotter : QtInteractor
        The QtInteractor instance that provides PyVista plotting functionality.
    parent_plotter : Plotter or None
        Reference to the parent Plotter instance, if provided.
    """

    # Type annotations for instance attributes
    app: "QApplication"
    _window: "QMainWindow"
    _frame: "QFrame"
    _vlayout: "QVBoxLayout"
    _toolbar: "QToolBar"
    plotter: "QtInteractor"
    parent_plotter: "Plotter | None"

    def __init__(
        self,
        title: str = "PyVista Plotter",
        window_size: tuple[int, int] = (1024, 768),
        position: tuple[int, int] | None = None,
        parent_plotter: "Plotter | None" = None,
        **qt_interactor_kwargs,
    ):
        """
        Initialize Qt window with QtInteractor plotter.

        Parameters
        ----------
        title : str, optional
            Window title. Default is "PyVista Plotter".
        window_size : tuple of int, optional
            Window size as (width, height) in pixels. Default is (1024, 768).
        position : tuple of int, optional
            Window position as (x, y) in screen coordinates. If None, uses OS default.
        parent_plotter : Plotter or None, optional
            Reference to the parent Plotter instance. Default is None.
        **qt_interactor_kwargs
            Additional keyword arguments passed to QtInteractor (e.g., off_screen).
        """
        # Store reference to parent plotter
        self.parent_plotter = parent_plotter

        # Get or create QApplication instance (singleton pattern)
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        # Create QMainWindow
        self._window = QMainWindow()
        self._window.setWindowTitle(title)
        self._window.resize(*window_size)
        if position is not None:
            self._window.move(*position)

        # Create container frame and layout
        self._frame = QFrame()
        self._vlayout = QVBoxLayout()
        self._vlayout.setContentsMargins(0, 0, 0, 0)  # Full-window rendering

        # Create QtInteractor (the rendering widget that IS the plotter)
        self.plotter = QtInteractor(parent=self._frame, off_screen=False, **qt_interactor_kwargs)

        # Build window hierarchy: window -> frame -> layout -> plotter
        self._vlayout.addWidget(self.plotter)
        self._frame.setLayout(self._vlayout)
        self._window.setCentralWidget(self._frame)

        # Create camera view toolbar
        self._create_camera_toolbar()

        # Attach close event handler
        self._window.closeEvent = lambda event: self._on_close(event)

    def _create_camera_toolbar(self) -> None:
        """
        Create and configure the camera view control toolbar.

        Adds a movable toolbar with buttons for reset camera, isometric view,
        and six orthogonal axis views (±X, ±Y, ±Z) using icons from Qt resources.
        """
        self._toolbar = QToolBar("Camera Controls")
        self._toolbar.setMovable(True)
        self._toolbar.setIconSize(QSize(24, 24))

        # Reset Camera action
        reset_action = QAction(QIcon(":/icons/ResetCamera.svg"), "Reset Camera", self._window)
        reset_action.setToolTip("Reset camera to frame all objects")
        reset_action.triggered.connect(self.plotter.reset_camera)
        self._toolbar.addAction(reset_action)

        self._toolbar.addSeparator()

        # Isometric view action
        iso_action = QAction(QIcon(":/icons/IsometricView.svg"), "Isometric", self._window)
        iso_action.setToolTip("Isometric view")
        iso_action.triggered.connect(self.plotter.view_isometric)
        self._toolbar.addAction(iso_action)

        self._toolbar.addSeparator()

        # +X view (Right)
        xplus_action = QAction(QIcon(":/icons/XPlus.svg"), "+X View", self._window)
        xplus_action.setToolTip("View from +X axis (Right)")
        xplus_action.triggered.connect(lambda: self.plotter.view_xy())
        self._toolbar.addAction(xplus_action)

        # -X view (Left)
        xminus_action = QAction(QIcon(":/icons/XMinus.svg"), "-X View", self._window)
        xminus_action.setToolTip("View from -X axis (Left)")
        xminus_action.triggered.connect(lambda: self.plotter.view_yx(negative=True))
        self._toolbar.addAction(xminus_action)

        # +Y view (Front)
        yplus_action = QAction(QIcon(":/icons/YPlus.svg"), "+Y View", self._window)
        yplus_action.setToolTip("View from +Y axis (Front)")
        yplus_action.triggered.connect(lambda: self.plotter.view_xz())
        self._toolbar.addAction(yplus_action)

        # -Y view (Back)
        yminus_action = QAction(QIcon(":/icons/YMinus.svg"), "-Y View", self._window)
        yminus_action.setToolTip("View from -Y axis (Back)")
        yminus_action.triggered.connect(lambda: self.plotter.view_xz(negative=True))
        self._toolbar.addAction(yminus_action)

        # +Z view (Top)
        zplus_action = QAction(QIcon(":/icons/ZPlus.svg"), "+Z View", self._window)
        zplus_action.setToolTip("View from +Z axis (Top)")
        zplus_action.triggered.connect(lambda: self.plotter.view_yz())
        self._toolbar.addAction(zplus_action)

        # -Z view (Bottom)
        zminus_action = QAction(QIcon(":/icons/ZMinus.svg"), "-Z View", self._window)
        zminus_action.setToolTip("View from -Z axis (Bottom)")
        zminus_action.triggered.connect(lambda: self.plotter.view_yz(negative=True))
        self._toolbar.addAction(zminus_action)

        # Add toolbar to main window
        self._window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._toolbar)

    @property
    def is_closed(self) -> bool:
        """
        Check if the plotter/window has been closed.

        Returns
        -------
        bool
            True if the plotter is closed, False otherwise.
        """
        return getattr(self.plotter, "_closed", False)

    def show(self) -> None:
        """
        Display the window and start the Qt event loop.

        This method is blocking - it will not return until the window is closed
        and the Qt event loop exits.
        """
        self._window.show()
        self.app.exec()

    def close(self) -> None:
        """
        Close the plotter and window, releasing resources.

        This method closes both the QtInteractor plotter and the QMainWindow.
        """
        if hasattr(self, "plotter") and self.plotter is not None:
            self.plotter.close()
        if hasattr(self, "_window") and self._window is not None:
            self._window.close()

    def _on_close(self, event) -> None:
        """
        Internal handler for window close events.

        Parameters
        ----------
        event : QCloseEvent
            The close event from Qt.
        """
        self.close()
