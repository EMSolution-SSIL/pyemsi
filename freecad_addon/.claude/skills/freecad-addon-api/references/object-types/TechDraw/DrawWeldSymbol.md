# `TechDraw::DrawWeldSymbol`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawWeldSymbol.cpp:42`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawWeldSymbol`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AllAround` | `App::PropertyBool` | `bool` | `bool \| int` | All Around Symbol on/off | `src/Mod/TechDraw/App/DrawWeldSymbol.cpp:49` |
| `AlternatingWeld` | `App::PropertyBool` | `bool` | `bool \| int` | Alternating Weld true/false | `src/Mod/TechDraw/App/DrawWeldSymbol.cpp:51` |
| `FieldWeld` | `App::PropertyBool` | `bool` | `bool \| int` | Field Weld Symbol on/off | `src/Mod/TechDraw/App/DrawWeldSymbol.cpp:50` |
| `Leader` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Parent Leader | `src/Mod/TechDraw/App/DrawWeldSymbol.cpp:48` |
| `TailText` | `App::PropertyString` | `str` | `str` | Text at tail of symbol | `src/Mod/TechDraw/App/DrawWeldSymbol.cpp:52` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

