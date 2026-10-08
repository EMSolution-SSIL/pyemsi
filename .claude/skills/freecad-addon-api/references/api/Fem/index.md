# `Fem`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `Fem/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [Fem.FemMesh](FemMesh.md)
- [Fem.FemPostBranchFilter](FemPostBranchFilter.md)
- [Fem.FemPostFilter](FemPostFilter.md)
- [Fem.FemPostObject](FemPostObject.md)
- [Fem.FemPostPipeline](FemPostPipeline.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from collections.abc import Sequence
from FreeCAD import DocumentObject
from FreeCAD import ComplexGeoData
from typing import overload
from FreeCAD.Base import Vector
from typing import Final
from Part import Shape as TopoShape
from FreeCAD.Base import Placement
from Part import Face as TopoShapeFace
from Part import Edge as TopoShapeEdge
from Part import Solid as TopoShapeSolid
from Part import Vertex as TopoShapeVertex
from FreeCAD import GeoFeature
from FreeCAD.Base import Unit
```

## `Fem.open`

```python
def open(name: str, /) -> None:
```

Open one FEM mesh file into a new document.

Evidence: public stub `Fem/__init__.pyi` line(s) 9.

## `Fem.insert`

```python
@overload
def insert(name: str, /) -> None:

@overload
def insert(name: str, doc_name: str, /) -> None:
```

Insert one FEM mesh or result file into the active document, creating one if needed.

Insert one FEM mesh or result file into the named document, creating it if needed.

Evidence: public stub `Fem/__init__.pyi` line(s) 14, 19.

## `Fem.export`

```python
def export(objects: Sequence[DocumentObject], name: str, /) -> None:
```

Export the first selected FEM mesh object to one mesh or solver file.

Evidence: public stub `Fem/__init__.pyi` line(s) 23.

## `Fem.read`

```python
def read(name: str, /) -> FemMesh:
```

Read one FEM mesh file and return the resulting `FemMesh` object.

Evidence: public stub `Fem/__init__.pyi` line(s) 27.

## `Fem.frdToVTK`

```python
def frdToVTK(filename: str, binary: bool=True, /) -> None:
```

Convert one CalculiX `.frd` result file to VTK output.

Evidence: public stub `Fem/__init__.pyi` line(s) 31.

## `Fem.readResult`

```python
@overload
def readResult(file_name: str, /) -> None:

@overload
def readResult(file_name: str, obj_name: str, /) -> None:
```

Read one CFD or mechanical result file into the active result target.

Read one CFD or mechanical result file into the named document object.

Evidence: public stub `Fem/__init__.pyi` line(s) 36, 41.

## `Fem.writeResult`

```python
@overload
def writeResult(file_name: str, /) -> None:

@overload
def writeResult(file_name: str, obj: DocumentObject, /) -> None:
```

Write the active CFD or FEM result object to one file.

Write one specific CFD or FEM result object to one file.

Evidence: public stub `Fem/__init__.pyi` line(s) 46, 51.

## `Fem.getVtkVersion`

```python
def getVtkVersion() -> str:
```

Return the VTK version string linked into this build.

Evidence: public stub `Fem/__init__.pyi` line(s) 55.

## `Fem.getVtkVersionNumber`

```python
def getVtkVersionNumber() -> int:
```

Return the VTK version as one packed integer value.

Evidence: public stub `Fem/__init__.pyi` line(s) 59.

## `Fem.vtkVersionCheck`

```python
def vtkVersionCheck(major: int, minor: int, build: int=0, /) -> int:
```

Pack one VTK major, minor, and build tuple into a version integer.

Evidence: public stub `Fem/__init__.pyi` line(s) 63.

## `Fem.isVtkCompatible`

```python
def isVtkCompatible(vtkObject: object, /) -> bool:
```

Return whether one Python VTK object is compatible with FreeCAD's VTK ABI.

Evidence: public stub `Fem/__init__.pyi` line(s) 67.

## `Fem.show`

```python
def show(mesh: FemMesh, name: str='Mesh', /) -> None:
```

Create one FEM mesh object in the active document from a `FemMesh`.

Evidence: public stub `Fem/__init__.pyi` line(s) 71.

