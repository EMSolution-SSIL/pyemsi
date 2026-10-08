# `TechDraw::DrawBrokenView`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawBrokenView.cpp:105`. Abstract macro: no.

Native parent: [TechDraw::DrawViewPart](../TechDraw/DrawViewPart.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawBrokenView`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Breaks` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Objects in the 3D view that define the start/end points and direction of breaks in this view. | `src/Mod/TechDraw/App/DrawBrokenView.cpp:112` |
| `Gap` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The separation distance for breaks in this view (unscaled 3D length). | `src/Mod/TechDraw/App/DrawBrokenView.cpp:116` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

