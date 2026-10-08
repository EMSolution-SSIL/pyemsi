# `TechDraw::DrawSVGTemplate`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawSVGTemplate.cpp:46`. Abstract macro: no.

Native parent: [TechDraw::DrawTemplate](../TechDraw/DrawTemplate.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawSVGTemplate`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `PageResult` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | Embedded SVG code for template. For system use. | `src/Mod/TechDraw/App/DrawSVGTemplate.cpp:52` |
| `Template` | `App::PropertyFile` | `str` | `str \| dict[str, str]` | Template file name. | `src/Mod/TechDraw/App/DrawSVGTemplate.cpp:53` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

