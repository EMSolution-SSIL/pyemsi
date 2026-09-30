# `Mesh.MeshPoint`

[Module](index.md)

```python
class MeshPoint:
```

Point in mesh
This is a point in a MeshObject. You can get it by e.g. iterating a
mesh. The point has a connection to its mesh and allows therefore
topological operations. It is also possible to create an unbounded mesh point e.g. to create
a mesh. In this case the topological operations will fail. The same is
when you cut the bound to the mesh by calling unbound().

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
License: LGPL-2.1-or-later

Evidence: public stub `Mesh/__init__.pyi` line 812. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Mesh.MeshPoint.unbound`

```python
def unbound(self) -> Any:
```

method unbound()
Cut the connection to a MeshObject. The point becomes
free and is more or less a simple vector/point.
After calling unbound() no topological operation will
work!

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 825.

## `Mesh.MeshPoint.Index`

```python
Index: Final[int]
```

The index of this point in the MeshObject

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 832.

## `Mesh.MeshPoint.Bound`

```python
Bound: Final[bool]
```

Bound state of the point

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 834.

## `Mesh.MeshPoint.Normal`

```python
Normal: Final[Any]
```

Normal vector of the point computed by the surrounding mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 836.

## `Mesh.MeshPoint.Vector`

```python
Vector: Final[Any]
```

Vector of the point.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 838.

## `Mesh.MeshPoint.x`

```python
x: Final[float]
```

The X component of the point.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 840.

## `Mesh.MeshPoint.y`

```python
y: Final[float]
```

The Y component of the point.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 842.

## `Mesh.MeshPoint.z`

```python
z: Final[float]
```

The Z component of the point.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 844.

