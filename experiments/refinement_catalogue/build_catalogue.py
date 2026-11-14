r"""The Stage 1 refinement catalogue (spec 9): each row of rows.CASES is built as a Study, its set-up saved, meshed with
its Refine Near items ("new") and again with them deleted ("today"), and its pictures drawn.

Run: pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py [--only ID ...]
Output: experiments/refinement_catalogue/<id>/<id>.FCStd, the set-up Study (git-ignored; rebuild it with this script),
and C:\Users\hamed\Desktop\delme\refinement_studies\<id>\new\ and ...\today\ (the Study and its mesh files, new.png and
today.png), results.json and catalogue.html (make_page.py). With --only the other rows of results.json are kept.
Exit code 1 when a row does not match its expectation."""

import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import rows  # noqa: E402 - sets up FreeCAD and the add-on paths
from rows import App  # noqa: E402

from emsolution import jobwriter, objects, validation  # noqa: E402
from tests.freecad_addon import symcases  # noqa: E402

import make_page  # noqa: E402
import render  # noqa: E402

OUT = r"C:\Users\hamed\Desktop\delme\refinement_studies"
RESULTS = os.path.join(OUT, "results.json")


def part_counts(msh_files):
    """{part: elements} of the highest dimension's physical groups of the mesh files, summed."""
    import gmsh

    out = {}
    for msh in msh_files:
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(msh)
            dim = max(d for d, _ in gmsh.model.getPhysicalGroups())
            for d, tag in gmsh.model.getPhysicalGroups(dim):
                name = gmsh.model.getPhysicalName(d, tag) or str(tag)
                n = sum(
                    len(t)
                    for ent in gmsh.model.getEntitiesForPhysicalGroup(d, tag)
                    for t in gmsh.model.mesh.getElements(d, ent)[1]
                )
                out[name] = out.get(name, 0) + n
        finally:
            gmsh.finalize()
    return out


def mesh_into(study, folder, name, picture):
    """Save the Study in folder, validate and mesh it, draw its picture. Returns (verdict, record)."""
    path = os.path.join(folder, name + ".FCStd")
    os.makedirs(folder, exist_ok=True)
    study.Document.saveAs(path)
    start = time.time()
    errors = validation.errors(validation.validate(study))
    if errors:
        return " | ".join(p.text for p in errors), {"seconds": round(time.time() - start, 1), "study": path}
    r = symcases.mesh_and_read(study)
    if not r.ok:
        return r.refused, {"seconds": round(r.seconds, 1), "study": path}
    msh = [jobwriter.mesh_file(study)]
    if study.Movement == "Sliding motion":
        msh.append(jobwriter.rotor_file(study))
    png = os.path.join(folder, os.path.basename(folder) + ".png")
    dim = 2 if study.Dimension == "2D" else 3
    hints = {k: picture[k] for k in ("clip", "at", "zoom") if k in picture}
    if os.path.exists(png):
        os.remove(png)
    render.picture(msh, png, dim, **hints)
    record = {"elements": part_counts(msh), "seconds": round(r.seconds, 1), "study": path, "msh": msh, "png": png}
    record["inverted"] = r.inverted
    return "meshes", record


def run(row):
    name, title, build, expected, picture = row
    out = {"id": name, "title": title, "expected": expected, "verdict": "", "match": False, "new": {}, "today": {}}
    study = None
    try:
        study = build()
        symcases.finish(study, os.path.join(OUT, name, "new", name + ".FCStd"))
        setup = os.path.join(HERE, name, name + ".FCStd")
        os.makedirs(os.path.dirname(setup), exist_ok=True)
        study.Document.saveCopy(setup)
        verdict, out["new"] = mesh_into(study, os.path.join(OUT, name, "new"), name, picture)
        out["verdict"] = verdict
        if verdict == "meshes":
            for item in objects.refine_items(study):
                study.Document.removeObject(item.Name)
            study.Document.recompute()
            today, out["today"] = mesh_into(study, os.path.join(OUT, name, "today"), name, picture)
            if today != "meshes":
                out["verdict"] = f"meshes, but today's copy did not: {today}"
        out["match"] = out["verdict"] == "meshes" if expected == "meshes" else expected in out["verdict"]
        out["files"] = {"setup": setup, "new": out["new"].get("study"), "today": out["today"].get("study")}
        after = rows.AFTER.get(name)
        if after is not None and out["verdict"] == "meshes":
            passed, text = after(os.path.join(OUT, name))
            out["check"] = {"passed": passed, "text": text}
            out["match"] = out["match"] and passed
    except Exception as err:  # a row that cannot be built is a row, not the end of the catalogue
        traceback.print_exc()
        out["verdict"] = f"{type(err).__name__}: {err}"
        out["match"] = expected != "meshes" and expected in out["verdict"]
    finally:
        if study is not None:
            App.closeDocument(study.Document.Name)
    return out


def main(argv):
    only = argv[argv.index("--only") + 1 :] if "--only" in argv else []
    unknown = [n for n in only if n not in {r[0] for r in rows.CASES}]
    if unknown:
        print(f"No such row: {', '.join(unknown)}")
        return 1
    old = {}
    if only and os.path.exists(RESULTS):
        with open(RESULTS, encoding="utf-8") as fh:
            old = {r["id"]: r for r in json.load(fh)}
    results = []
    for row in rows.CASES:
        if only and row[0] not in only:
            if row[0] in old:
                results.append(old[row[0]])
            continue
        r = run(row)
        results.append(r)
        count = lambda side: sum(r[side].get("elements", {}).values())  # noqa: E731 - a one-line helper
        print(
            f"{r['id']:7s} {'matches' if r['match'] else 'DOES NOT MATCH':14s} {r['verdict'][:90]} | today "
            f"{count('today')} new {count('new')} | {r['new'].get('seconds', 0)} s",
            flush=True,
        )
    os.makedirs(OUT, exist_ok=True)
    with open(RESULTS, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1, ensure_ascii=False)
    print("page:", make_page.write(RESULTS))
    bad = [r["id"] for r in results if not r["match"]]
    print(f"\n{len(results) - len(bad)} of {len(results)} match" + (f"; not matching: {', '.join(bad)}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
