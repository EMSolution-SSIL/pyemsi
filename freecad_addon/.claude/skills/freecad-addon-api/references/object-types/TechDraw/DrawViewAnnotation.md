# `TechDraw::DrawViewAnnotation`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewAnnotation.cpp:36`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawViewAnnotation`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Font` | `App::PropertyFont` | `str` | `str` | Font name | `src/Mod/TechDraw/App/DrawViewAnnotation.cpp:49` |
| `LineSpace` | `App::PropertyInteger` | `int` | `int` | Line spacing in %. 100 means single spaced,  200 would be double spaced. | `src/Mod/TechDraw/App/DrawViewAnnotation.cpp:55` |
| `MaxWidth` | `App::PropertyFloat` | `float` | `float` | Maximum width of the annotation block (in mm).  -1 means no maximum width. | `src/Mod/TechDraw/App/DrawViewAnnotation.cpp:54` |
| `Owner` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Feature to which this annotation is attached, if any | `src/Mod/TechDraw/App/DrawViewAnnotation.cpp:60` |
| `Text` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Annotation text | `src/Mod/TechDraw/App/DrawViewAnnotation.cpp:48` |
| `TextColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Text color | `src/Mod/TechDraw/App/DrawViewAnnotation.cpp:51` |
| `TextSize` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Text size | `src/Mod/TechDraw/App/DrawViewAnnotation.cpp:52` |
| `TextStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Text style | `src/Mod/TechDraw/App/DrawViewAnnotation.cpp:58` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

