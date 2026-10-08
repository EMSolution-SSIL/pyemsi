# `Robot`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `Robot/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [Robot.Robot6Axis](Robot6Axis.md)
- [Robot.RobotObject](RobotObject.md)
- [Robot.Trajectory](Trajectory.md)
- [Robot.Waypoint](Waypoint.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from collections.abc import Sequence
from FreeCAD import Base as Base
from FreeCAD.Base import Persistence
from FreeCAD import DocumentObject
from FreeCAD.Base import Placement
from typing import Final
```

## `Robot.simulateToFile`

```python
def simulateToFile(robot: Robot6Axis, trajectory: Trajectory, tick_size: float, file_name: str, /) -> float:
```

Run one robot simulation, write its result to one file, and return the numeric status.

Evidence: public stub `Robot/__init__.pyi` line(s) 9.

