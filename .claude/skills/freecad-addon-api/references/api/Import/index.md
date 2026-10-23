# `Import`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `Import/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [Import.StepShape](StepShape.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from collections.abc import Sequence
from typing import Literal, TypeAlias, TypedDict
from FreeCAD import DocumentObject
from Part import Feature, Shape
```

## `Import._ColorRGBA`

```python
_ColorRGBA: TypeAlias = tuple[float, float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Import/__init__.pyi` line(s) 10.

## `Import._DxfVersion`

```python
_DxfVersion: TypeAlias = Literal[12, 14]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Import/__init__.pyi` line(s) 11.

## `Import._ImportExportObject`

```python
_ImportExportObject: TypeAlias = DocumentObject | tuple[DocumentObject, Sequence[_ColorRGBA]]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Import/__init__.pyi` line(s) 12.

## `Import._ImportColorAssignments`

```python
_ImportColorAssignments: TypeAlias = list[tuple[Feature, list[_ColorRGBA]]]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Import/__init__.pyi` line(s) 13.

## `Import._UnsupportedFeatureOccurrences`

```python
_UnsupportedFeatureOccurrences: TypeAlias = dict[str, list[tuple[int, str]]]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Import/__init__.pyi` line(s) 14.

## `Import.DxfImportStats`

```python
DxfImportStats = TypedDict('DxfImportStats', {'dxfVersion': str, 'dxfEncoding': str, 'scalingSource': str, 'fileUnits': str, 'finalScalingFactor': float, 'importTimeSeconds': float, 'totalEntitiesCreated': int, 'entityCounts': dict[str, int], 'importSettings': dict[str, str], 'unsupportedFeatures': _UnsupportedFeatureOccurrences, 'systemBlockCounts': dict[str, int]})
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Import/__init__.pyi` line(s) 15.

## `Import.open`

```python
def open(name: str, docName: str | None=None, importHidden: bool | None=None, merge: bool | None=None, useLinkGroup: bool | None=None, mode: int=-1) -> _ImportColorAssignments | None:
```

Open one STEP, IGES, or glTF file and optionally return imported face colors.

Evidence: public stub `Import/__init__.pyi` line(s) 17.

## `Import.insert`

```python
def insert(name: str, docName: str | None=None, importHidden: bool | None=None, merge: bool | None=None, useLinkGroup: bool | None=None, mode: int=-1) -> _ImportColorAssignments | None:
```

Insert one STEP, IGES, or glTF file into a document and optionally return face colors.

Evidence: public stub `Import/__init__.pyi` line(s) 21.

## `Import.export`

```python
def export(obj: Sequence[_ImportExportObject], name: str, exportHidden: bool | None=None, legacy: bool | None=None, keepPlacement: bool | None=None) -> None:
```

Export document objects to one STEP, IGES, or glTF file.

Evidence: public stub `Import/__init__.pyi` line(s) 25.

## `Import.readDXF`

```python
def readDXF(filename: str, document: str | None=None, ignore_errors: bool=True, option_source: str | None=None, /) -> DxfImportStats:
```

Import one DXF file and return detailed import statistics.

Evidence: public stub `Import/__init__.pyi` line(s) 29.

## `Import.writeDXFShape`

```python
@overload
def writeDXFShape(shape: Shape, filename: str, version: _DxfVersion | int=-1, usePolyline: bool=False, optionSource: str | None=None, /) -> None:

@overload
def writeDXFShape(shape: Sequence[Shape], filename: str, version: _DxfVersion | int=-1, usePolyline: bool=False, optionSource: str | None=None, /) -> None:
```

Export one shape to a DXF file.

Export a shape sequence to a DXF file.

Evidence: public stub `Import/__init__.pyi` line(s) 34, 39.

## `Import.writeDXFObject`

```python
@overload
def writeDXFObject(obj: DocumentObject, filename: str, version: _DxfVersion | int=-1, usePolyline: bool=False, optionSource: str | None=None, /) -> None:

@overload
def writeDXFObject(obj: Sequence[DocumentObject], filename: str, version: _DxfVersion | int=-1, usePolyline: bool=False, optionSource: str | None=None, /) -> None:
```

Export one document object to a DXF file.

Export a document-object sequence to a DXF file.

Evidence: public stub `Import/__init__.pyi` line(s) 44, 49.

