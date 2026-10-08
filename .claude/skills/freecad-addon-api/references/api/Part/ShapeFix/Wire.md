# `Part.ShapeFix.Wire`

[Module](index.md)

```python
class Wire(Root):
```

Class for fixing operations on wires

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 822. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.Wire.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, wire: TopoShapeWire, face: TopoShapeFace, prec: float, /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 831, 835.

## `Part.ShapeFix.Wire.init`

```python
def init(self, wire: TopoShapeWire, face: TopoShapeFace, prec: float, /) -> None:
```

Initializes by wire, face, precision

Evidence: public stub `Part/ShapeFix.pyi` line(s) 838.

## `Part.ShapeFix.Wire.fixEdgeTool`

```python
def fixEdgeTool(self) -> Edge:
```

Returns tool for fixing wires

Evidence: public stub `Part/ShapeFix.pyi` line(s) 844.

## `Part.ShapeFix.Wire.clearModes`

```python
def clearModes(self) -> None:
```

Sets all modes to default

Evidence: public stub `Part/ShapeFix.pyi` line(s) 850.

## `Part.ShapeFix.Wire.clearStatuses`

```python
def clearStatuses(self) -> None:
```

Clears all statuses

Evidence: public stub `Part/ShapeFix.pyi` line(s) 856.

## `Part.ShapeFix.Wire.load`

```python
def load(self, wire: TopoShapeWire, /) -> None:
```

Load data for the wire, and drops all fixing statuses

Evidence: public stub `Part/ShapeFix.pyi` line(s) 862.

## `Part.ShapeFix.Wire.setFace`

```python
def setFace(self, face: TopoShapeFace, /) -> None:
```

Set working face for the wire

Evidence: public stub `Part/ShapeFix.pyi` line(s) 868.

## `Part.ShapeFix.Wire.setSurface`

```python
def setSurface(self, surface: object, placement: object=..., /) -> None:
```

setSurface(surface, [Placement])
Set surface for the wire

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 874.

## `Part.ShapeFix.Wire.setMaxTailAngle`

```python
def setMaxTailAngle(self, angle: float, /) -> None:
```

Sets the maximal allowed angle of the tails in radians

Evidence: public stub `Part/ShapeFix.pyi` line(s) 881.

## `Part.ShapeFix.Wire.setMaxTailWidth`

```python
def setMaxTailWidth(self, width: float, /) -> None:
```

Sets the maximal allowed width of the tails

Evidence: public stub `Part/ShapeFix.pyi` line(s) 887.

## `Part.ShapeFix.Wire.isLoaded`

```python
def isLoaded(self) -> bool:
```

Tells if the wire is loaded

Evidence: public stub `Part/ShapeFix.pyi` line(s) 893.

## `Part.ShapeFix.Wire.isReady`

```python
def isReady(self) -> bool:
```

Tells if the wire and face are loaded

Evidence: public stub `Part/ShapeFix.pyi` line(s) 899.

## `Part.ShapeFix.Wire.numberOfEdges`

```python
def numberOfEdges(self) -> int:
```

Returns number of edges in the working wire

Evidence: public stub `Part/ShapeFix.pyi` line(s) 905.

## `Part.ShapeFix.Wire.wire`

```python
def wire(self) -> TopoShape:
```

Makes the resulting Wire (by basic Brep_Builder)

Evidence: public stub `Part/ShapeFix.pyi` line(s) 911.

## `Part.ShapeFix.Wire.wireAPIMake`

```python
def wireAPIMake(self) -> TopoShape:
```

Makes the resulting Wire (by BRepAPI_MakeWire)

Evidence: public stub `Part/ShapeFix.pyi` line(s) 917.

## `Part.ShapeFix.Wire.face`

```python
def face(self) -> TopoShape:
```

Returns working face

Evidence: public stub `Part/ShapeFix.pyi` line(s) 923.

## `Part.ShapeFix.Wire.perform`

```python
def perform(self) -> bool:
```

Iterates on subshapes and performs fixes

Evidence: public stub `Part/ShapeFix.pyi` line(s) 929.

## `Part.ShapeFix.Wire.fixReorder`

```python
def fixReorder(self) -> bool:
```

Performs an analysis and reorders edges in the wire

Evidence: public stub `Part/ShapeFix.pyi` line(s) 935.

## `Part.ShapeFix.Wire.fixSmall`

```python
@overload
def fixSmall(self, lock: bool, prec: float=..., /) -> int:

@overload
def fixSmall(self, num: int, lock: bool, prec: float, /) -> bool:

def fixSmall(self, *args) -> int | bool:
```

Applies fixSmall(...) to all edges in the wire

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 942, 946, 949.

## `Part.ShapeFix.Wire.fixConnected`

```python
@overload
def fixConnected(self, prec: float=..., /) -> bool:

@overload
def fixConnected(self, num: int, prec: float, /) -> bool:

def fixConnected(self, *args) -> bool:
```

Applies fixConnected(num) to all edges in the wire
Connection between first and last edges is treated only if
flag ClosedMode is True
If prec is -1 then maxTolerance() is taken.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 956, 960, 963.

## `Part.ShapeFix.Wire.fixEdgeCurves`

```python
def fixEdgeCurves(self) -> bool:
```

Groups the fixes dealing with 3d and pcurves of the edges

Evidence: public stub `Part/ShapeFix.pyi` line(s) 972.

## `Part.ShapeFix.Wire.fixDegenerated`

```python
def fixDegenerated(self, num: int=..., /) -> bool:
```

Applies fixDegenerated(...) to all edges in the wire

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 978.

## `Part.ShapeFix.Wire.fixSelfIntersection`

```python
def fixSelfIntersection(self) -> bool:
```

Applies FixSelfIntersectingEdge(num) and
 FixIntersectingEdges(num) to all edges in the wire and
 FixIntersectingEdges(num1, num2) for all pairs num1 and num2
 and removes wrong edges if any

Evidence: public stub `Part/ShapeFix.pyi` line(s) 984.

## `Part.ShapeFix.Wire.fixLacking`

```python
@overload
def fixLacking(self, force: bool=..., /) -> bool:

@overload
def fixLacking(self, num: int, force: bool=..., /) -> bool:

def fixLacking(self, *args) -> bool:
```

Applies FixLacking(num) to all edges in the wire
Connection between first and last edges is treated only if
flag ClosedMode is True
If 'force' is False (default), test for connectness is done with
precision of vertex between edges, else it is done with minimal
value of vertex tolerance and Analyzer.Precision().
Hence, 'force' will lead to inserting lacking edges in replacement
of vertices which have big tolerances.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 994, 998, 1001.

## `Part.ShapeFix.Wire.fixClosed`

```python
def fixClosed(self, prec: float=..., /) -> bool:
```

Fixes a wire to be well closed

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1014.

## `Part.ShapeFix.Wire.fixGaps3d`

```python
def fixGaps3d(self) -> bool:
```

Fixes gaps between ends of 3d curves on adjacent edges

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1020.

## `Part.ShapeFix.Wire.fixGaps2d`

```python
def fixGaps2d(self) -> bool:
```

Fixes gaps between ends of pcurves on adjacent edges

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1026.

## `Part.ShapeFix.Wire.fixSeam`

```python
def fixSeam(self, num: int, /) -> bool:
```

Fixes seam edges

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1032.

## `Part.ShapeFix.Wire.fixShifted`

```python
def fixShifted(self) -> bool:
```

Fixes edges which have pcurves shifted by whole parameter
range on the closed surface

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1038.

## `Part.ShapeFix.Wire.fixNotchedEdges`

```python
def fixNotchedEdges(self) -> bool:
```

Fixes Notch edges.Check if there are notch edges in 2d and fix it

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1045.

## `Part.ShapeFix.Wire.fixGap3d`

```python
def fixGap3d(self, num: int, convert: bool, /) -> bool:
```

Fixes gap between ends of 3d curves on num-1 and num-th edges

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1051.

## `Part.ShapeFix.Wire.fixGap2d`

```python
def fixGap2d(self, num: int, convert: bool, /) -> bool:
```

Fixes gap between ends of pcurves on num-1 and num-th edges

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1057.

## `Part.ShapeFix.Wire.fixTails`

```python
def fixTails(self) -> bool:
```

Fixes issues related to 'tails' in the geometry.
Tails are typically small, undesired protrusions or deviations in the curves or edges that need correction.
This method examines the geometry and applies corrective actions to eliminate or reduce the presence of tails.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1063.

## `Part.ShapeFix.Wire.ModifyTopologyMode`

```python
ModifyTopologyMode: bool = ...
```

Mode for modifying topology of the wire

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1070.

## `Part.ShapeFix.Wire.ModifyGeometryMode`

```python
ModifyGeometryMode: bool = ...
```

Mode for modifying geometry of vertexes and edges

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1072.

## `Part.ShapeFix.Wire.ModifyRemoveLoopMode`

```python
ModifyRemoveLoopMode: bool = ...
```

Mode for modifying edges

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1074.

## `Part.ShapeFix.Wire.ClosedWireMode`

```python
ClosedWireMode: bool = ...
```


    Mode which defines whether the wire
    is to be closed (by calling methods like fixDegenerated()
    and fixConnected() for last and first edges)
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1076.

## `Part.ShapeFix.Wire.PreferencePCurveMode`

```python
PreferencePCurveMode: bool = ...
```


    Mode which defines whether the 2d 'True'
    representation of the wire is preferable over 3d one in the
    case of ambiguity in FixEdgeCurves
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1078.

## `Part.ShapeFix.Wire.FixGapsByRangesMode`

```python
FixGapsByRangesMode: bool = ...
```


    Mode which defines whether tool
    tries to fix gaps first by changing curves ranges (i.e.
    using intersection, extrema, projections) or not
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1080.

## `Part.ShapeFix.Wire.FixReorderMode`

```python
FixReorderMode: bool = ...
```


    Mode which performs an analysis and reorders edges in the wire using class WireOrder.
    Flag 'theModeBoth' determines the use of miscible mode if necessary.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1082.

## `Part.ShapeFix.Wire.FixSmallMode`

```python
FixSmallMode: bool = ...
```

Mode which applies FixSmall(num) to all edges in the wire

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1084.

## `Part.ShapeFix.Wire.FixConnectedMode`

```python
FixConnectedMode: bool = ...
```


    Mode which applies FixConnected(num) to all edges in the wire
    Connection between first and last edges is treated only if
    flag ClosedMode is True
    If 'prec' is -1 then MaxTolerance() is taken.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1086.

## `Part.ShapeFix.Wire.FixEdgeCurvesMode`

```python
FixEdgeCurvesMode: bool = ...
```


    Mode which groups the fixes dealing with 3d and pcurves of the edges.
    The order of the fixes and the default behaviour are:
    ShapeFix_Edge::FixReversed2d
    ShapeFix_Edge::FixRemovePCurve (only if forced)
    ShapeFix_Edge::FixAddPCurve
    ShapeFix_Edge::FixRemoveCurve3d (only if forced)
    ShapeFix_Edge::FixAddCurve3d
    FixSeam,
    FixShifted,
    ShapeFix_Edge::FixSameParameter
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1088.

## `Part.ShapeFix.Wire.FixDegeneratedMode`

```python
FixDegeneratedMode: bool = ...
```


    Mode which applies FixDegenerated(num) to all edges in the wire
    Connection between first and last edges is treated only if
    flag ClosedMode is True
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1090.

## `Part.ShapeFix.Wire.FixSelfIntersectionMode`

```python
FixSelfIntersectionMode: bool = ...
```


    Mode which applies FixSelfIntersectingEdge(num) and
    FixIntersectingEdges(num) to all edges in the wire and
    FixIntersectingEdges(num1, num2) for all pairs num1 and num2
    and removes wrong edges if any
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1092.

## `Part.ShapeFix.Wire.FixLackingMode`

```python
FixLackingMode: bool = ...
```


    Mode which applies FixLacking(num) to all edges in the wire
    Connection between first and last edges is treated only if
    flag ClosedMode is True
    If 'force' is False (default), test for connectness is done with
    precision of vertex between edges, else it is done with minimal
    value of vertex tolerance and Analyzer.Precision().
    Hence, 'force' will lead to inserting lacking edges in replacement
    of vertices which have big tolerances.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1094.

## `Part.ShapeFix.Wire.FixGaps3dMode`

```python
FixGaps3dMode: bool = ...
```


    Mode which fixes gaps between ends of 3d curves on adjacent edges
    myPrecision is used to detect the gaps.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1096.

## `Part.ShapeFix.Wire.FixGaps2dMode`

```python
FixGaps2dMode: bool = ...
```


    Mode whixh fixes gaps between ends of pcurves on adjacent edges
    myPrecision is used to detect the gaps.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1098.

## `Part.ShapeFix.Wire.FixReversed2dMode`

```python
FixReversed2dMode: bool = ...
```

Mode which fixes the reversed in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1100.

## `Part.ShapeFix.Wire.FixRemovePCurveMode`

```python
FixRemovePCurveMode: bool = ...
```

Mode which removePCurve in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1102.

## `Part.ShapeFix.Wire.FixAddPCurveMode`

```python
FixAddPCurveMode: bool = ...
```

Mode which fixes addCurve in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1104.

## `Part.ShapeFix.Wire.FixRemoveCurve3dMode`

```python
FixRemoveCurve3dMode: bool = ...
```

Mode which fixes removeCurve in 3d 

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1106.

## `Part.ShapeFix.Wire.FixAddCurve3dMode`

```python
FixAddCurve3dMode: bool = ...
```

Mode which fixes addCurve in 3d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1108.

## `Part.ShapeFix.Wire.FixSeamMode`

```python
FixSeamMode: bool = ...
```

Mode which fixes Seam 

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1110.

## `Part.ShapeFix.Wire.FixShiftedMode`

```python
FixShiftedMode: bool = ...
```

Mode which fixes Shifted

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1112.

## `Part.ShapeFix.Wire.FixSameParameterMode`

```python
FixSameParameterMode: bool = ...
```

Mode which fixes sameParameter in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1114.

## `Part.ShapeFix.Wire.FixVertexToleranceMode`

```python
FixVertexToleranceMode: bool = ...
```

Mode which fixes VertexTolerence in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1116.

## `Part.ShapeFix.Wire.FixNotchedEdgesMode`

```python
FixNotchedEdgesMode: bool = ...
```

Mode which fixes NotchedEdges in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1118.

## `Part.ShapeFix.Wire.FixSelfIntersectingEdgeMode`

```python
FixSelfIntersectingEdgeMode: bool = ...
```

Mode which fixes SelfIntersectionEdge in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1120.

## `Part.ShapeFix.Wire.FixIntersectingEdgesMode`

```python
FixIntersectingEdgesMode: bool = ...
```

Mode which fixes IntersectingEdges in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1122.

## `Part.ShapeFix.Wire.FixNonAdjacentIntersectingEdgesMode`

```python
FixNonAdjacentIntersectingEdgesMode: bool = ...
```

Mode which fixes NonAdjacentIntersectingEdges in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1124.

## `Part.ShapeFix.Wire.FixTailMode`

```python
FixTailMode: bool = ...
```

Mode which fixes Tails in 2d

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1126.

