# `Fem::ConstraintForce`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemConstraintForce.cpp:35`. Abstract macro: no.

Native parent: [Fem::Constraint](../Fem/Constraint.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AmplitudeValues` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Amplitude values | `src/Mod/Fem/App/FemConstraintForce.cpp:68` |
| `Direction` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Element giving direction of constraint | `src/Mod/Fem/App/FemConstraintForce.cpp:40` |
| `DirectionVector` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Direction of arrows | `src/Mod/Fem/App/FemConstraintForce.cpp:51` |
| `EnableAmplitude` | `App::PropertyBool` | `bool` | `bool \| int` | Amplitude of the force load | `src/Mod/Fem/App/FemConstraintForce.cpp:61` |
| `Force` | `App::PropertyForce` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Not documented by registration | `src/Mod/Fem/App/FemConstraintForce.cpp:39` |
| `Reversed` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/Fem/App/FemConstraintForce.cpp:50` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

