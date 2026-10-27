"""Build the 2D motor with a ready EMSolution Study for trying Symmetric Mesh by hand: the test model of
tests/freecad_addon/symcases.py (cells, Mirror, Polar Array, Fragments, two Symmetric Mesh items, 18 Materials on
faces, a Sliding Interface at r 35 with 144 divisions).

    pixi run -e addon python experiments/symmetric_spike/build_study.py   -> experiments/symmetric_spike/motor2d_study.FCStd
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [REPO, os.path.join(REPO, "freecad_addon")]

import FreeCAD as App  # noqa: E402 - needs the paths above

from tests.freecad_addon.symcases import motor_study  # noqa: E402 - needs the paths above

doc = App.newDocument("motor2d_study")
study = motor_study(doc)
doc.recompute()
path = os.path.join(HERE, "motor2d_study.FCStd")
doc.saveAs(path)
print("saved", path, "-", study.Label)
