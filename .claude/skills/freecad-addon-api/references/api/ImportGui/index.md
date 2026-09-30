# `ImportGui`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `ImportGui/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from collections.abc import Sequence
from typing import Literal, TypeAlias, TypedDict
from FreeCAD import DocumentObject
```

## `ImportGui._DxfVersion`

```python
_DxfVersion: TypeAlias = Literal[12, 14]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 9.

## `ImportGui._UnsupportedFeatureOccurrences`

```python
_UnsupportedFeatureOccurrences: TypeAlias = dict[str, list[tuple[int, str]]]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 10.

## `ImportGui.DxfImportStats`

```python
DxfImportStats = TypedDict('DxfImportStats', {'dxfVersion': str, 'dxfEncoding': str, 'scalingSource': str, 'fileUnits': str, 'finalScalingFactor': float, 'importTimeSeconds': float, 'totalEntitiesCreated': int, 'entityCounts': dict[str, int], 'importSettings': dict[str, str], 'unsupportedFeatures': _UnsupportedFeatureOccurrences, 'systemBlockCounts': dict[str, int]})
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 11.

## `ImportGui.ImportOptions`

```python
ImportOptions = TypedDict('ImportOptions', {'merge': bool, 'useLinkGroup': bool, 'useBaseName': bool, 'importHidden': bool, 'reduceObjects': bool, 'showProgress': bool, 'expandCompound': bool, 'mode': int, 'codePage': int}, total=False)
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 12.

## `ImportGui.ExportOptions`

```python
ExportOptions = TypedDict('ExportOptions', {'exportHidden': bool, 'keepPlacement': bool, 'legacy': bool}, total=False)
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 13.

## `ImportGui.open`

```python
def open(name: str, docName: str | None=None, options: ImportOptions | None=None, importHidden: bool | None=None, merge: bool | None=None, useLinkGroup: bool | None=None, mode: int=-1) -> DocumentObject | None:
```

Open one STEP, IGES, or glTF file with GUI import behavior.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 15.

## `ImportGui.insert`

```python
def insert(name: str, docName: str | None=None, options: ImportOptions | None=None, importHidden: bool | None=None, merge: bool | None=None, useLinkGroup: bool | None=None, mode: int=-1) -> DocumentObject | None:
```

Insert one STEP, IGES, or glTF file with GUI import behavior.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 19.

## `ImportGui.preScanDxf`

```python
def preScanDxf(filepath: str, /) -> dict[str, int]:
```

Return entity-count statistics gathered from one DXF file without importing it.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 23.

## `ImportGui.readDXF`

```python
def readDXF(filename: str, document: str | None=None, ignore_errors: bool=True, option_source: str | None=None, /) -> DxfImportStats:
```

Import one DXF file through the GUI path and return import statistics.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 27.

## `ImportGui.importOptions`

```python
def importOptions(name: str, /) -> ImportOptions:
```

Show the GUI import-options dialog for one file type and return the chosen options.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 31.

## `ImportGui.exportOptions`

```python
def exportOptions(name: str, /) -> ExportOptions:
```

Show the GUI export-options dialog for one file type and return the chosen options.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 35.

## `ImportGui.export`

```python
def export(obj: Sequence[DocumentObject], name: str, options: ExportOptions | None=None, exportHidden: bool | None=None, legacy: bool | None=None, keepPlacement: bool | None=None) -> None:
```

Export document objects through the GUI-aware OCAF exporter.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 39.

## `ImportGui.ocaf`

```python
def ocaf(name: str, /) -> None:
```

Open the OCAF browser for one STEP, IGES, or glTF file.

Evidence: public stub `ImportGui/__init__.pyi` line(s) 43.

