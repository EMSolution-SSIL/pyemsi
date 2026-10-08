# `TechDraw::DrawTemplate`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawTemplate.cpp:45`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawTemplate`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `EditableTexts` | `App::PropertyMap` | `dict[str, str]` | `dict[str, str]` | Editable strings in the template | `src/Mod/TechDraw/App/DrawTemplate.cpp:63` |
| `Height` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Height of page | `src/Mod/TechDraw/App/DrawTemplate.cpp:61` |
| `Orientation` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/TechDraw/App/DrawTemplate.cpp:57` |
| `Width` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Width of page | `src/Mod/TechDraw/App/DrawTemplate.cpp:60` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

