# `PathApp.Path`

[Module](index.md)

```python
class Path(Persistence):
```

Path([commands]): Represents a basic Gcode path
commands (optional) is a list of Path commands

Author: Yorik van Havre (yorik@uncreated.net)
License: LGPL-2.1-or-later

Evidence: public stub `PathApp/__init__.pyi` line 197. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PathApp.Path.addCommands`

```python
@overload
def addCommands(self, command: Command, /) -> Path:

@overload
def addCommands(self, commands: list[Command], /) -> Path:

def addCommands(self, arg: Union[Command, list[Command]], /) -> Path:
```

adds a command or a list of commands at the end of the path

Evidence: public stub `PathApp/__init__.pyi` line(s) 207, 211, 214.

## `PathApp.Path.insertCommand`

```python
def insertCommand(self, command: Command, pos: int=-1, /) -> Path:
```

adds a command at the given position or at the end of the path

Evidence: public stub `PathApp/__init__.pyi` line(s) 218.

## `PathApp.Path.deleteCommand`

```python
def deleteCommand(self, pos: int=-1, /) -> Path:
```

deletes the command found at the given position or from the end of the path

Evidence: public stub `PathApp/__init__.pyi` line(s) 224.

## `PathApp.Path.setFromGCode`

```python
def setFromGCode(self, gcode: str, /) -> None:
```

sets the contents of the path from a gcode string

Evidence: public stub `PathApp/__init__.pyi` line(s) 230.

## `PathApp.Path.getClearedArea`

```python
def getClearedArea(self, diameter: float, zmax: float, bbox: 'PathApp.BoundBox', /) -> Area:
```

Gets the area cleared when a tool of the specified diameter follows the gcode represented in the path, ignoring cleared space above zmax and path segments that don't affect space within the x/y space of bbox.

Evidence: public stub `PathApp/__init__.pyi` line(s) 234.

## `PathApp.Path.toGCode`

```python
def toGCode(self) -> str:
```

returns a gcode string representing the path

Evidence: public stub `PathApp/__init__.pyi` line(s) 238.

## `PathApp.Path.copy`

```python
def copy(self) -> Path:
```

returns a copy of this path

Evidence: public stub `PathApp/__init__.pyi` line(s) 242.

## `PathApp.Path.getCycleTime`

```python
def getCycleTime(self, h_feed: float, v_feed: float, rapid: float, /) -> float:
```

Return the cycle time estimation for this path in s. Parameter F from command overrides feeds from arguments.

Evidence: public stub `PathApp/__init__.pyi` line(s) 246.

## `PathApp.Path.Length`

```python
Length: Final[float]
```

the total length of this path in mm

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 249.

## `PathApp.Path.Size`

```python
Size: Final[int]
```

the number of commands in this path

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 251.

## `PathApp.Path.Commands`

```python
Commands: list
```

the list of commands of this path

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 253.

## `PathApp.Path.Center`

```python
Center: Any
```

the center position for all rotational parameters

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 255.

## `PathApp.Path.BoundBox`

```python
BoundBox: Final[Any]
```

the extent of this path

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 257.

