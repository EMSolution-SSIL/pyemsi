# `TechDraw::DrawTile`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawTile.cpp:36`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawTile`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `TileColumn` | `App::PropertyInteger` | `int` | `int` | Column in parent object | `src/Mod/TechDraw/App/DrawTile.cpp:45` |
| `TileParent` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Object to which this tile is attached | `src/Mod/TechDraw/App/DrawTile.cpp:42` |
| `TileRow` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Row in parent object  0 for arrow side, -1 for other side | `src/Mod/TechDraw/App/DrawTile.cpp:44` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

