from pyemsi.property_tree_widget import PropertyTreeWidget, regex_validator, range_validator, color_validator
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
tree = PropertyTreeWidget()

# String property with regex validation
tree.add_property(
    "username",
    "admin",
    "string",
    callback=lambda v: print(f"Username: {v}"),
    validator=regex_validator(r"^[a-zA-Z0-9_]+$"),
)

# Integer property with range
tree.add_property("count", 10, "int", callback=lambda v: print(v), validator=range_validator(0, 100), min=0, max=100)

# Float property with decimal precision
tree.add_property(
    "opacity",
    0.5,
    "slider",
    callback=lambda v: print(f"Opacity: {v:.3f}"),
    validator=range_validator(0.0, 1.0),
    min=0.0,
    max=1.0,
    steps=100,
    decimals=2,
)

# Boolean property
tree.add_property("enabled", True, "bool", callback=lambda v: print(v))

# Enum property
tree.add_property("mode", "viridis", "enum", callback=lambda v: print(v), choices=["viridis", "plasma", "cool", "hot"])

# Color property
tree.add_property("color", "#FF5733", "color", callback=lambda v: print(v), validator=color_validator())

# Create scalar field group
scalar_group = tree.add_group("Scalar Field")

tree.add_property(
    "color_map",
    "viridis",
    "enum",
    callback=lambda v: print(f"Colormap: {v}"),
    parent=scalar_group,
    choices=["viridis", "plasma", "cool", "hot", "jet"],
)

tree.add_property(
    "opacity",
    1.0,
    "float",
    callback=lambda v: print(f"Opacity: {v}"),
    validator=range_validator(0.0, 1.0),
    parent=scalar_group,
    min=0.0,
    max=1.0,
    decimals=1,
    steps=10,
)

tree.add_property(
    "edge_color",
    "#000000",
    "color",
    callback=lambda v: print(f"Edge color: {v}"),
    validator=color_validator(),
    parent=scalar_group,
)


# Read-only property
tree.add_property("fps", "60", "string", readonly=True)


# Create checkable group for optional features
advanced_group = tree.add_checkable_group(
    "Advanced Options", checked=False, callback=lambda checked: print(f"Advanced mode: {checked}")
)

tree.add_property(
    "cache_size",
    100,
    "int",
    callback=lambda v: print(f"Cache: {v}"),
    validator=range_validator(10, 1000),
    parent=advanced_group,
    min=10,
    max=1000,
)

tree.add_property(
    "log_level",
    "INFO",
    "enum",
    callback=lambda v: print(f"Log level: {v}"),
    parent=advanced_group,
    choices=["DEBUG", "INFO", "WARN", "ERROR"],
)

tree.show()

sys.exit(app.exec())
