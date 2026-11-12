"""Which side of a Sliding Interface a shape is on, and so whether it moves. No GUI code."""

import FreeCAD as App
import Part

from . import airshapes, geometry, objects

_EPS = 1e-6


def _half_space(shape, iface, plane):
    """The Inside / Above / Positive half-space of iface, as a shape that covers shape."""
    box = shape.BoundBox
    kind = iface.Kind
    position = iface.Position.Value if kind != "Rotational" else 0.0
    reach = max(abs(c) for c in (box.XMin, box.XMax, box.YMin, box.YMax, box.ZMin, box.ZMax))
    far = 2 * max(reach, abs(position), box.DiagonalLength, 1.0) + 1000.0  # past the shape from the plane
    if kind == "Rotational":
        radius = iface.Radius.Value
        if plane == "3D":
            return Part.makeCylinder(radius, 2 * far, App.Vector(0, 0, -far))
        return Part.Face(Part.Wire(Part.makeCircle(radius)))
    if kind == "Axial gap":
        return Part.makeBox(2 * far, 2 * far, far, App.Vector(-far, -far, position))
    axis = objects.AXES.index(iface.NormalAxis)
    corner, size = [-far] * 3, [2 * far] * 3
    corner[axis], size[axis] = position, far
    if plane != "3D":
        corner[2] = 0.0
        return Part.makePlane(size[0] if axis != 0 else far, size[1] if axis != 1 else far, App.Vector(*corner))
    return Part.makeBox(*size, App.Vector(*corner))


def side_of(shape, iface, plane):
    """ "moving", "fixed", or None when shape is on both sides of iface (all but 1e-6 of it must be on one side)."""
    whole = airshapes._measure(shape)
    half = _half_space(shape, iface, plane)
    # piece by piece: one common of a compound of touching pieces (a group's drawing) can lose some of them
    inside = sum(airshapes._measure(p.common(half)) for p in (shape.Solids or shape.Faces))
    if inside >= (1 - _EPS) * whole:
        positive = True
    elif inside <= _EPS * whole:
        positive = False
    else:
        return None
    return "moving" if positive == (iface.MovingSide == objects.MOVING_SIDES[iface.Kind][0]) else "fixed"


def piece_sides(pieces, interfaces, surfaces, plane):
    """([side of each air piece], [(message, object)]). The interfaces whose surface touches a piece vote with
    side_of; a piece they disagree about, or none borders, is None (the disagreement is an error)."""
    found, errors = [], []
    for piece in pieces:
        votes = [
            (iface, side_of(piece, iface, plane))
            for iface, surface in zip(interfaces, surfaces)
            if not surface.isNull() and piece.distToShape(surface)[0] <= airshapes.TOL
        ]
        votes = [(i, v) for i, v in votes if v is not None]
        sides = {v for _, v in votes}
        if len(sides) == 1:
            found.append(sides.pop())
            continue
        found.append(None)
        if len(sides) > 1:
            a = votes[0][0]
            b = next(i for i, v in votes if v != votes[0][1])
            errors.append(
                (
                    f"Sliding Interfaces {a.Label} and {b.Label} disagree about the side of the air between them:"
                    " change the moving side of one.",
                    a,
                )
            )
    return found, errors


def _pieces(study):
    """(air pieces, their sides) of a sliding Study without Symmetric Groups, or None when they cannot be worked out:
    no Air Region or interface, or one that does not cut the air (validation says why)."""
    airs, interfaces = objects.air_regions(study), objects.sliding_interfaces(study)
    if not airs or not interfaces:
        return None
    plane = airshapes.study_plane(study)
    try:
        air = airshapes.air_shape(airs[0], plane)
        surfaces = [airshapes.slide_surface(i, air, plane) for i in interfaces]
    except (ValueError, Part.OCCError):
        return None
    if not all(s.Edges for s in surfaces):  # an interface that misses the air
        return None
    pieces = airshapes.cells(air, surfaces)
    return pieces, piece_sides(pieces, interfaces, surfaces, plane)[0]


def group_side(study, item):
    """ "moving" or "fixed": the side of the Study's one Sliding Interface that Symmetric Group item's drawing is on;
    "fixed" without Sliding motion or without an interface. None when the drawing is on both sides, or has none
    (validation says why)."""
    if study.Movement != "Sliding motion":
        return "fixed"
    interfaces = objects.sliding_interfaces(study)
    if not interfaces:
        return "fixed"
    if item.Shape.isNull() or not item.Shape.Faces:  # rules that cannot be read, or too many copies to draw
        return None
    return side_of(item.Shape, interfaces[0], airshapes.study_plane(study))


def moving(study):
    """Names of the Study's free bodies on the moving side; empty without Sliding motion or when it cannot be worked
    out (validation says why). Without Symmetric Groups a body moves with the air piece it is in; with them, by its
    side of the one Sliding Interface."""
    if study.Movement != "Sliding motion":
        return set()
    bodies = geometry.study_geometry(study)[0]
    if objects.is_grouped(study):
        interfaces = objects.sliding_interfaces(study)
        if not interfaces:
            return set()
        plane = "3D" if study.Dimension == "3D" else airshapes.study_plane(study)
        return {b.Name for b in bodies if side_of(geometry.global_shape(b), interfaces[0], plane) == "moving"}
    found = _pieces(study)
    if found is None:
        return set()
    pieces, piece_side = found
    out = set()
    for body in bodies:
        k = airshapes.cell_of(geometry.global_shape(body), pieces)
        if k is not None and piece_side[k] == "moving":
            out.add(body.Name)
    return out


def moving_pieces(study):
    """Indices of the moving pieces of airshapes.cells(...) in a sliding Study without Symmetric Groups."""
    found = _pieces(study)
    return [] if found is None else [k for k, side in enumerate(found[1]) if side == "moving"]
