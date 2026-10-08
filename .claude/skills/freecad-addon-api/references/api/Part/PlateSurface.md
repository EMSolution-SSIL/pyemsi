# `Part.PlateSurface`

[Module](index.md)

```python
class PlateSurface(GeometrySurface):
```

Represents a plate surface in FreeCAD. Plate surfaces can be defined by specifying points or curves as constraints, and they can also be approximated to B-spline surfaces using the makeApprox method. This class is commonly used in CAD modeling for creating surfaces that represent flat or curved plates, such as sheet metal components or structural elements.

Evidence: public stub `Part/__init__.pyi` line 3208. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.PlateSurface.makeApprox`

```python
def makeApprox(self, *, Tol3d: float=0, MaxSegments: int=0, MaxDegree: int=0, MaxDistance: float=0, CritOrder: int=0, Continuity: str='', EnlargeCoeff: float=0) -> BSplineSurface:
```

Approximate the plate surface to a B-Spline surface

Evidence: public stub `Part/__init__.pyi` line(s) 3213.

