# `AssemblyGui.ViewProviderAssembly`

[Module](index.md)

```python
class ViewProviderAssembly(ViewProvider):
```

This is the ViewProviderAssembly class

Author: Ondsel (development@ondsel.com)
License: LGPL-2.1-or-later

Evidence: public stub `AssemblyGui/__init__.pyi` line 11. Inherited members are on the named base's reference; aliases keep their imported identity.

## `AssemblyGui.ViewProviderAssembly.isInEditMode`

```python
def isInEditMode(self) -> Any:
```

Return true if the assembly object is currently in edit mode.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `AssemblyGui/__init__.pyi` line(s) 19.

## `AssemblyGui.ViewProviderAssembly.getDragger`

```python
def getDragger(self) -> SoTransformDragger:
```

Return the assembly dragger coin object.

Evidence: public stub `AssemblyGui/__init__.pyi` line(s) 25.

## `AssemblyGui.ViewProviderAssembly.isolateComponents`

```python
def isolateComponents(self, components: List[DocumentObject] | Tuple[DocumentObject, ...], mode: int, /) -> None:
```

Temporarily isolates a given set of components in the 3D view.
Other components are faded or hidden based on the specified mode.

Args:
    components (List[DocumentObject] | Tuple[DocumentObject, ...]):
        A list or tuple of DocumentObjects to isolate.
    mode (int): An integer specifying the isolation mode:
        - 0: Transparent
        - 1: Wireframe
        - 2: Hidden

Evidence: public stub `AssemblyGui/__init__.pyi` line(s) 29.

## `AssemblyGui.ViewProviderAssembly.clearIsolate`

```python
def clearIsolate(self) -> None:
```

Restores the visual state of all components, clearing any active isolation.

Evidence: public stub `AssemblyGui/__init__.pyi` line(s) 44.

## `AssemblyGui.ViewProviderAssembly.EnableMovement`

```python
EnableMovement: bool
```

Enable moving the parts by clicking and dragging.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `AssemblyGui/__init__.pyi` line(s) 49.

## `AssemblyGui.ViewProviderAssembly.MoveOnlyPreselected`

```python
MoveOnlyPreselected: bool
```

If enabled, only the preselected object will move.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `AssemblyGui/__init__.pyi` line(s) 51.

## `AssemblyGui.ViewProviderAssembly.MoveInCommand`

```python
MoveInCommand: bool
```

If enabled, each move will be wrapped in a command.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `AssemblyGui/__init__.pyi` line(s) 53.

## `AssemblyGui.ViewProviderAssembly.DraggerVisibility`

```python
DraggerVisibility: bool
```

Show or hide the assembly dragger.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `AssemblyGui/__init__.pyi` line(s) 55.

## `AssemblyGui.ViewProviderAssembly.DraggerPlacement`

```python
DraggerPlacement: Any
```

Placement of the assembly dragger object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `AssemblyGui/__init__.pyi` line(s) 57.

