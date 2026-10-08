# `TechDraw::DrawViewArch`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewArch.cpp:42`. Abstract macro: no.

Native parent: [TechDraw::DrawViewSymbol](../TechDraw/DrawViewSymbol.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `TechDraw::DrawViewSymbol` -> `TechDraw.DrawViewSymbol`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AllOn` | `App::PropertyBool` | `bool` | `bool \| int` | If hidden objects must be shown or not | `src/Mod/TechDraw/App/DrawViewArch.cpp:56` |
| `CutLineWidth` | `App::PropertyFloat` | `float` | `float` | Width of cut lines of this view | `src/Mod/TechDraw/App/DrawViewArch.cpp:64` |
| `FillSpaces` | `App::PropertyBool` | `bool` | `bool \| int` | If True, BIM Spaces are shown as a colored area | `src/Mod/TechDraw/App/DrawViewArch.cpp:59` |
| `FontSize` | `App::PropertyFloat` | `float` | `float` | Text size for this view | `src/Mod/TechDraw/App/DrawViewArch.cpp:63` |
| `JoinArch` | `App::PropertyBool` | `bool` | `bool \| int` | If True, walls and structure will be fused by material | `src/Mod/TechDraw/App/DrawViewArch.cpp:65` |
| `LineSpacing` | `App::PropertyFloat` | `float` | `float` | The spacing between lines to use for multiline texts | `src/Mod/TechDraw/App/DrawViewArch.cpp:66` |
| `LineWidth` | `App::PropertyFloat` | `float` | `float` | Line width of this view | `src/Mod/TechDraw/App/DrawViewArch.cpp:62` |
| `RenderMode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | The render mode to use | `src/Mod/TechDraw/App/DrawViewArch.cpp:58` |
| `ShowFill` | `App::PropertyBool` | `bool` | `bool \| int` | If cut areas must be filled with a hatch pattern or not | `src/Mod/TechDraw/App/DrawViewArch.cpp:61` |
| `ShowHidden` | `App::PropertyBool` | `bool` | `bool \| int` | If the hidden geometry behind the section plane is shown or not | `src/Mod/TechDraw/App/DrawViewArch.cpp:60` |
| `Source` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | SectionPlane or BuildingPart object for this view | `src/Mod/TechDraw/App/DrawViewArch.cpp:54` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

