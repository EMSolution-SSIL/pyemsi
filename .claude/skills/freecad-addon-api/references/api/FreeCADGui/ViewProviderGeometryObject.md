# `FreeCADGui.ViewProviderGeometryObject`

[Module](index.md)

```python
class ViewProviderGeometryObject(ViewProviderDocumentObject):
```

This is the ViewProvider geometry class

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 2961. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.ViewProviderGeometryObject.BoundingBox`

```python
@property
def BoundingBox(self) -> bool:

@BoundingBox.setter
def BoundingBox(self, value: bool | int) -> None:
```

Display object bounding box

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2970, 2975.

## `FreeCADGui.ViewProviderGeometryObject.Selectable`

```python
@property
def Selectable(self) -> bool:

@Selectable.setter
def Selectable(self, value: bool | int) -> None:
```

Set if the object is selectable in the 3d view

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2979, 2984.

## `FreeCADGui.ViewProviderGeometryObject.Transparency`

```python
@property
def Transparency(self) -> int:

@Transparency.setter
def Transparency(self, value: int | dict[str, int] | tuple[int, int, int, int]) -> None:
```

Set object transparency

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2988, 2993.

## `FreeCADGui.ViewProviderGeometryObject.getUserDefinedMaterial`

```python
@staticmethod
def getUserDefinedMaterial() -> object:
```

Get a material object with the user-defined colors.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2997.

