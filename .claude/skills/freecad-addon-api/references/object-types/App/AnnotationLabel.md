# `App::AnnotationLabel`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/App/Annotation.cpp:44`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `BasePosition` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Base position | `src/App/Annotation.cpp:50` |
| `LabelText` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Text label of the annotation | `src/App/Annotation.cpp:49` |
| `TextPosition` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Text position | `src/App/Annotation.cpp:51` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

