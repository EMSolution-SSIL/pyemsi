# `CAM.FeatureArea`

[Module](index.md)

```python
class FeatureArea(DocumentObject):
```

This class handles Path Area features

Author: Zheng, Lei (realthunder.dev@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `CAM/__init__.pyi` line 10. Inherited members are on the named base's reference; aliases keep their imported identity.

## `CAM.FeatureArea.Sources`

```python
@property
def Sources(self) -> list[DocumentObject | None]:

@Sources.setter
def Sources(self, value: Sequence[DocumentObject]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `CAM/__init__.pyi` line(s) 19, 23.

## `CAM.FeatureArea.getArea`

```python
def getArea(self) -> Any:
```

Return a copy of the encapsulated Python Area object.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `CAM/__init__.pyi` line(s) 26.

## `CAM.FeatureArea.setParams`

```python
def setParams(self, **kwargs) -> Any:
```

Convenient function to configure this feature.

Call with keywords: setParams(key=value, ...)

Same usage as Path.Area.setParams(). This function stores the parameters in the properties.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `CAM/__init__.pyi` line(s) 30.

## `CAM.FeatureArea.WorkPlane`

```python
@property
def WorkPlane(self) -> Part.Shape:

@WorkPlane.setter
def WorkPlane(self, value: Part.Shape) -> None:
```

The current workplane. If no plane is set, it is derived from the added shapes.

Access: getter and setter declared in the stub.

Evidence: public stub `CAM/__init__.pyi` line(s) 41, 46.

