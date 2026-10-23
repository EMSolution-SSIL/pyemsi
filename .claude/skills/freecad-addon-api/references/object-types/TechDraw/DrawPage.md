# `TechDraw::DrawPage`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawPage.cpp:56`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawPage`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `KeepUpdated` | `App::PropertyBool` | `bool` | `bool \| int` | Keep page in sync with model | `src/Mod/TechDraw/App/DrawPage.cpp:66` |
| `NextBalloonIndex` | `App::PropertyInteger` | `int` | `int` | Auto-numbering for Balloons | `src/Mod/TechDraw/App/DrawPage.cpp:83` |
| `ProjectionType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/TechDraw/App/DrawPage.cpp:77` |
| `Scale` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Scale factor for this Page | `src/Mod/TechDraw/App/DrawPage.cpp:80` |
| `Template` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Attached Template | `src/Mod/TechDraw/App/DrawPage.cpp:68` |
| `Views` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Attached Views | `src/Mod/TechDraw/App/DrawPage.cpp:71` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

