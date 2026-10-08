# `App::Part`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/App/Part.cpp:36`. Abstract macro: no.

Native parent: [App::GeoFeature](../App/GeoFeature.md). Read the parent record for inherited properties.

Direct binding association: `FreeCAD.Part`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Color` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Not documented by registration | `src/App/Part.cpp:59` |
| `Id` | `App::PropertyString` | `str` | `str` | ID (Part-Number) of the Item | `src/App/Part.cpp:52` |
| `License` | `App::PropertyString` | `str` | `str` | License string of the Item | `src/App/Part.cpp:56` |
| `LicenseURL` | `App::PropertyString` | `str` | `str` | URL to the license text/contract | `src/App/Part.cpp:57` |
| `Material` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | The Material for this Part | `src/App/Part.cpp:47` |
| `Meta` | `App::PropertyMap` | `dict[str, str]` | `dict[str, str]` | Map with additional meta information | `src/App/Part.cpp:48` |
| `Type` | `App::PropertyString` | `str` | `str` | Not documented by registration | `src/App/Part.cpp:46` |
| `Uid` | `App::PropertyUUID` | `str` | `str` | UUID of the Item | `src/App/Part.cpp:53` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

