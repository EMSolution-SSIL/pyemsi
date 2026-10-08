# `FemGui::ViewProviderFemPostObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/Fem/Gui/ViewProviderFemPostObject.cpp:150`. Abstract macro: no.

Native parent: [Gui::ViewProviderDocumentObject](../Gui/ViewProviderDocumentObject.md). Read the parent record for inherited properties.

Direct binding association: `FemGui.ViewProviderFemPostFilter`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Component` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Select component to display | `src/Mod/Fem/Gui/ViewProviderFemPostObject.cpp:162` |
| `EdgeColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Set wireframe line color. | `src/Mod/Fem/Gui/ViewProviderFemPostObject.cpp:164` |
| `Field` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Select the field used for calculating the color | `src/Mod/Fem/Gui/ViewProviderFemPostObject.cpp:155` |
| `LineWidth` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Set wireframe line width. | `src/Mod/Fem/Gui/ViewProviderFemPostObject.cpp:185` |
| `NoneFieldColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Shape color used if Field property is None. | `src/Mod/Fem/Gui/ViewProviderFemPostObject.cpp:171` |
| `PlainColorEdgeOnSurface` | `App::PropertyBool` | `bool` | `bool \| int` | Use plain color for edges on surface. | `src/Mod/Fem/Gui/ViewProviderFemPostObject.cpp:178` |
| `PointSize` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Set node point size. | `src/Mod/Fem/Gui/ViewProviderFemPostObject.cpp:186` |
| `Transparency` | `App::PropertyPercent` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Set object transparency. | `src/Mod/Fem/Gui/ViewProviderFemPostObject.cpp:163` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

