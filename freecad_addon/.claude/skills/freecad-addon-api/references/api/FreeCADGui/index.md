# `FreeCADGui`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `FreeCADGui/__init__.pyi`; generated binding/typing declarations, runtime unverified.

[part 1](index.md) | [part 2](index-2.md)

## Classes

- [FreeCADGui._View3DObjectInfo](_View3DObjectInfo.md)
- [FreeCADGui._View3DRayInfo](_View3DRayInfo.md)
- [FreeCADGui._View3DEventInfo](_View3DEventInfo.md)
- [FreeCADGui.UserInput](UserInput.md)
- [FreeCADGui._WorkbenchBackend](_WorkbenchBackend.md)
- [FreeCADGui.Workbench](Workbench.md)
- [FreeCADGui.InputHint](InputHint.md)
- [FreeCADGui._HintManager](_HintManager.md)
- [FreeCADGui._AbstractSplitView](_AbstractSplitView.md)
- [FreeCADGui._Control](_Control.md)
- [FreeCADGui._MDIView](_MDIView.md)
- [FreeCADGui._MainWindow](_MainWindow.md)
- [FreeCADGui._PyResource](_PyResource.md)
- [FreeCADGui._TaskDialog](_TaskDialog.md)
- [FreeCADGui.TaskPlacement](TaskPlacement.md)
- [FreeCADGui.UiLoader](UiLoader.md)
- [FreeCADGui._View3DInventor](_View3DInventor.md)
- [FreeCADGui._View3DInventorViewer](_View3DInventorViewer.md)
- [FreeCADGui.AxisOrigin](AxisOrigin.md)
- [FreeCADGui.Command](Command.md)
- [FreeCADGui.Document](Document.md)
- [FreeCADGui.EditableDatumLabel](EditableDatumLabel.md)
- [FreeCADGui.LinkView](LinkView.md)
- [FreeCADGui.NavigationStyle](NavigationStyle.md)
- [FreeCADGui.PythonWorkbench](PythonWorkbench.md)
- [FreeCADGui.SelectionObject](SelectionObject.md)
- [FreeCADGui.ViewProvider](ViewProvider.md)
- [FreeCADGui.ViewProviderDocumentObject](ViewProviderDocumentObject.md)
- [FreeCADGui.ViewProviderExtension](ViewProviderExtension.md)
- [FreeCADGui.ViewProviderGeometryObject](ViewProviderGeometryObject.md)
- [FreeCADGui.ViewProviderLink](ViewProviderLink.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from typing_extensions import deprecated
import FreeCAD as App
from collections.abc import Sequence
from enum import IntEnum
from typing import ClassVar, Literal, Protocol, TypeAlias
from Base.Metadata import bootstrap_export, module, typing_only
from FreeCAD import DocumentObject
import PySide.QtWidgets as QtWidgets
from typing import TypedDict
from FreeCAD import Rotation
from os import PathLike
from typing import Any, overload
from typing_extensions import deprecated
from FreeCAD.Base import BaseClass
from typing import Tuple
from typing import Dict
from typing import Final
from typing import Optional
from typing import List
from FreeCAD.Base import Persistence
from FreeCAD.Base import Matrix
from typing import overload
from FreeCAD.Base import Placement
from FreeCAD.Base import Vector
from typing import Callable
from FreeCAD.Base import BoundBox
import FreeCADGui
from FreeCAD import ExtensionContainer
import enum
from FreeCAD import Extension
from typing import TYPE_CHECKING
from FreeCAD import DocumentObject as _DocumentObject
```

## `FreeCADGui._Pathish`

```python
_Pathish: TypeAlias = str | bytes | bytearray
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 13.

## `FreeCADGui._IconContent`

```python
_IconContent: TypeAlias = str | bytes | bytearray | memoryview
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 14.

## `FreeCADGui._WorkbenchMenu`

```python
_WorkbenchMenu: TypeAlias = str | Sequence[str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 15.

## `FreeCADGui._WorkbenchCommands`

```python
_WorkbenchCommands: TypeAlias = str | Sequence[str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 16.

## `FreeCADGui._ActiveObjectReference`

```python
_ActiveObjectReference: TypeAlias = tuple[DocumentObject, DocumentObject, str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 18.

## `FreeCADGui._EmptyActiveObjectReference`

```python
_EmptyActiveObjectReference: TypeAlias = tuple[None, None, str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 19.

## `FreeCADGui._PyResourceValue`

```python
_PyResourceValue: TypeAlias = str | int | float | bool | list[str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 20.

## `FreeCADGui._Point2`

```python
_Point2: TypeAlias = tuple[int, int]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 23.

## `FreeCADGui._Point3`

```python
_Point3: TypeAlias = tuple[float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 24.

## `FreeCADGui._Quaternion`

```python
_Quaternion: TypeAlias = tuple[float, float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 25.

## `FreeCADGui._ViewOrientation`

```python
_ViewOrientation: TypeAlias = Literal['Top', 'Bottom', 'Front', 'Rear', 'Left', 'Right', 'Isometric', 'Dimetric', 'Trimetric', 'Custom'] | str
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 26.

## `FreeCADGui._CameraType`

```python
_CameraType: TypeAlias = Literal['Orthographic', 'Perspective'] | int | str
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 27.

## `FreeCADGui._DraggerCallbackType`

```python
_DraggerCallbackType: TypeAlias = Literal['addFinishCallback', 'addStartCallback', 'addMotionCallback', 'addValueChangedCallback']
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 28.

## `FreeCADGui._Color`

```python
_Color: TypeAlias = tuple[float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 29.

## `FreeCADGui._View3DEventCallback`

```python
_View3DEventCallback: TypeAlias = Callable[[_View3DEventInfo], object]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 66.

## `FreeCADGui._View3DProxyCallback`

```python
_View3DProxyCallback: TypeAlias = Callable[[object], object]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 67.

## `FreeCADGui._InputSequence`

```python
_InputSequence: TypeAlias = UserInput | tuple[UserInput, ...]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 213.

## `FreeCADGui.HintManager`

```python
HintManager: _HintManager
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 369.

## `FreeCADGui.ActiveDocument`

```python
ActiveDocument: Document | None
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 370.

## `FreeCADGui.SendMsgToActiveView`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use View instead.')
def SendMsgToActiveView(name: str, suppress: bool=False, /) -> None:
```

Send one named message to the active view. Deprecated; use view methods instead.

``suppress`` controls whether failure warnings are emitted.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 373.

## `FreeCADGui.activateView`

```python
def activateView(typeName: str, create: bool, /) -> None:
```

Activate one view type, optionally creating it first.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 381.

## `FreeCADGui.activateWorkbench`

```python
def activateWorkbench(name: str, /) -> bool:
```

Activate one registered workbench by name; return False if it is already active.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 385.

## `FreeCADGui.activeDocument`

```python
def activeDocument() -> Document | None:
```

Return the active GUI document, if any.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 389.

## `FreeCADGui.activeView`

```python
@overload
def activeView() -> object | None:

@overload
def activeView(typeName: str, /) -> object | None:
```

Return the current active view, creating the default 3D view when needed.

Return the active view constrained to a specific FreeCAD view type name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 394, 399.

## `FreeCADGui.activeWorkbench`

```python
def activeWorkbench() -> Workbench:
```

Return the currently active workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 403.

## `FreeCADGui.addCommand`

```python
def addCommand(name: str, cmd: object, activation: str='', /) -> None:
```

Register one GUI command object under a command name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 407.

## `FreeCADGui.addDocumentObserver`

```python
def addDocumentObserver(obj: object, /) -> None:
```

Register one GUI document observer.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 411.

## `FreeCADGui.addIcon`

```python
def addIcon(name: str, content: _IconContent, format: str='XPM', /) -> None:
```

Register one icon payload under a symbolic name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 415.

## `FreeCADGui.addIconPath`

```python
def addIconPath(path: _Pathish, /) -> None:
```

Register an additional icon search path.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 419.

## `FreeCADGui.addLanguagePath`

```python
def addLanguagePath(path: _Pathish, /) -> None:
```

Register an additional translation search path.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 423.

## `FreeCADGui.addModule`

```python
def addModule(mod: str, /) -> None:
```

Record one module import in GUI command macros, emitting it only once.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 427.

## `FreeCADGui.addPreferencePage`

```python
@overload
def addPreferencePage(path: str, group: str, /) -> None:

@overload
def addPreferencePage(dialog: type[object], group: str, /) -> None:
```

Register a preference page from a `.ui` file path.

Register a preference page from a Python dialog class.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 432, 437.

## `FreeCADGui.addResourcePath`

```python
def addResourcePath(path: _Pathish, /) -> None:
```

Register an additional GUI resource search path.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 441.

## `FreeCADGui.addWorkbench`

```python
def addWorkbench(workbench: Workbench | type[Workbench], /) -> None:
```

Register one Python workbench implementation.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 445.

## `FreeCADGui.addWorkbenchManipulator`

```python
def addWorkbenchManipulator(obj: object, /) -> None:
```

Register one workbench manipulator helper.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 449.

## `FreeCADGui.applyElementColorOverride`

```python
def applyElementColorOverride(target: object, colors: dict[str, object], /) -> None:
```

Apply secondary element color overrides to one Coin node or path.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 453.

## `FreeCADGui.clearElementColorOverride`

```python
def clearElementColorOverride(target: object, /) -> None:
```

Clear secondary element color overrides from one Coin node or path.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 457.

## `FreeCADGui.coinRemoveAllChildren`

```python
def coinRemoveAllChildren(node: object, /) -> None:
```

Remove all Coin child nodes from one parent node.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 461.

## `FreeCADGui.createDialog`

```python
def createDialog(path: str, /) -> _PyResource:
```

Load one Qt Designer UI resource and return its wrapper.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 465.

## `FreeCADGui.createViewer`

```python
@overload
def createViewer() -> _View3DInventor:

@overload
def createViewer(views: Literal[1], name: str=..., /) -> _View3DInventor:

@overload
def createViewer(views: int, name: str=..., /) -> _View3DInventor | _AbstractSplitView:
```

Create the default single 3D viewer.

Create one named 3D viewer explicitly.

Create a split-view layout when more than one view is requested.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 470, 475, 480.

## `FreeCADGui.doCommand`

```python
def doCommand(cmd: str, /) -> None:
```

Print, record, and execute one Python command in the main console context.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 484.

## `FreeCADGui.doCommandEval`

```python
def doCommandEval(cmd: str, /) -> Any:
```

Evaluate one Python expression without printing or recording it, and return the result.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 488.

## `FreeCADGui.doCommandGui`

```python
def doCommandGui(cmd: str, /) -> None:
```

Print, record as GUI-scoped, and execute one Python command.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 492.

## `FreeCADGui.doCommandSkip`

```python
def doCommandSkip(cmd: str, /) -> None:
```

Record one command in the macro stream without executing it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 496.

## `FreeCADGui.editDocument`

```python
def editDocument() -> Document | None:
```

Return the document currently being edited in the GUI.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 500.

## `FreeCADGui.embedToWindow`

```python
def embedToWindow(pointer: str, /) -> None:
```

Embed the GUI into an existing native window handle.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 504.

## `FreeCADGui.exec_loop`

```python
def exec_loop() -> None:
```

Enter the GUI event loop and block until it terminates.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 508.

## `FreeCADGui.export`

```python
def export(objs: Sequence[DocumentObject], fileName: _Pathish, /) -> None:
```

Export GUI document objects to a scene file such as Inventor or VRML.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 512.

## `FreeCADGui.exportSubgraph`

```python
def exportSubgraph(node: object, output: object, format: str='VRML', /) -> None:
```

Serialize one Coin scene subgraph to an output target as VRML or Inventor.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 516.

## `FreeCADGui.getDocument`

```python
def getDocument(doc: str | App.Document, /) -> Document:
```

Return one GUI document by name or application document.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 520.

## `FreeCADGui.getIcon`

```python
def getIcon(name: str, /) -> object | None:
```

Return the cached icon object for one symbolic name, or None for a null icon.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 524.

## `FreeCADGui.getLocale`

```python
def getLocale() -> str:
```

Return the current GUI locale name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 528.

## `FreeCADGui.getMainWindow`

```python
def getMainWindow() -> _MainWindow:
```

Return the main application window wrapper.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 532.

## `FreeCADGui.getMarkerIndex`

```python
def getMarkerIndex(marker: str, size: int=9, /) -> int:
```

Return the Coin marker index for one named marker and size.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 536.

## `FreeCADGui.getSoDBVersion`

```python
def getSoDBVersion() -> str:
```

Return the linked Coin SoDB version string.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 540.

## `FreeCADGui.getUserEditMode`

```python
def getUserEditMode() -> str:
```

Return the current user edit-mode name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 544.

## `FreeCADGui.getWorkbench`

```python
def getWorkbench(name: str, /) -> Workbench:
```

Return one registered workbench by name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 548.

## `FreeCADGui.hide`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use hideObject instead.')
def hide(name: str, /) -> None:
```

Hide one named object in the active GUI document. Deprecated.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 553.

## `FreeCADGui.hideObject`

```python
def hideObject(obj: DocumentObject, /) -> None:
```

Hide one document object in the GUI.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 557.

## `FreeCADGui.insert`

```python
def insert(fileName: _Pathish, docName: str='', /) -> None:
```

Insert a macro, Inventor, VRML, or GUI-supported file into a document.

When ``docName`` is omitted, the active document is used.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 561.

## `FreeCADGui.isCommandActive`

```python
def isCommandActive(name: str, /) -> bool:
```

Return whether one command is active in the current GUI context.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 569.

## `FreeCADGui.isIconCached`

```python
def isIconCached(name: str, /) -> bool:
```

Return whether one icon name is already cached.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 573.

## `FreeCADGui.listCommands`

```python
def listCommands() -> list[str]:
```

Return the registered GUI command names.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 577.

## `FreeCADGui.listUserEditModes`

```python
def listUserEditModes() -> list[str]:
```

Return the available user edit-mode names.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 581.

## `FreeCADGui.listWorkbenches`

```python
def listWorkbenches() -> dict[str, Workbench]:
```

Return all registered workbenches keyed by name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 585.

## `FreeCADGui.loadFile`

```python
def loadFile(fileName: str, module: str='', /) -> None:
```

Load one file through the GUI import pipeline.

When ``module`` is empty, FreeCAD chooses an importer from the file extension.
If several importers match, the first registered importer is used; if none
matches, an exception is raised.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 589.

## `FreeCADGui.open`

```python
def open(fileName: _Pathish, /) -> None:
```

Open a macro, Inventor, VRML, or other GUI-supported file.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 599.

## `FreeCADGui.reload`

```python
def reload(name: str, /) -> App.Document | None:
```

Reload a partially opened document by name, or return None when it is not open.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 603.

## `FreeCADGui.removeDocumentObserver`

```python
def removeDocumentObserver(obj: object, /) -> None:
```

Unregister one GUI document observer.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 607.

## `FreeCADGui.removeWorkbench`

```python
def removeWorkbench(name: str, /) -> None:
```

Unregister one workbench by name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 611.

## `FreeCADGui.removeWorkbenchManipulator`

```python
def removeWorkbenchManipulator(obj: object, /) -> None:
```

Unregister one workbench manipulator helper.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 615.

## `FreeCADGui.resumeWaitCursor`

```python
def resumeWaitCursor() -> None:
```

Resume the application's wait cursor and event filter.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 619.

## `FreeCADGui.runCommand`

```python
def runCommand(name: str, index: int=0, /) -> None:
```

Run one registered GUI command.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 623.

## `FreeCADGui.sendMsgToFocusView`

```python
def sendMsgToFocusView(name: str, suppress: bool=False, /) -> None:
```

Send one named message to the focused view, optionally suppressing failure warnings.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 627.

## `FreeCADGui.setActiveDocument`

```python
def setActiveDocument(doc: str | App.Document, /) -> None:
```

Make one GUI document active.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 631.

## `FreeCADGui.setLocale`

```python
def setLocale(name: str, /) -> None:
```

Set the GUI locale by language name or top-level domain code.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 635.

## `FreeCADGui.setUserEditMode`

```python
def setUserEditMode(mode: str, /) -> bool:
```

Set the current user edit-mode by name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 639.

## `FreeCADGui.setupWithoutGUI`

```python
def setupWithoutGUI() -> None:
```

Initialize GUI services without showing the main window or running the event loop.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 643.

