# `Part.Geom2d.ArcOfConic2d`

[Module](index.md)

```python
class ArcOfConic2d(Curve2d):
```

Describes an abstract arc of conic in 2d space.

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 33. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.ArcOfConic2d.Location`

```python
Location: object = ...
```

Location of the conic.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 40.

## `Part.Geom2d.ArcOfConic2d.Eccentricity`

```python
Eccentricity: Final[float] = ...
```


    returns the eccentricity value of the conic e.
    e = 0 for a circle
    0 < e < 1 for an ellipse  (e = 0 if MajorRadius = MinorRadius)
    e > 1 for a hyperbola
    e = 1 for a parabola
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 42.

## `Part.Geom2d.ArcOfConic2d.XAxis`

```python
XAxis: object = ...
```

The X axis direction of the circle.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 44.

## `Part.Geom2d.ArcOfConic2d.YAxis`

```python
YAxis: object = ...
```

The Y axis direction of the circle.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 46.

