# `App::DatumElement`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/App/Datums.cpp:37`. Abstract macro: no.

Native parent: [App::GeoFeature](../App/GeoFeature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::GeoFeature` -> `FreeCAD.GeoFeature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::GeoFeature`: This implementation creates GeoFeaturePy. The binding is FreeCAD.GeoFeature; native descendants may override getPyObject. Evidence: `src/App/GeoFeature.cpp:82`, `src/App/GeoFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Role` | `App::PropertyString` | `str` | `str` | Role of the datum in the local coordinate system. | `src/App/Datums.cpp:46` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

