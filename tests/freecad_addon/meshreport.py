"""Reads a mesh the add-on wrote and describes it in text. Gmsh API only: never import FreeCAD here."""

import json
import math
import os

import gmsh


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


def _point(msh_path, group=None):
    """Coordinates of the node of a point group (the first one when group is None) in a mesh file; None if absent."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh_path)
        tags = [t for _, t in gmsh.model.getPhysicalGroups(0) if group in (None, t)]
        return tuple(gmsh.model.mesh.getNodesForPhysicalGroup(0, tags[0])[1][:3]) if tags else None
    finally:
        gmsh.finalize()


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


def _on_slide(slide, point, period, tol=1e-6):
    """f(node) -> True on a 2D slide curve: the circle through the slide point, or the line through it along the
    motion (the axis the period moves along)."""
    if slide["kind"] == "rotational":
        r = math.hypot(point[0], point[1])
        return lambda p: abs(math.hypot(p[0], p[1]) - r) < tol
    axis = next(k for k, x in enumerate(period["vector"]) if x)
    return lambda p: all(abs(p[k] - point[k]) < tol for k in range(3) if k != axis)


def _angle(p):
    return round(math.degrees(math.atan2(p[1], p[0])), 6) % 360


def slide_lines(data):
    """The slide and periodic checks of a sliding job: nodes on each slide in both files, the slide point, the period."""
    fixed, rotor = data["mesh_file"], data["rotor_file"]
    names = os.path.basename(fixed), os.path.basename(rotor)
    lines = []
    for s in data["slides"]:
        point = _point(rotor, s["slide_mat_id"])
        if point is None:
            raise RuntimeError(f"{s['name']}: no slide point (group {s['slide_mat_id']}) in {names[1]}")
        n_fixed, n_rotor, same = slide_check(fixed, rotor, _on_slide(s, point, data.get("periodic")))
        want = s["divisions"] if s["full"] else s["divisions"] + 1
        lines.append(
            f"Slide {s['name']} (SLIDE_MAT_ID {s['slide_mat_id']}, {s['divisions']} divisions): {n_fixed} nodes in"
            f" {names[0]}, {n_rotor} in {names[1]}, {want} expected"
        )
        lines.append(f"slide nodes match: {'yes' if same and n_fixed == want else 'no'}")
        where = f", angle {_angle(point):g}°" if s["kind"] == "rotational" else ""
        stray = "none" if _point(fixed) is None else "one too (wrong)"
        x, y = (round(c, 9) + 0.0 for c in point[:2])
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
