"""
Pick Result History Dialog for PyVista visualization.

Provides a simple history window to display picked point and cell results
with monospace formatting and clear functionality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit
    from PySide6.QtGui import QFont, QCloseEvent
    from pyemsi.qt_window import QtPlotterWindow

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit
from PySide6.QtGui import QFont


class PickResultHistoryDialog(QDialog):
    """
    Dialog for displaying pick result history.

    Provides a simple text display window with monospace font that shows
    accumulated point and cell pick results. Results are appended incrementally
    and can be cleared with a button.

    Parameters
    ----------
    parent_window : QtPlotterWindow
        Reference to the parent QtPlotterWindow instance.
    """

    # Type annotations for instance attributes
    _parent_window: "QtPlotterWindow"
    _text_widget: "QPlainTextEdit"
    _clear_button: "QPushButton"

    def __init__(self, parent_window: "QtPlotterWindow"):
        """
        Initialize pick result history dialog.

        Parameters
        ----------
        parent_window : QtPlotterWindow
            Reference to the parent QtPlotterWindow instance.
        """
        self._parent_window = parent_window
        super().__init__(parent_window._window)

        # Configure dialog
        self.setWindowTitle("Pick Result History")
        self.setModal(False)  # Non-blocking dialog
        self.resize(500, 400)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create text display widget with monospace font
        self._text_widget = QPlainTextEdit()
        self._text_widget.setReadOnly(True)
        monospace_font = QFont("Courier", 10)
        self._text_widget.setFont(monospace_font)
        main_layout.addWidget(self._text_widget)

        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push button to the right

        # Create Clear button
        self._clear_button = QPushButton("Clear")
        self._clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(self._clear_button)

        main_layout.addLayout(button_layout)

    def append_result(self, result_type: str, result_dict: dict) -> None:
        """
        Append a pick result to the history.

        Formats the result based on type (Point or Cell) and appends it
        to the text display in a compact, monospace-friendly format.

        Parameters
        ----------
        result_type : str
            Either "Point" or "Cell" to indicate the type of result.
        result_dict : dict
            Dictionary containing pick result data. Expected keys:
            - For Point: "point_id", "block_name", "coordinates"
            - For Cell: "cell_id", "block_name", "coordinates"
        """
        if result_type == "Point":
            point_id = result_dict.get("point_id", "?")
            block_name = result_dict.get("block_name")
            coordinates = result_dict.get("coordinates", (0, 0, 0))

            # Format block name
            block_str = f'"{block_name}"' if block_name is not None else "None"

            # Format coordinates with 2 decimal places
            coord_str = f"({coordinates[0]:.2f}, {coordinates[1]:.2f}, {coordinates[2]:.2f})"

            # Build result line
            result_line = f"Point #{point_id} Block: #{block_str}\n  - Coords: {coord_str}"

            for array_name, array_value in result_dict["highlight_mesh"].point_data.items():
                result_line += f"\n- {array_name}: {array_value}"

        elif result_type == "Cell":
            cell_id = result_dict.get("cell_id", "?")
            block_name = result_dict.get("block_name")
            coordinates = result_dict.get("coordinates", (0, 0, 0))
            area = result_dict["highlight_mesh"].area

            # Format block name
            block_str = f'"{block_name}"' if block_name is not None else "None"

            # Format coordinates with 2 decimal places
            coord_str = f"({coordinates[0]:.2f}, {coordinates[1]:.2f}, {coordinates[2]:.2f})"

            # Build result line
            result_line = f"[Cell #{cell_id}] Block: {block_str}\n- Area: {area}"

            for array_name, array_value in result_dict["highlight_mesh"].cell_data.items():
                result_line += f"\n- {array_name}: {array_value}"

        else:
            result_line = f"[Unknown] {result_dict}"

        result_line += "\n"
        result_line += "-" * 40

        # Append to text widget
        self._text_widget.appendPlainText(result_line)

    def clear_history(self) -> None:
        """
        Clear all text from the history display.

        This does not affect the toggle state or picking mode state.
        """
        self._text_widget.clear()

    def closeEvent(self, event: "QCloseEvent") -> None:
        """
        Handle dialog close event.

        Notifies the parent window that the dialog was closed so it can
        update toggle button states and disable picking modes.

        Parameters
        ----------
        event : QCloseEvent
            The close event.
        """
        # Notify parent window of closure
        if hasattr(self._parent_window, "_on_pick_history_dialog_closed"):
            self._parent_window._on_pick_history_dialog_closed()

        # Accept the close event
        event.accept()
