"""Job file -> Gmsh .msh at job["mesh_file"] + mesh.unv beside the job. Runs in its own process.
Sliding motion: the fixed side goes to job["mesh_file"], the moving side to job["rotor_file"].
Never import FreeCAD here.

Usage: python mesher.py <job.json> [--check]   (--check: geometry checks only, nothing written)
"""

import os
import sys

import gmsh

from meshcommon import (
    JobError,
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


def _import_one(path, *dims):
    tags = gmsh.model.occ.importShapes(path, highestDimOnly=True)
    if len(tags) != 1 or tags[0][0] not in dims:
        raise JobError(f"{os.path.basename(path)}: expected one {'/'.join(map(str, dims))}D entity, got {tags}")
    return tags[0]


def build(job, folder):
    """Import, fragment, check, tag and size the model. Gmsh must be initialized.
    Sliding motion: returns the split of the model into the fixed and the moving side (see meshcommon.run)."""
    vols, surfs = job["volumes"], job["surfaces"]
    if not vols:
        raise JobError("job has no volumes")
    pieces = [import_brep(os.path.join(folder, v["file"]), 3) for v in vols]  # a body may be several solids
    inputs = [t for p in pieces for t in p]
    air = job.get("air")
    if air:  # after the bodies, so the fragment keeps the bodies' pieces whole
        air_pieces = import_brep(os.path.join(folder, air["file"]), 3)
        inputs += air_pieces
    surf_files = [(s, os.path.join(folder, f)) for s in surfs for f in s["files"]]
    inputs += [_import_one(path, 2) for _, path in surf_files]
    size_files = [(z, os.path.join(folder, f)) for z in job["sizes"] for f in z["files"]]
    inputs += [_import_one(path, 0, 1, 2) for _, path in size_files]
    tf_files = transfinite_files(job, folder)
    inputs += [_import_one(path, 1 if kind == "edge" else 0) for kind, _, path in tf_files]

    def add(file, *dims):  # sliding: last, so the spans above keep their places
        start = len(inputs)
        inputs.extend(import_brep(os.path.join(folder, file), *dims))
        return start, len(inputs)

    cell_spans = [add(f, 3) for f in job.get("moving_cells", [])]  # the air there is moving air
    slides = job.get("slides", [])
    slide_spans = [([(f, add(f, 2)) for f in s["files"]], (s["marker"], add(s["marker"], 1))) for s in slides]

    if len(inputs) == 1:  # Gmsh skips a fragment with no tools and returns no map
        out_map = [inputs]
    else:
        _, out_map = gmsh.model.occ.fragment(inputs[:1], inputs[1:])
    gmsh.model.occ.synchronize()

    body_vols = {}  # MAT_ID -> list of final 3D tags of all its pieces
    owner = {}  # final 3D tag -> body name
    start = 0
    for v, p in zip(vols, pieces):
        tags = list(dict.fromkeys(t for dimtags in out_map[start : start + len(p)] for d, t in dimtags if d == 3))
        start += len(p)
        for t in tags:
            if owner.get(t, v["name"]) != v["name"]:  # pieces of one body may share a volume
                raise JobError(f"bodies {owner[t]} and {v['name']} overlap")
            owner[t] = v["name"]
        body_vols[v["mat_id"]] = tags

    def at(span):  # the final dimtags of inputs[span]
        return [dt for dimtags in out_map[span[0] : span[1]] for dt in dimtags]

    airs = air_items(job)
    if air:
        air_tags = claim_air([t for d, t in at((start, start + len(air_pieces))) if d == 3], owner)
        start += len(air_pieces)
        if "sides" in air:
            parts = split_air(air_tags, {t for span in cell_spans for d, t in at(span) if d == 3})
        else:
            parts = [air_tags]
        body_vols.update((a["mat_id"], tags) for a, tags in zip(airs, parts))
    job["unwritten"] = [a["mat_id"] for a in airs if not body_vols[a["mat_id"]]]  # run_job lists only the others
    rest = out_map[start:]  # surface, size and transfinite files, one entity each; then the slide files

    surf_tags = {s["smat_id"]: [] for s in surfs}
    for (s, _), dimtags in zip(surf_files, rest):
        surf_tags[s["smat_id"]] += [t for d, t in dimtags if d == 2]

    for s in surfs:
        boundary = {
            abs(t)
            for _, t in gmsh.model.getBoundary([(3, t) for t in body_vols[s["mat_id"]]], combined=False, oriented=False)
        }
        if not surf_tags[s["smat_id"]] or not set(surf_tags[s["smat_id"]]) <= boundary:
            raise JobError(
                f"excitation surface {s['name']} does not lie on its body (face did not merge with the body boundary)"
            )

    for v in vols + airs:
        if body_vols[v["mat_id"]]:  # a side of the air may be all bodies
            gmsh.model.addPhysicalGroup(3, body_vols[v["mat_id"]], v["mat_id"], name=v["name"])
    for s in surfs:
        gmsh.model.addPhysicalGroup(2, sorted(set(surf_tags[s["smat_id"]])), s["smat_id"], name=s["name"])

    by_size = {}  # size -> {dim: [tags]}
    for v, size in [(v, v["size"]) for v in vols] + [(a, air["size"]) for a in airs]:
        by_size.setdefault(float(size), {}).setdefault(3, []).extend(body_vols[v["mat_id"]])
    first = len(surf_files)
    for (z, path), dimtags in zip(size_files, rest[first:]):
        for d, t in dimtags:
            if len(gmsh.model.getAdjacencies(d, t)[0]) == 0:  # nothing above it: not merged
                raise JobError(f"mesh size {z['name']}: {os.path.basename(path)} did not merge with the bodies")
            by_size.setdefault(float(z["size"]), {}).setdefault(d, []).append(t)
    apply_size_fields(by_size)
    tf_maps = rest[first + len(size_files) : first + len(size_files) + len(tf_files)]
    mapped = [(kind, item, os.path.basename(path), dimtags) for (kind, item, path), dimtags in zip(tf_files, tf_maps)]
    tf_curves = apply_transfinite(job, mapped, body_vols, 3)
    apply_recombine(job, body_vols, 3, tf_curves)
    if job.get("periodic"):
        apply_periodic(job["periodic"], 3)
    if not slides:
        return None
    base = os.path.basename
    mapped = [([(base(f), at(span)) for f, span in files], (base(m), at(span))) for files, (m, span) in slide_spans]
    split = slide_split(job, vols, body_vols, apply_slides(slides, mapped, 3), 3)
    moving = set(job["moving"])
    for s in surfs:  # an excitation surface goes to the file of its body
        side = "moving" if s["mat_id"] in moving else "fixed"
        split[side].append((2, sorted(set(surf_tags[s["smat_id"]])), s["smat_id"], s["name"]))
    return split


def run_job(job_path):
    job = run(job_path, build, 3)
    for item in job["volumes"] + air_items(job):
        if item["mat_id"] in job["unwritten"]:
            continue
        print(f"MAT_ID  {item['mat_id']:>6}  {item['name']}")
    for item in job["surfaces"]:
        print(f"SMAT_ID {item['smat_id']:>6}  {item['name']}")
    for item in (job.get("transfinite") or {}).get("bodies", []):
        print(f"Structured      {item['name']}")
    for item in job["volumes"]:
        if item["mat_id"] in job.get("recombine", []):
            print(f"Recombined      {item['name']}")
    if job.get("slides"):
        print("\n".join(slide_report(job)))
    print(f"Wrote {job['mesh_file']}")
    if job.get("slides"):
        print(f"Wrote {job['rotor_file']}")


if __name__ == "__main__":
    sys.exit(main(sys.argv, "mesher.py", run_job, build))
