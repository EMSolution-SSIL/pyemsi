"""
Cell Query Dialog for PyVista visualization.

Provides interactive cell picking and query functionality with split-panel interface
showing selected cells (left) and query results (right).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QDialog, QSplitter, QTableWidget, QTabWidget, QVBoxLayout, QHBoxLayout
    from PySide6.QtWidgets import QPushButton, QLabel, QWidget, QMessageBox
    from pyvistaqt import QtInteractor
    from pyemsi.qt_window import QtPlotterWindow
    import pyvista as pv

from PySide6.QtWidgets import (
    QDialog,
    QSplitter,
    QTableWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QProgressDialog,
    QApplication,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import pyvista as pv
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class CellQueryDialog(QDialog):
    """
    Dialog for interactive cell picking and querying.

    Provides a split-panel interface with a selection table (left) showing
    picked cells and a tabbed results viewer (right) displaying query data.

    Parameters
    ----------
    plotter : QtInteractor
        The PyVista plotter instance for visualization.
    plotter_window : QtPlotterWindow
        Reference to the parent plotter window.

    Attributes
    ----------
    plotter : QtInteractor
        The PyVista plotter instance.
    plotter_window : QtPlotterWindow
        Reference to the parent plotter window.
    _selected_cells : list of tuple
        Internal list of selected (cell_id, block_name, mesh) tuples.
    """

    def __init__(
        self,
        plotter: "QtInteractor",
        plotter_window: "QtPlotterWindow",
    ):
        """
        Initialize the Cell Query Dialog.

        Parameters
        ----------
        plotter : QtInteractor
            The PyVista plotter instance.
        plotter_window : QtPlotterWindow
            Reference to the parent plotter window.
        """
        self.plotter_window = plotter_window
        super().__init__(plotter_window._window)
        self.plotter = plotter

        # Internal state
        self._selected_cells: list[tuple[int, str | None, pv.PolyData | pv.UnstructuredGrid]] = []
        self._visualization_actors: set[tuple[int, str | None]] = set()  # Track visualized cells

        # Configure dialog
        self.setWindowTitle("Cell Query")
        self.setWindowIcon(QIcon(":/icons/QueryCell.svg"))
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint
        )
        self.resize(900, 600)

        # Build UI
        self._create_ui()

        # Enable cell picking on open
        self._enable_picking()

    def _create_ui(self) -> None:
        """Create the dialog UI with split-panel layout."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create horizontal splitter for left/right panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Selection table and controls
        left_widget = self._create_left_panel()
        splitter.addWidget(left_widget)

        # Right panel: Query results tabs
        right_widget = self._create_right_panel()
        splitter.addWidget(right_widget)

        # Set initial splitter sizes (1:2 ratio)
        splitter.setSizes([300, 600])

        # Add splitter to main layout
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

    def _create_left_panel(self) -> QWidget:
        """
        Create the left panel with selection table and control buttons.

        Returns
        -------
        QWidget
            The left panel widget.
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Selection table
        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Cell ID", "Block ID"])
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self._table)

        # Button row
        button_layout = QHBoxLayout()

        self._run_query_button = QPushButton("Run Query")
        self._run_query_button.setEnabled(False)  # Initially disabled
        self._run_query_button.clicked.connect(self._on_run_query)
        button_layout.addWidget(self._run_query_button)

        self._remove_button = QPushButton("Remove Selected")
        self._remove_button.clicked.connect(self._on_remove_selected)
        button_layout.addWidget(self._remove_button)

        self._clear_button = QPushButton("Clear")
        self._clear_button.clicked.connect(self._on_clear)
        button_layout.addWidget(self._clear_button)

        left_layout.addLayout(button_layout)

        left_widget.setLayout(left_layout)
        return left_widget

    def _create_right_panel(self) -> QWidget:
        """
        Create the right panel with tabbed query results viewer.

        Returns
        -------
        QWidget
            The right panel widget.
        """
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget for results
        self._tab_widget = QTabWidget()

        # First tab: Query results - contains nested tabs for each cell
        self._results_tab_widget = QTabWidget()
        self._tab_widget.addTab(self._results_tab_widget, "Query Results")

        # Second tab: Plots - contains nested tabs for each field
        self._plots_tab_widget = QTabWidget()
        self._tab_widget.addTab(self._plots_tab_widget, "Plots")

        right_layout.addWidget(self._tab_widget)

        right_widget.setLayout(right_layout)
        return right_widget

    @property
    def _picking_enabled(self) -> bool:
        """Check if cell picking mode is enabled via the plotter window."""
        return self.plotter_window._cell_pick_mode_enabled

    def _enable_picking(self) -> None:
        """Enable cell picking mode via the plotter window."""
        try:
            self.plotter_window.enable_cell_picking_mode(
                on_picked=self._on_cell_picked,
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Picking Error",
                f"Failed to enable cell picking:\n{str(e)}",
            )

    def _disable_picking(self) -> None:
        """Disable cell picking mode via the plotter window."""
        try:
            self.plotter_window.disable_cell_picking_mode(render=False)
        except Exception:
            pass  # Silently ignore disable errors on close

    @staticmethod
    def _actor_suffix(block_name: str | None) -> str:
        """Create a stable actor name suffix from an optional block name."""
        if block_name is None:
            return "none"
        return str(block_name).replace(" ", "_")

    def _visualize_cell(
        self,
        cell_id: int,
        block_name: str | None,
        mesh: "pv.PolyData | pv.UnstructuredGrid",
    ) -> None:
        """Add wireframe and label visualization for a picked cell.

        Parameters
        ----------
        cell_id : int
            The cell ID.
        block_name : str or None
            The block name.
        mesh : pv.PolyData or pv.UnstructuredGrid
            The picked mesh containing the cell.
        """
        try:
            actor_suffix = self._actor_suffix(block_name)

            # Add wireframe visualization
            self.plotter.add_mesh(
                mesh,
                style="wireframe",
                color="red",
                line_width=5,
                render_lines_as_tubes=True,
                pickable=False,
                name=f"cell_viz_mesh_{cell_id}_{actor_suffix}",
            )

            # Get mesh center for label positioning
            center = mesh.center
            block_label = block_name if block_name is not None else "N/A"

            # Add label at center
            self.plotter.add_point_labels(
                [center],
                [f"{cell_id}({block_label})"],
                font_size=16,
                text_color="white",
                show_points=False,
                always_visible=True,
                shadow=True,
                shape="rounded_rect",
                fill_shape=True,
                shape_color="black",
                shape_opacity=0.7,
                name=f"cell_viz_label_{cell_id}_{actor_suffix}",
            )

            # Track this visualization
            self._visualization_actors.add((cell_id, block_name))

            # Render to show visualization immediately
            self.plotter.render()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Visualization Error",
                f"Failed to visualize cell {cell_id}:\n{str(e)}",
            )

    def _remove_cell_visualization(self, cell_id: int, block_name: str | None, render: bool = True) -> None:
        """Remove visualization actors for a specific cell.

        Parameters
        ----------
        cell_id : int
            The cell ID.
        block_name : str or None
            The block name.
        render : bool, optional
            Whether to render after removal. Default is True.
        """
        key = (cell_id, block_name)
        if key not in self._visualization_actors:
            return

        actor_suffix = self._actor_suffix(block_name)
        # Remove both actors using their names
        self.plotter.remove_actor(f"cell_viz_mesh_{cell_id}_{actor_suffix}", render=False)
        self.plotter.remove_actor(f"cell_viz_label_{cell_id}_{actor_suffix}", render=False)

        # Remove from tracking
        self._visualization_actors.discard(key)

        # Render if requested
        if render:
            self.plotter.render()

    def _restore_visualizations(self) -> None:
        """Restore visualizations for all selected cells.

        Called when the dialog is reopened to re-display the wireframe
        and labels for previously selected cells.
        """
        if not self._selected_cells:
            return

        # Suppress rendering for batch operations
        self.plotter.suppress_rendering = True

        # Re-visualize all selected cells
        for cell_id, block_name, mesh in self._selected_cells:
            # Skip if already visualized
            if (cell_id, block_name) in self._visualization_actors:
                continue

            actor_suffix = self._actor_suffix(block_name)
            block_label = block_name if block_name is not None else "N/A"

            # Add wireframe visualization
            self.plotter.add_mesh(
                mesh,
                style="wireframe",
                color="red",
                line_width=5,
                render_lines_as_tubes=True,
                pickable=False,
                name=f"cell_viz_mesh_{cell_id}_{actor_suffix}",
            )

            # Add label at center
            center = mesh.center
            self.plotter.add_point_labels(
                [center],
                [f"{cell_id}({block_label})"],
                font_size=16,
                text_color="white",
                show_points=False,
                always_visible=True,
                shadow=True,
                shape="rounded_rect",
                fill_shape=True,
                shape_color="black",
                shape_opacity=0.7,
                name=f"cell_viz_label_{cell_id}_{actor_suffix}",
            )

            # Track this visualization
            self._visualization_actors.add((cell_id, block_name))

        # Re-enable rendering and render once
        self.plotter.suppress_rendering = False
        self.plotter.render()

    def _on_cell_picked(self, result: dict) -> None:
        """
        Callback when a cell is picked.

        Parameters
        ----------
        result : dict
            Dict with 'cell_id', 'block_name', 'coordinates', 'highlight_mesh'.
        """
        try:
            # Extract values from result dict
            cell_id = result["cell_id"]
            block_name = result["block_name"]
            mesh = result["highlight_mesh"]

            # Check for duplicates
            if any(
                selected_id == cell_id and selected_block == block_name
                for selected_id, selected_block, _ in self._selected_cells
            ):
                return  # Already selected, ignore

            # Add to internal list
            self._selected_cells.append((cell_id, block_name, mesh))

            # Add row to table
            row_position = self._table.rowCount()
            self._table.insertRow(row_position)
            self._table.setItem(row_position, 0, QTableWidgetItem(str(cell_id)))
            self._table.setItem(row_position, 1, QTableWidgetItem(block_name if block_name is not None else "N/A"))

            # Visualize the picked cell
            self._visualize_cell(cell_id, block_name, mesh)

            # Enable Run Query button
            self._run_query_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Picking Error",
                f"Error processing picked cell:\n{str(e)}",
            )

    def _on_run_query(self) -> None:
        """Execute query on selected cells and display results."""
        if not self._selected_cells:
            return

        # Disable button during query to prevent concurrent operations
        self._run_query_button.setEnabled(False)
        progress_dialog = None

        try:
            # Extract cell IDs and block names
            cell_ids = [c[0] for c in self._selected_cells]
            block_names = [c[1] for c in self._selected_cells]

            # Query cells using parent plotter
            if self.plotter_window.parent_plotter is None:
                QMessageBox.warning(
                    self,
                    "Query Error",
                    "Parent plotter is not available.",
                )
                return

            # Create progress dialog
            progress_dialog = QProgressDialog(
                "Preparing to query cells...",
                "Cancel",
                0,
                100,
                self,
            )
            progress_dialog.setWindowTitle("Querying Cells")
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setMinimumDuration(500)  # Show after 500ms to avoid flicker
            progress_dialog.setValue(0)

            # Define progress callback
            def update_progress(current: int, total: int) -> bool:
                """Update progress dialog and check for cancellation."""
                if total > 0:
                    percentage = int((current / total) * 100)
                    progress_dialog.setValue(percentage)
                    progress_dialog.setLabelText(f"Processing cell data... ({current}/{total})")
                # Process events to keep UI responsive
                QApplication.processEvents()
                # Return False if user cancelled
                return not progress_dialog.wasCanceled()

            # Execute query with progress callback
            query_results = self.plotter_window.parent_plotter.query_cells(
                cell_ids, block_names, progress_callback=update_progress
            )

            # Close progress dialog
            progress_dialog.close()

            # Check if user cancelled
            if not query_results and progress_dialog.wasCanceled():
                QMessageBox.information(
                    self,
                    "Query Cancelled",
                    "Cell query was cancelled by user.",
                )
                return

            # Clear previous results
            self._results_tab_widget.clear()
            self._plots_tab_widget.clear()

            # Populate results tabs
            self._populate_results(query_results, cell_ids, block_names)
            self._populate_plots(query_results, cell_ids, block_names)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Query Error",
                f"Failed to query cells:\n{str(e)}",
            )
        finally:
            # Clean up progress dialog
            if progress_dialog is not None:
                progress_dialog.close()
                progress_dialog.deleteLater()

            # Re-enable button
            self._run_query_button.setEnabled(len(self._selected_cells) > 0)

    def _populate_results(
        self,
        query_results: list,
        cell_ids: list[int],
        block_names: list[str | None],
    ) -> None:
        """
        Populate the nested tabs with query results for each cell.

        Parameters
        ----------
        query_results : list
            List of dictionaries, one per cell. Each dict has field names as keys,
            with values being dicts containing 'time'/'value' or 'time'/'x_value'/'y_value'/'z_value'.
        cell_ids : list[int]
            List of cell IDs corresponding to query_results.
        block_names : list[str | None]
            List of block names corresponding to query_results.
        """
        if not query_results:
            # Show message in empty tab
            empty_label = QLabel("No data available for selected cells.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._results_tab_widget.addTab(empty_label, "No Results")
            return

        # Create a tab for each cell
        for cell_id, block_name, cell_data in zip(cell_ids, block_names, query_results):
            # Create table for this cell
            cell_table = QTableWidget()
            cell_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            cell_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            cell_table.horizontalHeader().setStretchLastSection(True)

            # Get all field names and time points for this cell
            all_fields = sorted(cell_data.keys())
            all_time_points = set()
            has_time_data = False

            for field_name, field_data in cell_data.items():
                if isinstance(field_data, dict) and "time" in field_data:
                    has_time_data = True
                    time_values = field_data["time"]
                    if isinstance(time_values, list):
                        all_time_points.update(time_values)

            all_time_points = sorted(all_time_points)

            # Build table structure
            if has_time_data and all_time_points:
                # Rows are time points, columns are fields
                cell_table.setRowCount(len(all_time_points))
                cell_table.setVerticalHeaderLabels([f"{t:.5g}" for t in all_time_points])

                # Count columns (some fields may be vectors with X, Y, Z)
                columns = []
                for field in all_fields:
                    field_data = cell_data[field]
                    if isinstance(field_data, dict) and all(k in field_data for k in ["x_value", "y_value", "z_value"]):
                        columns.append(field)  # Single column for vector
                    else:
                        columns.append(field)

                cell_table.setColumnCount(len(columns))
                cell_table.setHorizontalHeaderLabels(columns)

                # Populate table
                col_idx = 0
                for field in all_fields:
                    field_data = cell_data[field]

                    if isinstance(field_data, dict):
                        # Check for vector data
                        if all(k in field_data for k in ["x_value", "y_value", "z_value"]):
                            time_values = field_data.get("time", [])
                            x_values = field_data["x_value"]
                            y_values = field_data["y_value"]
                            z_values = field_data["z_value"]

                            for row_idx, t in enumerate(all_time_points):
                                try:
                                    t_idx = time_values.index(t)
                                    vector_str = (
                                        f"[{x_values[t_idx]:.6g}, {y_values[t_idx]:.6g}, {z_values[t_idx]:.6g}]"
                                    )
                                    cell_table.setItem(row_idx, col_idx, QTableWidgetItem(vector_str))
                                except (ValueError, IndexError):
                                    cell_table.setItem(row_idx, col_idx, QTableWidgetItem(""))
                            col_idx += 1

                        # Check for scalar data
                        elif "value" in field_data:
                            time_values = field_data.get("time", [])
                            data_values = field_data["value"]

                            for row_idx, t in enumerate(all_time_points):
                                try:
                                    t_idx = time_values.index(t)
                                    val = data_values[t_idx]
                                    cell_table.setItem(
                                        row_idx,
                                        col_idx,
                                        QTableWidgetItem(f"{val:.6g}" if isinstance(val, (int, float)) else str(val)),
                                    )
                                except (ValueError, IndexError):
                                    cell_table.setItem(row_idx, col_idx, QTableWidgetItem(""))
                            col_idx += 1
                        else:
                            # Unknown structure
                            for row_idx in range(len(all_time_points)):
                                cell_table.setItem(row_idx, col_idx, QTableWidgetItem(str(field_data)))
                            col_idx += 1
                    else:
                        # Non-dict field
                        for row_idx in range(len(all_time_points)):
                            cell_table.setItem(row_idx, col_idx, QTableWidgetItem(str(field_data)))
                        col_idx += 1

            else:
                # Static data: single row with field values
                columns = []
                for field in all_fields:
                    field_data = cell_data[field]
                    if isinstance(field_data, dict) and all(k in field_data for k in ["x_value", "y_value", "z_value"]):
                        columns.append(field)  # Single column for vector
                    else:
                        columns.append(field)

                cell_table.setRowCount(1)
                cell_table.setColumnCount(len(columns))
                cell_table.setHorizontalHeaderLabels(columns)
                cell_table.setVerticalHeaderLabels(["Value"])

                # Populate single row
                col_idx = 0
                for field in all_fields:
                    field_data = cell_data[field]

                    if isinstance(field_data, dict):
                        # Check for vector data
                        if all(k in field_data for k in ["x_value", "y_value", "z_value"]):
                            x_values = field_data["x_value"]
                            y_values = field_data["y_value"]
                            z_values = field_data["z_value"]

                            if isinstance(x_values, list) and len(x_values) > 0:
                                vector_str = f"[{x_values[0]:.6g}, {y_values[0]:.6g}, {z_values[0]:.6g}]"
                            else:
                                vector_str = f"[{x_values:.6g}, {y_values:.6g}, {z_values:.6g}]"
                            cell_table.setItem(0, col_idx, QTableWidgetItem(vector_str))
                            col_idx += 1

                        # Check for scalar data
                        elif "value" in field_data:
                            data_values = field_data["value"]
                            if isinstance(data_values, list) and len(data_values) > 0:
                                val = data_values[0]
                            else:
                                val = data_values
                            cell_table.setItem(
                                0,
                                col_idx,
                                QTableWidgetItem(f"{val:.6g}" if isinstance(val, (int, float)) else str(val)),
                            )
                            col_idx += 1
                        else:
                            # Unknown structure
                            cell_table.setItem(0, col_idx, QTableWidgetItem(str(field_data)))
                            col_idx += 1
                    else:
                        # Non-dict field
                        cell_table.setItem(0, col_idx, QTableWidgetItem(str(field_data)))
                        col_idx += 1

            # Resize columns to content
            cell_table.resizeColumnsToContents()

            # Add this cell's table as a tab
            block_label = block_name if block_name is not None else "N/A"
            self._results_tab_widget.addTab(cell_table, f"Cell {cell_id} (Block {block_label})")

    def _populate_plots(
        self,
        query_results: list,
        cell_ids: list[int],
        block_names: list[str | None],
    ) -> None:
        """
        Create matplotlib plots for each field showing all cells' time responses.

        Parameters
        ----------
        query_results : list
            List of dictionaries, one per cell. Each dict has field names as keys,
            with values being dicts containing 'time'/'value' or 'time'/'x_value'/'y_value'/'z_value'.
        cell_ids : list[int]
            List of cell IDs corresponding to query_results.
        block_names : list[str | None]
            List of block names corresponding to query_results.
        """
        if not query_results:
            return

        # Collect all unique field names across all cells
        all_fields = set()
        for cell_data in query_results:
            all_fields.update(cell_data.keys())

        # Sort for consistent ordering
        all_fields = sorted(all_fields)

        # Create one plot tab per field
        for field_name in all_fields:
            # Check if this field has temporal data (more than one time point)
            has_temporal_data = False
            for cell_data in query_results:
                if field_name in cell_data:
                    field_data = cell_data[field_name]
                    if isinstance(field_data, dict) and "time" in field_data:
                        time_values = field_data["time"]
                        if isinstance(time_values, list) and len(time_values) > 1:
                            has_temporal_data = True
                            break
                        elif not isinstance(time_values, list) and time_values != 0:
                            has_temporal_data = True
                            break

            # Skip plotting if only static data (time: [0])
            if not has_temporal_data:
                continue

            # Create widget for this field's plot
            plot_widget = QWidget()
            plot_layout = QVBoxLayout()
            plot_layout.setContentsMargins(5, 5, 5, 5)

            # Create matplotlib figure and canvas
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            # Create navigation toolbar
            toolbar = NavigationToolbar(canvas, plot_widget)

            # Add toolbar and canvas to layout
            plot_layout.addWidget(toolbar)
            plot_layout.addWidget(canvas)
            plot_widget.setLayout(plot_layout)

            # Plot data for each cell
            has_data = False
            for i, (cell_id, block_name, cell_data) in enumerate(zip(cell_ids, block_names, query_results)):
                if field_name not in cell_data:
                    continue

                field_data = cell_data[field_name]
                if not isinstance(field_data, dict):
                    continue

                time_values = field_data.get("time", [])
                if not time_values or (isinstance(time_values, list) and len(time_values) <= 1):
                    continue

                # Handle scalar fields
                if "value" in field_data:
                    values = field_data["value"]
                    block_label = block_name if block_name is not None else "N/A"
                    ax.plot(
                        time_values,
                        values,
                        marker="o",
                        label=f"Cell {cell_id} (Block {block_label})",
                        linewidth=2,
                        markersize=4,
                    )
                    has_data = True

                # Handle vector fields (plot X/Y/Z components as separate lines)
                elif all(k in field_data for k in ["x_value", "y_value", "z_value"]):
                    x_vals = np.array(field_data["x_value"])
                    y_vals = np.array(field_data["y_value"])
                    z_vals = np.array(field_data["z_value"])
                    block_label = block_name if block_name is not None else "N/A"

                    # Plot each component as a separate line
                    ax.plot(
                        time_values,
                        x_vals,
                        marker="o",
                        label=f"Cell {cell_id} (Block {block_label}) - X",
                        linewidth=2,
                        markersize=4,
                        linestyle="-",
                    )
                    ax.plot(
                        time_values,
                        y_vals,
                        marker="s",
                        label=f"Cell {cell_id} (Block {block_label}) - Y",
                        linewidth=2,
                        markersize=4,
                        linestyle="--",
                    )
                    ax.plot(
                        time_values,
                        z_vals,
                        marker="^",
                        label=f"Cell {cell_id} (Block {block_label}) - Z",
                        linewidth=2,
                        markersize=4,
                        linestyle="-.",
                    )
                    has_data = True

            if has_data:
                # Configure plot appearance
                ax.set_xlabel("Time (s)", fontsize=12)
                ax.set_ylabel(field_name, fontsize=12)
                ax.set_title(f"{field_name} vs Time", fontsize=14, fontweight="bold")
                ax.legend(loc="best", fontsize=9, framealpha=0.9)
                ax.grid(True, alpha=0.3, linestyle="--")
                fig.tight_layout()

                # Add tab
                self._plots_tab_widget.addTab(plot_widget, field_name)
            else:
                # Clean up unused figure
                fig.clear()
                del fig
                del canvas

    def _on_remove_selected(self) -> None:
        """Remove selected rows from table and internal list."""
        selected_rows = set(index.row() for index in self._table.selectedIndexes())

        if not selected_rows:
            return

        # Suppress rendering for batch operations
        self.plotter.suppress_rendering = True

        # Sort rows in descending order to remove from bottom up
        for row in sorted(selected_rows, reverse=True):
            # Remove visualization if exists
            if row < len(self._selected_cells):
                cell_id, block_name, mesh = self._selected_cells[row]
                self._remove_cell_visualization(cell_id, block_name, render=False)
                # Remove from internal list
                del self._selected_cells[row]

            # Remove from table
            self._table.removeRow(row)

        # Re-enable rendering and render once
        self.plotter.suppress_rendering = False
        self.plotter.render()

        # Update button state
        self._run_query_button.setEnabled(len(self._selected_cells) > 0)

    def _on_clear(self) -> None:
        """Clear all selected cells and query results."""
        # Suppress rendering for batch operations
        self.plotter.suppress_rendering = True

        # Remove all visualizations
        for cell_id, block_name in list(self._visualization_actors):
            self._remove_cell_visualization(cell_id, block_name, render=False)

        # Re-enable rendering and render once
        self.plotter.suppress_rendering = False
        self.plotter.render()

        # Clear internal list
        self._selected_cells.clear()

        # Clear table
        self._table.setRowCount(0)

        # Clear results
        self._results_tab_widget.clear()
        self._plots_tab_widget.clear()

        # Disable Run Query button
        self._run_query_button.setEnabled(False)

    def closeEvent(self, event) -> None:
        """Handle dialog close event."""
        # Suppress rendering for batch operations
        self.plotter.suppress_rendering = True

        # Remove all visualization actors
        for cell_id, block_name in list(self._visualization_actors):
            actor_suffix = self._actor_suffix(block_name)
            self.plotter.remove_actor(f"cell_viz_mesh_{cell_id}_{actor_suffix}", render=False)
            self.plotter.remove_actor(f"cell_viz_label_{cell_id}_{actor_suffix}", render=False)

        # Clear tracking set
        self._visualization_actors.clear()

        # Re-enable rendering and render once
        self.plotter.suppress_rendering = False
        self.plotter.render()

        # Disable picking mode
        self._disable_picking()

        # Accept the close event
        event.accept()
