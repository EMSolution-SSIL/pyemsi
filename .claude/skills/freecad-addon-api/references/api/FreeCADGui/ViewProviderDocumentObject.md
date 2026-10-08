# `FreeCADGui.ViewProviderDocumentObject`

[Module](index.md)

```python
class ViewProviderDocumentObject(ViewProvider):
```

This is the ViewProvider base class

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 2877. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.ViewProviderDocumentObject.DisplayMode`

```python
@property
def DisplayMode(self) -> str:

@DisplayMode.setter
def DisplayMode(self, value: str | list[str]) -> None:
```

Set the display mode

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2886, 2891.

## `FreeCADGui.ViewProviderDocumentObject.OnTopWhenSelected`

```python
@property
def OnTopWhenSelected(self) -> str:

@OnTopWhenSelected.setter
def OnTopWhenSelected(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2895, 2899.

## `FreeCADGui.ViewProviderDocumentObject.SelectionStyle`

```python
@property
def SelectionStyle(self) -> str:

@SelectionStyle.setter
def SelectionStyle(self, value: str | list[str]) -> None:
```

Set the object selection style

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2903, 2908.

## `FreeCADGui.ViewProviderDocumentObject.ShowInTree`

```python
@property
def ShowInTree(self) -> bool:

@ShowInTree.setter
def ShowInTree(self, value: bool | int) -> None:
```

Show the object in the tree view

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2912, 2917.

## `FreeCADGui.ViewProviderDocumentObject.Visibility`

```python
@property
def Visibility(self) -> bool:

@Visibility.setter
def Visibility(self, value: bool | int) -> None:
```

Show the object in the 3d view

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2921, 2926.

## `FreeCADGui.ViewProviderDocumentObject.update`

```python
def update(self) -> None:
```

Update the view representation of the object

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2929.

## `FreeCADGui.ViewProviderDocumentObject.Object`

```python
Object: _DocumentObject = ...
```

Set/Get the associated data object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2934.

## `FreeCADGui.ViewProviderDocumentObject.ForceUpdate`

```python
ForceUpdate: bool = False
```

Reference count to force update visual

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2936.

## `FreeCADGui.ViewProviderDocumentObject.Document`

```python
Document: Final['Document'] = ...
```

Return the document the view provider is part of

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2938.

