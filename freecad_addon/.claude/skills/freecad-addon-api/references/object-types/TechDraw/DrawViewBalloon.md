# `TechDraw::DrawViewBalloon`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewBalloon.cpp:59`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `TechDraw::DrawView` -> `TechDraw.DrawView`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `BubbleShape` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Shape of the balloon bubble | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:82` |
| `EndType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | End symbol for the balloon line | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:74` |
| `EndTypeScale` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | End symbol scale factor | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:77` |
| `KinkLength` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Distance from symbol to leader kink | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:92` |
| `OriginX` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Balloon origin x | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:70` |
| `OriginY` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Balloon origin y | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:71` |
| `ShapeScale` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Balloon shape scale | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:85` |
| `SourceView` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Source view for balloon | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:68` |
| `Text` | `App::PropertyString` | `str` | `str` | The text to be displayed | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:67` |
| `TextWrapLen` | `App::PropertyFloat` | `float` | `float` | Text wrap length; -1 means no wrap | `src/Mod/TechDraw/App/DrawViewBalloon.cpp:89` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

