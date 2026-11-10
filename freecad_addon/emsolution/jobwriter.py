"""Study -> checks -> job.json + BREP files for mesher.py / mesher2d.py."""

import json
import os

from . import airshapes, geometry, objects, symmetry, validation
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
    volumes  = [(body, size_mm)] in main geometry order, then the moving geometry's
    surfaces = [(excitation, body, [face names])] in tree order
    elements = [(mesh size, body, [face, edge and vertex names])] in tree order
    """
    found = validation.errors(validation.validate(study))
    if found:
        raise StudyError("\n".join(p.text for p in found))
    main, moving, _ = geometry.setup(study)
    surface_on = None  # the names excitations sit on, when not the meshed bodies themselves
    if objects.is_grouped(study):  # the free objects, then the cell objects of the groups
        free = validation.free_bodies(study, main, moving)
        bodies = free + objects.cell_bodies(study)
        surface_on = {b.Name for b in free} | {g.Name for g in objects.symmetric_groups(study)}
    elif objects.is_symmetric(study):
        bodies = objects.cell_bodies(study)  # only the cells are meshed
    else:
        bodies = list({b.Name: b for b in main + moving}.values())  # main geometry order, then moving
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


def export_subs(folder, body, subs, prefix):
    """Write each sub-element of body to geometry/<prefix>_<n>.brep. Returns the relative paths."""
    shape = meshed_shape(body)
    files = []
    for n, sub in enumerate(subs, 1):
        rel = f"geometry/{prefix}_{n}.brep"
        shape.getElement(sub).exportBrep(os.path.join(folder, rel))
        files.append(rel)
    return files


def write_slides(study, folder, job):
    """Add the slide keys to job and write their BREPs: the moving cells, each interface's surface and slide marker."""
    plane = airshapes.study_plane(study)
    air = airshapes.air_shape(objects.air_regions(study)[0], plane)
    interfaces = objects.sliding_interfaces(study)
    surfaces = [airshapes.slide_surface(i, air, plane) for i in interfaces]
    cells = airshapes.cells(air, surfaces)
    moving = {airshapes.cell_of(global_shape(b), cells) for b in geometry.setup(study)[1]}
    job["rotor_file"] = rotor_file(study)
    job["moving_cells"] = []
    for k in sorted(moving):
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


def write_symmetric(study, folder, ids):
    """The job["symmetric"] block: per side the cells (local ids), copy transforms and pieces; the slide if sliding."""
    main, moving, _ = geometry.setup(study)
    sliding = study.Movement == "Sliding motion"
    items = objects.symmetric_items(study)
    assignments = objects.piece_assignments(study)
    sides, count = [], 0
    for side, bodies in (("fixed", main), ("moving", moving if sliding else [])):
        names = {b.Name for b in bodies}
        for item in items:
            if item.Top.Name not in names:
                continue
            cells, transforms = symmetry.read_chain(item.Top)
            pieces = []
            for m in assignments:
                for body, subs in m.Pieces:
                    if body.Name != item.Top.Name:
                        continue
                    for sub in subs:
                        count += 1
                        rel = f"geometry/piece_{count}.brep"
                        global_shape(body).getElement(sub).exportBrep(os.path.join(folder, rel))
                        pieces.append(
                            {"mat_id": int(study.MatIds[m.Name]), "name": objects.volume_name(m), "file": rel}
                        )
            entry = {"side": side, "cells": [ids[c.Name] for c in cells], "transforms": transforms, "pieces": pieces}
            if study.Dimension == "3D":  # each Excitation's faces on this top, one file per face
                entry["excitations"] = []
                for e in objects.excitations(study):
                    for body, faces in objects.subs_by_body(e):
                        if body.Name == item.Top.Name and faces:
                            smat_id = int(study.SmatIds[f"{e.Name}|{body.Name}"])
                            files = export_subs(folder, body, _distinct_faces(body, faces), f"exc_{smat_id}")
                            name = objects.item_name(e, body)
                            entry["excitations"].append({"smat_id": smat_id, "name": name, "files": files})
            sides.append(entry)
    block = {"sides": sides}
    for iface in objects.sliding_interfaces(study):  # validation refuses a second one and any but Rotational
        block["slide"] = {
            "name": objects.volume_name(iface),
            "kind": "rotational",
            "radius": iface.Radius.Value,
            "divisions": iface.Divisions,
        }
        if study.Dimension == "3D":
            block["slide"]["cross_divisions"] = iface.CrossDivisions
        block["slide"].update(slide_mat_id=int(study.MatIds[iface.Name]), full=True)
    return block


def _body_job(study, folder, volumes, surfaces, elements, ids, prefix=""):
    """The part of a job that meshes bodies, as mesher.build / mesher2d.build read it: their volumes (bodies in 2D),
    excitation surfaces (3D), sizes, transfinite and recombine settings. volumes, surfaces and elements are what check
    returns, restricted to these bodies; ids: {body name: its MAT_ID in this job}. prefix starts the names of the BREP
    files, so two jobs of one Study do not write over each other."""
    two_d = study.Dimension == "2D"
    job = {"bodies": []} if two_d else {"volumes": [], "surfaces": []}
    job["sizes"] = []
    for body, size in volumes:
        mat_id = ids[body.Name]
        rel = f"geometry/{prefix}vol_{mat_id}.brep"
        global_shape(body).exportBrep(os.path.join(folder, rel))
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
    )
    assignments = {m.PartKey: m for m in objects.part_assignments(study)}
    rows, parts, index, written = objects.rows_of(item), [], {}, []
    for k, row in enumerate(rows, 1):
        picks = []
        for name in objects.row_parts(item, row):
            key = objects.part_key(study, item, name)
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
        "side": objects.part_key(study, item, "").partition("|")[0],
        "job": cell_job,
        "cells": list(ids.values()),
        "transforms": objects.group_transforms(item),
        "parts": parts,
        "rows": written,
    }
    if study.Movement == "Sliding motion":
        entry["turns"] = symmetry.turns_about_z(objects.rules_of(item))
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
    sliding = study.Movement == "Sliding motion"
    groups = objects.symmetric_groups(study)
    block = {
        "groups": [_group_entry(study, folder, g, n, volumes, surfaces, elements) for n, g in enumerate(groups, 1)]
    }
    main, moving, _ = geometry.setup(study)
    on_moving = {b.Name for b in moving} if sliding else set()
    free = {b.Name for b in validation.free_bodies(study, main, moving)}
    sides = []
    for side in ("fixed", "moving"):
        mine = {b.Name for b, _ in volumes if b.Name in free and (b.Name in on_moving) == (side == "moving")}
        if mine:
            job = _body_job(
                study,
                folder,
                [(b, size) for b, size in volumes if b.Name in mine],
                [s for s in surfaces if s[1].Name in mine],
                [e for e in elements if e[1].Name in mine],
                {name: int(study.MatIds[name]) for name in mine},
                f"free_{side}_",
            )
            sides.append({"side": side, "job": job})
    if sides:
        block["free"] = sides
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
        symmetric = objects.is_symmetric(study)
        if symmetric:  # the cells get local ids 1..n; the pieces carry the MAT_IDs
            ids = {body.Name: n for n, (body, _) in enumerate(volumes, 1)}
        else:
            ids = {body.Name: int(study.MatIds[body.Name]) for body, _ in volumes}
        job.update(_body_job(study, folder, volumes, surfaces, elements, ids))
        for air in [] if symmetric else objects.air_regions(study):  # validation allows one
            rel = "geometry/air.brep"
            meshed_shape(air).exportBrep(os.path.join(folder, rel))
            if sliding:  # the two sides get their own IDs and names
                sides = {
                    half: {
                        "mat_id": int(study.MatIds[f"{air.Name}#{half}"]),
                        "name": objects.key_name(study, f"{air.Name}#{half}"),
                    }
                    for half in ("fixed", "moving")
                }
                job["air"] = {"sides": sides, "file": rel, "size": air_size(study)}
            else:
                job["air"] = {
                    "name": objects.key_name(study, air.Name),
                    "mat_id": int(study.MatIds[air.Name]),
                    "file": rel,
                    "size": air_size(study),
                }
        if symmetric:
            job["symmetric"] = write_symmetric(study, folder, ids)
            if sliding:
                job["rotor_file"] = rotor_file(study)
        elif sliding:
            job["moving"] = [int(study.MatIds[b.Name]) for b in geometry.setup(study)[1]]
            write_slides(study, folder, job)
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2)
    return path
