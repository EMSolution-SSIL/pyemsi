# `Fem::ConstraintFluidBoundary`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:37`. Abstract macro: no.

Native parent: [Fem::Constraint](../Fem/Constraint.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `BoundaryType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Basic boundary type like inlet, wall, outlet,etc | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:68` |
| `BoundaryValue` | `App::PropertyFloat` | `float` | `float` | Scaler value for the specific value subtype, like pressure, velocity magnitude | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:74` |
| `Direction` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Vector direction of BoundaryValue | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:77` |
| `DirectionVector` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Direction of arrows | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:99` |
| `HTCoeffValue` | `App::PropertyFloat` | `float` | `float` | Heat transfer coefficient for convective boundary condition | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:97` |
| `HeatFluxValue` | `App::PropertyFloat` | `float` | `float` | Heat flux value for thermal boundary condition | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:95` |
| `Reversed` | `App::PropertyBool` | `bool` | `bool \| int` | To distinguish inlet (flow outward from solid) or outlet boundary condition | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:79` |
| `Subtype` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Subtype defines more specific boundary types | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:71` |
| `TemperatureValue` | `App::PropertyFloat` | `float` | `float` | Temperature value for thermal boundary condition | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:93` |
| `ThermalBoundaryType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Thermal boundary type | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:90` |
| `TurbulenceSpecification` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Method to specify burbulence magnitude on the boundary | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:82` |
| `TurbulentIntensityValue` | `App::PropertyFloat` | `float` | `float` | Scaler value for Turbulent intensity etc | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:85` |
| `TurbulentLengthValue` | `App::PropertyFloat` | `float` | `float` | Scaler value for Turbulent length scale, hydraulic diameter etc | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:87` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

