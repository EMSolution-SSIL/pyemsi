"""Outer shapes of Air Regions, slide surfaces of Sliding Interfaces and the air cells between them. No GUI code."""

import math

import FreeCAD as App
import Part
from BOPTools import SplitAPI

from . import geometry, objects

TOL = 1e-6


def study_plane(study):
    """ "3D" for a 3D Study; for 2D the plane of the first main-geometry face ("XY" or "ZX"), "XY" if there is none."""
    if study.Dimension == "3D":
        return "3D"
    for body in geometry.region(study, "Main")[0]:
        for face in geometry.global_shape(body).Faces:
            found = geometry.plane_of(face)
            if found:
                return found
    return "XY"


def air_shape(air, plane):
    """The Air Region's outer shape: a solid for "3D", else a face in z = 0 ("XY") or y = 0 ("ZX")."""
    if air.AirShape == "Custom":
        if air.Source is None:
            raise ValueError(f"Air Region {objects.display_name(air)}: choose a body for the Custom shape")
        shape = geometry.global_shape(air.Source)
    elif air.AirShape == "Sector":
        shape = _sector(air, plane)
    else:
        shape = _box(air, plane)
    return _baked(shape)


def _baked(shape):
    """The shape with its placement moved into the geometry: a Shape property applies the object's Placement again."""
    shape = shape.copy()
    shape.transformShape(shape.Placement.toMatrix(), True)
    shape.Placement = App.Placement()
    return shape


def _rectangle(plane, cx, cy, cz, length, width):
    """A face of length (x) by width (y in XY, z in ZX) centred on the given point."""
    dx, d2 = length / 2, width / 2
    if plane == "ZX":
        corners = [(cx - dx, 0, cz - d2), (cx + dx, 0, cz - d2), (cx + dx, 0, cz + d2), (cx - dx, 0, cz + d2)]
    else:
        corners = [(cx - dx, cy - d2, 0), (cx + dx, cy - d2, 0), (cx + dx, cy + d2, 0), (cx - dx, cy + d2, 0)]
    points = [App.Vector(*c) for c in corners]
    return Part.Face(Part.makePolygon(points + points[:1]))


def _box(air, plane):
    c, length, width = air.Center, air.Length.Value, air.Width.Value
    if plane == "3D":
        return Part.makeBox(length, width, air.Height.Value, c - App.Vector(length, width, air.Height.Value) * 0.5)
    return _rectangle(plane, c.x, c.y, c.z, length, width)


def _ring_sector(inner, outer, start, sweep, z0, height):
    """Solid ring sector about the Z axis, from angle start over sweep degrees."""
    solid = Part.makeCylinder(outer, height, App.Vector(0, 0, z0), App.Vector(0, 0, 1), sweep)
    if inner > 0:
        hole = Part.makeCylinder(inner, height + 2, App.Vector(0, 0, z0 - 1), App.Vector(0, 0, 1), sweep)
        solid = solid.cut(hole)
    solid.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), start)
    return solid


def _bottom_face(solid, z):
    return next(f for f in solid.Faces if abs(f.BoundBox.ZMin - z) < TOL and abs(f.BoundBox.ZMax - z) < TOL)


def _sector(air, plane):
    inner, outer = air.InnerRadius.Value, air.OuterRadius.Value
    if outer <= inner:
        raise ValueError(
            f"Air Region {objects.display_name(air)}: the outer radius must be larger than the inner radius."
        )
    if plane == "ZX":  # half ring in the XY plane, x >= 0, stood up into y = 0
        face = _bottom_face(_ring_sector(inner, outer, -90, 180, 0, 1), 0)
        face.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)
        face.translate(App.Vector(0, 0, air.Center.z))
        return face
    start, sweep = air.StartAngle.Value, air.EndAngle.Value - air.StartAngle.Value
    if not 0 < sweep <= 360:
        raise ValueError(
            f"Air Region {objects.display_name(air)}: the end angle must be larger than the start angle (at most 360° more)."
        )
    if plane == "3D":
        return _ring_sector(inner, outer, start, sweep, air.ZMin.Value, air.Height.Value)
    return _bottom_face(_ring_sector(inner, outer, start, sweep, 0, 1), 0)


def _points(shape):
    """Points on the shape that reach its farthest from an axis: its vertices and tessellation nodes."""
    box = shape.BoundBox
    points = [v.Point for v in shape.Vertexes]
    if shape.Faces:
        points += shape.tessellate(1e-3 * box.DiagonalLength)[0]
    return points


def radial_extent(shapes, center_z=None):
    """(smallest, largest) distance of the shapes from the Z axis; for the ZX half disc (center_z given) from the
    point (0, 0, center_z)."""
    low, high = math.inf, 0.0
    if center_z is None:
        for shape in shapes:
            far = 2 * (shape.BoundBox.DiagonalLength + shape.BoundBox.Center.Length) + 1
            axis = Part.makeLine(App.Vector(0, 0, -far), App.Vector(0, 0, far))
            low = min(low, shape.distToShape(axis)[0])
            high = max(high, max(math.hypot(p.x, p.y) for p in _points(shape)))
    else:
        centre = Part.Vertex(0, 0, center_z)
        for shape in shapes:
            low = min(low, shape.distToShape(centre)[0])
            high = max(high, max(math.hypot(p.x, p.z - center_z) for p in _points(shape)))
    return low, high


def _pad(air, side, size):
    """Padding of a side in mm: its percentage of size plus its length."""
    return getattr(air, f"Pad{side}Percent") / 100 * size + getattr(air, f"Pad{side}").Value


def _span(air, axis, low, high, fixed_low=None):
    """(start, length) of the bodies' extent low..high along axis ("X", "Y" or "Z") grown by the padding on both
    sides; the start is fixed_low when the low side does not move."""
    size = high - low
    start = low - _pad(air, f"{axis}Minus", size) if fixed_low is None else fixed_low
    end = high + _pad(air, f"{axis}Plus", size)
    if end - start <= 0:
        raise ValueError(
            f"Air Region {objects.display_name(air)}: padding gives no size along {axis}; add a length padding."
        )
    return start, end - start


def padded_size(air, bodies, plane):
    """The size properties of a Padding mode Air Region, from the global shapes of bodies: {name: value}, lengths in
    mm and Center a Vector. The Sector angles and the centre z of the ZX half disc stay as they are."""
    name = objects.display_name(air)
    if air.AirShape == "Custom":
        raise ValueError(f"Air Region {name}: Padding is not available for a Custom shape.")
    if not bodies:
        raise ValueError(f"Air Region {name}: Padding needs bodies in the main or moving geometry.")
    shapes = [geometry.global_shape(b) for b in bodies]
    box = App.BoundBox()
    for shape in shapes:
        box.add(shape.BoundBox)
    if air.AirShape == "Sector":
        return _padded_sector(air, shapes, box, plane)
    if plane == "ZX":  # the left edge stays on the axis, x = 0
        x0, length = _span(air, "X", box.XMin, box.XMax, 0.0)
        z0, width = _span(air, "Z", box.ZMin, box.ZMax)
        return {"Center": App.Vector(x0 + length / 2, 0, z0 + width / 2), "Length": length, "Width": width}
    x0, length = _span(air, "X", box.XMin, box.XMax)
    y0, width = _span(air, "Y", box.YMin, box.YMax)
    if plane == "XY":
        return {"Center": App.Vector(x0 + length / 2, y0 + width / 2, 0), "Length": length, "Width": width}
    z0, height = _span(air, "Z", box.ZMin, box.ZMax)
    center = App.Vector(x0 + length / 2, y0 + width / 2, z0 + height / 2)
    return {"Center": center, "Length": length, "Width": width, "Height": height}


def _padded_sector(air, shapes, box, plane):
    if plane == "ZX":
        low, high = radial_extent(shapes, air.Center.z)
    else:
        low, high = radial_extent(shapes)
    outer = high + _pad(air, "Outer", high)
    if outer <= 0:
        raise ValueError(
            f"Air Region {objects.display_name(air)}: padding gives no size along the radius; add a length padding."
        )
    size = {"OuterRadius": outer}
    if plane == "ZX":
        size["InnerRadius"] = 0.0  # a half disc
    else:
        size["InnerRadius"] = max(low - _pad(air, "Inner", high), 0.0) if air.InnerFromBodies else 0.0
    if plane == "3D":
        z0, height = _span(air, "Z", box.ZMin, box.ZMax)
        size.update({"ZMin": z0, "Height": height})
    return size


def fit_box(bodies, padding, plane):
    """(centre, length, width, height) of the bodies' global bound box, grown by padding % of its size on each side.

    Length is along x; width is along y ("3D", "XY") or z ("ZX"); height is along z and 0 in 2D.
    """
    box = App.BoundBox()
    for body in bodies:
        box.add(geometry.global_shape(body).BoundBox)
    grow = 1 + padding / 100 * 2
    length, depth, height = box.XLength * grow, box.YLength * grow, box.ZLength * grow
    if plane == "ZX":
        return App.Vector(box.Center.x, 0, box.Center.z), length, height, 0.0
    if plane == "XY":
        return App.Vector(box.Center.x, box.Center.y, 0), length, depth, 0.0
    return App.Vector(box.Center), length, depth, height


def fit_study(study, padding):
    """fit_box of all the Study's bodies (main and moving geometry, never the air), or None if it has none."""
    bodies = objects.study_bodies(study)
    return fit_box(bodies, padding, study_plane(study)) if bodies else None


def outside(body_shape, air_shape, plane):
    """Volume ("3D") or area (2D) of the part of body_shape that lies outside air_shape."""
    rest = body_shape.cut(air_shape)
    return rest.Volume if plane == "3D" else rest.Area


def _start(iface):
    """Start angle of the motion in degrees: the StartAngle of a Sector Air Region, else 0."""
    air = objects.air_of(iface)
    return air.StartAngle.Value if air is not None and air.AirShape == "Sector" else 0.0


def _far(shape):
    """A length from the origin that reaches past shape (1 for an empty shape)."""
    box = shape.BoundBox
    return 2 * (box.DiagonalLength + box.Center.Length) + 1 if box.isValid() else 1.0


def _at(values):
    """A Vector from {"X": x, "Y": y, "Z": z}; missing axes are 0."""
    return App.Vector(*(values.get(a, 0.0) for a in objects.AXES))


def _linear_tool(iface, far, plane):
    """A large plane (3D) or line (2D) where the NormalAxis coordinate is Position."""
    normal, pos = iface.NormalAxis, iface.Position.Value
    name = f"Sliding Interface {objects.display_name(iface)}: "
    if iface.MotionAxis == normal:
        raise ValueError(name + "the motion axis must differ from the normal axis.")
    if plane == "3D":
        a, b = [x for x in objects.AXES if x != normal]
        corners = [_at({normal: pos, a: sa * far, b: sb * far}) for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        return Part.Face(Part.makePolygon(corners + corners[:1]))
    if normal == "Z":
        raise ValueError(name + "in a 2D Study the normal axis is X or Y.")
    along = "Y" if normal == "X" else "X"
    return Part.makeLine(_at({normal: pos, along: -far}), _at({normal: pos, along: far}))


def _round_tool(iface, far, plane, start, sweep):
    """The part from start over sweep degrees about Z of a circle (2D), cylinder face or large disc (Axial gap)."""
    r = iface.Radius.Value
    if plane != "3D":
        return Part.makeCircle(r, App.Vector(0, 0, 0), App.Vector(0, 0, 1), start, start + sweep)
    if iface.Kind == "Axial gap":
        z = iface.Position.Value
        return _bottom_face(_ring_sector(0, far, start, sweep, z, 1), z)
    solid = _ring_sector(0, r, start, sweep, -far, 2 * far)
    return next(f for f in solid.Faces if isinstance(f.Surface, Part.Cylinder))


def _pieces(shape, plane):
    return shape.Faces if plane == "3D" else shape.Edges


def _goes_round(iface, pieces):
    """True if the pieces of a rotational slide surface go all the way round the Z axis."""
    if iface.Kind == "Axial gap":  # a disc or ring: the axis lies inside its outer boundary
        p = Part.Vertex(0, 0, iface.Position.Value)
        return any(Part.Face(f.OuterWire).distToShape(p)[0] < TOL < f.OuterWire.distToShape(p)[0] for f in pieces)
    spans = []  # angle ranges of the circle arcs or cylinder faces, folded into [0, 2 pi]
    for piece in pieces:
        lo, hi = piece.ParameterRange[:2]
        lo, hi = lo % math.tau, lo % math.tau + hi - lo
        spans += [(lo, min(hi, math.tau)), (0.0, max(hi - math.tau, 0.0))]
    covered = end = 0.0
    for lo, hi in sorted(spans):
        covered += max(hi - max(lo, end), 0.0)
        end = max(end, hi)
    return covered > math.tau - TOL


def slide_surface(iface, air_shape, plane):
    """The slide curves (2D) or faces (3D) of a Sliding Interface inside air_shape, as a compound; empty if it misses
    the air. One that goes all the way round is built in two halves, split at the start angle and 180° from it.
    """
    if plane == "ZX":
        raise ValueError(f"Sliding Interface {objects.display_name(iface)}: no sliding motion in a ZX Study.")
    if iface.Kind == "Axial gap" and plane != "3D":
        raise ValueError(f"Sliding Interface {objects.display_name(iface)}: an Axial gap needs a 3D Study.")
    far = _far(air_shape)
    if iface.Kind == "Linear":
        pieces = _pieces(_linear_tool(iface, far, plane).common(air_shape), plane)
    else:
        start = _start(iface)
        pieces = _pieces(_round_tool(iface, far, plane, start, 360).common(air_shape), plane)
        if _goes_round(iface, pieces):
            halves = [_round_tool(iface, far, plane, a, 180).common(air_shape) for a in (start, start + 180)]
            pieces = [p for half in halves for p in _pieces(half, plane)]
    return _baked(Part.makeCompound(pieces))


def full_turn(iface, air_shape, plane):
    """True if a Rotational or Axial gap interface goes all the way round the Z axis inside air_shape (slide_surface
    then builds it in two halves)."""
    if iface.Kind == "Linear":
        return False
    whole = _round_tool(iface, _far(air_shape), plane, _start(iface), 360).common(air_shape)
    return _goes_round(iface, _pieces(whole, plane))


def slide_marker(iface, surface, plane):
    """Where the motion starts on surface: the slide point (2D, a Vertex) or slide edge (3D, the generatrix Edge).

    Rotational and Axial gap: at the start angle. Linear: at the smallest motion-axis coordinate.
    """
    far = _far(surface)
    if iface.Kind == "Linear":
        axis = objects.AXES.index(iface.MotionAxis)
        if plane != "3D":
            return min(surface.Vertexes, key=lambda v: v.Point[axis])
        box = surface.BoundBox
        at, pos = (box.XMin, box.YMin, box.ZMin)[axis], iface.Position.Value
        across = next(a for a in objects.AXES if a not in (iface.NormalAxis, iface.MotionAxis))
        ends = [_at({iface.MotionAxis: at, iface.NormalAxis: pos, across: s * far}) for s in (-1, 1)]
    else:
        a = math.radians(_start(iface))
        out = App.Vector(math.cos(a), math.sin(a), 0)
        if plane != "3D":
            return Part.Vertex(out * iface.Radius.Value)
        if iface.Kind == "Axial gap":
            base = App.Vector(0, 0, iface.Position.Value)
            ends = [base, base + out * far]
        else:
            ends = [out * iface.Radius.Value + App.Vector(0, 0, z) for z in (-far, far)]
    edges = Part.makeLine(*ends).common(surface).Edges
    if not edges:
        raise ValueError(
            f"Sliding Interface {objects.display_name(iface)}: the slide edge does not lie on its surface."
        )
    return edges[0] if len(edges) == 1 else Part.makeCompound(edges)


def cells(air_shape, surfaces):
    """The pieces the slide surfaces cut air_shape into: solids for a 3D air, faces for a 2D one."""
    tools = [p for s in surfaces for p in (s.Faces or s.Edges)]  # slice does not split by a compound tool
    if not tools:
        return [air_shape]
    split = SplitAPI.slice(air_shape, tools, "Split")
    return list(split.Solids if air_shape.Solids else split.Faces)


def _measure(shape):
    return shape.Volume if shape.Solids else shape.Area


def cell_of(body_shape, cells):
    """Index of the cell that holds body_shape (all but 1e-6 of its volume or area); None if it crosses a surface."""
    whole = _measure(body_shape)
    for k, cell in enumerate(cells):
        if _measure(body_shape.common(cell)) >= (1 - 1e-6) * whole:
            return k
    return None


def period(study):
    """The motion period the Air Region gives, or None.

    A Sector under 360°: rotation about Z by its angle. A Box with a Linear interface: translation by the Box size
    along the motion axis. "start" is where the period begins: the start angle, or the Box minimum on that axis.
    """
    airs = objects.air_regions(study)
    if not airs:
        return None
    air = airs[0]
    if air.AirShape == "Sector":
        start, angle = air.StartAngle.Value, air.EndAngle.Value - air.StartAngle.Value
        return {"kind": "rotation", "angle": angle, "start": start} if angle < 360 - TOL else None
    linear = [i for i in objects.sliding_interfaces(study) if i.Kind == "Linear"]
    if air.AirShape != "Box" or not linear:
        return None
    axis = objects.AXES.index(linear[0].MotionAxis)
    length = (air.Length, air.Width, air.Height)[axis].Value
    vector = [0.0, 0.0, 0.0]
    vector[axis] = length
    return {"kind": "translation", "vector": vector, "start": air.Center[axis] - length / 2}
