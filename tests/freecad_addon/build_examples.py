r"""Builds the example models into a folder you can open in FreeCAD and check by hand.

From the repo root:
    pixi run python tests/freecad_addon/build_examples.py [out_dir] [--only NAME ...] [--sample DIR]
Each case gets out_dir/<name>/ with the .FCStd, the mesh and report.txt (elements per MAT_ID and a checklist).
One line per case: OK name, ERROR name: text (what an E-case must give) or FAILED name: text.
"""

import argparse
import os
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ADDON = os.path.join(REPO, "freecad_addon")
# What conftest.py sets up for pytest: the addon package and, for the mesher subprocess, PYTHONPATH.
sys.path[:0] = [REPO, ADDON]
os.environ["PYTHONPATH"] = os.pathsep.join(p for p in (ADDON, os.environ.get("PYTHONPATH")) if p)

from tests.freecad_addon.cases import CASES, run_case  # noqa: E402 - needs the paths above

DEFAULT_OUT = r"C:\Users\hamed\Desktop\delme\air_examples"


def one_line(text):
    return " | ".join(line for line in text.strip().splitlines() if line)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("out_dir", nargs="?", default=DEFAULT_OUT)
    parser.add_argument("--only", nargs="+", metavar="NAME", help="build only these cases")
    parser.add_argument("--sample", metavar="DIR", help="folder of a reference mesh to compare with (slide cases)")
    args = parser.parse_args(argv)
    cases = [c for c in CASES if not args.only or c.name in args.only]
    unknown = set(args.only or []) - {c.name for c in CASES}
    if unknown:
        parser.error("unknown case: " + ", ".join(sorted(unknown)))
    failed = 0
    for case in cases:
        try:
            text = run_case(case, args.out_dir)
        except Exception as exc:
            failed += 1
            print(f"FAILED {case.name}: {one_line(str(exc))}", flush=True)
            continue
        if not case.expect_error:
            print(f"OK {case.name}", flush=True)
        elif case.expect_error in text:
            print(f"ERROR {case.name}: {one_line(text)}", flush=True)
        else:
            failed += 1
            print(
                f"FAILED {case.name}: expected an error with '{case.expect_error}', got: {one_line(text)}", flush=True
            )
    print(f"Folder: {args.out_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
