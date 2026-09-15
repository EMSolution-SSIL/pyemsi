"""Build the EMSolutionDocs input control file editor and copy it into pyemsi.

Usage (from the repository root, inside the pixi environment):

    git submodule update --init EMSolutionDocs
    python tools/sync_input_control_editor.py [--skip-build]

The bundle is committed so pyemsi users do not need Node.js. The EMSolutionDocs
commit it was built from is recorded in ``editor/SOURCE_COMMIT``.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITOR_DIR = ROOT / "EMSolutionDocs" / "frontend" / "input-control-file-editor"
DIST_DIR = EDITOR_DIR / "dist"
TARGET_DIR = ROOT / "pyemsi" / "widgets" / "input_control_editor" / "editor"


def _run(command: list[str], cwd: Path) -> str:
    executable = shutil.which(command[0])
    if executable is None:
        sys.exit(f"'{command[0]}' was not found on PATH.")
    result = subprocess.run([executable, *command[1:]], cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-build", action="store_true", help="copy the existing dist folder without rebuilding")
    args = parser.parse_args()

    if not EDITOR_DIR.is_dir():
        sys.exit(f"Editor sources not found at {EDITOR_DIR}. Run: git submodule update --init EMSolutionDocs")

    if not args.skip_build:
        print("Installing editor dependencies...")
        _run(["npm", "ci"], EDITOR_DIR)
        print("Building editor bundle...")
        _run(["npm", "run", "build"], EDITOR_DIR)

    if not (DIST_DIR / "editor.js").is_file():
        sys.exit(f"No built bundle found at {DIST_DIR}.")

    commit = _run(["git", "rev-parse", "HEAD"], EDITOR_DIR)
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    shutil.copytree(DIST_DIR, TARGET_DIR)
    (TARGET_DIR / "SOURCE_COMMIT").write_text(commit + "\n", encoding="utf-8")
    print(f"Copied editor bundle from EMSolutionDocs {commit[:12]} to {TARGET_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
