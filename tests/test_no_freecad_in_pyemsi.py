"""pyemsi ships without FreeCAD: the FreeCAD viewer lives on ``experimental/freecad-viewer``."""

from __future__ import annotations

import re
from pathlib import Path

PYEMSI_ROOT = Path(__file__).resolve().parents[1] / "pyemsi"
SCANNED_SUFFIXES = {".py", ".pyx", ".qrc", ".md"}
FORBIDDEN = re.compile(r"freecad|ems_material|ems-material-manager", re.IGNORECASE)


def test_pyemsi_has_no_freecad_reference():
    offenders = []
    for path in sorted(PYEMSI_ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES or "__pycache__" in path.parts:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if FORBIDDEN.search(line):
                offenders.append(f"{path.relative_to(PYEMSI_ROOT.parent)}:{number}: {line.strip()[:80]}")
    assert not offenders, "FreeCAD references left in pyemsi:\n" + "\n".join(offenders)


def test_no_freecad_files_left_in_pyemsi():
    names = [p.name for p in PYEMSI_ROOT.rglob("*") if p.is_file() and "freecad" in p.name.lower()]
    assert names == []
