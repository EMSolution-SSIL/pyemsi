# `FreeCAD.Document`

[Module](index.md)

```python
class Document(PropertyContainer):
```

This is the Document class.

Evidence: public stub `FreeCAD/__init__.pyi` line 945. Inherited members are on the named base's reference; aliases keep their imported identity.

[part 1](Document.md) | [part 2](Document-2.md) | [part 3](Document-3.md)

## `FreeCAD.Document.DependencyGraph`

```python
DependencyGraph: Final[str] = ''
```

The dependency graph as GraphViz text

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 949.

## `FreeCAD.Document.ActiveObject`

```python
ActiveObject: Final[DocumentObject] = ...
```

The last created object in this document

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 951.

## `FreeCAD.Document.Objects`

```python
Objects: Final[list[DocumentObject]] = []
```

The list of objects in this document

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 953.

## `FreeCAD.Document.TopologicalSortedObjects`

```python
TopologicalSortedObjects: Final[list[DocumentObject]] = []
```

The list of objects in this document in topological sorted order

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 955.

## `FreeCAD.Document.RootObjects`

```python
RootObjects: Final[list[DocumentObject]] = []
```

The list of root objects in this document

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 957.

## `FreeCAD.Document.RootObjectsIgnoreLinks`

```python
RootObjectsIgnoreLinks: Final[list[DocumentObject]] = []
```

The list of root objects in this document ignoring references from links.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 959.

## `FreeCAD.Document.UndoMode`

```python
UndoMode: int = 0
```

The Undo mode of the Document (0 = no Undo, 1 = Undo/Redo)

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 961.

## `FreeCAD.Document.UndoRedoMemSize`

```python
UndoRedoMemSize: Final[int] = 0
```

The size of the Undo stack in byte

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 963.

## `FreeCAD.Document.UndoCount`

```python
UndoCount: Final[int] = 0
```

Number of possible Undos

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 965.

## `FreeCAD.Document.RedoCount`

```python
RedoCount: Final[int] = 0
```

Number of possible Redos

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 967.

## `FreeCAD.Document.UndoNames`

```python
UndoNames: Final[list[str]] = []
```

A list of Undo names

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 969.

## `FreeCAD.Document.RedoNames`

```python
RedoNames: Final[list[str]] = []
```

A List of Redo names

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 971.

## `FreeCAD.Document.Name`

```python
Name: Final[str] = ''
```

The internal name of the document

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 973.

## `FreeCAD.Document.RecomputesFrozen`

```python
RecomputesFrozen: bool = False
```

Returns or sets if automatic recomputes for this document are disabled.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 975.

## `FreeCAD.Document.HasPendingTransaction`

```python
HasPendingTransaction: Final[bool] = False
```

Check if there is a pending transaction

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 977.

## `FreeCAD.Document.InList`

```python
InList: Final[list[Document]] = []
```

A list of all documents that link to this document.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 979.

## `FreeCAD.Document.OutList`

```python
OutList: Final[list[Document]] = []
```

A list of all documents that this document links to.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 981.

## `FreeCAD.Document.Restoring`

```python
Restoring: Final[bool] = False
```

Indicate if the document is restoring

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 983.

## `FreeCAD.Document.Partial`

```python
Partial: Final[bool] = False
```

Indicate if the document is partially loaded

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 985.

## `FreeCAD.Document.Importing`

```python
Importing: Final[bool] = False
```

Indicate if the document is importing. Note the document will also report Restoring while importing

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 987.

## `FreeCAD.Document.Recomputing`

```python
Recomputing: Final[bool] = False
```

Indicate if the document is recomputing

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 989.

## `FreeCAD.Document.Transacting`

```python
Transacting: Final[bool] = False
```

Indicate whether the document is undoing/redoing

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 991.

## `FreeCAD.Document.OldLabel`

```python
OldLabel: Final[str] = ''
```

Contains the old label before change

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 993.

## `FreeCAD.Document.Temporary`

```python
Temporary: Final[bool] = False
```

Check if this is a temporary document

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 995.

## `FreeCAD.Document.Comment`

```python
@property
def Comment(self) -> str:

@Comment.setter
def Comment(self, value: str) -> None:
```

Additional tag to save a comment

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 999, 1004.

## `FreeCAD.Document.Company`

```python
@property
def Company(self) -> str:

@Company.setter
def Company(self, value: str) -> None:
```

Additional tag to save the name of the company

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1008, 1013.

## `FreeCAD.Document.CreatedBy`

```python
@property
def CreatedBy(self) -> str:

@CreatedBy.setter
def CreatedBy(self, value: str) -> None:
```

The creator of the document

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1017, 1022.

## `FreeCAD.Document.CreationDate`

```python
@property
def CreationDate(self) -> str:

@CreationDate.setter
def CreationDate(self, value: str) -> None:
```

Date of creation

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1026, 1031.

## `FreeCAD.Document.FileName`

```python
@property
def FileName(self) -> str:

@FileName.setter
def FileName(self, value: str) -> None:
```

The path to the file where the document is saved to

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1035, 1040.

## `FreeCAD.Document.Id`

```python
@property
def Id(self) -> str:

@Id.setter
def Id(self, value: str) -> None:
```

ID of the document

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1044, 1049.

## `FreeCAD.Document.Label`

```python
@property
def Label(self) -> str:

@Label.setter
def Label(self, value: str) -> None:
```

The name of the document

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1053, 1058.

## `FreeCAD.Document.LastModifiedBy`

```python
@property
def LastModifiedBy(self) -> str:

@LastModifiedBy.setter
def LastModifiedBy(self, value: str) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1062, 1066.

## `FreeCAD.Document.LastModifiedDate`

```python
@property
def LastModifiedDate(self) -> str:

@LastModifiedDate.setter
def LastModifiedDate(self, value: str) -> None:
```

Date of last modification

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1070, 1075.

## `FreeCAD.Document.License`

```python
@property
def License(self) -> str:

@License.setter
def License(self, value: str) -> None:
```

License string of the Item

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1079, 1084.

## `FreeCAD.Document.LicenseURL`

```python
@property
def LicenseURL(self) -> str:

@LicenseURL.setter
def LicenseURL(self, value: str) -> None:
```

URL to the license text/contract

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1088, 1093.

## `FreeCAD.Document.Material`

```python
@property
def Material(self) -> dict[str, str]:

@Material.setter
def Material(self, value: dict[str, str]) -> None:
```

Map with material properties

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1097, 1102.

## `FreeCAD.Document.Meta`

```python
@property
def Meta(self) -> dict[str, str]:

@Meta.setter
def Meta(self, value: dict[str, str]) -> None:
```

Map with additional meta information

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1106, 1111.

## `FreeCAD.Document.ShowHidden`

```python
@property
def ShowHidden(self) -> bool:

@ShowHidden.setter
def ShowHidden(self, value: bool | int) -> None:
```

Whether to show hidden object items in the tree view

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1115, 1120.

## `FreeCAD.Document.Tip`

```python
@property
def Tip(self) -> DocumentObject | None:

@Tip.setter
def Tip(self, value: DocumentObject | None) -> None:
```

Link of the tip object of the document

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1124, 1129.

## `FreeCAD.Document.TipName`

```python
@property
def TipName(self) -> str:

@TipName.setter
def TipName(self, value: str) -> None:
```

Link of the tip object of the document

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1133, 1138.

## `FreeCAD.Document.TransientDir`

```python
@property
def TransientDir(self) -> str:

@TransientDir.setter
def TransientDir(self, value: str) -> None:
```

Transient directory, where the files live while the document is open

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1142, 1147.

## `FreeCAD.Document.Uid`

```python
@property
def Uid(self) -> str:

@Uid.setter
def Uid(self, value: str) -> None:
```

UUID of the document

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1151, 1156.

## `FreeCAD.Document.UnitSystem`

```python
@property
def UnitSystem(self) -> str:

@UnitSystem.setter
def UnitSystem(self, value: str | list[str]) -> None:
```

Unit system to use in this project

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1160, 1165.

## `FreeCAD.Document.UseHasher`

```python
@property
def UseHasher(self) -> bool:

@UseHasher.setter
def UseHasher(self, value: bool | int) -> None:
```

Whether to use hasher on topological naming

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1169, 1174.

## `FreeCAD.Document.save`

```python
def save(self) -> None:
```

Save the document to disk.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1177.

## `FreeCAD.Document.saveAs`

```python
def saveAs(self, path: str, /) -> None:
```

Save the document under a new name to disk.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1183.

## `FreeCAD.Document.saveCopy`

```python
def saveCopy(self, path: str, /) -> None:
```

Save a copy of the document under a new name to disk.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1189.

## `FreeCAD.Document.canWriteRecoverySnapshot`

```python
def canWriteRecoverySnapshot(self) -> bool:
```

Return whether the document is in an App-side state that allows writing
a recovery snapshot.

This does not account for GUI-only constraints such as an active Gui
transaction.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1195.

## `FreeCAD.Document.load`

```python
def load(self, path: str, /) -> None:
```

Load the document from the given path.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1205.

## `FreeCAD.Document.restore`

```python
def restore(self) -> None:
```

Restore the document from disk

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1211.

## `FreeCAD.Document.isSaved`

```python
def isSaved(self) -> bool:
```

Checks if the document is saved

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1217.

## `FreeCAD.Document.getProgramVersion`

```python
def getProgramVersion(self) -> str:
```

Get the program version that a project file was created with

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1223.

## `FreeCAD.Document.getFileName`

```python
def getFileName(self) -> str:
```

For a regular document it returns its file name property.
For a temporary document it returns its transient directory.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1229.

## `FreeCAD.Document.settings`

```python
def settings(self, namespace: str, /) -> DocumentSettings:
```

Return document-persisted settings for a namespace backed by this document's Meta map.

The namespace may contain dot-separated identifier segments.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1236.

## `FreeCAD.Document.getUniqueObjectName`

```python
def getUniqueObjectName(self, objName: str, /) -> str:
```

Return the same name, or the name made unique, for Example Box -> Box002 if there are conflicting name
already in the document.

Args:
    objName: Object name candidate.

Returns:
    Unique object name based on objName.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1244.

## `FreeCAD.Document.mergeProject`

```python
def mergeProject(self, path: str, /) -> None:
```

Merges this document with another project file.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1257.

## `FreeCAD.Document.exportGraphviz`

```python
def exportGraphviz(self, path: str=..., /) -> str | None:
```

Export the dependencies of the objects as graph.

If path is passed, graph is written to it. if not a string is returned.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1263.

## `FreeCAD.Document.openTransaction`

```python
def openTransaction(self, name: str=..., /) -> None:
```

Open a new Undo/Redo transaction.

This function no long creates a new transaction, but calls
FreeCAD.setActiveTransaction(name) instead, which will auto creates a
transaction with the given name when any change happened in any opened document.
If more than one document is changed, all newly created transactions will have
the same internal ID and will be undo/redo together.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1271.

## `FreeCAD.Document.abortTransaction`

```python
def abortTransaction(self) -> None:
```

Abort an Undo/Redo transaction (rollback)

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1283.

## `FreeCAD.Document.commitTransaction`

```python
def commitTransaction(self) -> None:
```

Commit an Undo/Redo transaction

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1289.

