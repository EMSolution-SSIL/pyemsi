# `TechDraw::DrawTileWeld`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawTileWeld.cpp:43`. Abstract macro: no.

Native parent: [TechDraw::DrawTile](../TechDraw/DrawTile.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawTileWeld`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `CenterText` | `App::PropertyString` | `str` | `str` | Text above/below symbol | `src/Mod/TechDraw/App/DrawTileWeld.cpp:52` |
| `LeftText` | `App::PropertyString` | `str` | `str` | Text before symbol | `src/Mod/TechDraw/App/DrawTileWeld.cpp:49` |
| `RightText` | `App::PropertyString` | `str` | `str` | Text after symbol | `src/Mod/TechDraw/App/DrawTileWeld.cpp:51` |
| `SymbolFile` | `App::PropertyFile` | `str` | `str \| dict[str, str]` | Symbol File | `src/Mod/TechDraw/App/DrawTileWeld.cpp:53` |
| `SymbolIncluded` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | Embedded Symbol. System use only. | `src/Mod/TechDraw/App/DrawTileWeld.cpp:54` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

