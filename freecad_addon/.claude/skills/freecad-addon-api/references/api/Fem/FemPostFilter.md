# `Fem.FemPostFilter`

[Module](index.md)

```python
class FemPostFilter(FemPostObject):
```

The FemPostFilter class.

Author: Stefan Tröger (stefantroeger@gmx.net)
License: LGPL-2.1-or-later

Evidence: public stub `Fem/__init__.pyi` line 428. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Fem.FemPostFilter.Frame`

```python
@property
def Frame(self) -> float:

@Frame.setter
def Frame(self, value: float) -> None:
```

The step used to calculate the data

Access: getter and setter declared in the stub.

Evidence: public stub `Fem/__init__.pyi` line(s) 437, 442.

## `Fem.FemPostFilter.addFilterPipeline`

```python
def addFilterPipeline(self, name: str, source: vtkAlgorithm, target: vtkAlgorithm, /) -> None:
```

Registers a new vtk filter pipeline for data processing. Arguments are (name, source algorithm, target algorithm).

Evidence: public stub `Fem/__init__.pyi` line(s) 445.

## `Fem.FemPostFilter.setActiveFilterPipeline`

```python
def setActiveFilterPipeline(self, name: str, /) -> None:
```

Sets the filter pipeline that shall be used for data processing. Argument is the name of the filter pipeline to activate.

Evidence: public stub `Fem/__init__.pyi` line(s) 449.

## `Fem.FemPostFilter.getParentPostGroup`

```python
def getParentPostGroup(self) -> object | None:
```

Returns the postprocessing group the filter is in (e.g. a pipeline or branch object). None is returned if not in any.

Evidence: public stub `Fem/__init__.pyi` line(s) 453.

## `Fem.FemPostFilter.getInputData`

```python
def getInputData(self) -> object:
```

Returns the dataset available at the filter's input.
Note: Can lead to a full recompute of the whole pipeline, hence best to call this only in "execute", where the user expects long calculation cycles.

Evidence: public stub `Fem/__init__.pyi` line(s) 457.

## `Fem.FemPostFilter.getInputVectorFields`

```python
def getInputVectorFields(self) -> list[str]:
```

Returns the names of all vector fields available on this filter's input.
Note: Can lead to a full recompute of the whole pipeline, hence best to call this only in "execute", where the user expects long calculation cycles.

Evidence: public stub `Fem/__init__.pyi` line(s) 464.

## `Fem.FemPostFilter.getInputScalarFields`

```python
def getInputScalarFields(self) -> list[str]:
```

Returns the names of all scalar fields available on this filter's input.
Note: Can lead to a full recompute of the whole pipeline, hence best to call this only in "execute", where the user expects long calculation cycles.

Evidence: public stub `Fem/__init__.pyi` line(s) 471.

## `Fem.FemPostFilter.getOutputAlgorithm`

```python
def getOutputAlgorithm(self) -> vtkAlgorithm:
```

Returns the filters vtk algorithm currently used as output (the one generating the Data field). Note that the output algorithm may change depending on filter settings.

Evidence: public stub `Fem/__init__.pyi` line(s) 478.

