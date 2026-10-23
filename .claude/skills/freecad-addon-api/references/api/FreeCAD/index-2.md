# `FreeCAD`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `FreeCAD/__init__.pyi`; generated binding/typing declarations, runtime unverified.

[part 1](index.md) | [part 2](index-2.md)

## `FreeCAD.getHelpDir`

```python
def getHelpDir() -> str:
```

Return the directory that contains bundled help resources.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 382.

## `FreeCAD.getHomePath`

```python
def getHomePath() -> str:
```

Return the current FreeCAD home directory.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 386.

## `FreeCAD.getImportType`

```python
@overload
def getImportType() -> _FileTypeModules:

@overload
def getImportType(extension: str, /) -> list[str]:
```

Return the full extension-to-module map for all registered importers.

Return the importer modules registered for one specific extension.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 391, 396.

## `FreeCAD.getLastCrashReport`

```python
def getLastCrashReport() -> CrashReport | None:
```

If the last run of FreeCAD crashed, this will return the most recent crash report.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 400.

## `FreeCAD.getLibraryDir`

```python
def getLibraryDir() -> str:
```

Return the directory that contains FreeCAD shared libraries.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 404.

## `FreeCAD.getLinksTo`

```python
def getLinksTo(obj: DocumentObject | None=None, options: int=0, maxCount: int=0, /) -> tuple[DocumentObject, ...]:
```

Return objects that link to the given object.

``options & 1`` searches recursively. ``options & 2`` checks link arrays.
``maxCount`` limits the number of returned links.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 408.

## `FreeCAD.getLogLevel`

```python
def getLogLevel(tag: str, /) -> int:
```

Return the numeric level of one named log channel.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 417.

## `FreeCAD.getResourceDir`

```python
def getResourceDir() -> str:
```

Return the root resource directory shipped with FreeCAD.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 421.

## `FreeCAD.getTempPath`

```python
def getTempPath() -> str:
```

Return the temporary directory used by FreeCAD.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 425.

## `FreeCAD.getUserAppDataDir`

```python
def getUserAppDataDir() -> str:
```

Return the user application-data directory.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 429.

## `FreeCAD.getUserCachePath`

```python
def getUserCachePath() -> str:
```

Return the user cache directory used by FreeCAD.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 433.

## `FreeCAD.getUserConfigDir`

```python
def getUserConfigDir() -> str:
```

Return the user configuration directory.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 437.

## `FreeCAD.getUserMacroDir`

```python
def getUserMacroDir(actual: bool=False, /) -> str:
```

Return the standard user macro directory, or the effective user-defined path.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 441.

## `FreeCAD.isRestoring`

```python
def isRestoring() -> bool:
```

Return whether FreeCAD is currently restoring document state.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 445.

## `FreeCAD.listDocuments`

```python
def listDocuments(sort: bool=False, /) -> dict[str, Document]:
```

Return the loaded documents keyed by name, optionally sorted by dependency order.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 449.

## `FreeCAD.loadFile`

```python
def loadFile(path: str, doc: str='', module: str='', /) -> None:
```

Load one file by delegating to an importer module.

When ``module`` is empty, FreeCAD chooses an importer from the file extension.
If several importers match, the first registered importer is used; if none
matches, an exception is raised.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 453.

## `FreeCAD.newDocument`

```python
def newDocument(name: str | None=None, label: str | None=None, hidden: bool=False, temp: bool=False) -> Document:
```

Create and return a new document.

``name`` is the internal document name and is made unique automatically.
``label`` is the optional user-changeable label. ``hidden`` suppresses
creation of the document 3D view. ``temp`` marks the document as temporary
so it is not saved.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 463.

## `FreeCAD.open`

```python
def open(name: str, hidden: bool=False, temporary: bool=False) -> Document:
```

Open a document file and return the created document; see ``openDocument``.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 474.

## `FreeCAD.openDocument`

```python
def openDocument(name: str, hidden: bool=False, temporary: bool=False) -> Document:
```

Create a document, load an existing project file, and return it.

``hidden`` suppresses creation of the document 3D view. ``temporary`` hides
the document in the tree view. An I/O exception is raised when the file does
not exist or cannot be loaded. Non-file restore failures may leave the
created document open for recovery.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 478.

## `FreeCAD.removeDocumentObserver`

```python
def removeDocumentObserver(observer: object, /) -> None:
```

Unregister one document observer object.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 489.

## `FreeCAD.saveParameter`

```python
def saveParameter(name: str='User parameter', /) -> None:
```

Persist one named parameter tree to disk, defaulting to the user parameter set.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 493.

## `FreeCAD.setActiveDocument`

```python
def setActiveDocument(name: str, /) -> None:
```

Make one named document the active document.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 497.

## `FreeCAD.setActiveTransaction`

```python
def setActiveTransaction(name: str, persist: bool=False, /) -> int:
```

Start or select the active transaction and return its identifier.

While active, document changes open transactions with this application-wide
name and identifier. ``persist`` is kept for compatibility and has no effect.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 501.

## `FreeCAD.setLogLevel`

```python
def setLogLevel(tag: str, level: _LogLevelName | int, /) -> None:
```

Set one named log channel to a numeric or named level.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 510.

## `FreeCAD.writeRecoverySnapshotToTransientDir`

```python
def writeRecoverySnapshotToTransientDir(document: Document, /, *, compressed: bool=True, save_binary_brep: bool=True, save_thumbnail: bool=False) -> bool:
```

Write one recovery snapshot for a document into its transient directory.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 514.

