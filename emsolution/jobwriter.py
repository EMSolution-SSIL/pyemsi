"""Study -> checks -> job.json + BREP files for mesher.py."""
import json
import os

import FreeCAD as App

from . import objects


class StudyError(Exception):
    pass


def global_shape(obj):
    """Shape in global coordinates, including App::Part placement (same as FEM's gmshtools)."""
    shape = obj.getPropertyOfGeometry().transformed(App.Placement().Matrix)
    shape.Placement = obj.getGlobalPlacement()
    return shape


def output_folder(study):
    if study.OutputFolder:
        return study.OutputFolder
    if not study.Document.FileName:
        raise StudyError("Save the document first, or set the study's OutputFolder.")
    return os.path.splitext(study.Document.FileName)[0] + "_mesh"


def check(study):
    """Checks before meshing. Returns (volumes, surfaces):
    volumes  = [(body, material, size_mm)] in tree order
    surfaces = [(excitation, body, [face names])] in tree order
    """
    mats = objects.materials(study)
    if not mats:
        raise StudyError("The study has no materials.")
    material_of = {}
    for m in mats:
        for b in m.References:
            material_of.setdefault(b.Name, (b, []))[1].append(m)
    surfaces = [(e, b, faces) for e in objects.excitations(study)
                for b, faces in objects.faces_by_body(e)]
    for e, b, _ in surfaces:
        if b.Name not in material_of:
            raise StudyError(f"Excitation {e.Label} is on body {b.Label}, which has no material.")
    for s in objects.mesh_sizes(study):
        for b in s.References:
            if b.Name not in material_of:
                raise StudyError(f"Body {b.Label} has a mesh size but no material.")
    for b, ms in material_of.values():
        if not b.isDerivedFrom("Part::Feature"):
            raise StudyError(f"{b.Label} is not a solid body "
                             "(links and containers are not supported).")
        if len(ms) > 1:
            raise StudyError(f"Body {b.Label} has more than one material: "
                             + ", ".join(m.Label for m in ms))
        if len(b.Shape.Solids) != 1:
            raise StudyError(f"Body {b.Label} must be exactly one solid "
                             f"(it has {len(b.Shape.Solids)}).")
    for e, b, faces in surfaces:
        for face in faces:
            try:
                b.Shape.getElement(face)
            except Exception:
                raise StudyError(f"Excitation {e.Label}: body {b.Label} has no {face}. "
                                 "Reselect the faces.") from None
    if study.DefaultMeshSize.Value <= 0:
        raise StudyError("The default mesh size must be greater than 0.")
    size = {}
    for s in objects.mesh_sizes(study):
        if s.Size.Value <= 0:
            raise StudyError(f"Mesh size {s.Label} must be greater than 0.")
        for b in s.References:
            size[b.Name] = min(size.get(b.Name, s.Size.Value), s.Size.Value)
    volumes = [(b, ms[0], size.get(b.Name, study.DefaultMeshSize.Value))
               for b, ms in material_of.values()]
    names = [objects.item_name(m, b) for b, m, _ in volumes]
    names += [objects.item_name(e, b) for e, b, _ in surfaces]
    dups = sorted({n for n in names if names.count(n) > 1})
    if dups:
        raise StudyError("These group names are the same after removing special characters: "
                         + ", ".join(dups) + ". Rename the items or bodies.")
    return volumes, surfaces


def write_job(study):
    """Run the checks, update the ID table, write job.json and BREPs. Returns the job path."""
    volumes, surfaces = check(study)
    folder = output_folder(study)
    objects.update_ids(study)
    os.makedirs(os.path.join(folder, "geometry"), exist_ok=True)
    job = {"model_name": objects.clean(study.Label), "msh_version": float(study.MshVersion),
           "volumes": [], "surfaces": []}
    for body, mat, size in volumes:
        vid = int(study.VolumeIds[body.Name])
        rel = f"geometry/vol_{vid}.brep"
        global_shape(body).exportBrep(os.path.join(folder, rel))
        job["volumes"].append({"id": vid, "name": objects.item_name(mat, body),
                               "file": rel, "size": size})
    for exc, body, faces in surfaces:
        sid = int(study.SurfaceIds[f"{exc.Name}|{body.Name}"])
        shape = global_shape(body)
        files = []
        for n, face in enumerate(faces, 1):
            rel = f"geometry/surf_{sid}_{n}.brep"
            shape.getElement(face).exportBrep(os.path.join(folder, rel))
            files.append(rel)
        job["surfaces"].append({"id": sid, "name": objects.item_name(exc, body),
                                "volume_id": int(study.VolumeIds[body.Name]), "files": files})
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2)
    return path
