# `TechDraw::DrawHatch`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawHatch.cpp:46`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawHatch`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `HatchPattern` | `App::PropertyFile` | `str` | `str \| dict[str, str]` | The hatch pattern file for this area | `src/Mod/TechDraw/App/DrawHatch.cpp:54` |
| `Source` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | The View + Face to be hatched | `src/Mod/TechDraw/App/DrawHatch.cpp:52` |
| `SvgIncluded` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | Embedded SVG hatch file. System use only. | `src/Mod/TechDraw/App/DrawHatch.cpp:55` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

