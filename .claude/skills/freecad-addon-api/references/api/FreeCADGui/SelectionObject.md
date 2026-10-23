# `FreeCADGui.SelectionObject`

[Module](index.md)

```python
class SelectionObject(BaseClass):
```

This class represents selections made by the user. It holds information about the object, document and sub-element of the selection.

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 2540. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.SelectionObject.remove`

```python
def remove(self) -> None:
```

Remove this selection item from the selection.

--
This object becomes invalid.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2548.

## `FreeCADGui.SelectionObject.isObjectTypeOf`

```python
def isObjectTypeOf(self, type: Any, /) -> bool:
```

Test for a certain father class.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2557.

## `FreeCADGui.SelectionObject.ObjectName`

```python
ObjectName: Final[str] = ''
```

Name of the selected object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2562.

## `FreeCADGui.SelectionObject.SubElementNames`

```python
SubElementNames: Final[Tuple[str, ...]] = ()
```

Name of the selected sub-element if any

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2564.

## `FreeCADGui.SelectionObject.FullName`

```python
FullName: Final[str] = ''
```

Name of the selected object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2566.

## `FreeCADGui.SelectionObject.TypeName`

```python
TypeName: Final[str] = ''
```

Type name of the selected object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2568.

## `FreeCADGui.SelectionObject.DocumentName`

```python
DocumentName: Final[str] = ''
```

Name of the document of the selected object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2570.

## `FreeCADGui.SelectionObject.Document`

```python
Document: Final[Any] = ...
```

Document of the selected object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2572.

## `FreeCADGui.SelectionObject.Object`

```python
Object: Final[Any] = ...
```

Selected object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2574.

## `FreeCADGui.SelectionObject.SubObjects`

```python
SubObjects: Final[Tuple[Any, ...]] = ()
```

Selected sub-element, if any

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2576.

## `FreeCADGui.SelectionObject.PickedPoints`

```python
PickedPoints: Final[Tuple[Any, ...]] = ()
```

Picked points for selection

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2578.

## `FreeCADGui.SelectionObject.HasSubObjects`

```python
HasSubObjects: Final[bool] = False
```

Selected sub-element, if any

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2580.

