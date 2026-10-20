"""Study -> checks -> job.json + BREP files for mesher.py / mesher2d.py."""

import json
import os

from . import geometry, objects, validation
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


def check(study):
    """Refuse the Study if validation finds an error. Returns (volumes, surfaces, elements):
    volumes  = [(body, size_mm)] in main geometry order
    surfaces = [(excitation, body, [face names])] in tree order
    elements = [(mesh size, body, [face, edge and vertex names])] in tree order
    """
    found = validation.errors(validation.validate(study))
    if found:
        raise StudyError("\n".join(p.text for p in found))
    bodies, _, _ = geometry.setup(study)
    bodies = list({b.Name: b for b in bodies}.values())  # main geometry order
    included = {b.Name for b in bodies}
    excitation_items = objects.excitations(study) if study.Dimension == "3D" else []  # 2D: none yet
    surfaces = [(e, b, faces) for e in excitation_items for b, faces in objects.subs_by_body(e) if b.Name in included]
    sized = [
        (s, b, subs) for s in objects.mesh_sizes(study) for b, subs in objects.subs_by_body(s) if b.Name in included
    ]
    elements = [(s, b, [n for n in subs if n]) for s, b, subs in sized]
    elements = [el for el in elements if el[2]]
    size = {}
    for s, b, subs in sized:
        if "" in subs:  # the whole body
            size[b.Name] = min(size.get(b.Name, s.Size.Value), s.Size.Value)
    default = study.MeshSizesGroup.DefaultMeshSize.Value
    volumes = [(b, size.get(b.Name, default)) for b in bodies]
    return volumes, surfaces, elements


def transfinite_items(study, bodies):
    """The Study's transfinite items on bodies, after check(). Returns (structured, edges):
    structured = [(body, [corner vertex names])] in tree order
    edges      = [(item, body, [edge names])] in tree order
    """
    included = {b.Name for b in bodies}
    structured = []
    for t in objects.transfinite_bodies(study):
        corners = {}
        for b, subs in t.Corners:
            corners.setdefault(b.Name, []).extend(subs)
        for b, _ in objects.subs_by_body(t):
            if b.Name in included:
                structured.append((b, corners.get(b.Name, [])))
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
    two_d = study.Dimension == "2D"
    job = {
        "model_name": objects.clean(study.Label),
        "msh_version": float(study.MshVersion),
        "mesh_file": mesh_file(study),
        "options": mesh_options(study.MeshSizesGroup, study.Dimension),
    }
    if two_d:
        job["dimension"] = "2D"
        job["bodies"] = []
    else:
        job["volumes"] = []
        job["surfaces"] = []
    job["sizes"] = []
    for body, size in volumes:
        mat_id = int(study.MatIds[body.Name])
        rel = f"geometry/vol_{mat_id}.brep"
        global_shape(body).exportBrep(os.path.join(folder, rel))
        job["bodies" if two_d else "volumes"].append(
            {"mat_id": mat_id, "name": objects.volume_name(body), "file": rel, "size": size}
        )
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
    structured, tf_edges = transfinite_items(study, [b for b, _ in volumes])
    if structured or tf_edges:
        tf_bodies = []
        for body, corners in structured:
            mat_id = int(study.MatIds[body.Name])
            files = export_subs(folder, body, corners, f"corner_{mat_id}")
            tf_bodies.append({"name": objects.volume_name(body), "mat_id": mat_id, "corner_files": files})
        job["transfinite"] = {
            "bodies": tf_bodies,
            "edges": [
                {
                    "name": item.Label,
                    "nodes": item.Elements + 1,
                    "distribution": item.Distribution,
                    "coef": item.BumpCoefficient if item.Distribution == "Bump" else 1.0,  # Uniform ignores it
                    "files": export_subs(folder, body, subs, f"tedge_{k}"),
                }
                for k, (item, body, subs) in enumerate(tf_edges, 1)
            ],
        }
    recombine_names = {body.Name for item in objects.recombine_items(study) for body, _ in objects.subs_by_body(item)}
    recombine = [int(study.MatIds[b.Name]) for b, _ in volumes if b.Name in recombine_names]
    if recombine:
        job["recombine"] = recombine
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2)
    return path
