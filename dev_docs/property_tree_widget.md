# PropertyTreeWidget Documentation

## Overview

`PropertyTreeWidget` is a custom Qt widget for displaying and editing properties in a two-column tree structure. It provides a flexible property editor with support for multiple data types, validation, callbacks, and both flat and grouped property organization.

## Features

- **Two-column layout**: Property names in column 1, editable values in column 2
- **Multiple editor types**: String, integer, float, boolean, enum (combobox), color picker, and slider
- **Address-based identification**: Unique addressing system for properties (flat: `"name"`, grouped: `"group:name"`)
- **Custom validators**: Callable validators with error highlighting and tooltips
- **Callbacks**: Optional callbacks triggered when editing completes
- **Read-only properties**: Display-only properties with gray/italic styling
- **Visibility control**: Show/hide properties dynamically
- **Programmatic updates**: Update values without triggering callbacks
- **Built-in validators**: Common validation patterns included
- **Checkable groups**: Groups with checkbox control for conditional property sections

## Architecture

### Custom Qt Roles

The widget uses custom Qt roles to store metadata on `QTreeWidgetItem` instances:

| Role | Purpose |
|------|---------|
| `EDITOR_TYPE_ROLE` | Type of editor widget ("string", "int", "float", "bool", "enum", "color") |
| `CALLBACK_ROLE` | Callable to invoke when value changes |
| `VALIDATOR_ROLE` | Callable to validate value |
| `VALIDATION_ERROR_ROLE` | Error message if validation fails |
| `MIN_VALUE_ROLE` | Minimum value for numeric types |
| `MAX_VALUE_ROLE` | Maximum value for numeric types |
| `CHOICES_ROLE` | List of choices for enum type |
| `READONLY_ROLE` | Whether property is read-only |
| `ADDRESS_ROLE` | Unique address of property |

### Address System

Properties are identified by unique addresses:
- **Flat properties**: Simple name (e.g., `"opacity"`)
- **Grouped properties**: Group name + colon + property name (e.g., `"Scalar Field:color_map"`)
- **Reserved character**: Colon (`:`) is reserved and cannot be used in names
- **Single-level grouping**: Only one level of nesting supported (no nested groups)
- **Case-sensitive**: Addresses are case-sensitive

### Validation Flow

1. User edits value in column 2
2. Delegate's `setModelData()` method is called
3. Validator (if present) is invoked with the new value
4. If validator returns non-empty string:
   - Error message stored in `VALIDATION_ERROR_ROLE`
   - Background turns red
   - Tooltip shows error message
   - Callback is NOT invoked
5. If validator returns empty string:
   - Error state cleared
   - Callback is invoked (if present)

### Delegate Pattern

`PropertyDelegate` extends `QStyledItemDelegate` to provide custom editors:
- `createEditor()`: Returns appropriate widget based on editor type
- `setEditorData()`: Populates editor with current value
- `setModelData()`: Saves value, runs validation, invokes callback
- `paint()`: Custom painting for red error highlighting and read-only styling
- `editorEvent()`: Handles color picker dialog on double-click for color type

## API Reference

### PropertyTreeWidget Class

#### Constructor

```python
PropertyTreeWidget(parent=None)
```

Creates a new property tree widget.

**Parameters:**
- `parent` (QWidget, optional): Parent widget

**Example:**
```python
from pyemsi.property_tree_widget import PropertyTreeWidget

tree = PropertyTreeWidget()
tree.show()
```

---

#### add_property()

```python
add_property(
    name: str,
    value: Any,
    editor_type: str,
    callback: Optional[Callable[[Any], None]] = None,
    validator: Optional[Callable[[Any], str]] = None,
    parent: Optional[QTreeWidgetItem] = None,
    readonly: bool = False,
    **kwargs
) -> QTreeWidgetItem
```

Adds a property to the tree.

**Parameters:**
- `name` (str): Property name (cannot contain `:`)
- `value` (Any): Initial value
- `editor_type` (str): Editor type - see [Editor Types](#editor-types)
- `callback` (callable, optional): Function called when value changes, receives new value
- `validator` (callable, optional): Function to validate value - see [Validators](#validators)
- `parent` (QTreeWidgetItem, optional): Parent group item
- `readonly` (bool): If True, property is displayed but not editable
- `**kwargs`: Additional parameters based on editor type:
  - `min` (float): Minimum value for int/float/slider types
  - `max` (float): Maximum value for int/float/slider types
  - `decimals` (int): Number of decimal places for float type (default: 2)
  - `choices` (List[str]): List of choices for enum type
  - `steps` (int): Number of discrete slider positions for slider type (default: 100, applies to both int and float)

**Returns:**
- `QTreeWidgetItem`: The created property item

**Raises:**
- `ValueError`: If name contains colon or address already exists

**Examples:**
```python
# String property with regex validation
tree.add_property(
    "username", "admin", "string",
    callback=lambda v: print(f"Username: {v}"),
    validator=regex_validator(r'^[a-zA-Z0-9_]+$')
)

# Integer property with range
tree.add_property(
    "count", 10, "int",
    callback=lambda v: update_count(v),
    validator=range_validator(0, 100),
    min=0, max=100
)

# Float property with decimal precision
tree.add_property(
    "opacity", 1.0, "float",
    callback=lambda v: set_opacity(v),
    min=0.0, max=1.0, decimals=2
)

# Boolean property
tree.add_property(
    "enabled", True, "bool",
    callback=lambda v: toggle_feature(v)
)

# Enum property
tree.add_property(
    "mode", "viridis", "enum",
    callback=lambda v: set_colormap(v),
    choices=["viridis", "plasma", "cool", "hot"]
)

# Color property
tree.add_property(
    "color", "#FF5733", "color",
    callback=lambda v: set_color(v),
    validator=color_validator()
)

# Read-only property
tree.add_property(
    "fps", "60", "string",
    readonly=True
)
```

---

#### add_group()

```python
add_group(name: str) -> QTreeWidgetItem
```

Adds a property group (parent item) with bold font.

**Parameters:**
- `name` (str): Group name (cannot contain `:`)

**Returns:**
- `QTreeWidgetItem`: The created group item

**Raises:**
- `ValueError`: If name contains colon

**Example:**
```python
# Create group
scalar_group = tree.add_group("Scalar Field")

# Add properties to group
tree.add_property(
    "color_map", "viridis", "enum",
    parent=scalar_group,
    choices=["viridis", "plasma", "cool", "hot"]
)
tree.add_property(
    "opacity", 1.0, "float",
    parent=scalar_group,
    min=0.0, max=1.0
)

# Address will be "Scalar Field:color_map" and "Scalar Field:opacity"
```

---

#### add_checkable_group()

```python
add_checkable_group(
    name: str,
    checked: bool = True,
    callback: Optional[Callable[[bool], None]] = None
) -> QTreeWidgetItem
```

Adds a checkable property group with checkbox control in column 1.

When checked, children are visible and group auto-expands. When unchecked, children are hidden while the group itself remains expanded for visual consistency.

**Parameters:**
- `name` (str): Group name (cannot contain `:`)
- `checked` (bool): Initial checked state (default: True)
- `callback` (callable, optional): Function called when checkbox state changes, receives bool

**Returns:**
- `QTreeWidgetItem`: The created checkable group item

**Raises:**
- `ValueError`: If name contains colon or address already exists

**Address System:**
- Group address: `"name"` (stored in `_property_items`)
- Child properties: `"name:property_name"` (same as regular groups)

**Behavior:**
- **Checked**: Group auto-expands, children visible
- **Unchecked**: Children hidden, group stays expanded
- **Programmatic updates**: Use `update_property_value("GroupName", True/False)` to toggle state without triggering callback

**Examples:**
```python
# Basic checkable group
group = tree.add_checkable_group(
    "Advanced Settings",
    checked=False,
    callback=lambda checked: print(f"Advanced mode: {checked}")
)

tree.add_property("debug_mode", False, "bool", parent=group)
tree.add_property("log_level", "INFO", "enum", parent=group, choices=["DEBUG", "INFO", "WARN", "ERROR"])

# Conditional visualization settings
viz_group = tree.add_checkable_group(
    "Vector Field",
    checked=True,
    callback=lambda checked: toggle_vectors(checked)
)

tree.add_property("scale", 1.0, "float", parent=viz_group, min=0.1, max=10.0)
tree.add_property("glyph_type", "arrow", "enum", parent=viz_group, choices=["arrow", "cone", "sphere"])

# Programmatically control group state
tree.update_property_value("Advanced Settings", True)  # Check and show children
tree.update_property_value("Vector Field", False)     # Uncheck and hide children
```

**Use Cases:**
- Optional feature sections (e.g., "Show Advanced Options")
- Conditional rendering settings (e.g., "Enable Shadows")
- Toggleable analysis parameters (e.g., "Apply Smoothing")
- Debug/developer modes

---

#### get_property_item()

```python
get_property_item(address: str) -> Optional[QTreeWidgetItem]
```

Retrieves a property item by its address (case-sensitive).

**Parameters:**
- `address` (str): Property address

**Returns:**
- `QTreeWidgetItem` or `None`: Item if found, None otherwise

**Example:**
```python
item = tree.get_property_item("Scalar Field:opacity")
if item:
    current_value = item.text(1)
    print(f"Current opacity: {current_value}")
```

---

#### update_property_value()

```python
update_property_value(
    address_or_item: Union[str, QTreeWidgetItem],
    value: Any
)
```

Updates a property value programmatically without triggering the callback. Useful for synchronizing external state changes back to the UI.

For checkable groups, pass a boolean value to toggle the checkbox state and children visibility.

**Parameters:**
- `address_or_item` (str or QTreeWidgetItem): Property address or item
- `value` (Any): New value to set (for checkable groups, pass bool for checked state)

**Raises:**
- `ValueError`: If address not found

**Example:**
```python
# Update by address
tree.update_property_value("opacity", 0.5)

# For checkable groups
tree.update_property_value("Advanced Settings", True)  # Check and show children
tree.update_property_value("Vector Field", False)     # Uncheck and hide children

# Update by item
item = tree.get_property_item("opacity")
tree.update_property_value(item, 0.75)
```

---

#### get_all_addresses()

```python
get_all_addresses() -> List[str]
```

Returns a list of all property addresses.

**Returns:**
- `List[str]`: List of all property addresses

**Example:**
```python
addresses = tree.get_all_addresses()
print(addresses)
# Output: ['opacity', 'Scalar Field:color_map', 'Scalar Field:show_edges']

# Iterate over all properties
for address in tree.get_all_addresses():
    item = tree.get_property_item(address)
    print(f"{address}: {item.text(1)}")
```

---

#### set_property_visible()

```python
set_property_visible(
    address_or_item: Union[str, QTreeWidgetItem],
    visible: bool
)
```

Shows or hides a property.

**Parameters:**
- `address_or_item` (str or QTreeWidgetItem): Property address or item
- `visible` (bool): True to show, False to hide

**Raises:**
- `ValueError`: If address not found

**Example:**
```python
# Hide property
tree.set_property_visible("advanced_option", False)

# Show property
tree.set_property_visible("advanced_option", True)

# Toggle based on condition
tree.set_property_visible("debug_mode", is_developer)
```

---

## Editor Types

| Type | Widget | Description | Supported kwargs |
|------|--------|-------------|------------------|
| `"string"` | QLineEdit | Text input | - |
| `"int"` | QSpinBox | Integer spinner | `min`, `max` |
| `"float"` | QDoubleSpinBox | Decimal spinner | `min`, `max`, `decimals` |
| `"bool"` | QCheckBox | Checkbox | - |
| `"enum"` | QComboBox | Dropdown selection | `choices` (required) |
| `"color"` | QColorDialog | Color picker dialog (double-click) | - |
| `"slider"` | QSlider + QSpinBox/QDoubleSpinBox | Slider with numeric input field (dual input) | `min`, `max`, `steps`, `decimals` |

### Editor Behavior

- **String**: Opens text editor on click
- **Int/Float**: Opens spinner on click, supports keyboard input
- **Bool**: Toggles on click
- **Enum**: Opens dropdown on click
- **Color**: Double-click opens color picker dialog, displays hex value (`#RRGGBB`)
- **Slider**: Dual input - drag slider for continuous adjustment OR type directly into numeric field; both stay synchronized; callback fires when editing finishes

---

## Validators

Validators are callables with signature:

```python
def validator(value: Any) -> str:
    """Validates a value.
    
    Args:
        value: Value to validate
        
    Returns:
        Empty string if validation succeeds
        Error message string if validation fails
    """
```

### Built-in Validators

#### range_validator()

```python
range_validator(min_val: float, max_val: float) -> Callable[[Any], str]
```

Validates numeric values are within a range (inclusive).

**Example:**
```python
from pyemsi.property_tree_widget import range_validator

validator = range_validator(0, 100)
tree.add_property("percentage", 50, "int", validator=validator, min=0, max=100)
```

---

#### regex_validator()

```python
regex_validator(pattern: str) -> Callable[[Any], str]
```

Validates string values match a regular expression pattern.

**Example:**
```python
from pyemsi.property_tree_widget import regex_validator

# Email validation
validator = regex_validator(r'^[\w\.-]+@[\w\.-]+\.\w+$')
tree.add_property("email", "", "string", validator=validator)

# Alphanumeric only
validator = regex_validator(r'^[a-zA-Z0-9]+$')
tree.add_property("username", "", "string", validator=validator)
```

---

#### required_validator()

```python
required_validator() -> Callable[[Any], str]
```

Validates that a value is not empty or None.

**Example:**
```python
from pyemsi.property_tree_widget import required_validator

tree.add_property("name", "", "string", validator=required_validator())
```

---

#### color_validator()

```python
color_validator() -> Callable[[Any], str]
```

Validates hex color strings in `#RRGGBB` format.

**Example:**
```python
from pyemsi.property_tree_widget import color_validator

tree.add_property("bg_color", "#FFFFFF", "color", validator=color_validator())
```

---

### Slider Examples

The slider editor provides **dual input methods**:
- **Drag the slider** for continuous visual adjustment
- **Type directly** into the numeric field for precise values

Both controls stay synchronized automatically using a unified normalized mapping approach.

```python
from pyemsi.property_tree_widget import PropertyTreeWidget, range_validator

tree = PropertyTreeWidget()

# Integer slider (0-100) with default 100 steps
tree.add_property(
    "volume", 50, "slider",
    callback=lambda v: print(f"Volume: {v}"),
    min=0, max=100
)

# Float slider (0.0-1.0) with default 100 steps
tree.add_property(
    "opacity", 0.5, "slider",
    callback=lambda v: print(f"Opacity: {v:.3f}"),
    validator=range_validator(0.0, 1.0),
    min=0.0, max=1.0
)

# Float slider with custom decimal precision
tree.add_property(
    "precision_value", 0.5, "slider",
    callback=lambda v: print(f"Value: {v}"),
    min=0.0, max=1.0,
    decimals=4  # Show 4 decimal places in spinbox
)

# Float slider with high precision (1000 steps for finer control)
tree.add_property(
    "threshold", 0.5, "slider",
    callback=lambda v: set_threshold(v),
    min=0.0, max=1.0,
    steps=1000  # Higher = smoother slider movement
)

# Integer slider with custom steps (large range, coarser control)
tree.add_property(
    "frame_number", 500, "slider",
    callback=lambda v: set_frame(v),
    min=0, max=10000,
    steps=200  # 200 steps for 0-10000 range = 50 units per step
)
```

**Unified Precision Model:**
- `steps` parameter controls slider granularity for **both int and float** sliders (default: 100)
  - Higher steps = smoother slider movement and finer control
  - Lower steps = coarser slider steps
  - Effective step size = `(max - min) / steps`
- `decimals` parameter controls numeric field precision for float sliders only (default: 2)
  - Determines decimal places shown in the spinbox
  - Independent of slider steps
- **Tip**: For precise values, type directly into the numeric field instead of dragging

**Examples:**
- Int slider [0, 100] with 100 steps = 1 unit per slider step
- Int slider [0, 10000] with 100 steps = 100 units per slider step
- Float slider [0.0, 1.0] with 100 steps = 0.01 per slider step
- Float slider [0.0, 1.0] with 1000 steps = 0.001 per slider step

---

### Custom Validators

You can create custom validators by defining a function that follows the validator signature:

```python
def positive_even_validator(value):
    """Validates value is a positive even number."""
    try:
        num = int(value)
        if num <= 0:
            return "Value must be positive"
        if num % 2 != 0:
            return "Value must be even"
        return ""  # Success
    except (ValueError, TypeError):
        return "Invalid number"

tree.add_property("even_count", 10, "int", validator=positive_even_validator)
```

---

## Complete Usage Example

```python
from PySide6.QtWidgets import QApplication
from pyemsi.property_tree_widget import (
    PropertyTreeWidget,
    range_validator,
    regex_validator,
    required_validator,
    color_validator
)

app = QApplication([])

# Create property tree
tree = PropertyTreeWidget()
tree.setWindowTitle("Property Editor")
tree.resize(400, 600)

# Add flat properties
tree.add_property(
    "project_name", "MyProject", "string",
    callback=lambda v: print(f"Project: {v}"),
    validator=required_validator()
)

tree.add_property(
    "show_edges", True, "bool",
    callback=lambda v: print(f"Edges: {v}")
)

# Create scalar field group
scalar_group = tree.add_group("Scalar Field")

tree.add_property(
    "color_map", "viridis", "enum",
    callback=lambda v: print(f"Colormap: {v}"),
    parent=scalar_group,
    choices=["viridis", "plasma", "cool", "hot", "jet"]
)

tree.add_property(
    "opacity", 1.0, "float",
    callback=lambda v: print(f"Opacity: {v}"),
    validator=range_validator(0.0, 1.0),
    parent=scalar_group,
    min=0.0, max=1.0, decimals=2
)

tree.add_property(
    "edge_color", "#000000", "color",
    callback=lambda v: print(f"Edge color: {v}"),
    validator=color_validator(),
    parent=scalar_group
)

# Create vector field group
vector_group = tree.add_group("Vector Field")

tree.add_property(
    "scale_factor", 1.0, "float",
    callback=lambda v: print(f"Scale: {v}"),
    validator=range_validator(0.1, 10.0),
    parent=vector_group,
    min=0.1, max=10.0, decimals=1
)

tree.add_property(
    "glyph_type", "arrow", "enum",
    callback=lambda v: print(f"Glyph: {v}"),
    parent=vector_group,
    choices=["arrow", "cone", "sphere", "cylinder"]
)

# Add read-only status property
tree.add_property(
    "render_time", "16.7 ms", "string",
    readonly=True
)

# Create checkable group for optional features
advanced_group = tree.add_checkable_group(
    "Advanced Options",
    checked=False,
    callback=lambda checked: print(f"Advanced mode: {checked}")
)

tree.add_property(
    "cache_size", 100, "int",
    callback=lambda v: print(f"Cache: {v}"),
    validator=range_validator(10, 1000),
    parent=advanced_group,
    min=10, max=1000
)

tree.add_property(
    "log_level", "INFO", "enum",
    callback=lambda v: print(f"Log level: {v}"),
    parent=advanced_group,
    choices=["DEBUG", "INFO", "WARN", "ERROR"]
)

# Show tree
tree.show()

# Programmatic updates
def update_status():
    tree.update_property_value("render_time", "14.2 ms")

# Toggle checkable group programmatically
tree.update_property_value("Advanced Options", True)  # Check and show children

# Get all properties
addresses = tree.get_all_addresses()
print(f"Total properties: {len(addresses)}")
print(f"Addresses: {addresses}")

app.exec()
```

## Visual Feedback

### Validation Errors
- **Background**: Red background on value cell
- **Tooltip**: Error message displayed on hover
- **Callback**: Not invoked when validation fails

### Read-only Properties
- **Text color**: Gray (RGB: 128, 128, 128)
- **Font style**: Italic
- **Interaction**: Cannot be edited

### Groups
- **Font**: Bold
- **Expandable**: Click to collapse/expand children
- **Non-editable**: Value column is empty and non-editable

### Checkable Groups
- **Font**: Bold
- **Checkbox**: Displayed in column 1 (value column)
- **Checked**: Group auto-expands, children visible
- **Unchecked**: Children hidden, group remains expanded
- **Interaction**: Click checkbox to toggle state and children visibility

## Notes

- **Colon restriction**: Property and group names cannot contain `:` character (raises `ValueError`)
- **Single-level grouping**: Only one level of nesting supported
- **Case-sensitive addresses**: `"opacity"` and `"Opacity"` are different
- **Callback timing**: Callbacks are invoked when editing completes (not on every keystroke)
- **Signal blocking**: `update_property_value()` blocks signals to prevent recursive callbacks
- **Color format**: Colors are stored and displayed as hex strings (`#RRGGBB`)
- **Thread safety**: Widget is not thread-safe, use Qt signals/slots for cross-thread updates

## Integration Examples

### With PyVista Plotter

```python
from pyemsi.property_tree_widget import PropertyTreeWidget, range_validator
from pyemsi.plotter import Plotter

# Create plotter and property tree
plotter = Plotter()
tree = PropertyTreeWidget()

# Load mesh
plotter.set_file("mesh.vtm")

# Add visualization properties
tree.add_property(
    "opacity", 1.0, "float",
    callback=lambda v: plotter.set_scalar(opacity=v),
    validator=range_validator(0.0, 1.0),
    min=0.0, max=1.0
)

tree.add_property(
    "show_edges", False, "bool",
    callback=lambda v: plotter.set_feature_edges(enabled=v)
)

# Sync external changes back to UI
def on_external_opacity_change(new_opacity):
    tree.update_property_value("opacity", new_opacity)
```

### With QDockWidget

```python
from PySide6.QtWidgets import QMainWindow, QDockWidget
from pyemsi.property_tree_widget import PropertyTreeWidget

window = QMainWindow()

# Create dock widget
dock = QDockWidget("Properties", window)
tree = PropertyTreeWidget()
dock.setWidget(tree)

# Add dock to right side
window.addDockWidget(Qt.RightDockWidgetArea, dock)

# Add properties
tree.add_property("setting1", "value1", "string")
tree.add_property("setting2", 42, "int")

window.show()
```

## Future Enhancements

- Multi-level nested groups
- Undo/redo support
- Property search/filter
- Export/import to JSON/dict
- Custom editor widgets via plugin system
- Batch property updates with transaction support
- Property dependencies (enable/disable based on other values)
