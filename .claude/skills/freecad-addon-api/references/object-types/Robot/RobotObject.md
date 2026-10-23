# `Robot::RobotObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Robot/App/RobotObject.cpp:37`. Abstract macro: no.

Native parent: [App::GeoFeature](../App/GeoFeature.md). Read the parent record for inherited properties.

Direct binding association: `Robot.RobotObject`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Axis1` | `App::PropertyFloat` | `float` | `float` | Axis 1 angle of the robot in degre | `src/Mod/Robot/App/RobotObject.cpp:57` |
| `Axis2` | `App::PropertyFloat` | `float` | `float` | Axis 2 angle of the robot in degre | `src/Mod/Robot/App/RobotObject.cpp:58` |
| `Axis3` | `App::PropertyFloat` | `float` | `float` | Axis 3 angle of the robot in degre | `src/Mod/Robot/App/RobotObject.cpp:59` |
| `Axis4` | `App::PropertyFloat` | `float` | `float` | Axis 4 angle of the robot in degre | `src/Mod/Robot/App/RobotObject.cpp:60` |
| `Axis5` | `App::PropertyFloat` | `float` | `float` | Axis 5 angle of the robot in degre | `src/Mod/Robot/App/RobotObject.cpp:61` |
| `Axis6` | `App::PropertyFloat` | `float` | `float` | Axis 6 angle of the robot in degre | `src/Mod/Robot/App/RobotObject.cpp:62` |
| `Base` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Actual base frame of the robot | `src/Mod/Robot/App/RobotObject.cpp:66` |
| `Error` | `App::PropertyString` | `str` | `str` | Robot error while moving | `src/Mod/Robot/App/RobotObject.cpp:63` |
| `Home` | `App::PropertyFloatList` | `list[float]` | `Sequence[float]` | Axis position for home | `src/Mod/Robot/App/RobotObject.cpp:96` |
| `RobotKinematicFile` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | Included file with kinematic definition of the robot Axis | `src/Mod/Robot/App/RobotObject.cpp:49` |
| `RobotVrmlFile` | `App::PropertyFileIncluded` | `str` | `_FileInput \| dict[str, str] \| tuple[str \| bytes, str \| bytes]` | Included file with the VRML representation of the robot | `src/Mod/Robot/App/RobotObject.cpp:42` |
| `Tcp` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Tcp of the robot | `src/Mod/Robot/App/RobotObject.cpp:65` |
| `Tool` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Tool frame of the robot (Tool) | `src/Mod/Robot/App/RobotObject.cpp:73` |
| `ToolBase` | `App::PropertyPlacement` | `Base.Placement` | `Base.Placement \| Base.Matrix` | Defines where to connect the ToolShape | `src/Mod/Robot/App/RobotObject.cpp:87` |
| `ToolShape` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Link to the Shape is used as Tool | `src/Mod/Robot/App/RobotObject.cpp:80` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

