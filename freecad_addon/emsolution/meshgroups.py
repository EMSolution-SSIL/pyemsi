"""Symmetric mesh by groups: mesh each group's cell, copy the mesh by the group's transforms with numpy (meshfrozen) and
give every copy the part its row names. Runs in the mesher process (mesher2d.run_job and mesher.run_job call run for a
job whose "symmetric" has "groups"); dim is 2 (faces) or 3 (solids). Never import FreeCAD here."""

import json
import math
import os
import shutil
import tempfile
from collections import namedtuple
from contextlib import contextmanager

import gmsh
import numpy as np

from meshcommon import JobError, generate, import_brep, publish, slide_report, write_split, MSH_VERSION
import meshfrozen
import meshsym

POOR = 0.1  # an element whose min SICN is below this is reported as poor

# elements: {(row index, copy): {etype: ndarray}}; patches: [(excitation, {etype: ndarray})] of the landed copies
# reached: the group has an arc (2D) or a face (3D) on the sliding interface
# contacts: the contact table of the group (None when it was not needed); expected: see _expected_area
Copied = namedtuple("Copied", "V elements patches reached contacts expected", defaults=[False, None, 0.0])
# split and surfaces: {side: {id: (name, [entity tags])}} of model "full", for the bodies and the excitation surfaces
Model = namedtuple("Model", "split surfaces")
# T(a) touches b over area (length in 2D), T = transform (16 floats): for count pairs of copies, counted once per pair.
# seam: the contact is made of whole faces of both, so the seams of meshsym._periodic cover it.
Contact = namedtuple("Contact", "a b transform area count seam")
IDENTITY = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]


@contextmanager
def _scratch(name):
    """A gmsh model of its own, removed on exit, with the current one current again."""
    current = gmsh.model.getCurrent()
    gmsh.model.add(name)
    try:
        yield
    finally:
        gmsh.model.remove()
        gmsh.model.setCurrent(current)


def _key(m):
    """A transform as a dict key: rounded, so transforms that differ only by rounding errors have one key."""
    return tuple(round(float(v), 9) + 0.0 for v in m)


def _inverse(m):
    return np.linalg.inv(np.reshape(m, (4, 4))).ravel().tolist()


def _relative(transforms):
    """[(T, count)] of the relative transforms T_i^-1 T_j for i < j: how many pairs of copies have each. Never the
    identity: copies that coincide are for the check of the mesh to refuse."""
    M = [np.reshape(t, (4, 4)) for t in transforms]
    found = {}
    for i, first in enumerate(M):
        inverse = np.linalg.inv(first)
        for second in M[i + 1 :]:
            r = (inverse @ second).ravel().tolist()
            if _key(r) != _key(IDENTITY):
                found.setdefault(_key(r), [r, 0])[1] += 1
    return [tuple(v) for v in found.values()]


def _place(dimtags, m):
    """Move OCC entities by the rigid 4x4 row-major transform m with a mirror, a rotation and a translation: an
    occ.affineTransform would turn their planes and circles into splines, which fragment worse."""
    occ = gmsh.model.occ
    M = np.reshape(m, (4, 4))
    R = M[:3, :3]
    if np.linalg.det(R) < 0:
        occ.mirror(dimtags, 0, 0, 1, 0)
        R = R @ np.diag([1.0, 1.0, -1.0])
    axis = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    sine, cosine = np.linalg.norm(axis) / 2, (np.trace(R) - 1) / 2
    angle = math.atan2(sine, cosine)
    if angle > 1e-12:
        if sine < 1e-9 and cosine < 0:  # a half turn: R + I = 2 a aT, a column of it is along the axis
            B = R + np.eye(3)
            axis = B[:, np.argmax(np.linalg.norm(B, axis=0))]
        occ.rotate(dimtags, 0, 0, 0, axis[0], axis[1], axis[2], angle)
    if np.any(M[:3, 3]):
        occ.translate(dimtags, M[0, 3], M[1, 3], M[2, 3])


def _cell_shapes(group, job, folder, dim):
    """{cell: [dimtags]} of the cell objects of the group's cell job, imported into the current model."""
    by_id = {b["mat_id"]: b for b in job["bodies" if dim == 2 else "volumes"]}
    return {c: import_brep(os.path.join(folder, by_id[c]["file"]), dim) for c in group["cells"]}


def _box(dimtags):
    boxes = np.array([gmsh.model.occ.getBoundingBox(d, t) for d, t in dimtags])
    return np.concatenate([boxes[:, :3].min(axis=0), boxes[:, 3:].max(axis=0)])


def _boxes_touch(box_a, box_b, m, tol):
    """True when the box box_a moved by m (its axis aligned bounding box) meets box_b."""
    corners = np.array(
        [[box_a[3 * i], box_a[1 + 3 * j], box_a[2 + 3 * k]] for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    )
    M = np.reshape(m, (4, 4))
    moved = corners @ M[:3, :3].T + M[:3, 3]
    return bool(np.all(moved.min(axis=0) <= box_b[3:] + tol) and np.all(moved.max(axis=0) >= box_b[:3] - tol))


def _boundary(dim, dimtags):
    return sorted({abs(t) for _, t in gmsh.model.getBoundary(list(dimtags), combined=False, oriented=False)})


def _point_on(dim, t):
    """A point of entity t: its parametric middle, or failing that one of a grid over its parametric box that is
    inside its trimming."""
    lo, hi = gmsh.model.getParametrizationBounds(dim, t)
    steps = (0.5, 0.25, 0.75, 0.125, 0.375, 0.625, 0.875)
    for a in steps:
        for b in steps if dim == 2 else (0.5,):
            uv = [lo[0] + (hi[0] - lo[0]) * a] + ([lo[1] + (hi[1] - lo[1]) * b] if dim == 2 else [])
            if dim == 1 or gmsh.model.isInside(dim, t, uv, parametric=True):
                return list(gmsh.model.getValue(dim, t, uv))
    return list(gmsh.model.occ.getCenterOfMass(dim, t))


def _whole(references, pieces, dim, tol):
    """True when no entity of references (faces, or curves in 2D) is only partly covered by pieces, [(area, point)]."""
    for f in references:
        box = gmsh.model.getBoundingBox(dim - 1, f)
        covered = sum(area for area, p in pieces if meshsym._on_face(dim - 1, f, box, [p], tol))
        if covered > tol and abs(covered - gmsh.model.occ.getMass(dim - 1, f)) > tol:
            return False
    return True


def _shared(cells, a, b, m, dim, tol):
    """In the current model, fragment cell a moved by m with cell b, both copies. Returns (shared, seam, junk):
    shared, the faces (curves in 2D) between them as dimtags; seam, True when these are whole faces of both; junk, what
    the caller must give to _drop afterwards. A piece of volume they have in common (an overlap) shares no faces."""
    occ = gmsh.model.occ
    reference = occ.copy(cells[a])
    _place(reference, m)
    moved = occ.copy(cells[a])
    _place(moved, m)
    fixed = occ.copy(cells[b])
    out, per_input = occ.fragment(moved, fixed)
    occ.synchronize()
    tops = [
        {(d, t) for dimtags in part for d, t in dimtags if d == dim}
        for part in (per_input[: len(moved)], per_input[len(moved) :])
    ]
    overlap = tops[0] & tops[1]
    common = set(_boundary(dim, tops[0] - overlap)) & set(_boundary(dim, tops[1] - overlap))
    shared = [(dim - 1, t) for t in sorted(common) if occ.getMass(dim - 1, t) > tol]
    pieces = [(occ.getMass(d, t), _point_on(d, t)) for d, t in shared]
    seam = _whole(_boundary(dim, reference), pieces, dim, tol) and _whole(_boundary(dim, cells[b]), pieces, dim, tol)
    return shared, seam, out + reference


def _drop(junk):
    gmsh.model.occ.remove(junk, recursive=True)
    gmsh.model.occ.synchronize()


def contact_table(group, job, folder, dim):
    """[Contact] between the cell objects of group, whose cell job is job: where a copy of a cell touches a cell, over
    an area, in the cell's frame. One entry per relative transform of the group (see _relative) and ordered pair of
    cell objects, and one with the identity for each pair of different cell objects of one copy (count: the copies)."""
    with _scratch("contacts"):
        cells = _cell_shapes(group, job, folder, dim)
        gmsh.model.occ.synchronize()
        boxes = {c: _box(tags) for c, tags in cells.items()}
        every = np.array(list(boxes.values()))
        tol = 1e-6 * max(1.0, math.dist(every[:, :3].min(axis=0), every[:, 3:].max(axis=0)))
        jobs = [(a, b, IDENTITY, len(group["transforms"])) for a in cells for b in cells if a < b]
        jobs += [(a, b, m, n) for m, n in _relative(group["transforms"]) for a in cells for b in cells]
        table = []
        for a, b, m, n in jobs:
            if not _boxes_touch(boxes[a], boxes[b], m, tol):
                continue
            shared, seam, junk = _shared(cells, a, b, m, dim, tol)
            area = sum(gmsh.model.occ.getMass(d, t) for d, t in shared)
            _drop(junk)
            if area > tol:
                table.append(Contact(a, b, m, area, n, seam))
    return table


def _cuts(cells, source, contacts, dim, tol):
    """In the current model: the faces (dimtags) that split cell source where any non-seam contact has an edge on it.
    A contact's faces lie on b, and on a once moved back by the inverse of its transform."""
    tools = []
    for c in contacts:
        if c.seam or source not in (c.a, c.b):
            continue
        shared, _, junk = _shared(cells, c.a, c.b, c.transform, dim, tol)
        if source == c.b:
            tools += gmsh.model.occ.copy(shared)
        if source == c.a:
            faces = gmsh.model.occ.copy(shared)
            _place(faces, _inverse(c.transform))
            tools += faces
        _drop(junk)
    return tools


def _images_needed(contacts):
    """The contacts that need an image: not a seam, not within one copy, and one of each pair (a, b, T), (b, a, T^-1),
    for an image of each would be the master of the other's faces."""
    done, keep = set(), []
    for c in contacts:
        if c.seam or _key(c.transform) == _key(IDENTITY):
            continue
        if (c.b, c.a, _key(_inverse(c.transform))) not in done:
            done.add((c.a, c.b, _key(c.transform)))
            keep.append(c)
    return keep


def _split_cell(group, x, contacts, folder, dim):
    """In the current model: cell x fragmented with its _cuts and everything else in the model removed. Returns (x's
    dimtags now, True when that gave it more faces)."""
    occ = gmsh.model.occ
    cells = _cell_shapes(group, group["job"], folder, dim)
    occ.synchronize()
    boxes = np.array([_box(tags) for tags in cells.values()])
    tol = 1e-6 * max(1.0, math.dist(boxes[:, :3].min(axis=0), boxes[:, 3:].max(axis=0)))
    before = len(_boundary(dim, cells[x]))
    tools = _cuts(cells, x, contacts, dim, tol)
    keep = cells[x]
    if tools:
        _, per_input = occ.fragment(cells[x], tools)
        keep = [dt for part in per_input[: len(cells[x])] for dt in part]
    for other, tags in cells.items():
        if other != x:
            occ.remove(tags, recursive=True)
    occ.remove([dt for dt in occ.getEntities(dim) if dt not in set(keep)], recursive=True)
    occ.synchronize()
    return keep, len(_boundary(dim, keep)) != before


def _write_moved(source, m, target, dim):
    with _scratch("image"):
        tags = import_brep(source, dim)
        _place(tags, m)
        gmsh.model.occ.synchronize()
        gmsh.write(target)


def prepare_images(group, contacts, folder, dim):
    """A new group, with the images that the contacts not covered by seams need. Each source cell is split along all its
    contacts first, so that its faces pair one to one with those of its image; its image is then added to the job as
    a new body. group["cells"] is unchanged, so an image is meshed but never copied. group["images"] lists them for
    pair_images: {"id", "source", "transform"}; their BREPs are in group["images_folder"], for mesh_cell to delete."""
    needed = _images_needed(contacts)
    if not needed:
        return group
    key = "bodies" if dim == 2 else "volumes"
    entries = [dict(e) for e in group["job"][key]]
    by_id = {e["mat_id"]: e for e in entries}
    structured = {b["mat_id"] for b in (group["job"].get("transfinite") or {}).get("bodies", [])}
    for x in sorted(structured & ({c.a for c in needed} | {c.b for c in needed})):
        with _scratch("split"):
            if _split_cell(group, x, contacts, folder, dim)[1]:
                raise JobError(
                    f"group {group['name']}: the structured cell {by_id[x]['name']} would have to be split where a copy"
                    " touches part of its face; meshing that is not handled yet, a limit of the tool, not of the drawing"
                )
    where = tempfile.mkdtemp(prefix="images_", dir=folder)
    relative = os.path.basename(where)
    for a in sorted({c.a for c in needed}):
        with _scratch("split"):
            _split_cell(group, a, contacts, folder, dim)  # only the split cell is left to go to the file
            by_id[a]["file"] = f"{relative}/split_{a}.brep"
            gmsh.write(os.path.join(folder, by_id[a]["file"]))
    images, next_id = [], max(by_id) + 1
    for k, c in enumerate(needed):
        file = f"{relative}/image_{k}.brep"
        _write_moved(os.path.join(folder, by_id[c.a]["file"]), c.transform, os.path.join(folder, file), dim)
        entries.append(
            {"mat_id": next_id, "name": f"{by_id[c.a]['name']} image", "file": file, "size": by_id[c.a]["size"]}
        )
        images.append({"id": next_id, "source": c.a, "transform": c.transform})
        next_id += 1
    return dict(group, job=dict(group["job"], **{key: entries}), images=images, images_folder=where)


def _faces_of(dim, body):
    return _boundary(dim, [(dim, e) for e in gmsh.model.getEntitiesForPhysicalGroup(dim, body)])


def _copied_from(dim, entity, master):
    """True when the mesh of entity is a copy, directly or through others, of the mesh of master."""
    while True:
        above = int(gmsh.model.mesh.getPeriodic(dim, [entity])[0])
        if above == entity:
            return False
        if above == master:
            return True
        entity = above


def pair_images(group, images, dim):
    """After build: mesh each face of every image as a copy of the face of its source that it was moved from, paired
    by centre of mass. A face of both image and source is a seam of the cell: meshsym._periodic has it. A face on a real
    cell that finds no partner cannot be copied, and that is a limit of this method, not a fault in the drawing."""
    occ = gmsh.model.occ
    box = gmsh.model.getBoundingBox(-1, -1)
    tol = 1e-6 * max(1.0, math.dist(box[:3], box[3:]))
    real = {int(e) for c in group["cells"] for e in gmsh.model.getEntitiesForPhysicalGroup(dim, c)}
    for image in images:
        m = image["transform"]
        sources = {
            s: (occ.getMass(dim - 1, s), meshsym._apply(m, occ.getCenterOfMass(dim - 1, s)))
            for s in _faces_of(dim, image["source"])
        }
        for f in _faces_of(dim, image["id"]):
            if f in sources:
                continue
            mass, centre = occ.getMass(dim - 1, f), occ.getCenterOfMass(dim - 1, f)
            partner = next(
                (s for s, (q, p) in sources.items() if abs(q - mass) <= tol and math.dist(p, centre) <= tol), None
            )
            if partner is not None:
                if not _copied_from(dim - 1, partner, f):  # _periodic may have made it the other way round
                    gmsh.model.mesh.setPeriodic(dim - 1, [f], [partner], m)
            elif real & {int(e) for e in gmsh.model.getAdjacencies(dim - 1, f)[0]}:
                raise JobError(
                    f"group {group['name']}: a contact near ({', '.join(f'{v:.6g}' for v in centre[:dim])}) splits the"
                    " copy of a cell differently from the cell itself; this is a limit of the tool, not of the drawing"
                )


def _expected_area(group, contacts, dim):
    """After generate: Σ area × count over the contacts between copies, the area the copies must share. Each area is
    scaled by how much of it the flat facets of the cell's own mesh cover on the faces of the contact (found on cell b:
    moved back by the inverse of T they lie on cell a): an element edge is shorter than a curved edge it follows, so a
    face that is curved or has curved edges has less area in the mesh than in the geometry, even when it is flat."""
    crossing = [c for c in contacts if _crosses(c)]
    if not crossing:
        return 0.0
    box = gmsh.model.getBoundingBox(-1, -1)
    tol = 1e-6 * max(1.0, math.dist(box[:3], box[3:]))
    of_cell = {c: _faces_of(dim, c) for c in group["cells"]}
    boxes = {f: gmsh.model.getBoundingBox(dim - 1, f) for faces in of_cell.values() for f in faces}
    xyz, facets = meshfrozen.read_model(dim - 1, {f: [f] for f in boxes})
    meshed = {
        f: sum(float(meshfrozen._area(xyz, c).sum()) for c in per_type.values()) for f, per_type in facets.items()
    }

    def in_box(p, b):
        return all(b[i] - tol <= p[i] <= b[i + 3] + tol for i in range(3))

    total = 0.0
    for c in crossing:
        inverse = _inverse(c.transform)
        found = []
        for e in of_cell[c.b]:
            p = meshsym._apply(inverse, _point_on(dim - 1, e))
            if any(in_box(p, boxes[f]) and meshsym._on_face(dim - 1, f, boxes[f], [p], tol) for f in of_cell[c.a]):
                found.append(e)
        geometric = sum(gmsh.model.occ.getMass(dim - 1, e) for e in found)
        total += c.area * c.count * (sum(meshed[e] for e in found) / geometric if found else 1.0)
    return total


def _by_row(group, folder, dim):
    """{row index: [cell entity tags]}. A cell with one row gives it all its entities; a cell with several rows
    gives each entity to the row whose solid (BREP file) holds the first, middle and last element centres."""
    rows = group["rows"]
    out = {k: [] for k in range(len(rows))}
    several = []
    for cell in group["cells"]:
        mine = [k for k, row in enumerate(rows) if row["cell"] == cell]
        entities = [int(e) for e in gmsh.model.getEntitiesForPhysicalGroup(dim, cell)]
        if not mine:
            raise JobError(f"group {group['name']}: cell {cell} has no row")
        if len(mine) == 1:
            out[mine[0]] += entities
        else:
            several.append((mine, [meshsym._entity(dim, e) for e in entities]))
    if several:
        current = gmsh.model.getCurrent()
        gmsh.model.add("rows")
        try:
            for mine, ents in several:
                shapes = {k: [t for _, t in import_brep(os.path.join(folder, rows[k]["file"]), dim)] for k in mine}
                gmsh.model.occ.synchronize()
                for e, _, _, centres, _ in ents:
                    flat = [x for p in centres for x in p]
                    hits = [k for k in mine if sum(gmsh.model.isInside(dim, t, flat) for t in shapes[k]) == 3]
                    if len(hits) != 1:
                        where = ", ".join(f"{v:.6g}" for v in centres[0][:dim])
                        raise JobError(f"group {group['name']}: a piece of the cell near ({where}) is in no row")
                    out[hits[0]].append(e)
        finally:
            gmsh.model.remove()
            gmsh.model.setCurrent(current)
    return out


def _slide_cell(group, slide, dim):
    """Make the cell's arcs (2D) or faces (3D) on the sliding interface transfinite. Returns True when it has any: a
    group with none is left alone (the slide functions refuse such a side)."""
    r = slide["radius"]
    if dim == 2:
        reached = any(meshsym._on_arc(c, r, 1e-6 * r) for c in meshsym._side_seams(group, 2))
    else:
        reached = bool(meshsym._cylinder_faces(group, r, 1e-6 * r))
    if reached:
        (meshsym._slide_arcs if dim == 2 else meshsym._slide_faces_sym)(slide, [group])
    return reached


def mesh_cell(group, job, folder, build, dim, slide=None):
    """Mesh the cell of a group in a model of its own (removed at the end) and copy it by the group's transforms.
    Returns Copied: the joined nodes V, the elements of each (row, copy), the cell boundary patches that land on an
    excitation, copied with their copy, whether the cell reaches the sliding interface slide, the contact table of the
    group and the area its copies must share (_expected_area)."""
    contacts = None
    gmsh.model.add(f"cell_{group['name']}")
    try:
        if len(group["transforms"]) > 1 or len(group["cells"]) > 1:
            contacts = contact_table(group, group["job"], folder, dim)
            group = prepare_images(group, contacts, folder, dim)
        build(dict(group["job"]), folder)
        reached = _slide_cell(group, slide, dim) if slide else False
        meshsym._periodic([dict(group, transforms=_seam_transforms(contacts))], dim)
        pair_images(group, group.get("images", []), dim)
        generate(dict(group["job"], options=job.get("options", {})), dim)
        expected = _expected_area(group, contacts, dim) if contacts else 0.0
        by_row = _by_row(group, folder, dim)
        cell_patches = meshsym._cell_patches(group, dim)
        labels = meshsym._land_surfaces([group], [cell_patches], folder, dim)[0] if cell_patches else []
        xyz, bodies = meshfrozen.read_model(dim, by_row)
        pxyz, patches = meshfrozen.read_model(dim - 1, {j: [p[0]] for j, p in enumerate(cell_patches)})
    finally:
        gmsh.model.remove()
        if "images_folder" in group:
            shutil.rmtree(group["images_folder"], ignore_errors=True)
    frozen = {("row", k): v for k, v in bodies.items()}
    for j, per_type in patches.items():  # the patch nodes are cell nodes: they follow the bodies' joined nodes
        frozen[("patch", j)] = {t: c + len(xyz) for t, c in per_type.items()}
    V, out = meshfrozen.copy_mesh(np.vstack([xyz, pxyz]), frozen, group["transforms"])
    elements = {(k, c): out[(("row", k), c)] for k in bodies for c in range(len(group["transforms"]))}
    copied = []
    for j, copies in enumerate(labels):
        for c, x in enumerate(copies):
            if x is None:
                continue
            conn = out[(("patch", j), c)]
            if dim == 2 and np.linalg.det(np.reshape(group["transforms"][c], (4, 4))[:3, :3]) < 0:
                conn = {t: a[:, ::-1] for t, a in conn.items()}  # lines: reversed like a mirrored element
            copied.append((x, conn))
    return Copied(V, elements, copied, reached, contacts, expected)


def _crosses(contact):
    """True for a contact between two copies, False for one within a copy."""
    return _key(contact.transform) != _key(IDENTITY)


def _seam_transforms(contacts):
    """Each transform between copies that touch, and its inverse: meshsym._periodic pairs a seam only from its lower
    tag to its higher one, so it needs both directions; a relative transform need not be one of the group's own."""
    needed = {}
    for c in filter(_crosses, contacts or ()):
        for m in (c.transform, _inverse(c.transform)):
            needed.setdefault(_key(m), m)
    return list(needed.values())


def _near_contact(group, contacts, V, free, dim, folder):
    """Where the copies do not match, as text: the centre of a facet that only one element uses and that lies on a
    contact face between copies; failing that, the centre of a contact face."""
    centres = np.vstack([V[f].mean(axis=1) for f in free if len(f)] or [np.zeros((0, 3))])

    def text(p):
        return ", ".join(f"{v:.6g}" for v in p[:dim])

    fallback = "?"
    with _scratch("near"):
        cells = _cell_shapes(group, group["job"], folder, dim)
        gmsh.model.occ.synchronize()
        box = gmsh.model.getBoundingBox(-1, -1)
        tol = 1e-6 * max(1.0, math.dist(box[:3], box[3:]))
        for c in filter(_crosses, contacts):
            shared, _, junk = _shared(cells, c.a, c.b, c.transform, dim, tol)
            for _, s in shared:
                if fallback == "?":
                    fallback = text(gmsh.model.occ.getCenterOfMass(dim - 1, s))
                b = gmsh.model.getBoundingBox(dim - 1, s)
                inside = np.all(centres >= np.array(b[:3]) - tol, axis=1) & np.all(
                    centres <= np.array(b[3:]) + tol, axis=1
                )
                for p in centres[inside][:64]:  # the first copy has it unless the pairs do not start there
                    if meshsym._on_face(dim - 1, s, b, [list(p)], tol):
                        return text(p)
            _drop(junk)
    return fallback


def _check_contacts(group, one, whole, dim, folder):
    """The copies of a group share, across copies, the area that the geometry says their contacts have: a mismatch
    there leaves facets on the contact unshared. The shared facets inside one copy, the interior and the contacts of
    the cell's objects with each other, are subtracted: every copy has the same."""
    copies = len(group["transforms"])
    first = [one.elements[k] for k in one.elements if k[1] == 0]
    measured = whole.shared_area - copies * meshfrozen.boundary(one.V, first, dim).shared_area
    if abs(measured - one.expected) > 1e-6 * max(one.expected, 1e-3 * whole.shared_area):
        free = (whole.tri, whole.quad, whole.edge)
        where = _near_contact(group, one.contacts, one.V, free, dim, folder)
        raise JobError(
            f"the copies of {group['name']} do not match near ({where}): their contact faces should share an area of"
            f" {one.expected:.6g} but the meshes share {measured:.6g}"
        )


def _where(V, elements, dim):
    """The centre of an element using a facet that three or more elements use, as text."""
    faces = [(meshfrozen.EDGE_FACES, 2)] if dim == 2 else [(meshfrozen.TRI_FACES, 3), (meshfrozen.QUAD_FACES, 4)]
    for table, width in faces:
        facets, use, owner = meshfrozen._facets(V, elements, table, width)
        if (use >= 3).any():
            return ", ".join(f"{v:.6g}" for v in owner[use >= 3][0])
    return "?"


class _Entity:
    """The nodes and elements of one discrete entity of model "full", collected before they are added."""

    def __init__(self):
        self.tags, self.xyz, self.conn = [], [], {}

    def add(self, offset, V, owned, per_type):
        used = np.unique(np.concatenate([c.ravel() for c in per_type.values()])) if per_type else np.zeros(0, int)
        mine = used[~owned[used]]  # nodes no earlier element of the group added
        owned[mine] = True
        self.tags.append(offset + mine + 1)
        self.xyz.append(V[mine])
        for etype, conn in per_type.items():
            self.conn.setdefault(etype, []).append(offset + conn + 1)

    def add_nodes(self, dim, tag):
        gmsh.model.addDiscreteEntity(dim, tag)
        tags, xyz = np.concatenate(self.tags), np.vstack(self.xyz)
        gmsh.model.mesh.addNodes(dim, tag, tags.tolist(), xyz.ravel().tolist())

    def add_elements(self, tag):  # after every entity has its nodes: an element may use the nodes of another entity
        for etype, parts in self.conn.items():
            gmsh.model.mesh.addElementsByType(tag, etype, [], np.vstack(parts).ravel().tolist())


def mesh(job, folder, build, dim):
    """Mesh the cell of every group, copy it, check the copies and put them all in model "full" (current): one entity
    per (side, MAT_ID) and per (side, SMAT_ID). Returns a Model."""
    symmetric = job["symmetric"]
    if symmetric.get("free"):
        raise JobError("free bodies in a group job are not supported yet")
    slide = symmetric.get("slide")
    copied = []
    for group in symmetric["groups"]:
        one = mesh_cell(group, job, folder, build, dim, slide)
        every = list(one.elements.values())
        whole = meshfrozen.boundary(one.V, every, dim)
        if whole.over_used:
            where = _where(one.V, every, dim)
            raise JobError(
                f"the copies of {group['name']} do not fit: a face has more than two elements near ({where})"
            )
        if one.contacts is not None:
            _check_contacts(group, one, whole, dim, folder)
        copied.append(one)
    sides = [{"side": s} for s in ("fixed", "moving")]
    if slide:
        for side in sides:
            if not any(one.reached for group, one in zip(symmetric["groups"], copied) if group["side"] == side["side"]):
                what = (
                    "the cell of the {} side has no arc on the sliding circle"
                    if dim == 2
                    else "the cells of the {} side have no face on the sliding cylinder"
                )
                raise JobError(
                    f"sliding interface {slide['name']}: {what.format(side['side'])} (radius {slide['radius']:g} mm);"
                    " both sides must reach it"
                )
    gmsh.model.add("full")
    entities = {}  # (dim, side, id) -> (name, _Entity)
    offset = 0
    for group, one in zip(symmetric["groups"], copied):
        owned = np.zeros(len(one.V), dtype=bool)
        for (row, c), per_type in one.elements.items():
            part = group["parts"][group["rows"][row]["parts"][c]]
            _, entity = entities.setdefault((dim, group["side"], part["mat_id"]), (part["name"], _Entity()))
            entity.add(offset, one.V, owned, per_type)
        for x, per_type in one.patches:
            _, entity = entities.setdefault((dim - 1, group["side"], x["smat_id"]), (x["name"], _Entity()))
            entity.add(offset, one.V, owned, per_type)
        offset += len(one.V)
    split, surfaces = {}, {}
    ordered = sorted(entities.items())
    for tag, ((d, _, _), (_, entity)) in enumerate(ordered, 1):
        entity.add_nodes(d, tag)
    for tag, ((d, side, id_), (name, entity)) in enumerate(ordered, 1):
        entity.add_elements(tag)
        by_side = split if d == dim else surfaces
        by_side.setdefault(side, {}).setdefault(id_, (name, []))[1].append(tag)
    gmsh.model.mesh.removeDuplicateNodes()
    gmsh.model.mesh.renumberNodes()
    gmsh.model.mesh.renumberElements()
    for d, by_side in ((dim, split), (dim - 1, surfaces)):
        members = {}
        for groups in by_side.values():
            for id_, (name, ents) in groups.items():
                members.setdefault(id_, (name, []))[1].extend(ents)
        for id_, (name, ents) in sorted(members.items()):
            gmsh.model.addPhysicalGroup(d, ents, id_, name=name)
    if slide:
        (meshsym._on_circle if dim == 2 else meshsym._on_cylinder)(slide, sides, split)
    return Model(split, surfaces)


def check(job_path, build, dim=2):
    """--check of a group job: mesh the cells, copy them and run every check, nothing written."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add(job["model_name"])
        mesh(job, folder, build, dim)
    finally:
        gmsh.finalize()
    print("CHECK OK")


def _poor(model, dim):
    """[(name, poor elements, elements)] of each MAT_ID of model "full": poor is a min SICN below POOR."""
    found = {}
    for groups in model.split.values():
        for id_, (name, ents) in groups.items():
            found.setdefault(id_, [name, 0, 0])
            for e in ents:
                for etype, tags in zip(*gmsh.model.mesh.getElements(dim, e)[:2]):
                    quality = np.asarray(gmsh.model.mesh.getElementQualities(list(tags), "minSICN"))
                    found[id_][1] += int((quality < POOR).sum())
                    found[id_][2] += len(tags)
    return [tuple(v) for _, v in sorted(found.items())]


def run(job_path, build, dim=2):
    """Read the job, mesh and copy the cells of its groups with build(job, folder), write mesh.unv and replace
    job["mesh_file"] (and job["rotor_file"] when sliding: the moving side) with the finished .msh. Returns the job, with
    the poor elements per part in job["poor"]."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    msh = os.path.join(folder, "mesh.msh")
    outputs = [(msh, job["mesh_file"])]
    slide = job["symmetric"].get("slide")
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        model = mesh(job, folder, build, dim)
        job["poor"] = _poor(model, dim)
        point = (meshsym._marker if dim == 2 else meshsym._marker_line)(slide) if slide else None
        gmsh.option.setNumber("Mesh.MshFileVersion", MSH_VERSION)
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.write(os.path.join(folder, "mesh.unv"))
        if slide:
            outputs.append((os.path.join(folder, "rotor.msh"), job["rotor_file"]))
            for side, (path, _) in zip(("fixed", "moving"), outputs):
                parts = [(dim, ents, id_, name) for id_, (name, ents) in sorted(model.split.get(side, {}).items())]
                parts += [(dim - 1, e, id_, n) for id_, (n, e) in sorted(model.surfaces.get(side, {}).items())]
                if side == "moving":
                    parts.append((dim - 2, [point], slide["slide_mat_id"], slide["name"]))
                write_split(parts, path)
        else:
            gmsh.write(msh)
    finally:
        gmsh.finalize()
    publish(outputs)
    return job


def report(job):
    """The lines run_job prints: one MAT_ID line per part, one SMAT_ID line per excitation, the poor elements of each
    part that has any, the file written."""
    groups = job["symmetric"]["groups"]
    seen = {(p["mat_id"], p["name"]): None for g in groups for p in g["parts"]}
    lines = [f"MAT_ID  {id_:>6}  {name}" for id_, name in seen]
    excited = {(x["smat_id"], x["name"]): None for g in groups for x in g.get("excitations", [])}
    lines += [f"SMAT_ID {id_:>6}  {name}" for id_, name in excited]
    slide = job["symmetric"].get("slide")
    if slide:
        lines += slide_report({"slides": [slide]})
    lines += [f"Poor elements  {name}  {poor} of {total}" for name, poor, total in job.get("poor", []) if poor]
    lines.append(f"Wrote {job['mesh_file']}")
    if slide:
        lines.append(f"Wrote {job['rotor_file']}")
    return lines
