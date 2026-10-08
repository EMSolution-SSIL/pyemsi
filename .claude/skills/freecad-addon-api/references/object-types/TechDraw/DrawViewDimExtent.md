# `TechDraw::DrawViewDimExtent`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewDimExtent.cpp:45`. Abstract macro: no.

Native parent: [TechDraw::DrawViewDimension](../TechDraw/DrawViewDimension.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawViewDimExtent`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `CosmeticTags` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Id of cosmetic endpoints | `src/Mod/TechDraw/App/DrawViewDimExtent.cpp:61` |
| `DirExtent` | `App::PropertyInteger` | `int` | `int` | Horizontal / Vertical | `src/Mod/TechDraw/App/DrawViewDimExtent.cpp:58` |
| `Source` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | View containing the  dimension | `src/Mod/TechDraw/App/DrawViewDimExtent.cpp:52` |
| `Source3d` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | 3D geometry to be dimensioned | `src/Mod/TechDraw/App/DrawViewDimExtent.cpp:56` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

