"""Helpers of the group mesher (meshgroups.py) on a cell meshed in gmsh: its seams and their periodic copies, the
excitation patches that land on a face, the sliding circle or cylinder and its marker. "side" is a dict with the cells
("cells": physical ids), their copies ("transforms") and, for the sliding checks, its "side" name. Runs in the mesher
process; dim is 2 (faces) or 3 (solids). Never import FreeCAD here."""

import math
import os
from collections import Counter

import gmsh

from meshcommon import JobError, import_brep
from meshcommon import _slide_faces


def _apply(m, p):
    """Point p moved by the 4x4 row-major affine transform m."""
    return [sum(m[4 * i + k] * v for k, v in enumerate((*p, 1))) for i in range(3)]


def _angle(p):
    """Angle about Z in degrees, 0 <= a < 360; rounded first, so a point just below 0° is 0°, not 360°."""
    return round(math.degrees(math.atan2(p[1], p[0])), 6) % 360


def _side_seams(side, dim):
    """Tags of the boundary entities of the side's cell entities of dimension dim (curves in 2D, faces in 3D), sorted."""
    cells = [(dim, e) for id_ in side["cells"] for e in gmsh.model.getEntitiesForPhysicalGroup(dim, id_)]
    return sorted({abs(t) for _, t in gmsh.model.getBoundary(cells, combined=False, oriented=False)})


def _ends(c):
    return [gmsh.model.getValue(0, t, []) for _, t in gmsh.model.getBoundary([(1, c)], oriented=False)]


def _corners(dim, tag):
    """The points of a curve (its ends) or of a face (its corners)."""
    points = gmsh.model.getBoundary([(dim, tag)], oriented=False, recursive=True)
    return [gmsh.model.getValue(0, t, []) for _, t in points]


def _on_arc(c, r, tol):
    """True when curve c is an arc of the circle of radius r about Z: both its ends and its middle lie on it."""
    ends = _ends(c)
    lo, hi = gmsh.model.getParametrizationBounds(1, c)
    mid = gmsh.model.getValue(1, c, [(lo[0] + hi[0]) / 2])
    return len(ends) == 2 and all(abs(math.hypot(p[0], p[1]) - r) <= tol for p in ends + [mid])


def _slide_arcs(slide, sides):
    """Make the cells' arcs on the sliding circle transfinite: each gets its share of the divisions of the full turn,
    which must be whole, and both its ends must lie on the 360° / divisions grid that starts at 0°. The cell of every
    side must own such an arc."""
    r, n, name = slide["radius"], slide["divisions"], slide["name"]
    tol = 1e-6 * r
    arcs = set()
    for c in sorted({c for side in sides for c in _side_seams(side, 2)}):
        if not _on_arc(c, r, tol):
            continue
        ends = _ends(c)
        share = n * math.degrees(gmsh.model.occ.getMass(1, c) / r) / 360
        a0, a1 = sorted(_angle(p) for p in ends)
        if any(abs(x - round(x)) > 1e-6 for x in (share, n * a0 / 360, n * a1 / 360)):
            raise JobError(
                f"sliding interface {name}: the cell's arc from {a0:g}° to {a1:g}° gets {share:g} of the {n} "
                f"divisions; it needs a whole number, with both ends on the {360 / n:g}° grid that starts at 0°"
            )
        gmsh.model.mesh.setTransfiniteCurve(c, round(share) + 1)
        arcs.add(c)
    for side in sides:
        if not arcs & set(_side_seams(side, 2)):
            raise JobError(
                f"sliding interface {name}: the cell of the {side['side']} side has no arc on the sliding circle"
                f" (radius {r:g} mm); both sides must reach it"
            )


def _cylinder_faces(side, r, tol):
    """Tags of the boundary faces of the side's cells that lie on the cylinder of radius r about Z: their corners and
    points inside them."""
    out = []
    for f in _side_seams(side, 3):
        lo, hi = gmsh.model.getParametrizationBounds(2, f)
        steps = (0.25, 0.5, 0.75)
        uv = [x for a in steps for b in steps for x in (lo[0] + (hi[0] - lo[0]) * a, lo[1] + (hi[1] - lo[1]) * b)]
        xyz = gmsh.model.getValue(2, f, uv)
        pts = _corners(2, f) + [xyz[k : k + 3] for k in range(0, len(xyz), 3)]
        if all(abs(math.hypot(p[0], p[1]) - r) <= tol for p in pts):
            out.append(f)
    return out


def _slide_faces_sym(slide, sides):
    """3D twin of _slide_arcs: make the cells' faces on the sliding cylinder (radius about Z) transfinite. Each gets its
    share of the divisions of the full turn around Z (whole, its corners on the 360° / divisions grid from 0°) and its
    share of cross_divisions along Z over the height of the cylinder (its corners on that grid), with the "Left"
    triangles and corner order of 3D sliding (_slide_faces). The cells of every side must reach over the whole
    cylinder: all the copies of a side together cover z_range of the slide when it has one, else the height of the
    faces found."""
    r, n, k, name = slide["radius"], slide["divisions"], slide["cross_divisions"], slide["name"]
    tol = 1e-6 * r
    faces = {side["side"]: _cylinder_faces(side, r, tol) for side in sides}
    for side in sides:
        if not faces[side["side"]]:
            raise JobError(
                f"sliding interface {name}: the cells of the {side['side']} side have no face on the sliding cylinder"
                f" (radius {r:g} mm); both sides must reach it"
            )
    tags = sorted({f for fs in faces.values() for f in fs})
    corners = {f: _corners(2, f) for f in tags}
    z0, z1 = slide.get("z_range") or (
        min(p[2] for f in tags for p in corners[f]),
        max(p[2] for f in tags for p in corners[f]),
    )
    for side in sides:
        area = sum(gmsh.model.occ.getMass(2, f) for f in faces[side["side"]])
        need = 2 * math.pi * r / len(side["transforms"]) * (z1 - z0)
        if abs(area - need) > 1e-6 * need:
            raise JobError(
                f"sliding interface {name}: the cells of the {side['side']} side do not reach over the whole cylinder"
                f" (radius {r:g}, z {z0:g}..{z1:g})"
            )
    done = {}  # curve -> elements, so a curve between two faces gets one count
    for f in tags:
        zs = [p[2] for p in corners[f]]
        height = max(zs) - min(zs)
        share = n * math.degrees(gmsh.model.occ.getMass(2, f) / (r * height)) / 360
        angles = [_angle(p) for p in corners[f]]
        if any(abs(x - round(x)) > 1e-6 for x in [share] + [n * a / 360 for a in angles]):
            raise JobError(
                f"sliding interface {name}: the cell's cylinder face from {min(angles):g}° to {max(angles):g}° gets"
                f" {share:g} of the {n} divisions; it needs a whole number, with both ends on the {360 / n:g}° grid"
                " that starts at 0°"
            )
        for z in zs:
            x = k * (z - z0) / (z1 - z0)
            if abs(x - round(x)) > 1e-6:
                raise JobError(
                    f"sliding interface {name}: a cut at z = {z:g} is off the grid of {k} cross_divisions over"
                    f" z {z0:g}..{z1:g}"
                )
        cross = round(k * height / (z1 - z0))
        _slide_faces(dict(slide, cross_divisions=cross), f"sliding interface {name}", [f], round(share), None, done)


def _inside_points(dim, t):
    """Points of entity t on a grid over its parametric box that are inside its trimming (a face's box reaches past
    it); its centre of mass when none is."""
    lo, hi = gmsh.model.getParametrizationBounds(dim, t)
    steps = (0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875)
    grid = [[a] for a in steps] if dim == 1 else [[a, b] for a in steps for b in steps]
    uvs = [[lo[i] + (hi[i] - lo[i]) * f[i] for i in range(dim)] for f in grid]
    out = [list(gmsh.model.getValue(dim, t, uv)) for uv in uvs if dim == 1 or gmsh.model.isInside(dim, t, uv, True)]
    return out or [list(gmsh.model.occ.getCenterOfMass(dim, t))]


def _twin(c, d, m, tol, dim):
    """True when seam c (a curve when dim is 1, a face when 2) moved by the transform m covers seam d: the same length
    or area, and points inside c moved lie inside d. Their corners may still differ (see _same)."""
    if abs(gmsh.model.occ.getMass(dim, c) - gmsh.model.occ.getMass(dim, d)) > tol:
        return False
    moved = [_apply(m, p) for p in _inside_points(dim, c)]
    return _on_face(dim, d, gmsh.model.getBoundingBox(dim, d), moved, tol)


def _missing_corners(c, d, m, tol, dim):
    """(the corners of d that no corner of c moved by m reaches, the corners of c whose move reaches none of d)."""
    corners_c, corners_d = _corners(dim, c), _corners(dim, d)
    moved = [_apply(m, p) for p in corners_c]
    return (
        [q for q in corners_d if min((math.dist(p, q) for p in moved), default=math.inf) > tol],
        [p for p, n in zip(corners_c, moved) if min((math.dist(n, q) for q in corners_d), default=math.inf) > tol],
    )


def _corners_match(c, d, m, tol, dim):
    """True when the corners of c moved by m are those of d, one to one: gmsh copies a mesh only between such."""
    return len(_corners(dim, c)) == len(_corners(dim, d)) and not any(_missing_corners(c, d, m, tol, dim))


def _same(c, d, m, tol, dim):
    """True when seam c moved by the transform m is seam d: _twin, with _corners_match. A face's parametric box reaches
    past its trimming, so _twin tests points inside it: two faces of one plane with the same area and some corners in
    common (the two pieces of a disc that a lens cut off) are not the same."""
    return _corners_match(c, d, m, tol, dim) and _twin(c, d, m, tol, dim)


def _periodic(sides, dim):
    """Seams that a copy of the cell meets carry the same nodes: for seams c != d of a side's cells (curves in 2D,
    faces in 3D) with T(c) == d for one of the side's transforms T, d is meshed as a copy of c (gmsh periodic). A seam
    a transform maps onto itself (on a mirror) needs nothing. Each seam is copied from one master at most, and a
    master is no copy."""
    box = gmsh.model.getBoundingBox(-1, -1)
    tol = 1e-6 * max(1.0, math.dist(box[:3], box[3:]))
    masters, slaves = set(), set()
    for side in sides:
        seams = _side_seams(side, dim)
        for d in seams:
            if d in slaves or d in masters:
                continue
            for c in seams:
                if c >= d or c in slaves:
                    continue
                m = next((m for m in side["transforms"] if _same(c, d, m, tol, dim - 1)), None)
                if m is not None:
                    gmsh.model.mesh.setPeriodic(dim - 1, [d], [c], m)
                    masters.add(c)
                    slaves.add(d)
                    break


def _entity(dim, e):
    """(entity, {element type: node tags}, nodes used, element centres, area or volume) of a meshed entity."""
    types, tags, nodes = gmsh.model.mesh.getElements(dim, e)
    conn = {int(t): [int(n) for n in ns] for t, ns in zip(types, nodes)}
    used = sorted({n for ns in conn.values() for n in ns})
    per = len(nodes[0]) // len(tags[0])
    centres = []
    for k in (0, len(tags[0]) // 2, len(tags[0]) - 1):  # first, middle and last element: surely inside
        xyz = [gmsh.model.mesh.getNode(int(t))[0] for t in nodes[0][k * per : (k + 1) * per]]
        centres.append([sum(p[i] for p in xyz) / per for i in range(3)])
    return e, conn, used, centres, gmsh.model.occ.getMass(dim, e)


def _cell_patches(side, dim):
    """[_entity] of the boundary entities of the side's cell bodies (faces in 3D); none when it has no excitations."""
    if not side.get("excitations"):
        return []
    out = []
    for f in _side_seams(side, dim):
        e, conn, used, centres, area = _entity(dim - 1, f)
        near = gmsh.model.getClosestPoint(dim - 1, f, [x for p in centres for x in p])[0]  # flat elements: off a curve
        out.append((e, conn, used, [list(near[k : k + 3]) for k in range(0, len(near), 3)], area))
    return out


def _on_face(dim, t, box, points, tol):
    """True when every point lies on entity t: projected onto it within tol (a plane's face projects anywhere on the
    plane), inside its bounding box and inside the trimmed face."""
    flat = [x for p in points for x in p]
    near = gmsh.model.getClosestPoint(dim, t, flat)[0]
    if any(math.dist(p, near[3 * k : 3 * k + 3]) > tol for k, p in enumerate(points)):
        return False
    if any(not box[i] - tol <= p[i] <= box[i + 3] + tol for p in points for i in range(3)):
        return False
    return gmsh.model.isInside(dim, t, flat) == len(points)


def _land_surfaces(sides, patches, folder, dim):
    """labels[side][patch][copy] = the side's excitation that copy of the cell boundary patch lands on (all its element
    centres lie on one of its faces), or None: not copied as a surface. A copy landing where an earlier one did (the
    face two copies share) is None too. The landed patches must cover each excitation face exactly, or the cell is not
    split where the face ends."""
    box = gmsh.model.getBoundingBox(-1, -1)
    tol = 1e-6 * max(1.0, math.dist(box[:3], box[3:]))
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
    current = gmsh.model.getCurrent()
    gmsh.model.add("excitations")
    try:
        labels = []
        for side, ents in zip(sides, patches):
            files = [(x, f) for x in side.get("excitations", []) for f in x["files"]]
            faces = [[t for _, t in import_brep(os.path.join(folder, f), dim - 1)] for _, f in files]
            gmsh.model.occ.synchronize()
            targets = [(k, t, gmsh.model.getBoundingBox(dim - 1, t)) for k, ts in enumerate(faces) for t in ts]
            areas = [sum(gmsh.model.occ.getMass(dim - 1, t) for t in ts) for ts in faces]
            covered = [0.0] * len(files)
            seen, side_labels = [], []  # (node count, centre of the nodes) of each landed copy
            for _, _, used, centres, area in ents:
                mean = [sum(xyz[n][i] for n in used) / len(used) for i in range(3)]
                copies = []
                for m in side["transforms"]:
                    moved = [_apply(m, p) for p in centres]
                    hit = next((k for k, t, b in targets if _on_face(dim - 1, t, b, moved, tol)), None)
                    if hit is not None:
                        here = _apply(m, mean)  # the same nodes moved: the same centre, so compared within tol
                        if any(n == len(used) and math.dist(here, p) <= tol for n, p in seen):
                            hit = None
                        else:
                            seen.append((len(used), here))
                            covered[hit] += area
                    copies.append(None if hit is None else files[hit][0])
                side_labels.append(copies)
            for (x, f), area, got in zip(files, areas, covered):
                if abs(got - area) > 1e-6 * area:
                    raise JobError(
                        f"excitation {x['name']}: the copies of the cell cover {got:.6g} of the {area:.6g} mm² of {f};"
                        " the cell must be split where the face ends"
                    )
            labels.append(side_labels)
        return labels
    finally:
        gmsh.model.remove()
        gmsh.model.setCurrent(current)


def _marker(slide):
    """The slide point: a discrete point entity holding one point element on the node at (radius, 0)."""
    r = slide["radius"]
    tags, coords, _ = gmsh.model.mesh.getNodes()
    node = next(
        (int(t) for k, t in enumerate(tags) if math.dist(coords[3 * k : 3 * k + 3], (r, 0, 0)) < 1e-6 * r), None
    )
    if node is None:
        raise JobError(f"sliding interface {slide['name']}: the mesh has no node at ({r:g}, 0)")
    point = gmsh.model.addDiscreteEntity(0)
    gmsh.model.mesh.addElementsByType(point, 15, [], [node])
    gmsh.model.addPhysicalGroup(0, [point], slide["slide_mat_id"], name=slide["name"])
    return point


def _marker_line(slide):
    """The slide edge: a discrete curve entity holding the line elements between consecutive nodes on the sliding
    cylinder at 0°, the generatrix through (radius, 0)."""
    r = slide["radius"]
    tags, coords, _ = gmsh.model.mesh.getNodes()
    on = []
    for k, t in enumerate(tags):
        p = coords[3 * k : 3 * k + 3]
        if abs(p[0] - r) < 1e-6 * r and abs(p[1]) < 1e-6 * r:
            on.append((p[2], int(t)))
    nodes = [t for _, t in sorted(on)]
    if len(nodes) < 2:
        raise JobError(f"sliding interface {slide['name']}: the mesh has no line of nodes at ({r:g}, 0) along Z")
    line = gmsh.model.addDiscreteEntity(1)
    gmsh.model.mesh.addElementsByType(line, 1, [], [n for pair in zip(nodes, nodes[1:]) for n in pair])
    gmsh.model.addPhysicalGroup(1, [line], slide["slide_mat_id"], name=slide["name"])
    return line


def _side_facets(split, side, dim):
    """{sorted node tags: number of the side's elements using them} in model "full", over the element edges (2D) or
    the element faces (3D)."""
    facets = Counter()
    for _, ents in split.get(side["side"], {}).values():
        for e in ents:
            for typ in gmsh.model.mesh.getElementTypes(dim, e):
                for n in (2,) if dim == 2 else (3, 4):  # 3D: the triangle faces, then the quad faces
                    if dim == 2:
                        fn = gmsh.model.mesh.getElementEdgeNodes(typ, e, primary=True)
                    else:
                        fn = gmsh.model.mesh.getElementFaceNodes(typ, n, e, primary=True)
                    facets.update(tuple(sorted(int(v) for v in fn[k : k + n])) for k in range(0, len(fn), n))
    return facets


def _on_circle(slide, sides, split):
    """Each side has exactly one node on the sliding circle at each of the divisions grid angles."""
    r, n, name = slide["radius"], slide["divisions"], slide["name"]
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
    for side in sides:
        nodes = {v for e in _side_facets(split, side, 2) for v in e}
        angles = [_angle(xyz[v]) for v in nodes if abs(math.hypot(*xyz[v][:2]) - r) <= 1e-6 * r]
        steps = [a * n / 360 for a in angles]
        grid = {round(k) % n for k in steps if abs(k - round(k)) <= 1e-6}
        if len(angles) != n or len(grid) != n:
            raise JobError(
                f"sliding interface {name}: the {side['side']} side has {len(angles)} nodes on the circle"
                f" (radius {r:g} mm) where it needs one on each of the {n} divisions; its copies must cover the circle"
            )


def _on_cylinder(slide, sides, split):
    """3D twin of _on_circle: each side has exactly one node on the sliding cylinder at each point of the grid of
    divisions around Z by cross_divisions + 1 levels along it. Only the nodes have to match: the triangles may not."""
    r, n, k, name = slide["radius"], slide["divisions"], slide["cross_divisions"], slide["name"]
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = {int(t): coords[3 * j : 3 * j + 3] for j, t in enumerate(tags)}
    on = {}
    for side in sides:
        nodes = {v for f in _side_facets(split, side, 3) for v in f}
        on[side["side"]] = [xyz[v] for v in nodes if abs(math.hypot(*xyz[v][:2]) - r) <= 1e-6 * r]
    zs = [p[2] for pts in on.values() for p in pts]
    z0, height = min(zs, default=0), (max(zs, default=0) - min(zs, default=0)) or 1
    for side in sides:
        pts = on[side["side"]]
        steps = [(_angle(p) * n / 360, k * (p[2] - z0) / height) for p in pts]
        grid = {(round(a) % n, round(b)) for a, b in steps if abs(a - round(a)) <= 1e-6 and abs(b - round(b)) <= 1e-6}
        if len(pts) != n * (k + 1) or len(grid) != n * (k + 1):
            raise JobError(
                f"sliding interface {name}: the {side['side']} side has {len(pts)} nodes on the cylinder (radius {r:g}"
                f" mm) where it needs one on each of the {n} × {k + 1} grid points; its copies must cover the cylinder"
            )
