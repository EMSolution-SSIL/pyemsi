# `Fem::ConstraintContact`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemConstraintContact.cpp:32`. Abstract macro: no.

Native parent: [Fem::Constraint](../Fem/Constraint.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Adjust` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Node clearance adjustment limit | `src/Mod/Fem/App/FemConstraintContact.cpp:46` |
| `EnableThermalContact` | `App::PropertyBool` | `bool` | `bool \| int` | Enable thermal contact | `src/Mod/Fem/App/FemConstraintContact.cpp:74` |
| `Friction` | `App::PropertyBool` | `bool` | `bool \| int` | Enable friction interaction | `src/Mod/Fem/App/FemConstraintContact.cpp:53` |
| `FrictionCoefficient` | `App::PropertyFloat` | `float` | `float` | Friction coefficient | `src/Mod/Fem/App/FemConstraintContact.cpp:60` |
| `ReversedMaster` | `App::PropertyBoolList` | tuple[bool, ...] (source review) | bool \| int \| Iterable[bool \| int] \| dict[int, bool \| int] \| str (source review) | Use reversed normal direction for master references | `src/Mod/Fem/App/FemConstraintContact.cpp:81` |
| `ReversedSlave` | `App::PropertyBoolList` | tuple[bool, ...] (source review) | bool \| int \| Iterable[bool \| int] \| dict[int, bool \| int] \| str (source review) | Use reversed normal direction for slave references | `src/Mod/Fem/App/FemConstraintContact.cpp:88` |
| `Slope` | `App::PropertyStiffnessDensity` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Contact stiffness | `src/Mod/Fem/App/FemConstraintContact.cpp:39` |
| `StickSlope` | `App::PropertyStiffnessDensity` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Stick slope | `src/Mod/Fem/App/FemConstraintContact.cpp:67` |
| `SurfaceBehavior` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Surface behavior type | `src/Mod/Fem/App/FemConstraintContact.cpp:102` |
| `ThermalContactConductance` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Thermal contact conductance | `src/Mod/Fem/App/FemConstraintContact.cpp:95` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

