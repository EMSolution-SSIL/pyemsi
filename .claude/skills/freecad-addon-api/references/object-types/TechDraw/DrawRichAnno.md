# `TechDraw::DrawRichAnno`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawRichAnno.cpp:37`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawRichAnno`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AnnoParent` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Object to which this annontation is attached | `src/Mod/TechDraw/App/DrawRichAnno.cpp:43` |
| `AnnoText` | `App::PropertyString` | `str` | `str` | Annotation text | `src/Mod/TechDraw/App/DrawRichAnno.cpp:45` |
| `MaxWidth` | `App::PropertyFloat` | `float` | `float` | Width limit before auto wrap | `src/Mod/TechDraw/App/DrawRichAnno.cpp:49` |
| `OriginCentered` | `App::PropertyBool` | `bool` | `bool \| int` | Center the annotation on it's origin. | `src/Mod/TechDraw/App/DrawRichAnno.cpp:48` |
| `ShowFrame` | `App::PropertyBool` | `bool` | `bool \| int` | Outline rectangle on/off | `src/Mod/TechDraw/App/DrawRichAnno.cpp:46` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

