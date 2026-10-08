# `TechDraw::DrawViewSymbol`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewSymbol.cpp:44`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawViewSymbol`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `EditableTexts` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Substitution values for the editable strings in this symbol | `src/Mod/TechDraw/App/DrawViewSymbol.cpp:52` |
| `Owner` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Feature to which this symbol is attached | `src/Mod/TechDraw/App/DrawViewSymbol.cpp:54` |
| `Symbol` | `App::PropertyString` | `str` | `str` | The SVG code defining this symbol | `src/Mod/TechDraw/App/DrawViewSymbol.cpp:51` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

