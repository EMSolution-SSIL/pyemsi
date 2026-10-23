# `Part.ShapeFix.Shell`

[Module](index.md)

```python
class Shell(Root):
```

Root class for fixing operations

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 634. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.Shell.FixOrientationMode`

```python
FixOrientationMode: bool = ...
```

Mode for applying fixes of orientation of faces

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 641.

## `Part.ShapeFix.Shell.FixFaceMode`

```python
FixFaceMode: bool = ...
```

Mode for applying fixes using ShapeFix_Face

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 643.

## `Part.ShapeFix.Shell.init`

```python
def init(self, shell: TopoShapeShell, /) -> None:
```

Initializes by shell

Evidence: public stub `Part/ShapeFix.pyi` line(s) 646.

## `Part.ShapeFix.Shell.fixFaceTool`

```python
def fixFaceTool(self) -> Face:
```

Returns tool for fixing faces

Evidence: public stub `Part/ShapeFix.pyi` line(s) 652.

## `Part.ShapeFix.Shell.perform`

```python
def perform(self) -> bool:
```

Iterates on subshapes and performs fixes

Evidence: public stub `Part/ShapeFix.pyi` line(s) 658.

## `Part.ShapeFix.Shell.shell`

```python
def shell(self) -> TopoShape:
```

Returns fixed shell (or subset of oriented faces)

Evidence: public stub `Part/ShapeFix.pyi` line(s) 664.

## `Part.ShapeFix.Shell.numberOfShells`

```python
def numberOfShells(self) -> int:
```

Returns the number of obtained shells

Evidence: public stub `Part/ShapeFix.pyi` line(s) 670.

## `Part.ShapeFix.Shell.shape`

```python
def shape(self) -> TopoShape:
```

In case of multiconnexity returns compound of fixed shells and one shell otherwise

Evidence: public stub `Part/ShapeFix.pyi` line(s) 676.

## `Part.ShapeFix.Shell.errorFaces`

```python
def errorFaces(self) -> TopoShape:
```

Returns not oriented subset of faces

Evidence: public stub `Part/ShapeFix.pyi` line(s) 682.

## `Part.ShapeFix.Shell.fixFaceOrientation`

```python
def fixFaceOrientation(self, shell: TopoShapeShell, multi_conex: bool=..., non_manifold: bool=..., /) -> bool:
```

Fixes orientation of faces in shell.
Changes orientation of face in the shell, if it is oriented opposite
to neighbouring faces. If it is not possible to orient all faces in the
shell (like in case of mebious band), this method orients only subset
of faces. Other faces are stored in Error compound.
Modes :
isAccountMultiConex - mode for account cases of multiconnexity.
If this mode is equal to Standard_True, separate shells will be created
in the cases of multiconnexity. If this mode is equal to Standard_False,
one shell will be created without account of multiconnexity. By default - Standard_True;
NonManifold - mode for creation of non-manifold shells.
If this mode is equal to Standard_True one non-manifold will be created from shell
contains multishared edges. Else if this mode is equal to Standard_False only
manifold shells will be created. By default - Standard_False.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 688.

## `Part.ShapeFix.Shell.setNonManifoldFlag`

```python
def setNonManifoldFlag(self, non_manifold: bool, /) -> None:
```

Sets NonManifold flag

Evidence: public stub `Part/ShapeFix.pyi` line(s) 707.

