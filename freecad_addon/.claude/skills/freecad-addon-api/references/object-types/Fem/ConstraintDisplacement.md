# `Fem::ConstraintDisplacement`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemConstraintDisplacement.cpp:34`. Abstract macro: no.

Native parent: [Fem::Constraint](../Fem/Constraint.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AmplitudeValues` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Amplitude values | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:197` |
| `EnableAmplitude` | `App::PropertyBool` | `bool` | `bool \| int` | Amplitude of the displacement boundary condition | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:190` |
| `hasXFormula` | `App::PropertyBool` | `bool` | `bool \| int` | Define translation in X-direction as a formula | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:59` |
| `hasYFormula` | `App::PropertyBool` | `bool` | `bool \| int` | Define translation in Y-direction as a formula | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:89` |
| `hasZFormula` | `App::PropertyBool` | `bool` | `bool \| int` | Define translation in Z-direction as a formula | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:119` |
| `rotxFree` | `App::PropertyBool` | `bool` | `bool \| int` | Use free rotation in X-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:144` |
| `rotyFree` | `App::PropertyBool` | `bool` | `bool \| int` | Use free rotation in Y-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:160` |
| `rotzFree` | `App::PropertyBool` | `bool` | `bool \| int` | Use free rotation in Z-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:176` |
| `useFlowSurfaceForce` | `App::PropertyBool` | `bool` | `bool \| int` | Use flow surface force | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:135` |
| `xDisplacement` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Translation in local X-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:52` |
| `xDisplacementFormula` | `App::PropertyString` | `str` | `str` | Formula for translation in X-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:66` |
| `xFree` | `App::PropertyBool` | `bool` | `bool \| int` | Use free translation in X-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:45` |
| `xRotation` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Rotation in local X-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:151` |
| `yDisplacement` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Translation in local Y-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:82` |
| `yDisplacementFormula` | `App::PropertyString` | `str` | `str` | Formula for translation in Y-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:96` |
| `yFree` | `App::PropertyBool` | `bool` | `bool \| int` | Use free translation in Y-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:75` |
| `yRotation` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Rotation in local Y-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:167` |
| `zDisplacement` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Translation in local Z-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:112` |
| `zDisplacementFormula` | `App::PropertyString` | `str` | `str` | Formula for translation in Z-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:126` |
| `zFree` | `App::PropertyBool` | `bool` | `bool \| int` | Use free translation in Z-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:105` |
| `zRotation` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Rotation in local Z-direction | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:183` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

