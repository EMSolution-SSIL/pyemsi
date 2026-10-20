"""Outer shapes of Air Regions. No GUI code here."""

import FreeCAD as App
import Part

from . import geometry

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
            raise ValueError(f"Air Region {air.Label}: choose a body for the Custom shape")
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
        raise ValueError(f"Air Region {air.Label}: the outer radius must be larger than the inner radius")
    if plane == "ZX":  # half ring in the XY plane, x >= 0, stood up into y = 0
        face = _bottom_face(_ring_sector(inner, outer, -90, 180, 0, 1), 0)
        face.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)
        face.translate(App.Vector(0, 0, air.Center.z))
        return face
    start, sweep = air.StartAngle.Value, air.EndAngle.Value - air.StartAngle.Value
    if not 0 < sweep <= 360:
        raise ValueError(f"Air Region {air.Label}: the end angle must be 0 to 360 degrees above the start angle")
    if plane == "3D":
        return _ring_sector(inner, outer, start, sweep, air.ZMin.Value, air.Height.Value)
    return _bottom_face(_ring_sector(inner, outer, start, sweep, 0, 1), 0)


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
