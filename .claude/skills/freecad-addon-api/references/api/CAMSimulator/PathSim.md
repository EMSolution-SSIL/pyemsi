# `CAMSimulator.PathSim`

[Module](index.md)

```python
class PathSim(BaseClass):
```

FreeCAD python wrapper of CAMSimulator

      CAMSimulator.CAMSim():

      Create a path simulator object

Author: Shai Seger (shaise_at_g-mail)
License: LGPL-2.1-or-later

Evidence: public stub `CAMSimulator/__init__.pyi` line 11. Inherited members are on the named base's reference; aliases keep their imported identity.

## `CAMSimulator.PathSim.BeginSimulation`

```python
def BeginSimulation(self, stock: TopoShape, resolution: float) -> None:
```

Start a simulation process on a box shape stock with given resolution

Evidence: public stub `CAMSimulator/__init__.pyi` line(s) 23.

## `CAMSimulator.PathSim.ResetSimulation`

```python
def ResetSimulation(self, document: Document, /) -> None:
```

Clear the simulation and all gcode commands

Evidence: public stub `CAMSimulator/__init__.pyi` line(s) 29.

## `CAMSimulator.PathSim.AddTool`

```python
def AddTool(self, shape: TopoShape, toolnumber: int, diameter: float, resolution: float) -> Any:
```

Set the shape of the tool to be used for simulation

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `CAMSimulator/__init__.pyi` line(s) 35.

## `CAMSimulator.PathSim.SetBaseShape`

```python
def SetBaseShape(self, shape: TopoShape, resolution: float) -> None:
```

Set the shape of the base object of the job

Evidence: public stub `CAMSimulator/__init__.pyi` line(s) 41.

## `CAMSimulator.PathSim.AddCommand`

```python
def AddCommand(self, command: Command, /) -> Any:
```

Add a path command to the simulation.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `CAMSimulator/__init__.pyi` line(s) 47.

