"""Job file -> Gmsh .msh + .unv. Runs in its own process. Never import FreeCAD here.

Usage: python mesher.py <job.json>
"""
import json
import os
import sys

import gmsh


class JobError(Exception):
    pass


FIELD_LISTS = {0: "PointsList", 1: "CurvesList", 2: "SurfacesList", 3: "VolumesList"}


def _import_one(path, *dims):
    tags = gmsh.model.occ.importShapes(path, highestDimOnly=True)
    if len(tags) != 1 or tags[0][0] not in dims:
        raise JobError(f"{os.path.basename(path)}: expected one "
                       f"{'/'.join(map(str, dims))}D entity, got {tags}")
    return tags[0]


def build(job, folder):
    """Import, fragment, check, tag and size the model. Gmsh must be initialized."""
    vols, surfs = job["volumes"], job["surfaces"]
    if not vols:
        raise JobError("job has no volumes")
    inputs = [_import_one(os.path.join(folder, v["file"]), 3) for v in vols]
    surf_files = [(s, os.path.join(folder, f)) for s in surfs for f in s["files"]]
    inputs += [_import_one(path, 2) for _, path in surf_files]
    size_files = [(z, os.path.join(folder, f)) for z in job["sizes"] for f in z["files"]]
    inputs += [_import_one(path, 0, 1, 2) for _, path in size_files]

    if len(inputs) == 1:  # Gmsh skips a fragment with no tools and returns no map
        out_map = [inputs]
    else:
        _, out_map = gmsh.model.occ.fragment(inputs[:1], inputs[1:])
    gmsh.model.occ.synchronize()

    body_vols = {}  # volume id -> list of final 3D tags
    owner = {}      # final 3D tag -> body name
    for v, dimtags in zip(vols, out_map):
        tags = [t for d, t in dimtags if d == 3]
        for t in tags:
            if t in owner:
                raise JobError(f"bodies {owner[t]} and {v['name']} overlap")
            owner[t] = v["name"]
        body_vols[v["id"]] = tags

    surf_tags = {s["id"]: [] for s in surfs}
    for (s, path), dimtags in zip(surf_files, out_map[len(vols):]):
        surf_tags[s["id"]] += [t for d, t in dimtags if d == 2]

    for s in surfs:
        boundary = {abs(t) for _, t in gmsh.model.getBoundary(
            [(3, t) for t in body_vols[s["volume_id"]]], combined=False, oriented=False)}
        if not surf_tags[s["id"]] or not set(surf_tags[s["id"]]) <= boundary:
            raise JobError(f"excitation surface {s['name']} does not lie on its body "
                           f"(face did not merge with the body boundary)")

    for v in vols:
        gmsh.model.addPhysicalGroup(3, body_vols[v["id"]], v["id"], name=v["name"])
    for s in surfs:
        gmsh.model.addPhysicalGroup(2, sorted(set(surf_tags[s["id"]])), s["id"], name=s["name"])

    by_size = {}  # size -> {dim: [tags]}
    for v in vols:
        by_size.setdefault(float(v["size"]), {}).setdefault(3, []).extend(body_vols[v["id"]])
    first = len(vols) + len(surf_files)
    for (z, path), dimtags in zip(size_files, out_map[first:]):
        for d, t in dimtags:
            if len(gmsh.model.getAdjacencies(d, t)[0]) == 0:  # nothing above it: not merged
                raise JobError(f"mesh size {z['name']}: {os.path.basename(path)} "
                               f"did not merge with the bodies")
            by_size.setdefault(float(z["size"]), {}).setdefault(d, []).append(t)
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
    for opt in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints",
                "Mesh.MeshSizeFromCurvature"):
        gmsh.option.setNumber(opt, 0)


def run(job_path):
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        build(job, folder)
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.model.mesh.generate(3)
        gmsh.option.setNumber("Mesh.MshFileVersion", float(job["msh_version"]))
        gmsh.option.setNumber("Mesh.Binary", 0)
        base = os.path.join(folder, job["model_name"])
        gmsh.write(base + ".msh")
        gmsh.write(base + ".unv")
    finally:
        gmsh.finalize()
    for item in job["volumes"] + job["surfaces"]:
        print(f"{item['id']:>6}  {item['name']}")
    print(f"Wrote {base}.msh")


def main(argv):
    for stream in (sys.stdout, sys.stderr):  # the runner reads UTF-8, whatever the console code page
        stream.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) != 2:
        print("ERROR: usage: mesher.py <job.json>", file=sys.stderr)
        return 1
    try:
        run(argv[1])
    except Exception as exc:  # anything -> one clean ERROR line for the runner
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
