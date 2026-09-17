"""Locate and import FreeCAD strictly from the active Python environment.

FreeCAD's Python modules in a conda/Pixi environment live under
``<sys.prefix>/Library/bin`` (Windows) with workbenches under ``Library/Mod``
and ``Library/Ext``. This module adds those directories to ``sys.path`` once,
registers the DLL directory on Windows, imports ``FreeCAD``/``FreeCADGui``
lazily and refuses modules that resolve outside the active prefix. It never
searches system-wide FreeCAD installations.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
from dataclasses import dataclass
from types import ModuleType
from typing import Callable

LOGGER = logging.getLogger(__name__)


class FreeCADRuntimeError(RuntimeError):
    """FreeCAD could not be located or imported from the active environment."""


_CANDIDATE_SUBDIRS: tuple[str, ...] = (
    os.path.join("Library", "bin"),
    os.path.join("Library", "lib"),
    os.path.join("Library", "Ext"),
    os.path.join("Library", "Mod"),
    "lib",
    "Ext",
    "Mod",
)

# Module state so path/DLL setup happens once per prefix per process.
_prepared_prefixes: set[str] = set()
_dll_handles: list[object] = []


def _normalize_prefix(prefix: str | None) -> str:
    """Absolute prefix path with its original case (case-folding is done only for comparisons)."""
    return os.path.normpath(os.path.abspath(prefix or sys.prefix))


def _prefix_key(prefix: str) -> str:
    return os.path.normcase(prefix)


def freecad_search_paths(prefix: str | None = None) -> list[str]:
    """Return the existing FreeCAD directories under *prefix* (default ``sys.prefix``)."""
    base = os.path.abspath(prefix or sys.prefix)
    found: list[str] = []
    for sub in _CANDIDATE_SUBDIRS:
        candidate = os.path.normpath(os.path.join(base, sub))
        if os.path.isdir(candidate):
            found.append(candidate)
    return found


def _describe_failure(prefix: str, paths: list[str], reason: str) -> str:
    searched = ", ".join(paths) if paths else "(no FreeCAD directories found under the prefix)"
    return "\n".join(
        [
            "FreeCAD could not be initialized in the active pyemsi environment.",
            f"Reason: {reason}",
            f"Python executable: {sys.executable}",
            f"Environment prefix: {prefix}",
            f"Searched: {searched}",
        ]
    )


def prepare_freecad_paths(
    prefix: str | None = None,
    *,
    sys_path: list[str] | None = None,
    dll_adder: Callable[[str], object] | None = None,
) -> list[str]:
    """Make FreeCAD importable from *prefix*. Idempotent; returns the directories used."""
    norm_prefix = _normalize_prefix(prefix)
    target_path = sys.path if sys_path is None else sys_path
    paths = freecad_search_paths(norm_prefix)
    if not paths:
        raise FreeCADRuntimeError(
            _describe_failure(norm_prefix, paths, "no FreeCAD directories exist in this environment")
        )

    for directory in paths:
        if directory not in target_path:
            target_path.append(directory)

    key = _prefix_key(norm_prefix)
    if key not in _prepared_prefixes:
        adder = dll_adder if dll_adder is not None else getattr(os, "add_dll_directory", None)
        bin_dir = os.path.normpath(os.path.join(norm_prefix, "Library", "bin"))
        if adder is not None and os.path.isdir(bin_dir):
            _dll_handles.append(adder(bin_dir))
        _prepared_prefixes.add(key)
    return paths


@dataclass(frozen=True)
class FreeCADModules:
    """The two FreeCAD entry modules needed by the session."""

    app: ModuleType
    gui: ModuleType


def _is_within(path: str, prefix: str) -> bool:
    key = _prefix_key(prefix)
    try:
        return os.path.commonpath([os.path.normcase(os.path.abspath(path)), key]) == key
    except ValueError:  # different drives on Windows
        return False


def import_freecad(
    prefix: str | None = None,
    *,
    importer: Callable[[str], ModuleType] | None = None,
    sys_path: list[str] | None = None,
    dll_adder: Callable[[str], object] | None = None,
) -> FreeCADModules:
    """Import ``FreeCAD`` and ``FreeCADGui`` from *prefix* or raise :class:`FreeCADRuntimeError`."""
    norm_prefix = _normalize_prefix(prefix)
    do_import = importer or importlib.import_module
    LOGGER.info("FreeCAD runtime bootstrap started (prefix=%s)", norm_prefix)
    paths = prepare_freecad_paths(norm_prefix, sys_path=sys_path, dll_adder=dll_adder)

    try:
        app = do_import("FreeCAD")
        gui = do_import("FreeCADGui")
    except ImportError as exc:
        LOGGER.error("FreeCAD import failed: %s", exc)
        raise FreeCADRuntimeError(_describe_failure(norm_prefix, paths, f"{type(exc).__name__}: {exc}")) from exc

    for module in (app, gui):
        origin = getattr(module, "__file__", None)
        if origin is None or not _is_within(origin, norm_prefix):
            reason = f"{module.__name__} resolved outside the active environment: {origin}"
            LOGGER.error(reason)
            raise FreeCADRuntimeError(_describe_failure(norm_prefix, paths, reason))
        LOGGER.debug("%s imported from %s", module.__name__, origin)

    LOGGER.info("FreeCAD runtime bootstrap complete")
    return FreeCADModules(app=app, gui=gui)
