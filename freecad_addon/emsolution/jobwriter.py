"""Study -> checks -> job.json + BREP files for mesher.py / mesher2d.py."""

import json
import os

from . import airshapes, geometry, objects, sides, sweeps, validation
from .geometry import global_shape


SLIDE_KINDS = {"Rotational": "rotational", "Axial gap": "axial", "Linear": "linear"}


class StudyError(Exception):
    pass


def simulation_folder(study):
    """The folder of the saved .FCStd: EMSolution's run folder."""
    if not study.Document.FileName:
        raise StudyError("Save the document in the simulation folder first.")
    return os.path.dirname(os.path.abspath(study.Document.FileName))


def scratch_folder(study):
    """Gmsh working files: <simulation folder>/.pyemsi/freecad/<FCStd stem>/<Study Name>."""
    stem = os.path.splitext(os.path.basename(study.Document.FileName))[0]
    return os.path.join(simulation_folder(study), ".pyemsi", "freecad", stem, study.Name)


def mesh_file(study):
    """The fixed name EMSolution reads from the run folder."""
    return os.path.join(simulation_folder(study), "pre_geom2D.msh" if study.Dimension == "2D" else "pre_geom.msh")


def rotor_file(study):
    """The moving part's mesh, written by the slide job next to the mesh file."""
    return os.path.join(simulation_folder(study), "rotor_mesh2D.msh" if study.Dimension == "2D" else "rotor_mesh.msh")


def check(study):
    """Refuse the Study if validation finds an error. Returns (volumes, surfaces, elements):
    volumes  = [(body, size_mm)] in tree order (with Symmetric Groups the free bodies, then the cell objects)
    surfaces = [(excitation, body, [face names])] in tree order
    elements = [(mesh size, body, [face, edge and vertex names])] in tree order
    """
    found = validation.errors(validation.validate(study))
    if found:
        raise StudyError("\n".join(p.text for p in found))
    bodies = geometry.study_geometry(study)[0]
    surface_on = None  # the names excitations sit on, when not the meshed bodies themselves
    if objects.is_grouped(study):  # the free objects, then the cell objects of the groups
        surface_on = {b.Name for b in bodies} | {g.Name for g in objects.symmetric_groups(study)}
        bodies = bodies + objects.cell_bodies(study)
    included = surface_on if surface_on is not None else {b.Name for b in bodies}
    excitation_items = objects.excitations(study) if study.Dimension == "3D" else []  # 2D: none yet
    surfaces = [(e, b, faces) for e in excitation_items for b, faces in objects.subs_by_body(e) if b.Name in included]
    with_air = validation.meshed(study, bodies)  # the air takes Mesh Sizes like a body
    sized = [
        (s, b, subs) for s in objects.mesh_sizes(study) for b, subs in objects.subs_by_body(s) if b.Name in with_air
    ]
    elements = [(s, b, [n for n in subs if n]) for s, b, subs in sized]
    elements = [el for el in elements if el[2]]
    volumes = [(b, size) for b, size, _item in validation.body_sizes(study, bodies)]
    return volumes, surfaces, elements


def air_size(study):
    """The smallest whole-body Mesh Size on the Air Region, else the default size."""
    air = {a.Name for a in objects.air_regions(study)}
    sizes = [
        s.Size.Value
        for s in objects.mesh_sizes(study)
        for b, subs in objects.subs_by_body(s)
        if b.Name in air and "" in subs
    ]
    return min(sizes, default=study.MeshSizesGroup.DefaultMeshSize.Value)


def transfinite_items(study, bodies):
    """The Study's transfinite items on bodies, after check(). Returns (structured, edges):
    structured = [(item, body, faces, [corner vertex names])] in tree order, one per body of an item;
                 faces as objects.face_picks gives them ([] = the whole body)
    edges      = [(item, body, [edge names])] in tree order
    """
    included = {b.Name for b in bodies}
    structured = []
    for t in objects.transfinite_bodies(study):
        corners = {}
        for b, subs in t.Corners:
            corners.setdefault(b.Name, []).extend(subs)
        for b, faces in objects.face_picks(t):
            if b.Name in included:
                structured.append((t, b, faces, corners.get(b.Name, [])))
    edges = [
        (e, b, list(subs))
        for e in objects.transfinite_edges(study)
        for b, subs in objects.subs_by_body(e)
        if b.Name in included
    ]
    return structured, edges


def mesh_options(settings, dimension="3D"):
    """Gmsh options from the Mesh Sizes folder; a min or max size of 0 keeps Gmsh's default."""
    opts = {
        "Mesh.Algorithm": objects.ALGORITHMS_2D[settings.SurfaceAlgorithm],
        "Mesh.MeshSizeFactor": settings.SizeFactor,
        "Mesh.Smoothing": settings.SmoothingSteps,
        "Mesh.RecombinationAlgorithm": objects.RECOMBINATION_ALGORITHMS[settings.RecombinationAlgorithm],
    }
    if dimension == "3D":
        opts["Mesh.Algorithm3D"] = objects.ALGORITHMS_3D[settings.VolumeAlgorithm]
        opts["Mesh.OptimizeNetgen"] = int(settings.OptimizeNetgen)
    if settings.MinSize.Value > 0:
        opts["Mesh.MeshSizeMin"] = settings.MinSize.Value
    if settings.MaxSize.Value > 0:
        opts["Mesh.MeshSizeMax"] = settings.MaxSize.Value
    return opts


def meshed_shape(body):
    """The shape of body the mesh gets: an Air Region's is built from its properties, as validation sees it."""
    if objects.is_air(body):
        return airshapes.air_shape(body, airshapes.study_plane(objects.owner_study(body)))
    return global_shape(body)


# {body Name: the shape its vol file holds} for the bodies whose sweep is rebuilt, while write_job writes a job
_rebuilt = {}


def _on_rebuild(element, rebuilt):
    """Of rebuilt's sub-shapes of element's type (face, edge or vertex), the one whose centre of mass lies nearest
    element's, within sweeps.FOLLOW_TOL x size; element itself when none does. A face picked on the original body
    would be about 1e-5 off the rebuild's and split by the mesher's fragment."""
    kind = {"Face": "Faces", "Edge": "Edges", "Vertex": "Vertexes"}.get(element.ShapeType)
    if kind is None:
        return element

    def centre(shape):
        return shape.Point if shape.ShapeType == "Vertex" else shape.CenterOfMass

    tol = sweeps.FOLLOW_TOL * max(1.0, rebuilt.BoundBox.DiagonalLength)
    at = centre(element)
    near = [(centre(other).distanceToPoint(at), k) for k, other in enumerate(getattr(rebuilt, kind))]
    best = min(near, default=None)
    return getattr(rebuilt, kind)[best[1]] if best is not None and best[0] <= tol else element


def export_subs(folder, body, subs, prefix):
    """Write each sub-element of body to geometry/<prefix>_<n>.brep. Returns the relative paths. A body whose sweep is
    rebuilt (_rebuilt) gets each sub-element's match on the rebuild (_on_rebuild)."""
    shape = meshed_shape(body)
    rebuilt = _rebuilt.get(body.Name)
    files = []
    for n, sub in enumerate(subs, 1):
        rel = f"geometry/{prefix}_{n}.brep"
        element = shape.getElement(sub)
        if rebuilt is not None:
            element = _on_rebuild(element, rebuilt)
        element.exportBrep(os.path.join(folder, rel))
        files.append(rel)
    return files


def refine_entries(study, folder, ids, prefix="", group=None):
    """The job's "refine" list: one entry per Refine Near item that refers to the mesh. ids is {body or air Name:
    [MAT_ID, ...]}; a whole-body reference goes to "whole" (it wins over sub-elements of that body), the sub-elements
    are written to geometry/<prefix>refine_<item>_<body>_<n>.brep. group: the Symmetric Group whose cell job this is;
    a whole cell object then also picks its faces toward the free side (validation.free_faces), which the cell job
    holds nothing beyond."""
    entries = []
    for k, item in enumerate(objects.refine_items(study), 1):
        files, whole = [], []
        for j, (body, subs) in enumerate(objects.subs_by_body(item), 1):
            if body.Name not in ids:
                continue
            if "" in subs:
                whole.extend(ids[body.Name])
                if group is not None:
                    free = validation.free_faces(study, group, body)
                    files.extend(export_subs(folder, body, free, f"{prefix}refine_{k}_{j}"))
            else:
                files.extend(export_subs(folder, body, subs, f"{prefix}refine_{k}_{j}"))
        if not (files or whole):
            continue
        limit_to = [mat_id for body in item.LimitTo if body.Name in ids for mat_id in ids[body.Name]]
        if item.LimitTo and not limit_to:  # no Limit to body is meshed: the refinement has nowhere to apply
            continue
        entries.append(
            {
                "name": item.Label,
                "files": files,
                "whole": whole,
                "fine": item.FineSize.Value,
                "fine_distance": item.FineDistance.Value,
                "coarse": item.CoarseSize.Value,
                "growth": item.GrowthDistance.Value,
                "limit_to": limit_to,
            }
        )
    return entries


def air_grading_entries(study, ids):
    """The job's "air_grading" list: one entry per Air Grading whose air is meshed here. ids is {body or air Name:
    [MAT_ID, ...]}, the map refine_entries takes."""
    entries = []
    for item in objects.air_gradings(study):
        mat_ids = [mat_id for body, _ in objects.item_refs(item) if body.Name in ids for mat_id in ids[body.Name]]
        if mat_ids:
            entries.append(
                {
                    "name": item.Label,
                    "mat_ids": mat_ids,
                    "growth": item.GrowthDistance.Value,
                    "far": objects.far_size(item),
                }
            )
    return entries


def recognised_sweeps(study, names):
    """{body Name: [Sweep per solid]} for the whole bodies of Swept Body items whose Names are in names, each body
    from the first item that has it. A body that is no sweep is left out: validation refuses it before a job is
    written."""
    found, seen = {}, set()
    for item in objects.swept_bodies(study):
        for body, sub in objects.item_refs(item):
            if sub != "" or body.Name not in names or body.Name in seen:
                continue
            seen.add(body.Name)
            starts = [s for b, subs in item.StartFace if b.Name == body.Name for s in subs]
            result = sweeps.recognise_body(meshed_shape(body), starts)
            if not isinstance(result, str):
                found[body.Name] = result
    return found


def swept_entries(study, folder, ids, found, prefix="", group=None):
    """The job's "swept" list: one entry per whole body of a Swept Body item that is in ids ({body Name: MAT_ID}), in
    tree order. found: recognised_sweeps for ids. The profile face of each solid (its start face, or a closed ring's
    cut) is written to geometry/<prefix>sweep_<MAT_ID>_<k>.brep in global coordinates. The skin comes from the first
    Skin Layer on the body. group: the Symmetric Group whose cell job this is; each entry then lists in "free_faces"
    the cell's faces toward the free side (validation.free_faces), written to
    geometry/<prefix>swept_free_<MAT_ID>_<n>.brep: the cell model has nothing beyond them, so it cannot see them. Of
    those, the ones against a body with a skin of its own (validation.skinned_faces) are also in "skinned_faces",
    written to geometry/<prefix>swept_skinned_<MAT_ID>_<n>.brep: an end there is not graded."""
    entries, seen = [], set()
    picks = [pick for item in objects.recombine_items(study) for pick in objects.face_picks(item)]
    recombined = {body.Name for body, faces in picks if not faces}
    for item in objects.swept_bodies(study):
        for body, sub in objects.item_refs(item):
            if sub != "" or body.Name not in ids or body.Name in seen:
                continue
            seen.add(body.Name)
            result = found.get(body.Name)
            if result is None:  # validation refuses these before a job is written
                continue
            mat_id = ids[body.Name]
            size = objects.whole_body_size(study, body)
            skin = next(
                (
                    {"depth": layer.SkinDepth.Value, "per_depth": layer.ElementsPerDepth, "layer": layer.LayerDepth}
                    for layer in objects.skin_layers(study)
                    if any(b.Name == body.Name and s == "" for b, s in objects.item_refs(layer))
                ),
                None,
            )
            solids = []
            for k, sweep in enumerate(result, 1):
                rel = f"geometry/{prefix}sweep_{mat_id}_{k}.brep"
                sweep.face.exportBrep(os.path.join(folder, rel))
                pieces = [
                    {"origin": list(p.origin), "axis": list(p.axis), "angle": p.angle, "advance": p.advance}
                    for p in sweep.pieces
                ]
                solids.append({"profile": rel, "closed": sweep.closed, "pieces": pieces})
            entries.append(
                {
                    "name": objects.region_name(study, body),
                    "mat_id": mat_id,
                    "path_size": item.PathSize.Value or size,
                    "section_size": item.SectionSize.Value or size,
                    "recombine": body.Name in recombined,
                    "skin": skin,
                    "solids": solids,
                }
            )
            if group is not None:
                free = validation.free_faces(study, group, body)
                entries[-1]["free_faces"] = export_subs(folder, body, free, f"{prefix}swept_free_{mat_id}")
                skinned = validation.skinned_faces(study, group, body)
                entries[-1]["skinned_faces"] = export_subs(folder, body, skinned, f"{prefix}swept_skinned_{mat_id}")
    return entries


def swept_names(study, found=None):
    """The Names of the bodies in a Swept Body item: skin_entries leaves them out, the swept entry holds their skin.
    With found (recognised_sweeps), only those that get a swept entry: a body that is no sweep keeps its Skin Layer."""
    names = {body.Name for item in objects.swept_bodies(study) for body, sub in objects.item_refs(item) if sub == ""}
    return names if found is None else names & set(found)


def skin_entries(study, ids, quads=True, folder=None, prefix="", group=None):
    """The job's "skin" list: one entry per Skin Layer with a whole-body reference in ids ({body or air Name:
    [MAT_ID, ...]}, the map refine_entries takes), in tree order. Quad layers only when quads.
    group: the Symmetric Group whose cell job this is; the faces of its cell objects toward the free side
    (validation.free_faces) are written to geometry/<prefix>skin_<item>_<body>_<n>.brep and listed in "faces" with
    the MAT_ID of their body."""
    entries = []
    swept = swept_names(study, recognised_sweeps(study, ids))
    for k, item in enumerate(objects.skin_layers(study), 1):
        mat_ids = [
            mat_id
            for body, sub in objects.item_refs(item)
            if sub == "" and not objects.is_air(body) and body.Name in ids and body.Name not in swept
            for mat_id in ids[body.Name]
        ]
        mat_ids = list(dict.fromkeys(mat_ids))  # a body picked twice is one skin
        if mat_ids:
            entries.append(
                {
                    "name": item.Label,
                    "mat_ids": mat_ids,
                    "depth": item.SkinDepth.Value,
                    "per_depth": item.ElementsPerDepth,
                    "layer": item.LayerDepth,
                    "quads": bool(item.QuadLayers and quads),
                }
            )
            if group is not None:
                bodies = {body.Name: body for body, sub in objects.item_refs(item) if sub == "" and body.Name in ids}
                faces = []
                for j, body in enumerate(bodies.values(), 1):
                    free = validation.free_faces(study, group, body)
                    files = export_subs(folder, body, free, f"{prefix}skin_{k}_{j}")
                    faces += [{"mat_id": ids[body.Name][0], "file": f} for f in files]
                if faces:
                    entries[-1]["faces"] = faces
    return entries


def write_slides(study, folder, job):
    """Add the slide keys to job and write their BREPs: the moving cells, each interface's surface and slide marker."""
    plane = airshapes.study_plane(study)
    air = airshapes.air_shape(objects.air_regions(study)[0], plane)
    interfaces = objects.sliding_interfaces(study)
    surfaces = [airshapes.slide_surface(i, air, plane) for i in interfaces]
    cells = airshapes.cells(air, surfaces)
    job["rotor_file"] = rotor_file(study)
    job["moving_cells"] = []
    for k in sides.moving_pieces(study):
        rel = f"geometry/cell_{k + 1}.brep"
        cells[k].exportBrep(os.path.join(folder, rel))
        job["moving_cells"].append(rel)
    job["slides"] = []
    for iface, surface in zip(interfaces, surfaces):
        slide_id = int(study.MatIds[iface.Name])
        pieces = surface.Faces if plane == "3D" else surface.Edges
        files = []
        for n, piece in enumerate(pieces, 1):
            files.append(f"geometry/slide_{slide_id}_{n}.brep")
            piece.exportBrep(os.path.join(folder, files[-1]))
        marker = f"geometry/marker_{slide_id}.brep"
        airshapes.slide_marker(iface, surface, plane).exportBrep(os.path.join(folder, marker))
        slide = {
            "name": objects.volume_name(iface),
            "kind": SLIDE_KINDS[iface.Kind],
            "files": files,
            "marker": marker,
            "divisions": iface.Divisions,
        }
        if plane == "3D":
            slide["cross_divisions"] = iface.CrossDivisions
        slide["slide_mat_id"] = slide_id
        slide["full"] = airshapes.full_turn(iface, air, plane)
        job["slides"].append(slide)
    period = airshapes.period(study)
    if period:
        job["periodic"] = period


def _distinct_faces(body, faces):
    """faces (names like Face3) of body without a second pick of the same wall: the two coincident copies of an
    internal face give one surface, else the second would land on nothing."""
    shape = meshed_shape(body)
    tol = 1e-6 * max(1.0, shape.BoundBox.DiagonalLength)
    kept = []
    for name in faces:
        face = shape.getElement(name)
        if not any(objects.coincident_faces(face, shape.getElement(k), tol) for k in kept):
            kept.append(name)
    return kept


def _body_job(study, folder, volumes, surfaces, elements, ids, prefix="", group=None):
    """The part of a job that meshes bodies, as mesher.build / mesher2d.build read it: their volumes (bodies in 2D),
    excitation surfaces (3D), sizes, transfinite and recombine settings. volumes, surfaces and elements are what check
    returns, restricted to these bodies; ids: {body name: its MAT_ID in this job}. prefix starts the names of the BREP
    files, so two jobs of one Study do not write over each other. group: the Symmetric Group whose cell job this is
    (swept_entries)."""
    two_d = study.Dimension == "2D"
    job = {"bodies": []} if two_d else {"volumes": [], "surfaces": []}
    job["sizes"] = []
    found = recognised_sweeps(study, ids)
    for body, size in volumes:
        mat_id = ids[body.Name]
        rel = f"geometry/{prefix}vol_{mat_id}.brep"
        shape = global_shape(body)
        if body.Name in found:  # a sweep whose seam twists gets its rebuild (sweeps.rebuilt)
            original, shape = shape, sweeps.rebuilt_shape(shape, found[body.Name])
            if shape is not original:  # its faces and edges are exported from the rebuild (export_subs)
                _rebuilt[body.Name] = shape
        shape.exportBrep(os.path.join(folder, rel))
        job["bodies" if two_d else "volumes"].append(
            {"mat_id": mat_id, "name": objects.region_name(study, body), "file": rel, "size": size}
        )
    for exc, body, faces in surfaces:
        smat_id = int(study.SmatIds[f"{exc.Name}|{body.Name}"])
        job["surfaces"].append(
            {
                "smat_id": smat_id,
                "name": objects.item_name(exc, body),
                "mat_id": ids[body.Name],
                "files": export_subs(folder, body, faces, f"{prefix}surf_{smat_id}"),
            }
        )
    for k, (item, body, subs) in enumerate(elements, 1):
        files = export_subs(folder, body, subs, f"{prefix}size_{k}")
        job["sizes"].append({"name": item.Label, "size": item.Size.Value, "files": files})
    structured, tf_edges = transfinite_items(study, [b for b, _ in volumes])
    if structured or tf_edges:
        tf_bodies = []
        for k, (_, body, faces, corners) in enumerate(structured, 1):
            files = export_subs(folder, body, corners, f"{prefix}corner_{k}")
            entry = {"name": objects.region_name(study, body), "mat_id": ids[body.Name], "corner_files": files}
            if faces:  # a pick of faces; a whole body has no "faces" key
                paths = export_subs(folder, body, faces, f"{prefix}tface_{k}")
                entry["faces"] = [{"face": f, "file": p} for f, p in zip(faces, paths)]
            tf_bodies.append(entry)
        job["transfinite"] = {
            "bodies": tf_bodies,
            "edges": [
                {
                    "name": item.Label,
                    "nodes": item.Elements + 1,
                    "distribution": item.Distribution,
                    "coef": item.BumpCoefficient if item.Distribution == "Bump" else 1.0,  # Uniform ignores it
                    "files": export_subs(folder, body, subs, f"{prefix}tedge_{k}"),
                }
                for k, (item, body, subs) in enumerate(tf_edges, 1)
            ],
        }
    picks = [pick for item in objects.recombine_items(study) for pick in objects.face_picks(item)]
    recombine_names = {body.Name for body, faces in picks if not faces}
    recombine = [ids[b.Name] for b, _ in volumes if b.Name in recombine_names]
    if recombine:
        job["recombine"] = recombine
    included = {b.Name for b, _ in volumes}
    picked = {}  # (body name, face) -> body; the same face in two items is written once
    for body, faces in picks:
        if body.Name in included and body.Name not in recombine_names:
            picked.update({(body.Name, f): body for f in faces})
    if picked:
        job["recombine_faces"] = []
        for k, ((_, face), body) in enumerate(picked.items(), 1):
            (rel,) = export_subs(folder, body, [face], f"{prefix}rface_{k}")
            job["recombine_faces"].append(
                {"name": objects.region_name(study, body), "mat_id": ids[body.Name], "face": face, "file": rel}
            )
    swept = swept_entries(study, folder, ids, found, prefix, group)
    if swept:
        job["swept"] = swept
    return job


def _slide_block(study, groups):
    """The job["symmetric"]["slide"] block, or None without a Sliding Interface. In 3D it has the z extent of the
    drawings of the groups that reach the interface, both sides together."""
    for iface in objects.sliding_interfaces(study):  # validation refuses a second one and any but Rotational
        slide = {
            "name": objects.volume_name(iface),
            "kind": "rotational",
            "radius": iface.Radius.Value,
            "divisions": iface.Divisions,
        }
        if study.Dimension == "3D":
            slide["cross_divisions"] = iface.CrossDivisions
        slide.update(slide_mat_id=int(study.MatIds[iface.Name]), full=True)
        if study.Dimension == "3D":
            boxes = [g.Shape.BoundBox for g in groups if validation._reach(g, slide["radius"], True)]
            if boxes:
                slide["z_range"] = [round(min(b.ZMin for b in boxes), 6), round(max(b.ZMax for b in boxes), 6)]
        return slide
    return None


def _group_entry(study, folder, item, number, volumes, surfaces, elements):
    """The job of one Symmetric Group: a mini-job of its cell objects (local ids 1..n), the transforms of its copies, its
    parts with their final MAT_IDs and, per row, the part of every copy."""
    prefix = f"g{number}_"
    ids = {cell.Name: n for n, cell in enumerate(item.Cells, 1)}
    size = {b.Name: s for b, s in volumes}
    cell_job = _body_job(
        study,
        folder,
        [(cell, size[cell.Name]) for cell in item.Cells],
        [],
        [e for e in elements if e[1].Name in ids],
        ids,
        prefix,
        item,
    )
    refine = refine_entries(study, folder, {name: [n] for name, n in ids.items()}, prefix, item)
    if refine:
        cell_job["refine"] = refine
    skin = skin_entries(study, {name: [n] for name, n in ids.items()}, folder=folder, prefix=prefix, group=item)
    if skin:
        cell_job["skin"] = skin
    assignments = {m.PartKey: m for m in objects.part_assignments(study)}
    rows, parts, index, written = objects.rows_of(item), [], {}, []
    for k, row in enumerate(rows, 1):
        picks = []
        for key in objects.row_parts(item, row):
            if key not in index:
                index[key] = len(parts)
                m = assignments[key]
                parts.append({"mat_id": int(study.MatIds[m.Name]), "name": objects.volume_name(m)})
            picks.append(index[key])
        file = None
        if sum(r["cell"] == row["cell"] for r in rows) > 1:  # the mesher tells the rows of a cell by their solids
            file = f"geometry/{prefix}row_{k}.brep"
            objects.row_shape(item, row).exportBrep(os.path.join(folder, file))
        written.append({"cell": ids[row["cell"]], "file": file, "parts": picks})
    entry = {
        "name": objects.volume_name(item),
        "side": sides.group_side(study, item),
        "job": cell_job,
        "cells": list(ids.values()),
        "transforms": objects.group_transforms(item),
        "parts": parts,
        "rows": written,
    }
    if study.Dimension == "3D":  # each Excitation's faces on this drawing, one file per face
        entry["excitations"] = []
        for exc, body, faces in surfaces:
            if body.Name == item.Name:
                smat_id = int(study.SmatIds[f"{exc.Name}|{body.Name}"])
                files = export_subs(folder, body, _distinct_faces(body, faces), f"{prefix}exc_{smat_id}")
                entry["excitations"].append({"smat_id": smat_id, "name": objects.item_name(exc, body), "files": files})
    return entry


def write_groups(study, folder, checked=None):
    """The job["symmetric"] block of a Study with Symmetric Groups: per group a mini-job of its cell objects with the
    transforms of its copies, its parts and rows; per side the job of the free objects; the slide when sliding. checked
    is what check returns; without it the Study is checked and its IDs are updated here."""
    if checked is None:
        checked = check(study)
        objects.update_ids(study)
        os.makedirs(os.path.join(folder, "geometry"), exist_ok=True)
    volumes, surfaces, elements = checked
    groups = objects.symmetric_groups(study)
    block = {
        "groups": [_group_entry(study, folder, g, n, volumes, surfaces, elements) for n, g in enumerate(groups, 1)]
    }
    on_moving = sides.moving(study)
    cells = {b.Name for b in objects.cell_bodies(study)}  # volumes holds the free bodies, then the cell objects
    airs = objects.air_regions(study)  # validation allows one; with groups it is all on the fixed side
    free_jobs = []
    for side in ("fixed", "moving"):
        mine = {b.Name for b, _ in volumes if b.Name not in cells and (b.Name in on_moving) == (side == "moving")}
        with_air = airs if side == "fixed" else []
        if mine or with_air:
            named = mine | {a.Name for a in with_air}
            job = _body_job(
                study,
                folder,
                [(b, size) for b, size in volumes if b.Name in mine],
                [s for s in surfaces if s[1].Name in mine],
                [e for e in elements if e[1].Name in named],
                {name: int(study.MatIds[name]) for name in mine},
                f"free_{side}_",
            )
            refine_ids = {name: [int(study.MatIds[name])] for name in mine}
            for air in with_air:
                rel = "geometry/air.brep"
                meshed_shape(air).exportBrep(os.path.join(folder, rel))
                job["air"] = {
                    "name": objects.key_name(study, air.Name),
                    "mat_id": int(study.MatIds[air.Name]),
                    "file": rel,
                    "size": air_size(study),
                }
                refine_ids[air.Name] = [job["air"]["mat_id"]]
            refine = refine_entries(study, folder, refine_ids, f"free_{side}_")
            if refine:
                job["refine"] = refine
            grading = air_grading_entries(study, refine_ids)
            if grading:
                job["air_grading"] = grading
            skin = skin_entries(study, refine_ids, quads=False)
            if skin:
                job["skin"] = skin
            free_jobs.append({"side": side, "job": job})
    if free_jobs:
        block["free"] = free_jobs
    slide = _slide_block(study, groups)
    if slide:
        block["slide"] = slide
    return block


def write_job(study):
    """Run the checks, update the ID table, write job.json and BREPs to the scratch folder. Returns the job path."""
    validation.refresh_padding(study)  # Padding mode air as the bodies are now
    stale = [a for a in objects.air_regions(study) if "Touched" in a.State or a.Shape.isNull()]
    if stale:  # validation checks the sub-elements of Mesh Sizes on the air's Shape: make it current
        study.Document.recompute(stale)
    _rebuilt.clear()
    sweeps.memo = {}  # the checks' recognitions and rebuilds, for the job
    try:
        return _write_job(study)
    finally:
        _rebuilt.clear()
        sweeps.memo = None


def _write_job(study):
    """write_job after the reset of _rebuilt and sweeps.memo."""
    checked = check(study)
    volumes, surfaces, elements = checked
    folder = scratch_folder(study)  # raises for an unsaved document, before the IDs change
    objects.update_ids(study)
    os.makedirs(os.path.join(folder, "geometry"), exist_ok=True)
    job = {
        "model_name": objects.clean(study.Label),
        "mesh_file": mesh_file(study),
        "options": mesh_options(study.MeshSizesGroup, study.Dimension),
    }
    if study.Dimension == "2D":
        job["dimension"] = "2D"
    sliding = study.Movement == "Sliding motion"
    if objects.is_grouped(study):  # the cells are meshed in the groups' jobs, the free objects in theirs
        job["symmetric"] = write_groups(study, folder, checked)
        if sliding:
            job["rotor_file"] = rotor_file(study)
    else:
        ids = {body.Name: int(study.MatIds[body.Name]) for body, _ in volumes}
        job.update(_body_job(study, folder, volumes, surfaces, elements, ids))
        refine_ids = {name: [mat_id] for name, mat_id in ids.items()}
        for air in objects.air_regions(study):  # validation allows one
            rel = "geometry/air.brep"
            meshed_shape(air).exportBrep(os.path.join(folder, rel))
            if sliding:  # the two sides get their own IDs and names
                halves = {
                    half: {
                        "mat_id": int(study.MatIds[f"{air.Name}#{half}"]),
                        "name": objects.key_name(study, f"{air.Name}#{half}"),
                    }
                    for half in ("fixed", "moving")
                }
                job["air"] = {"sides": halves, "file": rel, "size": air_size(study)}
                refine_ids[air.Name] = [half["mat_id"] for half in halves.values()]
            else:
                job["air"] = {
                    "name": objects.key_name(study, air.Name),
                    "mat_id": int(study.MatIds[air.Name]),
                    "file": rel,
                    "size": air_size(study),
                }
                refine_ids[air.Name] = [job["air"]["mat_id"]]
        refine = refine_entries(study, folder, refine_ids)
        if refine:
            job["refine"] = refine
        grading = air_grading_entries(study, refine_ids)
        if grading:
            job["air_grading"] = grading
        skin = skin_entries(study, refine_ids)
        if skin:
            job["skin"] = skin
        if sliding:
            moving = sides.moving(study)
            job["moving"] = [int(study.MatIds[b.Name]) for b, _ in volumes if b.Name in moving]
            write_slides(study, folder, job)
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2)
    return path
