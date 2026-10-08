# `FreeCAD`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `FreeCAD/__init__.pyi`; generated binding/typing declarations, runtime unverified.

[part 1](index.md) | [part 2](index-2.md)

## Classes

- [FreeCAD.FCADLogger](FCADLogger.md)
- [FreeCAD.ScaleType](ScaleType.md)
- [FreeCAD.PropertyType](PropertyType.md)
- [FreeCAD.ReturnType](ReturnType.md)
- [FreeCAD._ParameterObserver](_ParameterObserver.md)
- [FreeCAD._ParameterManagerObserver](_ParameterManagerObserver.md)
- [FreeCAD.ParameterGrp](ParameterGrp.md)
- [FreeCAD.ApplicationDirectories](ApplicationDirectories.md)
- [FreeCAD.ComplexGeoData](ComplexGeoData.md)
- [FreeCAD.DepEdge](DepEdge.md)
- [FreeCAD.Document](Document.md)
- [FreeCAD.DocumentObject](DocumentObject.md)
- [FreeCAD.DocumentObjectExtension](DocumentObjectExtension.md)
- [FreeCAD.DocumentObjectGroup](DocumentObjectGroup.md)
- [FreeCAD.DocumentSettings](DocumentSettings.md)
- [FreeCAD.Extension](Extension.md)
- [FreeCAD.ExtensionContainer](ExtensionContainer.md)
- [FreeCAD.GeoFeature](GeoFeature.md)
- [FreeCAD.GeoFeatureGroupExtension](GeoFeatureGroupExtension.md)
- [FreeCAD.GroupExtension](GroupExtension.md)
- [FreeCAD.LinkBaseExtension](LinkBaseExtension.md)
- [FreeCAD.Material](Material.md)
- [FreeCAD.MeasureManager](MeasureManager.md)
- [FreeCAD.Metadata](Metadata.md)
- [FreeCAD.OriginGroupExtension](OriginGroupExtension.md)
- [FreeCAD.Part](Part.md)
- [FreeCAD.PropertyContainer](PropertyContainer.md)
- [FreeCAD.StringHasher](StringHasher.md)
- [FreeCAD.StringID](StringID.md)
- [FreeCAD.SuppressibleExtension](SuppressibleExtension.md)
- [FreeCAD.CrashFrame](CrashFrame.md)
- [FreeCAD.CrashReport](CrashReport.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from collections.abc import Sequence
from typing import Literal, TypeAlias
from Base.Metadata import module
from . import Console as Console
from . import Units as Units
from io import IOBase
from . import Base as Base
from typing import Protocol
import Assembly as _Assembly
import CAM as _CAM
import Fem as _Fem
import Measure as _Measure
import Mesh as _Mesh
import Part as _Part
import PartDesign as _PartDesign
import Robot as _Robot
import Sketcher as _Sketcher
import Spreadsheet as _Spreadsheet
import TechDraw as _TechDraw
from enum import IntEnum
from datetime import datetime
from collections.abc import Callable
from typing import Any
import FreeCAD
from FreeCAD.Base import Persistence
from typing import Final
from typing import overload
from typing import List
from typing import Optional
from typing import Union
from typing import Tuple
from typing_extensions import deprecated
from typing import Dict
from FreeCAD.Base import BaseClass
from typing import TYPE_CHECKING
from FreeCADGui import ViewProviderDocumentObject as _ViewProviderDocumentObject
from .Base import Axis as Axis
from .Base import BoundBox as BoundBox
from .Base import Matrix as Matrix
from .Base import Placement as Placement
from .Base import Rotation as Rotation
from .Base import Vector as Vector
```

## `FreeCAD._FileTypeModules`

```python
_FileTypeModules: TypeAlias = dict[str, str | list[str] | None]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 11.

## `FreeCAD._LogLevelName`

```python
_LogLevelName: TypeAlias = Literal['Default', 'Error', 'Warning', 'Message', 'Log', 'Trace']
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 12.

## `FreeCAD.GuiUp`

```python
GuiUp: int
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 13.

## `FreeCAD.ActiveDocument`

```python
ActiveDocument: Document | None
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 14.

## `FreeCAD.Gui`

```python
Gui: Any
```

Optional GUI module alias installed by GUI initialization; use FreeCADGui for typed APIs.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 15.

## `FreeCAD._DocumentObjectSubLinkPairInput`

```python
_DocumentObjectSubLinkPairInput: TypeAlias = tuple[DocumentObject, str | Sequence[str]] | list[DocumentObject | str | Sequence[str]]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 19.

## `FreeCAD._DocumentObjectLink`

```python
_DocumentObjectLink: TypeAlias = DocumentObject | None
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 20.

## `FreeCAD._DocumentObjectList`

```python
_DocumentObjectList: TypeAlias = list[DocumentObject | None]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 21.

## `FreeCAD._DocumentObjectListInput`

```python
_DocumentObjectListInput: TypeAlias = Sequence[DocumentObject]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 22.

## `FreeCAD._DocumentObjectSubLinkValue`

```python
_DocumentObjectSubLinkValue: TypeAlias = tuple[DocumentObject, list[str]] | None
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 23.

## `FreeCAD._DocumentObjectSubLinkInput`

```python
_DocumentObjectSubLinkInput: TypeAlias = DocumentObject | None | _DocumentObjectSubLinkPairInput
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 24.

## `FreeCAD._DocumentObjectSubLinkListItemInput`

```python
_DocumentObjectSubLinkListItemInput: TypeAlias = DocumentObject | _DocumentObjectSubLinkPairInput
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 25.

## `FreeCAD._DocumentObjectSubLinkList`

```python
_DocumentObjectSubLinkList: TypeAlias = list[tuple[DocumentObject, tuple[str, ...]]]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 26.

## `FreeCAD._DocumentObjectSubLinkListInput`

```python
_DocumentObjectSubLinkListInput: TypeAlias = _DocumentObjectSubLinkInput | Sequence[_DocumentObjectSubLinkListItemInput]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 27.

## `FreeCAD._XLinkListInput`

```python
_XLinkListInput: TypeAlias = _DocumentObjectListInput | _DocumentObjectSubLinkListInput
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 28.

## `FreeCAD._XLinkListValue`

```python
_XLinkListValue: TypeAlias = _DocumentObjectList | _DocumentObjectSubLinkList
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 29.

## `FreeCAD._QuantityInput`

```python
_QuantityInput: TypeAlias = float | str | Base.Quantity | Base.Unit
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 30.

## `FreeCAD._QuantityValueInput`

```python
_QuantityValueInput: TypeAlias = float | str | Base.Quantity
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 31.

## `FreeCAD._IntegerConstraintInput`

```python
_IntegerConstraintInput: TypeAlias = int | dict[str, int] | tuple[int, int, int, int]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 32.

## `FreeCAD._FloatConstraintInput`

```python
_FloatConstraintInput: TypeAlias = float | int | dict[str, float] | tuple[float, float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 33.

## `FreeCAD._VectorValue`

```python
_VectorValue: TypeAlias = Base.Vector
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 34.

## `FreeCAD._VectorInput`

```python
_VectorInput: TypeAlias = Base.Vector | tuple[float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 35.

## `FreeCAD._VectorList`

```python
_VectorList: TypeAlias = list[Base.Vector]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 36.

## `FreeCAD._VectorListInput`

```python
_VectorListInput: TypeAlias = Sequence[_VectorInput]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 37.

## `FreeCAD._StringList`

```python
_StringList: TypeAlias = list[str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 38.

## `FreeCAD._StringListInput`

```python
_StringListInput: TypeAlias = Sequence[str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 39.

## `FreeCAD._FloatList`

```python
_FloatList: TypeAlias = list[float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 40.

## `FreeCAD._FloatListInput`

```python
_FloatListInput: TypeAlias = Sequence[float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 41.

## `FreeCAD._IntegerList`

```python
_IntegerList: TypeAlias = list[int]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 42.

## `FreeCAD._IntegerListInput`

```python
_IntegerListInput: TypeAlias = Sequence[int]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 43.

## `FreeCAD._FileInput`

```python
_FileInput: TypeAlias = str | bytes | IOBase
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 44.

## `FreeCAD._FileIncludedInput`

```python
_FileIncludedInput: TypeAlias = _FileInput | dict[str, str] | tuple[str | bytes, str | bytes]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 45.

## `FreeCAD._ColorValue`

```python
_ColorValue: TypeAlias = tuple[float, float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 46.

## `FreeCAD._ColorInput`

```python
_ColorInput: TypeAlias = int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 47.

## `FreeCAD._XLinkValue`

```python
_XLinkValue: TypeAlias = DocumentObject | tuple[DocumentObject, str | list[str]] | None
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 48.

## `FreeCAD._XLinkInput`

```python
_XLinkInput: TypeAlias = DocumentObject | None | tuple[DocumentObject, str | Sequence[str]] | list[DocumentObject | str | Sequence[str]]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 49.

## `FreeCAD._ParameterValue`

```python
_ParameterValue: TypeAlias = str | int | float | bool
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 51.

## `FreeCAD._ParameterContentTag`

```python
_ParameterContentTag: TypeAlias = Literal['String', 'Integer', 'Float', 'Boolean', 'Unsigned Long']
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 52.

## `FreeCAD._ParameterContent`

```python
_ParameterContent: TypeAlias = tuple[_ParameterContentTag, str, _ParameterValue]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 53.

## `FreeCAD.Logger`

```python
Logger: type[FCADLogger]
```

Tagged logger class installed as FreeCAD.Logger.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 255.

## `FreeCAD.ConfigDump`

```python
def ConfigDump() -> dict[str, str]:
```

Return the current flat application configuration mapping.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 272.

## `FreeCAD.ConfigGet`

```python
def ConfigGet(key: str, /) -> str:
```

Return one application configuration value by key.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 276.

## `FreeCAD.ConfigSet`

```python
def ConfigSet(key: str, value: str, /) -> None:
```

Store one application configuration value by key.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 280.

## `FreeCAD.ParamGet`

```python
def ParamGet(path: str, /) -> ParameterGrp:
```

Return the parameter group rooted at one application preference path.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 284.

## `FreeCAD.Version`

```python
def Version() -> list[str]:
```

Return the FreeCAD version components as strings.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 288.

## `FreeCAD.activeDocument`

```python
def activeDocument() -> Document | None:
```

Return the current active document, if any.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 292.

## `FreeCAD.addDocumentObserver`

```python
def addDocumentObserver(observer: object, /) -> None:
```

Register one document observer object.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 296.

## `FreeCAD.addExportType`

```python
def addExportType(extension: str, module: str, /) -> None:
```

Register one exporter module for a file extension.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 300.

## `FreeCAD.addImportType`

```python
def addImportType(extension: str, module: str, /) -> None:
```

Register one importer module for a file extension.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 304.

## `FreeCAD.addTranslatableExportType`

```python
def addTranslatableExportType(description: str, extensions: list[str], module: str, /) -> None:
```

Register one exporter together with a translated file-dialog description.

``description`` should be registered with the translation system using the
``FileFormat`` context.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 308.

## `FreeCAD.changeExportModule`

```python
def changeExportModule(extension: str, old_module: str, new_module: str, /) -> None:
```

Replace one exporter module registration for a file extension.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 317.

## `FreeCAD.changeImportModule`

```python
def changeImportModule(extension: str, old_module: str, new_module: str, /) -> None:
```

Replace one importer module registration for a file extension.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 321.

## `FreeCAD.checkAbort`

```python
def checkAbort() -> None:
```

Raise ``Base.FreeCADAbort`` when the current operation was aborted.

This only works while a sequencer or Python progress indicator is active,
such as during document restore or recomputation. Users usually request the
abort by pressing Esc.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 325.

## `FreeCAD.checkLinkDepth`

```python
def checkLinkDepth(depth: int, /) -> int:
```

Clamp or validate one proposed link depth value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 335.

## `FreeCAD.clearCrashReports`

```python
def clearCrashReports() -> None:
```

Clear all existing crash reports. Safe to call while holding a crash report.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 339.

## `FreeCAD.closeActiveTransaction`

```python
def closeActiveTransaction(abort: bool=False, id: int=0, /) -> None:
```

Close or abort the current transaction.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 343.

## `FreeCAD.closeDocument`

```python
def closeDocument(document: str | Document, /) -> None:
```

Close one document by name or object.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 347.

## `FreeCAD.getActiveTransaction`

```python
def getActiveTransaction() -> tuple[str, int] | None:
```

Return the current transaction name and identifier, if any.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 351.

## `FreeCAD.getCrashReports`

```python
def getCrashReports() -> list[CrashReport]:
```

Get all "live" crash reports (retained according to the retention policy).

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 355.

## `FreeCAD.getDependentObjects`

```python
def getDependentObjects(obj: DocumentObject | Sequence[DocumentObject], options: int=0, /) -> tuple[DocumentObject, ...]:
```

Return objects that depend on one object or object sequence.

The result includes the input objects. ``options & 1`` sorts the result in
topological order; ``options & 2`` excludes Link-type dependencies.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 359.

## `FreeCAD.getDocument`

```python
def getDocument(name: str, /) -> Document:
```

Return one loaded document by name, raising if no such document exists.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 368.

## `FreeCAD.getExportType`

```python
@overload
def getExportType() -> _FileTypeModules:

@overload
def getExportType(extension: str, /) -> list[str]:
```

Return the full extension-to-module map for all registered exporters.

Return the exporter modules registered for one specific extension.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 373, 378.

