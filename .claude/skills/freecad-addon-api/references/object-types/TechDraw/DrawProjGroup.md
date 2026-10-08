# `TechDraw::DrawProjGroup`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawProjGroup.cpp:60`. Abstract macro: no.

Native parent: [TechDraw::DrawViewCollection](../TechDraw/DrawViewCollection.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawProjGroup`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Anchor` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | The root view to align projections with | `src/Mod/TechDraw/App/DrawProjGroup.cpp:74` |
| `AutoDistribute` | `App::PropertyBool` | `bool` | `bool \| int` | Distribute views automatically or manually | `src/Mod/TechDraw/App/DrawProjGroup.cpp:82` |
| `ProjectionType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | First or Third angle projection | `src/Mod/TechDraw/App/DrawProjGroup.cpp:79` |
| `Source` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Shape to view | `src/Mod/TechDraw/App/DrawProjGroup.cpp:69` |
| `XSource` | `App::PropertyXLinkList` | `_DocumentObjectList \| _DocumentObjectSubLinkList` | `_DocumentObjectListInput \| _DocumentObjectSubLinkListInput` | External 3D Shape to view | `src/Mod/TechDraw/App/DrawProjGroup.cpp:72` |
| `spacingX` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Not documented by registration | `src/Mod/TechDraw/App/DrawProjGroup.cpp:84` |
| `spacingY` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | If AutoDistribute is on, this is the vertical  spacing between the borders of views | `src/Mod/TechDraw/App/DrawProjGroup.cpp:87` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

