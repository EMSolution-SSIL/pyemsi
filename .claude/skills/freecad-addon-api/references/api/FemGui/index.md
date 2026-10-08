# `FemGui`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `FemGui/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [FemGui.ViewProviderFemConstraint](ViewProviderFemConstraint.md)
- [FemGui.ViewProviderFemMesh](ViewProviderFemMesh.md)
- [FemGui.ViewProviderFemPostFilter](ViewProviderFemPostFilter.md)
- [FemGui.ViewProviderFemPostPipeline](ViewProviderFemPostPipeline.md)
- [FemGui.ViewProviderShapeExtension](ViewProviderShapeExtension.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from FreeCAD import DocumentObject
from FreeCADGui import ViewProviderGeometryObject
from typing import Final
from FreeCAD.Base import Vector
from FreeCADGui import ViewProviderDocumentObject
from FreeCADGui import ViewProviderExtension
```

## `FemGui.setActiveAnalysis`

```python
@overload
def setActiveAnalysis() -> None:

@overload
def setActiveAnalysis(obj: DocumentObject, /) -> None:
```

Clear the currently active FEM analysis object.

Set the active FEM analysis object.

Evidence: public stub `FemGui/__init__.pyi` line(s) 9, 14.

## `FemGui.getActiveAnalysis`

```python
def getActiveAnalysis() -> DocumentObject | None:
```

Return the active FEM analysis object, if one is currently set.

Evidence: public stub `FemGui/__init__.pyi` line(s) 18.

## `FemGui.open`

```python
@overload
def open(name: str, /) -> None:

@overload
def open(name: str, doc_name: str, /) -> None:
```

Open one Abaqus or Python input file in the FEM editor.

Evidence: public stub `FemGui/__init__.pyi` line(s) 23, 28.

## `FemGui.insert`

```python
@overload
def insert(name: str, /) -> None:

@overload
def insert(name: str, doc_name: str, /) -> None:
```

Open one Abaqus or Python input file in the FEM editor.

Evidence: public stub `FemGui/__init__.pyi` line(s) 33, 38.

