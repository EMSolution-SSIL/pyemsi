# `TechDraw::DrawProjGroupItem`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawProjGroupItem.cpp:56`. Abstract macro: no.

Native parent: [TechDraw::DrawViewPart](../TechDraw/DrawViewPart.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawProjGroupItem`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `RotationVector` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Deprecated. Use XDirection. | `src/Mod/TechDraw/App/DrawProjGroupItem.cpp:62` |
| `Type` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/TechDraw/App/DrawProjGroupItem.cpp:61` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

