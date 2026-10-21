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


def claim_air(air_tags, owner):
    """The air's final top-dimension tags that no body owns, sorted. air_tags: all the air's final tags.
    owner: {final tag: body name}. A body wins where it overlaps the air."""
    tags = sorted(t for t in set(air_tags) if t not in owner)
    if not tags:
        raise JobError("the air region is fully covered by bodies")
    return tags


def air_items(job):
    """The air's {"mat_id", "name"} entries: the air of a static job, or its fixed and moving side (sliding)."""
    air = job.get("air")
    if not air:
        return []
    return [air["sides"]["fixed"], air["sides"]["moving"]] if "sides" in air else [air]


def split_air(air_tags, moving_cell_tags):
    """The air's tags (from claim_air) on the fixed and on the moving side: a piece inside a moving cell is moving."""
    moving = set(moving_cell_tags)
    return [t for t in air_tags if t not in moving], [t for t in air_tags if t in moving]


def import_brep(path, *dims):
    """All entities of a BREP file; every one must have a dimension in dims."""
    tags = gmsh.model.occ.importShapes(path, highestDimOnly=True)
    if not tags or any(d not in dims for d, _ in tags):
        raise JobError(f"{os.path.basename(path)}: expected {'/'.join(map(str, dims))}D entities, got {tags}")
    return tags


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


def _loop(face, curves, ends, at, start, label):
    """[(curve, its first point)] once around the face boundary from point start. at: point -> its curves.
    label: who owns the face, for the message."""
    loop, p, c = [], start, at[start][0]
    for _ in curves:  # bounded: a bad boundary cannot loop forever
        loop.append((c, p))
        p = ends[c][1] if ends[c][0] == p else ends[c][0]
        if p == start:
            break
        c = next((x for x in at[p] if x != c), c)
    if p != start or len(loop) != len(curves):
        raise JobError(f"{label}: face at {_at(2, face)} boundary is not one loop (a hole?); it cannot be structured")
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
    # a hole is the true error, whatever the corners
    _loop(face, curves, ends, at, min(points), f"structured body {body}")
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
        loop = _loop(face, curves, ends, at, start, f"structured body {body}")
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
    names = {v["mat_id"]: v["name"] for v in job["volumes"] + air_items(job)}
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


def apply_slides(slides, mapped, dim):
    """The same uniform division on both sides of every slide surface. Returns {slide_mat_id: the marker's final tags}.

    mapped: per slide, ([(file name, final dimtags)] of its pieces, (marker file name, final dimtags)).
    A full turn is built in two halves of divisions / 2 each; a sector or a line gets divisions. A piece that a
    touching body split further shares its count out by length. In 3D the pieces are faces (see _slide_face) and the
    marker is the slide edge, a generatrix of the surface.
    """
    markers = {}
    for slide, (pieces, (marker, marker_tags)) in zip(slides, mapped):
        name = f"sliding interface {slide['name']}"
        n = slide["divisions"] // 2 if slide["full"] else slide["divisions"]
        found = [t for d, t in marker_tags if d == dim - 2]  # the slide point (2D) or the slide edge's lines (3D)
        if not found or any(len(gmsh.model.getAdjacencies(dim - 2, t)[0]) == 0 for t in found):
            raise JobError(f"{name}: {marker} did not merge with the model")
        markers[slide["slide_mat_id"]] = found
        done = {}  # 3D: curve -> elements, so a curve between two faces gets one count
        for file, dimtags in pieces:
            tags = [t for d, t in dimtags if d == dim - 1]
            if not tags or any(len(gmsh.model.getAdjacencies(dim - 1, t)[0]) == 0 for t in tags):
                raise JobError(f"{name}: {file} did not merge with the model")
            if dim == 3:
                _slide_face(slide, f"{name}: {file}", tags, n, found[0], done)
                continue
            if len(tags) > n:
                raise JobError(f"{name}: {file} was split into {len(tags)} pieces by touching bodies, more than {n}")
            counts = _share(n, [gmsh.model.occ.getMass(dim - 1, t) for t in tags])
            if len(tags) > 1:
                parts = " + ".join(map(str, counts))
                _note(f"{name}: {file} was split into {len(tags)} pieces by a touching body; elements {parts}")
            for t, c in zip(tags, counts):
                gmsh.model.mesh.setTransfiniteCurve(t, c + 1)
    return markers


def slide_split(job, bodies, tags, markers, dim):
    """{"fixed": groups, "moving": groups} for run (see write_split): every body and air side that has elements on
    its side, and the slide markers (from apply_slides) on the moving side only, as physical groups of their own.

    bodies: the job's bodies (2D) or volumes (3D). tags: {mat_id: final tags of dimension dim} of bodies and air."""
    moving = set(job["moving"])
    split = {"fixed": [], "moving": []}
    sides = ["moving" if b["mat_id"] in moving else "fixed" for b in bodies] + ["fixed", "moving"]
    for b, side in zip(bodies + air_items(job), sides):
        if tags[b["mat_id"]]:
            split[side].append((dim, tags[b["mat_id"]], b["mat_id"], b["name"]))
    for s in job["slides"]:  # the slide point (2D) or slide edge (3D) goes to the moving side only
        gmsh.model.addPhysicalGroup(dim - 2, markers[s["slide_mat_id"]], s["slide_mat_id"], name=s["name"])
        split["moving"].append((dim - 2, markers[s["slide_mat_id"]], s["slide_mat_id"], s["name"]))
    return split


def _unit(v):
    """v scaled to length 1 and turned so that its largest component is positive: one direction for a line,
    whichever way it runs."""
    size = math.hypot(*v)
    sign = 1 if max(v, key=abs) > 0 else -1
    return [sign * x / size for x in v]


def _slide_face(slide, label, faces, n, edge, done):
    """3D: make one slide face transfinite with "Left" triangles and its corners in the same order on every face, so
    that the mesh of the surface is the same after a shift of one division.

    Its sides along the motion (arcs about Z at one radius and height; lines at one position across a linear plane)
    get n elements, the sides across it cross_divisions; a side split by a touching body shares its count by length.
    The corners are where a side along the motion meets one across, plus a point on the Z axis: a half disc that
    reaches the axis has 3 corners, and Gmsh collapses the first one, the axis point. edge: a line of the slide edge,
    which runs across the motion. done: {curve: elements} so far for this interface.
    """
    if len(faces) > 1:
        raise JobError(f"{label} was split into {len(faces)} faces by touching bodies; keep the bodies off it")
    face = faces[0]
    box = gmsh.model.getBoundingBox(-1, -1)
    tol = 1e-6 * math.dist(box[:3], box[3:])
    curves = _boundary(2, face)
    ends = {c: _boundary(1, c) for c in curves}
    if any(len(e) != 2 for e in ends.values()):
        raise JobError(f"{label}: the face at {_at(2, face)} has a closed edge; it cannot be structured")
    at = {}  # point -> the curves meeting there
    for c in curves:
        for p in ends[c]:
            at.setdefault(p, []).append(c)
    xyz = {p: gmsh.model.getValue(0, p, []) for p in at}
    rotational = slide["kind"] != "linear"
    if not rotational:
        across = _unit([y - x for x, y in zip(*(gmsh.model.getValue(0, p, []) for p in _boundary(1, edge)))])

    def level(p):
        """What stays the same along the motion: radius and height, or the position across a linear motion."""
        return (math.hypot(p[0], p[1]), p[2]) if rotational else (sum(x * g for x, g in zip(p, across)),)

    along = {}
    for c in curves:
        lo, hi = (b[0] for b in gmsh.model.getParametrizationBounds(1, c))
        pts = [level(gmsh.model.getValue(1, c, [lo + (hi - lo) * k / 4])) for k in range(5)]
        along[c] = all(abs(x - y) < tol for p in pts for x, y in zip(p, pts[0]))
    axis = [p for p in at if rotational and math.hypot(*xyz[p][:2]) < tol]
    corners = [p for p in at if p in axis or len({along[c] for c in at[p]}) == 2]
    if (len(corners), len(axis)) not in ((4, 0), (3, 1)):
        raise JobError(
            f"{label}: the face at {_at(2, face)} has {len(corners)} corners; it needs 4 (or 3, one on the Z axis)"
        )
    # u: the corner's coordinate along the motion; v: along the slide edge
    if rotational:
        cx, cy, _ = gmsh.model.occ.getCenterOfMass(2, face)
        mid = math.atan2(cy, cx)
        u = {p: math.remainder(math.atan2(xyz[p][1], xyz[p][0]) - mid, math.tau) for p in corners if p not in axis}
        v = {p: xyz[p][2] if slide["kind"] == "rotational" else math.hypot(*xyz[p][:2]) for p in u}
    else:
        a, b = (xyz[p] for p in ends[next(c for c in curves if along[c])])
        motion = _unit([y - x for x, y in zip(a, b)])
        u = {p: sum(x * m for x, m in zip(xyz[p], motion)) for p in corners}
        v = {p: level(xyz[p])[0] for p in corners}
    if axis:
        order = axis + sorted(u, key=u.get)
    else:
        mu, mv = sum(u.values()) / 4, sum(v.values()) / 4
        quarter = {(u[p] > mu, v[p] > mv): p for p in corners}
        order = [quarter.get(k) for k in ((False, False), (True, False), (True, True), (False, True))]
        if None in order:
            raise JobError(f"{label}: the corners of the face at {_at(2, face)} do not make a quadrangle")
    sides = []
    for c, p in _loop(face, curves, ends, at, order[0], label):
        if p in corners:
            sides.append([])
        sides[-1].append(c)
    kinds = [{along[c] for c in side} for side in sides]
    fits = kinds == [{False}, {True}, {False}] if axis else kinds in ([{True}, {False}] * 2, [{False}, {True}] * 2)
    if not fits:
        raise JobError(f"{label}: the face at {_at(2, face)} does not have sides along the motion and across it")
    for side, (is_along,) in zip(sides, kinds):
        total = n if is_along else slide["cross_divisions"]
        if len(side) > total:
            raise JobError(f"{label}: a side was split into {len(side)} pieces by touching bodies, more than {total}")
        counts = _share(total, [gmsh.model.occ.getMass(1, c) for c in side])
        if len(side) > 1:
            parts = " + ".join(map(str, counts))
            _note(f"{label}: a side was split into {len(side)} pieces by a touching body; elements {parts}")
        for c, k in zip(side, counts):
            if done.setdefault(c, k) != k:
                raise JobError(f"{label}: an edge between two slide faces gets {done[c]} and {k} elements")
            gmsh.model.mesh.setTransfiniteCurve(c, k + 1)
    gmsh.model.mesh.setTransfiniteSurface(face, "Left", order)


def _transform(periodic):
    """The affine matrix of one period (4 x 4, by rows) and a function that moves a point by it."""
    if periodic["kind"] == "rotation":
        a = math.radians(periodic["angle"])
        c, s = math.cos(a), math.sin(a)
        matrix = [c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    else:
        vx, vy, vz = periodic["vector"]
        matrix = [1, 0, 0, vx, 0, 1, 0, vy, 0, 0, 1, vz, 0, 0, 0, 1]
    return matrix, lambda p: [sum(m * x for m, x in zip(matrix[4 * i : 4 * i + 4], (*p, 1))) for i in range(3)]


def _on_plane(periodic, side, tol):
    """f(point) -> True on the first (side 0) or second (side 1) periodic boundary: the half-plane from the Z axis at
    the angle start (+ angle), or the plane where the motion-axis coordinate is start (+ the period length)."""
    if periodic["kind"] == "rotation":
        a = math.radians(periodic["start"] + side * periodic["angle"])
        c, s = math.cos(a), math.sin(a)
        return lambda p: abs(p[0] * s - p[1] * c) < tol and p[0] * c + p[1] * s > -tol
    length = math.hypot(*periodic["vector"])
    n = [x / length for x in periodic["vector"]]
    at = periodic["start"] + side * length
    return lambda p: abs(sum(a * b for a, b in zip(n, p)) - at) < tol


def _samples(dim, tag):
    """Points of an entity to test it against a plane: its centre of mass, its corners and points inside it."""
    pts = [gmsh.model.occ.getCenterOfMass(dim, tag)]
    corners = gmsh.model.getBoundary([(dim, tag)], combined=False, oriented=False, recursive=True)
    pts += [gmsh.model.getValue(0, t, []) for _, t in corners]
    lo, hi = gmsh.model.getParametrizationBounds(dim, tag)
    steps = [k / 4 for k in range(1, 4)]
    for g in [[u] for u in steps] if dim == 1 else [[u, v] for u in steps for v in steps]:
        pts.append(gmsh.model.getValue(dim, tag, [a + (b - a) * x for a, b, x in zip(lo, hi, g)]))
    return pts


def apply_periodic(periodic, dim):
    """Matching meshes on the two periodic boundaries: each boundary piece of dimension dim - 1 on the first one is
    linked to the piece one period on, which must have the same centre (after the move) and size."""
    box = gmsh.model.getBoundingBox(-1, -1)
    tol = 1e-6 * math.dist(box[:3], box[3:])
    matrix, move = _transform(periodic)
    whole = gmsh.model.getBoundary(gmsh.model.getEntities(dim), combined=True, oriented=False)
    boundary = list(dict.fromkeys(abs(t) for _, t in whole))
    sides = []
    for side in (0, 1):
        on = _on_plane(periodic, side, tol)
        sides.append([t for t in boundary if all(on(p) for p in _samples(dim - 1, t))])
    if not sides[0]:
        raise JobError("periodic boundaries do not match: no piece of the model boundary lies on the first one")
    occ = gmsh.model.occ
    targets = {t: (occ.getCenterOfMass(dim - 1, t), occ.getMass(dim - 1, t)) for t in sides[1]}
    for s in sides[0]:
        centre, size = move(occ.getCenterOfMass(dim - 1, s)), occ.getMass(dim - 1, s)
        partner = next(
            (t for t, (c, m) in targets.items() if math.dist(centre, c) < tol and abs(size - m) <= 1e-6 * max(size, m)),
            None,
        )
        if partner is None:
            raise JobError(
                f"periodic boundaries do not match: the piece at {_at(dim - 1, s)} has no partner on the other side"
            )
        del targets[partner]
        gmsh.model.mesh.setPeriodic(dim - 1, [partner], [s], matrix)
    if targets:  # left over on the second boundary
        at = _at(dim - 1, next(iter(targets)))
        raise JobError(f"periodic boundaries do not match: the piece at {at} has no partner on the other side")


def write_split(groups, path, version):
    """Write the elements of groups [(dim, entity tags, id, name)] of the meshed model to path as a model of its own:
    one discrete entity and physical group per group, nodes and elements numbered from 1."""
    all_tags, all_coords = gmsh.model.mesh.getNodes()[:2]
    where = {int(t): k for k, t in enumerate(all_tags)}
    blocks = []  # (dim, id, name, {element type: node tags})
    for dim, tags, id_, name in sorted(groups, key=lambda g: g[0]):  # points first: they own their node
        conn = {}
        for t in tags:
            for typ, nodes in zip(*gmsh.model.mesh.getElements(dim, t)[::2]):
                conn.setdefault(int(typ), []).extend(int(n) for n in nodes)
        blocks.append((dim, id_, name, conn))
    used = sorted({n for *_, conn in blocks for nodes in conn.values() for n in nodes})
    new = {old: k for k, old in enumerate(used, 1)}
    model = gmsh.model.getCurrent()
    gmsh.model.add(model + "_part")
    try:
        owned, element = set(), 1
        for dim, id_, name, conn in blocks:
            gmsh.model.addDiscreteEntity(dim, id_)
            mine = sorted({n for nodes in conn.values() for n in nodes} - owned)
            owned.update(mine)
            xyz = [x for n in mine for x in all_coords[3 * where[n] : 3 * where[n] + 3]]
            gmsh.model.mesh.addNodes(dim, id_, [new[n] for n in mine], xyz)
            for typ, nodes in conn.items():
                count = len(nodes) // gmsh.model.mesh.getElementProperties(typ)[3]
                gmsh.model.mesh.addElementsByType(id_, typ, range(element, element + count), [new[n] for n in nodes])
                element += count
            gmsh.model.addPhysicalGroup(dim, [id_], id_, name=name)
        gmsh.option.setNumber("Mesh.MshFileVersion", float(version))
        gmsh.write(path)
    finally:
        gmsh.model.remove()
        gmsh.model.setCurrent(model)


def slide_report(job):
    """The solver input values for the slides, to paste by hand: the add-on does not write the input file yet."""
    period = job.get("periodic")
    lines = []
    for s in job["slides"]:
        lines += [f"Sliding interface {s['name']}", f"SLIDE_NDIV {s['divisions']}", f"SLIDE_MAT_ID {s['slide_mat_id']}"]
    if period and period["kind"] == "translation":
        dxyz = [x / 1000 + 0.0 for x in period["vector"]]  # mm -> m
        lines.append("DXYZ " + " ".join(f"{x:g}" for x in dxyz))
        condition = {"CYCLIC": 1, "SYMMETRY": 1, "DXYZ": dxyz}
    else:  # a full turn is periodic over 360°
        angle = period["angle"] if period else 360.0
        lines.append(f"ANGLE {angle:g}")
        condition = {"CYCLIC": 2, "SYMMETRY": 1 if period else 0, "ANGLE": angle}
    condition["SLIDE_CONDITION"] = [
        {"SLIDE_NDIV": s["divisions"], "SLIDE_MAT_ID": s["slide_mat_id"], "FITNESS": 0.01} for s in job["slides"]
    ]
    block = json.dumps({"14_Periodic_Boundary_Conditions": {"PERIODIC_CONDITION": [condition]}}, indent=4)
    lines.append("set SYMMETRY to 0 for a periodic, 1 for an anti-periodic model")
    lines += [line[4:] for line in block.splitlines()[1:-1]]  # the key and its value, without the outer braces
    lines.append("Meshes are in mm: use UNIT = 1 in 10_1_Input_Files.")
    return lines


def run(job_path, build, dim):
    """Read the job, call build(job, folder) on a fresh model, mesh to dimension dim, write mesh.unv and
    replace job["mesh_file"] with the finished .msh. Returns the job.

    build may return split = {"fixed": groups, "moving": groups} (see write_split): the fixed side then goes to
    job["mesh_file"] and the moving side to job["rotor_file"]."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    msh = os.path.join(folder, "mesh.msh")
    outputs = [(msh, job["mesh_file"])]
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        split = build(job, folder)
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
        if split:
            outputs.append((os.path.join(folder, "rotor.msh"), job["rotor_file"]))
            for side, (path, _) in zip(("fixed", "moving"), outputs):
                write_split(split[side], path, job["msh_version"])
        else:
            gmsh.write(msh)
        gmsh.write(os.path.join(folder, "mesh.unv"))
    finally:
        gmsh.finalize()
    for path, target in outputs:
        try:
            os.replace(path, target)  # only a finished mesh replaces the solver's file
        except PermissionError:
            raise JobError(f"Could not replace {target}: it is read-only or open in another program.") from None
    return job


def check(job_path, build):
    """The geometry checks of a run without meshing: build(job, folder) on a fresh model, nothing written."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add(job["model_name"])
        build(job, folder)
    finally:
        gmsh.finalize()
    print("CHECK OK")


def main(argv, script, run_job, build=None):
    """argv: [script, job.json] meshes; [script, job.json, "--check"] only checks (needs build)."""
    for stream in (sys.stdout, sys.stderr):  # the runner reads UTF-8, whatever the console code page
        stream.reconfigure(encoding="utf-8", errors="replace")
    checking = len(argv) == 3 and argv[2] == "--check" and build is not None
    if len(argv) != 2 and not checking:
        print(f"ERROR: usage: {script} <job.json> [--check]", file=sys.stderr)
        return 1
    try:
        if checking:
            check(argv[1], build)
        else:
            run_job(argv[1])
    except Exception as exc:  # anything -> one clean ERROR line for the runner
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0
