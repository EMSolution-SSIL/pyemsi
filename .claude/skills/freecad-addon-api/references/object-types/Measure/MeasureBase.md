# `Measure::MeasureBase`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Measure/App/MeasureBase.cpp:43`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Direct binding association: `Measure.MeasureBase`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `DisplayUnit` | `App::PropertyString` | `str` | `str` | User selected display unit override. Empty uses the global schema. | `src/Mod/Measure/App/MeasureBase.cpp:54` |
| `Placement` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Visual placement of the measurement | `src/Mod/Measure/App/MeasureBase.cpp:47` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

