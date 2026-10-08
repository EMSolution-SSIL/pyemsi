# `TechDraw.CosmeticVertex`

[Module](index.md)

```python
class CosmeticVertex:
```

CosmeticVertex specifies an extra (cosmetic) vertex in Views

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 193. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.CosmeticVertex.clone`

```python
def clone(self) -> Any:
```

Create a clone of this CosmeticVertex

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 201.

## `TechDraw.CosmeticVertex.copy`

```python
def copy(self) -> Any:
```

Create a copy of this CosmeticVertex

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 205.

## `TechDraw.CosmeticVertex.Tag`

```python
Tag: Final[str]
```

Gives the tag of the CosmeticVertex as string.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 208.

## `TechDraw.CosmeticVertex.Point`

```python
Point: Any
```

Gives the position of this CosmeticVertex as vector.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 210.

## `TechDraw.CosmeticVertex.Show`

```python
Show: bool
```

Show/hide the vertex.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 212.

## `TechDraw.CosmeticVertex.Color`

```python
Color: Any
```

set/return the vertex's colour using a tuple (rgba).

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 214.

## `TechDraw.CosmeticVertex.Size`

```python
Size: Any
```

set/return the vertex's radius in mm.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 216.

## `TechDraw.CosmeticVertex.Style`

```python
Style: Any
```

set/return the vertex's style as integer.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 218.

