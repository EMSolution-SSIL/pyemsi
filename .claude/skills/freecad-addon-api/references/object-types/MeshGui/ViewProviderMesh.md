# `MeshGui::ViewProviderMesh`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/Mesh/Gui/ViewProvider.cpp:207`. Abstract macro: no.

Native parent: [Gui::ViewProviderGeometryObject](../Gui/ViewProviderGeometryObject.md). Read the parent record for inherited properties.

Direct binding association: `MeshGui.ViewProviderMesh`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Coloring` | `App::PropertyBool` | `bool` | `bool \| int` | Set coloring. | `src/Mod/Mesh/Gui/ViewProvider.cpp:225` |
| `CreaseAngle` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Set crease angle. | `src/Mod/Mesh/Gui/ViewProvider.cpp:222` |
| `Lighting` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Set if the illumination comes from two sides  or one side in the 3D view. | `src/Mod/Mesh/Gui/ViewProvider.cpp:226` |
| `LineColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Set line color. | `src/Mod/Mesh/Gui/ViewProvider.cpp:229` |
| `LineTransparency` | `App::PropertyPercent` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Set line transparency. | `src/Mod/Mesh/Gui/ViewProvider.cpp:216` |
| `LineWidth` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Set line width. | `src/Mod/Mesh/Gui/ViewProvider.cpp:218` |
| `OpenEdges` | `App::PropertyBool` | `bool` | `bool \| int` | Set open edges. | `src/Mod/Mesh/Gui/ViewProvider.cpp:224` |
| `PointSize` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Set point size. | `src/Mod/Mesh/Gui/ViewProvider.cpp:220` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

