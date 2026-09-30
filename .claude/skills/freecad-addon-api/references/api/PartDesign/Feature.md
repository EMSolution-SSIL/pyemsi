# `PartDesign.Feature`

[Module](index.md)

```python
class Feature(PartFeature):
```

This is the father of all PartDesign object classes

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `PartDesign/__init__.pyi` line 45. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PartDesign.Feature.BaseFeature`

```python
@property
def BaseFeature(self) -> DocumentObject | None:

@BaseFeature.setter
def BaseFeature(self, value: DocumentObject | None) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `PartDesign/__init__.pyi` line(s) 54, 58.

## `PartDesign.Feature.SuppressedShape`

```python
@property
def SuppressedShape(self) -> Part.Shape:

@SuppressedShape.setter
def SuppressedShape(self, value: Part.Shape) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `PartDesign/__init__.pyi` line(s) 62, 66.

## `PartDesign.Feature.getBaseObject`

```python
@overload
def getBaseObject(self) -> Optional[object]:

def getBaseObject(self) -> Optional[object]:
```

getBaseObject: returns feature this one fuses itself to, or None. Normally, this should be the same as BaseFeature property, except for legacy workflow. In legacy workflow, it will look up the support of referenced sketch.

Evidence: public stub `PartDesign/__init__.pyi` line(s) 70, 76.

