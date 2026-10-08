# `FreeCAD.MeasureManager`

[Module](index.md)

```python
class MeasureManager:
```

MeasureManager class.

The MeasureManager handles measure types and geometry handler across FreeCAD.

Author: David Friedli (david@friedli-be.ch)
Licence: LGPL
DeveloperDocu: MeasureManager

Evidence: public stub `FreeCAD/__init__.pyi` line 2477. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.MeasureManager.addMeasureType`

```python
@staticmethod
def addMeasureType(id: str, label: str, measureType: MeasureType, /) -> None:
```

Add a new measure type.

id : str
    Unique identifier of the measure type.
label : str
    Name of the module.
measureType : Measure.MeasureBasePython
    The actual measure type.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2489.

## `FreeCAD.MeasureManager.getMeasureTypes`

```python
@staticmethod
def getMeasureTypes() -> List[Tuple[str, str, MeasureType]]:
```

Returns a list of all registered measure types.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2503.

