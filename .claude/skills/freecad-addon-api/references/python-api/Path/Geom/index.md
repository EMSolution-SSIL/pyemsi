# Python source module `Path.Geom`

[Python catalogue](../../index.md)

Evidence: `src/Mod/CAM/Path/Geom.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Geom.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Geom.py:23`.

### import Path

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Geom.Path` -> `Path`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Geom.py:24`.

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Geom.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Geom.py:25`.

### from FreeCAD import Vector

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Geom.Vector` -> `FreeCAD.Vector`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Geom.py:27`.

### import Constants

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Geom.Constants` -> `Constants`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Geom.py:28`.

### from lazy_loader.lazy_loader import LazyLoader

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Geom.LazyLoader` -> `lazy_loader.lazy_loader.LazyLoader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Geom.py:31`.

## Classes

- [Path.Geom.Side](Side.md)

## `Path.Geom.Tolerance`

Status: source-defined name; no independently verified stability/export guarantee.

```python
Tolerance = 1e-06
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:40`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.Decimal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
Decimal = 6
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:41`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.translate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:43`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMoveRapid`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMoveRapid = Constants.GCODE_MOVE_RAPID
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:86`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMoveStraight`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMoveStraight = Constants.GCODE_MOVE_STRAIGHT
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:87`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMoveCW`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMoveCW = Constants.GCODE_MOVE_CW
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:88`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMoveCCW`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMoveCCW = Constants.GCODE_MOVE_CCW
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:89`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMoveDrill`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMoveDrill = Constants.GCODE_MOVE_DRILL
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:90`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMoveArc`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMoveArc = Constants.GCODE_MOVE_ARC
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:91`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMoveMill`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMoveMill = Constants.GCODE_MOVE_MILL
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:92`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMove`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMove = Constants.GCODE_MOVE
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:93`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMoveTap`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMoveTap = Constants.GCODE_MOVE_TAP
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:94`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.CmdMoveAll`

Status: source-defined name; no independently verified stability/export guarantee.

```python
CmdMoveAll = Constants.GCODE_MOVE_ALL
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Geom.py:95`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.ceil`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def ceil(value, decimal=Decimal):
```

ceil(value, [decimal=Decimal])
Rounding value to exclude precision error and returns ceiling result

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:98`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.isRoughly`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isRoughly(float1, float2, error=Tolerance):
```

isRoughly(float1, float2, [error=Tolerance])
Returns true if the two values are the same within a given error.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:104`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.isStrictlyGreater`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isStrictlyGreater(float1, float2, error=Tolerance):
```

isStrictlyGreater(float1, float2, [error=Tolerance])
Returns true if float1 is greater than float2 by more than a given error.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:110`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.isStrictlyLess`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isStrictlyLess(float1, float2, error=Tolerance):
```

isStrictlyLess(float1, float2, [error=Tolerance])
Returns true if float1 is less than float2 by more than a given error.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:116`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.isLessEqual`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isLessEqual(float1, float2, error=Tolerance):
```

isLessEqual(float1, float2, [error=Tolerance])
Returns true if float1 is less than float2 or the same within a given error.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:122`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.isGreaterEqual`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isGreaterEqual(float1, float2, error=Tolerance):
```

isGreaterEqual(float1, float2, [error=Tolerance])
Returns true if float1 is greater than float2 or the same within a given error.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:128`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.pointsCoincide`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def pointsCoincide(p1, p2, error=Tolerance):
```

pointsCoincide(p1, p2, [error=Tolerance])
Return True if two points are roughly identical (see also isRoughly).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:134`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.edgesMatch`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def edgesMatch(e0, e1, error=Tolerance):
```

edgesMatch(e0, e1, [error=Tolerance])
Return true if the edges start and end at the same point and have the same type of curve.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:140`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.edgeConnectsTo`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def edgeConnectsTo(edge, vector, error=Tolerance):
```

edgeConnectsTop(edge, vector, error=Tolerance)
Returns True if edge connects to given vector.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:151`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.normalizeAngle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def normalizeAngle(a):
```

normalizeAngle(a) ... return angle shifted into interval -pi <= a <= pi

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:159`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.getAngle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getAngle(vector):
```

getAngle(vector)
Returns the angle [-pi,pi] of a vector using the X-axis as the reference.
Positive angles for vertexes in the upper hemisphere (positive y values)
and negative angles for the lower hemisphere.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:168`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.diffAngle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def diffAngle(a1, a2, direction='CW'):
```

diffAngle(a1, a2, [direction='CW'])
Returns the difference between two angles (a1 -> a2) into a given direction.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:179`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.compareVecs`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def compareVecs(vec1, vec2, exact=False, error=Tolerance):
```

compareVecs(vec1, vec2, [exact=False, error=Tolerance])
Returns True if two vectors are aligned within a given error.
If exact is True, vectors must match direction.
Otherwise, alignment can indicate the vectors are the same or exactly opposite.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:193`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.isVertical`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isVertical(obj):
```

isVertical(obj) ... answer True if obj points into Z

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:207`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.isHorizontal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isHorizontal(obj):
```

isHorizontal(obj) ... answer True if obj points into X or Y

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:252`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.commandEndPoint`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def commandEndPoint(cmd, defaultPoint=Vector(), X='X', Y='Y', Z='Z'):
```

commandEndPoint(cmd, [defaultPoint=Vector()], [X='X'], [Y='Y'], [Z='Z'])
Extracts the end point from a Path Command.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:282`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.xy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def xy(point):
```

xy(point)
Convenience function to return the projection of the Vector in the XY-plane.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:291`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.speedBetweenPoints`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def speedBetweenPoints(p0, p1, hSpeed, vSpeed):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:297`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.cmdsForEdge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cmdsForEdge(edge, flip=False, approximation=False, hSpeed=0, vSpeed=0, tol=0.01):
```

cmdsForEdge(edge, flip=False, approximation=True) -> List(Path.Command)
Returns a list of Path.Command representing the given edge.

If 'flip' is True, the edge is considered to be backwards.

If 'approximation' is True:
- an edge based on BezierCurve, Ellipse, Hyperbola and Parabola
  will be represented as BSplineCurve;
- an edge based on a BSplineCurve will be represented as arcs and lines;
- not horizontal edge based on circle will be divided by short arcs
- arc with curvature less than tolerance will be represented as simple line

If 'approximation' is False and edge has no direct Path.Command mapping,
edge will be represented as number of short straight segments.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:323`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.edgeForCmd`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def edgeForCmd(cmd, startPoint):
```

edgeForCmd(cmd, startPoint).
Returns an Edge representing the given command, assuming a given startPoint.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:460`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.wireForPath`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def wireForPath(path, startPoint=Vector(0, 0, 0)):
```

wireForPath(path, [startPoint=Vector(0,0,0)])
Returns a wire representing all move commands found in the given path.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:544`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.wiresForPath`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def wiresForPath(path, startPoint=Vector(0, 0, 0)):
```

wiresForPath(path, [startPoint=Vector(0,0,0)])
Returns a collection of wires, each representing a continuous cutting Path in path.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:564`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.edgesToPoints`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def edgesToPoints(edges, chord, startPoint=None, error=Tolerance):
```

edgesToPoints(edges, chord, [startPoint=None, error=Tolerance])
Extract an ordered list of Vector waypoints from a sequence of connected edges
(e.g. wire.Edges, or a hand-ordered edge list).

Straight Line and LineSegment edges contribute only their two endpoints.
All other curve types (arcs, splines, etc.) are discretized at the given
chord spacing (mm) so their shape is preserved.

Each edge's samples are oriented to continue from the previous point, so the
edges need not share a consistent parametric direction (they only need to
connect end-to-end).  startPoint, when given, orients the first edge so its
nearest end leads.  Consecutive points closer than error are suppressed.

Returns a list of FreeCAD.Vector.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:585`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.arcToHelix`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def arcToHelix(edge, z0, z1):
```

arcToHelix(edge, z0, z1)
Assuming edge is an arc it'll return a helix matching the arc starting at z0 and rising/falling to z1.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:623`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.helixToArc`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def helixToArc(edge, z=0):
```

helixToArc(edge, z=0)
Returns the projection of the helix onto the XY-plane with a given offset.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:642`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.splitArcAt`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def splitArcAt(edge, pt):
```

splitArcAt(edge, pt)
Returns a list of 2 edges which together form the original arc split at the given point.
The Vector pt has to represent a point on the given arc.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:654`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.splitEdgeAt`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def splitEdgeAt(edge, pt):
```

splitEdgeAt(edge, pt)
Returns a list of 2 edges, forming the original edge split at the given point.
The results are undefined if the Vector representing the point is not part of the edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:664`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.splitArcEdge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def splitArcEdge(edge, tol=0.1):
```

splitArcEdge(edge) -> List(Part.Edge)
Returns a list of arc edges, angle each of them not great than 'maxArcAngle'
Useful for approximation not horizontal arcs and circles
Return a list with original edge, if arc angle less or equal 'maxArcAngle'

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:691`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.combineConnectedShapes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def combineConnectedShapes(shapes):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:731`. Decorators are copied as source expressions and have not been executed.

## `Path.Geom.uncompound`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def uncompound(shape):
```

uncompound(shape)
Go through the compound and return list of shapes
Can be useful to process shape Compound1(shape1, Compound2(shape2, Compound3(...)))

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Geom.py:761`. Decorators are copied as source expressions and have not been executed.

