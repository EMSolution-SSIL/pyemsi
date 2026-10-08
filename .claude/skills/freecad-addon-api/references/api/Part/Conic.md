# `Part.Conic`

[Module](index.md)

```python
class Conic(Curve):
```

Describes an abstract conic in 3d space

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 2112. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Conic.Location`

```python
Location: Vector = ...
```

Location of the conic.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2119.

## `Part.Conic.Center`

```python
@property
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use Location instead.')
def Center(self) -> Vector:

@Center.setter
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use Location instead.')
def Center(self, value: Vector) -> None:
```

Deprecated -- use Location.

Access: getter and setter declared in the stub.

Evidence: public stub `Part/__init__.pyi` line(s) 2124, 2130.

## `Part.Conic.Eccentricity`

```python
Eccentricity: Final[float] = ...
```


    Returns the eccentricity value of the conic e.
    e = 0 for a circle
    0 < e < 1 for an ellipse  (e = 0 if MajorRadius = MinorRadius)
    e > 1 for a hyperbola
    e = 1 for a parabola
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2132.

## `Part.Conic.AngleXU`

```python
AngleXU: float = ...
```

The angle between the X axis and the major axis of the conic.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2134.

## `Part.Conic.Axis`

```python
Axis: Vector = ...
```

The axis direction of the circle

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2136.

## `Part.Conic.XAxis`

```python
XAxis: Vector = ...
```

The X axis direction of the circle

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2138.

## `Part.Conic.YAxis`

```python
YAxis: Vector = ...
```

The Y axis direction of the circle

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2140.

