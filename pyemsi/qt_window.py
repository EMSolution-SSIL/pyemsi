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

from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QVBoxLayout, QToolBar, QComboBox
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize, Qt, QTimer
from pyvistaqt import QtInteractor
import pyvista as pv
import pyemsi.resources.resources  # noqa: F401
from .display_settings_dialog import DisplaySettingsDialog
from .block_visibility_dialog import BlockVisibilityDialog


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
    _block_visibility_dialog: "BlockVisibilityDialog | None"

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
        self._block_visibility_dialog = None

        # Animation state variables
        self._is_playing = False
        self._animation_direction = 1  # 1 for forward, -1 for reverse
        self._animation_timer = None

        # Get or create QApplication instance (singleton pattern)
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])

        # Initialize animation timer (will be configured after window creation)
        self._animation_timer = QTimer()

        # Create QMainWindow
        self._window = QMainWindow()
        self._window.setWindowIcon(QIcon(":/icons/Icon.svg"))
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
        self._create_animation_toolbar()

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

        # +Z view (Right)
        zplus_action = QAction(QIcon(":/icons/ZPlus.svg"), "+Z View", self._window)
        zplus_action.setToolTip("View from +Z axis (Right)")
        zplus_action.triggered.connect(lambda: self.plotter.view_xy())
        self._camera_toolbar.addAction(zplus_action)

        # -Z view (Left)
        zminus_action = QAction(QIcon(":/icons/ZMinus.svg"), "-Z View", self._window)
        zminus_action.setToolTip("View from -Z axis (Left)")
        zminus_action.triggered.connect(lambda: self.plotter.view_yx(negative=True))
        self._camera_toolbar.addAction(zminus_action)

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

        # +X view (Top)
        xplus_action = QAction(QIcon(":/icons/XPlus.svg"), "+X View", self._window)
        xplus_action.setToolTip("View from +X axis (Top)")
        xplus_action.triggered.connect(lambda: self.plotter.view_yz())
        self._camera_toolbar.addAction(xplus_action)

        # -X view (Bottom)
        xminus_action = QAction(QIcon(":/icons/XMinus.svg"), "-X View", self._window)
        xminus_action.setToolTip("View from -X axis (Bottom)")
        xminus_action.triggered.connect(lambda: self.plotter.view_yz(negative=True))
        self._camera_toolbar.addAction(xminus_action)

        # Add toolbar to main window
        self._window.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self._camera_toolbar)

    def _create_animation_toolbar(self) -> None:
        """
        Create and configure the animation control toolbar.

        Adds a movable toolbar with buttons for play, pause, stop, and step
        through animation frames.
        """
        self._animation_toolbar = QToolBar("Animation Controls")
        self._animation_toolbar.setMovable(True)
        self._animation_toolbar.setIconSize(QSize(24, 24))

        # First action
        first_action = QAction(QIcon(":/icons/First.svg"), "First Frame", self._window)
        first_action.setToolTip("Go to first frame of animation")
        first_action.triggered.connect(lambda: self.set_time_point(0))
        self._animation_toolbar.addAction(first_action)

        # Back action
        back_action = QAction(QIcon(":/icons/Back.svg"), "Back Animation", self._window)
        back_action.setToolTip("Back animation")
        back_action.triggered.connect(lambda: self.set_time_point(-1, relative=True))
        self._animation_toolbar.addAction(back_action)

        # Reverse action
        reverse_action = QAction(QIcon(":/icons/Reverse.svg"), "Reverse Animation", self._window)
        reverse_action.setToolTip("Reverse animation")
        reverse_action.triggered.connect(self.reverse)
        self._animation_toolbar.addAction(reverse_action)

        # Pause action
        pause_action = QAction(QIcon(":/icons/Pause.svg"), "Pause Animation", self._window)
        pause_action.setToolTip("Pause animation")
        pause_action.triggered.connect(self.pause)
        self._animation_toolbar.addAction(pause_action)

        # Play action
        play_action = QAction(QIcon(":/icons/Play.svg"), "Play Animation", self._window)
        play_action.setToolTip("Play animation")
        play_action.triggered.connect(self.play)
        self._animation_toolbar.addAction(play_action)

        # Forward action
        forward_action = QAction(QIcon(":/icons/Forward.svg"), "Forward Animation", self._window)
        forward_action.setToolTip("Forward animation")
        forward_action.triggered.connect(lambda: self.set_time_point(1, relative=True))
        self._animation_toolbar.addAction(forward_action)

        # Last action
        last_action = QAction(QIcon(":/icons/Last.svg"), "Last Frame", self._window)
        last_action.setToolTip("Go to last frame of animation")
        last_action.triggered.connect(lambda: self.set_time_point(-1))
        self._animation_toolbar.addAction(last_action)

        # Loop action
        self.loop_action = QAction(QIcon(":/icons/Loop.svg"), "Loop Animation", self._window)
        self.loop_action.setToolTip("Toggle animation looping")
        self.loop_action.setCheckable(True)
        self._animation_toolbar.addAction(self.loop_action)

        # Add separator
        self._animation_toolbar.addSeparator()

        # Time value combobox
        self._time_combobox = QComboBox(self._window)
        self._time_combobox.setToolTip("Select time value")
        self._time_combobox.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._animation_toolbar.addWidget(self._time_combobox)

        # Populate time combobox if parent plotter has time values
        if self.parent_plotter and self.parent_plotter.time_values:
            for i, time_val in enumerate(self.parent_plotter.time_values):
                self._time_combobox.addItem(f"{i:<4}: {time_val:.5g}")
            # Set current selection to active time value
            if self.parent_plotter.active_time_point is not None:
                self._time_combobox.setCurrentIndex(self.parent_plotter.active_time_point)
        self._time_combobox.currentIndexChanged.connect(self._on_time_combobox_changed)

        # Add toolbar to main window
        self._window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._animation_toolbar)

        # Configure animation timer
        self._animation_timer.timeout.connect(self._animation_step)
        self._animation_timer.setInterval(100)  # 100ms default interval

    def set_time_point(self, time_point: int, relative: bool = False) -> None:
        """
        Set the active time point for animation.

        Parameters
        ----------
        time_point : int
            The time point index to set. If `relative` is True, this is an offset
            from the current time point.
        relative : bool, optional
            If True, `time_point` is treated as an offset from the current time point.
        """
        if self.parent_plotter is None:
            return

        if relative:
            current_time_point = self.parent_plotter.active_time_point or 0
            new_time_point = current_time_point + time_point
        else:
            new_time_point = time_point

        self.parent_plotter.set_active_time_point(new_time_point)
        self.parent_plotter.render()
        self._update_time_combobox()

    def _create_display_toolbar(self) -> None:
        """
        Create and configure the display control toolbar.

        Adds a movable toolbar with checkable toggle buttons for axes, bounding box,
        grid display, and a settings button for future configuration dialog.
        """
        self._display_toolbar = QToolBar("Display Controls")
        self._display_toolbar.setMovable(True)
        self._display_toolbar.setIconSize(QSize(24, 24))

        # Settings action
        settings_action = QAction(QIcon(":/icons/Settings.svg"), "Settings", self._window)
        settings_action.setToolTip("Open display settings")
        settings_action.triggered.connect(self._open_display_settings)
        self._display_toolbar.addAction(settings_action)

        self._display_toolbar.addSeparator()

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

        # Block visibility action
        # TODO: Replace text with QIcon(":/icons/Blocks.svg") when icon is available
        self._block_visibility_action = QAction("Blocks", self._window)
        self._block_visibility_action.setToolTip("Control individual block visibility")
        self._block_visibility_action.triggered.connect(self._open_block_visibility_dialog)
        # Enable only if parent plotter has multi-block mesh
        is_multiblock = (
            self.parent_plotter is not None
            and self.parent_plotter.mesh is not None
            and isinstance(self.parent_plotter.mesh, pv.MultiBlock)
        )
        self._block_visibility_action.setEnabled(is_multiblock)
        self._display_toolbar.addAction(self._block_visibility_action)

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
        actor = self.get_actor_by_name("AxesAtOriginActor")
        if input and actor is None:
            actor = self.plotter.add_axes_at_origin()
            actor.SetObjectName("AxesAtOriginActor")
        elif not input and actor is not None:
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

    def _open_block_visibility_dialog(self) -> None:
        """Open block visibility dialog (non-blocking)."""
        # Only open if parent plotter has multi-block mesh
        if self.parent_plotter is None or not isinstance(self.parent_plotter.mesh, pv.MultiBlock):
            return

        # Create dialog if it doesn't exist or was closed
        if self._block_visibility_dialog is None:
            self._block_visibility_dialog = BlockVisibilityDialog(plotter=self.plotter, plotter_window=self)

        # Show and raise dialog (non-blocking)
        self._block_visibility_dialog.show()
        self._block_visibility_dialog.raise_()
        self._block_visibility_dialog.activateWindow()

    def get_actor_by_name(self, name: str) -> pv.Actor | None:
        """
        Retrieve an actor by its assigned name.

        Parameters
        ----------
        name : str
            The name of the actor to retrieve.

        Returns
        -------
        pv.Actor or None
            The actor with the specified name, or None if not found.
        """
        for actor in self.plotter.renderer.actors.values():
            if actor.GetObjectName() == name:
                return actor
        return None

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

    def play(self) -> None:
        """
        Start playing animation in forward direction.
        """
        if self.parent_plotter is None:
            return
        if self.parent_plotter.number_time_points is None or self.parent_plotter.number_time_points <= 1:
            return

        self._animation_direction = 1
        self._is_playing = True
        self._animation_timer.start()

    def pause(self) -> None:
        """
        Pause the animation.
        """
        self._is_playing = False
        self._animation_timer.stop()

    def reverse(self) -> None:
        """
        Start playing animation in reverse direction.
        """
        if self.parent_plotter is None:
            return
        if self.parent_plotter.number_time_points is None or self.parent_plotter.number_time_points <= 1:
            return

        self._animation_direction = -1
        self._is_playing = True
        self._animation_timer.start()

    def _animation_step(self) -> None:
        """
        Timer callback to advance animation by one frame.
        """
        if self.parent_plotter is None or not self._is_playing:
            return

        current_time_point = self.parent_plotter.active_time_point
        num_time_points = self.parent_plotter.number_time_points

        if current_time_point is None or num_time_points is None:
            return

        # Calculate next time point
        next_time_point = current_time_point + self._animation_direction

        # Handle boundaries
        if self._animation_direction > 0:  # Forward
            if next_time_point >= num_time_points:
                if self.loop_action.isChecked():
                    next_time_point = 0
                else:
                    self.pause()
                    return
        else:  # Reverse
            if next_time_point < 0:
                if self.loop_action.isChecked():
                    next_time_point = num_time_points - 1
                else:
                    self.pause()
                    return

        # Advance frame
        self.set_time_point(next_time_point)

    def _update_time_combobox(self) -> None:
        """
        Update the time combobox selection to match the current active time point.
        """
        if self.parent_plotter is None:
            return
        if self.parent_plotter.active_time_point is None:
            return

        # Block signals to prevent triggering _on_time_combobox_changed
        self._time_combobox.blockSignals(True)
        self._time_combobox.setCurrentIndex(self.parent_plotter.active_time_point)
        self._time_combobox.blockSignals(False)

    def _on_time_combobox_changed(self, index: int) -> None:
        """
        Handle time combobox selection change.

        Parameters
        ----------
        index : int
            The selected time point index.
        """
        if index >= 0:
            self.set_time_point(index)

    def close(self) -> None:
        """
        Close the plotter and window, releasing resources.

        This method closes both the QtInteractor plotter and the QMainWindow.
        """
        # Stop animation timer if running
        if self._animation_timer and self._animation_timer.isActive():
            self._animation_timer.stop()

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
