"""
Sample Lines Dialog for PyVista visualization.

Provides a dialog to define sample lines (start, end, resolution), run sampling
via Plotter.sample_lines, and view results in a tabbed interface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyvistaqt import QtInteractor
    from pyemsi.plotter.qt_window import QtPlotterWindow
    import pyvista as pv

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QApplication,
    QSplitter,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)
from PySide6.QtCore import Qt
import numpy as np
import pyvista as pv
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


# ---------------------------------------------------------------------------
# Helper: parse a "x, y, z" string into a float tuple
# ---------------------------------------------------------------------------


def _parse_xyz(text: str) -> tuple[float, float, float] | None:
    """Parse a comma-separated 'x, y, z' string into a float 3-tuple.

    Returns ``None`` if parsing fails.
    """
    try:
        parts = [p.strip() for p in text.split(",")]
        if len(parts) != 3:
            return None
        return (float(parts[0]), float(parts[1]), float(parts[2]))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# AddLineDialog
# ---------------------------------------------------------------------------


class AddLineDialog(QDialog):
    """
    Modal sub-dialog for defining a single sample line.

    Presents three inputs: start point, end point (both as ``QLineEdit`` with an
    optional pick-helper button), and a resolution ``QSpinBox``.

    Parameters
    ----------
    plotter_window : QtPlotterWindow
        Reference to the parent plotter window used to activate point-picking mode.
    parent : QWidget, optional
        Parent widget. Default is ``None``.
    """

    def __init__(self, plotter_window: "QtPlotterWindow", parent=None, initial_values=None) -> None:
        super().__init__(parent)
        self._plotter_window = plotter_window
        self._picking_target: str | None = None  # "start" or "end"
        self._initial_values = initial_values  # (start, end, resolution) or None

        self.setWindowTitle("Edit Sample Line" if initial_values is not None else "Add Sample Line")
        # NonModal so the user can interact with the plotter window during picking.
        # The dialog stays on top of its parent via Qt.WindowType.Window.
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowCloseButtonHint
        )
        self.resize(380, 160)

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct dialog layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 8)
        form = QFormLayout()
        form.setHorizontalSpacing(8)

        # --- Start point row ---
        self._start_edit = QLineEdit()
        self._start_edit.setPlaceholderText("x, y, z")

        self._start_pick_btn = QPushButton("Pick")
        self._start_pick_btn.setFixedWidth(50)
        self._start_pick_btn.setToolTip("Click a point in the 3D view to fill start coordinates")
        self._start_pick_btn.clicked.connect(self._on_pick_start)

        start_row = QHBoxLayout()
        start_row.addWidget(self._start_edit)
        start_row.addWidget(self._start_pick_btn)
        form.addRow("Start Point:", start_row)

        # --- End point row ---
        self._end_edit = QLineEdit()
        self._end_edit.setPlaceholderText("x, y, z")

        self._end_pick_btn = QPushButton("Pick")
        self._end_pick_btn.setFixedWidth(50)
        self._end_pick_btn.setToolTip("Click a point in the 3D view to fill end coordinates")
        self._end_pick_btn.clicked.connect(self._on_pick_end)

        end_row = QHBoxLayout()
        end_row.addWidget(self._end_edit)
        end_row.addWidget(self._end_pick_btn)
        form.addRow("End Point:", end_row)

        # --- Resolution row ---
        self._resolution_spin = QSpinBox()
        self._resolution_spin.setMinimum(1)
        self._resolution_spin.setMaximum(10000)
        self._resolution_spin.setValue(100)
        form.addRow("Resolution:", self._resolution_spin)

        # --- Pre-fill if editing an existing line ---
        if self._initial_values is not None:
            iv_start, iv_end, iv_res = self._initial_values
            self._start_edit.setText(f"{iv_start[0]:.6g}, {iv_start[1]:.6g}, {iv_start[2]:.6g}")
            self._end_edit.setText(f"{iv_end[0]:.6g}, {iv_end[1]:.6g}, {iv_end[2]:.6g}")
            self._resolution_spin.setValue(iv_res)

        layout.addLayout(form)

        # --- Button box ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Pick helpers
    # ------------------------------------------------------------------

    def _on_pick_start(self) -> None:
        """Activate point-picking mode to fill the start coordinate field."""
        self._picking_target = "start"
        self._start_pick_btn.setEnabled(False)
        self._end_pick_btn.setEnabled(False)
        try:
            self._plotter_window.enable_point_picking_mode(on_picked=self._on_point_picked)
        except Exception as exc:
            QMessageBox.critical(self, "Pick Error", f"Could not activate picking:\n{exc}")
            self._picking_target = None
            self._start_pick_btn.setEnabled(True)
            self._end_pick_btn.setEnabled(True)

    def _on_pick_end(self) -> None:
        """Activate point-picking mode to fill the end coordinate field."""
        self._picking_target = "end"
        self._start_pick_btn.setEnabled(False)
        self._end_pick_btn.setEnabled(False)
        try:
            self._plotter_window.enable_point_picking_mode(on_picked=self._on_point_picked)
        except Exception as exc:
            QMessageBox.critical(self, "Pick Error", f"Could not activate picking:\n{exc}")
            self._picking_target = None
            self._start_pick_btn.setEnabled(True)
            self._end_pick_btn.setEnabled(True)

    def _on_point_picked(self, result: dict) -> None:
        """
        Callback invoked when the user picks a point in the 3D view.

        Parameters
        ----------
        result : dict
            Dictionary with at least a ``'coordinates'`` key containing the
            world-space ``(x, y, z)`` tuple of the picked point.
        """
        try:
            coords = result.get("coordinates")
            if coords is None:
                return

            coord_str = f"{coords[0]:.6g}, {coords[1]:.6g}, {coords[2]:.6g}"

            if self._picking_target == "start":
                self._start_edit.setText(coord_str)
            elif self._picking_target == "end":
                self._end_edit.setText(coord_str)
        finally:
            self._picking_target = None
            self._start_pick_btn.setEnabled(True)
            self._end_pick_btn.setEnabled(True)
            try:
                self._plotter_window.disable_point_picking_mode(render=False)
            except Exception:
                pass
            # Bring this dialog back to the front so the user can continue.
            self.raise_()
            self.activateWindow()

    def _disable_picking_if_active(self) -> None:
        """Disable point-picking mode if this dialog was closed while picking."""
        if self._picking_target is not None:
            self._picking_target = None
            try:
                self._plotter_window.disable_point_picking_mode(render=False)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Accept / close
    # ------------------------------------------------------------------

    def _on_accept(self) -> None:
        """Validate inputs and accept the dialog."""
        start = _parse_xyz(self._start_edit.text())
        if start is None:
            QMessageBox.warning(self, "Invalid Input", "Start point must be in 'x, y, z' format.")
            return

        end = _parse_xyz(self._end_edit.text())
        if end is None:
            QMessageBox.warning(self, "Invalid Input", "End point must be in 'x, y, z' format.")
            return

        self._result_data = (start, end, self._resolution_spin.value())
        self.accept()

    def closeEvent(self, event) -> None:
        """Ensure picking is disabled when the dialog is closed."""
        self._disable_picking_if_active()
        super().closeEvent(event)

    def result_data(self) -> tuple[tuple[float, float, float], tuple[float, float, float], int] | None:
        """
        Return the parsed line definition after the dialog was accepted.

        Returns
        -------
        tuple or None
            ``(start, end, resolution)`` if the dialog was accepted, else ``None``.
        """
        return getattr(self, "_result_data", None)


# ---------------------------------------------------------------------------
# SampleLinesDialog
# ---------------------------------------------------------------------------


class SampleLinesDialog(QDialog):
    """
    Dialog for defining sample lines and running sampling queries.

    Provides a split-panel interface: left panel holds the line table and controls;
    right panel hosts a tab widget for future results.

    Parameters
    ----------
    plotter : QtInteractor
        The PyVista plotter instance for 3D visualization.
    plotter_window : QtPlotterWindow
        Reference to the parent plotter window.
    """

    def __init__(
        self,
        plotter: "QtInteractor",
        plotter_window: "QtPlotterWindow",
    ) -> None:
        super().__init__(plotter_window._window)
        self.plotter = plotter
        self._plotter_window = plotter_window

        # Internal state
        # Each entry: (start, end, resolution) where start/end are (x, y, z) float tuples
        self._lines: list[tuple[tuple[float, float, float], tuple[float, float, float], int]] = []
        # Mapping from line index to actor name for 3D visualization
        self._line_actor_names: dict[int, str] = {}
        # Monotonically increasing counter for stable actor names
        self._line_counter: int = 0
        # Reference to the open AddLineDialog, if any
        self._active_add_line_dlg: AddLineDialog | None = None

        self.setWindowTitle("Sample Lines")
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint
        )
        self.resize(900, 550)

        self._create_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _create_ui(self) -> None:
        """Create the dialog UI with split-panel layout."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = self._create_left_panel()
        splitter.addWidget(left_widget)

        right_widget = self._create_right_panel()
        splitter.addWidget(right_widget)

        splitter.setSizes([320, 580])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def _create_left_panel(self) -> QWidget:
        """
        Create the left panel with the line table and control buttons.

        Returns
        -------
        QWidget
            The left panel widget.
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # "Add New Line" at the top
        self._add_line_button = QPushButton("Add New Line")
        self._add_line_button.clicked.connect(self._on_add_line)
        left_layout.addWidget(self._add_line_button)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["#", "Start", "End", "Resolution"])
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.itemSelectionChanged.connect(self._update_button_states)
        self._table.cellDoubleClicked.connect(self._on_edit_selected_by_row)
        left_layout.addWidget(self._table)

        # Bottom buttons
        button_layout = QHBoxLayout()

        self._run_button = QPushButton("Run Sampling")
        self._run_button.setEnabled(False)
        self._run_button.clicked.connect(self._on_run_sampling)
        button_layout.addWidget(self._run_button)

        self._edit_button = QPushButton("Edit Selected")
        self._edit_button.setEnabled(False)
        self._edit_button.clicked.connect(self._on_edit_selected)
        button_layout.addWidget(self._edit_button)

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
        Create the right panel with a tab widget and placeholder content.

        Returns
        -------
        QWidget
            The right panel widget.
        """
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        self._results_tab_widget = QTabWidget()

        # Placeholder label
        placeholder = QLabel("Run sampling to see results.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._results_tab_widget.addTab(placeholder, "Results")

        right_layout.addWidget(self._results_tab_widget)
        right_widget.setLayout(right_layout)
        return right_widget

    # ------------------------------------------------------------------
    # 3D visualization helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fmt_xyz(pt: tuple[float, float, float]) -> str:
        """Format a 3D point as a compact string."""
        return f"({pt[0]:.4g}, {pt[1]:.4g}, {pt[2]:.4g})"

    def _add_line_visualization(
        self,
        line_idx: int,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        row_number: int | None = None,
    ) -> None:
        """Add a 3D line actor and label for the given line entry."""
        actor_name = f"sample_line_viz_{line_idx}"
        label_name = f"sample_line_label_{line_idx}"
        try:
            line_mesh = pv.Line(start, end)
            self.plotter.add_mesh(
                line_mesh,
                color="cyan",
                line_width=3,
                pickable=False,
                name=actor_name,
            )
            self._line_actor_names[line_idx] = actor_name

            # Add a label at the midpoint showing the table row number.
            if row_number is None:
                # Derive row number from current table state.
                row_number = self._table.rowCount()  # will be 1-based after insertion
            midpoint = [
                (start[0] + end[0]) / 2,
                (start[1] + end[1]) / 2,
                (start[2] + end[2]) / 2,
            ]
            self.plotter.add_point_labels(
                [midpoint],
                [str(row_number)],
                font_size=16,
                text_color="white",
                show_points=False,
                always_visible=True,
                shadow=True,
                shape="rounded_rect",
                fill_shape=True,
                shape_color="black",
                shape_opacity=0.7,
                name=label_name,
            )

            self.plotter.render()
        except Exception as exc:
            QMessageBox.warning(self, "Visualization Error", f"Could not draw line {line_idx}:\n{exc}")

    def _remove_line_visualization(self, line_idx: int, render: bool = True) -> None:
        """Remove the 3D actor and label for the given line entry if it exists."""
        actor_name = self._line_actor_names.pop(line_idx, None)
        if actor_name is None:
            return
        try:
            self.plotter.remove_actor(actor_name, render=False)
            self.plotter.remove_actor(f"sample_line_label_{line_idx}", render=False)
            if render:
                self.plotter.render()
        except Exception:
            pass

    def _remove_all_visualizations(self, render: bool = True) -> None:
        """Remove all 3D line actors and labels."""
        self.plotter.suppress_rendering = True
        for idx in list(self._line_actor_names.keys()):
            actor_name = self._line_actor_names.pop(idx)
            try:
                self.plotter.remove_actor(actor_name, render=False)
                self.plotter.remove_actor(f"sample_line_label_{idx}", render=False)
            except Exception:
                pass
        self.plotter.suppress_rendering = False
        if render:
            try:
                self.plotter.render()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Slot: Add Line
    # ------------------------------------------------------------------

    def _on_add_line(self) -> None:
        """Open AddLineDialog (non-modal) and wire accepted/rejected signals."""
        # Keep a reference so the dialog isn't garbage-collected.
        self._active_add_line_dlg = AddLineDialog(plotter_window=self._plotter_window, parent=self)
        self._active_add_line_dlg.accepted.connect(self._on_add_line_accepted)
        self._active_add_line_dlg.rejected.connect(self._on_add_line_rejected)
        self._active_add_line_dlg.show()
        self._active_add_line_dlg.raise_()
        self._active_add_line_dlg.activateWindow()
        # Disable the button while the sub-dialog is open to avoid duplicates.
        self._add_line_button.setEnabled(False)

    def _on_add_line_accepted(self) -> None:
        """Handle acceptance of the AddLineDialog."""
        dlg: AddLineDialog | None = getattr(self, "_active_add_line_dlg", None)
        self._add_line_button.setEnabled(True)
        if dlg is None:
            return

        data = dlg.result_data()
        self._active_add_line_dlg = None
        if data is None:
            return

        start, end, resolution = data

        # Use a monotonic counter so actor names remain unique after removals.
        line_idx = self._line_counter
        self._line_counter += 1

        self._lines.append((start, end, resolution))

        # Add table row.
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self._table.setItem(row, 1, QTableWidgetItem(self._fmt_xyz(start)))
        self._table.setItem(row, 2, QTableWidgetItem(self._fmt_xyz(end)))
        self._table.setItem(row, 3, QTableWidgetItem(str(resolution)))
        # Store line_idx in the first column item for later actor lookup.
        self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, line_idx)

        # Visualize in 3D.
        self._add_line_visualization(line_idx, start, end, row_number=row + 1)

        self._update_button_states()

    def _on_add_line_rejected(self) -> None:
        """Handle rejection/close of the AddLineDialog."""
        self._active_add_line_dlg = None
        self._add_line_button.setEnabled(True)
        self._update_button_states()

    # ------------------------------------------------------------------
    # Button state helper
    # ------------------------------------------------------------------

    def _update_button_states(self) -> None:
        """Enable/disable action buttons based on table selection and dialog state."""
        row_count = self._table.rowCount()
        selected_rows = self._table.selectionModel().selectedRows()
        sub_dialog_open = self._active_add_line_dlg is not None

        self._run_button.setEnabled(row_count > 0)
        self._edit_button.setEnabled(len(selected_rows) == 1 and not sub_dialog_open)

    # ------------------------------------------------------------------
    # Slot: Edit Line
    # ------------------------------------------------------------------

    def _on_edit_selected(self) -> None:
        """Open AddLineDialog pre-filled for the currently selected row."""
        selected_rows = self._table.selectionModel().selectedRows()
        if len(selected_rows) != 1:
            return
        row = selected_rows[0].row()
        self._open_edit_dialog_for_row(row)

    def _on_edit_selected_by_row(self, row: int, _col: int) -> None:
        """Handle double-click on a table row — open the edit dialog for that row."""
        self._open_edit_dialog_for_row(row)

    def _open_edit_dialog_for_row(self, row: int) -> None:
        """Open AddLineDialog pre-filled with the values for *row*."""
        if self._active_add_line_dlg is not None:
            # A sub-dialog is already open; bring it to front instead.
            self._active_add_line_dlg.raise_()
            self._active_add_line_dlg.activateWindow()
            return

        list_pos = row  # row index == list index (removes renumber both)
        if list_pos < 0 or list_pos >= len(self._lines):
            return

        line_idx = self._table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        dlg = AddLineDialog(
            plotter_window=self._plotter_window,
            parent=self,
            initial_values=self._lines[list_pos],
        )
        self._active_add_line_dlg = dlg
        dlg.accepted.connect(lambda: self._on_edit_line_accepted(row, list_pos, line_idx, dlg))
        dlg.rejected.connect(self._on_edit_line_rejected)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()
        self._add_line_button.setEnabled(False)
        self._edit_button.setEnabled(False)

    def _on_edit_line_rejected(self) -> None:
        """Handle rejection/close of the edit AddLineDialog."""
        self._active_add_line_dlg = None
        self._add_line_button.setEnabled(True)
        self._update_button_states()

    def _on_edit_line_accepted(
        self,
        row: int,
        list_pos: int,
        line_idx: int,
        dlg: "AddLineDialog",
    ) -> None:
        """Apply edits from the dialog back to the table, data model, and 3D view."""
        self._active_add_line_dlg = None
        self._add_line_button.setEnabled(True)

        data = dlg.result_data()
        if data is None:
            self._update_button_states()
            return

        new_start, new_end, new_resolution = data

        # Update internal data model.
        self._lines[list_pos] = (new_start, new_end, new_resolution)

        # Refresh table cells (columns 1-3; column 0 keeps its index / UserRole).
        self._table.item(row, 1).setText(self._fmt_xyz(new_start))
        self._table.item(row, 2).setText(self._fmt_xyz(new_end))
        self._table.item(row, 3).setText(str(new_resolution))

        # Update 3D visualization: remove old actor, re-add with same name.
        self._remove_line_visualization(line_idx, render=False)
        self._add_line_visualization(line_idx, new_start, new_end, row_number=row + 1)

        # Mark any existing result tabs for this line as stale.
        line_label = f"Line {row + 1}"
        stale_suffix = " [stale]"
        for top_idx in range(self._results_tab_widget.count()):
            top_tab = self._results_tab_widget.widget(top_idx)
            if isinstance(top_tab, QTabWidget):
                for sub_idx in range(top_tab.count()):
                    if top_tab.tabText(sub_idx) == line_label:
                        top_tab.setTabText(sub_idx, line_label + stale_suffix)

        self._update_button_states()

    # ------------------------------------------------------------------
    # Slot: Run Sampling
    # ------------------------------------------------------------------

    def _on_run_sampling(self) -> None:
        """Call Plotter.sample_lines for all defined lines and display results."""
        if not self._lines:
            return

        if self._plotter_window.parent_plotter is None:
            QMessageBox.warning(self, "Sampling Error", "Parent plotter is not available.")
            return

        self._run_button.setEnabled(False)
        progress_dialog = None

        try:
            # Unpack parallel lists
            starts = [line[0] for line in self._lines]
            ends = [line[1] for line in self._lines]
            resolutions = [line[2] for line in self._lines]

            # Create progress dialog
            progress_dialog = QProgressDialog(
                "Preparing to sample lines...",
                "Cancel",
                0,
                100,
                self,
            )
            progress_dialog.setWindowTitle("Sampling Lines")
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setMinimumDuration(500)
            progress_dialog.setValue(0)

            def update_progress(current: int, total: int) -> bool:
                """Update progress dialog; return False to request cancellation."""
                if total > 0:
                    percentage = int((current / total) * 100)
                    progress_dialog.setValue(percentage)
                    progress_dialog.setLabelText(f"Sampling lines... ({current}/{total})")
                QApplication.processEvents()
                return not progress_dialog.wasCanceled()

            results = self._plotter_window.parent_plotter.sample_lines(
                list(zip(starts, ends)),
                resolutions,
                progress_callback=update_progress,
            )

            progress_dialog.close()

            if not results and progress_dialog.wasCanceled():
                QMessageBox.information(self, "Sampling Cancelled", "Line sampling was cancelled by user.")
                return

            # Populate right panel
            self._populate_results(results)

        except Exception as exc:
            QMessageBox.critical(self, "Sampling Error", f"Failed to sample lines:\n{exc}")
        finally:
            if progress_dialog is not None:
                progress_dialog.close()
                progress_dialog.deleteLater()
            self._run_button.setEnabled(len(self._lines) > 0)

    # ------------------------------------------------------------------
    # Results population
    # ------------------------------------------------------------------

    def _populate_results(self, results) -> None:
        """
        Populate the right-panel tab widget with sampling results.

        Creates a nested tab hierarchy:

        - **Data tab** — top-level tab for all results.
          - **Line tabs** (``Line 1``, ``Line 2``, …) — one per sampled line.
            - **Array tabs** (``B-Mag (T)``, ``Temperature``, …) — one per data
              array found in the first time-step dictionary.
              - **Sub-key tabs** (``value``, ``distance``, ``x``, …) — one per
                entry inside the array dictionary.
                - **QTableWidget** — rows = time steps, columns = sample points.

        Parameters
        ----------
        results : list[list[dict]]
            The value returned by ``Plotter.sample_lines``.  Outer list is per
            line, inner list is per time step.  Each dict has a ``"time"`` key
            and one key per data array whose value is a sub-dict of equal-length
            lists (e.g. ``"distance"``, ``"value"``, ``"x"``, ``"y"``, ``"z"``
            for scalars).
        """
        # Clear existing tabs
        self._results_tab_widget.clear()

        if not results:
            placeholder = QLabel("No results returned.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._results_tab_widget.addTab(placeholder, "Results")
            return

        # Outer "Data" tab containing per-line sub-tabs
        line_tabs = QTabWidget()
        for line_idx, line_time_steps in enumerate(results):
            line_tab = self._build_line_tab(line_time_steps)
            line_tabs.addTab(line_tab, f"Line {line_idx + 1}")

        self._results_tab_widget.addTab(line_tabs, "Data")

        # "3D Surface" tab — same line hierarchy but matplotlib plot_surface leaves
        surface_line_tabs = QTabWidget()
        for line_idx, line_time_steps in enumerate(results):
            surface_line_tab = self._build_surface_line_tab(line_time_steps)
            surface_line_tabs.addTab(surface_line_tab, f"Line {line_idx + 1}")
        self._results_tab_widget.addTab(surface_line_tabs, "3D Surface")

        # "Heatmap" tab — same line hierarchy but matplotlib imshow leaves
        heatmap_line_tabs = QTabWidget()
        for line_idx, line_time_steps in enumerate(results):
            heatmap_line_tab = self._build_heatmap_line_tab(line_time_steps)
            heatmap_line_tabs.addTab(heatmap_line_tab, f"Line {line_idx + 1}")
        self._results_tab_widget.addTab(heatmap_line_tabs, "Heatmap")

    # ------------------------------------------------------------------
    # Result-tab builders
    # ------------------------------------------------------------------

    def _build_line_tab(self, line_time_steps: list[dict]) -> QWidget:
        """Build the array-level tab widget for a single line.

        Parameters
        ----------
        line_time_steps : list[dict]
            One dict per time step with ``"time"`` and array-name keys.

        Returns
        -------
        QWidget
            A widget containing a ``QTabWidget`` with one tab per array.
        """
        if not line_time_steps:
            lbl = QLabel("No time-step data.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        first_step = line_time_steps[0]
        array_names = [k for k in first_step if k != "time"]

        if not array_names:
            lbl = QLabel("No data arrays in result.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        array_tabs = QTabWidget()
        for array_name in array_names:
            sub_widget = self._build_array_tab(line_time_steps, array_name)
            array_tabs.addTab(sub_widget, array_name)

        return array_tabs

    def _build_array_tab(self, line_time_steps: list[dict], array_name: str) -> QWidget:
        """Build the sub-key-level tab widget for one data array.

        Parameters
        ----------
        line_time_steps : list[dict]
            Full time-step list for the line.
        array_name : str
            The array key (e.g. ``"B-Mag (T)"``).

        Returns
        -------
        QWidget
            A ``QTabWidget`` with one tab per sub-key.
        """
        first_array = line_time_steps[0].get(array_name, {})
        sub_keys = list(first_array.keys())

        if not sub_keys:
            lbl = QLabel(f"No sub-keys for '{array_name}'.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        sub_tabs = QTabWidget()
        for sub_key in sub_keys:
            table = self._build_data_table(line_time_steps, array_name, sub_key)
            sub_tabs.addTab(table, sub_key)

        return sub_tabs

    def _build_data_table(
        self,
        line_time_steps: list[dict],
        array_name: str,
        sub_key: str,
    ) -> QTableWidget:
        """Build a table for one sub-key of one array.

        Rows correspond to time steps and columns to sample points along the
        line.

        Parameters
        ----------
        line_time_steps : list[dict]
            Full time-step list for the line.
        array_name : str
            Data-array key.
        sub_key : str
            Sub-key inside the array dict (e.g. ``"value"``).

        Returns
        -------
        QTableWidget
        """
        n_times = len(line_time_steps)
        # Determine number of sample points from the first time step
        sample_data = line_time_steps[0].get(array_name, {}).get(sub_key, [])
        n_points = len(sample_data)

        table = QTableWidget(n_times, n_points)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

        # Horizontal header: point indices
        table.setHorizontalHeaderLabels([str(j) for j in range(n_points)])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.horizontalHeader().setDefaultSectionSize(80)

        # Vertical header: time values
        time_labels = [f"{ts.get('time', 0.0):.6g}" for ts in line_time_steps]
        table.setVerticalHeaderLabels(time_labels)

        # Populate cells — suppress UI updates for performance
        table.setUpdatesEnabled(False)
        try:
            for t_idx, ts in enumerate(line_time_steps):
                values = ts.get(array_name, {}).get(sub_key, [])
                for p_idx, val in enumerate(values):
                    item = QTableWidgetItem(f"{val:.6g}" if isinstance(val, (int, float)) else str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    table.setItem(t_idx, p_idx, item)
        finally:
            table.setUpdatesEnabled(True)

        return table

    # ------------------------------------------------------------------
    # 3D Surface tab builders
    # ------------------------------------------------------------------

    # Spatial / axis sub-keys that are excluded from the 3D Surface tabs.
    # "distance" is always the X-axis; "x", "y", "z" are sample-point coords.
    _SURFACE_EXCLUDED_SUBKEYS: frozenset[str] = frozenset({"distance", "x", "y", "z"})

    def _build_surface_line_tab(self, line_time_steps: list[dict]) -> QWidget:
        """Build the array-level tab widget for the 3D Surface view of one line.

        Parameters
        ----------
        line_time_steps : list[dict]
            One dict per time step with ``"time"`` and array-name keys.

        Returns
        -------
        QWidget
            A ``QTabWidget`` with one tab per data array.
        """
        if not line_time_steps:
            lbl = QLabel("No time-step data.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        first_step = line_time_steps[0]
        array_names = [k for k in first_step if k != "time"]

        if not array_names:
            lbl = QLabel("No data arrays in result.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        array_tabs = QTabWidget()
        for array_name in array_names:
            sub_widget = self._build_surface_array_tab(line_time_steps, array_name)
            array_tabs.addTab(sub_widget, array_name)

        return array_tabs

    def _build_surface_array_tab(self, line_time_steps: list[dict], array_name: str) -> QWidget:
        """Build the sub-key-level tab widget for the 3D Surface view of one array.

        Excludes ``"distance"``, ``"x"``, ``"y"``, ``"z"`` sub-keys because distance
        is the X-axis of the surface and the coordinate keys are not field values.

        Parameters
        ----------
        line_time_steps : list[dict]
            Full time-step list for the line.
        array_name : str
            The array key (e.g. ``"B-Mag (T)"``).

        Returns
        -------
        QWidget
            A ``QTabWidget`` with one surface-plot tab per plottable sub-key.
        """
        first_array = line_time_steps[0].get(array_name, {})
        if not first_array.get("distance"):
            lbl = QLabel("Distance data unavailable.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        sub_keys = [k for k in first_array if k not in self._SURFACE_EXCLUDED_SUBKEYS]

        if not sub_keys:
            lbl = QLabel(f"No plottable sub-keys for '{array_name}'.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        sub_tabs = QTabWidget()
        for sub_key in sub_keys:
            plot_widget = self._build_surface_plot(line_time_steps, array_name, sub_key)
            sub_tabs.addTab(plot_widget, sub_key)

        return sub_tabs

    def _build_surface_plot(
        self,
        line_time_steps: list[dict],
        array_name: str,
        sub_key: str,
    ) -> QWidget:
        """Build a matplotlib 3D surface (or 2D line fallback) widget.

        For datasets with more than one time step the method renders a
        ``plot_surface`` with:

        - **X** — distance along the sample line
        - **Y** — time value
        - **Z** — sampled field value (``sub_key``)

        For static datasets (single time step) a 2D ``ax.plot`` fallback is
        shown instead because a 1-row surface is degenerate.

        The Z-axis label follows decision C: the array name alone when
        ``sub_key == "value"``, otherwise ``"{array_name} - {sub_key}"``.

        Parameters
        ----------
        line_time_steps : list[dict]
            Full time-step list for the line.
        array_name : str
            Data-array key.
        sub_key : str
            Sub-key inside the array dict (e.g. ``"value"``, ``"tangential"``).

        Returns
        -------
        QWidget
            A widget containing a ``NavigationToolbar`` and a
            ``FigureCanvas`` with the rendered plot.
        """
        z_label = array_name if sub_key == "value" else f"{array_name} - {sub_key}"

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        fig = Figure(figsize=(10, 6))
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, widget)

        try:
            distances = line_time_steps[0][array_name]["distance"]
            times = [ts["time"] for ts in line_time_steps]
            values = [ts.get(array_name, {}).get(sub_key, []) for ts in line_time_steps]

            if len(line_time_steps) == 1:
                # --- 2D line fallback for static (single time step) datasets ---
                ax = fig.add_subplot(111)
                ax.plot(distances, values[0])
                ax.set_xlabel("Distance")
                ax.set_ylabel(z_label)
                ax.set_title(f"{z_label} (static)")
                ax.grid(True)
            else:
                # --- 3D surface for temporal datasets ---
                Z = np.array(values)  # shape (n_times, n_points)
                X, Y = np.meshgrid(distances, times)  # X=distance, Y=time

                ax = fig.add_subplot(111, projection="3d")
                ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none")
                ax.set_xlabel("Distance")
                ax.set_ylabel("Time")
                ax.set_zlabel(z_label)
                ax.set_title(z_label)

        except Exception as exc:  # noqa: BLE001
            fig.clear()
            ax = fig.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                f"Could not render surface:\n{exc}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.axis("off")

        fig.tight_layout()

        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget

    # ------------------------------------------------------------------
    # Heatmap tab builders
    # ------------------------------------------------------------------

    def _build_heatmap_line_tab(self, line_time_steps: list[dict]) -> QWidget:
        """Build the array-level tab widget for the Heatmap view of one line.

        Parameters
        ----------
        line_time_steps : list[dict]
            One dict per time step with ``"time"`` and array-name keys.

        Returns
        -------
        QWidget
            A ``QTabWidget`` with one tab per data array.
        """
        if not line_time_steps:
            lbl = QLabel("No time-step data.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        array_names = [k for k in line_time_steps[0] if k != "time"]

        if not array_names:
            lbl = QLabel("No data arrays in result.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        array_tabs = QTabWidget()
        for array_name in array_names:
            array_tabs.addTab(self._build_heatmap_array_tab(line_time_steps, array_name), array_name)
        return array_tabs

    def _build_heatmap_array_tab(self, line_time_steps: list[dict], array_name: str) -> QWidget:
        """Build the sub-key-level tab widget for the Heatmap view of one array.

        Excludes ``"distance"``, ``"x"``, ``"y"``, ``"z"`` sub-keys (same policy
        as the 3D Surface tab).

        Parameters
        ----------
        line_time_steps : list[dict]
            Full time-step list for the line.
        array_name : str
            The array key (e.g. ``"B-Mag (T)"``).

        Returns
        -------
        QWidget
            A ``QTabWidget`` with one heatmap tab per plottable sub-key.
        """
        first_array = line_time_steps[0].get(array_name, {})
        if not first_array.get("distance"):
            lbl = QLabel("Distance data unavailable.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        sub_keys = [k for k in first_array if k not in self._SURFACE_EXCLUDED_SUBKEYS]

        if not sub_keys:
            lbl = QLabel(f"No plottable sub-keys for '{array_name}'.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        sub_tabs = QTabWidget()
        for sub_key in sub_keys:
            sub_tabs.addTab(self._build_heatmap_plot(line_time_steps, array_name, sub_key), sub_key)
        return sub_tabs

    def _build_heatmap_plot(
        self,
        line_time_steps: list[dict],
        array_name: str,
        sub_key: str,
    ) -> QWidget:
        """Build a matplotlib ``imshow`` heatmap widget.

        Renders a 2-D image where:

        - **X axis (columns)** — distance along the sample line
        - **Y axis (rows)**    — time value
        - **colour**           — sampled field value (``sub_key``)

        Works for both temporal (multiple time steps) and static (single time
        step, displayed as a 1-row image) datasets.

        The colour-bar label follows decision C: the array name alone when
        ``sub_key == "value"``, otherwise ``"{array_name} - {sub_key}"``.

        Parameters
        ----------
        line_time_steps : list[dict]
            Full time-step list for the line.
        array_name : str
            Data-array key.
        sub_key : str
            Sub-key inside the array dict (e.g. ``"value"``, ``"tangential"``).

        Returns
        -------
        QWidget
            A widget containing a ``NavigationToolbar`` and a
            ``FigureCanvas`` with the rendered heatmap.
        """
        z_label = array_name if sub_key == "value" else f"{array_name} - {sub_key}"

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        fig = Figure(figsize=(10, 6))
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, widget)

        try:
            distances = line_time_steps[0][array_name]["distance"]
            times = [ts["time"] for ts in line_time_steps]
            Z = np.array(
                [ts.get(array_name, {}).get(sub_key, []) for ts in line_time_steps]
            )  # shape (n_times, n_points)

            ax = fig.add_subplot(111)

            # extent: [left, right, bottom, top] maps pixel axes to data coords
            # so the toolbar cursor readout shows real distance / time values.
            extent = [distances[0], distances[-1], times[0], times[-1]]
            im = ax.imshow(
                Z,
                aspect="auto",
                origin="lower",
                extent=extent,
                cmap="viridis",
                interpolation="nearest",
            )
            fig.colorbar(im, ax=ax, label=z_label)
            ax.set_xlabel("Distance")
            ax.set_ylabel("Time")
            ax.set_title(z_label)

        except Exception as exc:  # noqa: BLE001
            fig.clear()
            ax = fig.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                f"Could not render heatmap:\n{exc}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.axis("off")

        fig.tight_layout()

        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget

    # ------------------------------------------------------------------
    # Slot: Remove Selected
    # ------------------------------------------------------------------

    def _on_remove_selected(self) -> None:
        """Remove selected rows from the table, internal list, and 3D view."""
        selected_rows = sorted(
            {index.row() for index in self._table.selectedIndexes()},
            reverse=True,
        )
        if not selected_rows:
            return

        self.plotter.suppress_rendering = True

        for row in selected_rows:
            self._table.removeRow(row)
            if row < len(self._lines):
                del self._lines[row]

        # Renumber the "#" column
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item is not None:
                item.setText(str(row + 1))

        self.plotter.suppress_rendering = False
        self.plotter.render()

        self._remove_all_visualizations(render=False)
        self._restore_visualizations()

        self._run_button.setEnabled(len(self._lines) > 0)

    # ------------------------------------------------------------------
    # Slot: Clear
    # ------------------------------------------------------------------

    def _on_clear(self) -> None:
        """Remove all lines, their visualizations, and reset state."""
        self._remove_all_visualizations(render=False)

        self._lines.clear()
        self._table.setRowCount(0)

        # Reset results panel to placeholder
        self._results_tab_widget.clear()
        placeholder = QLabel("Run sampling to see results.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._results_tab_widget.addTab(placeholder, "Results")

        try:
            self.plotter.render()
        except Exception:
            pass

        self._run_button.setEnabled(False)

    # ------------------------------------------------------------------
    # Restore visualizations (called when dialog is reopened)
    # ------------------------------------------------------------------

    def _restore_visualizations(self) -> None:
        """Re-draw 3D actors for all current lines (called after dialog reopen)."""
        if not self._lines:
            return

        self.plotter.suppress_rendering = True

        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item is None:
                continue
            line_idx = item.data(Qt.ItemDataRole.UserRole)
            if line_idx is None or line_idx in self._line_actor_names:
                continue
            if row < len(self._lines):
                start, end, _ = self._lines[row]
                actor_name = f"sample_line_viz_{line_idx}"
                label_name = f"sample_line_label_{line_idx}"
                row_number = row + 1
                try:
                    line_mesh = pv.Line(start, end)
                    self.plotter.add_mesh(
                        line_mesh,
                        color="cyan",
                        line_width=3,
                        pickable=False,
                        name=actor_name,
                    )
                    self._line_actor_names[line_idx] = actor_name

                    # Add label at line midpoint showing the table row number.
                    midpoint = [
                        (start[0] + end[0]) / 2,
                        (start[1] + end[1]) / 2,
                        (start[2] + end[2]) / 2,
                    ]
                    self.plotter.add_point_labels(
                        [midpoint],
                        [str(row_number)],
                        font_size=16,
                        text_color="white",
                        show_points=False,
                        always_visible=True,
                        shadow=True,
                        shape="rounded_rect",
                        fill_shape=True,
                        shape_color="black",
                        shape_opacity=0.7,
                        name=label_name,
                    )
                except Exception:
                    pass

        self.plotter.suppress_rendering = False
        self.plotter.render()

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        """Remove all 3D line actors when the dialog is closed."""
        self._remove_all_visualizations(render=True)
        super().closeEvent(event)
