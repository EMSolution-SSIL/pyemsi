# `FemGui::ViewProviderFemMesh`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:187`. Abstract macro: no.

Native parent: [Gui::ViewProviderGeometryObject](../Gui/ViewProviderGeometryObject.md). Read the parent record for inherited properties.

Direct binding association: `FemGui.ViewProviderFemMesh`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `BackfaceCulling` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:205` |
| `ColorMode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Set the color mode | `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:209` |
| `ElementColorArray` | `App::PropertyColorList` | list[tuple[float, float, float, float]] (source review) | _ColorInput \| Iterable[_ColorInput] \| dict[int, _ColorInput] (source review) | Node diffuse color array | `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:217` |
| `LineWidth` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:200` |
| `MaxFacesShowInner` | `App::PropertyInteger` | `int` | `int` | Not documented by registration | `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:207` |
| `NodeColorArray` | `App::PropertyColorList` | list[tuple[float, float, float, float]] (source review) | _ColorInput \| Iterable[_ColorInput] \| dict[int, _ColorInput] (source review) | Node diffuse color array | `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:210` |
| `PointColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Not documented by registration | `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:197` |
| `PointSize` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:198` |
| `ShowInner` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:206` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

