# `Sketcher.SketchGeometryExtension`

[Module](index.md)

```python
class SketchGeometryExtension(GeometryExtension):
```

Describes a SketchGeometryExtension

Author: Abdullah Tahiri (abdullah.tahiri.yo@gmail.com)
Licence: LGPL

Evidence: public stub `Sketcher/__init__.pyi` line 410. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Sketcher.SketchGeometryExtension.Id`

```python
Id: int = 0
```

Returns the Id of the SketchGeometryExtension.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 417.

## `Sketcher.SketchGeometryExtension.InternalType`

```python
InternalType: str = ''
```

Returns the Id of the SketchGeometryExtension.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 419.

## `Sketcher.SketchGeometryExtension.Blocked`

```python
Blocked: bool = False
```

Sets/returns whether the geometry is blocked or not.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 421.

## `Sketcher.SketchGeometryExtension.Construction`

```python
Construction: bool = False
```

Sets/returns this geometry as a construction one, which will not be part of a later built shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 423.

## `Sketcher.SketchGeometryExtension.GeometryLayerId`

```python
GeometryLayerId: int = 0
```

Returns the Id of the geometry Layer in which the geometry is located.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 425.

## `Sketcher.SketchGeometryExtension.testGeometryMode`

```python
def testGeometryMode(self, mode: str, /) -> bool:
```

Returns a boolean indicating whether the given bit is set.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 428.

## `Sketcher.SketchGeometryExtension.setGeometryMode`

```python
def setGeometryMode(self, mode: str, on: bool=..., /) -> None:
```

Sets the given bit to true/false.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 434.

