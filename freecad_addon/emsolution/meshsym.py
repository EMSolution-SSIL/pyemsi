"""Symmetric mesh: mesh the cell, copy the mesh by the transforms and give every copy the MAT_ID of the drawn piece it
lands on. Runs in the mesher process (mesher2d.run_job calls run for a job with a "symmetric" key).
Never import FreeCAD here."""

import json
import math
import os
from collections import Counter

import gmsh

from meshcommon import JobError, generate, import_brep, publish, slide_report, write_split, MSH_VERSION


def _apply(m, p):
    """Point p moved by the 4x4 row-major affine transform m."""
    return [sum(m[4 * i + k] * v for k, v in enumerate((*p, 1))) for i in range(3)]


def _det(m):
    return (
        m[0] * (m[5] * m[10] - m[6] * m[9]) - m[1] * (m[4] * m[10] - m[6] * m[8]) + m[2] * (m[4] * m[9] - m[5] * m[8])
    )


def _angle(p):
    """Angle about Z in degrees, 0 <= a < 360; rounded first, so a point just below 0° is 0°, not 360°."""
    return round(math.degrees(math.atan2(p[1], p[0])), 6) % 360


def _side_curves(side):
    """Tags of the boundary curves of the side's cell faces, sorted."""
    faces = [(2, e) for id_ in side["cells"] for e in gmsh.model.getEntitiesForPhysicalGroup(2, id_)]
    return sorted({abs(t) for _, t in gmsh.model.getBoundary(faces, combined=False, oriented=False)})


def _ends(c):
    return [gmsh.model.getValue(0, t, []) for _, t in gmsh.model.getBoundary([(1, c)], oriented=False)]


def _slide_arcs(slide, sides):
    """Make the cells' arcs on the sliding circle transfinite: each gets its share of the divisions of the full turn,
    which must be whole, and both its ends must lie on the 360° / divisions grid that starts at 0°. The cell of every
    side must own such an arc."""
    r, n, name = slide["radius"], slide["divisions"], slide["name"]
    tol = 1e-6 * r
    arcs = set()
    for c in sorted({c for side in sides for c in _side_curves(side)}):
        ends = _ends(c)
        lo, hi = gmsh.model.getParametrizationBounds(1, c)
        mid = gmsh.model.getValue(1, c, [(lo[0] + hi[0]) / 2])
        if len(ends) != 2 or any(abs(math.hypot(p[0], p[1]) - r) > tol for p in ends + [mid]):
            continue
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
        if not arcs & set(_side_curves(side)):
            raise JobError(
                f"sliding interface {name}: the cell of the {side['side']} side has no arc on the sliding circle"
                f" (radius {r:g} mm); both sides must reach it"
            )


def _same(c, d, m, tol):
    """True when curve c moved by the transform m is curve d: the same ends and points of c moved lie on d."""
    if abs(gmsh.model.occ.getMass(1, c) - gmsh.model.occ.getMass(1, d)) > tol:
        return False
    ends_d = _ends(d)
    if any(min(math.dist(_apply(m, p), q) for q in ends_d) > tol for p in _ends(c)):
        return False
    lo, hi = gmsh.model.getParametrizationBounds(1, c)
    xyz = gmsh.model.getValue(1, c, [lo[0] + (hi[0] - lo[0]) * f for f in (0.25, 0.5, 0.75)])
    moved = [v for k in range(0, len(xyz), 3) for v in _apply(m, xyz[k : k + 3])]
    near = gmsh.model.getClosestPoint(1, d, moved)[0]
    return all(math.dist(moved[k : k + 3], near[k : k + 3]) <= tol for k in range(0, len(moved), 3))


def _periodic(sides):
    """Seams that a copy of the cell meets carry the same nodes: for curves c != d of a side's cells with T(c) == d for
    one of the side's transforms T, d is meshed as a copy of c (gmsh periodic). A curve a transform maps onto itself
    (a mirror line) needs nothing. Each curve is copied from one master at most, and a master is no copy."""
    box = gmsh.model.getBoundingBox(-1, -1)
    tol = 1e-6 * max(1.0, math.dist(box[:3], box[3:]))
    masters, slaves = set(), set()
    for side in sides:
        curves = _side_curves(side)
        for d in curves:
            if d in slaves or d in masters:
                continue
            for c in curves:
                if c >= d or c in slaves:
                    continue
                m = next((m for m in side["transforms"] if _same(c, d, m, tol)), None)
                if m is not None:
                    gmsh.model.mesh.setPeriodic(1, [d], [c], m)
                    masters.add(c)
                    slaves.add(d)
                    break


def _cell_entities(side):
    """[(entity, {element type: node tags}, nodes used, element centres, area)] of the side's cell bodies."""
    out = []
    for id_ in side["cells"]:
        for e in gmsh.model.getEntitiesForPhysicalGroup(2, id_):
            types, tags, nodes = gmsh.model.mesh.getElements(2, e)
            conn = {int(t): [int(n) for n in ns] for t, ns in zip(types, nodes)}
            used = sorted({n for ns in conn.values() for n in ns})
            per = len(nodes[0]) // len(tags[0])
            centres = []
            for k in (0, len(tags[0]) // 2, len(tags[0]) - 1):  # first, middle and last element: surely inside
                xyz = [gmsh.model.mesh.getNode(int(t))[0] for t in nodes[0][k * per : (k + 1) * per]]
                centres.append([sum(p[i] for p in xyz) / per for i in range(3)])
            out.append((e, conn, used, centres, gmsh.model.occ.getMass(2, e)))
    return out


def _land(sides, cells, folder):
    """labels[side][cell entity][copy] = index of the side's piece that copy lands on. The copies must cover every
    piece exactly (by area), or the drawing is not symmetric."""
    current = gmsh.model.getCurrent()
    gmsh.model.add("pieces")
    try:
        labels = []
        for side, ents in zip(sides, cells):
            pieces = side["pieces"]
            faces = [[t for _, t in import_brep(os.path.join(folder, p["file"]), 2)] for p in pieces]
            gmsh.model.occ.synchronize()
            areas = [sum(gmsh.model.occ.getMass(2, t) for t in ts) for ts in faces]
            covered = [0.0] * len(pieces)
            side_labels = []
            for _, _, _, centres, area in ents:
                copies = []
                for m in side["transforms"]:
                    moved = [_apply(m, p) for p in centres]
                    flat = [x for p in moved for x in p]
                    hits = [k for k, ts in enumerate(faces) if sum(gmsh.model.isInside(2, t, flat) for t in ts) == 3]
                    if len(hits) != 1:
                        x, y = moved[0][:2]
                        raise JobError(f"copy lands outside the drawing near ({x:.6g}, {y:.6g})")
                    covered[hits[0]] += area
                    copies.append(hits[0])
                side_labels.append(copies)
            for p, area, got in zip(pieces, areas, covered):
                if abs(got - area) > 1e-6 * area:
                    raise JobError(
                        f"not symmetric: piece {p['name']} ({p['file']}) has an area of {area:.6g} mm², "
                        f"but the copies of the cell landing on it cover {got:.6g} mm²"
                    )
            labels.append(side_labels)
        return labels
    finally:
        gmsh.model.remove()
        gmsh.model.setCurrent(current)


def _copy(sides, cells, labels):
    """Model "full": every side's cell entities copied by that side's transforms, each copy a discrete entity in the
    physical group of its piece's MAT_ID; mirrored copies reversed, shared nodes merged.
    Returns {side: {mat_id: (name, entities)}}."""
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
    shift = int(max(tags))
    gmsh.model.add("full")
    split, mirrored, entity, offset = {}, [], 0, 0
    for side, ents, side_labels in zip(sides, cells, labels):
        groups = split.setdefault(side["side"], {})
        for c, m in enumerate(side["transforms"]):
            owned = set()
            for (_, conn, used, _, _), copies in zip(ents, side_labels):
                entity += 1
                gmsh.model.addDiscreteEntity(2, entity)
                mine = [n for n in used if n not in owned]  # nodes the copy's earlier entities did not add
                owned.update(mine)
                moved = [v for n in mine for v in _apply(m, xyz[n])]
                gmsh.model.mesh.addNodes(2, entity, [n + offset for n in mine], moved)
                for typ, nodes in conn.items():
                    gmsh.model.mesh.addElementsByType(entity, typ, [], [n + offset for n in nodes])
                piece = side["pieces"][copies[c]]
                groups.setdefault(piece["mat_id"], (piece["name"], []))[1].append(entity)
                if _det(m) < 0:
                    mirrored.append((2, entity))
            offset += shift
    if mirrored:
        gmsh.model.mesh.reverse(mirrored)
    gmsh.model.mesh.removeDuplicateNodes()
    gmsh.model.mesh.renumberNodes()
    gmsh.model.mesh.renumberElements()
    members = {}
    for groups in split.values():
        for id_, (name, ents) in groups.items():
            members.setdefault(id_, (name, []))[1].extend(ents)
    for id_, (name, ents) in sorted(members.items()):
        gmsh.model.addPhysicalGroup(2, ents, id_, name=name)
    return split


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


def _side_edges(split, side):
    """{(node, node): number of the side's elements using that edge} in model "full"."""
    edges = Counter()
    for _, ents in split.get(side["side"], {}).values():
        for e in ents:
            for typ in gmsh.model.mesh.getElementTypes(2, e):
                en = gmsh.model.mesh.getElementEdgeNodes(typ, e, primary=True)
                edges.update(tuple(sorted((int(en[k]), int(en[k + 1])))) for k in range(0, len(en), 2))
    return edges


def _outline(side, folder, points):
    """For each point, the set of curves of the outer boundary of the side's pieces (their union) it lies on."""
    current = gmsh.model.getCurrent()
    gmsh.model.add("outline")
    try:
        faces = [dt for p in side["pieces"] for dt in import_brep(os.path.join(folder, p["file"]), 2)]
        if len(faces) > 1:
            gmsh.model.occ.fragment(faces[:1], faces[1:])
        gmsh.model.occ.synchronize()
        box = gmsh.model.getBoundingBox(-1, -1)
        tol = 1e-6 * max(1.0, math.dist(box[:3], box[3:]))
        flat = [v for p in points for v in p]
        on = [set() for _ in points]
        for _, c in gmsh.model.getEntities(1):
            if len(gmsh.model.getAdjacencies(1, c)[0]) != 1:  # between two pieces, or loose
                continue
            near = gmsh.model.getClosestPoint(1, c, flat)[0]  # on the bounded curve
            for k, p in enumerate(points):
                if math.dist(p, near[3 * k : 3 * k + 3]) <= tol:
                    on[k].add(c)
        return on
    finally:
        gmsh.model.remove()
        gmsh.model.setCurrent(current)


def _conform(sides, split, folder):
    """Every mesh edge that only one element of a side uses lies on the outer boundary of the side's pieces: the
    copies meet node to node everywhere else."""
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = {int(t): list(coords[3 * k : 3 * k + 3]) for k, t in enumerate(tags)}
    for side in sides:
        loose = [e for e, k in _side_edges(split, side).items() if k == 1]
        nodes = sorted({n for e in loose for n in e})
        on = dict(zip(nodes, _outline(side, folder, [xyz[n] for n in nodes])))
        bad = next((e for e in loose if not on[e[0]] & on[e[1]]), None)
        if bad is not None:
            x, y = [(a + b) / 2 for a, b in zip(xyz[bad[0]][:2], xyz[bad[1]][:2])]
            raise JobError(
                f"the copies of the cell do not match near ({x:.6g}, {y:.6g}) on the {side['side']} side: their"
                " meshes meet there without sharing nodes"
            )


def _on_circle(slide, sides, split):
    """Each side has exactly one node on the sliding circle at each of the divisions grid angles."""
    r, n, name = slide["radius"], slide["divisions"], slide["name"]
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
    for side in sides:
        nodes = {v for e in _side_edges(split, side) for v in e}
        angles = [_angle(xyz[v]) for v in nodes if abs(math.hypot(*xyz[v][:2]) - r) <= 1e-6 * r]
        steps = [a * n / 360 for a in angles]
        grid = {round(k) % n for k in steps if abs(k - round(k)) <= 1e-6}
        if len(angles) != n or len(grid) != n:
            raise JobError(
                f"sliding interface {name}: the {side['side']} side has {len(angles)} nodes on the circle"
                f" (radius {r:g} mm) where it needs one on each of the {n} divisions; its copies must cover the circle"
            )


def _mesh(job, folder, build):
    """Mesh the cell (gmsh initialized, model added), check it and copy it; model "full" is current.
    Returns (sides, slide, split)."""
    sides, slide = job["symmetric"]["sides"], job["symmetric"].get("slide")
    build(job, folder)  # one model holds the cells of both sides
    if slide:
        _slide_arcs(slide, sides)
    _periodic(sides)
    generate(job, 2)
    cells = [_cell_entities(side) for side in sides]
    labels = _land(sides, cells, folder)
    split = _copy(sides, cells, labels)
    _conform(sides, split, folder)
    if slide:
        _on_circle(slide, sides, split)
    return sides, slide, split


def check(job_path, build):
    """--check of a symmetric job: mesh the cell, copy it and run every check, nothing written."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add(job["model_name"])
        _mesh(job, folder, build)
    finally:
        gmsh.finalize()
    print("CHECK OK")


def run(job_path, build):
    """Read the job, mesh its cell with build(job, folder), copy it per side, write mesh.unv and replace
    job["mesh_file"] (and job["rotor_file"] when sliding: the moving side) with the finished .msh. Returns the job."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    msh = os.path.join(folder, "mesh.msh")
    outputs = [(msh, job["mesh_file"])]
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        _, slide, split = _mesh(job, folder, build)
        point = _marker(slide) if slide else None
        gmsh.option.setNumber("Mesh.MshFileVersion", MSH_VERSION)
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.write(os.path.join(folder, "mesh.unv"))
        if slide:
            outputs.append((os.path.join(folder, "rotor.msh"), job["rotor_file"]))
            for side, (path, _) in zip(("fixed", "moving"), outputs):
                groups = [(2, ents, id_, name) for id_, (name, ents) in sorted(split.get(side, {}).items())]
                if side == "moving":
                    groups.append((0, [point], slide["slide_mat_id"], slide["name"]))
                write_split(groups, path)
        else:
            gmsh.write(msh)
    finally:
        gmsh.finalize()
    publish(outputs)
    return job


def report(job):
    """The lines run_job prints: one MAT_ID line per piece assignment, the slide values, the files written."""
    slide = job["symmetric"].get("slide")
    seen = {(p["mat_id"], p["name"]): None for s in job["symmetric"]["sides"] for p in s["pieces"]}
    lines = [f"MAT_ID  {id_:>6}  {name}" for id_, name in seen]
    if slide:
        lines += slide_report({"slides": [slide]})
    lines.append(f"Wrote {job['mesh_file']}")
    if slide:
        lines.append(f"Wrote {job['rotor_file']}")
    return lines
