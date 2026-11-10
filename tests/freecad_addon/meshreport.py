"""Reads a mesh the add-on wrote and describes it in text. Gmsh API only: never import FreeCAD here."""

import collections
import json
import math
import os

import gmsh
import numpy as np

TYPE_NAMES = {2: "triangles", 3: "quadrangles", 4: "tetrahedra", 5: "hexahedra", 6: "prisms", 7: "pyramids"}
FACETS = {  # element type -> its facets as corner indexes: edges in 2D, triangles and quadrangles in 3D
    2: [(0, 1), (1, 2), (2, 0)],
    3: [(0, 1), (1, 2), (2, 3), (3, 0)],
    4: [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)],
    5: [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)],
    6: [(0, 1, 2), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (0, 2, 5, 3)],
    7: [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 1, 2, 3)],
}
CORNER_TETS = {  # element type -> (corner, its three neighbours), each a tetrahedron of positive volume when valid
    4: [(0, 1, 2, 3)],
    5: [(0, 1, 3, 4), (1, 2, 0, 5), (2, 3, 1, 6), (3, 0, 2, 7), (4, 7, 5, 0), (5, 4, 6, 1), (6, 5, 7, 2), (7, 6, 4, 3)],
    6: [(0, 1, 2, 3), (1, 2, 0, 4), (2, 0, 1, 5), (3, 5, 4, 0), (4, 3, 5, 1), (5, 4, 3, 2)],
    7: [(0, 1, 3, 4), (1, 2, 0, 4), (2, 3, 1, 4), (3, 0, 2, 4)],
}
CORNER_TRIS = {2: [(0, 1, 2)], 3: [(0, 1, 3), (1, 2, 0), (2, 3, 1), (3, 0, 2)]}  # 2D: (corner, next, previous)


def quality(msh_path, copied=()):
    """What a mesh file holds and whether it is sound, from the physical groups of its highest dimension:
    {"dim", "types": {type name: count}, "inverted", "faces_in_three", "kept", "boundary"}. Inverted: an element
    with a corner whose tetrahedron (3D) or triangle (2D, against the normal of the drawing's plane, +Z for XY) is not
    positive; a ZX drawing is held to the orientation most of its elements have. faces_in_three: facets (faces in 3D,
    edges in 2D) shared by 3 or more elements. kept: the facets on the surface of the elements of the MAT_IDs copied
    that another element shares. boundary: the facets used by one element, as (MAT_ID, centre, outward normal, size)
    arrays."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh_path)
        tags, coords, _ = gmsh.model.mesh.getNodes()
        at = np.zeros((int(tags.max()) + 1, 3))
        at[tags.astype(np.int64)] = np.reshape(coords, (-1, 3))
        dim = max(d for d, _ in gmsh.model.getPhysicalGroups())
        blocks = []  # (element type, connectivity, MAT_ID)
        for d, tag in gmsh.model.getPhysicalGroups(dim):
            for ent in gmsh.model.getEntitiesForPhysicalGroup(d, tag):
                for etype, etags, conn in zip(*gmsh.model.mesh.getElements(d, ent)):
                    corners = gmsh.model.mesh.getElementProperties(etype)[5]
                    per = len(conn) // len(etags)
                    blocks.append((int(etype), np.reshape(conn, (-1, per))[:, :corners].astype(np.int64), tag))
    finally:
        gmsh.finalize()
    types = collections.Counter()
    for etype, conn, _ in blocks:
        types[TYPE_NAMES.get(etype, f"type {etype}")] += len(conn)
    inverted = _inverted(at, blocks, dim)
    facets, owner_mat, owner_centre = {}, {}, {}
    for etype, conn, mat_id in blocks:
        centre = at[conn].mean(axis=1)
        for f in FACETS[etype]:
            facets.setdefault(len(f), []).append(conn[:, f])
            owner_mat.setdefault(len(f), []).append(np.full(len(conn), mat_id))
            owner_centre.setdefault(len(f), []).append(centre)
    over, kept, mats, centres, normals, sizes = 0, 0, [], [], [], []
    for n, parts in facets.items():
        each = np.vstack(parts)
        _, first, inverse, counts = np.unique(
            np.sort(each, axis=1), axis=0, return_index=True, return_inverse=True, return_counts=True
        )
        over += int((counts > 2).sum())
        of_copies = np.bincount(inverse.ravel(), np.isin(np.concatenate(owner_mat[n]), list(copied)), len(counts))
        kept += int(((of_copies == 1) & (counts == 2)).sum())
        once = first[counts == 1]
        nodes = at[each[once]]
        centre = nodes.mean(axis=1)
        away = centre - np.vstack(owner_centre[n])[once]
        if dim == 3:
            normal = np.cross(nodes[:, 1] - nodes[:, 0], nodes[:, -1] - nodes[:, 0])
        else:  # in the plane, across the edge
            along = (nodes[:, 1] - nodes[:, 0]) / np.linalg.norm(nodes[:, 1] - nodes[:, 0], axis=1)[:, None]
            normal = away - np.einsum("ij,ij->i", away, along)[:, None] * along
        normal *= np.where(np.einsum("ij,ij->i", normal, away) < 0, -1.0, 1.0)[:, None]
        normal /= np.linalg.norm(normal, axis=1)[:, None]
        mats.append(np.concatenate(owner_mat[n])[once])
        centres.append(centre)
        normals.append(normal)
        sizes.append(np.linalg.norm(nodes - centre[:, None, :], axis=2).max(axis=1))
    boundary = tuple(np.concatenate(x) if x else np.zeros(0) for x in (mats, centres, normals, sizes))
    return {
        "dim": dim,
        "types": dict(types),
        "inverted": inverted,
        "faces_in_three": over,
        "kept": kept,
        "boundary": boundary,
    }


def _inverted(at, blocks, dim):
    if dim == 3:
        bad = 0
        for etype, conn, _ in blocks:
            worst = np.full(len(conn), np.inf)
            for a, b, c, d in CORNER_TETS[etype]:
                p = at[conn[:, a]]
                vol = np.einsum("ij,ij->i", np.cross(at[conn[:, b]] - p, at[conn[:, c]] - p), at[conn[:, d]] - p)
                worst = np.minimum(worst, vol)
            bad += int((worst <= 0).sum())
        return bad
    every = np.vstack([at[conn].reshape(-1, 3) for _, conn, _ in blocks])
    axis = int(np.argmin(np.ptp(every, axis=0)))  # the normal of the drawing's plane
    signs = []
    for etype, conn, _ in blocks:
        worst, best = np.full(len(conn), np.inf), np.full(len(conn), -np.inf)
        for a, b, c in CORNER_TRIS[etype]:
            p = at[conn[:, a]]
            area = np.cross(at[conn[:, b]] - p, at[conn[:, c]] - p)[:, axis]
            worst, best = np.minimum(worst, area), np.maximum(best, area)
        signs.append(np.where(worst > 0, 1, np.where(best < 0, -1, 0)))
    signs = np.concatenate(signs)
    want = 1 if axis == 2 or (signs > 0).sum() >= (signs < 0).sum() else -1
    return int((signs != want).sum())


def groups(msh_path):
    """{MAT_ID: (name, element count)} of the physical groups of the highest dimension in the mesh file
    (volumes in 3D, surfaces in 2D); lower-dimension groups such as excitation surfaces are left out."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh_path)
        found = gmsh.model.getPhysicalGroups()
        if not found:
            return {}
        top = max(dim for dim, _ in found)
        out = {}
        for dim, tag in found:
            if dim != top:
                continue
            count = 0
            for entity in gmsh.model.getEntitiesForPhysicalGroup(dim, tag):
                count += sum(len(tags) for tags in gmsh.model.mesh.getElements(dim, entity)[1])
            out[tag] = (gmsh.model.getPhysicalName(dim, tag), count)
        return out
    finally:
        gmsh.finalize()


def _nodes(msh_path):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh_path)
        return len(gmsh.model.mesh.getNodes()[0])
    finally:
        gmsh.finalize()


def _coords(msh_path):
    """The node coordinates of a mesh file as (x, y, z) tuples."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh_path)
        c = gmsh.model.mesh.getNodes()[1]
    finally:
        gmsh.finalize()
    return [tuple(c[i : i + 3]) for i in range(0, len(c), 3)]


def _marker(msh_path, dim, group=None):
    """(element count, node coordinates) of a physical group of dimension dim (the first one when group is None) in a
    mesh file: the slide point (dim 0) or slide edge (dim 1). None if there is none."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh_path)
        tags = [t for _, t in gmsh.model.getPhysicalGroups(dim) if group in (None, t)]
        if not tags:
            return None
        count = 0
        for e in gmsh.model.getEntitiesForPhysicalGroup(dim, tags[0]):
            count += sum(len(t) for t in gmsh.model.mesh.getElements(dim, e)[1])
        c = gmsh.model.mesh.getNodesForPhysicalGroup(dim, tags[0])[1]
        return count, [tuple(c[i : i + 3]) for i in range(0, len(c), 3)]
    finally:
        gmsh.finalize()


def _point(msh_path, group=None):
    """Coordinates of the node of a point group (the first one when group is None) in a mesh file; None if absent."""
    found = _marker(msh_path, 0, group)
    return found[1][0] if found else None


def slide_check(fixed_msh, rotor_msh, on_slide):
    """(nodes on the slide in fixed_msh, in rotor_msh, whether the two coordinate sets are equal within 1e-9).
    on_slide(point) -> bool picks the nodes."""
    fixed, rotor = (sorted(p for p in _coords(m) if on_slide(p)) for m in (fixed_msh, rotor_msh))
    same = len(fixed) == len(rotor) and all(math.dist(p, q) <= 1e-9 for p, q in zip(fixed, rotor))
    return len(fixed), len(rotor), same


def _plane(period, side, tol):
    """f(point) -> True on the first (side 0) or second (side 1) periodic boundary of a job's "periodic"."""
    if period["kind"] == "rotation":
        a = math.radians(period["start"] + side * period["angle"])
        return lambda p: (
            abs(p[0] * math.sin(a) - p[1] * math.cos(a)) < tol and p[0] * math.cos(a) + p[1] * math.sin(a) > -tol
        )
    axis = next(k for k, x in enumerate(period["vector"]) if x)
    at = period["start"] + side * period["vector"][axis]
    return lambda p: abs(p[axis] - at) < tol


def _move(period, p):
    if period["kind"] == "rotation":
        a = math.radians(period["angle"])
        return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a), p[2])
    return tuple(x + d for x, d in zip(p, period["vector"]))


def periodic_check(msh_path, period):
    """True when the nodes on the first periodic boundary, moved by one period, are the nodes on the second."""
    pts = _coords(msh_path)
    lo, hi = [min(c) for c in zip(*pts)], [max(c) for c in zip(*pts)]
    tol = 1e-6 * math.dist(lo, hi)
    on_first, on_second = (_plane(period, side, tol) for side in (0, 1))
    first, left = [p for p in pts if on_first(p)], [p for p in pts if on_second(p)]
    for p in first:
        q = _move(period, p)
        match = next((k for k, r in enumerate(left) if math.dist(q, r) < tol), None)
        if match is None:
            return False
        left.pop(match)
    return bool(first) and not left


def _on_slide(slide, marker, period, tol=1e-6):
    """f(node) -> True on a slide curve or surface, from the marker's nodes: the circle (2D) or cylinder (3D) about Z
    through the slide point or edge, the plane z = const of an axial gap, or the line or plane through the marker
    along the motion (the axis the period moves along)."""
    point = marker[0]
    if slide["kind"] == "rotational":
        r = math.hypot(point[0], point[1])
        return lambda p: abs(math.hypot(p[0], p[1]) - r) < tol
    if slide["kind"] == "axial":
        return lambda p: abs(p[2] - point[2]) < tol
    axis = next(k for k, x in enumerate(period["vector"]) if x)
    fixed = [k for k in range(3) if k != axis and all(abs(q[k] - point[k]) < tol for q in marker)]
    return lambda p: all(abs(p[k] - point[k]) < tol for k in fixed)


def _round(p):
    return ", ".join(f"{round(c, 9) + 0.0:g}" for c in p)


def _angle(p):
    return round(math.degrees(math.atan2(p[1], p[0])), 6) % 360


def slide_lines(data):
    """The slide and periodic checks of a sliding job: nodes on each slide in both files, the slide point, the period."""
    fixed, rotor = data["mesh_file"], data["rotor_file"]
    names = os.path.basename(fixed), os.path.basename(rotor)
    lines = []
    dim = 1 if "volumes" in data else 0  # 3D: a slide edge; 2D: a slide point
    for s in data["slides"]:
        found = _marker(rotor, dim, s["slide_mat_id"])
        if found is None:
            what = "slide edge" if dim else "slide point"
            raise RuntimeError(f"{s['name']}: no {what} (group {s['slide_mat_id']}) in {names[1]}")
        count, marker = found
        n_fixed, n_rotor, same = slide_check(fixed, rotor, _on_slide(s, marker, data.get("periodic")))
        want = s["divisions"] if s["full"] else s["divisions"] + 1
        if s["kind"] == "axial" and min(math.hypot(p[0], p[1]) for p in marker) < 1e-9:
            want = want * s["cross_divisions"] + 1  # a disc: rings round its centre node
        elif dim:
            want *= s["cross_divisions"] + 1
        lines.append(
            f"Slide {s['name']} (SLIDE_MAT_ID {s['slide_mat_id']}, {s['divisions']} divisions): {n_fixed} nodes in"
            f" {names[0]}, {n_rotor} in {names[1]}, {want} expected"
        )
        lines.append(f"slide nodes match: {'yes' if same and n_fixed == want else 'no'}")
        out = max(marker, key=lambda p: math.hypot(p[0], p[1]))  # off the Z axis, for the angle
        where = f", angle {_angle(out):g}°" if s["kind"] != "linear" else ""
        stray = "none" if _marker(fixed, dim) is None else "one too (wrong)"
        if dim:
            b = max(marker, key=lambda p: math.dist(p, marker[0]))  # the two ends: the nodes farthest apart
            a, b = sorted((max(marker, key=lambda p: math.dist(p, b)), b), key=lambda p: [round(c, 6) for c in p])
            lines.append(
                f"slide edge in {names[1]}: {count} line elements from ({_round(a)}) to ({_round(b)}){where};"
                f" {stray} in {names[0]}"
            )
        else:
            x, y = (round(c, 9) + 0.0 for c in marker[0][:2])
            lines.append(f"slide point in {names[1]} at ({x:g}, {y:g}){where}; {stray} in {names[0]}")
    if data.get("periodic"):
        for path, name in zip((fixed, rotor), names):
            lines.append(f"{name} periodic: {'yes' if periodic_check(path, data['periodic']) else 'no'}")
    return lines


def checklist_text(checklist):
    return "\nCheck by hand:\n" + "".join(f"- {text}\n" for text in checklist) if checklist else ""


def report(case_dir, job, checklist=()):
    """The report of one case: the MAT_ID table (per file for a sliding job), the slide checks, the case's checklist.
    job is the path of the job.json the mesher ran. Raises if a body or the air of the job is missing or empty."""
    with open(job, encoding="utf-8") as fh:
        data = json.load(fh)
    bodies = data.get("bodies") or data.get("volumes") or []
    air = data.get("air")
    lines = [f"Case {os.path.basename(os.path.normpath(case_dir))}"]
    sides = list(air["sides"].values()) if air and "sides" in air else []
    if sides:  # sliding: the fixed side in the mesh file, the moving side in the rotor file
        moving = set(data["moving"])
        fixed_bodies = [b for b in bodies if b["mat_id"] not in moving]
        moving_bodies = [b for b in bodies if b["mat_id"] in moving]
        parts = [
            ("Fixed side", data["mesh_file"], fixed_bodies + [air["sides"]["fixed"]]),
            ("Moving side", data["rotor_file"], moving_bodies + [air["sides"]["moving"]]),
        ]
    else:
        parts = [("Mesh", data["mesh_file"], bodies + ([air] if air else []))]
    for title, path, expected in parts:
        found = groups(path)
        lines += ["", f"{title}: {os.path.basename(path)}", f"Nodes {_nodes(path)}", "MAT_ID  name  elements"]
        for item in expected:
            name, count = found.get(item["mat_id"], (item["name"], 0))
            if count == 0 and item in sides:  # a sliding air side holds no air when a body fills its cell
                lines.append(f"(no {item['name']}: that side has no air)")
                continue
            if count == 0:
                raise RuntimeError(
                    f"{item['name']} (MAT_ID {item['mat_id']}) has no elements in {os.path.basename(path)}"
                )
            lines.append(f"MAT_ID {item['mat_id']:>4}  {name}  {count}")
    if data.get("slides"):
        lines += [""] + slide_lines(data)
    return "\n".join(lines) + "\n" + checklist_text(checklist)


def compare_sample(job, sample_dir):
    """Compare a 2D slide case with a reference model in sample_dir (pre_geom2D.msh, rotor_mesh2D.msh): the angles of
    the slide nodes in each file and of the slide point. Only angles: the sample may use another length unit."""
    with open(job, encoding="utf-8") as fh:
        data = json.load(fh)
    ours = data["mesh_file"], data["rotor_file"]
    theirs = os.path.join(sample_dir, "pre_geom2D.msh"), os.path.join(sample_dir, "rotor_mesh2D.msh")
    mine, ref = _point(ours[1], data["slides"][0]["slide_mat_id"]), _point(theirs[1])
    lines = [f"Sample {sample_dir}"]
    for path, sample in zip(ours, theirs):
        angles = []
        for p, m in ((mine, path), (ref, sample)):
            r = math.hypot(p[0], p[1])
            angles.append(sorted(_angle(q) for q in _coords(m) if abs(math.hypot(q[0], q[1]) - r) < 1e-6 * r))
        same = len(angles[0]) == len(angles[1]) and all(abs(a - b) < 1e-6 for a, b in zip(*angles))
        lines.append(
            f"slide node angles {os.path.basename(path)}: {len(angles[0])} here, {len(angles[1])} in the sample,"
            f" {'same' if same else 'different'}"
        )
    a, b = _angle(mine), _angle(ref)
    lines.append(
        f"slide point angle: {a:g} deg here, {b:g} deg in the sample, {'same' if abs(a - b) < 1e-6 else 'different'}"
    )
    return lines
