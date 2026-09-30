# `Robot.RobotObject`

[Module](index.md)

```python
class RobotObject(DocumentObject):
```

Robot document object

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
License: LGPL-2.1-or-later

Evidence: public stub `Robot/__init__.pyi` line 46. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Robot.RobotObject.Axis1`

```python
@property
def Axis1(self) -> float:

@Axis1.setter
def Axis1(self, value: float) -> None:
```

Axis 1 angle of the robot in degre

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 55, 60.

## `Robot.RobotObject.Axis2`

```python
@property
def Axis2(self) -> float:

@Axis2.setter
def Axis2(self, value: float) -> None:
```

Axis 2 angle of the robot in degre

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 64, 69.

## `Robot.RobotObject.Axis3`

```python
@property
def Axis3(self) -> float:

@Axis3.setter
def Axis3(self, value: float) -> None:
```

Axis 3 angle of the robot in degre

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 73, 78.

## `Robot.RobotObject.Axis4`

```python
@property
def Axis4(self) -> float:

@Axis4.setter
def Axis4(self, value: float) -> None:
```

Axis 4 angle of the robot in degre

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 82, 87.

## `Robot.RobotObject.Axis5`

```python
@property
def Axis5(self) -> float:

@Axis5.setter
def Axis5(self, value: float) -> None:
```

Axis 5 angle of the robot in degre

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 91, 96.

## `Robot.RobotObject.Axis6`

```python
@property
def Axis6(self) -> float:

@Axis6.setter
def Axis6(self, value: float) -> None:
```

Axis 6 angle of the robot in degre

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 100, 105.

## `Robot.RobotObject.Base`

```python
@property
def Base(self) -> Base.Placement:

@Base.setter
def Base(self, value: Base.Placement | Base.Matrix) -> None:
```

Actual base frame of the robot

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 109, 114.

## `Robot.RobotObject.Error`

```python
@property
def Error(self) -> str:

@Error.setter
def Error(self, value: str) -> None:
```

Robot error while moving

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 118, 123.

## `Robot.RobotObject.Home`

```python
@property
def Home(self) -> list[float]:

@Home.setter
def Home(self, value: Sequence[float]) -> None:
```

Axis position for home

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 127, 132.

## `Robot.RobotObject.RobotKinematicFile`

```python
@property
def RobotKinematicFile(self) -> str:

@RobotKinematicFile.setter
def RobotKinematicFile(self, value: _FileInput | dict[str, str] | tuple[str | bytes, str | bytes]) -> None:
```

Included file with kinematic definition of the robot Axis

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 136, 141.

## `Robot.RobotObject.RobotVrmlFile`

```python
@property
def RobotVrmlFile(self) -> str:

@RobotVrmlFile.setter
def RobotVrmlFile(self, value: _FileInput | dict[str, str] | tuple[str | bytes, str | bytes]) -> None:
```

Included file with the VRML representation of the robot

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 145, 150.

## `Robot.RobotObject.Tcp`

```python
@property
def Tcp(self) -> Base.Placement:

@Tcp.setter
def Tcp(self, value: Base.Placement | Base.Matrix) -> None:
```

Tcp of the robot

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 154, 159.

## `Robot.RobotObject.Tool`

```python
@property
def Tool(self) -> Base.Placement:

@Tool.setter
def Tool(self, value: Base.Placement | Base.Matrix) -> None:
```

Tool frame of the robot (Tool)

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 163, 168.

## `Robot.RobotObject.ToolBase`

```python
@property
def ToolBase(self) -> Base.Placement:

@ToolBase.setter
def ToolBase(self, value: Base.Placement | Base.Matrix) -> None:
```

Defines where to connect the ToolShape

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 172, 177.

## `Robot.RobotObject.ToolShape`

```python
@property
def ToolShape(self) -> DocumentObject | None:

@ToolShape.setter
def ToolShape(self, value: DocumentObject | None) -> None:
```

Link to the Shape is used as Tool

Access: getter and setter declared in the stub.

Evidence: public stub `Robot/__init__.pyi` line(s) 181, 186.

## `Robot.RobotObject.getRobot`

```python
def getRobot(self) -> Any:
```

Returns a copy of the robot. Be aware, the robot behaves the same
like the robot of the object but is a copy!

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Robot/__init__.pyi` line(s) 189.

