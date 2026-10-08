# `Gui::ViewProviderLink`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Gui/ViewProviderLink.cpp:1921`. Abstract macro: no.

Native parent: [Gui::ViewProviderDocumentObject](../Gui/ViewProviderDocumentObject.md). Read the parent record for inherited properties.

Direct binding association: `FreeCADGui.ViewProviderLink`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `ChildViewProvider` | `App::PropertyPersistentObject` | `object` | `str` | Not documented by registration | `src/Gui/ViewProviderLink.cpp:1971` |
| `DrawStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Gui/ViewProviderLink.cpp:1952` |
| `LineWidth` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Gui/ViewProviderLink.cpp:1957` |
| `MaterialList` | `App::PropertyMaterialList` | tuple[FreeCAD.Material, ...] (source review) | FreeCAD.Material \| Iterable[FreeCAD.Material] \| dict[int, FreeCAD.Material] (source review) | Not documented by registration | `src/Gui/ViewProviderLink.cpp:1965` |
| `OverrideColorList` | `App::PropertyColorList` | list[tuple[float, float, float, float]] (source review) | _ColorInput \| Iterable[_ColorInput] \| dict[int, _ColorInput] (source review) | Not documented by registration | `src/Gui/ViewProviderLink.cpp:1969` |
| `OverrideMaterial` | `App::PropertyBool` | `bool` | `bool \| int` | Override linked object's material | `src/Gui/ViewProviderLink.cpp:1939` |
| `OverrideMaterialList` | `App::PropertyBoolList` | tuple[bool, ...] (source review) | bool \| int \| Iterable[bool \| int] \| dict[int, bool \| int] \| str (source review) | Not documented by registration | `src/Gui/ViewProviderLink.cpp:1968` |
| `PointSize` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Gui/ViewProviderLink.cpp:1962` |
| `Selectable` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Gui/ViewProviderLink.cpp:1937` |
| `ShapeAppearance` | `App::PropertyMaterialList` | tuple[FreeCAD.Material, ...] (source review) | FreeCAD.Material \| Iterable[FreeCAD.Material] \| dict[int, FreeCAD.Material] (source review) | Not documented by registration | `src/Gui/ViewProviderLink.cpp:1949` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

