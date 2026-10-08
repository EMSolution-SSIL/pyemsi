# `Fem::ConstraintTransform`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemConstraintTransform.cpp:35`. Abstract macro: no.

Native parent: [Fem::Constraint](../Fem/Constraint.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Axis` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Axis of cylindrical surface | `src/Mod/Fem/App/FemConstraintTransform.cpp:80` |
| `BasePoint` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Base point of cylindrical surface | `src/Mod/Fem/App/FemConstraintTransform.cpp:73` |
| `NameDispl` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Elements where the constraint is applied | `src/Mod/Fem/App/FemConstraintTransform.cpp:66` |
| `RefDispl` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Elements where the constraint is applied | `src/Mod/Fem/App/FemConstraintTransform.cpp:56` |
| `Rotation` | `App::PropertyRotation` | Base.Rotation (source review) | Base.Rotation \| Base.Matrix (source review) | Rectangular system transform | `src/Mod/Fem/App/FemConstraintTransform.cpp:41` |
| `TransformType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Type of transform, rectangular or cylindrical | `src/Mod/Fem/App/FemConstraintTransform.cpp:48` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

