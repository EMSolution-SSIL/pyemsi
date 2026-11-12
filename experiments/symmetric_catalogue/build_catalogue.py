r"""The example catalogue as FreeCAD Studies of Symmetric Groups: each case is built, saved, validated and meshed, and
its row is compared with what the catalogue expects ("meshes", or a refusal with a phrase of its message).

Run: pixi run -e addon python experiments/symmetric_catalogue/build_catalogue.py [--setup-only] [id ...]
Output: experiments/symmetric_catalogue/<id>/<id>.FCStd, the set-up Study of each case (git-ignored; rebuild it with
this script), and C:\Users\hamed\Desktop\delme\catalogue_studies\<id>\<id>.FCStd with the mesh files beside it.
--setup-only builds and saves the set-up Studies without validating or meshing them (a few minutes for all).
--coarse (or --coarse=<factor>) multiplies the default mesh size and every Mesh Size by 2 (or factor) for a quick pass;
Transfinite counts stay. Its meshes go to ...\catalogue_studies_coarse and the set-up Studies here are not rewritten,
so element counts are only comparable with an earlier --coarse run of the same factor.
Exit code 1 when a row does not match its expectation."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import common  # noqa: E402, F401 - FreeCAD and the add-on paths
import devices  # noqa: E402
import litz  # noqa: E402
import m2  # noqa: E402
import m3  # noqa: E402
import rods  # noqa: E402
import traps  # noqa: E402
from common import sl  # noqa: E402

OUT = r"C:\Users\hamed\Desktop\delme\catalogue_studies"
sl.OUT = OUT


def setup_path(name):
    """Where the set-up Study of a case is kept: its own folder in this one."""
    return os.path.join(HERE, name, name + ".FCStd")


def build_setup(name, build):
    """Build one case and save its set-up Study only. Returns "" or the reason it could not be built."""
    import FreeCAD as App
    from tests.freecad_addon import symcases

    study = None
    try:
        study = build()
        symcases.finish(study, setup_path(name))
        return ""
    except Exception as err:  # a case that cannot be built is reported, the others still are
        return f"{type(err).__name__}: {err}"
    finally:
        if study is not None:
            App.closeDocument(study.Document.Name)


def cases():
    """(id, builder, expected, check or None) of every section, then the success-list cases no section lists. A check
    (study) gives (ok, text) on the built Study (traps.py); a check with after(folder) also gives (ok, text) on the
    mesh files of a case that meshed (common.Structured)."""
    out = [(*c, None)[:4] for module in (m2, m3, rods, litz, devices, traps) for c in module.CASES]
    have = {c[0] for c in out}
    out.insert(0, ("motor_sliding", sl.motor_sliding, "meshes", None))
    out += [(n, b, "meshes", None) for n, b in sl.CASES if n not in have and n not in ("motor_sliding", "general")]
    return out


def checked(build, check, found):
    """build, with check run on the Study it gives and its (ok, text) put in found."""

    def wrapped():
        study = build()
        found.append(check(study))
        return study

    return wrapped


def coarsened(build, factor):
    """build, with the default mesh size and every Mesh Size item of the Study it gives multiplied by factor.
    Transfinite counts are left as they are."""
    from emsolution import objects

    def wrapped():
        study = build()
        study.MeshSizesGroup.DefaultMeshSize = study.MeshSizesGroup.DefaultMeshSize.Value * factor
        for item in objects.mesh_sizes(study):
            item.Size = item.Size.Value * factor
        study.Document.recompute()
        return study

    return wrapped


def matches(expected, verdict, detail):
    if expected == "meshes":
        return verdict == "OK"
    return verdict == "refused" and expected[1].lower() in detail.lower()


def want(expected):
    return "meshes" if expected == "meshes" else f"refused ({expected[1]})"


def setups_only(wanted):
    """--setup-only: build and save the set-up Study of each wanted case (all when none is named)."""
    failed = []
    for name, build, _, _ in cases():
        if wanted and name not in wanted:
            continue
        problem = build_setup(name, build)
        print(f"{name}: {problem or setup_path(name)}", flush=True)
        if problem:
            failed.append(name)
    unknown = [n for n in wanted if n not in {c[0] for c in cases()}]
    if unknown:
        print(f"No such case: {', '.join(unknown)}")
    print(f"\n{'Not built: ' + ', '.join(failed) if failed else 'All set-ups built.'}")
    sys.exit(1 if failed or unknown else 0)


def coarse_option(args):
    """(factor or None, the other arguments) for --coarse (factor 2) or --coarse=<factor> (a number above 0)."""
    factor, rest = None, []
    for a in args:
        if a == "--coarse" or a.startswith("--coarse="):
            factor = float(a.partition("=")[2] or 2)
            if factor <= 0:
                sys.exit(f"--coarse needs a factor above 0, not {factor:g}")
        else:
            rest.append(a)
    return factor, rest


if __name__ == "__main__":
    factor, wanted = coarse_option(sys.argv[1:])
    if "--setup-only" in wanted:
        setups_only([n for n in wanted if n != "--setup-only"])
    out = OUT if factor is None else f"{OUT}_coarse"  # a quick pass never overwrites the full run's meshes
    rows = []
    for name, build, expected, check in cases():
        if wanted and name not in wanted:
            continue
        found = []
        if factor is not None:
            build = coarsened(build, factor)
        if check is not None:
            build = checked(build, check, found)
        setup = setup_path(name) if factor is None else None  # the kept set-up Studies stay at full size
        _, verdict, detail = sl.run(name, build, os.path.join(out, name, name + ".FCStd"), setup)
        ok = matches(expected, verdict, detail)
        if check is not None:
            passed, text = found[0] if found else (False, "not run, the Study was not built")
            ok = ok and passed
            detail += f" | check {'passed' if passed else 'FAILED'}: {text}"
        if getattr(check, "after", None) is not None and verdict == "OK":  # a check of the mesh files (Structured)
            passed, text = check.after(os.path.join(out, name))
            ok = ok and passed
            detail += f" | mesh check {'passed' if passed else 'FAILED'}: {text}"
        rows.append((name, verdict, want(expected), ok, detail))
        print(f"{name} | {verdict} | {'matches' if ok else 'DOES NOT MATCH'} | {detail}", flush=True)
    print("\nCatalogue")
    for name, verdict, expected, ok, detail in rows:
        print(f"{name:14s} {verdict:8s} expected {expected:30s} {'matches' if ok else 'NO MATCH':8s} {detail}")
    bad = [r[0] for r in rows if not r[3]]
    print(f"\n{len(rows) - len(bad)} of {len(rows)} match" + (f"; not matching: {', '.join(bad)}" if bad else ""))
    unknown = [n for n in wanted if n not in {c[0] for c in cases()}]
    if unknown:
        print(f"No such case: {', '.join(unknown)}")
    if not rows:
        print("No case ran.")
    sys.exit(1 if bad or unknown or not rows else 0)
