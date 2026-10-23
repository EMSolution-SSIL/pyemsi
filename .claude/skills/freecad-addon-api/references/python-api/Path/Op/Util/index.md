# Python source module `Path.Op.Util`

[Python catalogue](../../../index.md)

Evidence: `src/Mod/CAM/Path/Op/Util.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Op.Util.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Op/Util.py:23`.

### import Path

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Op.Util.Path` -> `Path`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Op/Util.py:24`.

### import Path.Base.Util as PathUtil

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Op.Util.PathUtil` -> `Path.Base.Util`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Op/Util.py:25`.

### import Path.Dressup.Utils as PathDressup

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Op.Util.PathDressup` -> `Path.Dressup.Utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Op/Util.py:26`.

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Op.Util.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Op/Util.py:27`.

### import time

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Op.Util.time` -> `time`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Op/Util.py:28`.

### import area

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Op.Util.area` -> `area`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Op/Util.py:29`.

### from lazy_loader.lazy_loader import LazyLoader

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Op.Util.LazyLoader` -> `lazy_loader.lazy_loader.LazyLoader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Op/Util.py:32`.

## `Path.Op.Util.PrintWireDebug`

Status: source-defined name; no independently verified stability/export guarantee.

```python
PrintWireDebug = False
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Op/Util.py:42`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.translate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Op/Util.py:50`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.debugEdge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def debugEdge(label, e):
```

debugEdge(label, e) ... prints a python statement to create e
Currently lines and arcs are supported.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:53`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.makeWires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeWires(inEdges):
```

makeWires ... function to make non-forking wires from a collection of edges

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:86`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.debugWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def debugWire(label, w):
```

debugWire(label, w) ... prints python statements for all edges of w to be added to the object tree in a group.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:93`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.getCoincideTolerance`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getCoincideTolerance(edges):
```

getCoincideTolerance(edges) ... Returns actual tolerance of edges connection in wire
Assumes the edges are in an order so they can be connected.
Return None if any edge length less than defined tolerance

Note:
Default tolerance of methods Part.sortEdges() and Part.__sortEdges__()
is Base.Precision.confusion() => 1e-7

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:107`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.isWireClockwise`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isWireClockwise(w):
```

isWireClockwise(w) ... returns True if the wire winds clockwise.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:192`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.orientWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def orientWire(w, forward=True):
```

orientWire(w, forward=True) ... orients given wire in a specific direction.
If forward = True (the default) the wire is oriented clockwise, looking down the negative Z axis.
If forward = False the wire is oriented counter clockwise.
If forward = None the orientation is determined by the order in which the edges appear in the wire.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:197`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.approximateWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def approximateWire(wire, tolerance=0.01):
```

approximateWire approximates any non-line/arc edges with lines or arcs.
Edges that are lines or circular arcs are kept as-is.
tolerance: Deflection tolerance for approximation. Must be positive if wire contains non-line/arc edges.
Returns the wire with non-line/arc edges replaced by arcs and line segments.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:213`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.wireToCArea`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def wireToCArea(wire, tolerance=0.01):
```

wireToCArea(wire) ... converts a FreeCAD wire to a Clipper Area representation.

Parameters:
    wire: Part.Wire to convert

Returns:
    area.Area object containing a single curve representing the wire's geometry

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:265`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.cAreaToWires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cAreaToWires(carea, z=0.0, tolerance=0.01):
```

cAreaToWires(carea, z, tolerance) ... converts a Clipper Area to FreeCAD wires.

Parameters:
    carea: area.Area object to convert
    z: Z-coordinate for the wires (default: 0.0)
    tolerance: Tolerance to set on vertices (default: 0.01)

Returns:
    list of Part.Wire objects

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:329`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.offsetWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def offsetWire(wire, base, offset, tolerance=0.01):
```

offsetWire performs an open path offset using Clipper library.

tolerance: Deflection tolerance for discretization. Must be positive

Note that there is also offsetWireCompat, which is a direct migration of
the old offsetWire implementation. This version makes simpler choices
about the direction in which it offsets, and the orientation of its result curves.

return: (pos_wires, neg_wires): the wires resulting from performing the requested
open wire offset, and the negative of the requested offset. If the input wire is
open, all output wires are oriented in the same direction as the input. If it is
closed, output orientation will match the input if the input encloses positive
area, and be flipped if the input encloses negative area. (Future note: if this
flipping behavior is undesirable, we'll need a new flag to disable it in the C++
implementation. It was needed in C++ for compatibility with old behavior.)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:412`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.offsetWireCompat`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def offsetWireCompat(wire, base, offset, Side=None, tolerance=0.01):
```

offsetWire performs an open path offset using Clipper library.

tolerance: Deflection tolerance for discretization. Must be positive

offsetWireCompat is a direct migration of the old offsetWire implementation.
It preserves old decisions about how the offset side is chosen, and the orientation
of output wires. Some of these choices are poor choices, imo, so I have also
implemented an alternative offsetWire function with that simply does type
conversions and connects to the C++ open wire offset functionality.

Compat offset side: this method tries to automatically detect which offset
direction is into the part and which direction is outside the part, and returns
the outside-direction offset, regardless of the sign of the offset parameter.

Compat result orientation: for the most part, results are returned in the correct
orientation for climb cutting an offset path. This means that external offsets
are clockwise, and internal offsets are counterclockwise. However, to preserve
old behavior, single-edge circular wires are always returned in the clockwise
orientation. I think this is a bug that should be fixed. Also I think the caller
ought to be able to choose if the output wires are oriented for climb cutting (or
conventional) or if they should be oriented correctly for positive winding rules.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:463`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.getClearedAreas`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getClearedAreas(currentOp, bbox):
```

Returns the cleared area relevant to the operation
- currentOp: the operation we are checking for. Only operations performed
  before this operation will be considered
- bbox: the cleared region is only generated where it is close enough to
  impact the bbox region

Operations whose Workplane differs from the current op's are skipped:
each op's Path stores X/Y/Z in the rotated workplane frame used at
generation time, and projecting cleared area between non-coplanar
workplanes has no meaningful 2D interpretation. For ops that share a
non-Z-up Workplane the path's leading rotary G0 is stripped before
walking so positions are read in the same rotated frame as bbox.

Frames are compared with PathUtil.sameWorkplane() rather than by hand.
That predicate compares tool axes only, which is correct while a
Workplane's origin is recorded but not consumed; when origins are
consumed, two operations sharing a tool axis but not an origin stop
being the same frame and this reuse becomes wrong. Changing the
predicate has to change this function with it.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:578`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.getOpSide`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getOpSide(obj, default='Outside'):
```

getOpSide(obj) ...  offer side for op base

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:625`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.getCycleTimeEstimate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getCycleTimeEstimate(obj, formatted=True):
```

getCycleTimeEstimate(obj, formated=True) ... Returns operation cycle time estimation
If formatted=True returns string which describes time in format 'hh:mm:ss'
If formatted=False returns seconds as a float value

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:701`. Decorators are copied as source expressions and have not been executed.

## `Path.Op.Util.drillTipLength`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def drillTipLength(tool):
```

returns the length of the drillbit tip. Tools without a TipAngle (e.g. an
endmill, used to drill/plunge a hole) have no cone to compensate for, so this
is a normal case, not an error -- 0.0 is the correct length, not a fallback.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Op/Util.py:748`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`Path.Op.Util.__title__`, `Path.Op.Util.__author__`, `Path.Op.Util.__url__`, `Path.Op.Util.__doc__`, `Path.Op.Util._orientEdges`, `Path.Op.Util._isWireClockwise`, `Path.Op.Util._ROTARY_AXES`, `Path.Op.Util._stripRotaryAxes`. These are source internals unless an explicit export establishes otherwise.

