# `Fem::ConstraintHeatflux`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemConstraintHeatflux.cpp:33`. Abstract macro: no.

Native parent: [Fem::Constraint](../Fem/Constraint.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AmbientTemp` | `App::PropertyTemperature` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Ambient temperature | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:39` |
| `AmplitudeValues` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Amplitude values | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:74` |
| `CavityName` | `App::PropertyString` | `str` | `str` | Cavity name | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:59` |
| `CavityRadiation` | `App::PropertyBool` | `bool` | `bool \| int` | Cavity radiation | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:58` |
| `ClosedCavity` | `App::PropertyBool` | `bool` | `bool \| int` | Use closed cavity radiation | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:60` |
| `ConstraintType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Type of constraint, surface convection, radiation or surface heat flux | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:50` |
| `DistributedHeatFlux` | `App::PropertyHeatFlux` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Distributed heat flux | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:43` |
| `Emissivity` | `App::PropertyFloat` | `float` | `float` | Emissivity | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:42` |
| `EnableAmplitude` | `App::PropertyBool` | `bool` | `bool \| int` | Amplitude of the heat flux load | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:67` |
| `FilmCoef` | `App::PropertyThermalTransferCoefficient` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Film coefficient | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:41` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

