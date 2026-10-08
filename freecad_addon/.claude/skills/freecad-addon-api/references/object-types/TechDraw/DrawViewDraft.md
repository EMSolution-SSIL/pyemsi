# `TechDraw::DrawViewDraft`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewDraft.cpp:43`. Abstract macro: no.

Native parent: [TechDraw::DrawViewSymbol](../TechDraw/DrawViewSymbol.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `TechDraw::DrawViewSymbol` -> `TechDraw.DrawViewSymbol`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Color` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | The default color of text and lines | `src/Mod/TechDraw/App/DrawViewDraft.cpp:55` |
| `Direction` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Projection direction. The direction you are looking from. | `src/Mod/TechDraw/App/DrawViewDraft.cpp:54` |
| `FontSize` | `App::PropertyFloat` | `float` | `float` | Text size for this view | `src/Mod/TechDraw/App/DrawViewDraft.cpp:53` |
| `LineSpacing` | `App::PropertyFloat` | `float` | `float` | The spacing between lines to use for multiline texts | `src/Mod/TechDraw/App/DrawViewDraft.cpp:57` |
| `LineStyle` | `App::PropertyString` | `str` | `str` | A line style to use for this view. Can be Solid, Dashed, Dashdot, Dot or a SVG pattern like 0.20, 0.20 | `src/Mod/TechDraw/App/DrawViewDraft.cpp:56` |
| `LineWidth` | `App::PropertyFloat` | `float` | `float` | Line width of this view. If Override Style is false, this value multiplies the object line width | `src/Mod/TechDraw/App/DrawViewDraft.cpp:52` |
| `OverrideStyle` | `App::PropertyBool` | `bool` | `bool \| int` | If True, line color, width and style of this view will override those of rendered objects | `src/Mod/TechDraw/App/DrawViewDraft.cpp:58` |
| `Source` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Draft object for this view | `src/Mod/TechDraw/App/DrawViewDraft.cpp:50` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

