# `Part.ShapeFix.Face`

[Module](index.md)

```python
class Face(Root):
```

Class for fixing operations on faces

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 249. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.Face.FixWireMode`

```python
FixWireMode: bool = ...
```

Mode for applying fixes of ShapeFix_Wire

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 256.

## `Part.ShapeFix.Face.FixOrientationMode`

```python
FixOrientationMode: bool = ...
```


    Mode for applying fixes of orientation
    If True, wires oriented to border limited square
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 258.

## `Part.ShapeFix.Face.FixAddNaturalBoundMode`

```python
FixAddNaturalBoundMode: bool = ...
```


    If true, natural boundary is added on faces that miss them.
    Default is False for faces with single wire (they are
    handled by FixOrientation in that case) and True for others.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 260.

## `Part.ShapeFix.Face.FixMissingSeamMode`

```python
FixMissingSeamMode: bool = ...
```

If True, tries to insert seam if missing

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 262.

## `Part.ShapeFix.Face.FixSmallAreaWireMode`

```python
FixSmallAreaWireMode: bool = ...
```

If True, drops small wires

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 264.

## `Part.ShapeFix.Face.RemoveSmallAreaFaceMode`

```python
RemoveSmallAreaFaceMode: bool = ...
```

If True, drops small wires

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 266.

## `Part.ShapeFix.Face.FixIntersectingWiresMode`

```python
FixIntersectingWiresMode: bool = ...
```

Mode for applying fixes of intersecting wires

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 268.

## `Part.ShapeFix.Face.FixLoopWiresMode`

```python
FixLoopWiresMode: bool = ...
```

Mode for applying fixes of loop wires

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 270.

## `Part.ShapeFix.Face.FixSplitFaceMode`

```python
FixSplitFaceMode: bool = ...
```

Mode for applying fixes of split face

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 272.

## `Part.ShapeFix.Face.AutoCorrectPrecisionMode`

```python
AutoCorrectPrecisionMode: bool = ...
```

Mode for applying auto-corrected precision

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 274.

## `Part.ShapeFix.Face.FixPeriodicDegeneratedMode`

```python
FixPeriodicDegeneratedMode: bool = ...
```

Mode for applying periodic degeneration

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 276.

## `Part.ShapeFix.Face.init`

```python
@overload
def init(self, face: TopoShapeFace, /) -> None:

@overload
def init(self, surface: GeometrySurface, prec: float, fwd: bool=True, /) -> None:

def init(self, *args) -> None:
```

Initializes by face

Evidence: public stub `Part/ShapeFix.pyi` line(s) 280, 284, 287.

## `Part.ShapeFix.Face.fixWireTool`

```python
def fixWireTool(self):
```

Returns tool for fixing wires

Evidence: public stub `Part/ShapeFix.pyi` line(s) 293.

## `Part.ShapeFix.Face.clearModes`

```python
def clearModes(self) -> None:
```

Sets all modes to default

Evidence: public stub `Part/ShapeFix.pyi` line(s) 299.

## `Part.ShapeFix.Face.add`

```python
def add(self, wire: TopoShapeWire, /) -> None:
```

Add a wire to current face using BRep_Builder.
Wire is added without taking into account orientation of face
(as if face were FORWARD)

Evidence: public stub `Part/ShapeFix.pyi` line(s) 305.

## `Part.ShapeFix.Face.fixOrientation`

```python
def fixOrientation(self) -> bool:
```

Fixes orientation of wires on the face
It tries to make all wires lie outside all others (according
to orientation) by reversing orientation of some of them.
If face lying on sphere or torus has single wire and
AddNaturalBoundMode is True, that wire is not reversed in
any case (supposing that natural bound will be added).
Returns True if wires were reversed

Evidence: public stub `Part/ShapeFix.pyi` line(s) 313.

## `Part.ShapeFix.Face.fixAddNaturalBound`

```python
def fixAddNaturalBound(self) -> bool:
```

Adds natural boundary on face if it is missing.
Two cases are supported:
 - face has no wires
 - face lies on geometrically double-closed surface
(sphere or torus) and none of wires is left-oriented
Returns True if natural boundary was added

Evidence: public stub `Part/ShapeFix.pyi` line(s) 325.

## `Part.ShapeFix.Face.fixMissingSeam`

```python
def fixMissingSeam(self) -> bool:
```

Detects and fixes the special case when face on a closed
surface is given by two wires closed in 3d but with gap in 2d.
In that case it creates a new wire from the two, and adds a
missing seam edge
Returns True if missing seam was added

Evidence: public stub `Part/ShapeFix.pyi` line(s) 336.

## `Part.ShapeFix.Face.fixSmallAreaWire`

```python
def fixSmallAreaWire(self, remove_small: bool, /) -> bool:
```

Detects wires with small area (that is less than
100*Precision.PConfusion(). Removes these wires if they are internal.
Returns True if at least one small wire removed, False nothing is done.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 346.

## `Part.ShapeFix.Face.fixLoopWire`

```python
def fixLoopWire(self) -> tuple[bool, list]:
```

Detects if wire has a loop and fixes this situation by splitting on the few parts.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 354.

## `Part.ShapeFix.Face.fixIntersectingWires`

```python
def fixIntersectingWires(self) -> bool:
```

Detects and fixes the special case when face has more than one wire
and this wires have intersection point

Evidence: public stub `Part/ShapeFix.pyi` line(s) 360.

## `Part.ShapeFix.Face.fixWiresTwoCoincidentEdges`

```python
def fixWiresTwoCoincidentEdges(self) -> bool:
```

If wire contains two coincidence edges it must be removed

Evidence: public stub `Part/ShapeFix.pyi` line(s) 367.

## `Part.ShapeFix.Face.fixPeriodicDegenerated`

```python
def fixPeriodicDegenerated(self) -> bool:
```

Fixes topology for a specific case when face is composed
by a single wire belting a periodic surface. In that case
a degenerated edge is reconstructed in the degenerated pole
of the surface. Initial wire gets consistent orientation.
Must be used in couple and before FixMissingSeam routine

Evidence: public stub `Part/ShapeFix.pyi` line(s) 373.

## `Part.ShapeFix.Face.perform`

```python
def perform(self) -> bool:
```

Iterates on subshapes and performs fixes

Evidence: public stub `Part/ShapeFix.pyi` line(s) 383.

## `Part.ShapeFix.Face.face`

```python
def face(self) -> TopoShapeFace:
```

Returns a face which corresponds to the current state

Evidence: public stub `Part/ShapeFix.pyi` line(s) 389.

## `Part.ShapeFix.Face.result`

```python
def result(self) -> Union[TopoShapeFace, TopoShapeShell]:
```

Returns resulting shape (Face or Shell if split)
To be used instead of face() if FixMissingSeam involved

Evidence: public stub `Part/ShapeFix.pyi` line(s) 395.

