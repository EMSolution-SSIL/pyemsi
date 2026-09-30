# `TechDraw::DrawViewImage`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewImage.cpp:43`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `TechDraw::DrawView` -> `TechDraw.DrawView`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Height` | `App::PropertyFloat` | `float` | `float` | The height of cropped image | `src/Mod/TechDraw/App/DrawViewImage.cpp:54` |
| `ImageFile` | `App::PropertyFile` | `str` | `str \| dict[str, str]` | The file containing this bitmap | `src/Mod/TechDraw/App/DrawViewImage.cpp:50` |
| `ImageIncluded` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | Embedded image file. System use only. | `src/Mod/TechDraw/App/DrawViewImage.cpp:51` |
| `Owner` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Feature to which this symbol is attached | `src/Mod/TechDraw/App/DrawViewImage.cpp:55` |
| `Width` | `App::PropertyFloat` | `float` | `float` | The width of cropped image | `src/Mod/TechDraw/App/DrawViewImage.cpp:53` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

