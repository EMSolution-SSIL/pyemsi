# `Gui::ViewProviderTextDocument`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Gui/ViewProviderTextDocument.cpp:42`. Abstract macro: no.

Native parent: [Gui::ViewProviderDocumentObject](../Gui/ViewProviderDocumentObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Gui::ViewProviderDocumentObject` -> `FreeCADGui.ViewProviderDocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `FontName` | `App::PropertyFont` | `str` | `str` | Font name | `src/Gui/ViewProviderTextDocument.cpp:79` |
| `FontSize` | `App::PropertyFloat` | `float` | `float` | Font size | `src/Gui/ViewProviderTextDocument.cpp:78` |
| `ReadOnly` | `App::PropertyBool` | `bool` | `bool \| int` | Defines whether the content can be edited. | `src/Gui/ViewProviderTextDocument.cpp:49` |
| `SyntaxHighlighter` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Syntax highlighting | `src/Gui/ViewProviderTextDocument.cpp:87` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

