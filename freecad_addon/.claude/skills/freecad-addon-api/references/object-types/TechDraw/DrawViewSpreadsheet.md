# `TechDraw::DrawViewSpreadsheet`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewSpreadsheet.cpp:50`. Abstract macro: no.

Native parent: [TechDraw::DrawViewSymbol](../TechDraw/DrawViewSymbol.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `TechDraw::DrawViewSymbol` -> `TechDraw.DrawViewSymbol`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `CellEnd` | `App::PropertyString` | `str` | `str` | The bottom right cell of the range to display | `src/Mod/TechDraw/App/DrawViewSpreadsheet.cpp:59` |
| `CellStart` | `App::PropertyString` | `str` | `str` | The top left cell of the range to display | `src/Mod/TechDraw/App/DrawViewSpreadsheet.cpp:58` |
| `Font` | `App::PropertyFont` | `str` | `str` | The name of the font to use | `src/Mod/TechDraw/App/DrawViewSpreadsheet.cpp:60` |
| `LineWidth` | `App::PropertyFloat` | `float` | `float` | The thickness of the cell lines | `src/Mod/TechDraw/App/DrawViewSpreadsheet.cpp:64` |
| `Owner` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Feature to which this sheet is attached | `src/Mod/TechDraw/App/DrawViewSpreadsheet.cpp:66` |
| `Source` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Spreadsheet to view | `src/Mod/TechDraw/App/DrawViewSpreadsheet.cpp:56` |
| `TextColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | The default color of the text and lines | `src/Mod/TechDraw/App/DrawViewSpreadsheet.cpp:62` |
| `TextSize` | `App::PropertyFloat` | `float` | `float` | The size of the text | `src/Mod/TechDraw/App/DrawViewSpreadsheet.cpp:63` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

