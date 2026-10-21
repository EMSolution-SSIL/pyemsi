"""Study -> checks -> job.json + BREP files for mesher.py / mesher2d.py."""

import json
import os

from . import airshapes, geometry, objects, validation
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
    bodies = list({b.Name: b for b in main + moving}.values())  # main geometry order, then moving
    included = {b.Name for b in bodies}
    excitation_items = objects.excitations(study) if study.Dimension == "3D" else []  # 2D: none yet
    surfaces = [(e, b, faces) for e in excitation_items for b, faces in objects.subs_by_body(e) if b.Name in included]
    with_air = validation.meshed(study, bodies)  # the air takes Mesh Sizes like a body
    sized = [
        (s, b, subs) for s in objects.mesh_sizes(study) for b, subs in objects.subs_by_body(s) if b.Name in with_air
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


def write_job(study):
    """Run the checks, update the ID table, write job.json and BREPs to the scratch folder. Returns the job path."""
    stale = [a for a in objects.air_regions(study) if "Touched" in a.State or a.Shape.isNull()]
    if stale:  # validation checks the sub-elements of Mesh Sizes on the air's Shape: make it current
        study.Document.recompute(stale)
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
    sliding = study.Movement == "Sliding motion"
    for air in objects.air_regions(study):  # validation allows one
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
    if sliding:
        job["moving"] = [int(study.MatIds[b.Name]) for b in geometry.setup(study)[1]]
        write_slides(study, folder, job)
    recombine_names = {body.Name for item in objects.recombine_items(study) for body, _ in objects.subs_by_body(item)}
    recombine = [int(study.MatIds[b.Name]) for b, _ in volumes if b.Name in recombine_names]
    if recombine:
        job["recombine"] = recombine
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2)
    return path
