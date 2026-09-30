# `Part.ShapeFix.Solid`

[Module](index.md)

```python
class Solid(Root):
```

Root class for fixing operations

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 714. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.Solid.FixShellMode`

```python
FixShellMode: bool = ...
```

Mode for applying fixes of ShapeFix_Shell

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 721.

## `Part.ShapeFix.Solid.FixShellOrientationMode`

```python
FixShellOrientationMode: bool = ...
```


    Mode for applying analysis and fixes of
    orientation of shells in the solid
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 723.

## `Part.ShapeFix.Solid.CreateOpenSolidMode`

```python
CreateOpenSolidMode: bool = ...
```

Mode for creation of solids

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 725.

## `Part.ShapeFix.Solid.init`

```python
def init(self, solid: TopoShapeSolid, /) -> None:
```

Initializes by solid

Evidence: public stub `Part/ShapeFix.pyi` line(s) 728.

## `Part.ShapeFix.Solid.perform`

```python
def perform(self) -> bool:
```

Iterates on subshapes and performs fixes

Evidence: public stub `Part/ShapeFix.pyi` line(s) 734.

## `Part.ShapeFix.Solid.solidFromShell`

```python
def solidFromShell(self, shell: TopoShapeShell, /) -> TopoShape:
```

Calls MakeSolid and orients the solid to be not infinite

Evidence: public stub `Part/ShapeFix.pyi` line(s) 740.

## `Part.ShapeFix.Solid.solid`

```python
def solid(self) -> TopoShape:
```

Returns resulting solid

Evidence: public stub `Part/ShapeFix.pyi` line(s) 746.

## `Part.ShapeFix.Solid.shape`

```python
def shape(self) -> TopoShape:
```

In case of multiconnexity returns compound of fixed solids
else returns one solid

Evidence: public stub `Part/ShapeFix.pyi` line(s) 752.

## `Part.ShapeFix.Solid.fixShellTool`

```python
def fixShellTool(self) -> Shell:
```

Returns tool for fixing shells

Evidence: public stub `Part/ShapeFix.pyi` line(s) 759.

