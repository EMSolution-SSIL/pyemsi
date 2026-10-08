# `Fem::ConstraintBearing`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemConstraintBearing.cpp:39`. Abstract macro: no.

Native parent: [Fem::Constraint](../Fem/Constraint.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AxialFree` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/Fem/App/FemConstraintBearing.cpp:51` |
| `Axis` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Axis of bearing seat | `src/Mod/Fem/App/FemConstraintBearing.cpp:61` |
| `BasePoint` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Base point of cylindrical bearing seat | `src/Mod/Fem/App/FemConstraintBearing.cpp:54` |
| `Dist` | `App::PropertyFloat` | `float` | `float` | Not documented by registration | `src/Mod/Fem/App/FemConstraintBearing.cpp:50` |
| `Height` | `App::PropertyFloat` | `float` | `float` | Not documented by registration | `src/Mod/Fem/App/FemConstraintBearing.cpp:53` |
| `Location` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Element giving axial location of constraint | `src/Mod/Fem/App/FemConstraintBearing.cpp:43` |
| `Radius` | `App::PropertyFloat` | `float` | `float` | Not documented by registration | `src/Mod/Fem/App/FemConstraintBearing.cpp:52` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

