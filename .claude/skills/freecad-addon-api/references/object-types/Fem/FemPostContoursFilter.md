# `Fem::FemPostContoursFilter`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemPostFilter.cpp:882`. Abstract macro: no.

Native parent: [Fem::FemPostFilter](../Fem/FemPostFilter.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Fem::FemPostFilter` -> `Fem.FemPostFilter`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::GeoFeature`: This implementation creates GeoFeaturePy. The binding is FreeCAD.GeoFeature; native descendants may override getPyObject. Evidence: `src/App/GeoFeature.cpp:82`, `src/App/GeoFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Field` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | The field used to clip | `src/Mod/Fem/App/FemPostFilter.cpp:888` |
| `NoColor` | `App::PropertyBool` | `bool` | `bool \| int` | Don't color the contours | `src/Mod/Fem/App/FemPostFilter.cpp:890` |
| `NumberOfContours` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | The number of contours | `src/Mod/Fem/App/FemPostFilter.cpp:887` |
| `VectorMode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Select what vector field | `src/Mod/Fem/App/FemPostFilter.cpp:889` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

