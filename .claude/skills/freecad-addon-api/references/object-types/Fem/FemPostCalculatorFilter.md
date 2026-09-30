# `Fem::FemPostCalculatorFilter`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemPostFilter.cpp:1416`. Abstract macro: no.

Native parent: [Fem::FemPostFilter](../Fem/FemPostFilter.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Fem::FemPostFilter` -> `Fem.FemPostFilter`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::GeoFeature`: This implementation creates GeoFeaturePy. The binding is FreeCAD.GeoFeature; native descendants may override getPyObject. Evidence: `src/App/GeoFeature.cpp:82`, `src/App/GeoFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `FieldName` | `App::PropertyString` | `str` | `str` | Name of the calculated field | `src/Mod/Fem/App/FemPostFilter.cpp:1421` |
| `Function` | `App::PropertyString` | `str` | `str` | Expression of the unction to evaluate | `src/Mod/Fem/App/FemPostFilter.cpp:1428` |
| `ReplaceInvalid` | `App::PropertyBool` | `bool` | `bool \| int` | Replace invalid values | `src/Mod/Fem/App/FemPostFilter.cpp:1436` |
| `ReplacementValue` | `App::PropertyFloat` | `float` | `float` | Value used to replace invalid operations | `src/Mod/Fem/App/FemPostFilter.cpp:1429` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

