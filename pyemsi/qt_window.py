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
import pyvista as pv
import pyemsi.resources.resources  # noqa: F401
from .display_settings_dialog import DisplaySettingsDialog


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
    _camera_toolbar: "QToolBar"
    _display_toolbar: "QToolBar"
    plotter: "QtInteractor | pv.Plotter"
    parent_plotter: "Plotter | None"
    _display_settings_dialog: "DisplaySettingsDialog | None"

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

        # Initialize display settings dialog reference
        self._display_settings_dialog = None

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

        # Create toolbars
        self._create_camera_toolbar()

        # Attach close event handler
        self._window.closeEvent = lambda event: self._on_close(event)

    def _create_camera_toolbar(self) -> None:
        """
        Create and configure the camera view control toolbar.

        Adds a movable toolbar with buttons for reset camera, isometric view,
        and six orthogonal axis views (±X, ±Y, ±Z) using icons from Qt resources.
        """
        self._camera_toolbar = QToolBar("Camera Controls")
        self._camera_toolbar.setMovable(True)
        self._camera_toolbar.setIconSize(QSize(24, 24))

        # Reset Camera action
        reset_action = QAction(QIcon(":/icons/ResetCamera.svg"), "Reset Camera", self._window)
        reset_action.setToolTip("Reset camera to frame all objects")
        reset_action.triggered.connect(self.plotter.reset_camera)
        self._camera_toolbar.addAction(reset_action)

        self._camera_toolbar.addSeparator()

        # Isometric view action
        iso_action = QAction(QIcon(":/icons/IsometricView.svg"), "Isometric", self._window)
        iso_action.setToolTip("Isometric view")
        iso_action.triggered.connect(self.plotter.view_isometric)
        self._camera_toolbar.addAction(iso_action)

        self._camera_toolbar.addSeparator()

        # +X view (Right)
        xplus_action = QAction(QIcon(":/icons/XPlus.svg"), "+X View", self._window)
        xplus_action.setToolTip("View from +X axis (Right)")
        xplus_action.triggered.connect(lambda: self.plotter.view_xy())
        self._camera_toolbar.addAction(xplus_action)

        # -X view (Left)
        xminus_action = QAction(QIcon(":/icons/XMinus.svg"), "-X View", self._window)
        xminus_action.setToolTip("View from -X axis (Left)")
        xminus_action.triggered.connect(lambda: self.plotter.view_yx(negative=True))
        self._camera_toolbar.addAction(xminus_action)

        # +Y view (Front)
        yplus_action = QAction(QIcon(":/icons/YPlus.svg"), "+Y View", self._window)
        yplus_action.setToolTip("View from +Y axis (Front)")
        yplus_action.triggered.connect(lambda: self.plotter.view_xz())
        self._camera_toolbar.addAction(yplus_action)

        # -Y view (Back)
        yminus_action = QAction(QIcon(":/icons/YMinus.svg"), "-Y View", self._window)
        yminus_action.setToolTip("View from -Y axis (Back)")
        yminus_action.triggered.connect(lambda: self.plotter.view_xz(negative=True))
        self._camera_toolbar.addAction(yminus_action)

        # +Z view (Top)
        zplus_action = QAction(QIcon(":/icons/ZPlus.svg"), "+Z View", self._window)
        zplus_action.setToolTip("View from +Z axis (Top)")
        zplus_action.triggered.connect(lambda: self.plotter.view_yz())
        self._camera_toolbar.addAction(zplus_action)

        # -Z view (Bottom)
        zminus_action = QAction(QIcon(":/icons/ZMinus.svg"), "-Z View", self._window)
        zminus_action.setToolTip("View from -Z axis (Bottom)")
        zminus_action.triggered.connect(lambda: self.plotter.view_yz(negative=True))
        self._camera_toolbar.addAction(zminus_action)

        # Add toolbar to main window
        self._window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._camera_toolbar)

    def _create_display_toolbar(self) -> None:
        """
        Create and configure the display control toolbar.

        Adds a movable toolbar with checkable toggle buttons for axes, bounding box,
        grid display, and a settings button for future configuration dialog.
        """
        self._display_toolbar = QToolBar("Display Controls")
        self._display_toolbar.setMovable(True)
        self._display_toolbar.setIconSize(QSize(24, 24))

        # Axes toggle action
        self._axes_action = QAction("Axes", self._window)
        self._axes_action.setToolTip("Toggle axes orientation widget")
        self._axes_action.setCheckable(True)
        self._axes_action.setChecked(self.plotter.renderer.axes_enabled)
        self._axes_action.triggered.connect(self._toggle_axes)
        self._display_toolbar.addAction(self._axes_action)

        # Axes at origin action
        self._axes_at_origin_action = QAction("Axes at Origin", self._window)
        self._axes_at_origin_action.setToolTip("Add axes orientation widget at origin")
        self._axes_at_origin_action.setCheckable(True)
        self._axes_at_origin_action.setChecked(
            any(x.__class__.__name__ == "vtkAxesActor" for x in self.plotter.renderer.actors.values())
        )
        self._axes_at_origin_action.triggered.connect(self._toggle_axes_at_origin)
        self._display_toolbar.addAction(self._axes_at_origin_action)

        # Grid toggle action
        self._grid_action = QAction("Grid", self._window)
        self._grid_action.setToolTip("Toggle grid and labeled axes")
        self._grid_action.setCheckable(True)
        self._grid_action.setChecked(
            any(x.__class__.__name__ == "CubeAxesActor" for x in self.plotter.renderer.actors.values())
        )
        self._grid_action.triggered.connect(self._toggle_grid)
        self._display_toolbar.addAction(self._grid_action)

        # Camera orientation widget toggle action
        self._camera_orientation_action = QAction("Camera Orientation", self._window)
        self._camera_orientation_action.setToolTip("Toggle camera orientation widget")
        self._camera_orientation_action.setCheckable(True)
        self._camera_orientation_action.setChecked(
            any(x.__class__.__name__ == "vtkCameraOrientationWidget" for x in self.plotter.camera_widgets)
        )
        self._camera_orientation_action.triggered.connect(self._toggle_camera_orientation)
        self._display_toolbar.addAction(self._camera_orientation_action)

        self._display_toolbar.addSeparator()

        # Settings action
        settings_action = QAction(QIcon(":/icons/Settings.svg"), "Settings", self._window)
        settings_action.setToolTip("Open display settings")
        settings_action.triggered.connect(self._open_display_settings)
        self._display_toolbar.addAction(settings_action)

        # Add toolbar to main window
        self._window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._display_toolbar)

    def _toggle_axes(self, input: bool) -> None:
        """Toggle axes orientation widget visibility."""
        if input:
            self.plotter.show_axes()
        else:
            self.plotter.hide_axes()

    def _toggle_axes_at_origin(self, input: bool) -> None:
        """Toggle axes orientation widget at origin."""
        if input:
            self.plotter.add_axes_at_origin()
        else:
            for actor in list(self.plotter.renderer.actors.values()):
                if actor.__class__.__name__ == "vtkAxesActor":
                    self.plotter.remove_actor(actor)

    def _toggle_grid(self, input: bool) -> None:
        """Toggle grid and labeled axes display."""
        if input:
            self.plotter.show_grid()
        else:
            self.plotter.remove_bounds_axes()

    def _toggle_camera_orientation(self, input: bool) -> None:
        """Toggle camera orientation widget visibility."""
        if input:
            self.plotter.add_camera_orientation_widget()
        else:
            for widget in self.plotter.camera_widgets:
                if widget.__class__.__name__ == "vtkCameraOrientationWidget":
                    widget.Off()
                    self.plotter.camera_widgets.remove(widget)

    def _open_display_settings(self) -> None:
        """Open display settings dialog (non-blocking)."""
        # Create dialog if it doesn't exist or was closed
        if self._display_settings_dialog is None:
            self._display_settings_dialog = DisplaySettingsDialog(plotter=self.plotter, plotter_window=self)

        # Show and raise dialog (non-blocking)
        self._display_settings_dialog.show()
        self._display_settings_dialog.raise_()
        self._display_settings_dialog.activateWindow()

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
        self._create_display_toolbar()
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
