# Python source module `Path.Geom`

[Python catalogue](../../index.md)

Evidence: `src/Mod/CAM/Path/Geom.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## `Path.Geom.removeDuplicateEdges`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeDuplicateEdges(wire):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:776`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.flipEdge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def flipEdge(edge):
```

flipEdge(edge)
Flips given edge around so the new Vertexes[0] was the old Vertexes[-1] and vice versa, without changing the shape.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:867`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.flipWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def flipWire(wire):
```

Flip the entire wire and all its edges so it is being processed the other way around.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:882`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.makeBoundBoxFace`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeBoundBoxFace(bBox, offset=0.0, zHeight=0.0):
```

makeBoundBoxFace(bBox, offset=0.0, zHeight=0.0)...
Function to create boundbox face, with possible extra offset and custom Z-height.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:890`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.combineHorizontalFaces`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def combineHorizontalFaces(faces, keepOrder=False):
```

combineHorizontalFaces(faces)...
This function successfully identifies and combines multiple connected faces and
works on multiple independent faces with multiple connected faces within the list.
The return value is a list of simplified faces.
The Adaptive op is not concerned with which hole edges belong to which face.

Attempts to do the same shape connecting failed with TechDraw.findShapeOutline() and
Path.Geom.combineConnectedShapes(), so this algorithm was created.

If keepOrder is True, returns shapes with original order

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:907`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`Path.Geom.__title__`, `Path.Geom.__author__`, `Path.Geom.__url__`, `Path.Geom.__doc__`, `Path.Geom._flipEdge`. These are source internals unless an explicit export establishes otherwise.

