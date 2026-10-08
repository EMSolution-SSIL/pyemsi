import os
import sys

# FreeCAD finds the addon's `emsolution` package through the Mod folder; tests and the
# subprocesses they start (mesher, document reload) find it through these paths.
ADDON = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon"))
sys.path.insert(0, ADDON)
os.environ["PYTHONPATH"] = os.pathsep.join(p for p in (ADDON, os.environ.get("PYTHONPATH")) if p)
