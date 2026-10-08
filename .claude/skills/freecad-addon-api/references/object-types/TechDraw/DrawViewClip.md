# `TechDraw::DrawViewClip`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewClip.cpp:40`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawViewClip`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Height` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The height of the view area of this clip | `src/Mod/TechDraw/App/DrawViewClip.cpp:47` |
| `ShowFrame` | `App::PropertyBool` | `bool` | `bool \| int` | Specifies if the clip frame appears on the page or not | `src/Mod/TechDraw/App/DrawViewClip.cpp:49` |
| `Views` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | The Views in this Clip group | `src/Mod/TechDraw/App/DrawViewClip.cpp:50` |
| `Width` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The width of the view area of this clip | `src/Mod/TechDraw/App/DrawViewClip.cpp:48` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

