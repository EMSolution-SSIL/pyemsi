import importlib.util
import os
import sys

# The add-on suite runs in the `addon` environment (`pixi run -e addon test-addon`). Without FreeCAD (the default
# environment, e.g. a bare `pytest tests`) collect nothing here instead of failing on the FreeCAD imports.
if importlib.util.find_spec("FreeCAD") is None:
    collect_ignore_glob = ["*"]

# FreeCAD finds the addon's `emsolution` package through the Mod folder; tests and the
# subprocesses they start (mesher, document reload) find it through these paths.
ADDON = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon"))
sys.path.insert(0, ADDON)
os.environ["PYTHONPATH"] = os.pathsep.join(p for p in (ADDON, os.environ.get("PYTHONPATH")) if p)
