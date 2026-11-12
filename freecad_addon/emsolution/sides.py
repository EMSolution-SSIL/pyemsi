"""Which side of a Sliding Interface a shape is on, and so whether it moves. No GUI code."""

import FreeCAD as App
import Part

from . import airshapes, objects

_EPS = 1e-6


def _half_space(shape, iface, plane):
    """The Inside / Above / Positive half-space of iface, as a shape that covers shape."""
    box = shape.BoundBox
    far = 4 * max(box.DiagonalLength, abs(box.XMin), abs(box.XMax), abs(box.YMin), abs(box.YMax), 1.0) + 1000.0
    kind = iface.Kind
    if kind == "Rotational":
        radius = iface.Radius.Value
        if plane == "3D":
            return Part.makeCylinder(radius, 2 * far, App.Vector(0, 0, -far))
        return Part.Face(Part.Wire(Part.makeCircle(radius)))
    position = iface.Position.Value
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
    inside = airshapes._measure(shape.common(_half_space(shape, iface, plane)))
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
