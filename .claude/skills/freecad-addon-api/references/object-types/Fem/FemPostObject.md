# `Fem::FemPostObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemPostObject.cpp:39`. Abstract macro: no.

Native parent: [App::GeoFeature](../App/GeoFeature.md). Read the parent record for inherited properties.

Direct binding association: `Fem.FemPostObject`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Data` | `Fem::PropertyPostDataObject` | VTK Python data-object wrapper when FC_USE_VTK_PYTHON is enabled (source review) | VTK Python object convertible to vtkDataObject when FC_USE_VTK_PYTHON is enabled (source review) | Not documented by registration | `src/Mod/Fem/App/FemPostObject.cpp:44` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

