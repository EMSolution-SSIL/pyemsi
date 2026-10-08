# `Robot.Trajectory`

[Module](index.md)

```python
class Trajectory(Persistence):
```

Trajectory class

Author: Juergen Riegel (Juergen.Riegel@web.de)
License: LGPL-2.1-or-later

Evidence: public stub `Robot/__init__.pyi` line 194. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Robot.Trajectory.insertWaypoints`

```python
def insertWaypoints(self, waypoint: Placement | Waypoint | list[Waypoint], /) -> Trajectory:
```

adds one or a list of waypoint to the end of the trajectory

Evidence: public stub `Robot/__init__.pyi` line(s) 202.

## `Robot.Trajectory.position`

```python
def position(self, pos: float, /) -> Placement:
```

returns a Frame to a given time in the trajectory

Evidence: public stub `Robot/__init__.pyi` line(s) 206.

## `Robot.Trajectory.velocity`

```python
def velocity(self, pos: float, /) -> float:
```

returns the velocity to a given time in the trajectory

Evidence: public stub `Robot/__init__.pyi` line(s) 210.

## `Robot.Trajectory.deleteLast`

```python
def deleteLast(self, n: int=..., /) -> Trajectory:
```

deleteLast(n) - delete n waypoints at the end
deleteLast()  - delete the last waypoint

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Robot/__init__.pyi` line(s) 214.

## `Robot.Trajectory.Duration`

```python
Duration: Final[float]
```

duration of the trajectory

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 220.

## `Robot.Trajectory.Length`

```python
Length: Final[float]
```

length of the trajectory

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 222.

## `Robot.Trajectory.Waypoints`

```python
Waypoints: list[Waypoint]
```

waypoints of this trajectory

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 224.

