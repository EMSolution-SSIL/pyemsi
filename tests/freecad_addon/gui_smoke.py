r"""GUI smoke test: runs inside FreeCAD, drives the commands, runs a mesh, then quits.

Needs the addon linked into a throwaway FreeCAD profile (PowerShell, repo root):
    $h = "$env:TEMP\ems_fc_home"; New-Item -ItemType Directory -Force "$h\Mod" | Out-Null
    if (-not (Test-Path "$h\Mod\EMSolution")) { New-Item -ItemType Junction -Path "$h\Mod\EMSolution" -Target "$PWD\freecad_addon" | Out-Null }
    $env:FREECAD_USER_HOME = $h
    Start-Process -Wait "$env:LOCALAPPDATA\Programs\FreeCAD 1.1\bin\FreeCAD.exe" tests\freecad_addon\gui_smoke.py
    Get-Content "$env:TEMP\ems_gui_smoke.txt"
The last line of the result file is "PASS" or "FAIL". FreeCAD may report a crash on quit after that.
For the pixi env's FreeCAD 1.1.0, replace the Start-Process line with
    pixi run freecad tests\freecad_addon\gui_smoke.py
"""

import os
import tempfile
import traceback

RESULT = os.path.join(tempfile.gettempdir(), "ems_gui_smoke.txt")
log = []


def main():
    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide import QtWidgets

    Gui.activateWorkbench("EMSolutionWorkbench")  # loaded by FreeCAD from the Mod folder
    # FreeCAD 1.1.0 started from a script keeps the Tasks dock hidden in the overlay (by hand it shows),
    # so take the docks out of the overlay. 1.1.4 doesn't need it.
    mw = Gui.getMainWindow()
    tasks = mw.findChild(QtWidgets.QDockWidget, "Tasks")
    if App.Version()[:3] == ["1", "1", "0"] and tasks.parent() is not mw:
        Gui.runCommand("Std_DockOverlayAll", 0)
        Gui.updateGui()
    from emsolution import commands, objects, runner, taskpanels

    commands.ask_text = lambda title, label, default: {"Material": "Copper", "Excitation": "Terminal In"}[title]
    commands.ask_size = lambda default: 3.0
    commands.ask_study = lambda: ("Study", "3D")

    doc = App.newDocument("Smoke")
    for name, x in (("A", 0), ("B", 10)):
        box = doc.addObject("Part::Box", name)
        box.Placement.Base = App.Vector(x, 0, 0)
    doc.recompute()

    Gui.runCommand("EMS_NewStudy")
    study = objects.find_study(doc)
    assert study is not None, "no study"
    assert study.MainMode == "Unassigned"
    study.MainMode = "Materials"  # legacy workflow remains supported
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
    (mat,) = objects.materials(study)
    (exc,) = objects.excitations(study)
    size, fine = objects.mesh_sizes(study)
    assert [b.Name for b in mat.References] == ["A", "B"], mat.References
    assert exc.References == [(doc.A, ("Face1",))], exc.References
    assert size.Size.Value == 3.0
    assert size.References == [(doc.A, ("",)), (doc.B, ("",))], size.References
    assert fine.References == [(doc.A, ("Edge1",)), (doc.B, ("Vertex8",))], fine.References
    for item in (mat, exc, size, fine):  # the tree would grey them out as hidden
        assert item.ViewObject.isVisible(), item.Name
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, mat.Name)
    Gui.runCommand("Std_ToggleVisibility")
    for _ in range(3):  # shown again from a timer
        Gui.updateGui()
    assert mat.ViewObject.isVisible(), "the eye hid an item"
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

    def task_buttons():
        boxes = Gui.getMainWindow().findChildren(QtWidgets.QDialogButtonBox)
        return sorted(b.text().replace("&", "") for box in boxes if box.isVisible() for b in box.buttons())

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
        return {
            first_column[t.horizontalHeaderItem(0).text()]: t
            for t in tables
            if t.isVisible() and t.horizontalHeaderItem(0).text() in first_column
        }

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

    select(study.Name)
    assert not any(
        w.isVisible() and w.title() == "Advanced mesh settings"
        for w in Gui.getMainWindow().findChildren(QtWidgets.QGroupBox)
    )
    select(study.MeshSizesGroup.Name)
    (advanced,) = [
        w
        for w in Gui.getMainWindow().findChildren(QtWidgets.QGroupBox)
        if w.isVisible() and w.title() == "Advanced mesh settings"
    ]
    assert advanced.isChecked(), "Gmsh options are collapsed by default"
    (combo,) = [
        c for c in Gui.getMainWindow().findChildren(QtWidgets.QComboBox) if c.isVisible() and c.findText("HXT") >= 0
    ]
    combo.setCurrentText("HXT")
    (factor,) = [
        s for s in Gui.getMainWindow().findChildren(QtWidgets.QDoubleSpinBox) if s.isVisible() and s.suffix() == ""
    ]
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

    from emsolution import highlight

    shown_refs = []
    real_show = highlight.show

    def spy_show(refs):
        shown_refs.append(sorted((b.Name, s) for b, s in refs))
        real_show(refs)

    highlight.show = spy_show

    def drawn():
        """Coin shapes drawn by the highlight: IndexedFaceSet, LineSet, PointSet."""
        n = highlight.shown()
        if n is None:
            return []
        assert Gui.getDocument(doc.Name).activeView().getSceneGraph().findChild(n) >= 0
        return [n.getChild(i).getChild(2).getTypeId().getName().getString() for i in range(2, n.getNumChildren())]

    select(mat.Name)
    assert shown_refs[-1] == [("A", ""), ("B", "")], shown_refs
    assert drawn() == ["IndexedFaceSet"], drawn()
    select(fine.Name)
    assert shown_refs[-1] == [("A", "Edge1"), ("B", "Face2"), ("B", "Vertex8")], shown_refs
    assert drawn() == ["IndexedFaceSet", "LineSet", "PointSet"], drawn()
    select("A")
    assert drawn() == [], "highlight kept for a body"
    select(study.ExcitationsGroup.Name)
    assert drawn() == [], "highlight shown for a folder"
    shown_folders()["Excitations"].selectRow(0)
    assert shown_refs[-1] == [("A", "Face1")] and drawn() == ["IndexedFaceSet"], shown_refs
    select(study.MaterialsGroup.Name)
    shown_folders()["Materials"].selectRow(1)
    assert shown_refs[-1] == [("B", "")], shown_refs
    shown_folders()["Materials"].cellDoubleClicked.emit(1, 0)
    for _ in range(5):
        Gui.updateGui()
    assert drawn() == [], "highlight kept during an edit"
    Gui.Control.closeDialog()
    highlight.show = real_show
    log.append("highlight ok")

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
    assert [r[2] for r in dialog.rows] == ["A", "B", "Terminal_In_A"], dialog.rows
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

    # Several Studies: ownership, setup controls, bulk selection and undo.
    import Part
    from emsolution import geometry

    commands.ask_study = lambda: ("Cross-section", "2D")
    Gui.runCommand("EMS_NewStudy")
    for _ in range(5):
        Gui.updateGui()
    first, second = objects.studies(doc)
    assert first == study and second.Dimension == "2D"
    assert commands.active_study() == second
    assert not commands.COMMANDS["EMS_Material"].IsActive()
    assert not commands.COMMANDS["EMS_RunMesh"].IsActive()
    assert taskpanels.FolderView(second.MaterialsGroup).rows == []
    source = doc.addObject("App::DocumentObjectGroup", "FaceGroup")
    section = doc.addObject("Part::Feature", "Section")
    section.Shape = Part.makePlane(10, 10)
    source.addObject(section)
    part = doc.addObject("App::Part", "SolidPart")
    part.addObject(doc.A)
    doc.recompute()
    view = taskpanels.StudyView(second)
    combo = view.regions["Main"][1]
    assert combo.findData("source:" + source.Name) >= 0 and combo.findData("source:" + part.Name) >= 0
    named_manual = doc.addObject("App::DocumentObjectGroup", "Manual")
    view.refresh()
    combo.setCurrentIndex(combo.findData("source:" + named_manual.Name))
    assert second.MainMode == "Container" and second.MainSource == named_manual
    undo_before = list(doc.UndoNames)
    view.refresh()
    assert list(doc.UndoNames) == undo_before, "populating widgets changed the model"
    combo.setCurrentIndex(combo.findData("source:" + source.Name))
    assert second.MainSource == source and second.MainMode == "Container"
    assert "1 face region" in view.regions["Main"][2].text()
    assert not view.run_button.isEnabled()
    view.movement.setCurrentText("Sliding motion")
    assert second.Movement == "Sliding motion" and study.Movement == "No movement"
    assert view.regions["Moving"][0].isHidden() is False
    select(study.MaterialsGroup.Name)
    assert commands.active_study() == study
    select("B")
    assert commands.active_study() == study, "geometry selection lost the target Study"
    select(study.Name, second.Name)
    assert commands.active_study() is None, "ambiguous Study selection picked a target"
    select("B")
    assert commands.active_study() is None, "ambiguous target was silently remembered"
    select(second.Name)
    manual = taskpanels.GeometryPanel(second, "Main", editable=True)
    Gui.Control.showDialog(manual)
    select(source.Name, section.Name)
    manual.add_selection()
    assert manual.current == [section], "bulk container selection duplicated a face"
    manual.reject()
    assert second.MainMode == "Container", "Cancel changed the saved geometry"
    manual = taskpanels.GeometryPanel(second, "Main", editable=True)
    Gui.Control.showDialog(manual)
    select(source.Name)
    manual.add_selection()
    manual.accept()
    assert second.MainMode == "Manual" and second.MainObjects == [section]
    doc.undo()
    assert second.MainMode == "Container" and second.MainObjects == []
    doc.redo()
    assert second.MainMode == "Manual" and second.MainObjects == [section]
    assert study.MainMode == "Materials"
    select(second.Name)
    assert second.ViewObject.Proxy.doubleClicked(second.ViewObject)
    assert not Gui.Control.activeDialog(), "double-click Study opened the ID dialog"
    log.append("multiple Study setup and undo ok")

    # The selected folder's settings stay isolated and targeting cannot cross documents.
    view = taskpanels.FolderView(study.MeshSizesGroup)
    view.settings.factor.setValue(0.7)
    assert study.MeshSizesGroup.SizeFactor == 0.7
    assert second.MeshSizesGroup.SizeFactor == 1.0
    second_settings = taskpanels.FolderView(second.MeshSizesGroup)
    assert not second_settings.settings.box.isEnabled()
    inspect = taskpanels.GeometryPanel(second, "Main")
    Gui.Control.showDialog(inspect)
    inspect.refs.item(0).setSelected(True)
    assert highlight.shown() is not None
    inspect.reject()
    assert highlight.shown() is None
    select(second.Name)
    (actual_combo,) = [
        c
        for c in Gui.getMainWindow().findChildren(QtWidgets.QComboBox)
        if c.isVisible() and c.objectName() == "MainGeometry"
    ]
    actual_combo.setCurrentIndex(actual_combo.findData("source:" + source.Name))
    Gui.activeDocument().activeView().viewTop()
    Gui.activeDocument().activeView().fitAll()
    Gui.updateGui()
    Gui.getMainWindow().grab().save(os.path.join(tempfile.gettempdir(), "study-setup.png"))
    another_doc = App.newDocument("Other")
    other_study = objects.make_study(another_doc)
    assert commands.active_study() == other_study
    App.closeDocument(another_doc.Name)
    App.setActiveDocument(doc.Name)
    select(second.Name)
    name = second.Name
    doc.removeObject(name)
    select("B")
    assert commands.active_study() == study, "deleted Study remained the target"
    Gui.activateWorkbench("PartWorkbench")
    Gui.activateWorkbench("EMSolutionWorkbench")
    select(study.Name)
    assert not geometry.export_unavailable(study)
    study.MainMode, study.MainSource = "Container", part
    view = taskpanels.StudyView(study)
    assert commands.COMMANDS["EMS_RunMesh"].IsActive()
    assert view.run_button.isEnabled()
    mat.References = [doc.B]
    view.refresh()
    assert "A (A)" in view.diagnostics.text()
    assert view.run_button.isEnabled(), "missing materials disabled generation"
    mat.References = [doc.A, doc.B]
    view.refresh()
    run = runner.start(study)
    assert run is not None and run.proc.waitForFinished(120000)
    Gui.updateGui()
    assert run.error == "" and not runner.busy()
    import json

    with open(run.job, encoding="utf-8") as fh:
        selected_job = json.load(fh)
    assert [v["name"] for v in selected_job["volumes"]] == ["A"]
    assert study.MeshResult.FemMesh.VolumeCount > 0
    log.append("selected geometry mesh and missing-material validation ok")
    log.append("Study isolation and lifecycle ok")
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
