# `FreeCADGui.Document`

[Module](index.md)

```python
class Document(Persistence):
```

This is a Document class

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 1768. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.Document.show`

```python
def show(self, object_name: str, /) -> None:
```

Show an object.

object_name : str
    Name of the `Gui.ViewProvider` to show.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1776.

## `FreeCADGui.Document.hide`

```python
def hide(self, object_name: str, /) -> None:
```

Hide an object.

object_name : str
    Name of the `Gui.ViewProvider` to hide.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1785.

## `FreeCADGui.Document.setPos`

```python
def setPos(self, object_name: str, matrix: Matrix, /) -> None:
```

Set the position of an object.

object_name : str
    Name of the `Gui.ViewProvider`.

matrix : Base.Matrix
    Transformation to apply on the object.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1794.

## `FreeCADGui.Document.setEdit`

```python
def setEdit(self, obj: str | DocumentObject | _ViewProvider, mode: int=0, subname: str=..., /) -> bool:
```

Set an object in edit mode.

obj : str, App.DocumentObject, Gui.ViewPrivider
    Object to set in edit mode.
mode : int
    Edit mode.
subname : str
    Subelement name. Optional.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1806.

## `FreeCADGui.Document.getInEdit`

```python
def getInEdit(self) -> Optional[Any]:
```

Returns the current object in edit mode or None if there is no such object.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1819.

## `FreeCADGui.Document.resetEdit`

```python
def resetEdit(self) -> None:
```

End the current editing.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1825.

## `FreeCADGui.Document.addAnnotation`

```python
def addAnnotation(self, name: str, filename: str, mode: str='Main', /) -> None:
```

Add an Inventor object from a file.

name : str
    Annotation name.
filename : str
    File name.
mode : str
    Display mode name. Optional.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1831.

## `FreeCADGui.Document.update`

```python
def update(self) -> None:
```

Update the view representations of all objects.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1844.

## `FreeCADGui.Document.getObject`

```python
def getObject(self, name: str, /) -> Optional[Any]:
```

Return the object with the given name. If no one exists, return None.

name : str
    Object name.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1850.

## `FreeCADGui.Document.activeObject`

```python
def activeObject(self) -> Optional[Any]:
```

The active object of the document. Deprecated, use ActiveObject.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1859.

## `FreeCADGui.Document.activeView`

```python
def activeView(self) -> Optional[Any]:
```

The active view of the document. Deprecated, use ActiveView.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1865.

## `FreeCADGui.Document.createView`

```python
def createView(self, type: str, /) -> Optional[Any]:
```

Return a newly created view of a given type.

type : str
    Type name.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1871.

## `FreeCADGui.Document.mdiViewsOfType`

```python
def mdiViewsOfType(self, type: str, /) -> List[Any]:
```

Return a list of mdi views of a given type.

type : str
    Type name.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1880.

## `FreeCADGui.Document.save`

```python
def save(self) -> bool:
```

Attempts to save the document

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1889.

## `FreeCADGui.Document.saveAs`

```python
def saveAs(self) -> bool:
```

Attempts to save the document under a new name

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1895.

## `FreeCADGui.Document.sendMsgToViews`

```python
def sendMsgToViews(self, msg: str, /) -> None:
```

Send a message to all views of the document.

msg : str

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1901.

## `FreeCADGui.Document.mergeProject`

```python
def mergeProject(self, filename: str, /) -> None:
```

Merges this document with another project file.

filename : str
    File name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1909.

## `FreeCADGui.Document.toggleTreeItem`

```python
def toggleTreeItem(self, obj: DocumentObject, mode: int=0, subname: str=..., /) -> None:
```

Change TreeItem of a document object.

obj : App.DocumentObject
mode : int
    Item mode.
    0: Toggle, 1: Collapse, 2: Expand, 3: Expand path.
subname : str
    Subelement name. Optional.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1918.

## `FreeCADGui.Document.scrollToTreeItem`

```python
def scrollToTreeItem(self, obj: _ViewProviderDocumentObject, /) -> None:
```

Scroll the tree view to the item of a view object.

obj : Gui.ViewProviderDocumentObject

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1931.

## `FreeCADGui.Document.toggleInSceneGraph`

```python
def toggleInSceneGraph(self, obj: _ViewProvider, /) -> None:
```

Add or remove view object from scene graph of all views depending
on its canAddToSceneGraph().

obj : Gui.ViewProvider

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1939.

## `FreeCADGui.Document.openCommand`

```python
def openCommand(self, name: str) -> int:
```

openCommand(name) -> int

Opens a named transaction for the document and returns it's
id or 0 on failure

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1948.

## `FreeCADGui.Document.commitCommand`

```python
def commitCommand(self) -> None:
```

commitCommand() -> None

Commits the current transaction of the document

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1957.

## `FreeCADGui.Document.abortCommand`

```python
def abortCommand(self) -> None:
```

abortCommand() -> None

Aborts the current transaction of the document

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1965.

## `FreeCADGui.Document.ActiveObject`

```python
ActiveObject: Any = ...
```

The active object of the document.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1972.

## `FreeCADGui.Document.ActiveView`

```python
ActiveView: Any = ...
```

The active view of the document.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1974.

## `FreeCADGui.Document.EditingTransform`

```python
EditingTransform: Any = ...
```

The editing transformation matrix.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1976.

## `FreeCADGui.Document.InEditInfo`

```python
InEditInfo: Any = ...
```

A tuple(obj,subname,subElement,editMode) of editing object reference, or None if no object is in edit.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1978.

## `FreeCADGui.Document.EditMode`

```python
EditMode: Final[int] = 0
```

Current edit mode. Only meaningful when there is a current object in edit.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1980.

## `FreeCADGui.Document.Document`

```python
Document: Final[Any] = ...
```

The related App document to this Gui document.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1982.

## `FreeCADGui.Document.Transacting`

```python
Transacting: Final[bool] = False
```

Indicate whether the document is undoing/redoing.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1984.

## `FreeCADGui.Document.Modified`

```python
Modified: bool = False
```

Returns True if the document is marked as modified, and False otherwise.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1986.

## `FreeCADGui.Document.TreeRootObjects`

```python
TreeRootObjects: Final[List[Any]] = []
```

The list of tree root objects.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1988.

