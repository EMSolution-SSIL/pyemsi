"""Study -> checks -> job.json + BREP files for mesher.py."""

import json
import os

from . import geometry, objects
from .geometry import global_shape


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


def _check_subs(kind, item, body, subs):
    for sub in subs:
        try:
            body.Shape.getElement(sub)
        except Exception:
            raise StudyError(f"{kind} {item.Label}: body {body.Label} has no {sub}. Reselect it.") from None


def check(study):
    """Checks before meshing. Returns (volumes, surfaces, elements):
    volumes  = [(body, material, size_mm)] in tree order
    surfaces = [(excitation, body, [face names])] in tree order
    elements = [(mesh size, body, [face, edge and vertex names])] in tree order
    """
    unavailable = geometry.export_unavailable(study)
    if unavailable:
        raise StudyError(unavailable)
    bodies, _, errors = geometry.setup(study)
    if errors:
        raise StudyError("\n".join(errors))
    material_of = {b.Name: (b, []) for b in bodies}  # main geometry order
    for m in objects.materials(study):
        for b in m.References:
            if b.Name in material_of:
                material_of[b.Name][1].append(m)
    missing = [b for b, ms in material_of.values() if not ms]
    if missing:
        raise StudyError(
            "Main geometry has bodies with no material: "
            + ", ".join(f"{b.Label} ({b.Name})" for b in missing)
            + ". Assign one material to each body."
        )
    for b, ms in material_of.values():
        if len(ms) > 1:
            raise StudyError(f"Body {b.Label} has more than one material: " + ", ".join(m.Label for m in ms))
    surfaces = [
        (e, b, faces)
        for e in objects.excitations(study)
        for b, faces in objects.subs_by_body(e)
        if b.Name in material_of
    ]
    sized = [
        (s, b, subs) for s in objects.mesh_sizes(study) for b, subs in objects.subs_by_body(s) if b.Name in material_of
    ]
    for e, b, faces in surfaces:
        _check_subs("Excitation", e, b, faces)
    elements = [(s, b, [n for n in subs if n]) for s, b, subs in sized]
    elements = [el for el in elements if el[2]]
    for s, b, subs in elements:
        _check_subs("Mesh size", s, b, subs)
    settings = study.MeshSizesGroup
    if settings.DefaultMeshSize.Value <= 0:
        raise StudyError("The default mesh size must be greater than 0.")
    if 0 < settings.MaxSize.Value < settings.MinSize.Value:
        raise StudyError("The minimum mesh size is larger than the maximum.")
    size_items = dict.fromkeys(s for s, _, _ in sized)
    for s in size_items:
        if s.Size.Value <= 0:
            raise StudyError(f"Mesh size {s.Label} must be greater than 0.")
    size = {}
    for s, b, subs in sized:
        if "" in subs:  # the whole body
            size[b.Name] = min(size.get(b.Name, s.Size.Value), s.Size.Value)
    volumes = [(b, ms[0], size.get(b.Name, settings.DefaultMeshSize.Value)) for b, ms in material_of.values()]
    names = [objects.item_name(m, b) for b, m, _ in volumes]
    names += [objects.item_name(e, b) for e, b, _ in surfaces]
    dups = sorted({n for n in names if names.count(n) > 1})
    if dups:
        raise StudyError(
            "These group names are the same after removing special characters: "
            + ", ".join(dups)
            + ". Rename the items or bodies."
        )
    return volumes, surfaces, elements


def mesh_options(settings):
    """Gmsh options from the Mesh Sizes folder; a min or max size of 0 keeps Gmsh's default."""
    opts = {
        "Mesh.Algorithm": objects.ALGORITHMS_2D[settings.SurfaceAlgorithm],
        "Mesh.Algorithm3D": objects.ALGORITHMS_3D[settings.VolumeAlgorithm],
        "Mesh.MeshSizeFactor": settings.SizeFactor,
        "Mesh.Smoothing": settings.SmoothingSteps,
        "Mesh.OptimizeNetgen": int(settings.OptimizeNetgen),
    }
    if settings.MinSize.Value > 0:
        opts["Mesh.MeshSizeMin"] = settings.MinSize.Value
    if settings.MaxSize.Value > 0:
        opts["Mesh.MeshSizeMax"] = settings.MaxSize.Value
    return opts


def export_subs(folder, body, subs, prefix):
    """Write each sub-element of body to geometry/<prefix>_<n>.brep. Returns the relative paths."""
    shape = global_shape(body)
    files = []
    for n, sub in enumerate(subs, 1):
        rel = f"geometry/{prefix}_{n}.brep"
        shape.getElement(sub).exportBrep(os.path.join(folder, rel))
        files.append(rel)
    return files


def write_job(study):
    """Run the checks, update the ID table, write job.json and BREPs to the scratch folder. Returns the job path."""
    volumes, surfaces, elements = check(study)
    folder = scratch_folder(study)  # raises for an unsaved document, before the IDs change
    objects.update_ids(study)
    os.makedirs(os.path.join(folder, "geometry"), exist_ok=True)
    job = {
        "model_name": objects.clean(study.Label),
        "msh_version": float(study.MshVersion),
        "mesh_file": mesh_file(study),
        "options": mesh_options(study.MeshSizesGroup),
        "volumes": [],
        "surfaces": [],
        "sizes": [],
    }
    for body, mat, size in volumes:
        mat_id = int(study.MatIds[body.Name])
        rel = f"geometry/vol_{mat_id}.brep"
        global_shape(body).exportBrep(os.path.join(folder, rel))
        job["volumes"].append({"mat_id": mat_id, "name": objects.item_name(mat, body), "file": rel, "size": size})
    for exc, body, faces in surfaces:
        smat_id = int(study.SmatIds[f"{exc.Name}|{body.Name}"])
        job["surfaces"].append(
            {
                "smat_id": smat_id,
                "name": objects.item_name(exc, body),
                "mat_id": int(study.MatIds[body.Name]),
                "files": export_subs(folder, body, faces, f"surf_{smat_id}"),
            }
        )
    for k, (item, body, subs) in enumerate(elements, 1):
        job["sizes"].append(
            {"name": item.Label, "size": item.Size.Value, "files": export_subs(folder, body, subs, f"size_{k}")}
        )
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2)
    return path
