"""Symmetric mesh by groups: mesh each group's cell, copy the mesh by the group's transforms with numpy (meshfrozen) and
give every copy the part its row names. Runs in the mesher process (mesher2d.run_job and mesher.run_job call run for a
job whose "symmetric" has "groups"); dim is 2 (faces) or 3 (solids). Never import FreeCAD here."""

import itertools
import json
import math
import os
import shutil
import tempfile
from collections import namedtuple
from contextlib import contextmanager

import gmsh
import numpy as np

from meshcommon import JobError, generate, import_brep, publish, slide_report, write_split, FIELD_LISTS, MSH_VERSION
from meshcommon import _note
from meshcommon import face_normal, plane_normal
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
# A free body after meshing. added: its new nodes; elements: {etype: connectivity}, node i < n the frozen node i of the
# side (n: the nodes of the side's copies), node n + k added[k]; surfaces: {smat_id: (name, per type)}, the 2D elements
# of its excitation faces, numbered the same way.
FreeBody = namedtuple("FreeBody", "name added elements surfaces")
# One OCC volume (face in 2D) of a free body, read before anything of its model changes. faces: its faces (lines in 2D);
# frozen: {"tri"/"quad"/"edge": mask over the side's facets that bound it}: inside it, or flush against it from
# outside; covered: {face: [the node rows of the frozen facets lying on it]}
Survey = namedtuple("Survey", "body entity faces frozen covered")
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
    the caller must give to _drop afterwards. A piece of volume they have in common (an overlap) shares no faces.
    A mirror turns the moved copy into BSplines, whose area OCC gets wrong by up to a few per mille on a curved
    surface or edge: so fixed goes first in the fragment, for the shared faces to keep its exact surfaces, and the
    pieces are checked against cell a itself, moved back, not against the moved copy."""
    occ = gmsh.model.occ
    moved = occ.copy(cells[a])
    _place(moved, m)
    fixed = occ.copy(cells[b])
    out, per_input = occ.fragment(fixed, moved)
    occ.synchronize()
    tops = [
        {(d, t) for dimtags in part for d, t in dimtags if d == dim}
        for part in (per_input[: len(fixed)], per_input[len(fixed) :])
    ]
    overlap = tops[0] & tops[1]
    common = set(_boundary(dim, tops[0] - overlap)) & set(_boundary(dim, tops[1] - overlap))
    shared = [(dim - 1, t) for t in sorted(common) if occ.getMass(dim - 1, t) > tol]
    pieces = [(occ.getMass(d, t), _point_on(d, t)) for d, t in shared]
    back = [(area, meshsym._apply(_inverse(m), p)) for area, p in pieces]
    seam = _whole(_boundary(dim, cells[a]), back, dim, tol) and _whole(_boundary(dim, cells[b]), pieces, dim, tol)
    return shared, seam, out


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


def _add_free(entities, free_bodies, offset, copied, dim):
    """Add the free bodies (and their excitation surfaces) to the entities of model "full": their new nodes are numbered
    from offset, after every node of the groups; their frozen nodes are nodes of the groups."""
    V = np.vstack([one.V for one in copied] + [entry[4].added for entry in free_bodies] + [np.zeros((0, 3))])
    owned = np.zeros(len(V), dtype=bool)
    owned[: sum(len(one.V) for one in copied)] = True  # those are the groups' nodes
    base = offset
    for side, n, tags, mat_id, body in free_bodies:

        def numbered(conn):  # node i < n is the frozen node i of the side, the others are the new ones
            out = conn - n + base
            frozen = conn < n
            out[frozen] = tags[conn[frozen]]
            return out

        _, entity = entities.setdefault((dim, side, mat_id), (body.name, _Entity()))
        entity.add(0, V, owned, {t: numbered(c) for t, c in body.elements.items()})
        for smat_id, (name, per_type) in body.surfaces.items():
            _, entity = entities.setdefault((dim - 1, side, smat_id), (name, _Entity()))
            entity.add(0, V, owned, {t: numbered(c) for t, c in per_type.items()})
        base += len(body.added)


def _text(p, dim):
    return ", ".join(f"{float(v):.6g}" for v in p[:dim])


def _structured_names(free_job, dim):
    """The names of the free bodies the free job asks for a structured or recombined mesh."""
    by_id = {b["mat_id"]: b["name"] for b in free_job["bodies" if dim == 2 else "volumes"]}
    names = [b["name"] for b in (free_job.get("transfinite") or {}).get("bodies", [])]
    names += [by_id[m] for m in free_job.get("recombine", [])]
    return names + [f["name"] for f in free_job.get("recombine_faces", [])]


def _join_onto(W, xyz):
    """Number the nodes xyz among the nodes W: each one coincident with a node of W is that node, the others are
    appended. Returns (W with them, index[len(xyz)])."""
    count, labels = meshfrozen.join_nodes(np.vstack([W, xyz]))
    first = np.full(count, -1, dtype=np.int64)
    first[labels[::-1]] = np.arange(len(labels))[::-1]
    index = first[labels[len(W) :]]  # the lowest member of each joined node: the node of W when there is one
    fresh = index >= len(W)
    unique, inverse = np.unique(index[fresh], return_inverse=True)
    index[fresh] = len(W) + inverse.ravel()
    return np.vstack([W, xyz[unique - len(W)]]), index


def _missing(needed, have):
    """The rows of needed, sets of nodes, that are in no row of have."""
    first, second = np.sort(needed, axis=1), np.sort(have, axis=1)
    rows = np.unique(np.vstack([first, second]), axis=0, return_inverse=True)[1].ravel()
    return needed[~np.isin(rows[: len(first)], rows[len(first) :])]


def _turn_counterclockwise(face, W, elements):
    """2D: every element of elements turned counterclockwise seen from the plane of the free OCC face it came from
    (plane_normal), whichever way that face was drawn."""
    normal = np.array(plane_normal(face_normal(face)))
    for etype, conn in elements.items():
        a, b, c = W[conn[:, 0]], W[conn[:, 1]], W[conn[:, 2]]
        wrong = np.einsum("ij,j->i", np.cross(b - a, c - a), normal) < 0
        conn[wrong] = conn[wrong][:, meshfrozen.FLIP[etype]]


def _limit(name, reason, where):
    return JobError(
        f"free object {name}: {reason} near ({where}); this is not handled yet, a limit of the tool, not of the drawing"
    )


def _refuse_coincident(name, V, parts, dim):
    """Frozen facets of two groups that lie on each other (each group's own contacts have dropped out of its boundary)
    would leave two shells touching: their meshes are not joined, and which is inside which cannot be told."""
    if not any(len(p) for p in parts):
        return
    labels = meshfrozen.join_nodes(V)[1]
    for part in parts:
        if len(part):
            _, inverse, counts = np.unique(
                np.sort(labels[part], axis=1), axis=0, return_inverse=True, return_counts=True
            )
            twice = counts[inverse.ravel()] > 1
            if twice.any():
                raise JobError(
                    f"free object {name}: copies of two groups touch near ({_text(V[part[twice][0]].mean(axis=0), dim)})"
                    " inside it, which is not handled yet, a limit of the tool; put them in one group, or draw a"
                    " normally meshed body between them"
                )


def _copies_surface(side, dim):
    """The whole surface of the copies of a side as triangles (edges in 2D), running outward, for meshfrozen.wraps."""
    return np.vstack([side.edge] if dim == 2 else [side.tri, side.quad[:, [0, 1, 2]], side.quad[:, [0, 2, 3]]])


def _refuse_inside_a_copy(name, V, side, points, dim):
    """A free body with a point of its surface inside the solid of a copy overlaps that copy. The whole surface of the
    copies is used, with its facets running outward, so a cavity of a copy counts as outside. Clearly inside only: a
    point on a copy's surface gives one half, and that is for the checks of the facets."""
    every = _copies_surface(side, dim)
    if len(every):
        for point in points:
            if abs(meshfrozen.wraps(V, every, point)) > 0.75:
                raise JobError(
                    f"free object {name}: it lies inside a copy near ({_text(point, dim)}); the geometry does not fit"
                )


def _survey(body, entity, side, V, dim):
    """What the frozen facets of the side are to one OCC volume (face in 2D) of a free body: see Survey. A facet on one
    of its faces bounds it only when its owning element is outside it (flush against it); with the owner inside it is
    an end cap, which the free object cannot touch. Either way the face leaves room (_leave_room)."""
    faces = _boundary(dim, [(dim, entity)])
    kinds = {"edge": (side.edge, side.edge_owner)}
    if dim == 3:
        kinds = {"tri": (side.tri, side.tri_owner), "quad": (side.quad, side.quad_owner)}
    frozen, covered = {}, {}
    for kind, (rows, owners) in kinds.items():
        on = meshfrozen.on_surface(V, rows, owners, faces, dim)
        mask = meshfrozen.inside(dim, entity, V[rows].mean(axis=1))
        mask[on.index] = ~on.inside
        frozen[kind] = mask
        for k, face in zip(on.index.tolist(), on.face.tolist()):
            covered.setdefault(face, []).append(rows[k])
    return Survey(body, entity, faces, frozen, covered)


class _Vertices:
    """Points that coincide are one vertex: a frozen node and a corner of the free object can be the same place. tag
    gives its OCC point, an existing corner of the free object when it is one, else a new point at the frozen node."""

    def __init__(self, V, nodes, curves):
        corners = {int(t) for c in curves for _, t in gmsh.model.getBoundary([(1, c)], oriented=False)}
        corners = sorted(corners)
        xyz = [V[nodes]] + [np.array(gmsh.model.getValue(0, t, [])).reshape(1, 3) for t in corners]
        joined = np.vstack(xyz)
        labels = meshfrozen.join_nodes(joined)[1]
        self.of_node = dict(zip(nodes.tolist(), labels[: len(nodes)].tolist()))
        self.of_point = dict(zip(corners, labels[len(nodes) :].tolist()))
        self.xyz = dict(zip(labels.tolist(), joined))
        self.tags = {label: t for t, label in self.of_point.items()}

    def add(self, xyz):
        """A new vertex at xyz. Returns its label."""
        label = max(self.xyz) + 1
        self.xyz[label] = np.asarray(xyz, dtype=float)
        return label

    def tag(self, label):
        if label not in self.tags:
            self.tags[label] = gmsh.model.occ.addPoint(*self.xyz[label].tolist())
        return self.tags[label]


PART_OF_CURVED = "a copy covers only part of a curved face or edge of it"


def _tol():
    box = gmsh.model.getBoundingBox(-1, -1)
    return 1e-6 * max(1.0, math.dist(box[:3], box[3:]))


def _pieces(curve, nodes, pairs, vertices, V, tol):
    """The curve cut at those of the frozen nodes that lie on it: [(a, b, frozen)], a and b vertex labels, frozen True
    when the frozen edges pairs (sets of two vertex labels) hold that stretch. Empty when no frozen node lies on it
    but its ends."""
    box = np.array(gmsh.model.getBoundingBox(1, curve))
    near = nodes[np.all((V[nodes] >= box[:3] - tol) & (V[nodes] <= box[3:] + tol), axis=1)]
    corners = [int(t) for _, t in gmsh.model.getBoundary([(1, curve)], oriented=False)]
    if not len(near):
        return []
    coords = gmsh.model.getClosestPoint(1, curve, V[near].ravel().tolist())[0]
    close = np.linalg.norm(np.reshape(coords, (-1, 3)) - V[near], axis=1) <= tol
    on = [k for k in np.flatnonzero(close) if gmsh.model.isInside(1, curve, V[near[k]].tolist())]
    if not on:
        return []
    params = gmsh.model.getParametrization(1, curve, V[near].ravel().tolist())  # getClosestPoint's parameters are junk
    labels = [vertices.of_node[int(near[k])] for k in sorted(on, key=lambda k: params[k])]
    ends = [vertices.of_point[t] for t in corners]
    closed = len(set(ends)) < 2
    if closed:
        chain = labels + labels[:1]
    else:
        start, stop = _ends_in_order(curve, corners, ends)
        chain = [start] + [v for v in labels if v not in (start, stop)] + [stop]
    pieces = [(a, b, {a, b} in pairs) for a, b in zip(chain, chain[1:]) if a != b]
    if not closed and len(pieces) == 1 and not pieces[0][2]:
        return []  # only its ends touch a frozen node
    return pieces


def _ends_in_order(curve, corners, ends):
    params = gmsh.model.getParametrization(1, curve, [x for t in corners for x in gmsh.model.getValue(0, t, [])])
    return ends if params[0] <= params[1] else ends[::-1]


def _chords(curve, cut, vertices, size):
    """A curve whose stretches cannot be separate OCC curves: its pieces (see _pieces) with each stretch no frozen edge
    holds turned into straight chords of about size. Returns (those pieces, all marked frozen, as a planar face takes
    them; the vertices in order along the curve; True when it is closed)."""
    lo, hi = gmsh.model.getParametrizationBounds(1, curve)
    period = hi[0] - lo[0]
    closed = cut[0][0] == cut[-1][1]
    out, order = [], []
    for a, b, frozen in cut:
        order.append(a)
        if frozen:
            out.append((a, b, True))
            continue
        ua, ub = gmsh.model.getParametrization(1, curve, [*vertices.xyz[a], *vertices.xyz[b]])
        ub = ub + period if ub <= ua else ub
        along = (np.linspace(ua, ub, 33) - lo[0]) % period + lo[0] if closed else np.linspace(ua, ub, 33)
        samples = np.reshape(gmsh.model.getValue(1, curve, along.tolist()), (-1, 3))
        steps = max(1, math.ceil(float(np.linalg.norm(np.diff(samples, axis=0), axis=1).sum()) / size))
        chain = [a] + [vertices.add(samples[round(32 * k / steps)]) for k in range(1, steps)] + [b]
        out += [(p, q, True) for p, q in zip(chain, chain[1:])]
        order += chain[1:-1]
    if not closed:
        order.append(cut[-1][1])
    return out, order, closed


def _place_rim_nodes(rims):
    """After the curves are meshed: put the nodes of each rim, (curve, its target points in order, closed), on its
    targets. The rim was made transfinite with as many nodes. On a closed curve the node of its own vertex goes to the
    nearest target: the vertex stays where it is in the face's parameters, and only the node's place changes."""
    for curve, targets, closed in rims:
        tags, _, params = gmsh.model.mesh.getNodes(1, curve, False, True)
        tags = np.asarray(tags)[np.argsort(params)]
        rest = targets[1:-1] if not closed else targets
        if closed:
            every = gmsh.model.mesh.getNodes(1, curve, True)[0]
            vertex = next(int(t) for t in every if t not in set(tags.tolist()))
            first = gmsh.model.mesh.getNode(vertex)[0]
            k = int(np.argmin(np.linalg.norm(targets - first, axis=1)))
            gmsh.model.mesh.setNode(vertex, targets[k].tolist(), [])
            rest = np.vstack([targets[k + 1 :], targets[:k]])
        if len(rest) != len(tags):
            raise JobError(f"curve {curve}: gmsh made {len(tags)} inner nodes on a rim, {len(rest)} were asked for")
        us = gmsh.model.getParametrization(1, curve, rest.ravel().tolist())
        for tag, point, u in zip(tags.tolist(), rest.tolist(), us.tolist()):
            gmsh.model.mesh.setNode(tag, point, [u])


def _loops(edges):
    """Close edges [(a, b, payload)] into loops: [[(a, b, payload)]], each walked in order. None when a vertex has not
    exactly two of them (a copy touching another at one point on the face, or edges that do not close)."""
    at = {}
    for k, (a, b, _) in enumerate(edges):
        at.setdefault(a, []).append(k)
        at.setdefault(b, []).append(k)
    if any(len(v) != 2 for v in at.values()):
        return None
    loops, seen = [], set()
    for k in range(len(edges)):
        if k in seen:
            continue
        start = vertex = edges[k][0]
        current, loop = k, []
        while True:
            a, b, payload = edges[current]
            vertex_next = b if a == vertex else a
            loop.append((vertex, vertex_next, payload))
            seen.add(current)
            vertex = vertex_next
            if vertex == start:
                break
            current = at[vertex][0] if at[vertex][1] == current else at[vertex][1]
        loops.append(loop)
    return loops


def _plane_frame(face):
    """Two orthonormal axes of the plane of face, as an array[2, 3]."""
    lo, hi = gmsh.model.getParametrizationBounds(2, face)
    n = np.array(gmsh.model.getNormal(face, [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2]))
    u = np.cross(n, [1.0, 0.0, 0.0] if abs(n[0]) < 0.9 else [0.0, 1.0, 0.0])
    u /= np.linalg.norm(u)
    return np.array([u, np.cross(n, u)])


def _ring_points(loop, vertices):
    """The points of a loop of _loops, in order, with whole curves sampled."""
    points = []
    for a, b, payload in loop:
        kind, ref = payload
        if kind == "curve":
            lo, hi = gmsh.model.getParametrizationBounds(1, ref)
            params = np.linspace(lo[0], hi[0], 25)[: -1 if a == b else None]
            samples = np.reshape(gmsh.model.getValue(1, ref, params.tolist()), (-1, 3))
            if a != b and np.linalg.norm(samples[0] - vertices.xyz[a]) > np.linalg.norm(samples[-1] - vertices.xyz[a]):
                samples = samples[::-1]
            points.extend(samples[:-1] if a != b else samples)
        else:
            points.append(vertices.xyz[a])
    return np.array(points)


def _surfaces_of(face, loops, vertices):
    """Which loops (of _loops) of the planar face bound which of its remaining pieces: [(outer, [holes])] in loop
    numbers. A loop inside a hole bounds an island of the face (the bore of a ring of copies, say)."""
    frame = _plane_frame(face)
    rings, rows, start = [], [], 0
    for loop in loops:
        points = _ring_points(loop, vertices) @ frame.T
        rings.append(np.column_stack([points, np.zeros(len(points))]))
        count = len(points)
        rows.append(np.column_stack([np.arange(count), np.roll(np.arange(count), -1)]) + start)
        start += count
    flat, facets = np.vstack(rings), np.vstack(rows)
    shells, first = [], 0
    for ring in rings:
        shells.append(np.arange(first, first + len(ring)))
        first += len(ring)
    return meshfrozen.nest(flat, facets, shells)


def _new_size_field(by_size, dim):
    """One Constant field per {size: [entities of dimension dim]}, joined to the background Min field."""
    field = gmsh.model.mesh.field
    fmin = next(f for f in field.list() if field.getType(f) == "Min")
    fields = [int(f) for f in field.getNumbers(fmin, "FieldsList")]
    for size, tags in by_size.items():
        f = field.add("Constant")
        field.setNumber(f, "VIn", float(size))
        field.setNumbers(f, FIELD_LISTS[dim], tags)
        field.setNumber(f, "IncludeBoundary", 1)
        fields.append(f)
    field.setNumbers(fmin, "FieldsList", fields)


def _carry_size_picks(replaced, dim):
    """A Mesh Size picked on a face (line in 2D) that was replaced goes on to what replaced it."""
    field = gmsh.model.mesh.field
    for f in field.list():
        if field.getType(f) != "Constant":
            continue
        old = [int(t) for t in field.getNumbers(f, FIELD_LISTS[dim])]
        if any(t in replaced for t in old):
            field.setNumbers(f, FIELD_LISTS[dim], [n for t in old for n in replaced.get(t, [t])])


def _physical_groups_of(replaced, dim):
    """[(physical tag, name, entity tags)] of the physical groups of dimension dim that hold a replaced entity."""
    found = []
    for _, tag in gmsh.model.getPhysicalGroups(dim):
        members = [int(e) for e in gmsh.model.getEntitiesForPhysicalGroup(dim, tag)]
        if any(e in replaced for e in members):
            found.append((tag, gmsh.model.getPhysicalName(dim, tag), members))
    return found


def _carry_physical_groups(saved, replaced, dim):
    """Put each physical group of saved back with its replaced entities swapped for what replaced them."""
    for tag, name, members in saved:
        gmsh.model.removePhysicalGroups([(dim, tag)])
        new = [n for e in members for n in replaced.get(e, [e])]
        if new:
            gmsh.model.addPhysicalGroup(dim, new, tag, name=name)


def _outer_edges(rows, name, V):
    """The edges of the facets rows (a list of node rows of 3 or 4) that just one of them has: the boundary of the
    region they cover. Three facets on an edge are not a region."""
    edges = np.array([[r[k], r[(k + 1) % len(r)]] for r in (row.tolist() for row in rows) for k in range(len(r))])
    unique, counts = np.unique(np.sort(edges, axis=1), axis=0, return_counts=True)
    if (counts > 2).any():
        raise _limit(name, "copies overlap on its surface", _text(V[unique[counts > 2][0]].mean(axis=0), 3))
    return unique[counts == 1]


def _taken(face, rows, solid, V, dim, tol):
    """True when no part of the face (line in 2D) is free: every point of a grid over it, and a point just past every
    outer edge of its frozen facets rows (_free_beside), is on one of those facets or on or inside the copies, whose
    whole surface is solid. A free part always borders the covered region, so a gap between facets is found whatever
    its width and whether or not the grid falls in it; the grid finds a free part that holds no facet at all."""
    own = np.asarray(rows, dtype=np.int64).reshape(-1, 2) if dim == 2 else _triangles(rows)
    lo, hi = gmsh.model.getParametrizationBounds(dim - 1, face)
    count = 64 if dim == 2 else 24
    steps = [[lo[k] + (hi[k] - lo[k]) * (i + 0.5) / count for i in range(count)] for k in range(dim - 1)]
    found = False
    for uv in itertools.product(*steps):
        if dim == 3 and not gmsh.model.isInside(2, face, list(uv), parametric=True):
            continue
        found = True
        if _is_free(np.array(gmsh.model.getValue(dim - 1, face, list(uv))), own, solid, V, tol):
            return False
    return found and not _free_beside(face, rows, own, solid, V, dim, tol)


def _is_free(point, own, solid, V, tol):
    """True when point is not on one of the facets own, nor on or inside the copies (one half on a facet, one inside)."""
    if len(own) and meshfrozen.on_facets(V, own, point, tol):
        return False
    return not len(solid) or abs(meshfrozen.wraps(V, solid, point)) <= 0.1


def _free_beside(face, rows, own, solid, V, dim, tol):
    """True when the point just past some outer edge (in 2D, end node) of the frozen facets rows on face is free. An
    edge along the face's own rim has nothing of the face past it, or only the sliver between a chord and the curve."""
    sides = {}
    for row in rows:
        nodes = row.tolist()
        for k, n in enumerate(nodes):
            side = (n,) if dim == 2 else tuple(sorted((n, nodes[(k + 1) % len(nodes)])))
            sides[side] = None if side in sides else row
    for side, row in sides.items():
        if row is None:
            continue
        middle = V[list(side)].mean(axis=0)
        outward = middle - V[row].mean(axis=0)
        if dim == 3:
            along = V[side[1]] - V[side[0]]
            outward -= along * (outward @ along) / (along @ along)
        reach = float(np.linalg.norm(outward))
        beyond = middle + outward / reach * max(10 * tol, 5e-3 * reach)
        point = gmsh.model.getClosestPoint(dim - 1, face, beyond.tolist())[0]
        if gmsh.model.isInside(dim - 1, face, list(point)) and _is_free(point, own, solid, V, tol):
            if not _on_rim(face, side, V, dim, tol):
                return True
    return False


def _on_rim(face, side, V, dim, tol):
    """True when the outer edge side (nodes; one node in 2D) of a covered region runs along a bounding curve of face (in
    2D: the node is an end of the line)."""
    bounds = [abs(int(t)) for _, t in gmsh.model.getBoundary([(dim - 1, face)], oriented=False)]
    if dim == 2:
        return any(np.linalg.norm(V[side[0]] - gmsh.model.getValue(0, t, [])) <= tol for t in bounds)
    ends = V[list(side)]
    middle, length = ends.mean(axis=0), float(np.linalg.norm(ends[1] - ends[0]))
    for curve in bounds:
        near = np.reshape(gmsh.model.getClosestPoint(1, curve, [*ends.ravel(), *middle])[0], (-1, 3))
        off = np.linalg.norm(near - np.vstack([ends, middle]), axis=1)
        if off[0] <= tol and off[1] <= tol and off[2] <= max(tol, 0.2 * length):
            return True
    return False


def _triangles(rows):
    """The node rows of 3 or 4 of frozen facets as triangles[n, 3]."""
    tris = [t for row in rows for t in ([row[:3]] if len(row) == 3 else [row[[0, 1, 2]], row[[0, 2, 3]]])]
    return np.array(tris, dtype=np.int64).reshape(-1, 3)


def _open_lines(surveys, covered, names, V, side):
    """2D: a line of the free object that frozen edges lie on leaves room for them: dropped when no part of it is free
    (_taken), split at their end nodes otherwise, the pieces meshed as new lines. A curved line partly covered is a
    limit of the tool. A line with no frozen edge on it that ends on one and lies inside the copies is dropped too.
    Returns {line: [its new lines]}."""
    occ = gmsh.model.occ
    tol = _tol()
    nodes = np.unique(np.vstack([np.asarray(rows) for rows in covered.values()]))
    every = sorted({f for s in surveys for f in s.faces})
    vertices = _Vertices(V, nodes, every)
    sizes = {f: s.body["size"] for s in surveys for f in s.faces}
    solid = _copies_surface(side, 2)
    frozen_labels = set(vertices.of_node.values())
    replaced, by_size = {}, {}
    for line in every:
        if line in covered:
            continue
        ends = {vertices.of_point[int(t)] for _, t in gmsh.model.getBoundary([(1, line)], oriented=False)}
        if ends & frozen_labels and _taken(line, [], solid, V, 2, tol):
            replaced[line] = []
    for line, rows in covered.items():
        pairs = {frozenset(vertices.of_node[int(n)] for n in r) for r in rows}
        pieces = [p for p in _pieces(line, nodes, pairs, vertices, V, tol) if not p[2]]
        if pieces and _taken(line, rows, solid, V, 2, tol):
            pieces = []
        if pieces and gmsh.model.getType(1, line) != "Line":
            raise _limit(names[line], PART_OF_CURVED, _text(V[rows[0]].mean(axis=0), 2))
        replaced[line] = [occ.addLine(vertices.tag(a), vertices.tag(b)) for a, b, _ in pieces]
        if replaced[line]:
            by_size.setdefault(sizes[line], []).extend(replaced[line])
    occ.synchronize()
    if by_size:
        _new_size_field(by_size, 1)
    _carry_size_picks(replaced, 1)
    return replaced


def _open_faces(surveys, covered, names, V, side):
    """3D: the faces that frozen facets lie on leave room for them, and so do the faces that share a curve with those. A
    face with no free part (_taken: under frozen facets or inside the copies) is dropped; a planar one with a free part
    is rebuilt with one hole per loop of the region's outer
    edges, through the exact nodes of the copies (each polygon line one element), and a stretch of a bounding curve that
    only reaches a frozen node is kept. A curved face the copies reach only along its rim keeps its surface and its
    curves, whose mesh goes through the frozen nodes (_chords, _place_rim_nodes). A curved face partly covered is a limit
    of the tool. Returns ({face: [the faces in its place]}, the rims for _place_rim_nodes); the new tags come after an
    occ.remove of the volumes: their face lists come from the surveys, read first."""
    tol = _tol()
    faces = {f for s in surveys for f in s.faces}
    outer = {f: _outer_edges(rows, names[f], V) for f, rows in covered.items()}
    nodes = np.unique(np.vstack(list(outer.values())))
    curves_of = {f: [abs(int(t)) for _, t in gmsh.model.getBoundary([(2, f)], oriented=False)] for f in faces}
    curves = sorted({c for cs in curves_of.values() for c in cs})
    seams = {c for c in curves if len(gmsh.model.getAdjacencies(1, c)[0]) < 2}  # bounds a single face: its seam
    vertices = _Vertices(V, nodes, [c for c in curves if c not in seams])
    every = {frozenset(vertices.of_node[int(n)] for n in e) for edges in outer.values() for e in edges}
    pieces = {}
    for c in curves:
        if c not in seams:
            cut = _pieces(c, nodes, every, vertices, V, tol)
            if cut:
                pieces[c] = cut
    solid = _copies_surface(side, 3)
    touched = sorted(f for f in faces if f in outer or any(c in pieces for c in curves_of[f]))
    taken = {f for f in touched if _taken(f, covered.get(f, []), solid, V, 3, tol)}
    kept_curved = {f for f in faces if f not in outer and f not in taken and gmsh.model.getType(2, f) != "Plane"}
    sizes = {f: s.body["size"] for s in surveys for f in s.faces}
    rims = []
    for c, cut in list(pieces.items()):
        on_kept = any(c in curves_of[f] for f in kept_curved)
        if on_kept or gmsh.model.getType(1, c) != "Line":
            size = min(sizes[f] for f in faces if c in curves_of[f])
            pieces[c], order, closed = _chords(c, cut, vertices, size)
            if on_kept:
                rims.append((c, np.array([vertices.xyz[v] for v in order]), closed))
    plans, dropped = {}, []
    for f in sorted(faces):
        if f in taken:
            dropped.append(f)
            continue
        if f in kept_curved or (f not in outer and not any(c in pieces for c in curves_of[f])):
            continue
        mine = {frozenset(vertices.of_node[int(n)] for n in e) for e in outer.get(f, ())}
        edges, along = [], set()
        for c in curves_of[f]:
            if c in seams:
                continue
            if c not in pieces:
                ends = [vertices.of_point[int(t)] for _, t in gmsh.model.getBoundary([(1, c)], oriented=False)]
                a, b = (ends[0], ends[-1]) if ends else (-c, -c)  # a closed curve is a loop on its own
                edges.append((a, b, ("curve", c)))
                continue
            for a, b, frozen in pieces[c]:
                if frozen and frozenset((a, b)) in mine:
                    along.add(frozenset((a, b)))
                else:
                    edges.append((a, b, ("frozen" if frozen else "line", None)))
        for pair in mine - along:  # the region's edges inside the face
            a, b = sorted(pair)
            edges.append((a, b, ("frozen", None)))
        if not edges:
            dropped.append(f)
            continue
        if gmsh.model.getType(2, f) != "Plane":
            raise _limit(names[f], PART_OF_CURVED, _text(V[covered[f][0]].mean(axis=0), 3))
        plans[f] = edges
    return _rebuild(plans, dropped, surveys, vertices, names, rims), rims


def _rebuild(plans, dropped, surveys, vertices, names, rims):
    """Apply _open_faces: every free volume that has a face to change is taken out of the OCC model (not its faces),
    each of those faces is removed and the planned ones are made again as plane surfaces, keeping physical groups and
    sizes. Returns {face: [new faces]}."""
    occ = gmsh.model.occ
    replaced = {f: [] for f in dropped}
    loops_of = {}
    for f, edges in plans.items():
        loops = _loops(edges)
        if loops is None:  # two loops touching at a point
            where = gmsh.model.occ.getCenterOfMass(2, f)
            raise _limit(names[f], "copies touch each other at a point on a face of it", _text(where, 3))
        loops_of[f] = loops
    gone = set(plans) | set(dropped)
    volumes = sorted({int(v) for f in gone for v in gmsh.model.getAdjacencies(2, f)[0]})
    saved = _physical_groups_of(gone, 2)
    occ.remove([(3, v) for v in volumes], recursive=False)
    occ.remove([(2, f) for f in sorted(gone)], recursive=False)
    polygon, lines = set(), {}

    def line(a, b, frozen):
        key = frozenset((a, b))
        if key not in lines:
            lines[key] = occ.addLine(vertices.tag(a), vertices.tag(b))
        if frozen:
            polygon.add(lines[key])
        return lines[key]

    for f, loops in loops_of.items():
        wires = []
        for loop in loops:
            curves = [
                payload[1] if payload[0] == "curve" else line(a, b, payload[0] == "frozen") for a, b, payload in loop
            ]
            wires.append(occ.addCurveLoop(curves))
        replaced[f] = [
            occ.addPlaneSurface([wires[outer]] + [wires[h] for h in holes])
            for outer, holes in _surfaces_of(f, loops, vertices)
        ]
    occ.synchronize()
    for tag in polygon:
        gmsh.model.mesh.setTransfiniteCurve(tag, 2)
    for curve, targets, closed in rims:
        gmsh.model.mesh.setTransfiniteCurve(curve, len(targets) + (1 if closed else 0))
    _carry_physical_groups(saved, replaced, 2)
    _carry_size_picks(replaced, 2)
    gone_volumes = set(volumes)
    _carry_size_picks({v: [] for v in gone_volumes}, 3)  # a size field naming a volume that is gone would fail
    by_size = {}
    for s in surveys:
        if s.entity in gone_volumes:
            for f in s.faces:
                by_size.setdefault(s.body["size"], set()).update(replaced.get(f, [f]))
    if by_size:
        _new_size_field({size: sorted(tags) for size, tags in by_size.items()}, 2)
    return replaced


def _leave_room(surveys, V, dim, side):
    """Open the free surface where frozen facets lie on it (see _open_faces, _open_lines). Returns (the surveys with the
    faces they have now, for the model has changed; the rims for _place_rim_nodes)."""
    covered = {}
    for s in surveys:
        covered.update(s.covered)  # a face between two bodies has the same facets on it for both
    if not covered:
        return surveys, []
    names = {f: s.body["name"] for s in surveys for f in s.faces}
    replaced, rims = (
        _open_faces(surveys, covered, names, V, side)
        if dim == 3
        else (_open_lines(surveys, covered, names, V, side), [])
    )
    return [s._replace(faces=[n for f in s.faces for n in replaced.get(f, [f])]) for s in surveys], rims


def _meets(faces, where, dim):
    """What it is that an open surface near the point where shows: the copy crosses a curved face, or a planar one."""
    if not faces:
        return "a copy meets its surface"
    nearest = min(
        faces,
        key=lambda f: math.dist(where, gmsh.model.getClosestPoint(dim - 1, f, list(map(float, where)))[0]),
    )
    if gmsh.model.getType(dim - 1, nearest) in ("Plane", "Line"):
        return "a copy crosses its surface without ending on it"
    return "a copy crosses a curved face of it"


def _mesh_free_entity(survey, side, V, dim):
    """Mesh one OCC volume (face in 2D) of a free body whose surface is already meshed. The facets of its own surface
    and the frozen facets that bound it (survey.frozen) bound one region or several (nest), each meshed by
    mesh_region. Returns (W, elements, own): W is V with the apexes of the pyramids and the new nodes appended,
    elements numbered into it, own {face: {etype: connectivity}} the mesh of each of its own faces, for excitations."""
    body, entity, faces = survey.body, survey.entity, survey.faces
    name = body["name"]
    xyz, own = meshfrozen.read_model(dim - 1, {f: [f] for f in faces})
    facet_type = 2 if dim == 3 else 1
    pyramids = np.zeros((0, 5), dtype=np.int64)
    W = V
    quads = np.zeros((0, 4), dtype=np.int64)
    if dim == 3:
        mask, quad_mask = survey.frozen["tri"], survey.frozen["quad"]
        tris, quads = side.tri[mask], side.quad[quad_mask]
        _refuse_coincident(name, V, (tris, quads), dim)
        W, pyramids, sides = meshfrozen.quad_pyramids(V, quads)  # gmsh sees only their triangles
        frozen, needed = np.vstack([tris, sides]), tris
        owners = np.vstack([side.tri_owner[mask], np.repeat(side.quad_owner[quad_mask], 4, axis=0)])
    else:
        mask = survey.frozen["edge"]
        frozen = needed = side.edge[mask]
        _refuse_coincident(name, V, (frozen,), dim)
        owners = side.edge_owner[mask]
    W, mine = _join_onto(W, xyz)
    own = {f: {t: mine[c] for t, c in per.items()} for f, per in own.items()}
    pieces = [per[facet_type] for per in own.values() if facet_type in per]
    surface = np.vstack(pieces) if pieces else np.zeros((0, facet_type + 1), dtype=np.int64)
    facets = np.vstack([surface, frozen])
    if not len(facets):  # every face of it is taken, and nothing of the copies bounds it: it is all inside them
        raise JobError(f"free object {name}: it lies wholly inside copies; the geometry does not fit")
    try:
        found = meshfrozen.shells(facets)
    except meshfrozen.FrozenError as err:
        where = W[err.nodes].mean(axis=0) if err.nodes is not None else W[facets[0]].mean(axis=0)
        raise _limit(name, _meets(faces, where, dim), _text(where, dim)) from None
    regions = meshfrozen.nest(W, facets, found)
    # own surface inside a hole of the free object (a copy around a cavity): its inside is not free space. Removing
    # copies may leave several regions with their own outer surfaces, but those do not lie inside one another
    for outer, _ in regions:
        if found[outer].min() >= len(surface):
            continue
        point = W[facets[found[outer][0]]].mean(axis=0)
        if any(i != outer and meshfrozen.encloses(W, facets, found[i], point) for i, _ in enumerate(found)):
            raise _limit(name, "an inner surface of it lies inside a copy", _text(point, dim))
    # after the checks above: a surface that crosses a copy is a limit of the tool, one wholly inside it does not fit
    if len(surface):
        _refuse_inside_a_copy(name, V, side, W[surface[[0, len(surface) // 2, -1]]].mean(axis=1), dim)
    for outer, holes in regions:  # a frozen shell has the solid of its copies inside it only when it is a hole
        for shell, solid_inside in [(outer, False)] + [(h, True) for h in holes]:
            first = found[shell][0]
            if found[shell].min() >= len(surface):
                if meshfrozen.encloses(W, facets, found[shell], owners[first - len(surface)]) != solid_inside:
                    where = _text(W[facets[first]].mean(axis=0), dim)
                    raise _limit(name, "copies of its side overlap or touch each other", where)
    elements = {}
    if len(pyramids):
        elements[7] = pyramids
    for outer, holes in regions:
        try:
            W, region = meshfrozen.mesh_region(W, facets, found[outer], [found[h] for h in holes], body["size"], dim)
        except Exception as err:  # gmsh could not mesh around them, or moved a frozen node
            where = W[facets[found[outer][0]]].mean(axis=0)
            raise _limit(name, f"the mesh around the copies failed ({err})", _text(where, dim)) from None
        for etype, conn in region.items():
            elements[etype] = np.vstack([elements[etype], conn]) if etype in elements else conn
    if dim == 2:
        _turn_counterclockwise(entity, W, elements)
    whole = meshfrozen.boundary(W, [elements], dim)
    if whole.over_used:
        raise _limit(name, "a face has more than two elements", _where(W, [elements], dim))
    for wanted, have in ((np.vstack([surface, needed]), whole.tri if dim == 3 else whole.edge), (quads, whole.quad)):
        lost = _missing(wanted, have)
        if len(lost):
            where = _text(W[lost[0]].mean(axis=0), dim)
            raise _limit(name, "the elements around the copies did not keep a face", where)
    return W, elements, own


def mesh_free(free, side_boundary, V, job, folder, build, dim):
    """Mesh the free bodies of one side around the frozen facets of its copies. free: an entry of symmetric["free"];
    side_boundary: the Boundary of the side's copies, node numbers into V. Returns {mat_id: FreeBody}: FreeBody.added
    are the new nodes, numbered after those of V, and the frozen nodes keep their numbers."""
    free_job = free["job"]
    names = _structured_names(free_job, dim)
    if names:
        raise JobError(
            f"free object {names[0]}: a Transfinite or Recombine setting on a free object is not handled yet, a limit"
            " of the tool, not of the drawing"
        )
    out = {}
    start = len(V)
    with _scratch(f"free_{free['side']}"):
        build(dict(free_job), folder)
        bodies = free_job["bodies" if dim == 2 else "volumes"]
        surveys = [
            _survey(b, int(e), side_boundary, V, dim)
            for b in bodies
            for e in gmsh.model.getEntitiesForPhysicalGroup(dim, b["mat_id"])
        ]
        surveys, rims = _leave_room(
            surveys, V, dim, side_boundary
        )  # only now: the volumes of the changed faces leave the model
        settings = dict(free_job, options=job.get("options", {}))
        if rims:  # gmsh keeps a mesh of the curves when asked for the surfaces next
            generate(settings, 1)
            _place_rim_nodes(rims)
        generate(settings, dim - 1)
        surfaces = free_job.get("surfaces", [])
        for body in bodies:
            added, elements, excited, count = [], {}, {}, 0
            for survey in surveys:
                if survey.body is not body:
                    continue
                W, per_type, own = _mesh_free_entity(survey, side_boundary, V, dim)
                shifted = {t: np.where(c >= start, c + count, c) for t, c in per_type.items()}
                for etype, conn in shifted.items():
                    elements[etype] = np.vstack([elements[etype], conn]) if etype in elements else conn
                # an excitation's group is gone when its faces are all under copies
                alive = {tag for _, tag in gmsh.model.getPhysicalGroups(dim - 1)}
                for s in surfaces:
                    if s["mat_id"] != body["mat_id"] or s["smat_id"] not in alive:
                        continue
                    for face in gmsh.model.getEntitiesForPhysicalGroup(dim - 1, s["smat_id"]):
                        for etype, conn in own.get(int(face), {}).items():
                            lifted = np.where(conn >= start, conn + count, conn)
                            per = excited.setdefault(s["smat_id"], (s["name"], {}))[1]
                            per[etype] = np.vstack([per[etype], lifted]) if etype in per else lifted
                added.append(W[start:])
                count += len(W) - start
            for s in surfaces:
                if s["mat_id"] == body["mat_id"] and s["smat_id"] not in excited:
                    raise JobError(
                        f"free object {body['name']}: the face of the excitation {s['name']} is wholly under copies;"
                        " the geometry does not fit"
                    )
            out[body["mat_id"]] = FreeBody(body["name"], np.vstack(added or [np.zeros((0, 3))]), elements, excited)
    return out


def _side_pool(side, groups_, copied, wholes, offsets):
    """The copies of one side as one mesh: (V, the pooled Boundary, tags: full-model node number of each node of V)."""
    members = [k for k, g in enumerate(groups_) if g["side"] == side]
    V = np.vstack([np.zeros((0, 3))] + [copied[k].V for k in members])
    starts = np.cumsum([0] + [len(copied[k].V) for k in members])
    tags = np.concatenate([np.zeros(0, dtype=np.int64)] + [offsets[k] + np.arange(len(copied[k].V)) for k in members])

    def facets(field, width):
        return np.vstack(
            [np.zeros((0, width), dtype=np.int64)] + [getattr(wholes[k], field) + s for k, s in zip(members, starts)]
        )

    def owners(field):
        return np.vstack([np.zeros((0, 3))] + [getattr(wholes[k], field) for k in members])

    pool = meshfrozen.Boundary(
        facets("tri", 3),
        facets("quad", 4),
        facets("edge", 2),
        owners("tri_owner"),
        owners("quad_owner"),
        owners("edge_owner"),
        sum(wholes[k].over_used for k in members),
        sum(wholes[k].shared_area for k in members),
    )
    return V, pool, tags


def mesh(job, folder, build, dim):
    """Mesh the cell of every group, copy it, check the copies, mesh the free objects around them and put them all in
    model "full" (current): one entity per (side, MAT_ID) and per (side, SMAT_ID). Returns a Model."""
    symmetric = job["symmetric"]
    slide = symmetric.get("slide")
    copied, wholes = [], []
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
        wholes.append(whole)
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
    offsets = np.cumsum([0] + [len(one.V) for one in copied[:-1]]) if copied else np.zeros(0, dtype=np.int64)
    free_bodies = []  # (side, len(V of the side), full-model number of each node of V, mat_id, FreeBody)
    for free in symmetric.get("free", []):
        V, pool, tags = _side_pool(free["side"], symmetric["groups"], copied, wholes, offsets)
        for mat_id, body in mesh_free(free, pool, V, job, folder, build, dim).items():
            free_bodies.append((free["side"], len(V), tags, mat_id, body))
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
    _add_free(entities, free_bodies, offset, copied, dim)
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
        for name, poor, total in job["poor"]:
            if poor:  # a NOTE: line, which the runner shows when the mesh is loaded (spec section 6: warned)
                _note(f"Poor elements  {name}  {poor} of {total} have a minimum SICN below {POOR}")
        point = (meshsym._marker if dim == 2 else meshsym._marker_line)(slide) if slide else None
        gmsh.option.setNumber("Mesh.MshFileVersion", MSH_VERSION)
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.write(os.path.join(folder, "mesh.unv"))
        if slide:
            outputs.append((os.path.join(folder, "moving.msh"), job["rotor_file"]))
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
    """The lines run_job prints: one MAT_ID line per part, one SMAT_ID line per excitation, the file written. The poor
    elements of a part are a note of run's (stderr), not a line here."""
    groups = job["symmetric"]["groups"]
    free = job["symmetric"].get("free", [])
    seen = {(p["mat_id"], p["name"]): None for g in groups for p in g["parts"]}
    seen.update(
        ((b["mat_id"], b["name"]), None) for f in free for b in f["job"].get("volumes", f["job"].get("bodies", []))
    )
    lines = [f"MAT_ID  {id_:>6}  {name}" for id_, name in seen]
    excited = {(x["smat_id"], x["name"]): None for g in groups for x in g.get("excitations", [])}
    excited.update(((s["smat_id"], s["name"]), None) for f in free for s in f["job"].get("surfaces", []))
    lines += [f"SMAT_ID {id_:>6}  {name}" for id_, name in excited]
    slide = job["symmetric"].get("slide")
    if slide:
        lines += slide_report({"slides": [slide]})
    lines.append(f"Wrote {job['mesh_file']}")
    if slide:
        lines.append(f"Wrote {job['rotor_file']}")
    return lines
