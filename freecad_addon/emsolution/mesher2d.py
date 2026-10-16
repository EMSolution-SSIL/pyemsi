"""2D job file -> Gmsh .msh at job["mesh_file"] + mesh.unv beside the job. Runs in its own process.
Never import FreeCAD here.

Usage: python mesher2d.py <job.json>
"""

import os
import sys

import gmsh

from meshcommon import JobError, apply_size_fields, apply_transfinite, main, run, transfinite_files, apply_recombine


def _import(path, *dims):
    """All entities of a BREP file; every one must have a dimension in dims."""
    tags = gmsh.model.occ.importShapes(path, highestDimOnly=True)
    if not tags or any(d not in dims for d, _ in tags):
        raise JobError(f"{os.path.basename(path)}: expected {'/'.join(map(str, dims))}D entities, got {tags}")
    return tags


def _on_bodies(dim, tag, faces):
    """True when the entity is a body face, or lies on one: an edge of a face, a point of such an edge."""
    if dim == 2:
        return tag in faces
    above = gmsh.model.getAdjacencies(dim, tag)[0]
    if dim == 1:
        return any(t in faces for t in above)
    return any(_on_bodies(1, t, faces) for t in above)


def build(job, folder):
    """Import, fragment, check, tag and size the model. Gmsh must be initialized."""
    bodies = job["bodies"]
    if not bodies:
        raise JobError("job has no bodies")
    inputs, body_spans = [], []  # body i owns inputs[start:end]
    for b in bodies:
        start = len(inputs)
        inputs += _import(os.path.join(folder, b["file"]), 2)
        body_spans.append((start, len(inputs)))
    size_files = [(z, os.path.join(folder, f)) for z in job["sizes"] for f in z["files"]]
    size_spans = []
    for _, path in size_files:
        start = len(inputs)
        inputs += _import(path, 0, 1, 2)
        size_spans.append((start, len(inputs)))
    tf_files = transfinite_files(job, folder)
    tf_spans = []
    for kind, _, path in tf_files:
        start = len(inputs)
        inputs += _import(path, 1 if kind == "edge" else 0)
        tf_spans.append((start, len(inputs)))

    if len(inputs) == 1:  # Gmsh skips a fragment with no tools and returns no map
        out_map = [inputs]
    else:
        _, out_map = gmsh.model.occ.fragment(inputs[:1], inputs[1:])
    gmsh.model.occ.synchronize()

    body_faces = {}  # MAT_ID -> list of final 2D tags
    owner = {}  # final 2D tag -> body name
    for b, (start, end) in zip(bodies, body_spans):
        tags = sorted({t for dimtags in out_map[start:end] for d, t in dimtags if d == 2})
        for t in tags:
            if owner.get(t, b["name"]) != b["name"]:
                raise JobError(f"bodies {owner[t]} and {b['name']} overlap")
            owner[t] = b["name"]
        body_faces[b["mat_id"]] = tags

    for b in bodies:
        gmsh.model.addPhysicalGroup(2, body_faces[b["mat_id"]], b["mat_id"], name=b["name"])

    by_size = {}  # size -> {dim: [tags]}
    for b in bodies:
        by_size.setdefault(float(b["size"]), {}).setdefault(2, []).extend(body_faces[b["mat_id"]])
    for (z, path), (start, end) in zip(size_files, size_spans):
        for dimtags in out_map[start:end]:
            for d, t in dimtags:
                if not _on_bodies(d, t, owner):
                    raise JobError(f"mesh size {z['name']}: {os.path.basename(path)} did not merge with the bodies")
                by_size.setdefault(float(z["size"]), {}).setdefault(d, []).append(t)
    apply_size_fields(by_size)
    mapped = [
        (kind, item, os.path.basename(path), [dt for dimtags in out_map[start:end] for dt in dimtags])
        for (kind, item, path), (start, end) in zip(tf_files, tf_spans)
    ]
    tf_curves = apply_transfinite(job, mapped, body_faces, 2)
    apply_recombine(job, body_faces, 2, tf_curves)


def run_job(job_path):
    job = run(job_path, build, 2)
    for item in job["bodies"]:
        print(f"MAT_ID  {item['mat_id']:>6}  {item['name']}")
    for item in (job.get("transfinite") or {}).get("bodies", []):
        print(f"Structured      {item['name']}")
    for item in job["bodies"]:
        if item["mat_id"] in job.get("recombine", []):
            print(f"Recombined      {item['name']}")
    print(f"Wrote {job['mesh_file']}")


if __name__ == "__main__":
    sys.exit(main(sys.argv, "mesher2d.py", run_job))
