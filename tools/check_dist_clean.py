"""Refuse pyemsi outputs that carry FreeCAD, the add-on or ems_material.

Usage: python tools/check_dist_clean.py PATH...

PATH is a ``.whl`` / ``.zip``, a ``.tar.gz`` sdist, or a directory (e.g. the portable runtime, whose bundled
Python runtime is scanned too). A glob pattern is expanded here, so it also works from shells that do not.
Exit code 0 when clean, 1 when something was found (one line per hit: ``<archive or dir>: <member path>: <name>``),
2 when a PATH does not exist.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Iterable, Iterator

PATH_NAMES = ("freecad_addon", "ems_material")
IMPORT_NAMES = r"FreeCADGui|FreeCAD|ems_material"
# ``import FreeCAD``, ``import os, FreeCAD as App``, ``from ems_material.x import Y`` (also when indented)
IMPORT_RE = re.compile(
    rf"^[ \t]*(?:from[ \t]+({IMPORT_NAMES})\b|import[ \t]+(?:[\w.]+(?:[ \t]+as[ \t]+\w+)?[ \t]*,[ \t]*)*({IMPORT_NAMES})\b)",
    re.MULTILINE,
)
REQUIRES_RE = re.compile(r"^Requires-Dist:[ \t]*(ems[-_.]material[-_.]manager|freecad)\b", re.IGNORECASE | re.MULTILINE)
# Cheap pre-filter: most .py files mention neither name, so they never reach the regex.
PREFILTER = (b"FreeCAD", b"ems_material")
METADATA_FILES = {"METADATA", "PKG-INFO"}


def _members(path: Path) -> Iterator[tuple[str, "callable"]]:
    """Yield (member path, reader) for every file; the reader returns the member's bytes."""
    if path.is_dir():
        for root, _dirs, files in os.walk(path):
            for name in files:
                full = Path(root, name)
                yield full.relative_to(path).as_posix(), full.read_bytes
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if not info.is_dir():
                    yield info.filename, lambda info=info: archive.read(info)
    else:
        with tarfile.open(path, "r:*") as archive:
            for member in archive:
                if member.isfile():
                    yield member.name, lambda member=member: archive.extractfile(member).read()


def find_leaks(path: Path) -> list[tuple[str, str]]:
    """Return [(member path, forbidden name)] for one wheel, sdist or directory."""
    hits: list[tuple[str, str]] = []
    for member, read in _members(path):
        lowered = member.lower()
        for name in PATH_NAMES:
            if name in lowered:
                hits.append((member, name))
        base = member.rsplit("/", 1)[-1]
        if member.endswith(".py"):
            data = read()
            if any(token in data for token in PREFILTER):
                match = IMPORT_RE.search(data.decode("utf-8", errors="replace"))
                if match:
                    hits.append((member, match.group(1) or match.group(2)))
        elif base in METADATA_FILES:
            match = REQUIRES_RE.search(read().decode("utf-8", errors="replace"))
            if match:
                hits.append((member, match.group(1)))
    return hits


def _expand(arguments: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for argument in arguments:
        matches = [argument] if os.path.exists(argument) else sorted(glob.glob(argument))
        if not matches:
            raise FileNotFoundError(f"no such file or directory: {argument}")
        paths.extend(Path(m) for m in matches)
    return paths


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if not arguments:
        print("usage: check_dist_clean.py PATH...", file=sys.stderr)
        return 2
    try:
        paths = _expand(arguments)
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 2
    found = False
    for path in paths:
        for member, name in find_leaks(path):
            print(f"{path}: {member}: {name}")
            found = True
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
