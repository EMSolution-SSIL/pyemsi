"""Recognising a body as a profile face swept along a path (Swept Body). No GUI or mesh generation here.

Stage 2 recognises straight sweeps (an end face moved by a translation onto the other end face, every side face
running along the translation), revolved ones (an end face turned about a line onto the other end face, every other
face running around that line) and closed rings (no end faces, every face running around one line; the profile is the
body cut by a half-plane through the line)."""

import math
from collections import namedtuple

import FreeCAD as App
import Part

from . import objects

# A screw motion: angle (degrees) about the axis through origin, and advance (mm) along it. A straight piece has angle
# 0 and advance its length; origin is then the profile's centre of mass. A revolved piece has advance 0, origin the
# axis point nearest the profile's centre of mass, and its axis turned so that a positive angle runs from the start
# face to the end face.
Piece = namedtuple("Piece", "origin axis angle advance")
# profile, end: face names of the solid (end is None when closed, both None for a closed ring); pieces: a list of
# Piece; face: the profile as a Part.Face in the solid's coordinates (the start face, or a closed ring's cut).
Sweep = namedtuple("Sweep", "profile end pieces closed face")

NO_END = "it has no flat end face that matches another end face moved"
NOT_AN_END = "the start face {face} is not a flat end face of it"
NOT_STRAIGHT = "only straight and revolved sweeps are made so far"
SIDE_FACE = "a side face does not run straight from one end to the other"
VOLUME = "its volume is not the start face swept to the end face"
NO_AXIS = "its faces do not all turn about one axis"


def _planar(face):
    return isinstance(face.Surface, Part.Plane)


def _normal(face):
    """The outward normal of a planar face of a solid."""
    u0, u1, v0, v1 = face.ParameterRange
    return face.normalAt((u0 + u1) / 2, (v0 + v1) / 2)


def _runs_along(face, d, tol):
    """True if face's normal is perpendicular to the unit vector d at 5 x 5 sample points."""
    u0, u1, v0, v1 = face.ParameterRange
    for i in range(5):
        for j in range(5):
            n = face.normalAt(u0 + (u1 - u0) * (i + 0.5) / 5, v0 + (v1 - v0) * (j + 0.5) / 5)
            if abs(n.dot(d)) >= tol:
                return False
    return True


def _turns_about(face, point, axis, tol):
    """True if face's normal is perpendicular to the motion of a turn about the line (point, axis) at 5 x 5 sample
    points: the face runs around that line."""
    u0, u1, v0, v1 = face.ParameterRange
    for i in range(5):
        for j in range(5):
            u, v = u0 + (u1 - u0) * (i + 0.5) / 5, v0 + (v1 - v0) * (j + 0.5) / 5
            motion = axis.cross(face.valueAt(u, v) - point)
            if motion.Length > tol and abs(face.normalAt(u, v).dot(motion)) >= tol * motion.Length:
                return False
    return True


def _axis_line(face):
    """(point, unit direction) of the axis of face's surface of revolution, or None when it is not one."""
    s = face.Surface
    if isinstance(s, (Part.Cylinder, Part.Cone, Part.Toroid, Part.Sphere)):
        return App.Vector(s.Center), App.Vector(s.Axis).normalize()
    if isinstance(s, Part.SurfaceOfRevolution):
        return App.Vector(s.Location), App.Vector(s.Direction).normalize()
    return None


def _first_axis(faces):
    """The axis of the first face that is not planar (a sphere's only when no other face has one: any line through
    its centre is an axis), or None when there is none or that face is not a surface of revolution."""
    curved = sorted((f for f in faces if not _planar(f)), key=lambda f: isinstance(f.Surface, Part.Sphere))
    return _axis_line(curved[0]) if curved else None


def _nearest(point, axis, c):
    """The point of the line (point, axis) nearest c."""
    return point + axis * axis.dot(c - point)


def _touches(face, point, axis, length, length_tol):
    """True if face reaches the line (point, axis), length either side of point: a profile there would sweep into a
    degenerate centre."""
    return face.distToShape(Part.makeLine(point - axis * length, point + axis * length))[0] <= length_tol


def _pappus(solid, face, rc, theta, tol):
    """True if solid's volume is face swept by theta radians at its centre of mass' distance rc from the axis."""
    return abs(solid.Volume - face.Area * rc * theta) <= tol * solid.Volume


def _rotation(solid, i, j, na, nb, tol, length_tol):
    """(origin, axis, angle) of a turn that maps face i of solid onto face j, every other face running around that
    line: origin is the line's point nearest face i's centre, and the axis is turned so that the positive angle runs
    through the body. None when there is no such turn."""
    faces = solid.Faces
    a, b = faces[i], faces[j]
    others = [f for k, f in enumerate(faces) if k not in (i, j)]
    c = a.CenterOfMass
    axis = na.cross(-nb)
    if axis.Length >= tol:
        axis.normalize()
        angle = math.degrees(math.atan2(na.cross(-nb).Length, na.dot(-nb)))
        # A point on the line: on both planes, and on the plane through a's centre normal to the line.
        da, db, du = na.dot(c), nb.dot(b.CenterOfMass), axis.dot(c)
        point = (nb.cross(axis) * da + axis.cross(na) * db + na.cross(nb) * du) * (1.0 / na.dot(nb.cross(axis)))
    else:
        # Both faces in one plane (half way round): the line is the axis of the other faces, lying in that plane.
        line = _first_axis(others)
        if line is None or na.dot(nb) < 0 or abs(na.dot(b.CenterOfMass - c)) > length_tol:
            return None
        point, axis = line
        if abs(axis.dot(na)) > tol or abs(na.dot(point - c)) > length_tol:
            return None
        point, angle = _nearest(point, axis, c), 180.0
    moved = a.copy()
    moved.rotate(point, axis, angle)
    if not objects.coincident_faces(moved, b, length_tol):
        return None
    if not all(_turns_about(f, point, axis, tol) for f in others):
        return None
    if axis.cross(c - point).dot(na) > 0:  # the short turn leaves the body through a: it runs the long way round
        axis, angle = -axis, 360.0 - angle
    return point, axis, angle


def _screw_maps(a, b, na, nb, length_tol):
    """True if face a, turned into face b's plane and moved onto b's centre, lies on b: the ends of a helix (or of a
    path of several pieces)."""
    moved = a.copy()
    axis = na.cross(-nb)
    if axis.Length > 1e-12:
        moved.rotate(a.CenterOfMass, axis, math.degrees(math.atan2(axis.Length, na.dot(-nb))))
    moved.translate(b.CenterOfMass - a.CenterOfMass)
    return objects.coincident_faces(moved, b, length_tol)


def _meridian(solid, point, axis, length_tol):
    """The unit direction, normal to axis, of a half-plane bounded by the line (point, axis) that holds an edge of
    solid (a seam, or the joint of two half rings), or None when no edge lies in such a half-plane."""
    for edge in solid.Edges:
        if edge.Length <= length_tol:
            continue
        u0, u1 = edge.ParameterRange
        radial = []
        for k in range(7):
            q = edge.valueAt(u0 + (u1 - u0) * k / 6) - point
            radial.append(q - axis * axis.dot(q))
        r0 = max(radial, key=lambda r: r.Length)
        if r0.Length <= length_tol:
            continue
        r0 = App.Vector(r0).normalize()
        m = axis.cross(r0)
        if all(abs(m.dot(r)) <= length_tol and r.dot(r0) >= -length_tol for r in radial):
            return r0
    return None


def _ring(solid, tol, length_tol):
    """The Sweep of solid as a closed ring, the reason it is not one, or None when it has no curved face to turn
    about or its cut does not make a ring (it touches the axis: a body of revolution without a hole, a sphere)."""
    faces = solid.Faces
    if all(_planar(f) for f in faces):
        return None
    line = _first_axis(faces)
    if line is None:
        return NO_AXIS
    point, axis = line
    if not all(_turns_about(f, point, axis, tol) for f in faces):
        return NO_AXIS
    u = _meridian(solid, point, axis, length_tol)
    if u is None:  # no seam: angle 0 about the axis
        ref = App.Vector(1, 0, 0) if abs(axis.x) < 0.9 else App.Vector(0, 1, 0)
        u = (ref - axis * axis.dot(ref)).normalize()
    box = solid.BoundBox
    length = 2 * box.DiagonalLength + (box.Center - point).Length
    low, high = point - axis * length, point + axis * length
    half = Part.Face(Part.makePolygon([low, high, high + u * length, low + u * length, low]))
    cut = solid.common(half).Faces
    if len(cut) != 1:
        return None
    face = cut[0]
    c = face.CenterOfMass
    origin = _nearest(point, axis, c)
    if _touches(face, point, axis, length, length_tol):
        return None
    if not _pappus(solid, face, (c - origin).Length, 2 * math.pi, tol):
        return VOLUME
    if axis.cross(c - origin).dot(_normal(face)) > 0:  # turn against the cut's normal, as from a start face
        axis = -axis
    return Sweep(None, None, [Piece(tuple(origin), tuple(axis), 360.0, 0.0)], True, face)


def _forward(d, tol):
    """True if d's first component that is not about 0 is positive: of a pair of end faces matched both ways
    without a start face, the sweep runs this way (from the z = 0 end of an upright bar)."""
    return next((c > 0 for c in d if abs(c) > tol), True)


def _recognise(solid, start, label, tol):
    """recognise with start a 0-based face index or None; label names the start face in the reason. Of several
    sweeps the longest path wins, measured at the profile's centre of mass for a turn."""
    faces = solid.Faces
    length_tol = tol * max(1.0, solid.BoundBox.DiagonalLength)
    reach = 2 * solid.BoundBox.DiagonalLength
    planar = [k for k, f in enumerate(faces) if _planar(f)]
    if start is not None and start not in planar:
        return NOT_AN_END.format(face=label)
    reasons, best = [], None  # best: (path length, Sweep)
    for i in planar if start is None else [start]:
        a = faces[i]
        na = _normal(a)
        for j in planar:
            b = faces[j]
            if j == i or abs(a.Area - b.Area) > tol * max(a.Area, b.Area):
                continue
            nb = _normal(b)
            if na.dot(nb) > -1 + tol:
                turn = _rotation(solid, i, j, na, nb, tol, length_tol)
                if turn is None:
                    curved = not any(_planar(f) for k, f in enumerate(faces) if k not in (i, j))
                    if curved and _screw_maps(a, b, na, nb, length_tol):
                        reasons.append(NOT_STRAIGHT)
                    continue
                point, axis, angle = turn
                rc, theta = (a.CenterOfMass - point).Length, math.radians(angle)
                if _touches(a, point, axis, reach + rc, length_tol):
                    continue
                if not _pappus(solid, a, rc, theta, tol):
                    reasons.append(VOLUME)
                    continue
                if best is None or rc * theta > best[0] + length_tol:
                    piece = Piece(tuple(point), tuple(axis), angle, 0.0)
                    best = (rc * theta, Sweep(f"Face{i + 1}", f"Face{j + 1}", [piece], False, a))
                continue
            d = b.CenterOfMass - a.CenterOfMass
            if d.Length < length_tol or (start is None and not _forward(d, length_tol)):
                continue  # without a start face, each pair is tried one way: the other is the same sweep reversed
            moved = a.copy()
            moved.translate(d)
            if not objects.coincident_faces(moved, b, length_tol):
                continue
            unit = App.Vector(d).normalize()
            if not all(_runs_along(f, unit, tol) for k, f in enumerate(faces) if k not in (i, j)):
                reasons.append(SIDE_FACE)
                continue
            if abs(solid.Volume - a.Area * abs(d.dot(na))) > tol * solid.Volume:
                reasons.append(VOLUME)
                continue
            if best is None or d.Length > best[0] + length_tol:
                piece = Piece(tuple(a.CenterOfMass), tuple(unit), 0, d.Length)
                best = (d.Length, Sweep(f"Face{i + 1}", f"Face{j + 1}", [piece], False, a))
    if start is None:
        ring = _ring(solid, tol, length_tol)
        if isinstance(ring, Sweep):
            path = 2 * math.pi * (ring.face.CenterOfMass - App.Vector(ring.pieces[0].origin)).Length
            if best is None or path > best[0] + length_tol:
                best = (path, ring)
        elif ring is not None and not (ring == NO_AXIS and planar):  # with flat faces, the end faces are wrong
            reasons.append(ring)
    if best:
        return best[1]
    for reason in (NOT_STRAIGHT, SIDE_FACE, VOLUME, NO_AXIS):
        if reason in reasons:
            return reason
    return NO_END if start is None else NOT_AN_END.format(face=label)


def recognise(solid, start_face=None, tol=1e-6):
    """The Sweep solid is, or the reason it is not one (a string). start_face: a face name of solid ("Face3") to
    sweep from; without it, any flat end face (the longest sweep when several match), or a closed ring's cut."""
    start = None if start_face is None else int(start_face[4:]) - 1
    return _recognise(solid, start, start_face, tol)


def recognise_body(shape, start_faces=(), tol=1e-6):
    """One Sweep per solid of shape, in shape.Solids order, or the first refusal (a string, prefixed "solid k: " when
    there are several solids). start_faces: face names of shape, each matched to the solid holding it."""
    solids = shape.Solids
    starts = {}
    for name in start_faces:
        face = shape.getElement(name)
        owner = next(
            ((s, k) for s, solid in enumerate(solids) for k, f in enumerate(solid.Faces) if f.isSame(face)), None
        )
        if owner is None:
            return NOT_AN_END.format(face=name)
        starts.setdefault(owner[0], (owner[1], name))
    if not solids:
        return NO_END
    result = []
    for s, solid in enumerate(solids):
        start, label = starts.get(s, (None, None))
        sweep = _recognise(solid, start, label, tol)
        if isinstance(sweep, str):
            return f"solid {s + 1}: {sweep}" if len(solids) > 1 else sweep
        result.append(sweep)
    return result
