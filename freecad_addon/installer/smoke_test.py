"""Installer smoke test, run as: freecad.exe smoke_test.py <out_dir> <input.json>

Checks that the EMSolution workbench loads, pyemsi imports, and the input control
editor renders in its own window. Writes result.txt + editor.png to <out_dir>, then quits.
"""

import os
import sys
import traceback

import FreeCAD as App
import FreeCADGui as Gui
from PySide6.QtCore import Qt, QTimer

out_dir, input_file = sys.argv[-2], sys.argv[-1]
os.makedirs(out_dir, exist_ok=True)
log = open(os.path.join(out_dir, "result.txt"), "w", encoding="utf-8")


def report(*args):
    print(*args, file=log, flush=True)


report("freecad", ".".join(App.Version()[:3]), "prefix", sys.prefix)
report("EMSolution workbench", "EMSolutionWorkbench" in Gui.listWorkbenches())
mw = Gui.getMainWindow()
state = {}


def open_editor():
    try:
        import pyemsi
        from pyemsi.widgets.input_control_editor import InputControlEditorWidget

        report("pyemsi", pyemsi.__version__, pyemsi.__file__)
        w = InputControlEditorWidget(mw)
        w.setWindowFlag(Qt.WindowType.Window)
        w.load_file(input_file)
        w.setGeometry(mw.x() + 300, mw.y() + 100, 1100, 750)
        w.show()
        state["editor"] = w
    except Exception:
        report(traceback.format_exc())
    QTimer.singleShot(8000, check)


def check():
    w = state.get("editor")
    if w is None:
        return finish()
    report("editor ready", w._ready)
    w.screen().grabWindow(w.winId()).save(os.path.join(out_dir, "editor.png"))
    w.screen().grabWindow(0).save(os.path.join(out_dir, "screen.png"))
    w.page().runJavaScript("document.body.innerText.length", 0, lambda n: (report("editor text length", n), finish()))


def finish():
    if "editor" in state:
        state["editor"].close()
    report("done")
    log.close()
    mw.close()


QTimer.singleShot(2000, open_editor)
