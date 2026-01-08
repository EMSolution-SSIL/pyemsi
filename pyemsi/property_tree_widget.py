"""Property tree widget with editable values and validation support."""

from typing import Callable, Any, Optional, Union, List, Literal
import re
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from .property_delegate import PropertyDelegate


# Built-in validator factories
def range_validator(min_val: float, max_val: float) -> Callable[[Any], str]:
    """Create a validator for numeric range constraints.

    Args:
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        Validator callable that returns empty string on success or error message on failure

    Example:
        >>> validator = range_validator(0, 100)
        >>> validator(50)  # Returns ""
        >>> validator(150)  # Returns "Value must be between 0 and 100"
    """

    def validator(value: Any) -> str:
        try:
            num_val = float(value)
            if num_val < min_val or num_val > max_val:
                return f"Value must be between {min_val} and {max_val}"
            return ""
        except (ValueError, TypeError):
            return "Invalid number format"

    return validator


def regex_validator(pattern: str) -> Callable[[Any], str]:
    """Create a validator for regex pattern matching.

    Args:
        pattern: Regular expression pattern to match

    Returns:
        Validator callable that returns empty string on success or error message on failure

    Example:
        >>> validator = regex_validator(r'^[A-Za-z]+$')
        >>> validator("Hello")  # Returns ""
        >>> validator("Hello123")  # Returns "Value must match pattern: ^[A-Za-z]+$"
    """

    def validator(value: Any) -> str:
        try:
            if not re.match(pattern, str(value)):
                return f"Value must match pattern: {pattern}"
            return ""
        except re.error:
            return f"Invalid regex pattern: {pattern}"

    return validator


def required_validator() -> Callable[[Any], str]:
    """Create a validator for non-empty values.

    Returns:
        Validator callable that returns empty string on success or error message on failure

    Example:
        >>> validator = required_validator()
        >>> validator("text")  # Returns ""
        >>> validator("")  # Returns "Value is required"
        >>> validator(None)  # Returns "Value is required"
    """

    def validator(value: Any) -> str:
        if value is None or str(value).strip() == "":
            return "Value is required"
        return ""

    return validator


def color_validator() -> Callable[[Any], str]:
    """Create a validator for hex color strings.

    Returns:
        Validator callable that returns empty string on success or error message on failure

    Example:
        >>> validator = color_validator()
        >>> validator("#FF5733")  # Returns ""
        >>> validator("#XYZ")  # Returns "Invalid hex color format. Expected #RRGGBB"
    """

    def validator(value: Any) -> str:
        pattern = r"^#[0-9A-Fa-f]{6}$"
        if not re.match(pattern, str(value)):
            return "Invalid hex color format. Expected #RRGGBB"
        return ""

    return validator


class PropertyTreeWidget(QTreeWidget):
    """Tree widget for displaying and editing properties with validation.

    Features:
    - Two-column layout (Property Name | Value)
    - Support for flat properties and grouped properties
    - Address-based identification (group:name for grouped, name for flat)
    - Multiple editor types: string, int, float, bool, enum, color, slider
    - Custom validators with error highlighting and tooltips
    - Optional callbacks triggered after editing completes
    - Read-only properties with gray/italic styling
    - Visibility control for properties
    - Programmatic value updates

    Custom Qt Roles:
        EDITOR_TYPE_ROLE: Type of editor widget
        CALLBACK_ROLE: Callable to invoke when value changes
        VALIDATOR_ROLE: Callable to validate value
        VALIDATION_ERROR_ROLE: Error message if validation fails
        MIN_VALUE_ROLE: Minimum value for numeric types
        MAX_VALUE_ROLE: Maximum value for numeric types
        CHOICES_ROLE: List of choices for enum type
        READONLY_ROLE: Whether property is read-only
        ADDRESS_ROLE: Unique address of property
    """

    # Custom Qt roles (must match PropertyDelegate)
    EDITOR_TYPE_ROLE = Qt.ItemDataRole.UserRole + 1
    CALLBACK_ROLE = Qt.ItemDataRole.UserRole + 2
    VALIDATOR_ROLE = Qt.ItemDataRole.UserRole + 3
    VALIDATION_ERROR_ROLE = Qt.ItemDataRole.UserRole + 4
    MIN_VALUE_ROLE = Qt.ItemDataRole.UserRole + 5
    MAX_VALUE_ROLE = Qt.ItemDataRole.UserRole + 6
    CHOICES_ROLE = Qt.ItemDataRole.UserRole + 7
    READONLY_ROLE = Qt.ItemDataRole.UserRole + 8
    ADDRESS_ROLE = Qt.ItemDataRole.UserRole + 9
    STEP_ROLE = Qt.ItemDataRole.UserRole + 10
    GROUP_CHECKABLE_ROLE = Qt.ItemDataRole.UserRole + 11
    GROUP_CHECKED_ROLE = Qt.ItemDataRole.UserRole + 12

    def __init__(self, parent=None):
        """Initialize the property tree widget.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        # Setup tree widget
        self.setHeaderLabels(["Property", "Value"])
        self.setColumnCount(2)
        self.setWordWrap(True)

        # Set proportional column widths
        self.header().setStretchLastSection(True)

        # Set custom delegate for all columns (handles column 0 non-editability)
        self._delegate = PropertyDelegate(self)
        self.setItemDelegate(self._delegate)

        # Dictionary to store property items by address
        self._property_items = {}

        # Connect signals
        self.itemChanged.connect(self._on_item_changed)

    def add_property(
        self,
        name: str,
        value: Any,
        editor_type: Literal["string", "int", "float", "bool", "enum", "color", "slider"],
        callback: Optional[Callable[[Any], None]] = None,
        validator: Optional[Callable[[Any], str]] = None,
        parent: Optional[QTreeWidgetItem] = None,
        readonly: bool = False,
        **kwargs,
    ) -> QTreeWidgetItem:
        """Add a property item with callback and validation.

        Args:
            name: Property name (colon ':' is reserved and will raise ValueError)
            value: Initial value
            editor_type: Type of editor - "string", "int", "float", "bool", "enum", "color", "slider"
            callback: Optional callable invoked when value changes (receives new value)
            validator: Optional callable for validation (returns "" on success, error message on failure)
            parent: Optional parent group item
            readonly: If True, property is displayed but not editable
            **kwargs: Additional parameters:
                - min: Minimum value for int/float/slider types
                - max: Maximum value for int/float/slider types
                - decimals: Number of decimal places for float type
                - choices: List of choices for enum type
                - steps: Number of discrete steps for float slider (default: 1000)

        Returns:
            Created QTreeWidgetItem

        Raises:
            ValueError: If name contains colon character or if address already exists

        Example:
            >>> tree = PropertyTreeWidget()
            >>> # Add float property with range validation
            >>> tree.add_property(
            ...     "opacity", 1.0, "float",
            ...     callback=lambda v: print(f"Opacity: {v}"),
            ...     validator=range_validator(0.0, 1.0),
            ...     min=0.0, max=1.0, decimals=2
            ... )
        """
        # Validate name doesn't contain colon
        if ":" in name:
            raise ValueError(f"Property name cannot contain colon ':' character: {name}")

        # Generate address
        if parent:
            parent_name = parent.text(0)
            address = f"{parent_name}:{name}"
        else:
            address = name

        # Check if address already exists
        if address in self._property_items:
            raise ValueError(f"Property with address '{address}' already exists")

        # Create item
        item = QTreeWidgetItem([name, str(value)])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

        # Store metadata in column 1 (value column)
        item.setData(1, self.EDITOR_TYPE_ROLE, editor_type)
        item.setData(1, self.ADDRESS_ROLE, address)
        item.setData(1, self.READONLY_ROLE, readonly)

        if callback is not None:
            item.setData(1, self.CALLBACK_ROLE, callback)

        if validator is not None:
            item.setData(1, self.VALIDATOR_ROLE, validator)

        # Store additional parameters
        if "min" in kwargs:
            item.setData(1, self.MIN_VALUE_ROLE, kwargs["min"])
        if "max" in kwargs:
            item.setData(1, self.MAX_VALUE_ROLE, kwargs["max"])
        if "decimals" in kwargs:
            item.setData(1, Qt.ItemDataRole.UserRole + 10, kwargs["decimals"])  # DECIMALS_ROLE
        if "choices" in kwargs:
            item.setData(1, self.CHOICES_ROLE, kwargs["choices"])
        if "steps" in kwargs:
            item.setData(1, self.STEP_ROLE, kwargs["steps"])

        # Apply read-only styling
        if readonly:
            font = item.font(1)
            font.setItalic(True)
            item.setFont(1, font)
            item.setForeground(1, QColor(128, 128, 128))
            # Make non-editable
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        # Add to tree
        if parent:
            parent.addChild(item)
        else:
            self.addTopLevelItem(item)

        # Store in dictionary
        self._property_items[address] = item

        return item

    def add_group(self, name: str) -> QTreeWidgetItem:
        """Add a property group (parent item) with bold font.

        Args:
            name: Group name (colon ':' is reserved and will raise ValueError)

        Returns:
            Created QTreeWidgetItem for the group

        Raises:
            ValueError: If name contains colon character

        Example:
            >>> tree = PropertyTreeWidget()
            >>> group = tree.add_group("Scalar Field")
            >>> tree.add_property("color_map", "viridis", "enum", parent=group, choices=["viridis", "plasma"])
        """
        # Validate name doesn't contain colon
        if ":" in name:
            raise ValueError(f"Group name cannot contain colon ':' character: {name}")

        # Create group item
        group = QTreeWidgetItem([name, ""])
        group.setFlags(group.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make non-editable
        group.setExpanded(True)  # Expand by default

        # Apply bold font
        font = group.font(0)
        font.setBold(True)
        group.setFont(0, font)

        # Add to tree
        self.addTopLevelItem(group)
        group.setFirstColumnSpanned(True)

        return group

    def add_checkable_group(
        self,
        name: str,
        checked: bool = True,
        callback: Optional[Callable[[bool], None]] = None,
    ) -> QTreeWidgetItem:
        """Add a checkable property group with checkbox control.

        When checked, children are visible and group auto-expands.
        When unchecked, children are hidden (group remains expanded for visual consistency).

        Args:
            name: Group name (colon ':' is reserved and will raise ValueError)
            checked: Initial checked state (default: True)
            callback: Optional callable invoked when checkbox state changes (receives bool)

        Returns:
            Created QTreeWidgetItem for the checkable group

        Raises:
            ValueError: If name contains colon character or if address already exists

        Example:
            >>> tree = PropertyTreeWidget()
            >>> group = tree.add_checkable_group(
            ...     "Advanced Settings",
            ...     checked=False,
            ...     callback=lambda checked: print(f"Advanced: {checked}")
            ... )
            >>> tree.add_property("debug_mode", False, "bool", parent=group)
        """
        # Validate name doesn't contain colon
        if ":" in name:
            raise ValueError(f"Group name cannot contain colon ':' character: {name}")

        # Check if address already exists
        if name in self._property_items:
            raise ValueError(f"Property with address '{name}' already exists")

        # Create group item
        group = QTreeWidgetItem([name, ""])
        group.setFlags(group.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make non-editable
        group.setExpanded(True)  # Expand by default

        # Apply bold font
        font = group.font(0)
        font.setBold(True)
        group.setFont(0, font)

        # Store checkbox metadata in column 1
        group.setData(1, self.GROUP_CHECKABLE_ROLE, True)
        group.setData(1, self.GROUP_CHECKED_ROLE, checked)

        if callback is not None:
            group.setData(1, self.CALLBACK_ROLE, callback)

        # Add to tree
        self.addTopLevelItem(group)
        # Note: Do NOT call setFirstColumnSpanned() for checkable groups

        # Store in dictionary
        self._property_items[name] = group

        # Apply initial visibility state to children (may be none yet)
        self._set_group_children_visible(group, checked)

        return group

    def _get_group_children(self, group_item: QTreeWidgetItem) -> List[QTreeWidgetItem]:
        """Get all direct children of a group item.

        Args:
            group_item: The group item

        Returns:
            List of child QTreeWidgetItem instances
        """
        children = []
        for i in range(group_item.childCount()):
            children.append(group_item.child(i))
        return children

    def _set_group_children_visible(self, group_item: QTreeWidgetItem, visible: bool):
        """Set visibility for all children of a group.

        Args:
            group_item: The group item
            visible: If True, show children; if False, hide children
        """
        for child in self._get_group_children(group_item):
            child.setHidden(not visible)

    def get_property_item(self, address: str) -> Optional[QTreeWidgetItem]:
        """Get property item by address (case-sensitive).

        Args:
            address: Property address (e.g., "opacity" or "Scalar Field:color_map")

        Returns:
            QTreeWidgetItem if found, None otherwise

        Example:
            >>> item = tree.get_property_item("Scalar Field:color_map")
            >>> if item:
            ...     print(item.text(1))  # Print current value
        """
        return self._property_items.get(address)

    def update_property_value(self, address_or_item: Union[str, QTreeWidgetItem], value: Any):
        """Update property value programmatically without triggering callback.

        Args:
            address_or_item: Property address string or QTreeWidgetItem
            value: New value to set (for checkable groups, pass bool for checked state)

        Raises:
            ValueError: If address not found

        Example:
            >>> tree.update_property_value("opacity", 0.5)
            >>> # For checkable groups
            >>> tree.update_property_value("Advanced Settings", True)
            >>> # Or using item directly
            >>> item = tree.get_property_item("opacity")
            >>> tree.update_property_value(item, 0.5)
        """
        # Get item
        if isinstance(address_or_item, str):
            item = self.get_property_item(address_or_item)
            if item is None:
                raise ValueError(f"Property with address '{address_or_item}' not found")
        else:
            item = address_or_item

        # Block signals to prevent triggering callback
        self.blockSignals(True)

        try:
            # Check if this is a checkable group
            if item.data(1, self.GROUP_CHECKABLE_ROLE):
                # Handle as checkable group
                checked = bool(value)
                item.setData(1, self.GROUP_CHECKED_ROLE, checked)

                # Auto-expand if checked
                if checked:
                    item.setExpanded(True)

                # Set children visibility
                self._set_group_children_visible(item, checked)

                # Trigger repaint to update checkbox visual state
                self.viewport().update()
            else:
                # Handle as regular property
                # Update text
                item.setText(1, str(value))

                # Run validation
                validator = item.data(1, self.VALIDATOR_ROLE)
                if callable(validator):
                    error_msg = validator(value)
                    if error_msg:
                        item.setData(1, self.VALIDATION_ERROR_ROLE, error_msg)
                        item.setToolTip(1, error_msg)
                    else:
                        item.setData(1, self.VALIDATION_ERROR_ROLE, "")
                        item.setToolTip(1, "")

                # Trigger repaint to update visual state
                self.viewport().update()
        finally:
            # Unblock signals
            self.blockSignals(False)

    def get_all_addresses(self) -> List[str]:
        """Get list of all property addresses.

        Returns:
            List of property addresses

        Example:
            >>> addresses = tree.get_all_addresses()
            >>> print(addresses)  # ['opacity', 'Scalar Field:color_map', 'Scalar Field:show_edges']
        """
        return list(self._property_items.keys())

    def set_property_visible(self, address_or_item: Union[str, QTreeWidgetItem], visible: bool):
        """Toggle property visibility.

        Args:
            address_or_item: Property address string or QTreeWidgetItem
            visible: If True, show the property; if False, hide it

        Raises:
            ValueError: If address not found

        Example:
            >>> tree.set_property_visible("opacity", False)  # Hide property
            >>> tree.set_property_visible("opacity", True)   # Show property
        """
        # Get item
        if isinstance(address_or_item, str):
            item = self.get_property_item(address_or_item)
            if item is None:
                raise ValueError(f"Property with address '{address_or_item}' not found")
        else:
            item = address_or_item

        # Set hidden state
        item.setHidden(not visible)

    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Internal handler for item changes - validates and invokes callback.

        Args:
            item: Changed item
            column: Changed column
        """
        # Get editor type and callback
        editor_type = item.data(1, self.EDITOR_TYPE_ROLE)
        callback = item.data(1, self.CALLBACK_ROLE)

        # Skip if no editor type (e.g., group items)
        if not editor_type:
            return

        # Get value and convert to appropriate type
        value = item.text(1)

        try:
            if editor_type == "int":
                value = int(value)
            elif editor_type == "float":
                value = float(value)
            elif editor_type == "slider":
                # Check if original value was float or int
                try:
                    if "." in item.text(1) or "e" in item.text(1).lower():
                        value = float(value)
                    else:
                        value = int(value)
                except (ValueError, TypeError):
                    value = int(value)
            elif editor_type == "bool":
                if isinstance(value, str):
                    value = value.lower() in ("true", "1", "yes")
                else:
                    value = bool(value)
        except (ValueError, TypeError):
            # If conversion fails, keep as string
            pass

        # Check validation status
        error_msg = item.data(1, self.VALIDATION_ERROR_ROLE)

        # Only invoke callback if validation passed and callback exists
        if not error_msg and callable(callback):
            callback(value)
