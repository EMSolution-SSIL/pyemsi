r"""The example catalogue as FreeCAD Studies of Symmetric Groups: each case is built, saved, validated and meshed, and
its row is compared with what the catalogue expects ("meshes", or a refusal with a phrase of its message).

Run: pixi run -e addon python experiments/symmetric_catalogue/build_catalogue.py [id ...]
Output: C:\Users\hamed\Desktop\delme\catalogue_studies\<id>\<id>.FCStd (the mesh files beside it)
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


def cases():
    """(id, builder, expected) of every section, then the success-list cases no section lists."""
    out = [c for module in (m2, m3, rods, litz, devices, traps) for c in module.CASES]
    have = {c[0] for c in out}
    out.insert(0, ("motor_sliding", sl.motor_sliding, "meshes"))
    out += [(n, b, "meshes") for n, b in sl.CASES if n not in have and n not in ("motor_sliding", "general")]
    return out


def matches(expected, verdict, detail):
    if expected == "meshes":
        return verdict == "OK"
    return verdict == "refused" and expected[1].lower() in detail.lower()


def want(expected):
    return "meshes" if expected == "meshes" else f"refused ({expected[1]})"


if __name__ == "__main__":
    wanted = sys.argv[1:]
    rows = []
    for name, build, expected in cases():
        if wanted and name not in wanted:
            continue
        _, verdict, detail = sl.run(name, build, os.path.join(OUT, name, name + ".FCStd"))
        ok = matches(expected, verdict, detail)
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
