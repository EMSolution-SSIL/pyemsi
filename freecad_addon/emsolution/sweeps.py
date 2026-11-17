"""Recognising a body as a profile face swept along a path (Swept Body). No GUI or mesh generation here.

A sweep is its start face moved along a path of pieces, each a screw motion: straight (a translation), revolved (a turn
about a line) or helical (both). A face is invariant under a piece when its points, moved along the piece, stay on the
piece's side faces. Recognised are:
- one piece between two flat end faces: the end face is the start face moved by a translation, a turn or a helix
  (fitted to the side faces), and every other face is invariant under it;
- closed rings: no end faces, every face invariant under a whole turn about one line; the profile is the body cut by a
  half-plane through the line;
- chains: walked from the start face, each group of side faces touching the current section is a piece whose far
  boundary is a flat section congruent with the profile, the last one ending on a flat end face."""

import math
from collections import namedtuple

import numpy as np

import FreeCAD as App
import Part

from . import objects

# A screw motion: a turn by angle (degrees) about the axis through origin, then an advance (mm) along that axis. A
# straight piece has angle 0 and advance its length; origin is then the profile's centre of mass. A revolved piece has
# advance 0, a helical one both. For those, origin is the axis point nearest the profile's centre of mass, and the axis
# is turned so that a positive angle runs from the start face to the end face; a helix's advance is signed along it.
Piece = namedtuple("Piece", "origin axis angle advance")
# profile, end: face names of the solid (end is None when closed, both None for a closed ring); pieces: a list of
# Piece in path order, each starting where the last ended; face: the profile as a Part.Face in the solid's coordinates
# (the start face, or a closed ring's cut); rebuild: True when the side surfaces follow the pieces but an edge along
# them does not (a round pipe made without Frenet mode: its seam twists), so the solid is exported rebuilt.
Sweep = namedtuple("Sweep", "profile end pieces closed face rebuild", defaults=(False,))

NO_END = "it has no flat end face that matches another end face moved"
NOT_AN_END = "the start face {face} is not a flat end face of it"
PATH = "its path is not made of straight, arc and helical pieces"
TWISTS = "the profile twists along the path; make the pipe with Frenet mode"
SIDE_FACE = "a side face does not run straight from one end to the other"
VOLUME = "its volume is not the start face swept to the end face"
NO_AXIS = "its faces do not all turn about one axis"

FRACTIONS = (0.25, 0.5, 0.75)  # of a piece's motion, by which _invariant moves its samples
# A helix fit whose largest |n . v| / |v| is below this, but whose side faces are not invariant, is a profile that
# twists along a helix (a non-round pipe made without Frenet mode); its end then lies within this x size of the
# moved start face's centre and normal. Anything further off is not a helix at all.
TWIST_FIT = 0.02
# How far an edge along a helical piece may lie from the screw image of its start, times the body's size, before the
# solid is exported rebuilt: the mesher's tolerance (meshsweep.TOL), as it then still meets the edge.
FOLLOW_TOL = 2.5e-5
MAX_TURN = 2 * math.pi * 1000  # radians: a fitted helix turning further is a turn (a rise per radian of about 0)


def _planar(face):
    return isinstance(face.Surface, Part.Plane)


def _normal(face):
    """The outward normal of a planar face of a solid."""
    u0, u1, v0, v1 = face.ParameterRange
    return face.normalAt((u0 + u1) / 2, (v0 + v1) / 2)


def _array(v):
    return np.array([v.x, v.y, v.z])


def _samples(face, m):
    """(point, normal) at the points of face's m x m parameter grid that lie on the face (inside its trims); a finer
    grid when none does."""
    u0, u1, v0, v1 = face.ParameterRange
    out = []
    for i in range(m):
        for j in range(m):
            u, v = u0 + (u1 - u0) * (i + 0.5) / m, v0 + (v1 - v0) * (j + 0.5) / m
            if face.isPartOfDomain(u, v):
                out.append((face.valueAt(u, v), face.normalAt(u, v)))
    return out if out or m > 40 else _samples(face, 3 * m)


def _distance(face, q):
    """The distance of point q from face: by projection onto its surface when that lands inside the face
    (distToShape can miss the inside of a periodic face, such as a part of a torus), else by distToShape."""
    surface = face.Surface
    u, v = surface.parameter(q)
    if face.isPartOfDomain(u, v):
        return (surface.value(u, v) - q).Length
    return face.distToShape(Part.Vertex(q))[0]


def _move(p, piece, f):
    """Point p moved by the fraction f (negative: back) of piece's screw motion."""
    o, d = App.Vector(*piece.origin), App.Vector(*piece.axis)
    return o + App.Rotation(d, piece.angle * f).multVec(p - o) + d * (piece.advance * f)


def _moved(face, piece):
    """A copy of face moved by the whole of piece's screw motion."""
    out = face.copy()
    out.rotate(App.Vector(*piece.origin), App.Vector(*piece.axis), piece.angle)
    out.translate(App.Vector(*piece.axis) * piece.advance)
    return out


def _crossings(p, piece, c, n, reach):
    """The fractions s in about [0, 1] at which p, moved back by s of a turning piece's motion, crosses the plane (c,
    n) within reach of c."""
    o, d = _array(App.Vector(*piece.origin)), _array(App.Vector(*piece.axis))
    theta, advance = math.radians(piece.angle), piece.advance
    q0 = _array(p) - o
    cross, along = np.cross(d, q0), d * d.dot(q0)
    c, n = _array(c) - o, _array(n)

    def back(s):
        cos, sin = np.cos(-theta * s)[:, None], np.sin(-theta * s)[:, None]
        return (q0 - along) * cos + cross * sin + along - d * (advance * s)[:, None]

    s = np.linspace(-0.01, 1.01, max(9, math.ceil(theta / 0.05) + 1))
    q = back(s)
    g = (q - c) @ n
    step = (np.linalg.norm(q0 - along) * theta + abs(advance)) * (s[1] - s[0])
    near = np.linalg.norm(q - c, axis=1) <= reach + step
    out = []
    for i in np.nonzero(np.sign(g[:-1]) != np.sign(g[1:]))[0]:
        if not (near[i] or near[i + 1]):
            continue
        lo, hi, low = s[i], s[i + 1], g[i] > 0
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            if ((back(np.array([mid]))[0] - c) @ n > 0) == low:
                lo = mid
            else:
                hi = mid
        out.append(float(0.5 * (lo + hi)))
    return out


def _phase(p, piece, start, tol):
    """The fraction s in [0, 1] of piece's motion that moves a point of start (its planar start face) onto p: the
    nearest one, within tol. None when no point of start gets there."""
    c, n = start.CenterOfMass, _normal(start)
    if piece.angle:
        found = _crossings(p, piece, c, n, start.BoundBox.DiagonalLength + tol)
    else:
        rate = piece.advance * n.dot(App.Vector(*piece.axis))
        found = [n.dot(p - c) / rate] if abs(rate) > tol else []
    best = None
    for s in found:
        if -1e-6 <= s <= 1 + 1e-6:
            dist = _distance(start, _move(p, piece, -s))
            if dist <= tol and (best is None or dist < best[0]):
                best = (dist, min(max(s, 0.0), 1.0))
    return None if best is None else best[1]


def _invariant(face, piece, origin_state, tol):
    """True if face is invariant under piece's screw motion: each point sampled on face (5 x 5, inside its trims),
    moved by the fractions 0.25, 0.5 and 0.75 of the motion, lies within tol of the side faces. origin_state: (start,
    sides), start the piece's planar start face, or None for a closed ring (whole turns, moved forward), and sides a
    list of the piece's side faces. On an open piece each sample must trace back to start, at a fraction s of the
    motion; it is then moved forward, or back when forward would pass the end, and a fraction that fits neither way is
    skipped."""
    start, sides = origin_state
    for p, _ in _samples(face, 5):
        s = 0.0 if start is None else _phase(p, piece, start, tol)
        if s is None:
            return False
        for f in FRACTIONS:
            if start is not None and s + f > 1:
                if s - f < 0:
                    continue
                f = -f
            q = _move(p, piece, f)
            if all(_distance(side, q) > tol for side in sides):
                return False
    return True


def _swept_volume(face, piece):
    """The volume face sweeps along piece: A |n . (theta axis x (c - origin) + advance axis)|."""
    o, d = App.Vector(*piece.origin), App.Vector(*piece.axis)
    v = d.cross(face.CenterOfMass - o) * math.radians(piece.angle) + d * piece.advance
    return face.Area * abs(_normal(face).dot(v))


def _length(face, piece):
    """The length of the path of face's centre of mass along piece: sqrt((rc theta)^2 + advance^2)."""
    d = App.Vector(*piece.axis)
    q = face.CenterOfMass - App.Vector(*piece.origin)
    return math.hypot((q - d * d.dot(q)).Length * math.radians(piece.angle), piece.advance)


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


def _rotation(a, b, others, na, nb, tol, length_tol):
    """The revolved Piece that turns face a onto face b about a line: origin is the line's point nearest a's centre,
    and the axis is turned so that the positive angle runs through the body. None when there is no such turn."""
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
    if axis.cross(c - point).dot(na) > 0:  # the short turn leaves the body through a: it runs the long way round
        axis, angle = -axis, 360.0 - angle
    return Piece(tuple(point), tuple(axis), angle, 0.0)


def _screw_fit(faces, size):
    """(origin, unit axis, rise per radian, residual) of the screw motion whose velocity is tangent to faces at their
    10 x 10 samples: the least-squares null vector of the rows [(p - c) x n / size, n]. The residual is the largest
    |n . v| / |v| over the samples. None when there are too few samples or the motion does not turn."""
    at = [s for f in faces for s in _samples(f, 10)]
    if len(at) < 6:
        return None
    points, normals = np.array([_array(p) for p, _ in at]), np.array([_array(n) for _, n in at])
    c = points.mean(axis=0)
    x = np.linalg.svd(np.hstack([np.cross(points - c, normals) / size, normals]), full_matrices=False)[2][-1]
    k = np.linalg.norm(x[:3])
    if k < 1e-9:
        return None
    d, v = x[:3] / k, x[3:] * size / k
    origin, h = c + np.cross(d, v), float(d.dot(v))
    velocity = np.cross(d, points - origin) + h * d
    speed = np.maximum(np.linalg.norm(velocity, axis=1), 1e-300)
    residual = float(np.max(np.abs(np.einsum("ij,ij->i", normals, velocity)) / speed))
    return App.Vector(*map(float, origin)), App.Vector(*map(float, d)), h, residual


def _follows(a, b, others, piece, tol):
    """True if the edges along piece follow its screw motion: each vertex of a lands on a vertex of b, and points of
    the lateral edges (those of others not on a or b) trace back to vertices of a. A Frenet pipe's do; the seam of a
    round pipe made without Frenet mode twists, while its side surface does not."""
    starts, ends = [v.Point for v in a.Vertexes], [v.Point for v in b.Vertexes]
    for p in starts:
        q = _move(p, piece, 1.0)
        if not ends or min(q.distanceToPoint(e) for e in ends) > tol:
            return False
    for face in others:
        for edge in face.Edges:
            u0, u1 = edge.ParameterRange
            mid = Part.Vertex(edge.valueAt((u0 + u1) / 2))
            if a.distToShape(mid)[0] <= tol or b.distToShape(mid)[0] <= tol:
                continue
            for k in (1, 2, 3):
                p = edge.valueAt(u0 + (u1 - u0) * k / 4)
                s = _phase(p, piece, a, tol)
                if s is None:
                    return False
                q = _move(p, piece, -s)
                if not starts or min(q.distanceToPoint(x) for x in starts) > tol:
                    return False
    return True


def _lands(moved, b, tol):
    """True if face moved lies on face b within tol: the same area and centre, and each one's boundary, sampled at 8
    points an edge, on the other (coincident_faces compares bounding boxes, which are loose about curved edges)."""
    if abs(moved.Area - b.Area) > tol * max(1.0, b.Area) or moved.CenterOfMass.distanceToPoint(b.CenterOfMass) > tol:
        return False
    for f, g in ((moved, b), (b, moved)):
        for edge in f.Edges:
            u0, u1 = edge.ParameterRange
            if any(_distance(g, edge.valueAt(u0 + (u1 - u0) * k / 8)) > tol for k in range(8)):
                return False
    return True


def _ends_screw(a, b, na, nb, origin, d, theta, advance):
    """The helical Piece from face a to face b about the fitted axis (origin, d), turning about theta radians: the
    angle and the axis position refined from the end faces, which are exact where the fit is only as good as the side
    surfaces. The angle turns a's normal into b's, the whole turns taken from theta. The position comes from the
    centres, unless the turn is about whole turns (the centres then do not fix it)."""
    pa, pb = -na - d * d.dot(-na), nb - d * d.dot(nb)
    if pa.Length > 1e-3 and pb.Length > 1e-3:
        part = math.atan2(d.dot(pa.cross(pb)), pa.dot(pb))
        theta = part + 2 * math.pi * round((theta - part) / (2 * math.pi))
    ca, cb = a.CenterOfMass, b.CenterOfMass
    if abs(math.sin(theta / 2)) > 0.05:
        # o + R (ca - o) = cb - advance d, in the plane normal to d: (I - R) o = w
        w = cb - d * advance - App.Rotation(d, math.degrees(theta)).multVec(ca)
        w -= d * d.dot(w)
        e1 = d.cross(App.Vector(0, 0, 1) if abs(d.z) < 0.9 else App.Vector(1, 0, 0)).normalize()
        e2 = d.cross(e1)
        c, s = math.cos(theta), math.sin(theta)
        x, y, det = w.dot(e1), w.dot(e2), (1 - c) ** 2 + s**2
        origin = (e1 * ((1 - c) * x - s * y) + e2 * (s * x + (1 - c) * y)) * (1 / det)
    return Piece(tuple(_nearest(origin, d, ca)), tuple(d), math.degrees(theta), advance)


def _helix(a, b, na, nb, others, state, length_tol, size):
    """(helical Piece, rebuild) from face a to face b, fitted to others (the side faces, all curved); TWISTS when the
    fit is close but the profile turns about its normal along the way; None when it is no helix."""
    fit = _screw_fit(others, size)
    if fit is None:
        return None
    origin, d, h, residual = fit
    ca, cb = a.CenterOfMass, b.CenterOfMass
    advance = d.dot(cb - ca)
    if abs(advance) <= length_tol or abs(h) <= length_tol or abs(advance / h) > MAX_TURN:
        return None  # a translation or a turn: not a helix
    theta = advance / h
    if theta < 0:
        d, theta, advance = -d, -theta, -advance
    piece = _ends_screw(a, b, na, nb, origin, d, theta, advance)
    close = residual < TWIST_FIT
    moved = _moved(a, piece)
    if not _lands(moved, b, length_tol):
        lands = moved.CenterOfMass.distanceToPoint(cb) <= TWIST_FIT * size and _normal(moved).dot(nb) < -1 + TWIST_FIT
        return TWISTS if close and lands else None
    if not all(_invariant(f, piece, state, length_tol) for f in others):
        return TWISTS if close else None
    return piece, not _follows(a, b, others, piece, FOLLOW_TOL * size)


def _screw_maps(a, b, na, nb, length_tol):
    """True if face a, turned into face b's plane and moved onto b's centre, lies on b: the ends of a path that is not
    one translation or turn."""
    moved = a.copy()
    axis = na.cross(-nb)
    if axis.Length > 1e-12:
        moved.rotate(a.CenterOfMass, axis, math.degrees(math.atan2(axis.Length, na.dot(-nb))))
    moved.translate(b.CenterOfMass - a.CenterOfMass)
    return _lands(moved, b, length_tol)


def _leaves_line(solid, a, others, d, length_tol):
    """True if, of end faces a and a moved by the translation d, every other face is curved and the straight line
    between their centres leaves solid: a path that is not straight (a straight body with a bulge or a groove keeps
    its centre line inside)."""
    if any(_planar(f) for f in others):
        return False
    c = a.CenterOfMass
    return any(not solid.isInside(c + d * (k / 8), length_tol, True) for k in range(1, 8))


def _piece(solid, a, b, na, nb, others, tol, length_tol, size):
    """(Piece, rebuild) of the screw motion that moves face a onto face b, every face of others (the side faces)
    invariant under it: a translation (when the normals are opposite), a turn, or a helix fitted to curved side faces.
    Else the reason it is no piece (PATH, TWISTS or SIDE_FACE), or None when the ends do not match. na, nb: the outward
    normals of a and b (a's points back along the path, b's forward)."""
    state = (a, others)
    curved = not any(_planar(f) for f in others)
    reason = None
    if na.dot(nb) <= -1 + tol:
        d = b.CenterOfMass - a.CenterOfMass
        moved = a.copy()
        moved.translate(d)
        if d.Length >= length_tol and objects.coincident_faces(moved, b, length_tol):
            piece = Piece(tuple(a.CenterOfMass), tuple(App.Vector(d).normalize()), 0, d.Length)
            if all(_invariant(f, piece, state, length_tol) for f in others):
                return piece, False
            reason = PATH if _leaves_line(solid, a, others, d, length_tol) else SIDE_FACE
    else:
        piece = _rotation(a, b, others, na, nb, tol, length_tol)
        if piece is not None and all(_invariant(f, piece, state, length_tol) for f in others):
            return piece, False
        if curved and _screw_maps(a, b, na, nb, length_tol):
            reason = PATH
    if curved:
        helix = _helix(a, b, na, nb, others, state, length_tol, size)
        if helix is not None:
            return helix
    return reason


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
    turn = Piece(tuple(point), tuple(axis), 360.0, 0.0)
    if not all(_invariant(f, turn, (None, faces), length_tol) for f in faces):
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
    piece = Piece(tuple(origin), tuple(axis), 360.0, 0.0)
    if abs(solid.Volume - _swept_volume(face, piece)) > tol * solid.Volume:
        return VOLUME
    if axis.cross(c - origin).dot(_normal(face)) > 0:  # turn against the cut's normal, as from a start face
        axis = -axis
    return Sweep(None, None, [Piece(tuple(origin), tuple(axis), 360.0, 0.0)], True, face)


def _forward(d, tol):
    """True if d's first component that is not about 0 is positive: of a pair of end faces matched both ways
    without a start face, the sweep runs this way (from the z = 0 end of an upright bar)."""
    return next((c > 0 for c in d if abs(c) > tol), True)


def _topology(solid):
    """(owners, face_edges): the set of face indexes holding each edge of solid, and of edge indexes of each face."""
    edges = solid.Edges
    face_edges = [{n for n, e in enumerate(edges) if any(e.isSame(g) for g in f.Edges)} for f in solid.Faces]
    return [{k for k, held in enumerate(face_edges) if n in held} for n in range(len(edges))], face_edges


def _section(edges):
    """The planar face bounded by edges (closed wires, holes inside the outer one), or None when they bound none."""
    try:
        wires = [Part.Wire(group) for group in Part.sortEdges(edges)]
        if not all(w.isClosed() for w in wires):
            return None
        faces = Part.makeFace(wires, "Part::FaceMakerBullseye").Faces
    except (Part.OCCError, RuntimeError):  # edges that make no closed wires, or wires in different planes
        return None
    return faces[0] if len(faces) == 1 and _planar(faces[0]) else None


def _onward(face, lateral, back, tol):
    """face's normal turned away from the piece that ends on it: along the lateral edges where they reach it (back:
    the piece's start section, whose centre gives the way when no lateral edge does)."""
    n = _normal(face)
    for edge in lateral:
        u0, u1 = edge.ParameterRange
        for end, inner in ((u1, u1 - 0.01 * (u1 - u0)), (u0, u0 + 0.01 * (u1 - u0))):
            p = edge.valueAt(end)
            if face.distToShape(Part.Vertex(p))[0] <= tol:
                return n if n.dot(p - edge.valueAt(inner)) > 0 else -n
    return n if n.dot(face.CenterOfMass - back.CenterOfMass) > 0 else -n


def _merged(pieces, tol, length_tol):
    """pieces with each run of one screw motion joined (a path edge split in two, a helix made of several edges)."""
    out = [pieces[0]]
    for q in pieces[1:]:
        p = out[-1]
        axis = App.Vector(*p.axis)
        same = axis.dot(App.Vector(*q.axis)) >= 1 - tol and bool(p.angle) == bool(q.angle)
        if same and p.angle:
            off = App.Vector(*q.origin) - App.Vector(*p.origin)
            rise = abs(p.advance / p.angle - q.advance / q.angle) * 360
            same = (off - axis * axis.dot(off)).Length <= length_tol and rise <= length_tol
        out[-1:] = [Piece(p.origin, p.axis, p.angle + q.angle, p.advance + q.advance)] if same else [p, q]
    return out


def _walk(solid, i, topology, tol, length_tol, size):
    """(path length, Sweep) of solid as a chain of pieces walked from its flat face i to a flat end face. The reason
    the walk stops when it found a piece before (PATH, or the next piece's reason); None when face i starts no chain.
    Each step's piece is the faces not yet used that touch the current section; its far boundary, the edges it shares
    with other faces, is the next section (or the end face)."""
    faces, edges = solid.Faces, solid.Edges
    owners, face_edges = topology
    used, boundary, cur = {i}, face_edges[i], faces[i]
    pieces, rebuild, volume, length, end = [], False, 0.0, 0.0, None
    while end is None:
        group = {k for k in range(len(faces)) if k not in used and face_edges[k] & boundary}
        inner = set().union(*(face_edges[k] for k in group))
        far = {n for n in inner - boundary if not owners[n] <= group}
        beyond = set().union(*(owners[n] for n in far)) - group
        if not far or beyond & used:
            return PATH if pieces else None
        if len(beyond) == 1 and face_edges[min(beyond)] == far and _planar(faces[min(beyond)]):
            end = min(beyond)
            b = faces[end]
            nb = _normal(b)
        else:
            b = _section([edges[n] for n in far])
            if b is None:
                return PATH if pieces else None
            nb = _onward(b, [edges[n] for n in inner - boundary - far], cur, length_tol)
        result = _piece(solid, cur, b, _normal(cur), nb, [faces[k] for k in sorted(group)], tol, length_tol, size)
        if not isinstance(result, tuple):
            return (result or PATH) if pieces else None
        piece, bent = result
        pieces.append(piece)
        rebuild = rebuild or bent
        volume += _swept_volume(cur, piece)
        length += _length(cur, piece)
        used |= group
        boundary, cur = far, _moved(cur, piece)
    if len(used) + 1 != len(faces):
        return PATH
    if abs(solid.Volume - volume) > tol * solid.Volume:
        return VOLUME
    return length, Sweep(f"Face{i + 1}", f"Face{end + 1}", _merged(pieces, tol, length_tol), False, faces[i], rebuild)


def _recognise(solid, start, label, tol):
    """recognise with start a 0-based face index or None; label names the start face in the reason. Of several
    sweeps the longest path wins, measured at the profile's centre of mass. A chain is walked only when no single
    piece or ring fits."""
    faces = solid.Faces
    size = max(1.0, solid.BoundBox.DiagonalLength)
    length_tol = tol * size
    reach = 2 * solid.BoundBox.DiagonalLength
    planar = [k for k, f in enumerate(faces) if _planar(f)]
    if start is not None and start not in planar:
        return NOT_AN_END.format(face=label)
    starts = planar if start is None else [start]
    reasons, best = [], None  # best: (path length, Sweep)
    for i in starts:
        a = faces[i]
        na = _normal(a)
        for j in planar:
            b = faces[j]
            if j == i or abs(a.Area - b.Area) > tol * max(a.Area, b.Area):
                continue
            nb = _normal(b)
            if na.dot(nb) <= -1 + tol:
                d = b.CenterOfMass - a.CenterOfMass
                if d.Length < length_tol or (start is None and not _forward(d, length_tol)):
                    continue  # without a start face, each pair is tried one way: the other is the same sweep reversed
            others = [f for k, f in enumerate(faces) if k not in (i, j)]
            result = _piece(solid, a, b, na, nb, others, tol, length_tol, size)
            if not isinstance(result, tuple):
                if result:
                    reasons.append(result)
                continue
            piece, rebuild = result
            if piece.angle and not piece.advance:
                point, axis = App.Vector(*piece.origin), App.Vector(*piece.axis)
                if _touches(a, point, axis, reach + (a.CenterOfMass - point).Length, length_tol):
                    continue
            if abs(solid.Volume - _swept_volume(a, piece)) > tol * solid.Volume:
                reasons.append(VOLUME)
                continue
            path = _length(a, piece)
            if best is None or path > best[0] + length_tol:
                best = (path, Sweep(f"Face{i + 1}", f"Face{j + 1}", [piece], False, a, rebuild))
    if start is None:
        ring = _ring(solid, tol, length_tol)
        if isinstance(ring, Sweep):
            path = _length(ring.face, ring.pieces[0])
            if best is None or path > best[0] + length_tol:
                best = (path, ring)
        elif ring is not None and not (ring == NO_AXIS and planar):  # with flat faces, the end faces are wrong
            reasons.append(ring)
    if best is None and planar:
        topology, stops = _topology(solid), []
        for i in starts:
            chain = _walk(solid, i, topology, tol, length_tol, size)
            if isinstance(chain, str):
                stops.append(chain)
            elif chain is not None and (best is None or chain[0] > best[0] + length_tol):
                best = chain
        reasons = reasons or stops  # a walk's reason only when no single piece gave one
    if best:
        return best[1]
    for reason in (TWISTS, PATH, SIDE_FACE, VOLUME, NO_AXIS):
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
