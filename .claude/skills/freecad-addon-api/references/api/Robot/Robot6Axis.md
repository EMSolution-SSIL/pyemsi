# `Robot.Robot6Axis`

[Module](index.md)

```python
class Robot6Axis(Persistence):
```

Robot6Axis class

Author: Juergen Riegel (Juergen.Riegel@web.de)
License: LGPL-2.1-or-later

Evidence: public stub `Robot/__init__.pyi` line 17. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Robot.Robot6Axis.check`

```python
def check(self) -> Any:
```

Checks the shape and report errors in the shape structure.
This is a more detailed check as done in isValid().

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Robot/__init__.pyi` line(s) 25.

## `Robot.Robot6Axis.Axis1`

```python
Axis1: float
```

Pose of Axis 1 in degrees

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 29.

## `Robot.Robot6Axis.Axis2`

```python
Axis2: float
```

Pose of Axis 2 in degrees

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 31.

## `Robot.Robot6Axis.Axis3`

```python
Axis3: float
```

Pose of Axis 3 in degrees

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 33.

## `Robot.Robot6Axis.Axis4`

```python
Axis4: float
```

Pose of Axis 4 in degrees

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 35.

## `Robot.Robot6Axis.Axis5`

```python
Axis5: float
```

Pose of Axis 5 in degrees

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 37.

## `Robot.Robot6Axis.Axis6`

```python
Axis6: float
```

Pose of Axis 6 in degrees

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 39.

## `Robot.Robot6Axis.Tcp`

```python
Tcp: Any
```

Tool center point frame. Where the tool of the robot is

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Robot/__init__.pyi` line(s) 41.

## `Robot.Robot6Axis.Base`

```python
Base: Any
```

Actual Base system in respect to the robot world system

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Robot/__init__.pyi` line(s) 43.

