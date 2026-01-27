"""Block visibility dialog for controlling individual block visibility in multi-block meshes."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyvistaqt import QtInteractor

import pyvista as pv
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from .property_tree_widget import PropertyTreeWidget


class BlockVisibilityDialog(QDialog):
    """
    Dialog for controlling visibility of individual blocks in multi-block meshes.

    Provides a PropertyTreeWidget with checkboxes for each block, allowing real-time
    toggling of block visibility. Changes are applied immediately as checkboxes are
    toggled, with Ok, Apply, and Cancel buttons for dialog control.

    Parameters
    ----------
    plotter : QtInteractor | pv.Plotter
        The PyVista plotter instance to configure.
    plotter_window : QtPlotterWindow
        The parent Qt window that owns this dialog.

    Attributes
    ----------
    plotter : QtInteractor | pv.Plotter
        Reference to the plotter instance.
    plotter_window : QtPlotterWindow
        Reference to the parent window.
    tree : PropertyTreeWidget
        The property tree widget for block visibility checkboxes.
    initial_block_visibility : dict
        Initial visibility state of each block for restore on Cancel.
    """

    def __init__(self, plotter: "QtInteractor | pv.Plotter", plotter_window="QtPlotterWindow"):
        """
        Initialize the block visibility dialog.

        Parameters
        ----------
        plotter : QtInteractor | pv.Plotter
            The PyVista plotter instance to configure.
        plotter_window : QtPlotterWindow
            The parent Qt window.
        """
        self.plotter_window = plotter_window
        super().__init__(plotter_window._window)

        # Store plotter reference
        self.plotter = plotter

        # Configure dialog
        self.setWindowTitle("Block Visibility")
        self.setWindowIcon(QIcon(":/icons/Settings.svg"))
        self.setModal(False)  # Non-blocking dialog
        self.resize(400, 500)

        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create PropertyTreeWidget
        self.tree = PropertyTreeWidget()
        layout.addWidget(self.tree)

        # Create button box with Ok, Apply, Cancel
        self.button_box = QDialogButtonBox()

        # Add individual buttons
        self.ok_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.apply_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Apply)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)

        # Disable Apply button since changes are immediate
        self.apply_button.setEnabled(False)

        # Connect button signals
        self.ok_button.clicked.connect(self._on_ok)
        self.apply_button.clicked.connect(self._on_apply)
        self.cancel_button.clicked.connect(self._on_cancel)

        layout.addWidget(self.button_box)

        # Store initial visibility settings to allow reset on Cancel
        self.initial_block_visibility = {}
        if self.plotter_window.parent_plotter:
            block_names = self.plotter_window.parent_plotter.get_block_names()
            for block_name in block_names:
                self.initial_block_visibility[block_name] = self.plotter_window.parent_plotter.get_block_visibility(
                    block_name
                )

        # Populate property tree
        self.populate_blocks()

        # Connect item changed signal for immediate updates
        self.tree.itemChanged.connect(self._on_item_changed)

    def populate_blocks(self) -> None:
        """Populate the property tree with block visibility checkboxes.

        Creates a boolean property (checkbox) for each block in the multi-block mesh,
        using the block name as the label and initial visibility state.
        """

        # Add checkbox for each block
        for block_name, visible in self.initial_block_visibility.items():
            self.tree.add_property(name=block_name, value=visible, editor_type="bool")

    def _on_item_changed(self, item, column: int) -> None:
        """
        Handle item changed event for immediate visibility updates.

        Called when any checkbox in the property tree is toggled. Extracts the
        block name and new visibility state, then updates actor visibility immediately.

        Parameters
        ----------
        item : QTreeWidgetItem
            The tree item that was changed.
        column : int
            The column index that was changed.
        """
        # Only process value column changes (column 1)
        if column != 1:
            return

        # Get block name from item text
        block_name = item.text(0)

        # Get new visibility state from checkbox
        state = bool(self.tree.get_property_value(block_name))
        self.plotter_window.parent_plotter.set_block_visibility(block_name, state)

    def _on_ok(self) -> None:
        """Handle Ok button click - close dialog (changes already applied)."""
        self.accept()

    def _on_apply(self) -> None:
        """Handle Apply button click - no-op since changes are immediate."""
        # Changes are applied immediately via _on_item_changed, so nothing to do
        pass

    def _on_cancel(self) -> None:
        """Handle Cancel button click - restore initial visibility and close."""
        # Restore initial visibility for all blocks
        if self.plotter_window.parent_plotter:
            for block_name, visible in self.initial_block_visibility.items():
                self.plotter_window.parent_plotter.set_block_visibility(block_name, visible)

        self.reject()
