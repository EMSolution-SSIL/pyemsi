# `FreeCAD.Part`

[Module](index.md)

```python
class Part(GeoFeature):
```

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL
This class handles document objects in Part

Evidence: public stub `FreeCAD/__init__.pyi` line 2779. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Part.Color`

```python
@property
def Color(self) -> tuple[float, float, float, float]:

@Color.setter
def Color(self, value: int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2788, 2792.

## `FreeCAD.Part.Id`

```python
@property
def Id(self) -> str:

@Id.setter
def Id(self, value: str) -> None:
```

ID (Part-Number) of the Item

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2796, 2801.

## `FreeCAD.Part.License`

```python
@property
def License(self) -> str:

@License.setter
def License(self, value: str) -> None:
```

License string of the Item

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2805, 2810.

## `FreeCAD.Part.LicenseURL`

```python
@property
def LicenseURL(self) -> str:

@LicenseURL.setter
def LicenseURL(self, value: str) -> None:
```

URL to the license text/contract

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2814, 2819.

## `FreeCAD.Part.Material`

```python
@property
def Material(self) -> DocumentObject | None:

@Material.setter
def Material(self, value: DocumentObject | None) -> None:
```

The Material for this Part

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2823, 2828.

## `FreeCAD.Part.Meta`

```python
@property
def Meta(self) -> dict[str, str]:

@Meta.setter
def Meta(self, value: dict[str, str]) -> None:
```

Map with additional meta information

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2832, 2837.

## `FreeCAD.Part.Type`

```python
@property
def Type(self) -> str:

@Type.setter
def Type(self, value: str) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2841, 2845.

## `FreeCAD.Part.Uid`

```python
@property
def Uid(self) -> str:

@Uid.setter
def Uid(self, value: str) -> None:
```

UUID of the Item

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2849, 2854.

