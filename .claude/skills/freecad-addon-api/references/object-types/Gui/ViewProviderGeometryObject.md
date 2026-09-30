# `Gui::ViewProviderGeometryObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Gui/ViewProviderGeometryObject.cpp:54`. Abstract macro: no.

Native parent: [Gui::ViewProviderDragger](../Gui/ViewProviderDragger.md). Read the parent record for inherited properties.

Direct binding association: `FreeCADGui.ViewProviderGeometryObject`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `BoundingBox` | `App::PropertyBool` | `bool` | `bool \| int` | Display object bounding box | `src/Gui/ViewProviderGeometryObject.cpp:78` |
| `Selectable` | `App::PropertyBool` | `bool` | `bool \| int` | Set if the object is selectable in the 3d view | `src/Gui/ViewProviderGeometryObject.cpp:79` |
| `ShapeAppearance` | `App::PropertyMaterialList` | tuple[FreeCAD.Material, ...] (source review) | FreeCAD.Material \| Iterable[FreeCAD.Material] \| dict[int, FreeCAD.Material] (source review) | Shape appearance | `src/Gui/ViewProviderGeometryObject.cpp:77` |
| `Transparency` | `App::PropertyPercent` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Set object transparency | `src/Gui/ViewProviderGeometryObject.cpp:68` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

