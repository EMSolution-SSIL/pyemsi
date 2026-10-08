# `TechDraw.CenterLine`

[Module](index.md)

```python
class CenterLine:
```

CenterLine specifies additional mark up edges in a View

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 125. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.CenterLine.clone`

```python
def clone(self) -> Any:
```

Create a clone of this centerline

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 133.

## `TechDraw.CenterLine.copy`

```python
def copy(self) -> Any:
```

Create a copy of this centerline

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 137.

## `TechDraw.CenterLine.Tag`

```python
Tag: Final[str]
```

Gives the tag of the CenterLine as string.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 140.

## `TechDraw.CenterLine.Type`

```python
Type: Final[int]
```

0 - face, 1 - 2 line, 2 - 2 point.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 142.

## `TechDraw.CenterLine.Mode`

```python
Mode: int
```

0 - vert/ 1 - horiz/ 2 - aligned.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 144.

## `TechDraw.CenterLine.Format`

```python
Format: dict[str, Any]
```

The appearance attributes (style, color, weight, visible) for this CenterLine.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 146.

## `TechDraw.CenterLine.HorizShift`

```python
HorizShift: float
```

The left/right offset for this CenterLine.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 148.

## `TechDraw.CenterLine.VertShift`

```python
VertShift: float
```

The up/down offset for this CenterLine.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 150.

## `TechDraw.CenterLine.Rotation`

```python
Rotation: float
```

The rotation of the Centerline in degrees.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 152.

## `TechDraw.CenterLine.Extension`

```python
Extension: float
```

The additional length to be added to this CenterLine.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 154.

## `TechDraw.CenterLine.Flip`

```python
Flip: bool
```

Reverse the order of points for 2 point CenterLine.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 156.

## `TechDraw.CenterLine.Edges`

```python
Edges: list[Any]
```

The names of source edges for this CenterLine.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 158.

## `TechDraw.CenterLine.Faces`

```python
Faces: list[Any]
```

The names of source Faces for this CenterLine.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 160.

## `TechDraw.CenterLine.Points`

```python
Points: list[Any]
```

The names of source Points for this CenterLine.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 162.

