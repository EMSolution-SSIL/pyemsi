# `Fem::ConstraintGear`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemConstraintGear.cpp:35`. Abstract macro: no.

Native parent: [Fem::ConstraintBearing](../Fem/ConstraintBearing.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Diameter` | `App::PropertyFloat` | `float` | `float` | Not documented by registration | `src/Mod/Fem/App/FemConstraintGear.cpp:39` |
| `Direction` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Element giving direction of gear force | `src/Mod/Fem/App/FemConstraintGear.cpp:42` |
| `DirectionVector` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Direction of gear force | `src/Mod/Fem/App/FemConstraintGear.cpp:50` |
| `Force` | `App::PropertyFloat` | `float` | `float` | Not documented by registration | `src/Mod/Fem/App/FemConstraintGear.cpp:40` |
| `ForceAngle` | `App::PropertyFloat` | `float` | `float` | Not documented by registration | `src/Mod/Fem/App/FemConstraintGear.cpp:41` |
| `Reversed` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/Fem/App/FemConstraintGear.cpp:49` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

