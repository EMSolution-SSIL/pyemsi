"""2D job file -> Gmsh .msh at job["mesh_file"] + mesh.unv beside the job. Runs in its own process.
Sliding motion: the fixed side goes to job["mesh_file"], the moving side to job["rotor_file"].
A job with a "symmetric" key meshes only the cell and copies it (meshsym.py).
Never import FreeCAD here.

Usage: python mesher2d.py <job.json> [--check]   (--check: geometry checks only, nothing written)
"""

import json
import os
import sys

import gmsh

from meshcommon import (
    JobError,
    check,
    apply_size_fields,
    apply_transfinite,
    main,
    run,
    transfinite_files,
    apply_recombine,
    claim_air,
    air_items,
    split_air,
    apply_slides,
    apply_periodic,
    slide_report,
    import_brep,
    slide_split,
)
import meshsym


def _on_bodies(dim, tag, faces):
    """True when the entity is a body face, or lies on one: an edge of a face, a point of such an edge."""
    if dim == 2:
        return tag in faces
    above = gmsh.model.getAdjacencies(dim, tag)[0]
    if dim == 1:
        return any(t in faces for t in above)
    return any(_on_bodies(1, t, faces) for t in above)


def build(job, folder):
    """Import, fragment, check, tag and size the model. Gmsh must be initialized.
    Sliding motion: returns the split of the model into the fixed and the moving side (see meshcommon.run)."""
    bodies = job["bodies"]
    if not bodies:
        raise JobError("job has no bodies")
    inputs, body_spans = [], []  # body i owns inputs[start:end]
    for b in bodies:
        start = len(inputs)
        inputs += import_brep(os.path.join(folder, b["file"]), 2)
        body_spans.append((start, len(inputs)))
    air = job.get("air")
    if air:  # after the bodies, so the fragment keeps the bodies' pieces whole
        air_start = len(inputs)
        inputs += import_brep(os.path.join(folder, air["file"]), 2)
        air_span = (air_start, len(inputs))

    def add(file, *dims):
        start = len(inputs)
        inputs.extend(import_brep(os.path.join(folder, file), *dims))
        return start, len(inputs)

    cell_spans = [add(f, 2) for f in job.get("moving_cells", [])]  # sliding: the air there is moving air
    slides = job.get("slides", [])
    slide_spans = [([(f, add(f, 1)) for f in s["files"]], (s["marker"], add(s["marker"], 0))) for s in slides]
    size_files = [(z, os.path.join(folder, f)) for z in job["sizes"] for f in z["files"]]
    size_spans = []
    for _, path in size_files:
        start = len(inputs)
        inputs += import_brep(path, 0, 1, 2)
        size_spans.append((start, len(inputs)))
    tf_files = transfinite_files(job, folder)
    tf_spans = []
    for kind, _, path in tf_files:
        start = len(inputs)
        inputs += import_brep(path, 1 if kind == "edge" else 0)
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

    def at(span):  # the final dimtags of inputs[span]
        return [dt for dimtags in out_map[span[0] : span[1]] for dt in dimtags]

    def final(span, dim):
        return [t for d, t in at(span) if d == dim]

    placed = dict(owner)  # what a Mesh Size can merge with: the bodies and the air
    airs = air_items(job)
    if air:
        air_tags = claim_air(final(air_span, 2), owner)
        if "sides" in air:
            pieces = split_air(air_tags, {t for span in cell_spans for t in final(span, 2)})
        else:
            pieces = [air_tags]
        for a, tags in zip(airs, pieces):
            body_faces[a["mat_id"]] = tags
            placed.update(dict.fromkeys(tags, a["name"]))

    job["unwritten"] = [a["mat_id"] for a in airs if not body_faces[a["mat_id"]]]  # run_job lists only the others
    for b in bodies + airs:
        if body_faces[b["mat_id"]]:  # a side of the air may be all bodies, or hold no air at all
            gmsh.model.addPhysicalGroup(2, body_faces[b["mat_id"]], b["mat_id"], name=b["name"])

    by_size = {}  # size -> {dim: [tags]}
    for b, size in [(b, b["size"]) for b in bodies] + [(a, air["size"]) for a in airs]:
        by_size.setdefault(float(size), {}).setdefault(2, []).extend(body_faces[b["mat_id"]])
    for (z, path), (start, end) in zip(size_files, size_spans):
        for dimtags in out_map[start:end]:
            for d, t in dimtags:
                if not _on_bodies(d, t, placed):
                    raise JobError(f"mesh size {z['name']}: {os.path.basename(path)} did not merge with the bodies")
                by_size.setdefault(float(z["size"]), {}).setdefault(d, []).append(t)
    apply_size_fields(by_size)
    mapped = [
        (kind, item, os.path.basename(path), [dt for dimtags in out_map[start:end] for dt in dimtags])
        for (kind, item, path), (start, end) in zip(tf_files, tf_spans)
    ]
    tf_curves = apply_transfinite(job, mapped, body_faces, 2)
    apply_recombine(job, body_faces, 2, tf_curves)
    if job.get("periodic"):
        apply_periodic(job["periodic"], 2)
    if not slides:
        return None
    base = os.path.basename
    mapped = [([(base(f), at(span)) for f, span in files], (base(m), at(span))) for files, (m, span) in slide_spans]
    return slide_split(job, bodies, body_faces, apply_slides(slides, mapped, 2), 2)


def _symmetric(job_path):
    with open(job_path, encoding="utf-8") as fh:
        return "symmetric" in json.load(fh)


def check_job(job_path, build):
    """--check: a symmetric job meshes and copies its cell to run its checks (meshsym.check)."""
    (meshsym.check if _symmetric(job_path) else check)(job_path, build)


def run_job(job_path):
    if _symmetric(job_path):  # mesh the cell and copy it
        print("\n".join(meshsym.report(meshsym.run(job_path, build))))
        return
    job = run(job_path, build, 2)
    for item in job["bodies"] + air_items(job):
        if item["mat_id"] in job["unwritten"]:
            continue
        print(f"MAT_ID  {item['mat_id']:>6}  {item['name']}")
    for item in (job.get("transfinite") or {}).get("bodies", []):
        print(f"Structured      {item['name']}")
    for item in job["bodies"]:
        if item["mat_id"] in job.get("recombine", []):
            print(f"Recombined      {item['name']}")
    if job.get("slides"):
        print("\n".join(slide_report(job)))
    print(f"Wrote {job['mesh_file']}")
    if job.get("slides"):
        print(f"Wrote {job['rotor_file']}")


if __name__ == "__main__":
    sys.exit(main(sys.argv, "mesher2d.py", run_job, build, check_job))
