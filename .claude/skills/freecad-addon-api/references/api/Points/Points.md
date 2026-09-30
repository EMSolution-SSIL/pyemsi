# `Points.Points`

[Module](index.md)

```python
class Points(object):
```

Points() -- Create an empty points object.

This class allows one to manipulate the Points object by adding new points, deleting facets, importing from an STL file,
transforming and much more.

Author: Juergen Riegel (Juergen.Riegel@web.de)
License: LGPL-2.1-or-later

Evidence: public stub `Points/__init__.pyi` line 33. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Points.Points.copy`

```python
def copy(self) -> Any:
```

Create a copy of this points object

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Points/__init__.pyi` line(s) 44.

## `Points.Points.read`

```python
def read(self, filename: str, /) -> None:
```

Read in a points object from file.

Evidence: public stub `Points/__init__.pyi` line(s) 48.

## `Points.Points.write`

```python
def write(self, filename: str, /) -> None:
```

Write the points object into file.

Evidence: public stub `Points/__init__.pyi` line(s) 52.

## `Points.Points.writeInventor`

```python
def writeInventor(self) -> Any:
```

Write the points in OpenInventor format to a string.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Points/__init__.pyi` line(s) 56.

## `Points.Points.addPoints`

```python
def addPoints(self, points: Sequence[Vector | tuple[float, float, float]], /) -> None:
```

Add one or more points to the object

Evidence: public stub `Points/__init__.pyi` line(s) 60.

## `Points.Points.fromSegment`

```python
def fromSegment(self, indices: Sequence[int], /) -> 'Points.Points':
```

Get a new point object from a given segment

Evidence: public stub `Points/__init__.pyi` line(s) 64.

## `Points.Points.fromValid`

```python
def fromValid(self) -> Any:
```

Get a new point object from points with valid coordinates (i.e. that are not NaN)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Points/__init__.pyi` line(s) 68.

## `Points.Points.CountPoints`

```python
CountPoints: Final[int]
```

Return the number of vertices of the points object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Points/__init__.pyi` line(s) 71.

## `Points.Points.Points`

```python
Points: Final[list]
```

A collection of points
With this attribute it is possible to get access to the points of the object

for p in pnt.Points:
	print p

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Points/__init__.pyi` line(s) 73.

