"""Mesher tests. Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_mesher.py"""

import hashlib
import json
import math
import os
import stat
import subprocess
import sys
import tempfile
import unittest

import gmsh

MESHER = os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution", "mesher.py")


def write_box(path, x, y, z, dx, dy, dz):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addBox(x, y, z, dx, dy, dz)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_rect(path, x, y, z, dx, dy):
    """Rectangle in the plane z = const."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addRectangle(x, y, z, dx, dy)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_rect_x(path, x, y, z, dy, dz):
    """Rectangle in the plane x = const."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        face = gmsh.model.occ.addRectangle(0, 0, 0, dz, dy)  # (a, b, 0) turns to (0, b, a)
        gmsh.model.occ.rotate([(2, face)], 0, 0, 0, 0, 1, 0, -math.pi / 2)
        gmsh.model.occ.translate([(2, face)], x, y, z)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_line(path, p, q):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addLine(gmsh.model.occ.addPoint(*p), gmsh.model.occ.addPoint(*q))
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_point(path, p):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addPoint(*p)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_rings(path, *rings):
    """One BREP holding a solid ring sector about Z per (inner, outer, z0, height[, a0, a1]): a cylinder when inner
    is 0, from angle a0 to a1 (degrees, default the full turn)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        for inner, outer, z0, h, *angles in rings:
            a0, a1 = angles or (0.0, 360.0)
            sweep = math.radians(a1 - a0)
            vol = [(3, occ.addCylinder(0, 0, z0, 0, 0, h, outer, angle=sweep))]
            if inner:
                vol = occ.cut(vol, [(3, occ.addCylinder(0, 0, z0 - 1, 0, 0, h + 2, inner, angle=sweep))])[0]
            occ.rotate(vol, 0, 0, 0, 0, 0, 1, math.radians(a0))
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_revolved(path, p, q, a0, a1):
    """The face swept by the line p-q turning about Z from angle a0 to a1 (degrees): a cylinder piece for a vertical
    line, a disc or ring piece for a radial one. Built like FreeCAD's half faces, so a disc piece has a corner on Z."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        line = occ.addLine(occ.addPoint(*p), occ.addPoint(*q))
        out = occ.revolve([(1, line)], 0, 0, 0, 0, 0, 1, math.radians(a1 - a0))
        occ.rotate([dt for dt in out if dt[0] == 2], 0, 0, 0, 0, 0, 1, math.radians(a0))
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_sphere_shell(path, outer, inner):
    """The octant of a spherical shell. Both spherical faces have the pole of their sphere, a zero-length edge, on a
    corner."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        big = occ.addSphere(0, 0, 0, outer, angle1=0, angle2=math.pi / 2, angle3=math.pi / 2)
        small = occ.addSphere(0, 0, 0, inner, angle1=0, angle2=math.pi / 2, angle3=math.pi / 2)
        occ.cut([(3, big)], [(3, small)])
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_arc(path, p, q, centre):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        occ.addCircleArc(occ.addPoint(*p), occ.addPoint(*centre), occ.addPoint(*q))
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def read_nodes(path):
    """[(x, y, z)] of the nodes of a mesh file, rounded to 1e-9."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        c = gmsh.model.mesh.getNodes()[1]
    finally:
        gmsh.finalize()
    return [tuple(round(x, 9) + 0.0 for x in c[i : i + 3]) for i in range(0, len(c), 3)]


def box_lines(x=0.0):
    """The 12 edges of the unit box at x as point pairs."""
    pts = [(x + i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    return [(p, q) for a, p in enumerate(pts) for q in pts[a + 1 :] if sum(abs(u - v) for u, v in zip(p, q)) == 1]


def air_grading(name="Grow", mat_ids=(2,), growth=60.0, far=20.0):
    """An entry of job["air_grading"]."""
    return {"name": name, "mat_ids": list(mat_ids), "growth": growth, "far": far}


def simplices(path, dim, group=None):
    """[(corner points)] of the dim-dimensional triangles (2D) or tetrahedra (3D) of a mesh file, of one physical
    group if given."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        tags, coords = gmsh.model.mesh.getNodes()[:2]
        at = {int(t): tuple(float(x) for x in coords[3 * k : 3 * k + 3]) for k, t in enumerate(tags)}
        if group is None:
            ents = [t for _, t in gmsh.model.getEntities(dim)]
        else:
            ents = gmsh.model.getEntitiesForPhysicalGroup(dim, group)
        out = []
        for e in ents:
            for nodes in gmsh.model.mesh.getElements(dim, e)[2]:
                n = dim + 1
                out += [tuple(at[int(t)] for t in nodes[k : k + n]) for k in range(0, len(nodes), n)]
    finally:
        gmsh.finalize()
    return out


def facets(elements, keep):
    """The faces (of tetrahedra) or edges (of triangles) that only one of the elements has, with every corner passing
    keep(point): the boundary of the elements, or a part of it."""
    count = {}
    for e in elements:
        for k in range(len(e)):
            f = tuple(sorted(e[:k] + e[k + 1 :]))
            count[f] = count.get(f, 0) + 1
    return [f for f, n in count.items() if n == 1 and all(keep(p) for p in f)]


def band_edge(elements, half, lo, hi):
    """Mean length of the first edge of the elements whose centre lies lo..hi from the box |x_i| <= half_i (the spikes'
    measure of the local size)."""
    lengths = []
    for e in elements:
        c = [sum(p[i] for p in e) / len(e) for i in range(3)]
        if lo <= math.hypot(*(max(abs(x) - h, 0) for x, h in zip(c, half))) < hi:
            lengths.append(math.dist(e[0], e[1]))
    return sum(lengths) / len(lengths)


def skin(name="Skin", mat_ids=(1,), depth=1.0, per_depth=2.0, layer=3.0):
    """An entry of job["skin"]."""
    return {
        "name": name,
        "mat_ids": list(mat_ids),
        "depth": depth,
        "per_depth": per_depth,
        "layer": layer,
        "quads": False,
    }


def depth_edge(elements, depth, lo, hi=math.inf):
    """Mean length of the first edge of the elements whose centre c lies lo..hi below the surface, depth(c) deep."""
    lengths = []
    for e in elements:
        if lo <= depth([sum(p[i] for p in e) / len(e) for i in range(3)]) < hi:
            lengths.append(math.dist(e[0], e[1]))
    return sum(lengths) / len(lengths)


def write_cylinder_and_end(path, end_path, r, z0, length):
    """A cylinder about Z from z0, and its end face at z0 (the profile of a Swept Body), the same OCC face."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        cyl = occ.addCylinder(0, 0, z0, 0, 0, length, r)
        occ.synchronize()
        gmsh.write(path)
        faces = [abs(f) for _, f in gmsh.model.getBoundary([(3, cyl)])]
        face = next(f for f in faces if abs(gmsh.model.getBoundingBox(2, f)[5] - z0) < 1e-6)
        occ.copy([(2, face)])
        occ.remove([(3, cyl)], recursive=True)
        occ.synchronize()
        gmsh.write(end_path)
    finally:
        gmsh.finalize()


def swept(profile, mat_id=1, name="Bar", path_size=4.0, section_size=2.0, recombine=True, skin=None, advance=40.0):
    """An entry of job["swept"]: one straight solid along +Z from its profile."""
    piece = {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0], "angle": 0.0, "advance": advance}
    return {
        "name": name,
        "mat_id": mat_id,
        "path_size": path_size,
        "section_size": section_size,
        "recombine": recombine,
        "skin": skin,
        "solids": [{"profile": "geometry/" + profile, "pieces": [piece]}],
    }


def write_revolved_rect(path, profile_path, x0, x1, z0, z1, angle):
    """A rectangle x0..x1, z0..z1 in the plane y = 0 (the profile) and the solid it sweeps turning about Z by angle
    (degrees; 360: a closed ring, its seams on the profile)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        face = occ.addRectangle(x0, z0, 0, x1 - x0, z1 - z0)
        occ.rotate([(2, face)], 0, 0, 0, 1, 0, 0, math.pi / 2)  # (x, y, 0) turns to (x, 0, y)
        occ.synchronize()
        gmsh.write(profile_path)
        out = occ.revolve([(2, face)], 0, 0, 0, 0, 0, 1, math.radians(angle))
        occ.remove([(2, face)] + [dt for dt in out if dt[0] == 2], recursive=False)
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_two_half_rings(path, profile_path, x0, x1, z0, z1, seam):
    """The closed ring of write_revolved_rect made of two half rings fused, from angles 0 and seam (degrees) about Z:
    its corners on two meridians, the profile's (angle 0) and seam."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        face = occ.addRectangle(x0, z0, 0, x1 - x0, z1 - z0)
        occ.rotate([(2, face)], 0, 0, 0, 1, 0, 0, math.pi / 2)  # (x, y, 0) turns to (x, 0, y)
        occ.synchronize()
        gmsh.write(profile_path)
        other = occ.copy([(2, face)])
        occ.rotate(other, 0, 0, 0, 0, 0, 1, math.radians(seam))
        a = [dt for dt in occ.revolve([(2, face)], 0, 0, 0, 0, 0, 1, math.radians(seam)) if dt[0] == 3]
        b = [dt for dt in occ.revolve(other, 0, 0, 0, 0, 0, 1, math.radians(360 - seam)) if dt[0] == 3]
        gmsh.option.setNumber("Geometry.OCCUnionUnify", 0)  # keep the faces split at the seams
        occ.fuse(a, b)
        occ.remove(occ.getEntities(2), recursive=False)
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_torus(path, profile_path, big, small, start=(1, 0, 0)):
    """A torus about Z (gmsh's addTorus) and its profile, the disc in the plane y = 0 whose circle starts in the
    direction start from its centre: by default where the torus's two seam circles meet, (big + small, 0, 0)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        occ.addDisk(big, 0, 0, small, small, zAxis=[0, 1, 0], xAxis=list(start))
        occ.synchronize()
        gmsh.write(profile_path)
        occ.remove(occ.getEntities(2), recursive=True)
        occ.addTorus(0, 0, 0, big, small)
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def swept_turn(profile, angle, name="Ring", path_size=4.0, section_size=2.0, recombine=False, skin=None):
    """An entry of job["swept"]: one solid turning about Z from its profile by angle (degrees; 360: a closed ring)."""
    piece = {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0], "angle": float(angle), "advance": 0.0}
    entry = swept(profile, name=name, path_size=path_size, section_size=section_size, recombine=recombine, skin=skin)
    entry["solids"] = [{"profile": "geometry/" + profile, "closed": angle == 360, "pieces": [piece]}]
    return entry


def write_helix_pipe(path, profile_path, radius, pitch, turns, section, end_path=None):
    """A Frenet pipe along a helix about Z from (radius, 0, 0) rising pitch per turn (a spline through 288 points per
    turn: its far end within 1e-5 of the screw's), and the face it is piped from (the profile of a Swept Body).
    section: ("disc", r), or ("rect", w, h) with w toward the axis and h along the binormal. end_path: also a copy of
    the pipe's end face."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        c = pitch / (2 * math.pi)
        n = math.ceil(288 * turns)
        a = [2 * math.pi * turns * k / n for k in range(n + 1)]
        spline = occ.addSpline([occ.addPoint(radius * math.cos(t), radius * math.sin(t), c * t) for t in a])
        p0 = (radius, 0.0, 0.0)
        tangent = [0.0, radius / math.hypot(radius, c), c / math.hypot(radius, c)]
        normal = [-1.0, 0.0, 0.0]
        binormal = [0.0, -tangent[2], tangent[1]]  # tangent x normal
        if section[0] == "disc":
            loop = occ.addCurveLoop([occ.addCircle(*p0, section[1], zAxis=tangent, xAxis=normal)])
        else:
            w, h = section[1] / 2, section[2] / 2
            corners = [
                occ.addPoint(*(p0[i] + u * normal[i] + v * binormal[i] for i in range(3)))
                for u, v in ((-w, -h), (w, -h), (w, h), (-w, h))
            ]
            loop = occ.addCurveLoop([occ.addLine(corners[k], corners[(k + 1) % 4]) for k in range(4)])
        face = occ.addPlaneSurface([loop])
        occ.synchronize()
        gmsh.write(profile_path)
        occ.addPipe([(2, face)], occ.addWire([spline]), "Frenet")
        occ.remove([(2, face), (1, spline)], recursive=True)
        occ.synchronize()
        gmsh.write(path)
        if end_path:
            vol = gmsh.model.getEntities(3)
            ends = [
                abs(f)
                for _, f in gmsh.model.getBoundary(vol, oriented=False)
                if gmsh.model.getType(2, abs(f)) == "Plane"
            ]
            end = max(ends, key=lambda f: math.dist(occ.getCenterOfMass(2, f), p0))
            occ.copy([(2, end)])
            occ.remove(vol, recursive=True)
            occ.synchronize()
            gmsh.write(end_path)
    finally:
        gmsh.finalize()


def write_bent_busbar(path, profile_path, x0, x1, z0, z1, leg):
    """A busbar along +Y from y = -leg to 0, a 90 degree bend about Z, then along -X for leg: the rectangle x0..x1,
    z0..z1 in the plane y = -leg (the profile) extruded, revolved and extruded, fused into one solid (its top and bottom
    faces each one plane across the three pieces)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        face = occ.addRectangle(x0, z0, 0, x1 - x0, z1 - z0)
        occ.rotate([(2, face)], 0, 0, 0, 1, 0, 0, math.pi / 2)  # (x, y, 0) turns to (x, 0, y)
        occ.translate([(2, face)], 0, -leg, 0)
        occ.synchronize()
        gmsh.write(profile_path)
        first = occ.extrude([(2, face)], 0, leg, 0)
        bend = occ.revolve([first[0]], 0, 0, 0, 0, 0, 1, math.pi / 2)
        last = occ.extrude([bend[0]], -leg, 0, 0)
        occ.fuse([first[1]], [bend[1], last[1]])
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def swept_chain(profile, pieces, name="Bend", path_size=4.0, section_size=2.0, skin=None, closed=False):
    """An entry of job["swept"]: one solid along pieces (closed: back round to its profile)."""
    entry = swept(profile, name=name, path_size=path_size, section_size=section_size, recombine=False, skin=skin)
    entry["solids"] = [{"profile": "geometry/" + profile, "closed": closed, "pieces": pieces}]
    return entry


def write_racetrack(path, profile_path, leg=30.0, r=10.0):
    """A closed racetrack: the rectangle y -r - 2..-r + 2, z -1..1 in the plane x = 0 (the profile) extruded leg along
    +x, turned half round about the line x = leg, y = 0, extruded leg along -x and turned half round about Z, fused
    into one solid (the joints' edges stay)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        corners = [occ.addPoint(0, -r + y, z) for y, z in ((-2, -1), (2, -1), (2, 1), (-2, 1))]
        loop = occ.addCurveLoop([occ.addLine(corners[k], corners[(k + 1) % 4]) for k in range(4)])
        face = occ.addPlaneSurface([loop])
        occ.synchronize()
        gmsh.write(profile_path)
        first = occ.extrude([(2, face)], leg, 0, 0)
        bend = occ.revolve([first[0]], leg, 0, 0, 0, 0, 1, math.pi)
        back = occ.extrude([bend[0]], -leg, 0, 0)
        turn = occ.revolve([back[0]], 0, 0, 0, 0, 0, 1, math.pi)
        occ.fuse([first[1]], [bend[1], back[1], turn[1]])
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def turn_z(deg):
    """The rotation about Z by deg degrees, a 4 x 4 row-major transform."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def mirror_z_line(deg):
    """The mirror in the plane through Z at angle deg, a 4 x 4 row-major transform."""
    c, s = math.cos(math.radians(2 * deg)), math.sin(math.radians(2 * deg))
    return [c, s, 0, 0, s, -c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def compose_z(a, b):
    """The transform b, then a (4 x 4 row-major)."""
    return [sum(a[4 * i + k] * b[4 * k + j] for k in range(4)) for i in range(4) for j in range(4)]


def face_centre(path):
    """The centre of mass of the one face in path."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        ((_, face),) = gmsh.model.occ.importShapes(path)
        gmsh.model.occ.synchronize()
        return gmsh.model.occ.getCenterOfMass(2, face)
    finally:
        gmsh.finalize()


def write_faces(path, folder, prefix, keep=lambda centre: True):
    """Each face of the solid in path whose centre of mass keep accepts, alone in folder/<prefix>_<n>.brep (n from 1).
    Returns the file names."""
    names = []
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        occ.importShapes(path)
        occ.synchronize()
        faces = [t for _, t in gmsh.model.getEntities(2) if keep(occ.getCenterOfMass(2, t))]
        for f in faces:
            gmsh.clear()
            occ.importShapes(path)
            occ.synchronize()
            copy = occ.copy([(2, f)])
            occ.remove(occ.getEntities(3), recursive=True)
            occ.remove([dt for dt in occ.getEntities(2) if dt not in copy], recursive=True)
            occ.synchronize()
            names.append(f"{prefix}_{len(names) + 1}.brep")
            gmsh.write(os.path.join(folder, names[-1]))
    finally:
        gmsh.finalize()
    return names


def write_turned(path, target, deg):
    """The shapes of path turned about Z by deg degrees, written to target."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        occ.rotate(occ.importShapes(path), 0, 0, 0, 0, 0, 1, math.radians(deg))
        occ.synchronize()
        gmsh.write(target)
    finally:
        gmsh.finalize()


FACES_3D = {  # gmsh element type: (nodes, its faces)
    4: (4, ((0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3))),
    5: (8, ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))),
    6: (6, ((0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5))),
    7: (5, ((0, 3, 2, 1), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4))),
}


def inner_free_faces(box):
    """The faces of the open model's 3D elements used once that do not lie on a face of box (x, y, z, dx, dy, dz):
    none in a conformal mesh."""
    tags, coords = gmsh.model.mesh.getNodes()[:2]
    at = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
    count = {}
    for _, e in gmsh.model.getEntities(3):
        for typ, nodes in zip(*gmsh.model.mesh.getElements(3, e)[::2]):
            n, faces = FACES_3D[int(typ)]
            for k in range(0, len(nodes), n):
                cell = nodes[k : k + n]
                for f in faces:
                    key = tuple(sorted(int(cell[i]) for i in f))
                    count[key] = count.get(key, 0) + 1
    lo, hi = box[:3], [box[i] + box[i + 3] for i in range(3)]

    def on_box(f):
        return any(all(abs(at[n][i] - b[i]) < 1e-9 for n in f) for i in range(3) for b in (lo, hi))

    return [f for f, c in count.items() if c == 1 and not on_box(f)]


def group_cells(path, group):
    """The 3D elements of a physical group of a mesh file as sorted tuples of their node coordinates."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        tags, coords = gmsh.model.mesh.getNodes()[:2]
        at = {int(t): tuple(round(float(x), 6) + 0.0 for x in coords[3 * k : 3 * k + 3]) for k, t in enumerate(tags)}
        out = []
        for e in gmsh.model.getEntitiesForPhysicalGroup(3, group):
            for typ, nodes in zip(*gmsh.model.mesh.getElements(3, e)[::2]):
                n = gmsh.model.mesh.getElementProperties(typ)[3]
                out += [tuple(sorted(at[int(t)] for t in nodes[k : k + n])) for k in range(0, len(nodes), n)]
    finally:
        gmsh.finalize()
    return sorted(out)


class MesherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.mkdir(os.path.join(self.dir, "geometry"))

    def tearDown(self):
        self.tmp.cleanup()

    def geo(self, name):
        return os.path.join(self.dir, "geometry", name)

    def run_job(
        self,
        volumes,
        surfaces=(),
        sizes=(),
        options=None,
        mesh_file=None,
        transfinite=None,
        recombine=None,
        air=None,
        extra=None,
    ):
        job = {
            "model_name": "Model",
            "mesh_file": mesh_file or os.path.join(self.dir, "pre_geom.msh"),
            "volumes": list(volumes),
            "surfaces": list(surfaces),
            "sizes": list(sizes),
        }
        if options is not None:
            job["options"] = options
        if transfinite is not None:
            job["transfinite"] = transfinite
        if recombine is not None:
            job["recombine"] = recombine
        if air is not None:
            job["air"] = air
        job.update(extra or {})  # e.g. the slide keys
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        return subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")

    def edge_item(self, name, lines, n):
        files = []
        for k, (p, q) in enumerate(lines, 1):
            write_line(self.geo(f"{name}_{k}.brep"), p, q)
            files.append(f"geometry/{name}_{k}.brep")
        return {"name": name, "nodes": n + 1, "distribution": "Uniform", "coef": 1.0, "files": files}

    def element_counts(self, group, dim=3):
        out = {}
        for e in gmsh.model.getEntitiesForPhysicalGroup(dim, group):
            types, tags = gmsh.model.mesh.getElements(dim, e)[:2]
            for t, ts in zip(types, tags):
                name = gmsh.model.mesh.getElementProperties(t)[0]
                out[name] = out.get(name, 0) + len(ts)
        return out

    def structured_box(self, n=3):
        return {
            "bodies": [{"name": "Core", "mat_id": 1, "corner_files": []}],
            "edges": [self.edge_item("tedge_1", box_lines(), n)],
        }

    def structured_boxes(self, *names_ids_x):
        return {
            "bodies": [{"name": n, "mat_id": m, "corner_files": []} for n, m, _ in names_ids_x],
            "edges": [self.edge_item(f"tedge_{i}", box_lines(x), 3) for i, (_, _, x) in enumerate(names_ids_x, 1)],
        }

    def open_msh(self):
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(os.path.join(self.dir, "pre_geom.msh"))
        self.addCleanup(gmsh.finalize)

    def vol(self, id_, name, file, size=0.5):
        return {"mat_id": id_, "name": name, "file": "geometry/" + file, "size": size}

    def test_two_touching_boxes_get_ids_names_and_shared_nodes(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep"), self.vol(2, "Air_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        self.open_msh()
        groups = {t: gmsh.model.getPhysicalName(3, t) for _, t in gmsh.model.getPhysicalGroups(3)}
        self.assertEqual(groups, {1: "Copper_Box", 2: "Air_Box001"})
        nodes1 = set(gmsh.model.mesh.getNodesForPhysicalGroup(3, 1)[0])
        nodes2 = set(gmsh.model.mesh.getNodesForPhysicalGroup(3, 2)[0])
        self.assertTrue(nodes1 & nodes2, "no shared nodes on the common face")

    def test_excitation_face_becomes_surface_group(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("surf_1001_1.brep"), 0, 0, 1, 1, 1)  # top face
        r = self.run_job(
            [self.vol(1, "Copper_Box", "vol_1.brep")],
            [{"smat_id": 1001, "name": "Terminal_In_Box", "mat_id": 1, "files": ["geometry/surf_1001_1.brep"]}],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(gmsh.model.getPhysicalName(2, 1001), "Terminal_In_Box")
        _, coords = gmsh.model.mesh.getNodesForPhysicalGroup(2, 1001)
        self.assertTrue(len(coords) > 0)
        for z in coords[2::3]:
            self.assertAlmostEqual(z, 1.0, places=6)

    def test_smaller_size_gives_denser_mesh(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Fine_Box", "vol_1.brep", size=0.1), self.vol(2, "Coarse_Box", "vol_2.brep", size=0.5)]
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()

        def tets(group):
            ents = gmsh.model.getEntitiesForPhysicalGroup(3, group)
            return sum(len(gmsh.model.mesh.getElements(3, e)[1][0]) for e in ents)

        self.assertGreater(tets(1), 5 * tets(2))

    def mesh_box_with_size(self, file=None, size=0.05):
        """Mesh a unit box at size 0.5, plus one size item from geometry/<file> if given.
        Returns the node coordinates as (x, y, z) tuples."""
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        sizes = [{"name": "Fine", "size": size, "files": ["geometry/" + file]}] if file else []
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], sizes=sizes)
        self.assertEqual(r.returncode, 0, r.stderr)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(os.path.join(self.dir, "pre_geom.msh"))
            c = gmsh.model.mesh.getNodes()[1]
        finally:
            gmsh.finalize()
        return [tuple(c[i : i + 3]) for i in range(0, len(c), 3)]

    def test_face_size_refines_only_that_face(self):
        write_rect(self.geo("size_1_1.brep"), 0, 0, 1, 1, 1)  # top face
        nodes = self.mesh_box_with_size("size_1_1.brep")
        top = sum(abs(z - 1) < 1e-9 for x, y, z in nodes)
        bottom = sum(abs(z) < 1e-9 for x, y, z in nodes)
        self.assertGreater(top, 20 * bottom)

    def test_edge_size_refines_that_edge(self):
        write_line(self.geo("size_1_1.brep"), (0, 0, 0), (1, 0, 0))  # box edge along x
        nodes = self.mesh_box_with_size("size_1_1.brep")
        on_edge = sum(abs(y) < 1e-9 and abs(z) < 1e-9 for x, y, z in nodes)
        opposite = sum(abs(y - 1) < 1e-9 and abs(z - 1) < 1e-9 for x, y, z in nodes)
        self.assertGreaterEqual(on_edge, 20)
        self.assertLess(opposite, 5)

    def test_vertex_size_refines_around_that_corner(self):
        def near_corner(nodes):
            return sum(0 < x * x + y * y + z * z < 0.3**2 for x, y, z in nodes)

        before = near_corner(self.mesh_box_with_size())
        write_point(self.geo("size_1_1.brep"), (0, 0, 0))
        self.assertGreater(near_corner(self.mesh_box_with_size("size_1_1.brep")), before)

    def test_size_face_off_the_bodies_fails(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("size_1_1.brep"), 0, 0, 1.5, 1, 1)  # floats above the box
        r = self.run_job(
            [self.vol(1, "Copper_Box", "vol_1.brep")],
            sizes=[{"name": "Fine", "size": 0.1, "files": ["geometry/size_1_1.brep"]}],
        )
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("Fine", last)

    def refine(self, files=(), whole=(), fine=0.05, coarse=0.5, growth=0.3, fine_distance=0.0, limit_to=()):
        return {
            "name": "Near",
            "files": ["geometry/" + f for f in files],
            "whole": list(whole),
            "fine": fine,
            "fine_distance": fine_distance,
            "coarse": coarse,
            "growth": growth,
            "limit_to": list(limit_to),
        }

    def two_boxes_refined(self, entry, face=False):
        """Boxes 1 (x 0..1) and 2 (x 1..2) meshed at size 0.5 with one refine entry (face: the shared face x = 1 is
        its refine_1_1_1.brep). Returns the node coordinates."""
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        if face:
            write_rect_x(self.geo("refine_1_1_1.brep"), 1, 0, 0, 1, 1)
        vols = [self.vol(1, "Box1", "vol_1.brep"), self.vol(2, "Box2", "vol_2.brep")]
        r = self.run_job(vols, extra={"refine": [entry]})
        self.assertEqual(r.returncode, 0, r.stderr)
        return read_nodes(os.path.join(self.dir, "pre_geom.msh"))

    def test_refine_near_an_edge_grades_away_from_it(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_line(self.geo("refine_1_1_1.brep"), (0, 0, 0), (1, 0, 0))
        r = self.run_job([self.vol(1, "Box", "vol_1.brep")], extra={"refine": [self.refine(["refine_1_1_1.brep"])]})
        self.assertEqual(r.returncode, 0, r.stderr)
        nodes = read_nodes(os.path.join(self.dir, "pre_geom.msh"))
        near = sum(math.hypot(y, z) < 0.1 for x, y, z in nodes)
        far = sum(math.hypot(y - 1, z - 1) < 0.1 for x, y, z in nodes)
        self.assertGreater(near, 10 * max(far, 1))

    def test_refine_near_does_not_cap_sizes_beyond_its_reach(self):
        def near_far_face(extra):  # size 0.2: at 0.5 only about 12 nodes are there, too few to compare
            r = self.run_job([self.vol(1, "Box", "vol_1.brep", size=0.2)], extra=extra)
            self.assertEqual(r.returncode, 0, r.stderr)
            return sum(x > 0.75 for x, y, z in read_nodes(os.path.join(self.dir, "pre_geom.msh")))

        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_line(self.geo("refine_1_1_1.brep"), (0, 0, 0), (0, 1, 0))  # on x = 0, reach 0.3
        plain = near_far_face(None)
        refined = near_far_face({"refine": [self.refine(["refine_1_1_1.brep"], coarse=0.1)]})
        self.assertLess(abs(refined - plain), 0.2 * plain, (plain, refined))

    def limited_to_box_1(self):
        # a fine layer of 0.1: with none, box 1 has only about 67 nodes in 0.9 < x < 1 against 15 (box 2's side faces
        # by the fine edges), the size grows that fast
        return self.refine(["refine_1_1_1.brep"], fine_distance=0.1, limit_to=[1])

    def test_limit_to_keeps_the_refinement_in_that_body(self):
        nodes = self.two_boxes_refined(self.limited_to_box_1(), face=True)
        inside = sum(0.9 < x < 1 for x, y, z in nodes)
        outside = sum(1 < x < 1.1 for x, y, z in nodes)
        self.assertGreater(inside, 5 * outside, (inside, outside))

    def test_limit_to_keeps_the_body_boundary_sized(self):
        nodes = self.two_boxes_refined(self.limited_to_box_1(), face=True)
        on_edge = sum(x == 0 and z == 0 for x, y, z in nodes)  # the edge (0,0,0)-(0,1,0) of box 1
        self.assertGreaterEqual(on_edge, 1 / 0.5 + 1)

    def test_limit_to_a_body_not_in_the_mesh_notes_and_refines_nothing(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_line(self.geo("refine_1_1_1.brep"), (0, 0, 0), (1, 0, 0))
        entry = self.refine(["refine_1_1_1.brep"], limit_to=[7])  # MAT_ID 7 has no volumes
        r = self.run_job([self.vol(1, "Box", "vol_1.brep")], extra={"refine": [entry]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Refine Near Near: its Limit to bodies are not in this mesh; it refines nothing", r.stderr)
        nodes = read_nodes(os.path.join(self.dir, "pre_geom.msh"))
        self.assertLess(sum(math.hypot(y, z) < 0.1 for x, y, z in nodes), 10, "no refinement anywhere")

    def test_whole_body_pick_refines_only_shared_faces(self):
        nodes = self.two_boxes_refined(self.refine(whole=[1]))
        shared = sum(abs(x - 1) < 0.1 for x, y, z in nodes)
        outer = sum(x < 0.1 for x, y, z in nodes)
        self.assertGreater(shared, 5 * outer, (shared, outer))

    def test_whole_body_pick_with_no_shared_face_notes_and_meshes(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Box", "vol_1.brep")], extra={"refine": [self.refine(whole=[1])]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("has no face shared with another region", r.stderr)

    def test_refine_file_off_the_bodies_fails(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_line(self.geo("refine_1_1_1.brep"), (0, 0, 1.5), (1, 0, 1.5))  # floats above the box
        r = self.run_job([self.vol(1, "Box", "vol_1.brep")], extra={"refine": [self.refine(["refine_1_1_1.brep"])]})
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("refine near Near", last)

    def box_tets(self, options=None):
        """Mesh a unit box at size 0.5. Returns {element type: count} of the 3D elements."""
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], options=options)
        self.assertEqual(r.returncode, 0, r.stderr)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(os.path.join(self.dir, "pre_geom.msh"))
            types, tags, _ = gmsh.model.mesh.getElements(3)
        finally:
            gmsh.finalize()
        return {int(t): len(x) for t, x in zip(types, tags)}

    def test_options_are_applied(self):
        plain = self.box_tets()
        finer = self.box_tets({"Mesh.Algorithm3D": 10, "Mesh.MeshSizeFactor": 0.5, "Mesh.OptimizeNetgen": 1})
        self.assertEqual(list(finer), [4], "only first-order tetrahedra")
        self.assertGreater(finer[4], 3 * plain[4])  # 100 -> about 400 tetrahedra

    def test_max_size_option_caps_the_body_size(self):
        plain = self.box_tets()
        capped = self.box_tets({"Mesh.MeshSizeMax": 0.2})
        self.assertGreater(capped[4], 4 * plain[4])

    def test_unknown_option_fails_cleanly(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], options={"Mesh.NoSuchOption": 1})
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("NoSuchOption", last)

    def test_mesh_goes_to_mesh_file_and_unv_beside_the_job(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = os.path.join(self.dir, "run dir", "pre_geom.msh")
        os.mkdir(os.path.dirname(target))
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], mesh_file=target)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(target))
        self.assertTrue(os.path.isfile(os.path.join(self.dir, "mesh.unv")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "pre_geom.msh")))
        self.assertIn(f"Wrote {target}", r.stdout)

    def write_old_mesh(self):
        path = os.path.join(self.dir, "pre_geom.msh")
        with open(path, "w", encoding="ascii") as fh:
            fh.write("old")
        return path

    def read_text(self, path):
        with open(path, encoding="ascii") as fh:
            return fh.read()

    def test_existing_mesh_is_replaced(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = self.write_old_mesh()
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.read_text(target).startswith("$MeshFormat"))

    def test_failed_run_keeps_the_existing_mesh(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 0.5, 0, 0, 1, 1, 1)  # overlaps vol_1
        target = self.write_old_mesh()
        r = self.run_job([self.vol(1, "A_Box", "vol_1.brep"), self.vol(2, "B_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.read_text(target), "old")

    def test_read_only_mesh_fails_cleanly_and_stays(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = self.write_old_mesh()
        os.chmod(target, stat.S_IREAD)
        try:
            r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        finally:
            os.chmod(target, stat.S_IREAD | stat.S_IWRITE)  # let the temporary folder be deleted
        self.assertCannotReplace(r, target)

    def test_mesh_open_in_another_program_fails_cleanly_and_stays(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = self.write_old_mesh()
        with open(target, encoding="ascii"):  # a viewer holding pre_geom.msh open
            r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertCannotReplace(r, target)

    def assertCannotReplace(self, r, target):
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertEqual(last, f"ERROR: Could not replace {target}: it is read-only or open in another program.")
        self.assertEqual(self.read_text(target), "old")

    def test_overlapping_boxes_fail(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 0.5, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "A_Box", "vol_1.brep"), self.vol(2, "B_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("overlap", last)

    def test_offset_face_fails_merge_check(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("surf_1001_1.brep"), 0, 0, 1.5, 1, 1)  # floats above the box
        r = self.run_job(
            [self.vol(1, "Copper_Box", "vol_1.brep")],
            [{"smat_id": 1001, "name": "Terminal_In_Box", "mat_id": 1, "files": ["geometry/surf_1001_1.brep"]}],
        )
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("Terminal_In_Box", last)

    def test_missing_geometry_file_fails_cleanly(self):
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stderr.strip().splitlines()[-1].startswith("ERROR:"))

    def test_single_box_without_faces(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(gmsh.model.getPhysicalName(3, 1), "Copper_Box")

    def test_excitation_on_face_shared_by_two_bodies(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        gmsh.initialize()  # the x = 1 interface, as a face of box 1
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
            gmsh.model.occ.synchronize()
            face = next(
                t
                for _, t in gmsh.model.getBoundary([(3, 1)], oriented=False)
                if abs(gmsh.model.occ.getCenterOfMass(2, t)[0] - 1) < 1e-9
            )
            gmsh.model.occ.remove([(3, 1)])
            gmsh.model.occ.synchronize()
            gmsh.model.occ.remove([(2, t) for _, t in gmsh.model.getEntities(2) if t != face], recursive=True)
            gmsh.model.occ.synchronize()
            gmsh.write(self.geo("surf_1001_1.brep"))
        finally:
            gmsh.finalize()
        r = self.run_job(
            [self.vol(1, "Coil_A", "vol_1.brep"), self.vol(2, "Lead_B", "vol_2.brep")],
            [{"smat_id": 1001, "name": "Terminal_A", "mat_id": 1, "files": ["geometry/surf_1001_1.brep"]}],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        _, coords = gmsh.model.mesh.getNodesForPhysicalGroup(2, 1001)
        self.assertTrue(len(coords) > 0)
        for x in coords[0::3]:
            self.assertAlmostEqual(x, 1.0, places=6)

    def test_structured_box_with_recombine_has_only_hexahedra(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], transfinite=self.structured_box(), recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})

    def test_structured_box_without_recombine_has_six_tetrahedra_per_cell(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], transfinite=self.structured_box())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Tetrahedron 4": 162})

    def test_structured_box_next_to_unstructured_box_gets_pyramids(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep", size=0.3)],
            options={"Mesh.Algorithm3D": 1},
            transfinite=self.structured_box(),
            recombine=[1],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertIn("Pyramid 5", self.element_counts(2))

    def three_boxes(self):
        for i, x in enumerate((0, 1, 2), 1):
            write_box(self.geo(f"vol_{i}.brep"), x, 0, 0, 1, 1, 1)
        return [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep"), self.vol(3, "Coil", "vol_3.brep")]

    def test_faces_between_two_tet_bodies_stay_triangles_with_a_note(self):
        r = self.run_job(
            self.three_boxes(),
            options={"Mesh.Algorithm3D": 1},
            transfinite=self.structured_box(),
            recombine=[1, 2, 3],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: recombine: faces between Air and Coil stay triangles", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertIn("Pyramid 5", self.element_counts(2))
        self.assertIn("Pyramid 5", self.element_counts(3))  # Coil's outside faces are quads

    def test_only_the_structured_body_chosen_next_to_two_tet_bodies(self):
        r = self.run_job(self.three_boxes(), transfinite=self.structured_box(), recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("NOTE: recombine", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertEqual(set(self.element_counts(3)), {"Tetrahedron 4"})

    def test_unstructured_box_alone_gets_pyramids(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Air", "vol_1.brep", 0.3)], recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertIn("Pyramid 5", self.element_counts(1))

    def test_body_inside_a_tet_body_stays_tetrahedra_with_a_note(self):
        # Coil is the middle cube of a 3x3x3 block; six Air slabs touch each of its faces (bodies cannot overlap)
        slabs = [(0, 0, 0, 3, 3, 1), (0, 0, 2, 3, 3, 1), (0, 0, 1, 1, 3, 1), (2, 0, 1, 1, 3, 1)]
        slabs += [(1, 0, 1, 1, 1, 1), (1, 2, 1, 1, 1, 1)]
        vols = []
        for i, box in enumerate(slabs, 1):
            write_box(self.geo(f"vol_{i}.brep"), *box)
            vols.append(self.vol(i, f"Air{i}", f"vol_{i}.brep"))
        write_box(self.geo("vol_7.brep"), 1, 1, 1, 1, 1, 1)
        vols.append(self.vol(7, "Coil", "vol_7.brep", 0.3))
        r = self.run_job(vols, recombine=[7])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: recombine: Coil has no face that can be recombined", r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(7)), {"Tetrahedron 4"})

    def test_structured_body_not_chosen_next_to_a_chosen_structured_body_is_an_error(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        tf = self.structured_boxes(("Core", 1, 0), ("Yoke", 2, 1))
        vols = [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Yoke", "vol_2.brep")]
        r = self.run_job(vols, transfinite=tf, recombine=[1])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR: recombine: Yoke is structured"), last)
        self.assertIn("Core", last)

    def test_quads_next_to_tets_need_delaunay(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep")],
            options={"Mesh.Algorithm3D": 10},
            transfinite=self.structured_box(),
            recombine=[1],
        )
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("Delaunay", last)
        self.assertIn("Core", last)
        self.assertIn("Air", last)

    def full_quad_core_and_air(self, n):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        return self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep", size=0.3)],
            options={"Mesh.RecombinationAlgorithm": 3},
            transfinite=self.structured_box(n),
            recombine=[1, 2],
        )

    def test_full_quad_with_an_odd_transfinite_count_next_to_a_recombined_body_is_an_error(self):
        r = self.full_quad_core_and_air(3)
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR: recombine: full-quad"), last)
        self.assertIn("Air", last)
        self.assertIn("tedge_1", last)

    def test_full_quad_with_an_even_transfinite_count_meshes(self):
        r = self.full_quad_core_and_air(4)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 64})

    def test_structured_and_two_unstructured_bodies_all_chosen(self):
        r = self.run_job(
            self.three_boxes(),
            options={"Mesh.Algorithm3D": 1},
            transfinite=self.structured_box(),
            recombine=[1, 2],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: recombine: faces between Air and Coil stay triangles", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertEqual(set(self.element_counts(3)), {"Tetrahedron 4"})

    def test_structured_box_alone_meshes_with_hxt(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep")],
            options={"Mesh.Algorithm3D": 10},
            transfinite=self.structured_box(),
            recombine=[1],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})

    def test_structured_box_edge_without_item_is_an_error(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        tf = self.structured_box()
        tf["edges"] = [self.edge_item("tedge_1", box_lines()[:11], 3)]
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], transfinite=tf)
        self.assertEqual(r.returncode, 1)
        self.assertIn("without Transfinite Edges", r.stderr.strip().splitlines()[-1])

    def test_structured_volume_with_seven_faces_is_an_error(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0.25, 0.25, 1, 0.5, 0.5)  # touches the middle of Core's x = 1 face
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep")], transfinite=self.structured_box()
        )
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR:"), last)
        self.assertIn("7 faces, needs 5 or 6", last)

    def test_structured_sphere_pole_needs_no_transfinite_edge(self):
        outer, inner = 1.5, 0.75  # a spherical face has its pole on a corner: a zero-length edge Gmsh does not need
        write_sphere_shell(self.geo("vol_1.brep"), outer, inner)
        axes = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        rays = [(tuple(inner * c for c in d), tuple(outer * c for c in d)) for d in axes]
        n = 0
        for radius in (inner, outer):
            for k in range(3):
                n += 1
                p, q = (tuple(radius * c for c in axes[(k + i) % 3]) for i in range(2))
                write_arc(self.geo(f"tedge_2_{n}.brep"), p, q, (0, 0, 0))
        tf = {
            "bodies": [{"name": "Core", "mat_id": 1, "corner_files": []}],
            "edges": [
                self.edge_item("tedge_1", rays, 3),
                {
                    "name": "tedge_2",
                    "nodes": 4,
                    "distribution": "Uniform",
                    "coef": 1.0,
                    "files": [f"geometry/tedge_2_{k}.brep" for k in range(1, n + 1)],
                },
            ],
        }
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], transfinite=tf, recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_folder_with_spaces_and_persian_letters(self):
        self.dir = os.path.join(self.tmp.name, "my model \u0645\u062f\u0644")
        os.makedirs(os.path.join(self.dir, "geometry"))
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "pre_geom.msh")))

    def test_air_fills_around_box(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("air.brep"), -1, -1, -1, 3, 3, 3)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.8}
        r = self.run_job([self.vol(1, "Body", "vol_1.brep", size=0.8)], air=air)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("MAT_ID       2  Air", r.stdout)
        self.open_msh()
        groups = {t: gmsh.model.getPhysicalName(3, t) for _, t in gmsh.model.getPhysicalGroups(3)}
        self.assertEqual(groups, {1: "Body", 2: "Air"})
        volume = 0.0
        for e in gmsh.model.getEntitiesForPhysicalGroup(3, 2):
            volume += sum(gmsh.model.mesh.getElementQualities(gmsh.model.mesh.getElements(3, e)[1][0], "volume"))
        self.assertAlmostEqual(volume, 27 - 1, delta=1e-6)

    def test_air_covered_by_bodies_fails_cleanly(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("air.brep"), 0, 0, 0, 1, 1, 1)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.8}
        r = self.run_job([self.vol(1, "Body", "vol_1.brep")], air=air)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stderr.strip().splitlines()[-1], "ERROR: the air region is fully covered by bodies")

    def test_recombined_body_inside_air_meshes(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("air.brep"), -1, -1, -1, 3, 3, 3)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.8}
        r = self.run_job([self.vol(1, "Body", "vol_1.brep", size=0.8)], recombine=[1], air=air)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("faces between Air and Body stay triangles", r.stderr)

    def test_face_size_on_the_air_merges(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("air.brep"), -1, -1, -1, 3, 3, 3)
        write_rect(self.geo("size_1.brep"), -1, -1, -1, 3, 3)  # the air's bottom face
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.8}
        sizes = [{"name": "Fine", "size": 0.4, "files": ["geometry/size_1.brep"]}]
        r = self.run_job([self.vol(1, "Body", "vol_1.brep", size=0.8)], sizes=sizes, air=air)
        self.assertEqual(r.returncode, 0, r.stderr)

    # ---- Air Grading. The numbers are the spike's (mean edge in bands 0-3 / 3-10 / 10-25 / 25-50 / 50-80 mm from the
    # block), block size 2, air size 20, growth 60

    def graded_block(
        self, grading=None, size=2.0, block=(-10, -10, -5, 20, 20, 10), box=(-100, -100, -100, 200, 200, 200)
    ):
        """The block (MAT_ID 1, mesh size `size`) in an air box (MAT_ID 2, size 20), with one Air Grading entry if
        given. Returns the tetrahedra."""
        write_box(self.geo("vol_1.brep"), *block)
        write_box(self.geo("air.brep"), *box)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 20.0}
        extra = {"air_grading": [grading]} if grading else None
        r = self.run_job([self.vol(1, "Block", "vol_1.brep", size=size)], air=air, extra=extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        return simplices(os.path.join(self.dir, "pre_geom.msh"), 3)

    def test_air_grading_grows_from_the_block(self):
        # today 2.48 / 9.20 / 18.6 / 27.4 / 28.2, graded 2.61 / 4.86 / 8.95 / 16.7 / 25.8
        half = (10, 10, 5)
        today = band_edge(self.graded_block(), half, 3, 10)
        graded = self.graded_block(air_grading())
        self.assertLess(band_edge(graded, half, 3, 10), 0.7 * today, today)
        self.assertGreater(band_edge(graded, half, 50, 80), 0.6 * 20)

    def test_far_size_larger_than_the_air_size(self):
        # far 40: 2.69 / 6.24 / 14.6 / 30.1 / 48.8, 7.8k elements against today's 9.2k
        today = len(self.graded_block())
        graded = self.graded_block(air_grading(far=40.0))
        self.assertLess(len(graded), today)
        self.assertGreater(band_edge(graded, (10, 10, 5), 50, 80), 30)

    def test_far_size_does_not_coarsen_the_body_surface(self):
        # block size 30 in air size 20: the block's faces keep the smaller size, 20, as today; far 40 must not make
        # them 30. An 80 mm block: on the spike's 20 mm one an edge cannot get much longer than 20 either way. Mean
        # edge of its faces 18.65 today and graded, 24.2 when its faces lose the air's size
        self.graded_block(
            air_grading(far=40.0), size=30.0, block=(-40, -40, -40, 80, 80, 80), box=(-150,) * 3 + (300,) * 3
        )
        block = simplices(os.path.join(self.dir, "pre_geom.msh"), 3, group=1)
        edges = [math.dist(f[a], f[b]) for f in facets(block, lambda p: True) for a, b in ((0, 1), (1, 2), (0, 2))]
        self.assertLessEqual(sum(edges) / len(edges), 22)

    def test_air_face_on_the_domain_boundary_grades_3d(self):
        # a half model, the block on the plane z = 0; the air's triangles on that plane: today 2.30 / 6.17 / 18.0 /
        # 19.7, graded 2.19 / 3.54 / 6.73 / 12.2 / 19.0 (without the outer faces in the Restrict and the inner faces'
        # curves in the Extend the plane's mesh jumps to the far size). Taken here from the tetrahedra's faces (the
        # first edge of each differs): band 3-10 today 9.04, graded 3.41
        def plane(grading):
            tets = self.graded_block(grading, block=(-10, -10, 0, 20, 20, 5), box=(-100, -100, 0, 200, 200, 100))
            return facets(tets, lambda p: abs(p[2]) < 1e-9)

        half = (10, 10, 0)
        today = band_edge(plane(None), half, 3, 10)
        self.assertLess(band_edge(plane(air_grading()), half, 3, 10), 0.7 * today, today)

    # ---- Skin Layer: an aluminium block 40 x 40 x 20 (MAT_ID 1), skin depth 2.69, in an air box of 200 at size 20

    def skin_block(self, entry=None, size=8.0):
        """The block at mesh size `size` in the air box, with one Skin Layer entry if given. Returns its tetrahedra."""
        write_box(self.geo("vol_1.brep"), -20, -20, -10, 40, 40, 20)
        write_box(self.geo("air.brep"), -100, -100, -100, 200, 200, 200)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 20.0}
        extra = {"skin": [entry]} if entry else None
        r = self.run_job([self.vol(1, "Block", "vol_1.brep", size=size)], air=air, extra=extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        return simplices(os.path.join(self.dir, "pre_geom.msh"), 3, group=1)

    def test_skin_grades_the_block_3d(self):
        # mean edge 0-δ / δ-2δ / 2δ-3δ / beyond: 1.72 / 2.56 / 4.97 / 6.58, 35.9k tetrahedra; a uniform 1.35 block 1.71 to
        # 1.87 and 60.9k (the first edge of a tetrahedron is longer than its size)
        d = 2.69
        block = self.skin_block(skin(depth=d))

        def depth(c):
            return min(20 - abs(c[0]), 20 - abs(c[1]), 10 - abs(c[2]))

        self.assertLess(depth_edge(block, depth, 0, d), 0.75 * d)
        self.assertGreater(depth_edge(block, depth, 3 * d), 0.6 * 8)
        self.assertLess(len(block), len(self.skin_block(size=d / 2)))

    def test_empty_swept_key_is_unchanged(self):
        self.skin_block(skin(depth=2.69))
        before = read_nodes(os.path.join(self.dir, "pre_geom.msh"))
        write_box(self.geo("air.brep"), -100, -100, -100, 200, 200, 200)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 20.0}
        extra = {"skin": [skin(depth=2.69)], "swept": []}
        r = self.run_job([self.vol(1, "Block", "vol_1.brep", size=8.0)], air=air, extra=extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(read_nodes(os.path.join(self.dir, "pre_geom.msh")), before)

    # ---- Swept Body: a bar 10 x 4 x 40 (MAT_ID 1) along Z, its profile the end face at z = -20, in an air box
    # 60 x 60 x 100 at size 6 (MAT_ID 2)

    AIR_BOX = (-30, -30, -50, 60, 60, 100)

    def swept_bar(
        self, entry=None, box=AIR_BOX, volumes=(), surfaces=(), sizes=(), recombine=(1,), options=None, skins=()
    ):
        write_box(self.geo("vol_1.brep"), -5, -2, -20, 10, 4, 40)
        write_rect(self.geo("sweep_1_1.brep"), -5, -2, -20, 10, 4)
        write_box(self.geo("air.brep"), *box)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 6.0}
        extra = {"swept": [entry or swept("sweep_1_1.brep")]}
        if skins:
            extra["skin"] = list(skins)
        vols = [self.vol(1, "Bar", "vol_1.brep", size=2.0), *volumes]
        r = self.run_job(vols, surfaces, sizes, options, recombine=list(recombine), air=air, extra=extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def msh(self):
        return os.path.join(self.dir, "pre_geom.msh")

    def bar_nodes(self):
        return gmsh.model.mesh.getNodesForPhysicalGroup(3, 1)[1].reshape(-1, 3)

    def steps(self, axis):
        """The steps between the bar's node coordinates along axis (0, 1, 2)."""
        values = sorted({round(float(x), 6) for x in self.bar_nodes()[:, axis]})
        return [b - a for a, b in zip(values, values[1:])]

    def test_swept_bar_meshes(self):
        r = self.swept_bar(swept("sweep_1_1.brep", recombine=False), recombine=())  # four sides: a grid, hexahedra
        self.open_msh()
        self.assertIn("Swept           Bar", r.stdout)
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8"})
        self.assertEqual(len(self.steps(2)), 10)
        self.assertEqual(inner_free_faces(self.AIR_BOX), [])

    def test_swept_size_factor_halves_the_steps(self):
        self.swept_bar(swept("sweep_1_1.brep", recombine=False), recombine=(), options={"Mesh.MeshSizeFactor": 0.5})
        self.open_msh()
        self.assertEqual(len(self.steps(2)), 20)
        self.assertEqual(inner_free_faces(self.AIR_BOX), [])

    def test_swept_bar_sets_delaunay(self):
        r = self.swept_bar(options={"Mesh.Algorithm3D": 10})  # HXT refuses quads on the air's boundary
        self.assertIn("the 3D algorithm is set to Delaunay so the air can meet the swept bodies' quad faces", r.stderr)
        self.open_msh()
        self.assertEqual(inner_free_faces(self.AIR_BOX), [])

    def test_swept_bar_with_skin(self):
        self.swept_bar(swept("sweep_1_1.brep", skin={"depth": 1.0, "per_depth": 2.0, "layer": 3.0}))
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8"})
        for axis in (0, 1):  # across each side
            steps = self.steps(axis)
            self.assertAlmostEqual(steps[0], 0.5, delta=0.125)
            self.assertAlmostEqual(steps[-1], 0.5, delta=0.125)
        z = self.steps(2)  # both ends are real surface in the air
        self.assertAlmostEqual(z[0], 0.5, delta=0.01)
        self.assertAlmostEqual(z[-1], 0.5, delta=0.01)
        self.assertLessEqual(max(z), 4.0 + 1e-9)
        self.assertEqual(inner_free_faces(self.AIR_BOX), [])

    def test_swept_round_wire_is_conformal(self):
        write_cylinder_and_end(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"), 0.45, -10, 20)
        write_box(self.geo("air.brep"), -3, -3, -15, 6, 6, 30)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.6}
        wire = swept("sweep_1_1.brep", name="Wire", path_size=0.6, section_size=0.15, recombine=False, advance=20.0)
        wire["skin"] = {"depth": 0.2, "per_depth": 2.0, "layer": 2.0}  # 3 skin depths are more than the radius
        extra = {"swept": [wire]}
        r = self.run_job([self.vol(1, "Wire", "vol_1.brep", size=0.15)], air=air, extra=extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8", "Prism 6"})
        self.assertEqual(inner_free_faces((-3, -3, -15, 6, 6, 30)), [])

    def bar_on_block(self, skins=()):
        """The bar with a skin, its profile's end on a 30 x 30 x 10 block (MAT_ID 3, size 3). Returns the steps along
        the bar."""
        write_box(self.geo("vol_3.brep"), -15, -15, -30, 30, 30, 10)
        skin_ = {"depth": 1.0, "per_depth": 2.0, "layer": 3.0}
        block = self.vol(3, "Block", "vol_3.brep", 3.0)
        self.swept_bar(swept("sweep_1_1.brep", skin=skin_), volumes=[block], skins=skins)
        self.open_msh()
        return self.steps(2)

    def test_swept_bar_end_on_a_terminal(self):
        z = self.bar_on_block([skin(mat_ids=(3,), depth=1.0)])  # a terminal: a conductor with its own skin
        self.assertGreater(z[0], 0.8 * 4.0)  # the profile's end lies on the terminal: no grading
        self.assertLessEqual(z[0], 4.0 + 1e-9)
        self.assertAlmostEqual(z[-1], 0.5, delta=0.01)  # the free end in the air
        self.assertEqual(set(self.element_counts(3)), {"Tetrahedron 4", "Pyramid 5"})  # pyramids on the quads
        self.assertEqual(inner_free_faces(self.AIR_BOX), [])

    def test_swept_bar_end_on_iron_is_graded(self):
        z = self.bar_on_block()  # a block without a skin (iron): real surface for the bar's skin
        self.assertAlmostEqual(z[0], 0.5, delta=0.01)
        self.assertAlmostEqual(z[-1], 0.5, delta=0.01)
        self.assertEqual(inner_free_faces(self.AIR_BOX), [])

    def test_swept_tight_air_is_meshed_again(self):
        # 1 mm of air around the bar at size 6: the pushed-out pyramids cut the air's faces ("PLC Error"); meshing
        # again in the same model left the air with no elements and exit code 0. Now gmsh starts afresh without that
        write_box(self.geo("vol_1.brep"), -5, -2, -20, 10, 4, 40)
        write_rect(self.geo("sweep_1_1.brep"), -5, -2, -20, 10, 4)
        box = (-6, -3, -21, 12, 6, 42)
        write_box(self.geo("air.brep"), *box)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 6.0}
        bar = swept("sweep_1_1.brep", recombine=False, skin={"depth": 1.0, "per_depth": 2.0, "layer": 3.0})
        r = self.run_job([self.vol(1, "Bar", "vol_1.brep", size=2.0)], air=air, extra={"swept": [bar]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("gmsh could not optimise the pyramids", r.stderr)
        self.open_msh()
        self.assertIn("Tetrahedron 4", self.element_counts(2))
        self.assertEqual(inner_free_faces(box), [])

    def test_swept_bar_cut_end_is_not_graded(self):
        box = (-30, -30, -20, 60, 60, 70)  # the bar's end at z = -20 on the air box's outer face
        self.swept_bar(swept("sweep_1_1.brep", skin={"depth": 1.0, "per_depth": 2.0, "layer": 3.0}), box=box)
        self.open_msh()
        z = self.steps(2)
        self.assertGreater(z[0], 0.8 * 4.0)
        self.assertAlmostEqual(z[-1], 0.5, delta=0.01)
        self.assertEqual(inner_free_faces(box), [])

    def test_swept_ignores_size_fields(self):
        self.swept_bar()
        plain = group_cells(self.msh(), 1)
        write_rect_x(self.geo("size_1.brep"), 5, -2, -20, 4, 40)  # the bar's side x = 5
        size = {"name": "Fine", "size": 0.5, "files": ["geometry/size_1.brep"]}
        self.swept_bar(sizes=[size])
        self.assertEqual(group_cells(self.msh(), 1), plain)

    def test_swept_excitation_surface(self):
        write_rect(self.geo("surf_10_1.brep"), -5, -2, 20, 10, 4)  # the far end face
        surface = {"smat_id": 10, "name": "In", "mat_id": 1, "files": ["geometry/surf_10_1.brep"]}
        self.swept_bar(surfaces=[surface])
        self.open_msh()
        hexes = self.element_counts(1)["Hexahedron 8"]
        self.assertEqual(self.element_counts(10, dim=2), {"Quadrilateral 4": hexes // len(self.steps(2))})
        self.assertEqual(inner_free_faces(self.AIR_BOX), [])  # the air is meshed

    def air_min_sicn(self):
        tags = [t for e in gmsh.model.getEntitiesForPhysicalGroup(3, 2) for t in gmsh.model.mesh.getElements(3, e)[1]]
        return min(float(gmsh.model.mesh.getElementQualities(t, "minSICN").min()) for t in tags if len(t))

    def test_swept_whole_face_split_by_the_fragment_names_the_body(self):
        # a block on half of the bar's far end face splits it in the fragment; the excitation file is that whole face
        write_box(self.geo("vol_1.brep"), -5, -2, -20, 10, 4, 40)
        write_rect(self.geo("sweep_1_1.brep"), -5, -2, -20, 10, 4)
        write_box(self.geo("vol_3.brep"), 0, -2, 20, 10, 4, 5)
        write_rect(self.geo("surf_10_1.brep"), -5, -2, 20, 10, 4)
        write_box(self.geo("air.brep"), *self.AIR_BOX)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 6.0}
        surface = {"smat_id": 10, "name": "In", "mat_id": 1, "files": ["geometry/surf_10_1.brep"]}
        vols = [self.vol(1, "Bar", "vol_1.brep", size=2.0), self.vol(3, "Block", "vol_3.brep", size=2.0)]
        r = self.run_job(vols, [surface], recombine=[1], air=air, extra={"swept": [swept("sweep_1_1.brep")]})
        self.assertEqual(r.returncode, 1)
        self.assertIn(
            "Swept Body Bar: surf_10_1.brep is a whole face of it, but the fragment split that face; check what"
            " touches it",
            r.stderr,
        )

    def test_swept_end_face_excitation_keeps_the_pyramids(self):
        # fragmented in, a whole end face turned gmsh's normals of the bar's other faces inward: the pushed-out
        # pyramids then always failed ("PLC Error") and the fallback left slivers in the air. It now goes on the bar's
        # own end face, not into the fragment
        self.swept_bar()
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(self.msh())
            plain = self.air_min_sicn()
        finally:
            gmsh.finalize()
        write_rect(self.geo("surf_10_1.brep"), -5, -2, 20, 10, 4)  # the far end face
        surface = {"smat_id": 10, "name": "In", "mat_id": 1, "files": ["geometry/surf_10_1.brep"]}
        r = self.swept_bar(surfaces=[surface])
        self.assertNotIn("could not optimise the pyramids", r.stderr)
        self.open_msh()
        nodes = gmsh.model.mesh.getNodesForPhysicalGroup(2, 10)[1].reshape(-1, 3)
        self.assertTrue(len(nodes))
        self.assertTrue(all(abs(z - 20) < 1e-9 for z in nodes[:, 2]))
        self.assertGreaterEqual(self.air_min_sicn(), 0.5 * plain)

    def test_straight_sweep_unchanged_by_stage2(self):
        # the bar of test_swept_bar_with_skin: its node coordinates as at Stage 1 (7b39a49)
        self.swept_bar(swept("sweep_1_1.brep", skin={"depth": 1.0, "per_depth": 2.0, "layer": 3.0}))
        self.open_msh()
        rows = sorted(tuple(round(float(x), 6) + 0.0 for x in p) for p in self.bar_nodes())
        self.assertEqual(
            hashlib.sha256(repr(rows).encode()).hexdigest(),
            "9c7657b4f37d066c2acbbb8ed32a08f52fff2efbfdb69785144491c26aded40e",
        )

    def test_ordinary_swept_unchanged_by_stage4(self):
        # SW-01's busbar 10 x 4 x 100 (size 4, Skin Layer 1 kHz in copper, path size 4) in its 30 mm Padding Box: its
        # node coordinates as at b09834a, before Stage 4's mesher
        write_box(self.geo("vol_1.brep"), -5, -2, 0, 10, 4, 100)
        write_rect(self.geo("sweep_1_1.brep"), -5, -2, 0, 10, 4)
        box = (-35, -32, -30, 70, 64, 160)
        write_box(self.geo("air.brep"), *box)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 4.0}
        depth = 1000 * math.sqrt(2 / (2 * math.pi * 1000 * 4e-7 * math.pi * 5.8e7))
        bar = swept("sweep_1_1.brep", name="Busbar", section_size=4.0, recombine=False, advance=100.0)
        bar["skin"] = {"depth": depth, "per_depth": 2.0, "layer": 3.0}
        r = self.run_job([self.vol(1, "Busbar", "vol_1.brep", size=4.0)], air=air, extra={"swept": [bar]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8"})
        rows = sorted(tuple(round(float(x), 6) + 0.0 for x in p) for p in self.bar_nodes())
        self.assertEqual(
            hashlib.sha256(repr(rows).encode()).hexdigest(),
            "c686b1c71dd0abdd647c96c593cf6efd91906815151de1392dc37d7e55b75c6e",
        )

    # ---- revolved Swept Bodies about Z in an air box 120 x 120 x 60 at size 8 (MAT_ID 2)

    TURN_BOX = (-60, -60, -30, 120, 120, 60)

    def swept_turn_job(self, entry):
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 8.0}
        write_box(self.geo("air.brep"), *self.TURN_BOX)
        r = self.run_job([self.vol(1, entry["name"], "vol_1.brep", size=2.0)], air=air, extra={"swept": [entry]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        return r

    def angles(self):
        """The bar's distinct node angles about Z, in degrees from 0 to 360, sorted."""
        p = self.bar_nodes()
        return sorted({round(math.degrees(math.atan2(y, x)), 6) % 360 for x, y in p[:, :2]})

    def test_swept_closed_ring_is_conformal(self):
        write_revolved_rect(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"), 20, 30, -2, 2, 360)
        self.swept_turn_job(swept_turn("sweep_1_1.brep", 360, skin={"depth": 1.0, "per_depth": 2.0, "layer": 3.0}))
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8"})
        self.assertEqual(inner_free_faces(self.TURN_BOX), [])
        angles = self.angles()
        stations = len(angles)
        tags, coords = gmsh.model.mesh.getNodes()[:2]
        at = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
        seam = set()  # the section's quads: the hexahedra's faces in the half-plane y = 0, x > 0
        for e in gmsh.model.getEntitiesForPhysicalGroup(3, 1):
            for nodes in gmsh.model.mesh.getElements(3, e)[2]:
                for k in range(0, len(nodes), 8):
                    for f in FACES_3D[5][1]:
                        q = [int(nodes[k + i]) for i in f]
                        if all(abs(at[n][1]) < 1e-9 and at[n][0] > 0 for n in q):
                            seam.add(tuple(sorted(q)))
        self.assertEqual(self.element_counts(1)["Hexahedron 8"], len(seam) * stations)
        steps = [math.radians(b - a) * 25 for a, b in zip(angles, angles[1:] + [angles[0] + 360])]
        for s in steps:  # rc 25
            self.assertAlmostEqual(s, 4.0, delta=1.0)

    def test_swept_ring_with_two_seams(self):
        # corners at 0 and 180 degrees: 39 equal steps from the cut (rc 25, path size 4) would miss the ones at 180
        write_two_half_rings(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"), 20, 30, -2, 2, 180)
        self.swept_turn_job(swept_turn("sweep_1_1.brep", 360))
        self.assertEqual(inner_free_faces(self.TURN_BOX), [])
        self.assertIn(180.0, self.angles())

    def test_swept_torus(self):
        write_torus(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"), 20, 3)
        self.swept_turn_job(
            swept_turn("sweep_1_1.brep", 360, section_size=1.0, skin={"depth": 0.5, "per_depth": 2.0, "layer": 3.0})
        )
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8", "Prism 6"})
        self.assertEqual(inner_free_faces(self.TURN_BOX), [])

    def test_swept_torus_profile_vertex_elsewhere(self):
        # the profile circle starts at (22.4, 0, 1.8), 37 degrees from where the torus's seam circles cross the profile
        write_torus(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"), 20, 3, start=(0.8, 0, 0.6))
        self.swept_turn_job(
            swept_turn("sweep_1_1.brep", 360, section_size=1.0, skin={"depth": 0.5, "per_depth": 2.0, "layer": 3.0})
        )
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8", "Prism 6"})
        self.assertEqual(inner_free_faces(self.TURN_BOX), [])
        self.assertIn((23.0, 0.0, 0.0), {tuple(round(float(x), 6) + 0.0 for x in p) for p in self.bar_nodes()})

    def test_swept_bend_grades_both_ends(self):
        write_revolved_rect(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"), 20, 30, -2, 2, 90)
        self.swept_turn_job(swept_turn("sweep_1_1.brep", 90, skin={"depth": 1.0, "per_depth": 2.0, "layer": 3.0}))
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8"})
        self.assertEqual(inner_free_faces(self.TURN_BOX), [])
        angles = self.angles()
        self.assertAlmostEqual(angles[0], 0, places=6)
        self.assertAlmostEqual(angles[-1], 90, places=6)
        steps = [math.radians(b - a) * 25 for a, b in zip(angles, angles[1:])]  # at rc 25
        self.assertAlmostEqual(steps[0], 0.5, delta=0.125)
        self.assertAlmostEqual(steps[-1], 0.5, delta=0.125)
        middle = steps[len(steps) // 2]
        self.assertAlmostEqual(middle, 4.0, delta=0.5)
        self.assertLessEqual(max(steps), 4.0 + 1e-6)

    # ---- helical and chained Swept Bodies

    STRAND_BOX = (-3, -3, -5, 6, 6, 25)
    HELIX = {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]}

    def strand_job(self, surfaces=()):
        """litz1's strand: r 0.45 along 1.5 turns of a helix r 1.2, pitch 10, in an air box 6 x 6 x 25 at 0.6. Path size
        0.4, section 0.2: the spike's 0.6 and 0.15 (quads 4 : 1) left gmsh's air mesh "overlapping facets" in about half
        the runs (gmsh's 3D mesh differs from run to run); these met it in 11 of 11."""
        write_box(self.geo("air.brep"), *self.STRAND_BOX)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.6}
        piece = {**self.HELIX, "angle": 540.0, "advance": 15.0}
        wire = swept_chain("sweep_1_1.brep", [piece], name="Wire", path_size=0.4, section_size=0.2)
        wire["skin"] = {"depth": 0.2, "per_depth": 2.0, "layer": 2.0}
        r = self.run_job([self.vol(1, "Wire", "vol_1.brep", size=0.15)], surfaces, air=air, extra={"swept": [wire]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8", "Prism 6"})
        self.assertEqual(inner_free_faces(self.STRAND_BOX), [])
        return r

    def test_swept_helix_strand_is_conformal(self):
        write_helix_pipe(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"), 1.2, 10.0, 1.5, ("disc", 0.45))
        self.strand_job()
        # the seam: the one body curve that runs along the helix, a node at each station
        seam = []
        for _, c in gmsh.model.getEntities(1):
            xyz = gmsh.model.mesh.getNodes(1, c, includeBoundary=True)[1]
            nodes = [xyz[k : k + 3] for k in range(0, len(xyz), 3)]
            z, x = [p[2] for p in nodes], [abs(p[0]) for p in nodes]
            if nodes and max(z) - min(z) > 10 and max(x) < 2:  # not the air box's edges
                seam.append(nodes)
        self.assertEqual(len(seam), 1)
        z_phi = sorted((z, math.atan2(y, x)) for x, y, z in seam[0])  # in z order, unwrapped below
        phi = [p for _, p in z_phi]
        turns = [phi[0]]
        for p in phi[1:]:
            turns.append(turns[-1] + (p - turns[-1] + math.pi) % (2 * math.pi) - math.pi)
        length = math.hypot(1.2 * 3 * math.pi, 15.0)
        steps = [(b - a) * length / (3 * math.pi) for a, b in zip(turns, turns[1:])]
        self.assertAlmostEqual(sum(steps), length, delta=1e-3)
        middle = steps[len(steps) // 4 : -len(steps) // 4]  # past the graded ends
        for s in middle:
            self.assertAlmostEqual(s, 0.4, delta=0.1)

    def test_swept_strand_excitation(self):
        # an excitation face on the far end of a helical strand: the vol file's own end face. One from other geometry
        # (the exact screw image of the profile) does not merge in gmsh's fragment, so the jobwriter exports a rebuilt
        # strand's faces from the rebuild (test_study's test_swept_rebuilt_strand_excitation)
        write_helix_pipe(
            self.geo("vol_1.brep"),
            self.geo("sweep_1_1.brep"),
            1.2,
            10.0,
            1.5,
            ("disc", 0.45),
            end_path=self.geo("surf_10_1.brep"),
        )
        surface = {"smat_id": 10, "name": "In", "mat_id": 1, "files": ["geometry/surf_10_1.brep"]}
        self.strand_job([surface])
        faces = self.element_counts(10, dim=2)
        self.assertTrue(faces)
        self.assertLessEqual(set(faces), {"Quadrilateral 4", "Triangle 3"})

    def test_swept_coil_turn(self):
        write_helix_pipe(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"), 20.0, 6.0, 1.0, ("rect", 2.0, 4.0))
        box = (-26, -26, -6, 52, 52, 18)
        write_box(self.geo("air.brep"), *box)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 4.0}
        coil = swept_chain("sweep_1_1.brep", [{**self.HELIX, "angle": 360.0, "advance": 6.0}], "Coil", 4.0, 1.0)
        r = self.run_job([self.vol(1, "Coil", "vol_1.brep", size=1.0)], air=air, extra={"swept": [coil]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8"})
        self.assertEqual(inner_free_faces(box), [])

    BEND_PIECES = [
        {"origin": [20.0, -30.0, 0.0], "axis": [0.0, 1.0, 0.0], "angle": 0.0, "advance": 30.0},
        {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0], "angle": 90.0, "advance": 0.0},
        {"origin": [0.0, 20.0, 0.0], "axis": [-1.0, 0.0, 0.0], "angle": 0.0, "advance": 30.0},
    ]

    def bent_busbar(self, box):
        """The bent busbar 10 x 4 along line 30 + arc r 20 90 degrees + line 30, with a skin, in the air box at 8."""
        write_bent_busbar(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"), 15, 25, -2, 2, 30)
        write_box(self.geo("air.brep"), *box)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 8.0}
        bar = swept_chain("sweep_1_1.brep", self.BEND_PIECES, skin={"depth": 1.0, "per_depth": 2.0, "layer": 3.0})
        r = self.run_job([self.vol(1, "Bend", "vol_1.brep", size=2.0)], air=air, extra={"swept": [bar]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8"})
        self.assertEqual(inner_free_faces(box), [])
        return r

    def test_swept_bent_busbar_is_conformal(self):
        r = self.bent_busbar((-40, -40, -12, 75, 75, 24))
        self.assertNotIn("is a cut in one piece", r.stderr)
        p = self.bar_nodes()
        section = sum(1 for x in p if abs(x[1] + 30) < 1e-9)  # the nodes of the start face
        for joint in (abs(p[:, 1]) < 1e-9) & (p[:, 0] > 0), (abs(p[:, 0]) < 1e-9) & (p[:, 1] > 0):
            self.assertEqual(int(joint.sum()), section)

    def test_swept_chain_mixed_real_sides(self):
        # the outer side of the first leg (x = 25) on the air box's outer face, as on a symmetry plane: a cut there,
        # real surface along the bend and the other leg
        r = self.bent_busbar((-40, -40, -12, 65, 75, 24))
        self.assertIn("Swept Body Bend: a side of MAT_ID 1 is a cut in one piece and real in another", r.stderr)
        x = sorted({round(float(p[0]), 6) for p in self.bar_nodes() if p[1] < -1e-6})  # leg 1
        self.assertAlmostEqual(x[-1] - x[-2], 0.5, delta=0.125)  # the outer curve is skinned though cut in leg 1

    RACETRACK_PIECES = [  # as sweeps.recognise gives them for the racetrack (test_sweeps)
        {"origin": [0.0, -10.0, 0.0], "axis": [1.0, 0.0, 0.0], "angle": 0.0, "advance": 30.0},
        {"origin": [30.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0], "angle": 180.0, "advance": 0.0},
        {"origin": [30.0, 10.0, 0.0], "axis": [-1.0, 0.0, 0.0], "angle": 0.0, "advance": 30.0},
        {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0], "angle": 180.0, "advance": 0.0},
    ]

    def test_swept_racetrack_is_conformal(self):
        # a closed chain: line 30 + half circle r 10 + line 30 + half circle, 4 x 2, with a skin; no ends to grade
        write_racetrack(self.geo("vol_1.brep"), self.geo("sweep_1_1.brep"))
        box = (-25, -25, -10, 80, 50, 20)
        write_box(self.geo("air.brep"), *box)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 8.0}
        skin = {"depth": 0.5, "per_depth": 2.0, "layer": 2.0}
        track = swept_chain("sweep_1_1.brep", self.RACETRACK_PIECES, "Track", 4.0, 1.0, skin, closed=True)
        r = self.run_job([self.vol(1, "Track", "vol_1.brep", size=1.0)], air=air, extra={"swept": [track]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Hexahedron 8"})
        self.assertEqual(inner_free_faces(box), [])
        p = self.bar_nodes()
        section = int(((abs(p[:, 0]) < 1e-9) & (p[:, 1] < 0)).sum())  # the profile's nodes
        self.assertGreater(section, 4)
        for x, below in ((30, True), (30, False), (0, False)):  # a station at each other joint
            self.assertEqual(int(((abs(p[:, 0] - x) < 1e-9) & ((p[:, 1] < 0) == below)).sum()), section)
        x = sorted({round(float(q[0]), 6) for q in p if q[1] < -7 and -1e-9 <= q[0] <= 30 + 1e-9})  # the first leg
        for a, b in zip(x, x[1:]):  # path size 4: 8 steps of 3.75, none graded at the profile
            self.assertAlmostEqual(b - a, 3.75, delta=1e-6)

    # ---- Swept Body on the cell of a Symmetric Group: the cell job holds the cell, its copies are meshed in the free
    # job's air (MAT_ID 30); each copy c takes the part MAT_ID 5 + c when parts are per copy

    def group_job(self, cell, transforms, free_box=None, air_size=4.0, per_copy=False, excitations=None, cells=()):
        """Run mesher.py on a job of one group "Ring" of the swept cell job entry cell (a volumes entry with its
        "swept"), with more cell objects cells (volumes entries), and free air in free_box."""
        n = len(transforms)
        parts = [{"mat_id": 5 + c, "name": f"Copy{c}"} for c in range(n if per_copy else 1)]
        volumes = [cell["volume"], *cells]
        group = {
            "name": "Ring",
            "side": "fixed",
            "job": {"volumes": volumes, "surfaces": [], "sizes": [], "swept": [cell["swept"]]},
            "cells": [v["mat_id"] for v in volumes],
            "transforms": transforms,
            "parts": parts,
            "rows": [
                {"cell": v["mat_id"], "file": None, "parts": list(range(n)) if per_copy else [0] * n} for v in volumes
            ],
        }
        if excitations:
            group["excitations"] = excitations
        job = {"model_name": "Model", "mesh_file": self.msh(), "options": {}, "symmetric": {"groups": [group]}}
        if free_box:
            write_box(self.geo("air.brep"), *free_box)
            air = {"name": "Air", "mat_id": 30, "file": "geometry/air.brep", "size": air_size}
            job["symmetric"]["free"] = [
                {"side": "fixed", "job": {"volumes": [], "surfaces": [], "sizes": [], "air": air}}
            ]
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        return subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")

    def min_sicn(self, *groups_):
        """The lowest min SICN of the 3D elements of the physical groups (all of them when none is given)."""
        groups_ = groups_ or [t for _, t in gmsh.model.getPhysicalGroups(3)]
        tags = [
            t
            for g in groups_
            for e in gmsh.model.getEntitiesForPhysicalGroup(3, g)
            for t in gmsh.model.mesh.getElements(3, e)[1]
        ]
        return min(float(gmsh.model.mesh.getElementQualities(t, "minSICN").min()) for t in tags if len(t))

    SECTOR_BOX = (-27, -27, -8, 54, 54, 16)  # 6 mm of air round the ring r 19..21, z -2..2

    def sector_cell(self):
        """The 2 x 4 sector r 19..21, z -2..2, 0..45° (MAT_ID 1, size 1) swept about Z, its skin 0.66 deep (10 kHz in
        copper, 2 per depth, 3 deep); its faces toward the free side: all but the two cuts in the planes 0° and 45°."""
        write_revolved_rect(self.geo("cell_1.brep"), self.geo("sweep_1_1.brep"), 19, 21, -2, 2, 45)

        def free(c):
            return abs(c[1]) > 1e-6 and abs(c[0] - c[1]) > 1e-6

        files = write_faces(self.geo("cell_1.brep"), os.path.join(self.dir, "geometry"), "swept_free_1", free)
        entry = swept_turn("sweep_1_1.brep", 45, name="Sector", path_size=1.0, section_size=1.0)
        entry["skin"] = {"depth": 0.66, "per_depth": 2.0, "layer": 3.0}
        entry["free_faces"] = ["geometry/" + f for f in files]
        return {"volume": self.vol(1, "Sector", "cell_1.brep", size=1.0), "swept": entry}

    def test_swept_sector_cell_is_conformal(self):
        r = self.group_job(self.sector_cell(), [turn_z(45 * k) for k in range(8)], self.SECTOR_BOX)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(5)), {"Hexahedron 8"})
        self.assertEqual(inner_free_faces(self.SECTOR_BOX), [])
        self.assertGreater(self.min_sicn(), 0)
        print(f"sector: the air's min SICN {self.min_sicn(30):.4f}")
        p = gmsh.model.mesh.getNodesForPhysicalGroup(3, 5)[1].reshape(-1, 3)
        angles = sorted({round(math.degrees(math.atan2(y, x)), 6) % 360 for x, y in p[:, :2]})
        steps = [b - a for a, b in zip(angles, angles[1:] + [angles[0] + 360])]
        self.assertEqual(len(steps), 8 * 16)  # path size 1 at rc 20: 16 steps per copy
        for s in steps:  # the cuts are not graded: every step along the path is the plain one
            self.assertAlmostEqual(s, 45 / 16, delta=1e-6)
        radii = sorted({round(float(math.hypot(x, y)), 6) for x, y in p[:, :2]})
        self.assertAlmostEqual(radii[-1] - radii[-2], 0.33, delta=0.08)  # the outer face: the skin's first layer
        self.assertAlmostEqual(radii[1] - radii[0], 0.33, delta=0.08)
        z = sorted({round(float(v), 6) for v in p[:, 2]})
        self.assertAlmostEqual(z[-1] - z[-2], 0.33, delta=0.08)

    def test_swept_mirrored_cell(self):
        # the sector copied by [identity, mirror at 45°] × 4 rotations by 90°: both its cuts lie on mirror planes
        transforms = [compose_z(turn_z(90 * k), m) for k in range(4) for m in (turn_z(0), mirror_z_line(45))]
        r = self.group_job(self.sector_cell(), transforms, self.SECTOR_BOX)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(5)), {"Hexahedron 8"})
        self.assertEqual(inner_free_faces(self.SECTOR_BOX), [])
        self.assertGreater(self.min_sicn(5), 0)
        self.assertGreater(self.min_sicn(30), 0)

    def strand_cell(self):
        """litz1's strand as a cell (MAT_ID 1): r 0.45 along 1.5 turns of a helix r 1.2, pitch 10, path size 0.4,
        section 0.2, skin 0.2 deep, all its faces toward the free side. Also writes its far end face, end.brep."""
        write_helix_pipe(
            self.geo("cell_1.brep"), self.geo("sweep_1_1.brep"), 1.2, 10.0, 1.5, ("disc", 0.45), self.geo("end.brep")
        )
        files = write_faces(self.geo("cell_1.brep"), os.path.join(self.dir, "geometry"), "swept_free_1")
        piece = {**self.HELIX, "angle": 540.0, "advance": 15.0}
        entry = swept_chain("sweep_1_1.brep", [piece], name="Strand", path_size=0.4, section_size=0.2)
        entry["skin"] = {"depth": 0.2, "per_depth": 2.0, "layer": 2.0}
        entry["free_faces"] = ["geometry/" + f for f in files]
        return {"volume": self.vol(1, "Strand", "cell_1.brep", size=0.15), "swept": entry}

    SIX = [turn_z(60 * k) for k in range(6)]

    def test_swept_strand_cell_copies(self):
        r = self.group_job(self.strand_cell(), self.SIX, self.STRAND_BOX, air_size=0.6, per_copy=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        counts = [self.element_counts(5 + c) for c in range(6)]
        self.assertEqual(set(counts[0]), {"Hexahedron 8", "Prism 6"})
        self.assertEqual(counts, [counts[0]] * 6)
        self.assertEqual(inner_free_faces(self.STRAND_BOX), [])
        self.assertGreater(self.min_sicn(), 0)
        print(f"strand: the air's min SICN {self.min_sicn(30):.4f}")

    def test_swept_cell_excitation_on_every_copy(self):
        cell = self.strand_cell()
        files = []
        for c in range(6):
            write_turned(self.geo("end.brep"), self.geo(f"exc_{c}.brep"), 60 * c)
            files.append(f"geometry/exc_{c}.brep")
        excitations = [{"smat_id": 101, "name": "End", "files": files}]
        r = self.group_job(cell, self.SIX, self.STRAND_BOX, air_size=0.6, excitations=excitations)
        self.assertEqual(r.returncode, 0, r.stderr)
        centres = [face_centre(self.geo(f"exc_{c}.brep")) for c in range(6)]
        self.open_msh()
        faces = self.element_counts(101, dim=2)
        self.assertIn("Quadrilateral 4", faces)
        self.assertLessEqual(set(faces), {"Quadrilateral 4", "Triangle 3"})
        self.assertEqual(sum(faces.values()) % 6, 0)
        hits = set()
        for p in gmsh.model.mesh.getNodesForPhysicalGroup(2, 101)[1].reshape(-1, 3):
            k = min(range(6), key=lambda c: math.dist(p, centres[c]))
            self.assertLess(math.dist(p, centres[k]), 0.45 + 1e-4)  # on the end disc of copy k
            hits.add(k)
        self.assertEqual(hits, set(range(6)))

    def test_swept_cell_seam_with_a_meshed_copy_is_refused(self):
        # the sector beside a tetrahedral cell 45..90°, 4 rotations by 90°: the sector's cut at 0° meets the copy of
        # the other cell's face at 90°, which gmsh meshes on its own, not as the sector's hand-made section
        cell = self.sector_cell()
        write_revolved_rect(self.geo("cell_2.brep"), self.geo("profile_2.brep"), 19, 21, -2, 2, 45)
        write_turned(self.geo("cell_2.brep"), self.geo("cell_2.brep"), 45)
        other = self.vol(2, "Tooth", "cell_2.brep", size=1.0)
        r = self.group_job(cell, [turn_z(90 * k) for k in range(4)], cells=[other])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(
            "group Ring: the swept cell Sector meets a copy on a face whose mesh the copy cannot share; meshing that"
            " is not handled yet, a limit of the tool, not of the drawing",
            r.stderr,
        )

    def test_swept_cell_needing_a_vertex_is_refused(self):
        # the bar x 0..1, y 0..1 along z 0..4 and its copy moved by x + 1; the block x 0..0.5, y 1..2, z 0..2 beside
        # it ends its edge on the bar's edge x = 0, y = 1 at z = 2, which the copy's face x = 1 does not have
        write_box(self.geo("cell_1.brep"), 0, 0, 0, 1, 1, 4)
        write_rect(self.geo("sweep_1_1.brep"), 0, 0, 0, 1, 1)
        write_box(self.geo("cell_2.brep"), 0, 1, 0, 0.5, 1, 2)
        bar = swept("sweep_1_1.brep", name="Bar", path_size=1.0, section_size=0.5, recombine=False, advance=4.0)
        cell = {"volume": self.vol(1, "Bar", "cell_1.brep", size=0.5), "swept": bar}
        shift = [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        r = self.group_job(cell, [turn_z(0), shift], cells=[self.vol(2, "Block", "cell_2.brep", size=0.5)])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(
            "group Ring: the swept cell Bar would need a mesh node on its edge where an edge of a copy ends on it;"
            " meshing that is not handled yet, a limit of the tool, not of the drawing",
            r.stderr,
        )

    # ---- sliding motion: the fixed side goes to pre_geom.msh, the moving side to rotor_mesh.msh

    def files(self):
        return os.path.join(self.dir, "pre_geom.msh"), os.path.join(self.dir, "rotor_mesh.msh")

    def slide(self, kind, files, n, cross, full=False, id_=20):
        """A slide entry named Slide; its marker is geometry/marker_<id_>.brep."""
        return {
            "name": "Slide",
            "kind": kind,
            "files": ["geometry/" + f for f in files],
            "marker": f"geometry/marker_{id_}.brep",
            "divisions": n,
            "cross_divisions": cross,
            "slide_mat_id": id_,
            "full": full,
        }

    def slide_job(self, volumes, moving, slides, periodic=None, surfaces=()):
        """Run a slide job: air from geometry/air.brep (fixed ID 10, moving 11), moving cell geometry/cell_1.brep."""
        sides = {"fixed": {"mat_id": 10, "name": "Air_fixed"}, "moving": {"mat_id": 11, "name": "Air_moving"}}
        air = {"sides": sides, "file": "geometry/air.brep", "size": 15.0}
        extra = {
            "rotor_file": self.files()[1],
            "moving": moving,
            "moving_cells": ["geometry/cell_1.brep"],
            "slides": slides,
        }
        if periodic:
            extra["periodic"] = periodic
        return self.run_job(volumes, surfaces, air=air, extra=extra)

    def motor_job(self, tooth=None, surfaces=(), rotor=40, start=0):
        """Case 17: stator ring 45..80 fixed, rotor (radius rotor) moving, both z 0..50, air cylinder r 100 from z -25
        to 75, slide cylinder r 42.5 in two halves from angle start, 72 divisions round and 10 up, slide edge at start.
        tooth: (z0, height, a0, a1) of a stator tooth 42.5..45 that touches the slide cylinder."""
        write_rings(self.geo("vol_1.brep"), (45, 80, 0, 50), *([(42.5, 45, *tooth)] if tooth else []))
        write_rings(self.geo("vol_2.brep"), (0, rotor, 0, 50))
        write_rings(self.geo("air.brep"), (0, 100, -25, 100))
        write_rings(self.geo("cell_1.brep"), (0, 42.5, -25, 100))
        for k, a in enumerate((start, start + 180), 1):
            write_revolved(self.geo(f"slide_20_{k}.brep"), (42.5, 0, -25), (42.5, 0, 75), a, a + 180)
        x, y = 42.5 * math.cos(math.radians(start)), 42.5 * math.sin(math.radians(start))
        write_line(self.geo("marker_20.brep"), (x, y, -25), (x, y, 75))
        vols = [self.vol(1, "Stator", "vol_1.brep", 10), self.vol(2, "Rotor", "vol_2.brep", 10)]
        slide = self.slide("rotational", ["slide_20_1.brep", "slide_20_2.brep"], 72, 10, True)
        return self.slide_job(vols, [2], [slide], surfaces=surfaces)

    def test_radial_slide_cylinder_matches(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (
            sorted(p for p in read_nodes(f) if abs(math.hypot(p[0], p[1]) - 42.5) < 1e-6) for f in self.files()
        )
        self.assertEqual(len(fixed), 72 * 11)
        self.assertEqual(fixed, moving)
        self.assertEqual(sorted({p[2] for p in fixed}), list(range(-25, 76, 10)))
        angles = sorted({round(math.degrees(math.atan2(p[1], p[0])), 6) % 360 for p in fixed})
        self.assertEqual(len(angles), 72)
        for got, want in zip(angles, range(0, 360, 5)):
            self.assertAlmostEqual(got, want, places=6)
        self.assertIn("MAT_ID      10  Air_fixed", r.stdout)
        self.assertIn("MAT_ID      11  Air_moving", r.stdout)
        self.assertIn("SLIDE_NDIV 72", r.stdout)
        self.assertIn(f"Wrote {self.files()[1]}", r.stdout)
        for path in self.files():  # each file numbers its nodes from 1
            tags = self.node_tags(path)
            self.assertEqual(tags, list(range(1, len(tags) + 1)), path)

    def node_tags(self, path):
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(path)
            return sorted(int(t) for t in gmsh.model.mesh.getNodes()[0])
        finally:
            gmsh.finalize()

    def cylinder_nodes(self, r=42.5):
        """The nodes on the slide cylinder in each file."""
        return [sorted(p for p in read_nodes(f) if abs(math.hypot(p[0], p[1]) - r) < 1e-6) for f in self.files()]

    def test_rotor_on_the_slide_cylinder_matches(self):
        """The rotor's outer face is part of the slide cylinder: its end circles cut each half into three bands."""
        r = self.motor_job(rotor=42.5)
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = self.cylinder_nodes()
        self.assertEqual(len(fixed), 72 * 11)
        self.assertEqual(fixed, moving)
        self.assertEqual(len({p[2] for p in fixed}), 11)
        self.assertEqual(len({round(math.degrees(math.atan2(p[1], p[0])), 6) % 360 for p in fixed}), 72)

    def test_excitation_surface_goes_to_the_file_of_its_body(self):
        write_revolved(self.geo("surf_1001_1.brep"), (45, 0, 50), (80, 0, 50), 0, 360)  # the stator's top face
        surface = {"smat_id": 1001, "name": "Terminal", "mat_id": 1, "files": ["geometry/surf_1001_1.brep"]}
        r = self.motor_job(surfaces=[surface])
        self.assertEqual(r.returncode, 0, r.stderr)
        found = []
        for path in self.files():
            gmsh.initialize()
            try:
                gmsh.option.setNumber("General.Terminal", 0)
                gmsh.open(path)
                found.append(gmsh.model.getPhysicalGroups(2))
                if found[-1]:
                    z = gmsh.model.mesh.getNodesForPhysicalGroup(2, 1001)[1][2::3]
                    self.assertTrue(len(z) and all(abs(v - 50) < 1e-9 for v in z))
            finally:
                gmsh.finalize()
        self.assertEqual(found, [[(2, 1001)], []])

    def test_tooth_on_the_slide_cylinder_keeps_the_grid(self):
        """A tooth face from 10° to 20° over the whole height splits a half along the motion, on the 5° grid."""
        r = self.motor_job(tooth=(-25, 100, 10, 20))
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = self.cylinder_nodes()
        self.assertEqual(len(fixed), 72 * 11)
        self.assertEqual(fixed, moving)
        angles = sorted({round(math.degrees(math.atan2(p[1], p[0])), 6) % 360 for p in fixed})
        for got, want in zip(angles, range(0, 360, 5)):
            self.assertAlmostEqual(got, want, places=6)

    def test_tooth_on_part_of_the_slide_cylinder_fails_cleanly(self):
        """A tooth face from 10° to 20° and z 0..50 is a hole in the half cylinder face: it cannot be structured."""
        r = self.motor_job(tooth=(0, 50, 10, 20))
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(
            last.startswith("ERROR: sliding interface Slide: slide_20_1.brep: a body lies on only part"), last
        )
        self.assertIn("must reach from edge to edge", last)

    def test_tooth_between_two_divisions_fails_cleanly(self):
        last = self.last_error(self.motor_job(tooth=(-25, 100, 12, 20)))
        self.assertIn("sliding interface Slide: slide_20_1.brep: the point at (41.571", last)
        self.assertIn("at 12° lies between two divisions along the motion", last)
        self.assertIn("(every 5°)", last)

    def test_rotor_seam_between_two_divisions_fails_cleanly(self):
        """The slide starts at 3°: the seam of the rotor's cylinder face at 0° cuts the slide cylinder off the grid."""
        last = self.last_error(self.motor_job(rotor=42.5, start=3))
        self.assertIn("at 0° lies between two divisions along the motion", last)
        self.assertIn("it may be a body edge or the seam of a round body face", last)
        self.assertIn("(every 5°), or change Divisions or the start angle", last)

    def test_rotor_on_the_slide_cylinder_with_its_seam_on_the_grid_matches(self):
        r = self.motor_job(rotor=42.5, start=-30)  # the seam at 0° lies on the 5° grid from -30°
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = self.cylinder_nodes()
        self.assertEqual(len(fixed), 72 * 11)
        self.assertEqual(fixed, moving)

    def last_error(self, r):
        self.assertEqual(r.returncode, 1, r.stderr)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR:"), last)
        return last

    def line_group(self, path, group):
        """(element count, node coordinates) of the dim-1 physical group in a mesh file; None if it has none."""
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(path)
            if (1, group) not in gmsh.model.getPhysicalGroups(1):
                return None
            count = 0
            for e in gmsh.model.getEntitiesForPhysicalGroup(1, group):
                count += sum(len(t) for t in gmsh.model.mesh.getElements(1, e)[1])
            c = gmsh.model.mesh.getNodesForPhysicalGroup(1, group)[1]
            return count, [tuple(round(x, 9) + 0.0 for x in c[i : i + 3]) for i in range(0, len(c), 3)]
        finally:
            gmsh.finalize()

    def test_rotor_file_has_slide_edge_at_start_angle(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, rotor = self.files()
        count, nodes = self.line_group(rotor, 20)
        self.assertEqual(count, 10)
        self.assertEqual(sorted(nodes), [(42.5, 0, z) for z in range(-25, 76, 10)])
        self.assertIsNone(self.line_group(fixed, 20))

    def slide_triangles(self, path, r):
        """The faces of the tetrahedra in path that lie on the cylinder of radius r, each as a frozenset of
        (5° step, z) of its nodes."""
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(path)
            tags, coords = gmsh.model.mesh.getNodes()[:2]
            where = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
            _, nodes = gmsh.model.mesh.getElementsByType(4)
        finally:
            gmsh.finalize()
        on = {t: (round(math.degrees(math.atan2(y, x)) / 5) % 72, round(z, 6)) for t, (x, y, z) in where.items()}
        on = {t: key for t, key in on.items() if abs(math.hypot(*where[t][:2]) - r) < 1e-6}
        found = set()
        for k in range(0, len(nodes), 4):
            tet = [int(n) for n in nodes[k : k + 4]]
            for skip in range(4):
                tri = [n for i, n in enumerate(tet) if i != skip]
                if all(n in on for n in tri):
                    found.add(frozenset(on[n] for n in tri))
        return found

    def test_slide_triangles_same_after_one_division(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        tris = self.slide_triangles(self.files()[1], 42.5)
        self.assertEqual(len(tris), 72 * 10 * 2)
        turned = {frozenset(((k + 1) % 72, z) for k, z in tri) for tri in tris}
        self.assertEqual(turned, tris)

    def axial_job(self, rotor_z=0):
        """Case 19: rotor disc r 50 from z rotor_z, 10 high, moving; stator disc z 12..22 fixed; slide disc z 11 over
        the whole air r 80, 36 divisions round and 8 out."""
        write_rings(self.geo("vol_1.brep"), (0, 50, 12, 10))
        write_rings(self.geo("vol_2.brep"), (0, 50, rotor_z, 10))
        write_rings(self.geo("air.brep"), (0, 80, -10, 42))
        write_rings(self.geo("cell_1.brep"), (0, 80, -10, 21))
        for k, a in enumerate((0, 180), 1):
            write_revolved(self.geo(f"slide_20_{k}.brep"), (0, 0, 11), (80, 0, 11), a, a + 180)
        write_line(self.geo("marker_20.brep"), (0, 0, 11), (80, 0, 11))
        vols = [self.vol(1, "Stator", "vol_1.brep", 10), self.vol(2, "Rotor", "vol_2.brep", 10)]
        slide = self.slide("axial", ["slide_20_1.brep", "slide_20_2.brep"], 36, 8, True)
        return self.slide_job(vols, [2], [slide])

    def test_axial_gap_disc_reaching_axis(self):
        r = self.axial_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (sorted(p for p in read_nodes(f) if abs(p[2] - 11) < 1e-9) for f in self.files())
        self.assertEqual(len(fixed), 36 * 8 + 1)
        self.assertEqual(fixed, moving)
        count, nodes = self.line_group(self.files()[1], 20)
        self.assertEqual(count, 8)
        self.assertEqual(sorted(nodes), [(x, 0, 11) for x in range(0, 81, 10)])

    def test_rotor_disc_on_the_axial_gap_plane_matches(self):
        """The rotor's top face lies on the slide disc: each half is a half disc r < 50 and a half ring around it."""
        r = self.axial_job(rotor_z=1)
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (sorted(p for p in read_nodes(f) if abs(p[2] - 11) < 1e-9) for f in self.files())
        self.assertEqual(len(fixed), 36 * 8 + 1)
        self.assertEqual(fixed, moving)

    def linear_job(self, mover=(0, 0, 24, 80, 40, 16)):
        """Case 20: stator box below z 20 fixed, mover box (x, y, z, dx, dy, dz) moving, slide plane z 22 moving along
        x with 32 divisions and 8 across, the period is the 80 mm air box length."""
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 80, 40, 20)
        write_box(self.geo("vol_2.brep"), *mover)
        write_box(self.geo("air.brep"), 0, 0, -5, 80, 40, 50)
        write_box(self.geo("cell_1.brep"), 0, 0, 22, 80, 40, 23)
        write_rect(self.geo("slide_20_1.brep"), 0, 0, 22, 80, 40)
        write_line(self.geo("marker_20.brep"), (0, 0, 22), (0, 40, 22))
        vols = [self.vol(1, "Stator", "vol_1.brep", 10), self.vol(2, "Mover", "vol_2.brep", 10)]
        period = {"kind": "translation", "vector": [80.0, 0.0, 0.0], "start": 0.0}
        return self.slide_job(vols, [2], [self.slide("linear", ["slide_20_1.brep"], 32, 8)], period)

    def test_mover_on_the_linear_plane_matches(self):
        """The mover's bottom face (y 10..30) lies on the slide plane: it cuts it into three bands across the motion."""
        r = self.linear_job(mover=(0, 10, 22, 80, 20, 18))
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (sorted(p for p in read_nodes(f) if abs(p[2] - 22) < 1e-9) for f in self.files())
        self.assertEqual(len(fixed), 33 * 9)
        self.assertEqual(fixed, moving)
        self.assertEqual(sorted({p[1] for p in fixed}), list(range(0, 41, 5)))

    def test_linear_3d_plane_and_period(self):
        r = self.linear_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        planes = []
        for path in self.files():
            pts = read_nodes(path)
            planes.append(sorted(p for p in pts if abs(p[2] - 22) < 1e-9))
            self.assertEqual(len(planes[-1]), 33 * 9, path)
            left = sorted(p[1:] for p in pts if abs(p[0]) < 1e-9)
            right = sorted(p[1:] for p in pts if abs(p[0] - 80) < 1e-9)
            self.assertGreater(len(left), 9)
            self.assertEqual(left, right, path)
        self.assertEqual(planes[0], planes[1])
        self.assertEqual(self.line_group(self.files()[1], 20)[0], 8)
        self.assertIn("DXYZ 0.08 0 0", r.stdout)


if __name__ == "__main__":
    unittest.main()
