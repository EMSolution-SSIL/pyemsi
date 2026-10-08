# `PartGui::ViewProviderPartExt`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/Part/Gui/ViewProviderExt.cpp:101`. Abstract macro: no.

Native parent: [Gui::ViewProviderGeometryObject](../Gui/ViewProviderGeometryObject.md). Read the parent record for inherited properties.

Direct binding association: `PartGui.ViewProviderPartExt`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AngularDeflection` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Not documented by registration | `src/Mod/Part/Gui/ViewProviderExt.cpp:202` |
| `Deviation` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/Part/Gui/ViewProviderExt.cpp:192` |
| `DrawStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Defines the style of the edges in the 3D view. | `src/Mod/Part/Gui/ViewProviderExt.cpp:214` |
| `Lighting` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Set object lighting. | `src/Mod/Part/Gui/ViewProviderExt.cpp:212` |
| `LineColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Set object line color. | `src/Mod/Part/Gui/ViewProviderExt.cpp:172` |
| `LineColorArray` | `App::PropertyColorList` | list[tuple[float, float, float, float]] (source review) | _ColorInput \| Iterable[_ColorInput] \| dict[int, _ColorInput] (source review) | Object line color array. | `src/Mod/Part/Gui/ViewProviderExt.cpp:181` |
| `LineMaterial` | `App::PropertyMaterial` | FreeCAD.Material (source review) | FreeCAD.Material \| _ColorInput (source review) | Object line material. | `src/Mod/Part/Gui/ViewProviderExt.cpp:170` |
| `LineWidth` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Set object line width. | `src/Mod/Part/Gui/ViewProviderExt.cpp:188` |
| `PointColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Set object point color | `src/Mod/Part/Gui/ViewProviderExt.cpp:173` |
| `PointColorArray` | `App::PropertyColorList` | list[tuple[float, float, float, float]] (source review) | _ColorInput \| Iterable[_ColorInput] \| dict[int, _ColorInput] (source review) | Object point color array. | `src/Mod/Part/Gui/ViewProviderExt.cpp:174` |
| `PointMaterial` | `App::PropertyMaterial` | FreeCAD.Material (source review) | FreeCAD.Material \| _ColorInput (source review) | Object point material. | `src/Mod/Part/Gui/ViewProviderExt.cpp:171` |
| `PointSize` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Set object point size. | `src/Mod/Part/Gui/ViewProviderExt.cpp:191` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

