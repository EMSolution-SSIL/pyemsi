# `Part.Geom2d.Geometry2d`

[Module](index.md)

```python
class Geometry2d:
```

The abstract class Geometry for 2D space is the root class of all geometric objects.
It describes the common behavior of these objects when:
- applying geometric transformations to objects, and
- constructing objects by geometric transformation (including copying).

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 1013. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.Geometry2d.mirror`

```python
def mirror(self, point: Any, axis: Any=..., /) -> None:
```

Performs the symmetrical transformation of this geometric object.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1024.

## `Part.Geom2d.Geometry2d.rotate`

```python
def rotate(self, point: Any, angle: float, /) -> None:
```

Rotates this geometric object at angle Ang (in radians) around a point.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1030.

## `Part.Geom2d.Geometry2d.scale`

```python
def scale(self, point: Any, factor: float, /) -> None:
```

Applies a scaling transformation on this geometric object with a center and scaling factor.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1036.

## `Part.Geom2d.Geometry2d.transform`

```python
def transform(self, matrix: Any, /) -> None:
```

Applies a transformation to this geometric object.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1042.

## `Part.Geom2d.Geometry2d.translate`

```python
def translate(self, offset: Any, /) -> None:
```

Translates this geometric object.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1048.

## `Part.Geom2d.Geometry2d.copy`

```python
def copy(self) -> 'Geometry2d':
```

Create a copy of this geometry.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1054.

