"""CLI entry-point for running an EMSolution simulation via pyemsol.

Usage::

    python -m pyemsi.tools.run_emsol <input.json>

The script reads the JSON input file, then calls::

    pyemsol.initialize(data, directory)
    pyemsol.solve()
    pyemsol.finalize()
"""

from __future__ import annotations

import json
import os
import sys


def _ensure_repo_root_on_sys_path() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


_ensure_repo_root_on_sys_path()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m pyemsi.tools.run_emsol <input.json>", file=sys.stderr)
        sys.exit(1)

    input_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(input_path):
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    directory = os.path.dirname(input_path)

    with open(input_path, encoding="utf-8") as fh:
        data = json.load(fh)

    import pyemsol

    print(f"Initializing pyemsol with {input_path} ...")
    pyemsol.initialize(data, directory)

    print("Solving ...")
    pyemsol.solve()

    print("Finalizing ...")
    pyemsol.finalize()

    print("Done.")


if __name__ == "__main__":
    main()
