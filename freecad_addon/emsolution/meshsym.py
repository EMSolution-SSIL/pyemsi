"""Symmetric mesh: mesh the cell, copy the mesh by the transforms and give every copy the MAT_ID of the drawn piece it
lands on. Runs in the mesher process (mesher2d.run_job calls run for a job with a "symmetric" key).
Never import FreeCAD here."""

import json
import math
import os

import gmsh

from meshcommon import JobError, generate, import_brep, publish, slide_report, write_split


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


def _slide_arcs(slide):
    """Make the cell's arcs on the sliding circle transfinite: each gets its share of the divisions of the full turn,
    which must be whole, and both its ends must lie on the 360° / divisions grid that starts at 0°."""
    r, n, name = slide["radius"], slide["divisions"], slide["name"]
    tol = 1e-6 * r
    found = False
    for _, c in gmsh.model.getEntities(1):
        ends = [gmsh.model.getValue(0, t, []) for _, t in gmsh.model.getBoundary([(1, c)], oriented=False)]
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
        found = True
    if not found:
        raise JobError(f"sliding interface {name}: the cell has no arc on its circle (radius {r:g} mm)")


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


def run(job_path, build):
    """Read the job, mesh its cell with build(job, folder), copy it per side, write mesh.unv and replace
    job["mesh_file"] (and job["rotor_file"] when sliding: the moving side) with the finished .msh. Returns the job."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    sides, slide = job["symmetric"]["sides"], job["symmetric"].get("slide")
    msh = os.path.join(folder, "mesh.msh")
    outputs = [(msh, job["mesh_file"])]
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        build(job, folder)  # one model holds the cells of both sides
        if slide:
            _slide_arcs(slide)
        generate(job, 2)
        cells = [_cell_entities(side) for side in sides]
        labels = _land(sides, cells, folder)
        split = _copy(sides, cells, labels)
        point = _marker(slide) if slide else None
        gmsh.option.setNumber("Mesh.MshFileVersion", float(job["msh_version"]))
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.write(os.path.join(folder, "mesh.unv"))
        if slide:
            outputs.append((os.path.join(folder, "rotor.msh"), job["rotor_file"]))
            for side, (path, _) in zip(("fixed", "moving"), outputs):
                groups = [(2, ents, id_, name) for id_, (name, ents) in sorted(split.get(side, {}).items())]
                if side == "moving":
                    groups.append((0, [point], slide["slide_mat_id"], slide["name"]))
                write_split(groups, path, job["msh_version"])
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
