# `Part.ShapeFix.FixSmallSolid`

[Module](index.md)

```python
class FixSmallSolid(Root):
```

Fixing solids with small size

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 507. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.FixSmallSolid.setFixMode`

```python
def setFixMode(self, theMode: int, /) -> None:
```

Set working mode for operator:
- theMode = 0 use both WidthFactorThreshold and VolumeThreshold parameters
- theMode = 1 use only WidthFactorThreshold parameter
- theMode = 2 use only VolumeThreshold parameter

Evidence: public stub `Part/ShapeFix.pyi` line(s) 515.

## `Part.ShapeFix.FixSmallSolid.setVolumeThreshold`

```python
def setVolumeThreshold(self, value: float=-1.0, /) -> None:
```

Set or clear volume threshold for small solids

Evidence: public stub `Part/ShapeFix.pyi` line(s) 524.

## `Part.ShapeFix.FixSmallSolid.setWidthFactorThreshold`

```python
def setWidthFactorThreshold(self, value: float=-1.0, /) -> None:
```

Set or clear width factor threshold for small solids

Evidence: public stub `Part/ShapeFix.pyi` line(s) 530.

## `Part.ShapeFix.FixSmallSolid.remove`

```python
def remove(self, shape: TopoShape, /) -> TopoShape:
```

Remove small solids from the given shape

Evidence: public stub `Part/ShapeFix.pyi` line(s) 536.

## `Part.ShapeFix.FixSmallSolid.merge`

```python
def merge(self, shape: TopoShape, /) -> TopoShape:
```

Merge small solids in the given shape to adjacent non-small ones

Evidence: public stub `Part/ShapeFix.pyi` line(s) 542.

