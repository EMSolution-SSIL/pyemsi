"""What mesher.py (3D) and mesher2d.py (2D) share. Runs in their process. Never import FreeCAD here."""

import json
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


def run(job_path, build, dim):
    """Read the job, call build(job, folder) on a fresh model, mesh to dimension dim, write mesh.unv and
    replace job["mesh_file"] with the finished .msh. Returns the job."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    msh = os.path.join(folder, "mesh.msh")
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        build(job, folder)
        for name, value in job.get("options", {}).items():  # the user's mesh settings
            gmsh.option.setNumber(name, value)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)  # set last: the settings may not change it
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.model.mesh.generate(dim)
        gmsh.option.setNumber("Mesh.MshFileVersion", float(job["msh_version"]))
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.write(msh)
        gmsh.write(os.path.join(folder, "mesh.unv"))
    finally:
        gmsh.finalize()
    try:
        os.replace(msh, job["mesh_file"])  # only a finished mesh replaces the solver's file
    except PermissionError:
        raise JobError(f"Could not replace {job['mesh_file']}: it is read-only or open in another program.") from None
    return job


def main(argv, script, run_job):
    for stream in (sys.stdout, sys.stderr):  # the runner reads UTF-8, whatever the console code page
        stream.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) != 2:
        print(f"ERROR: usage: {script} <job.json>", file=sys.stderr)
        return 1
    try:
        run_job(argv[1])
    except Exception as exc:  # anything -> one clean ERROR line for the runner
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0
