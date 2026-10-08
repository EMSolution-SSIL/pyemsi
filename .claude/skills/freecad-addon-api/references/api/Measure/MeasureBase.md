# `Measure.MeasureBase`

[Module](index.md)

```python
class MeasureBase(DocumentObject):
```

User documentation here

Author: David Friedli(hlorus) (david@friedli-be.ch)
License: LGPL-2.1-or-later

Evidence: public stub `Measure/__init__.pyi` line 15. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Measure.MeasureBase.DisplayUnit`

```python
@property
def DisplayUnit(self) -> str:

@DisplayUnit.setter
def DisplayUnit(self, value: str) -> None:
```

User selected display unit override. Empty uses the global schema.

Access: getter and setter declared in the stub.

Evidence: public stub `Measure/__init__.pyi` line(s) 24, 29.

## `Measure.MeasureBase.Placement`

```python
@property
def Placement(self) -> Base.Placement:

@Placement.setter
def Placement(self, value: Base.Placement | Base.Matrix) -> None:
```

Visual placement of the measurement

Access: getter and setter declared in the stub.

Evidence: public stub `Measure/__init__.pyi` line(s) 33, 38.

