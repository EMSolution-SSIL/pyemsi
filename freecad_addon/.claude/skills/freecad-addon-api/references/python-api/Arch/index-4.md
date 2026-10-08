# Python source module `Arch`

[Python catalogue](../index.md)

Evidence: `src/Mod/BIM/Arch.py`. Import path is source-routed; installed availability is unverified.

Core API for architectural and Building Information Modeling (BIM) in FreeCAD.

Provides tools for creating parametric architectural elements (walls, windows,
structures) and managing BIM data. Serves as the foundation for both the BIM
Workbench and third-party extensions.

## Features
- Parametric architectural components (walls, floors, roofs, windows)
- BIM data support (materials, IFC properties, classification systems)
- Integration with FreeCAD's core (Part, Draft) and other workbenches
- Object creation utilities for architectural workflows

## Usage
Designed for:
1. Internal API for FreeCAD's built-in BIM commands
2. Public API for add-on developers creating extension macros, workbenches, or
   other specialized BIM tools

## Examples
```python
import Arch
wall = Arch.makeWall(length=5000, width=200, height=3000)  # mm units
wall.recompute()
```

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md) | [part 3](index-3.md) | [part 4](index-4.md)

## Internal definitions not expanded

`Arch.__title__`, `Arch.__author__`, `Arch.__url__`, `Arch._initializeArchObject`. These are source internals unless an explicit export establishes otherwise.

