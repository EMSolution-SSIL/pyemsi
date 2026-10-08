# `Fem.FemPostObject`

[Module](index.md)

```python
class FemPostObject(GeoFeature):
```

The FemPostObject class.

Author: Mario Passaglia (mpassaglia@cbc.uba.ar)
License: LGPL-2.1-or-later

Evidence: public stub `Fem/__init__.pyi` line 482. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Fem.FemPostObject.writeVTK`

```python
def writeVTK(self, file_name: str, /) -> None:
```

Write data object to VTK file.

filename: str
    File extension is automatically detected from data type.

Evidence: public stub `Fem/__init__.pyi` line(s) 490.

## `Fem.FemPostObject.getDataSet`

```python
def getDataSet(self) -> vtkDataSet | None:
```

Returns the current output dataset.
For normal filters this is equal to the objects Data property output.
However, a pipelines Data property could store multiple frames, and hence
Data can be of type vtkCompositeData, which is not a vtkDataset.

To simplify implementations this function always returns a vtkDataSet,
and for a pipeline it will be the dataset of the currently selected frame.

Note that the returned value could be None, if no data is set at all.

Evidence: public stub `Fem/__init__.pyi` line(s) 499.

