"""
Qt window management for PyVista visualization.

Provides QtPlotterWindow class that encapsulates Qt application and window
management for interactive 3D visualization using pyvistaqt.QtInteractor.
"""

from typing import TYPE_CHECKING, Callable, TypedDict

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QVBoxLayout
    from pyvistaqt import QtInteractor
    from pyemsi.plotter import Plotter

from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QVBoxLayout, QToolBar, QComboBox
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize, Qt, QTimer
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np
from vtkmodules.vtkCommonDataModel import vtkStaticPointLocator
from vtkmodules.vtkRenderingCore import vtkCellPicker
import pyemsi.resources.resources  # noqa: F401
from .display_settings_dialog import DisplaySettingsDialog
from .block_visibility_dialog import BlockVisibilityDialog
from .scalar_bar_settings_dialog import ScalarBarSettingsDialog
from .cell_query_dialog import CellQueryDialog
from .point_query_dialog import PointQueryDialog


class PointPickResult(TypedDict):
    """Result payload returned by one-shot point-picking mode."""

    coordinates: tuple[float, float, float]
    point_id: int
    block_name: str | None
    highlight_mesh: pv.PolyData


class _PointPickCandidate(PointPickResult):
    """Internal candidate payload with global point-cloud index."""

    global_index: int


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
        Window size as (width, height) in pixels. Default is None.
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
    _query_toolbar: "QToolBar"
    plotter: "QtInteractor | pv.Plotter"
    parent_plotter: "Plotter | None"
    _point_pick_mode_enabled: bool
    _point_pick_mode_move_observer: int | None
    _point_pick_mode_click_observer: int | None
    _point_pick_mode_callback: Callable[[PointPickResult], None] | None
    _point_pick_mode_point_color: str
    _point_pick_mode_point_size: int
    _point_pick_mode_render_points_as_spheres: bool
    _point_pick_mode_picker_tolerance: float
    _point_pick_mode_highlight_actor_name: str
    _point_pick_mode_active_idx: int | None
    _point_pick_mode_world_picker: vtkCellPicker | None
    _point_pick_mode_point_cloud: pv.PolyData | None
    _point_pick_mode_locator: vtkStaticPointLocator | None
    _point_pick_mode_block_index_to_name: dict[int, str | None]

    def __init__(
        self,
        title: str = "PyVista Plotter",
        window_size: tuple[int, int] | None = None,
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
        window_size : tuple of int or None, optional
            Window size as (width, height) in pixels. Default is None.
        position : tuple of int or None, optional
            Window position as (x, y) in screen coordinates. If None, uses OS default.
        parent_plotter : Plotter or None, optional
            Reference to the parent Plotter instance. Default is None.
        **qt_interactor_kwargs
            Additional keyword arguments passed to QtInteractor (e.g., off_screen).
        """
        # Store reference to parent plotter
        self.parent_plotter = parent_plotter

        # Dialog references to maintain state
        self._cell_query_dialog: CellQueryDialog | None = None
        self._point_query_dialog: PointQueryDialog | None = None

        # One-shot point-picking mode state
        self._point_pick_mode_enabled = False
        self._point_pick_mode_move_observer = None
        self._point_pick_mode_click_observer = None
        self._point_pick_mode_callback = None
        self._point_pick_mode_point_color = "red"
        self._point_pick_mode_point_size = 16
        self._point_pick_mode_render_points_as_spheres = True
        self._point_pick_mode_picker_tolerance = 0.025
        self._point_pick_mode_highlight_actor_name = "_point_pick_mode_highlight"
        self._point_pick_mode_active_idx = None
        self._point_pick_mode_world_picker = None
        self._point_pick_mode_point_cloud = None
        self._point_pick_mode_locator = None
        self._point_pick_mode_block_index_to_name: dict[int, str | None] = {}

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
        if window_size is not None:
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
        self._create_query_toolbar()

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

    def _create_query_toolbar(self) -> None:
        """
        Create and configure the query tools toolbar.

        Adds a movable toolbar with buttons for cell query and other query operations.
        """
        self._query_toolbar = QToolBar("Query Tools")
        self._query_toolbar.setMovable(True)
        self._query_toolbar.setIconSize(QSize(24, 24))

        # Cell Query action
        cell_query_action = QAction(QIcon(":/icons/QueryCell.svg"), "Cell Query", self._window)
        cell_query_action.setToolTip("Open cell query dialog")
        cell_query_action.triggered.connect(self._open_cell_query_dialog)
        self._query_toolbar.addAction(cell_query_action)

        # Point Query action
        point_query_action = QAction(QIcon(":/icons/QueryPoint.svg"), "Point Query", self._window)
        point_query_action.setToolTip("Open point query dialog")
        point_query_action.triggered.connect(self._open_point_query_dialog)
        self._query_toolbar.addAction(point_query_action)

        check_point_action = QAction("Check Point", self._window)
        check_point_action.setToolTip("Check point picking mode")
        check_point_action.triggered.connect(
            lambda: self.enable_point_picking_mode(
                on_picked=lambda result: print(f"Picked point: {result}"),
                point_color="yellow",
                point_size=20,
                render_points_as_spheres=True,
                picker_tolerance=0.01,
            )
        )
        self._query_toolbar.addAction(check_point_action)

        # Add toolbar to main window
        self._window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._query_toolbar)

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

        # Scalar bar action
        scalar_bar_action = QAction("Scalar Bars", self._window)
        scalar_bar_action.setToolTip("Control scalar bars")
        scalar_bar_action.triggered.connect(self._open_scalar_bar_settings_dialog)
        self._display_toolbar.addAction(scalar_bar_action)

        # Add toolbar to main window
        self._window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self._display_toolbar)

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
        display_settings_dialog = DisplaySettingsDialog(plotter=self.plotter, plotter_window=self)
        display_settings_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Show and raise dialog (non-blocking)
        display_settings_dialog.show()
        display_settings_dialog.raise_()
        display_settings_dialog.activateWindow()

    def _open_scalar_bar_settings_dialog(self) -> None:
        """Open the scalar bar settings dialog."""
        scalar_bar_settings_dialog = ScalarBarSettingsDialog(plotter=self.plotter, plotter_window=self)
        scalar_bar_settings_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Show and bring to front
        scalar_bar_settings_dialog.show()
        scalar_bar_settings_dialog.raise_()
        scalar_bar_settings_dialog.activateWindow()

    def _open_block_visibility_dialog(self) -> None:
        """Open block visibility dialog (non-blocking)."""
        # Only open if parent plotter has multi-block mesh
        if self.parent_plotter is None or not isinstance(self.parent_plotter.mesh, pv.MultiBlock):
            return

        # Create dialog if it doesn't exist or was closed
        block_visibility_dialog = BlockVisibilityDialog(plotter=self.plotter, plotter_window=self)
        block_visibility_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Show and raise dialog (non-blocking)
        block_visibility_dialog.show()
        block_visibility_dialog.raise_()
        block_visibility_dialog.activateWindow()

    def _open_scalar_bar_settings_dialog(self) -> None:
        """Open scalar bar settings dialog (non-blocking)."""
        # Create dialog if it doesn't exist or was closed
        scalar_bar_settings_dialog = ScalarBarSettingsDialog(plotter=self.plotter, plotter_window=self)
        scalar_bar_settings_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Show and raise dialog (non-blocking)
        scalar_bar_settings_dialog.show()
        scalar_bar_settings_dialog.raise_()
        scalar_bar_settings_dialog.activateWindow()

    def _open_cell_query_dialog(self) -> None:
        """Open cell query dialog (non-blocking)."""
        self.disable_point_picking_mode(render=False)

        # Disable point picking before enabling cell picking.
        if self._point_query_dialog is not None and self._point_query_dialog._picking_enabled:
            self._point_query_dialog._disable_picking()

        # Create dialog if it doesn't exist or was deleted
        if self._cell_query_dialog is None or not self._cell_query_dialog.isVisible():
            # Check if the dialog object was deleted by Qt
            try:
                if self._cell_query_dialog is not None:
                    # Try to access a property to see if it's still valid
                    _ = self._cell_query_dialog.isVisible()
            except RuntimeError:
                # Object was deleted, create a new one
                self._cell_query_dialog = None

            if self._cell_query_dialog is None:
                self._cell_query_dialog = CellQueryDialog(plotter=self.plotter, plotter_window=self)
                # Don't set WA_DeleteOnClose to keep the dialog alive between sessions

        # Re-enable picking if it was disabled
        if not self._cell_query_dialog._picking_enabled:
            self._cell_query_dialog._enable_picking()

        # Restore visualizations for previously selected cells
        self._cell_query_dialog._restore_visualizations()

        # Show and raise dialog (non-blocking)
        self._cell_query_dialog.show()
        self._cell_query_dialog.raise_()
        self._cell_query_dialog.activateWindow()

    def _open_point_query_dialog(self) -> None:
        """Open point query dialog (non-blocking)."""
        self.disable_point_picking_mode(render=False)

        # Disable cell picking before enabling point picking.
        if self._cell_query_dialog is not None and self._cell_query_dialog._picking_enabled:
            self._cell_query_dialog._disable_picking()

        # Create dialog if it doesn't exist or was deleted
        if self._point_query_dialog is None or not self._point_query_dialog.isVisible():
            # Check if the dialog object was deleted by Qt
            try:
                if self._point_query_dialog is not None:
                    _ = self._point_query_dialog.isVisible()
            except RuntimeError:
                self._point_query_dialog = None

            if self._point_query_dialog is None:
                self._point_query_dialog = PointQueryDialog(plotter=self.plotter, plotter_window=self)
                # Don't set WA_DeleteOnClose to keep the dialog alive between sessions

        # Re-enable picking if it was disabled
        if not self._point_query_dialog._picking_enabled:
            self._point_query_dialog._enable_picking()

        # Restore visualizations for previously selected points
        self._point_query_dialog._restore_visualizations()

        # Show and raise dialog (non-blocking)
        self._point_query_dialog.show()
        self._point_query_dialog.raise_()
        self._point_query_dialog.activateWindow()

    def enable_point_picking_mode(
        self,
        *,
        on_picked: Callable[[PointPickResult], None],
        point_color: str = "red",
        point_size: int = 16,
        render_points_as_spheres: bool = True,
        picker_tolerance: float = 0.025,
    ) -> None:
        """Enable one-shot point-picking mode.

        In this mode, the nearest point to the mouse hover location is highlighted.
        On a valid left click, the point payload is returned through ``on_picked``,
        then mode is automatically disabled and cleaned up.
        """
        if not callable(on_picked):
            raise TypeError("on_picked must be callable.")

        self.disable_point_picking_mode(render=False)

        # Enforce mutual exclusion with existing query picking modes.
        if self._cell_query_dialog is not None and self._cell_query_dialog._picking_enabled:
            self._cell_query_dialog._disable_picking()
        if self._point_query_dialog is not None and self._point_query_dialog._picking_enabled:
            self._point_query_dialog._disable_picking()

        self._point_pick_mode_callback = on_picked
        self._point_pick_mode_point_color = point_color
        self._point_pick_mode_point_size = point_size
        self._point_pick_mode_render_points_as_spheres = render_points_as_spheres
        self._point_pick_mode_picker_tolerance = picker_tolerance

        self._build_point_pick_mode_index()

        self._point_pick_mode_world_picker = vtkCellPicker()
        self._point_pick_mode_world_picker.SetTolerance(self._point_pick_mode_picker_tolerance)

        iren = getattr(self.plotter, "iren", None)
        if iren is None:
            self.disable_point_picking_mode(render=False)
            raise RuntimeError("Plotter interactor is not available.")

        self._point_pick_mode_move_observer = iren.add_observer("MouseMoveEvent", self._on_point_pick_mode_mouse_move)
        self._point_pick_mode_click_observer = iren.add_observer(
            "LeftButtonPressEvent", self._on_point_pick_mode_left_click
        )

        self._point_pick_mode_enabled = True
        self._point_pick_mode_active_idx = None

    def disable_point_picking_mode(self, render: bool = True) -> None:
        """Disable one-shot point-picking mode and clean up temporary actors."""
        iren = getattr(self.plotter, "iren", None)
        if iren is not None and self._point_pick_mode_move_observer is not None:
            iren.remove_observer(self._point_pick_mode_move_observer)
        if iren is not None and self._point_pick_mode_click_observer is not None:
            iren.remove_observer(self._point_pick_mode_click_observer)

        self._point_pick_mode_move_observer = None
        self._point_pick_mode_click_observer = None
        self._point_pick_mode_enabled = False

        self._clear_point_pick_mode_highlight(render=False)

        self._point_pick_mode_callback = None
        self._point_pick_mode_world_picker = None
        self._point_pick_mode_point_cloud = None
        self._point_pick_mode_locator = None
        self._point_pick_mode_block_index_to_name.clear()

        if render:
            self.plotter.render()

    def _build_point_pick_mode_index(self) -> None:
        """Build a global point index for nearest-point lookup."""
        if self.parent_plotter is None:
            raise ValueError("Parent plotter is not available.")

        mesh = self.parent_plotter.mesh
        if mesh is None:
            raise ValueError("No mesh is loaded for point picking.")

        all_points: list[np.ndarray] = []
        all_point_ids: list[np.ndarray] = []
        all_block_indices: list[np.ndarray] = []
        self._point_pick_mode_block_index_to_name.clear()

        if isinstance(mesh, pv.MultiBlock):
            for idx, block in enumerate(mesh):
                if block is None:
                    continue
                if getattr(block, "n_points", 0) <= 0:
                    continue

                block_name = mesh.get_block_name(idx)
                if not block_name:
                    block_name = str(idx)
                if not self.parent_plotter.get_block_visibility(block_name):
                    continue

                points = np.asarray(block.points, dtype=float)
                if points.size == 0:
                    continue
                n_points = points.shape[0]

                all_points.append(points)
                all_point_ids.append(np.arange(n_points, dtype=np.int64))
                all_block_indices.append(np.full(n_points, idx, dtype=np.int64))
                self._point_pick_mode_block_index_to_name[idx] = block_name
        else:
            if getattr(mesh, "n_points", 0) > 0:
                points = np.asarray(mesh.points, dtype=float)
                if points.size > 0:
                    n_points = points.shape[0]
                    all_points.append(points)
                    all_point_ids.append(np.arange(n_points, dtype=np.int64))
                    all_block_indices.append(np.full(n_points, -1, dtype=np.int64))
                    self._point_pick_mode_block_index_to_name[-1] = None

        if not all_points:
            raise ValueError("No visible points available for point picking.")

        point_cloud = pv.PolyData(np.concatenate(all_points, axis=0))
        point_cloud.point_data["orig_point_id"] = np.concatenate(all_point_ids, axis=0)
        point_cloud.point_data["orig_block_flat_index"] = np.concatenate(all_block_indices, axis=0)

        locator = vtkStaticPointLocator()
        locator.SetDataSet(point_cloud)
        locator.BuildLocator()

        self._point_pick_mode_point_cloud = point_cloud
        self._point_pick_mode_locator = locator
        self._point_pick_mode_active_idx = None

    def _resolve_point_pick_mode_candidate(self) -> _PointPickCandidate | None:
        """Resolve nearest candidate point from current mouse event position."""
        if not self._point_pick_mode_enabled:
            return None
        if self._point_pick_mode_point_cloud is None or self._point_pick_mode_locator is None:
            return None
        if self._point_pick_mode_world_picker is None:
            return None

        iren = getattr(self.plotter, "iren", None)
        if iren is None:
            return None

        x_pos, y_pos = iren.get_event_position()
        renderer = iren.get_poked_renderer(x_pos, y_pos)
        if renderer is None:
            return None

        self._point_pick_mode_world_picker.Pick(x_pos, y_pos, 0, renderer)
        if self._point_pick_mode_world_picker.GetDataSet() is None:
            return None

        picked_position = self._point_pick_mode_world_picker.GetPickPosition()
        global_index = int(self._point_pick_mode_locator.FindClosestPoint(picked_position))
        if global_index < 0:
            return None

        point_array = self._point_pick_mode_point_cloud.points[global_index]
        coordinates = (float(point_array[0]), float(point_array[1]), float(point_array[2]))
        point_id = int(self._point_pick_mode_point_cloud.point_data["orig_point_id"][global_index])
        block_index = int(self._point_pick_mode_point_cloud.point_data["orig_block_flat_index"][global_index])
        block_name = self._point_pick_mode_block_index_to_name.get(block_index)
        highlight_mesh = pv.PolyData(np.array([coordinates], dtype=float))

        return {
            "global_index": global_index,
            "coordinates": coordinates,
            "point_id": point_id,
            "block_name": block_name,
            "highlight_mesh": highlight_mesh,
        }

    def _update_point_pick_mode_highlight(self, highlight_mesh: pv.PolyData) -> None:
        """Update temporary hover highlight actor."""
        self.plotter.remove_actor(self._point_pick_mode_highlight_actor_name, render=False)
        self.plotter.add_mesh(
            highlight_mesh,
            style="points",
            color=self._point_pick_mode_point_color,
            point_size=self._point_pick_mode_point_size,
            render_points_as_spheres=self._point_pick_mode_render_points_as_spheres,
            pickable=False,
            reset_camera=False,
            name=self._point_pick_mode_highlight_actor_name,
        )
        self.plotter.render()

    def _clear_point_pick_mode_highlight(self, render: bool) -> None:
        """Remove temporary hover highlight actor."""
        self.plotter.remove_actor(self._point_pick_mode_highlight_actor_name, render=False)
        self._point_pick_mode_active_idx = None
        if render:
            self.plotter.render()

    def _on_point_pick_mode_mouse_move(self, *_args) -> None:
        """Update hover highlight on mouse move."""
        candidate = self._resolve_point_pick_mode_candidate()
        if candidate is None:
            if self._point_pick_mode_active_idx is not None:
                self._clear_point_pick_mode_highlight(render=True)
            return

        if candidate["global_index"] == self._point_pick_mode_active_idx:
            return

        self._point_pick_mode_active_idx = candidate["global_index"]
        self._update_point_pick_mode_highlight(candidate["highlight_mesh"])

    def _on_point_pick_mode_left_click(self, *_args) -> None:
        """Return picked point payload on valid left click and then disable mode."""
        candidate = self._resolve_point_pick_mode_candidate()
        if candidate is None:
            return

        payload: PointPickResult = {
            "coordinates": candidate["coordinates"],
            "point_id": candidate["point_id"],
            "block_name": candidate["block_name"],
            "highlight_mesh": candidate["highlight_mesh"],
        }

        callback = self._point_pick_mode_callback
        try:
            if callback is not None:
                callback(payload)
        finally:
            self.disable_point_picking_mode(render=True)

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
        self.plotter.reset_camera()
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
        self.disable_point_picking_mode(render=False)

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
