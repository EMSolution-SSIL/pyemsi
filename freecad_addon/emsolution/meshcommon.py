"""What mesher.py (3D) and mesher2d.py (2D) share. Runs in their process. Never import FreeCAD here."""

import json
import math
import os
import sys

import gmsh


class JobError(Exception):
    pass


FIELD_LISTS = {0: "PointsList", 1: "CurvesList", 2: "SurfacesList", 3: "VolumesList"}


def apply_size_fields(by_size):
    """by_size: {size: {dim: [entity tags]}}. One Constant field per size; the smallest size wins."""
    fields = []
    for size, by_dim in by_size.items():
        f = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumber(f, "VIn", size)
        for d, tags in by_dim.items():
            gmsh.model.mesh.field.setNumbers(f, FIELD_LISTS[d], tags)
        gmsh.model.mesh.field.setNumber(f, "IncludeBoundary", 1)
        fields.append(f)
    fmin = gmsh.model.mesh.field.add("Min")
    gmsh.model.mesh.field.setNumbers(fmin, "FieldsList", fields)
    gmsh.model.mesh.field.setAsBackgroundMesh(fmin)
    for opt in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints", "Mesh.MeshSizeFromCurvature"):
        gmsh.option.setNumber(opt, 0)


def _note(text):
    """Something the mesher fixed by itself; the runner shows stderr in FreeCAD's Report view."""
    print(f"NOTE: {text}", file=sys.stderr)


def transfinite_files(job, folder):
    """[(kind, item, path)] for job["transfinite"]: every edge file ("edge"), then every corner file ("corner")."""
    tf = job.get("transfinite") or {}
    out = [("edge", e, os.path.join(folder, f)) for e in tf.get("edges", []) for f in e["files"]]
    out += [("corner", b, os.path.join(folder, f)) for b in tf.get("bodies", []) for f in b["corner_files"]]
    return out


def _boundary(dim, tag):
    return list(dict.fromkeys(abs(t) for _, t in gmsh.model.getBoundary([(dim, tag)], combined=False, oriented=False)))


def _at(dim, tag):
    """Where an entity is, for messages: Gmsh tags mean nothing to the user."""
    return "({:g}, {:g}, {:g})".format(*(round(x, 6) + 0.0 for x in gmsh.model.occ.getCenterOfMass(dim, tag)))


def _share(n, lengths):
    """n >= len(lengths) elements over the pieces of a split edge, by length: each at least 1, the total stays n."""
    raw = [n * x / sum(lengths) for x in lengths]
    counts = [max(1, round(r)) for r in raw]
    while sum(counts) < n:
        counts[max(range(len(raw)), key=lambda i: raw[i] - counts[i])] += 1
    while sum(counts) > n:
        counts[max((i for i in range(len(raw)) if counts[i] > 1), key=lambda i: counts[i] - raw[i])] -= 1
    return counts


def _direction(curve, point):
    """Unit tangent of curve at its end point."""
    lo, hi = gmsh.model.getParametrizationBounds(1, curve)
    xyz = gmsh.model.getValue(0, point, [])
    u = min((lo[0], hi[0]), key=lambda v: math.dist(gmsh.model.getValue(1, curve, [v]), xyz))
    d = gmsh.model.getDerivative(1, curve, [u])
    size = math.hypot(*d)
    return [x / size for x in d]


def _turns(point, c1, c2):
    """True when the boundary changes direction at point, where curves c1 and c2 meet."""
    return abs(abs(sum(a * b for a, b in zip(_direction(c1, point), _direction(c2, point)))) - 1) > 1e-6


def _loop(face, curves, ends, at, start, body):
    """[(curve, its first point)] once around the face boundary from point start. at: point -> its curves."""
    loop, p, c = [], start, at[start][0]
    for _ in curves:  # bounded: a bad boundary cannot loop forever
        loop.append((c, p))
        p = ends[c][1] if ends[c][0] == p else ends[c][0]
        if p == start:
            break
        c = next((x for x in at[p] if x != c), c)
    if p != start or len(loop) != len(curves):
        raise JobError(
            f"structured body {body}: face at {_at(2, face)} boundary is not one loop (a hole?); it cannot be structured"
        )
    return loop


def _set_face(face, chosen, curve_set, body):
    """Check one face of a structured body (R4, R6) and make it transfinite. curve_set: curve -> (nodes, ...)."""
    curves = _boundary(2, face)
    if any(c not in curve_set for c in curves):
        raise JobError(f"structured body {body}: face at {_at(2, face)} has edges without Transfinite Edges")
    ends = {c: _boundary(1, c) for c in curves}
    if any(len(e) != 2 for e in ends.values()):
        raise JobError(
            f"structured body {body}: face at {_at(2, face)} has a closed edge (circle?); it cannot be structured"
        )
    at = {}  # point -> the curves meeting there
    for c in curves:
        for p in ends[c]:
            at.setdefault(p, []).append(c)
    points = set(at)
    _loop(face, curves, ends, at, min(points), body)  # a hole is the true error, whatever the corners
    corners = points if len(points) <= 4 else {p for p in chosen if p in points}
    if not corners:  # more than 4 points and none chosen: the points where the boundary turns
        corners = {p for p in points if len(at[p]) == 2 and _turns(p, *at[p])}
        if len(corners) in (3, 4):
            _note(
                f"structured body {body}: face at {_at(2, face)} has {len(points)} boundary points;"
                f" using the {len(corners)} where the boundary turns as corners"
            )
    if len(corners) not in (3, 4):
        raise JobError(
            f"structured body {body}: face at {_at(2, face)} has {len(points)} boundary points and {len(corners)} corners"
            " on it; it needs 3 or 4 (choose Corners in the Transfinite Body)"
        )
    for start in sorted(corners):  # 3 corners: Gmsh collapses the first one; its two sides must match
        loop = _loop(face, curves, ends, at, start, body)
        sides = []
        for c, p in loop:
            if p in corners:
                sides.append(0)
            sides[-1] += curve_set[c][0] - 1
        if len(sides) == 4 or sides[0] == sides[2]:
            break
    else:
        raise JobError(
            f"structured body {body}: face at {_at(2, face)} has 3 corners and its sides have {'/'.join(map(str, sorted(sides)))}"
            " elements; two of them must match"
        )
    if len(sides) == 4 and (sides[0] != sides[2] or sides[1] != sides[3]):
        raise JobError(
            f"structured body {body}: face at {_at(2, face)} opposite sides have {sides[0]}/{sides[2]} and"
            f" {sides[1]}/{sides[3]} elements; they must match"
        )
    gmsh.model.mesh.setTransfiniteSurface(face, cornerTags=[p for _, p in loop if p in corners])


def apply_transfinite(job, mapped, body_tags, dim):
    """Transfinite curves, faces and (3D) volumes from job["transfinite"]. Returns {curve: (nodes, item name)}.

    mapped: [(kind, item, file name, final dimtags)] in transfinite_files order, from the fragment map.
    body_tags: {mat_id: the body's final entity tags of dimension dim}.
    """
    curve_set, corners, edges = {}, {}, []  # final curve -> (nodes, distribution, coef, item name); body -> points

    def put(t, setting, owner):
        old = curve_set.setdefault(t, (*setting, owner))
        if old[:3] != setting:
            raise JobError(f"Transfinite Edges {old[3]} and {owner} give one edge different settings")

    for kind, item, name, dimtags in mapped:
        want = 1 if kind == "edge" else 0
        label = f"Transfinite Edges {item['name']}" if kind == "edge" else f"structured body {item['name']}"
        tags = [t for d, t in dimtags if d == want]
        if not tags or any(len(gmsh.model.getAdjacencies(want, t)[0]) == 0 for t in tags):
            raise JobError(f"{label}: {name} did not merge with the bodies")
        if kind == "corner":
            corners.setdefault(item["name"], set()).update(tags)
            continue
        if len(tags) == 1:  # whole edges first: the user set exactly these
            put(tags[0], (item["nodes"], item["distribution"], item["coef"]), item["name"])
        else:
            edges.append((label, item, name, tags))
    whole = dict(curve_set)
    for label, item, name, tags in edges:  # a touching body's vertex lies on the edge: share what is left
        split = f"{label}: {name} was split into {len(tags)} pieces by a touching body"
        if item["distribution"] == "Bump":
            raise JobError(f"{split}; a Bump edge cannot be shared out (use Uniform, or make the bodies match)")
        n, free = item["nodes"] - 1, [t for t in tags if t not in whole]
        fixed = {t: whole[t][0] - 1 for t in tags if t in whole}
        owners = ", ".join(dict.fromkeys(whole[t][3] for t in fixed))
        left = n - sum(fixed.values())
        if not free and left:
            raise JobError(
                f"{split}; it has {n} elements but all its pieces are set by other Transfinite Edges"
                f" ({sum(fixed.values())} elements: {owners})"
            )
        if len(free) > left:
            set_by = f", {n - left} of them set by {owners}" if fixed else ""
            raise JobError(f"{split}; it has {n} elements{set_by}: {left} left for {len(free)} pieces")
        counts = dict(zip(free, _share(left, [gmsh.model.occ.getMass(1, t) for t in free]))) if free else {}
        for t, c in counts.items():
            put(t, (c + 1, item["distribution"], item["coef"]), item["name"])
        parts = [f"{fixed[t]} (set by {whole[t][3]})" if t in fixed else str(counts[t]) for t in tags]
        _note(f"{split}; elements " + " + ".join(parts))
    for t, (nodes, distribution, coef, _) in curve_set.items():
        bump = distribution == "Bump"
        gmsh.model.mesh.setTransfiniteCurve(t, nodes, "Bump" if bump else "Progression", coef if bump else 1.0)
    for b in (job.get("transfinite") or {}).get("bodies", []):
        tags = body_tags[b["mat_id"]]
        faces = list(tags) if dim == 2 else []
        for v in tags if dim == 3 else []:
            vfaces = _boundary(3, v)
            if len(vfaces) not in (5, 6):
                where = "volume"
                if len(tags) > 1:  # name the piece of a sliced body by where it is
                    where = f"piece at {_at(3, v)}"
                raise JobError(
                    f"structured body {b['name']}: {where} has {len(vfaces)} faces, needs 5 or 6"
                    " (split by a touching body, or slice it further)"
                )
            faces += vfaces
        for f in dict.fromkeys(faces):
            _set_face(f, corners.get(b["name"], set()), curve_set, b["name"])
        for v in tags if dim == 3 else []:
            gmsh.model.mesh.setTransfiniteVolume(v)
    return {t: (nodes, item) for t, (nodes, _, _, item) in curve_set.items()}


def _check_full_quad(job, faces, tf_curves):
    """RC4: full-quad halves the 1D mesh on the edges of recombined faces that are not transfinite faces.
    faces: [(body name, face)] of those faces. tf_curves: {curve: (nodes, item name)}."""
    if job.get("options", {}).get("Mesh.RecombinationAlgorithm") not in (2, 3):
        return
    for body, face in faces:
        for c in _boundary(2, face):
            nodes, item = tf_curves.get(c, (1, None))
            if (nodes - 1) % 2:
                raise JobError(
                    f"recombine: full-quad needs an even number of elements on Transfinite Edges {item}"
                    f" next to recombined body {body}; use an even number or the Blossom or Simple algorithm"
                )


def apply_recombine(job, body_tags, dim, tf_curves):
    """Recombine the bodies listed in job["recombine"] (MAT_IDs) into quads (2D) or hexes (3D).

    body_tags: {mat_id: the body's final entity tags of dimension dim}.
    tf_curves: what apply_transfinite returned.
    """
    if dim == 3:
        _recombine_3d(job, body_tags, tf_curves)
        return
    structured = {b["mat_id"] for b in (job.get("transfinite") or {}).get("bodies", [])}
    names = {b["mat_id"]: b["name"] for b in job["bodies"]}
    faces = [(m, f) for m in job.get("recombine", []) for f in dict.fromkeys(body_tags[m])]
    _check_full_quad(job, [(names[m], f) for m, f in faces if m not in structured], tf_curves)
    for _, f in faces:
        gmsh.model.mesh.setRecombine(2, f)


def _recombine_3d(job, body_tags, tf_curves):
    """Quad faces on the boundary of the chosen bodies, except where Gmsh could not build the pyramids."""
    chosen = set(job.get("recombine", []))
    structured = {b["mat_id"] for b in (job.get("transfinite") or {}).get("bodies", [])}
    names = {v["mat_id"]: v["name"] for v in job["volumes"]}
    mat_of = {t: m for m, tags in body_tags.items() for t in tags}

    def kind(vol):
        m = mat_of[vol]
        return "hex" if m in chosen & structured else "stet" if m in structured else "tet"

    candidates = {}
    for m in job.get("recombine", []):
        for v in body_tags[m]:
            candidates.update(dict.fromkeys(_boundary(3, v)))
    kept, pairs, tet_side, plain = [], set(), None, []  # plain: (body, face) of kept faces with no hex side
    for face in candidates:
        sides = list(gmsh.model.getAdjacencies(2, face)[0])
        kinds = [kind(v) for v in sides]
        if "stet" not in kinds and kinds.count("tet") <= 1:
            kept.append(face)
            if "hex" not in kinds:
                plain.append((next(names[mat_of[v]] for v in sides if mat_of[v] in chosen), face))
            if "tet" in kinds and not tet_side:
                tet = names[mat_of[sides[kinds.index("tet")]]]
                tet_side = (next((names[mat_of[v]] for v in sides if kind(v) != "tet"), tet), tet)
        elif "hex" in kinds:
            stet = names[mat_of[sides[kinds.index("stet")]]]
            hexb = names[mat_of[sides[kinds.index("hex")]]]
            raise JobError(
                f"recombine: {stet} is structured and touches recombined structured body {hexb};"
                f" add {stet} to a Recombine item too"
            )
        else:
            pairs.add(tuple(sorted(names[mat_of[v]] for v in sides)))
    for a, b in sorted(pairs):
        if a == b:  # an internal face of one body
            continue
        _note(
            f"recombine: faces between {a} and {b} stay triangles (a quad face there would need pyramids on both sides)"
        )
    kept_set = set(kept)
    for m in job.get("recombine", []):
        if not kept_set & {f for v in body_tags[m] for f in _boundary(3, v)}:
            _note(f"recombine: {names[m]} has no face that can be recombined; it stays all triangles")
    if tet_side and job.get("options", {}).get("Mesh.Algorithm3D", 1) != 1:
        quad, tet = tet_side
        raise JobError(
            f"recombine: quad faces of {quad} next to tetrahedra of {tet} need the Delaunay volume algorithm"
        )
    _check_full_quad(job, plain, tf_curves)
    for face in kept:
        gmsh.model.mesh.setRecombine(2, face)


def run(job_path, build, dim):
    """Read the job, call build(job, folder) on a fresh model, mesh to dimension dim, write mesh.unv and
    replace job["mesh_file"] with the finished .msh. Returns the job."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    msh = os.path.join(folder, "mesh.msh")
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        build(job, folder)
        for name, value in job.get("options", {}).items():  # the user's mesh settings
            gmsh.option.setNumber(name, value)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)  # set last: the settings may not change it
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.logger.start()  # Gmsh only warns when a transfinite face or volume falls back to unstructured
        try:
            gmsh.model.mesh.generate(dim)
            failed = [m for m in gmsh.logger.get() if "cannot be meshed using the transfinite" in m]
        finally:
            gmsh.logger.stop()
        if failed:
            raise JobError(failed[0].split(":", 1)[-1].strip() + "; it would not be structured")
        gmsh.option.setNumber("Mesh.MshFileVersion", float(job["msh_version"]))
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.write(msh)
        gmsh.write(os.path.join(folder, "mesh.unv"))
    finally:
        gmsh.finalize()
    try:
        os.replace(msh, job["mesh_file"])  # only a finished mesh replaces the solver's file
    except PermissionError:
        raise JobError(f"Could not replace {job['mesh_file']}: it is read-only or open in another program.") from None
    return job


def main(argv, script, run_job):
    for stream in (sys.stdout, sys.stderr):  # the runner reads UTF-8, whatever the console code page
        stream.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) != 2:
        print(f"ERROR: usage: {script} <job.json>", file=sys.stderr)
        return 1
    try:
        run_job(argv[1])
    except Exception as exc:  # anything -> one clean ERROR line for the runner
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0
