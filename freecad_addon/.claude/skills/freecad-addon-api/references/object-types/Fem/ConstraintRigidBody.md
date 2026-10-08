# `Fem::ConstraintRigidBody`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemConstraintRigidBody.cpp:31`. Abstract macro: no.

Native parent: [Fem::Constraint](../Fem/Constraint.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AmplitudeValues` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Amplitude values | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:132` |
| `Displacement` | `App::PropertyPosition` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Reference node displacement | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:44` |
| `EnableAmplitude` | `App::PropertyBool` | `bool` | `bool \| int` | Amplitude of the rigid body boundary condition or load | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:125` |
| `ForceX` | `App::PropertyForce` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Applied force in X-direction | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:58` |
| `ForceY` | `App::PropertyForce` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Applied force in Y-direction | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:59` |
| `ForceZ` | `App::PropertyForce` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Applied force in Z-direction | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:60` |
| `MomentX` | `App::PropertyMoment` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Applied moment in X-direction | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:61` |
| `MomentY` | `App::PropertyMoment` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Applied moment in Y-direction | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:68` |
| `MomentZ` | `App::PropertyMoment` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Applied moment in Z-direction | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:75` |
| `ReferenceNode` | `App::PropertyPosition` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Reference node position | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:37` |
| `Rotation` | `App::PropertyRotation` | Base.Rotation (source review) | Base.Rotation \| Base.Matrix (source review) | Reference node rotation | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:51` |
| `RotationalModeX` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | X-direction rotation/moment mode | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:103` |
| `RotationalModeY` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Y-direction rotation/moment mode | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:110` |
| `RotationalModeZ` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Z-direction rotation/moment mode | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:117` |
| `TranslationalModeX` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | X-direction displacement/force  mode | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:82` |
| `TranslationalModeY` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Y-direction displacement/force  mode | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:89` |
| `TranslationalModeZ` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Z-direction displacement/force  mode | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:96` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

