# `PathSimulator.PathSim`

[Module](index.md)

```python
class PathSim(BaseClass):
```

FreeCAD python wrapper of PathSimulator

PathSimulator.PathSim():

Create a path simulator object

Author: Shai Seger (shaise_at_g-mail)
License: LGPL-2.1-or-later

Evidence: public stub `PathSimulator/__init__.pyi` line 13. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PathSimulator.PathSim.BeginSimulation`

```python
def BeginSimulation(self, stock: TopoShape, resolution: float) -> None:
```

Start a simulation process on a box shape stock with given resolution

Evidence: public stub `PathSimulator/__init__.pyi` line(s) 25.

## `PathSimulator.PathSim.SetToolShape`

```python
def SetToolShape(self, tool: TopoShape, resolution: float, /) -> None:
```

Set the shape of the tool to be used for simulation

Evidence: public stub `PathSimulator/__init__.pyi` line(s) 31.

## `PathSimulator.PathSim.GetResultMesh`

```python
def GetResultMesh(self) -> tuple[Mesh, Mesh]:
```

Return the current mesh result of the simulation.

Evidence: public stub `PathSimulator/__init__.pyi` line(s) 37.

## `PathSimulator.PathSim.ApplyCommand`

```python
def ApplyCommand(self, position: Placement, command: Command) -> Placement:
```

Apply a single path command on the stock starting from placement.

Evidence: public stub `PathSimulator/__init__.pyi` line(s) 43.

## `PathSimulator.PathSim.Tool`

```python
Tool: Final[Any]
```

Return current simulation tool.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathSimulator/__init__.pyi` line(s) 48.

