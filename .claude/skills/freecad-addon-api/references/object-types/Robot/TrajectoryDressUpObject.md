# `Robot::TrajectoryDressUpObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Robot/App/TrajectoryDressUpObject.cpp:33`. Abstract macro: no.

Native parent: [Robot::TrajectoryObject](../Robot/TrajectoryObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::GeoFeature` -> `FreeCAD.GeoFeature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::GeoFeature`: This implementation creates GeoFeaturePy. The binding is FreeCAD.GeoFeature; native descendants may override getPyObject. Evidence: `src/App/GeoFeature.cpp:82`, `src/App/GeoFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Acceleration` | `App::PropertyAcceleration` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Acceleration to use | `src/Mod/Robot/App/TrajectoryDressUpObject.cpp:52` |
| `AddType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | How to change the Position & Orientation | `src/Mod/Robot/App/TrajectoryDressUpObject.cpp:75` |
| `ContType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Define the dress up of continuity | `src/Mod/Robot/App/TrajectoryDressUpObject.cpp:60` |
| `PosAdd` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Position & Orientation to use | `src/Mod/Robot/App/TrajectoryDressUpObject.cpp:68` |
| `Source` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Trajectory to dress up | `src/Mod/Robot/App/TrajectoryDressUpObject.cpp:49` |
| `Speed` | `App::PropertySpeed` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Speed to use | `src/Mod/Robot/App/TrajectoryDressUpObject.cpp:50` |
| `UseAcceleration` | `App::PropertyBool` | `bool` | `bool \| int` | Switch the acceleration usage on | `src/Mod/Robot/App/TrajectoryDressUpObject.cpp:53` |
| `UseSpeed` | `App::PropertyBool` | `bool` | `bool \| int` | Switch the speed usage on | `src/Mod/Robot/App/TrajectoryDressUpObject.cpp:51` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

