r"""GUI smoke test: runs inside FreeCAD, drives the commands, runs a mesh, then quits.

Needs the addon linked into a throwaway FreeCAD profile (PowerShell, repo root):
    $h = "$env:TEMP\ems_fc_home"; New-Item -ItemType Directory -Force "$h\Mod" | Out-Null
    if (-not (Test-Path "$h\Mod\EMSolution")) { New-Item -ItemType Junction -Path "$h\Mod\EMSolution" -Target (Get-Location).Path | Out-Null }
    $env:FREECAD_USER_HOME = $h
    Start-Process -Wait "$env:LOCALAPPDATA\Programs\FreeCAD 1.1\bin\FreeCAD.exe" tests\gui_smoke.py
    Get-Content "$env:TEMP\ems_gui_smoke.txt"
The last line of the result file is "PASS" or "FAIL".
"""
import os
import tempfile
import traceback

RESULT = os.path.join(tempfile.gettempdir(), "ems_gui_smoke.txt")
log = []


def main():
    import FreeCAD as App
    import FreeCADGui as Gui

    Gui.activateWorkbench("EMSolutionWorkbench")  # loaded by FreeCAD from the Mod folder
    from emsolution import commands, objects, runner, taskpanels

    commands.ask_text = lambda title, label, default: {"Material": "Copper",
                                                       "Excitation": "Terminal In"}[title]
    commands.ask_size = lambda default: 3.0

    doc = App.newDocument("Smoke")
    for name, x in (("A", 0), ("B", 10)):
        box = doc.addObject("Part::Box", name)
        box.Placement.Base = App.Vector(x, 0, 0)
    doc.recompute()

    Gui.runCommand("EMS_NewStudy")
    study = objects.find_study(doc)
    assert study is not None, "no study"
    study.OutputFolder = tempfile.mkdtemp()
    log.append("study ok")

    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A")
    Gui.Selection.addSelection(doc.Name, "B")
    Gui.Selection.addSelection(doc.Name, study.MaterialsGroup.Name)  # must be ignored
    Gui.runCommand("EMS_Material")
    Gui.runCommand("EMS_MeshSize")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A", "Face1")
    Gui.runCommand("EMS_Excitation")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A", "Edge1")
    Gui.Selection.addSelection(doc.Name, "B", "Vertex8")
    Gui.runCommand("EMS_MeshSize")
    mat, = objects.materials(study)
    exc, = objects.excitations(study)
    size, fine = objects.mesh_sizes(study)
    assert [b.Name for b in mat.References] == ["A", "B"], mat.References
    assert exc.References == [(doc.A, ("Face1",))], exc.References
    assert size.Size.Value == 3.0
    assert size.References == [(doc.A, ("",)), (doc.B, ("",))], size.References
    assert fine.References == [(doc.A, ("Edge1",)), (doc.B, ("Vertex8",))], fine.References
    log.append("commands ok")

    panel = taskpanels.ItemPanel(fine)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "B", "Face2")
    Gui.Selection.addSelection(doc.Name, "A")
    panel.add_selection()
    Gui.Control.showDialog(panel)
    panel.accept()
    refs = {(b.Name, s) for b, subs in fine.References for s in subs}
    assert refs == {("A", "Edge1"), ("A", ""), ("B", "Vertex8"), ("B", "Face2")}, refs
    fine.References = [(doc.A, "Edge1"), (doc.B, "Vertex8"), (doc.B, "Face2")]
    log.append("mesh size panel ok")

    panel = taskpanels.ItemPanel(mat)
    panel.name.setText("Iron")
    panel.refs.item(1).setSelected(True)
    panel.remove()
    Gui.Control.showDialog(panel)
    panel.accept()
    assert mat.Label == "Iron" and [b.Name for b in mat.References] == ["A"]
    mat.References = [doc.A, doc.B]
    log.append("panel ok")

    from PySide import QtWidgets

    def task_buttons():
        boxes = Gui.getMainWindow().findChildren(QtWidgets.QDialogButtonBox)
        return sorted(b.text().replace("&", "") for box in boxes if box.isVisible()
                      for b in box.buttons())

    def select(*names):
        Gui.Selection.clearSelection()
        for name in names:
            Gui.Selection.addSelection(doc.Name, name)
        for _ in range(5):  # the watcher panel and the workbench switch follow the selection
            Gui.updateGui()

    first_column = {"Material": "Materials", "Excitation": "Excitations", "Mesh size": "Mesh Sizes"}

    def shown_folders():
        """{folder name: table} for the folder panels visible in the Tasks tab."""
        tables = Gui.getMainWindow().findChildren(QtWidgets.QTableWidget)
        return {first_column[t.horizontalHeaderItem(0).text()]: t for t in tables
                if t.isVisible() and t.horizontalHeaderItem(0).text() in first_column}

    rows = {"Materials": 2, "Excitations": 1, "Mesh Sizes": 2}
    for folder in (study.MaterialsGroup, study.ExcitationsGroup, study.MeshSizesGroup):
        assert isinstance(folder.ViewObject.Proxy, taskpanels.ViewProviderFolder), folder.Name
        folder.Label = "Renamed"
        assert folder.Label == folder.Proxy.LABEL, folder.Label
        assert folder.ViewObject.Proxy.doubleClicked(folder.ViewObject)
        assert not Gui.Control.activeDialog(), "double-click opened a dialog"
        select(folder.Name)
        shown = shown_folders()
        assert list(shown) == [folder.Label], (folder.Name, list(shown))
        assert shown[folder.Label].rowCount() == rows[folder.Label], folder.Name
    select("A")
    assert shown_folders() == {}, "folder panel still shown for a body"

    select(study.MeshSizesGroup.Name)
    combo, = [c for c in Gui.getMainWindow().findChildren(QtWidgets.QComboBox)
              if c.isVisible() and c.findText("HXT") >= 0]
    combo.setCurrentText("HXT")
    factor, = [s for s in Gui.getMainWindow().findChildren(QtWidgets.QDoubleSpinBox)
               if s.isVisible() and s.suffix() == ""]
    factor.setValue(0.9)
    assert (study.MeshSizesGroup.VolumeAlgorithm, study.MeshSizesGroup.SizeFactor) == ("HXT", 0.9)
    assert doc.UndoNames[:2] == ["Edit mesh settings"] * 2, doc.UndoNames

    select(study.MaterialsGroup.Name)
    shown_folders()["Materials"].cellDoubleClicked.emit(1, 0)
    for _ in range(5):
        Gui.updateGui()
    assert task_buttons() == ["Cancel", "OK"], ("item panel did not open from the row", task_buttons())
    assert shown_folders() == {}, "folder panel shown beside the edit dialog"
    Gui.Control.closeDialog()
    for _ in range(5):
        Gui.updateGui()
    assert list(shown_folders()) == ["Materials"], "folder panel not back after the edit"
    log.append("folder panels ok")

    Gui.activateWorkbench("PartWorkbench")
    select("A")
    assert Gui.activeWorkbench().name() == "PartWorkbench", "a body switched the workbench"
    Gui.Control.showDialog(taskpanels.ItemPanel(mat))
    select(study.ExcitationsGroup.Name)
    assert Gui.activeWorkbench().name() == "PartWorkbench", "switched during an edit"
    Gui.Control.closeDialog()
    select(study.ExcitationsGroup.Name)
    assert Gui.activeWorkbench().name() == "EMSolutionWorkbench", Gui.activeWorkbench().name()
    assert list(shown_folders()) == ["Excitations"], list(shown_folders())
    log.append("workbench switch ok")

    dialog = taskpanels.IdTableDialog(study)
    assert [r[2] for r in dialog.rows] == ["Iron_A", "Iron_B", "Terminal_In_A"], dialog.rows
    dialog.table.item(0, 2).setText("7")
    assert study.VolumeIds["A"] == "7"
    log.append("id table ok")

    run = runner.start(study)
    assert run is not None, "start failed"
    assert run.proc.waitForFinished(120000), "mesher timed out"
    App.Gui.updateGui()
    assert not runner.busy(), "run did not finish"
    assert run.error == "", run.error
    assert study.MeshResult is not None and study.MeshResult.FemMesh.VolumeCount > 0
    log.append(f"mesh ok: {study.MeshResult.FemMesh.VolumeCount} volumes")
    App.closeDocument(doc.Name)


try:
    main()
    log.append("PASS")
except Exception:
    log.append(traceback.format_exc())
    log.append("FAIL")
with open(RESULT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(log) + "\n")
os._exit(0)
