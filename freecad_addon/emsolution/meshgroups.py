"""Symmetric mesh by groups: mesh each group's cell, copy the mesh by the group's transforms with numpy (meshfrozen) and
give every copy the part its row names. Runs in the mesher process (mesher2d.run_job and mesher.run_job call run for a
job whose "symmetric" has "groups"); dim is 2 (faces) or 3 (solids). Never import FreeCAD here."""

import json
import os
from collections import namedtuple

import gmsh
import numpy as np

from meshcommon import JobError, generate, import_brep, publish, MSH_VERSION
import meshfrozen
import meshsym

POOR = 0.1  # an element whose min SICN is below this is reported as poor

# elements: {(row index, copy): {etype: ndarray}}; patches: [(excitation, {etype: ndarray})] of the landed copies
Copied = namedtuple("Copied", "V elements patches")
# split and surfaces: {side: {id: (name, [entity tags])}} of model "full", for the bodies and the excitation surfaces
Model = namedtuple("Model", "split surfaces")


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


def mesh_cell(group, job, folder, build, dim):
    """Mesh the cell of a group in a model of its own (removed at the end) and copy it by the group's transforms.
    Returns Copied: the joined nodes V, the elements of each (row, copy), and the cell boundary patches that land on an
    excitation, copied with their copy."""
    gmsh.model.add(f"cell_{group['name']}")
    try:
        build(dict(group["job"]), folder)
        meshsym._periodic([group], dim)
        generate(dict(group["job"], options=job.get("options", {})), dim)
        by_row = _by_row(group, folder, dim)
        cell_patches = meshsym._cell_patches(group, dim)
        labels = meshsym._land_surfaces([group], [cell_patches], folder, dim)[0] if cell_patches else []
        xyz, bodies = meshfrozen.read_model(dim, by_row)
        pxyz, patches = meshfrozen.read_model(dim - 1, {j: [p[0]] for j, p in enumerate(cell_patches)})
    finally:
        gmsh.model.remove()
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
    return Copied(V, elements, copied)


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
    if symmetric.get("slide"):
        raise JobError("a sliding interface in a group job is not supported yet")
    copied = []
    for group in symmetric["groups"]:
        one = mesh_cell(group, job, folder, build, dim)
        every = list(one.elements.values())
        if meshfrozen.boundary(one.V, every, dim).over_used:
            where = _where(one.V, every, dim)
            raise JobError(
                f"the copies of {group['name']} do not fit: a face has more than two elements near ({where})"
            )
        copied.append(one)
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
    job["mesh_file"] with the finished .msh. Returns the job, with the poor elements per part in job["poor"]."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    msh = os.path.join(folder, "mesh.msh")
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        model = mesh(job, folder, build, dim)
        job["poor"] = _poor(model, dim)
        gmsh.option.setNumber("Mesh.MshFileVersion", MSH_VERSION)
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.write(os.path.join(folder, "mesh.unv"))
        gmsh.write(msh)
    finally:
        gmsh.finalize()
    publish([(msh, job["mesh_file"])])
    return job


def report(job):
    """The lines run_job prints: one MAT_ID line per part, one SMAT_ID line per excitation, the poor elements of each
    part that has any, the file written."""
    groups = job["symmetric"]["groups"]
    seen = {(p["mat_id"], p["name"]): None for g in groups for p in g["parts"]}
    lines = [f"MAT_ID  {id_:>6}  {name}" for id_, name in seen]
    excited = {(x["smat_id"], x["name"]): None for g in groups for x in g.get("excitations", [])}
    lines += [f"SMAT_ID {id_:>6}  {name}" for id_, name in excited]
    lines += [f"Poor elements  {name}  {poor} of {total}" for name, poor, total in job.get("poor", []) if poor]
    lines.append(f"Wrote {job['mesh_file']}")
    return lines
