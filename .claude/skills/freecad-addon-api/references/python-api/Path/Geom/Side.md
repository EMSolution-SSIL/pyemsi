# `Path.Geom.Side`

[Source module](index.md)

```python
class Side:
```

Class to determine and define the side a Path is on, or Vectors are in relation to each other.

Evidence: `src/Mod/CAM/Path/Geom.py:52`. Source-defined class; runtime behavior and support status unverified.

## `Path.Geom.Side.Left`

Status: source-defined name; no independently verified stability/export guarantee.

```python
Left = +1
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:55`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.Side.Right`

Status: source-defined name; no independently verified stability/export guarantee.

```python
Right = -1
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:56`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.Side.Straight`

Status: source-defined name; no independently verified stability/export guarantee.

```python
Straight = 0
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:57`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.Side.On`

Status: source-defined name; no independently verified stability/export guarantee.

```python
On = 0
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:58`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.Side.toString`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@classmethod
def toString(cls, side):
```

toString(side)
Returns a string representation of the enum value.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:61`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.Side.of`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@classmethod
def of(cls, ptRef, pt):
```

of(ptRef, pt)
Determine the side of pt in relation to ptRef.
If both Points are viewed as vectors with their origin in (0,0,0)
then the two vectors either form a straight line (On) or pt
lies in the left or right hemisphere in regards to ptRef.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:71`. Decorators are copied as source expressions and have not been executed.

