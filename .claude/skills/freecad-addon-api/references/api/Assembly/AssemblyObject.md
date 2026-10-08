# `Assembly.AssemblyObject`

[Module](index.md)

```python
class AssemblyObject(Part):
```

This class handles document objects in Assembly

Author: Ondsel (development@ondsel.com)
License: LGPL-2.1-or-later

Evidence: public stub `Assembly/__init__.pyi` line 40. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Assembly.AssemblyObject.solve`

```python
def solve(self, enableUndo: bool=False, /) -> int:
```

Solve the assembly and update part placements.

Args:
enableRedo: Whether the solve save the initial position of parts
to enable undoing it even without a transaction.
Defaults to `False` ie the solve cannot be undone if called
outside of a transaction.

Returns:
0 in case of success, otherwise the following codes in this order of
priority:
-6 if no parts are fixed.
-4 if over-constrained,
-3 if conflicting constraints,
-5 if malformed constraints
-1 if solver error,
-2 if redundant constraints.

Evidence: public stub `Assembly/__init__.pyi` line(s) 48.

## `Assembly.AssemblyObject.generateSimulation`

```python
def generateSimulation(self, simulationObject: DocumentObject, /) -> int:
```

Generate the simulation.

Args:
simulationObject: The simulation Object.

Returns:
0 in case of success, otherwise the following codes in this order of
priority:
-6 if no parts are fixed.
-4 if over-constrained,
-3 if conflicting constraints,
-5 if malformed constraints
-1 if solver error,
-2 if redundant constraints.

Evidence: public stub `Assembly/__init__.pyi` line(s) 70.

## `Assembly.AssemblyObject.updateForFrame`

```python
def updateForFrame(self, index: int, /) -> None:
```

Update entire assembly to frame number specified.

Args:
    index: index of frame.

Returns: None

Evidence: public stub `Assembly/__init__.pyi` line(s) 89.

## `Assembly.AssemblyObject.numberOfFrames`

```python
def numberOfFrames(self) -> int:
```

Return Number of frames

Evidence: public stub `Assembly/__init__.pyi` line(s) 100.

## `Assembly.AssemblyObject.updateSolveStatus`

```python
def updateSolveStatus(self) -> Any:
```

updateSolveStatus()

Args: None

Returns: None

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Assembly/__init__.pyi` line(s) 104.

## `Assembly.AssemblyObject.undoSolve`

```python
def undoSolve(self) -> Any:
```

Undo the last solve of the assembly and return part placements to their initial position.

undoSolve()

Returns: None

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Assembly/__init__.pyi` line(s) 112.

## `Assembly.AssemblyObject.ensureIdentityPlacements`

```python
def ensureIdentityPlacements(self) -> None:
```

Makes sure that LinkGroups or sub-assemblies have identity placements.

Evidence: public stub `Assembly/__init__.pyi` line(s) 120.

## `Assembly.AssemblyObject.clearUndo`

```python
def clearUndo(self) -> None:
```

Clear the registered undo positions.

Evidence: public stub `Assembly/__init__.pyi` line(s) 126.

## `Assembly.AssemblyObject.isPartConnected`

```python
def isPartConnected(self, obj: DocumentObject, /) -> bool:
```

Check if a part is connected to the ground through joints.
Returns: True if part is connected to ground.

Evidence: public stub `Assembly/__init__.pyi` line(s) 132.

## `Assembly.AssemblyObject.isJointConnectingPartToGround`

```python
def isJointConnectingPartToGround(self, joint: DocumentObject, prop_name: str, /) -> Any:
```

Check if a joint is connecting a part to the ground.

Args:
- joint: document object of the joint to check.
- prop_name: string 'Part1' or 'Part2' of the joint.

Returns: True if part is connected to ground.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Assembly/__init__.pyi` line(s) 139.

## `Assembly.AssemblyObject.isPartGrounded`

```python
def isPartGrounded(self, obj: DocumentObject, /) -> Any:
```

Check if a part has a grounded joint.

Args:
- obj: document object of the part to check.

Returns: True if part has grounded joint.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Assembly/__init__.pyi` line(s) 151.

## `Assembly.AssemblyObject.exportAsASMT`

```python
def exportAsASMT(self, file_name: str, /) -> None:
```

Export the assembly in a text format called ASMT.

Args:
- fileName: The name of the file where the ASMT will be exported.

Evidence: public stub `Assembly/__init__.pyi` line(s) 162.

## `Assembly.AssemblyObject.getDownstreamParts`

```python
def getDownstreamParts(self, start_part: DocumentObject, joint_to_ignore: DocumentObject, /) -> list[DocumentObject]:
```

Finds all parts connected to a start_part that are not connected to ground
when a specific joint is ignored.

This is used to find the entire rigid group of unconstrained components that
should be moved together during a pre-solve operation or a drag.

Args:
    start_part: The App.DocumentObject to begin the search from.
    joint_to_ignore: The App.DocumentObject (a joint) to temporarily
                     suppress during the connectivity check.

Returns:
    A list of App.DocumentObject instances representing the downstream parts.

Evidence: public stub `Assembly/__init__.pyi` line(s) 171.

## `Assembly.AssemblyObject.Joints`

```python
Joints: Final[list]
```

A list of all joints this assembly has.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Assembly/__init__.pyi` line(s) 188.

