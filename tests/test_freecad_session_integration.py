"""End-to-end check of FreeCADSession against the real FreeCAD in the Pixi env.

Runs in a subprocess (offscreen Qt) so a native failure cannot kill pytest.
Takes ~15-30 s because FreeCAD's GUI initializes all workbenches.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from pyemsi.gui.freecad_runtime import freecad_search_paths

REPO_ROOT = Path(__file__).resolve().parents[1]

_SCRIPT = r"""
import json, os, sys, tempfile
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
app = QApplication.instance() or QApplication([])

from pyemsi.gui.freecad_session import FreeCADDocumentError, FreeCADSession

out = {}
session = FreeCADSession()
session.ensure_initialized()
session.ensure_initialized()
out["initialized"] = session.is_initialized
out["parked_hidden"] = not session.main_window.isVisible()

tmp = tempfile.mkdtemp()
path = os.path.join(tmp, "Box.FCStd")
import FreeCAD
doc = FreeCAD.newDocument("Box")
doc.addObject("Part::Box", "Box")
doc.recompute()
doc.saveAs(path)
FreeCAD.closeDocument("Box")

name1 = session.open_document(path)
name2 = session.open_document(path.replace("\\", "/"))
out["names"] = [name1, name2]
out["doc_count"] = len(FreeCAD.listDocuments())
out["is_open"] = session.is_document_open(path)
out["modified_after_open"] = session.modified_documents()

bad = os.path.join(tmp, "bad.FCStd")
with open(bad, "w") as fh:
    fh.write("not a zip")
try:
    session.open_document(bad)
    out["bad_error"] = None
except FreeCADDocumentError as exc:
    out["bad_error"] = str(exc)
out["still_initialized"] = session.is_initialized

cycles = 0
for _ in range(3):
    host = QWidget(); QVBoxLayout(host)
    session.attach(host)
    assert session.main_window.parent() is host
    session.detach(host)
    assert session.attached_host is None
    host.deleteLater()
    app.processEvents()
    cycles += 1
out["cycles"] = cycles
session.prepare_for_application_exit()
print(json.dumps(out))
"""


@pytest.mark.skipif(not freecad_search_paths(), reason="FreeCAD is not installed in the active environment")
def test_real_freecad_session_lifecycle():
    result = subprocess.run(
        [sys.executable, "-c", _SCRIPT],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    payload = json.loads(result.stdout.strip().splitlines()[-1])

    assert payload["initialized"] and payload["parked_hidden"]
    assert payload["names"] == ["Box", "Box"]
    assert payload["doc_count"] == 1
    assert payload["is_open"] is True
    assert payload["modified_after_open"] == []
    assert payload["bad_error"] and "Invalid project file" in payload["bad_error"]
    assert payload["still_initialized"] is True
    assert payload["cycles"] == 3
