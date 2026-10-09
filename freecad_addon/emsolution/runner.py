"""Run mesher.py in a background process, stream its output, load the result."""

import json
import os
import sys

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import jobwriter

MESHER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesher.py")
_run = None  # the active MeshRun; the reference also keeps it alive


def busy():
    return _run is not None


def python_exe():
    # Stock FreeCAD keeps python.exe in <home>\bin; a conda env (pixi, installer) in its root.
    for exe in (os.path.join(App.getHomePath(), "bin", "python.exe"), os.path.join(sys.prefix, "python.exe")):
        if os.path.exists(exe):
            return exe
    return exe


def start(study):
    global _run
    try:
        job = jobwriter.write_job(study)
    except Exception as exc:  # StudyError, or anything the geometry export trips on
        QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "EMSolution", str(exc))
        return None
    _run = MeshRun(study, job)
    return _run


class MeshRun:
    def __init__(self, study, job):
        self.study, self.job = study, job
        self.cancelled = False
        self.error = ""
        with open(job, encoding="utf-8") as fh:
            self.mesh_file = json.load(fh)["mesh_file"]
        self.replaced = os.path.exists(self.mesh_file)  # before the mesher starts
        self.dialog = QtWidgets.QProgressDialog("Meshing…", "Cancel", 0, 0, Gui.getMainWindow())
        self.dialog.setWindowTitle("EMSolution")
        self.dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.dialog.canceled.connect(self.cancel)
        self.proc = QtCore.QProcess()
        self.proc.readyReadStandardOutput.connect(self._stdout)
        self.proc.readyReadStandardError.connect(self._stderr)
        self.proc.finished.connect(self._finished)
        self.proc.errorOccurred.connect(self._failed_to_start)
        self.proc.start(python_exe(), [MESHER, job])
        self.dialog.show()

    def _stdout(self):
        App.Console.PrintMessage(bytes(self.proc.readAllStandardOutput()).decode(errors="replace"))

    def _stderr(self):
        text = bytes(self.proc.readAllStandardError()).decode(errors="replace")
        App.Console.PrintWarning(text)
        for line in text.splitlines():
            if line.startswith("ERROR:"):
                self.error = line[len("ERROR:") :].strip()

    def cancel(self):
        self.cancelled = True
        self.proc.kill()

    def _failed_to_start(self, err):
        if err == QtCore.QProcess.FailedToStart:
            self.error = f"Could not start {python_exe()}"
            self._finished(-1, None)

    def _finished(self, code, _status):
        global _run
        _run = None
        self.dialog.canceled.disconnect(self.cancel)  # closing the dialog emits canceled
        self.dialog.close()
        parent = Gui.getMainWindow()
        if self.cancelled:
            QtWidgets.QMessageBox.information(parent, "EMSolution", "Meshing cancelled.")
        elif code != 0:
            QtWidgets.QMessageBox.critical(
                parent, "EMSolution", self.error or f"The mesher stopped with exit code {code}."
            )
        else:
            self.load_result()

    def load_result(self):
        import Fem
        import FemGui  # noqa: F401  registers the view provider for FEM meshes

        doc = self.study.Document
        mesh_obj = self.study.MeshResult
        if mesh_obj is None:
            mesh_obj = doc.addObject("Fem::FemMeshObject", "MeshResult")
            self.study.addObject(mesh_obj)
            self.study.MeshResult = mesh_obj
        mesh_obj.FemMesh = Fem.read(os.path.join(os.path.dirname(self.job), "mesh.unv"))
        doc.recompute()
        folder, name = os.path.split(self.mesh_file)
        replaced = " (replaced existing file)" if self.replaced else ""
        App.Console.PrintMessage(
            f"{name} written to {folder} from Study {self.study.Label}{replaced}\n"
            'Input files read it with INPUT_MESH_FILE = "GMSH" (11).\n'
        )
