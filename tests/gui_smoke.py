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
    Gui.runCommand("EMS_Material")
    Gui.runCommand("EMS_MeshSize")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A", "Face1")
    Gui.runCommand("EMS_Excitation")
    mat, = objects.materials(study)
    exc, = objects.excitations(study)
    size, = objects.mesh_sizes(study)
    assert [b.Name for b in mat.References] == ["A", "B"], mat.References
    assert exc.References == [(doc.A, ("Face1",))], exc.References
    assert size.Size.Value == 3.0
    log.append("commands ok")

    panel = taskpanels.ItemPanel(mat)
    panel.name.setText("Iron")
    panel.refs.item(1).setSelected(True)
    panel.remove()
    Gui.Control.showDialog(panel)
    panel.accept()
    assert mat.Label == "Iron" and [b.Name for b in mat.References] == ["A"]
    mat.References = [doc.A, doc.B]
    log.append("panel ok")

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
