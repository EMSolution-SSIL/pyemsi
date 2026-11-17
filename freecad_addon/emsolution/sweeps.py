"""Recognising a body as a profile face swept along a path (Swept Body). No GUI or mesh generation here.

Stage 1 recognises straight sweeps only: an end face moved by a translation onto the other end face, every side face
running along the translation."""

import math
from collections import namedtuple

import FreeCAD as App
import Part

from . import objects

# A screw motion: angle (degrees) about the axis through origin, and advance (mm) along it. A straight piece has angle
# 0 and advance its length; origin is then the profile's centre of mass.
Piece = namedtuple("Piece", "origin axis angle advance")
# profile, end: face names of the solid (end is None when closed); pieces: a list of Piece.
Sweep = namedtuple("Sweep", "profile end pieces closed")

NO_END = "it has no flat end face that matches another end face moved"
NOT_AN_END = "the start face {face} is not a flat end face of it"
NOT_STRAIGHT = "only straight sweeps are made so far"
SIDE_FACE = "a side face does not run straight from one end to the other"
VOLUME = "its volume is not the start face swept to the end face"


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


def _rotation_maps(solid, i, j, na, nb, tol, length_tol):
    """True if a turn about the line where the planes of faces i and j of solid meet maps face i onto face j, and
    every other face runs around that line (a revolved body, made in a later stage)."""
    faces = solid.Faces
    a, b = faces[i], faces[j]
    axis = na.cross(-nb)
    if axis.Length < tol:
        return False  # parallel planes: no line to turn about
    axis.normalize()
    angle = math.degrees(math.atan2(na.cross(-nb).Length, na.dot(-nb)))
    # A point on the line: on both planes, and on the plane through a's centre normal to the line.
    da, db, du = na.dot(a.CenterOfMass), nb.dot(b.CenterOfMass), axis.dot(a.CenterOfMass)
    point = (nb.cross(axis) * da + axis.cross(na) * db + na.cross(nb) * du) * (1.0 / na.dot(nb.cross(axis)))
    moved = a.copy()
    moved.rotate(point, axis, angle)
    if not objects.coincident_faces(moved, b, length_tol):
        return False
    return all(_turns_about(f, point, axis, tol) for k, f in enumerate(faces) if k not in (i, j))


def _forward(d, tol):
    """True if d's first component that is not about 0 is positive: of a pair of end faces matched both ways
    without a start face, the sweep runs this way (from the z = 0 end of an upright bar)."""
    return next((c > 0 for c in d if abs(c) > tol), True)


def _recognise(solid, start, label, tol):
    """recognise with start a 0-based face index or None; label names the start face in the reason."""
    faces = solid.Faces
    length_tol = tol * max(1.0, solid.BoundBox.DiagonalLength)
    planar = [k for k, f in enumerate(faces) if _planar(f)]
    if start is not None and start not in planar:
        return NOT_AN_END.format(face=label)
    reasons, best = [], None
    for i in planar if start is None else [start]:
        a = faces[i]
        na = _normal(a)
        for j in planar:
            b = faces[j]
            if j == i or abs(a.Area - b.Area) > tol * max(a.Area, b.Area):
                continue
            nb = _normal(b)
            if na.dot(nb) > -1 + tol:
                if _rotation_maps(solid, i, j, na, nb, tol, length_tol):
                    reasons.append(NOT_STRAIGHT)
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
            if best is None or d.Length > best[2].Length + length_tol:
                best = (i, j, d, unit)
    if best:
        i, j, d, unit = best
        piece = Piece(tuple(faces[i].CenterOfMass), tuple(unit), 0, d.Length)
        return Sweep(f"Face{i + 1}", f"Face{j + 1}", [piece], False)
    for reason in (NOT_STRAIGHT, SIDE_FACE, VOLUME):
        if reason in reasons:
            return reason
    return NO_END if start is None else NOT_AN_END.format(face=label)


def recognise(solid, start_face=None, tol=1e-6):
    """The Sweep solid is, or the reason it is not one (a string). start_face: a face name of solid ("Face3") to
    sweep from; without it, any flat end face (the longest sweep when several match)."""
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
