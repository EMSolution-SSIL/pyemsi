# `TechDraw::DrawLeaderLine`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawLeaderLine.cpp:53`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawLeaderLine`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AutoHorizontal` | `App::PropertyBool` | `bool` | `bool \| int` | Forces last line segment to be horizontal | `src/Mod/TechDraw/App/DrawLeaderLine.cpp:97` |
| `EndSymbol` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/TechDraw/App/DrawLeaderLine.cpp:94` |
| `LeaderParent` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | View to which this leader is attached | `src/Mod/TechDraw/App/DrawLeaderLine.cpp:84` |
| `RotatesWithParent` | `App::PropertyBool` | `bool` | `bool \| int` | If true, leader rotates around parent.  If false, only first segment of leader changes with parent rotation. | `src/Mod/TechDraw/App/DrawLeaderLine.cpp:98` |
| `Scalable` | `App::PropertyBool` | `bool` | `bool \| int` | Scale line with LeaderParent | `src/Mod/TechDraw/App/DrawLeaderLine.cpp:96` |
| `StartSymbol` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/TechDraw/App/DrawLeaderLine.cpp:91` |
| `WayPoints` | `App::PropertyVectorList` | `list[Base.Vector]` | `Sequence[_VectorInput]` | Intermediate points for Leader line | `src/Mod/TechDraw/App/DrawLeaderLine.cpp:87` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

