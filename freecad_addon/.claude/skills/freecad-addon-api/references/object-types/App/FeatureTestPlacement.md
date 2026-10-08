# `App::FeatureTestPlacement`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/App/FeatureTest.cpp:319`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Input1` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Not documented by registration | `src/App/FeatureTest.cpp:324` |
| `Input2` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Not documented by registration | `src/App/FeatureTest.cpp:325` |
| `MultLeft` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Not documented by registration | `src/App/FeatureTest.cpp:326` |
| `MultRight` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Not documented by registration | `src/App/FeatureTest.cpp:327` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

