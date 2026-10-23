# `Robot.Waypoint`

[Module](index.md)

```python
class Waypoint(Persistence):
```

Waypoint class

Author: Juergen Riegel (Juergen.Riegel@web.de)
License: LGPL-2.1-or-later

Evidence: public stub `Robot/__init__.pyi` line 227. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Robot.Waypoint.Name`

```python
Name: str
```

Name of the waypoint

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 234.

## `Robot.Waypoint.Type`

```python
Type: str
```

Type of the waypoint[PTP|LIN|CIRC|WAIT]

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 236.

## `Robot.Waypoint.Pos`

```python
Pos: Any
```

End position (destination) of the waypoint

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Robot/__init__.pyi` line(s) 238.

## `Robot.Waypoint.Cont`

```python
Cont: bool
```

Control the continuity to the next waypoint in the trajectory

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 240.

## `Robot.Waypoint.Velocity`

```python
Velocity: float
```

Control the velocity to the next waypoint in the trajectory
In Case of PTP 0-100% Axis speed
In Case of LIN m/s
In Case of WAIT s wait time

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 242.

## `Robot.Waypoint.Tool`

```python
Tool: int
```

Describe which tool frame to use for that point

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 244.

## `Robot.Waypoint.Base`

```python
Base: int
```

Describe which Base frame to use for that point

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Robot/__init__.pyi` line(s) 246.

