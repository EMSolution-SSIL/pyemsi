"""Job file -> Gmsh .msh at job["mesh_file"] + mesh.unv beside the job. Runs in its own process.
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
)


def _import_one(path, *dims):
    tags = gmsh.model.occ.importShapes(path, highestDimOnly=True)
    if len(tags) != 1 or tags[0][0] not in dims:
        raise JobError(f"{os.path.basename(path)}: expected one {'/'.join(map(str, dims))}D entity, got {tags}")
    return tags[0]


def _import_solids(path):
    """A body file holds one or more solids, e.g. the pieces of a Part Slice."""
    tags = gmsh.model.occ.importShapes(path, highestDimOnly=True)
    if not tags or any(d != 3 for d, _ in tags):
        raise JobError(f"{os.path.basename(path)}: expected 3D entities, got {tags}")
    return tags


def build(job, folder):
    """Import, fragment, check, tag and size the model. Gmsh must be initialized."""
    vols, surfs = job["volumes"], job["surfaces"]
    if not vols:
        raise JobError("job has no volumes")
    pieces = [_import_solids(os.path.join(folder, v["file"])) for v in vols]
    inputs = [t for p in pieces for t in p]
    air = job.get("air")
    if air and "sides" in air:
        raise JobError("sliding motion cannot be meshed in 3D yet")
    if air:  # after the bodies, so the fragment keeps the bodies' pieces whole
        air_pieces = _import_solids(os.path.join(folder, air["file"]))
        inputs += air_pieces
    surf_files = [(s, os.path.join(folder, f)) for s in surfs for f in s["files"]]
    inputs += [_import_one(path, 2) for _, path in surf_files]
    size_files = [(z, os.path.join(folder, f)) for z in job["sizes"] for f in z["files"]]
    inputs += [_import_one(path, 0, 1, 2) for _, path in size_files]
    tf_files = transfinite_files(job, folder)
    inputs += [_import_one(path, 1 if kind == "edge" else 0) for kind, _, path in tf_files]

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
    if air:
        air_tags = [t for dimtags in out_map[start : start + len(air_pieces)] for d, t in dimtags if d == 3]
        start += len(air_pieces)
        body_vols[air["mat_id"]] = claim_air(air_tags, owner)
    rest = out_map[start:]  # surface, size and transfinite files, one entity each

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

    for v in vols + ([air] if air else []):
        gmsh.model.addPhysicalGroup(3, body_vols[v["mat_id"]], v["mat_id"], name=v["name"])
    for s in surfs:
        gmsh.model.addPhysicalGroup(2, sorted(set(surf_tags[s["smat_id"]])), s["smat_id"], name=s["name"])

    by_size = {}  # size -> {dim: [tags]}
    for v in vols + ([air] if air else []):
        by_size.setdefault(float(v["size"]), {}).setdefault(3, []).extend(body_vols[v["mat_id"]])
    first = len(surf_files)
    for (z, path), dimtags in zip(size_files, rest[first:]):
        for d, t in dimtags:
            if len(gmsh.model.getAdjacencies(d, t)[0]) == 0:  # nothing above it: not merged
                raise JobError(f"mesh size {z['name']}: {os.path.basename(path)} did not merge with the bodies")
            by_size.setdefault(float(z["size"]), {}).setdefault(d, []).append(t)
    apply_size_fields(by_size)
    tf_maps = rest[first + len(size_files) :]
    mapped = [(kind, item, os.path.basename(path), dimtags) for (kind, item, path), dimtags in zip(tf_files, tf_maps)]
    tf_curves = apply_transfinite(job, mapped, body_vols, 3)
    apply_recombine(job, body_vols, 3, tf_curves)


def run_job(job_path):
    job = run(job_path, build, 3)
    for item in job["volumes"] + air_items(job):
        print(f"MAT_ID  {item['mat_id']:>6}  {item['name']}")
    for item in job["surfaces"]:
        print(f"SMAT_ID {item['smat_id']:>6}  {item['name']}")
    for item in (job.get("transfinite") or {}).get("bodies", []):
        print(f"Structured      {item['name']}")
    for item in job["volumes"]:
        if item["mat_id"] in job.get("recombine", []):
            print(f"Recombined      {item['name']}")
    print(f"Wrote {job['mesh_file']}")


if __name__ == "__main__":
    sys.exit(main(sys.argv, "mesher.py", run_job, build))
