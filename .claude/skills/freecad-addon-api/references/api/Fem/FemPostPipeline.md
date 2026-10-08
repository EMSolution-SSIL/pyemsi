# `Fem.FemPostPipeline`

[Module](index.md)

```python
class FemPostPipeline(FemPostObject):
```

The FemPostPipeline class.

Author: Stefan Tröger (stefantroeger@gmx.net)
License: LGPL-2.1-or-later

Evidence: public stub `Fem/__init__.pyi` line 513. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Fem.FemPostPipeline.Frame`

```python
@property
def Frame(self) -> str:

@Frame.setter
def Frame(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `Fem/__init__.pyi` line(s) 522, 526.

## `Fem.FemPostPipeline.MergeDuplicate`

```python
@property
def MergeDuplicate(self) -> bool:

@MergeDuplicate.setter
def MergeDuplicate(self, value: bool | int) -> None:
```

Remove coindent elements.

Access: getter and setter declared in the stub.

Evidence: public stub `Fem/__init__.pyi` line(s) 530, 535.

## `Fem.FemPostPipeline.read`

```python
@overload
def read(self, file_name: str, /) -> None:

@overload
def read(self, files: list[str] | tuple[str], values: list[int] | tuple[int], unit: Unit, frame_type: str, /) -> None:

def read(self, *args) -> None:
```

Reads in a single vtk file or creates a multiframe result by reading in multiple result files.

If multiframe is wanted, 4 argumenhts are needed:
1. List of result files each being one frame,
2. List of values valid for each frame (e.g. [s] if time data),
3. the unit of the value as FreeCAD.Units.Unit,
4. the Description of the frame type

Evidence: public stub `Fem/__init__.pyi` line(s) 539, 543, 546.

## `Fem.FemPostPipeline.scale`

```python
def scale(self, scale: float, /) -> None:
```

scale the points of a loaded vtk file

Evidence: public stub `Fem/__init__.pyi` line(s) 558.

## `Fem.FemPostPipeline.load`

```python
@overload
def load(self, obj: DocumentObject, /) -> None:

@overload
def load(self, result: list[DocumentObject] | tuple[DocumentObject], values: list[float] | tuple[float], unit: Unit, frame_type: str, /) -> None:

def load(self, *args) -> Any:
```

Load a single result object or create a multiframe result by loading multiple result frames.

If multiframe is wanted, 4 argumenhts are needed:
1. List of result objects each being one frame,
2. List of values valid for each frame (e.g. [s] if time data),
3. the unit of the value as FreeCAD.Units.Unit,
4. the Description of the frame type

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Fem/__init__.pyi` line(s) 563, 567, 570.

## `Fem.FemPostPipeline.getFilter`

```python
def getFilter(self) -> list[object]:
```

Returns all filters, that this pipeline uses (non recursive, result does not contain branch child filters)

Evidence: public stub `Fem/__init__.pyi` line(s) 582.

## `Fem.FemPostPipeline.recomputeChildren`

```python
def recomputeChildren(self) -> None:
```

Recomputes all children of the pipeline

Evidence: public stub `Fem/__init__.pyi` line(s) 586.

## `Fem.FemPostPipeline.getLastPostObject`

```python
def getLastPostObject(self) -> DocumentObject | None:
```

Get the last post-processing object

Evidence: public stub `Fem/__init__.pyi` line(s) 590.

## `Fem.FemPostPipeline.holdsPostObject`

```python
def holdsPostObject(self, obj: DocumentObject, /) -> bool:
```

Check if this pipeline holds a given post-processing object

Evidence: public stub `Fem/__init__.pyi` line(s) 594.

## `Fem.FemPostPipeline.renameArrays`

```python
def renameArrays(self, names: dict[str, str], /) -> None:
```

Change name of data arrays

Evidence: public stub `Fem/__init__.pyi` line(s) 598.

## `Fem.FemPostPipeline.addArrayFromFunction`

```python
def addArrayFromFunction(self, functions: dict[str, str], /) -> None:
```

Add new arrays as functions of the current fields.
The arrays are defined as "func_name": "func" key-value pairs.
Field names behave similarly to those in the calculator filter.

Evidence: public stub `Fem/__init__.pyi` line(s) 602.

## `Fem.FemPostPipeline.getOutputAlgorithm`

```python
def getOutputAlgorithm(self) -> vtkAlgorithm:
```

Returns the pipeline vtk algorithm, which generates the data passed to the pipelines filters.

Note that the output algorithm may change depending on pipeline settings.

Evidence: public stub `Fem/__init__.pyi` line(s) 610.

## `Fem.FemPostPipeline.setTimeInfo`

```python
def setTimeInfo(self, frame_type: str, unit: Unit, /) -> None:
```

Set pipeline frame information.

Evidence: public stub `Fem/__init__.pyi` line(s) 617.

