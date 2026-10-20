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
    from emsolution import jobwriter
    from emsolution import highlight

    commands.ask_text = lambda title, label, default: {"Excitation": "Terminal In"}[title]
    asked = []  # bodies the Assign dialog was opened for; the modal dialog is driven directly below
    taskpanels.ask_assignment = lambda study, bodies: asked.append([b.Name for b in bodies])
    warned = []  # commands' warnings; panels' warnings go to the log as "refused: ..."
    commands.warn = lambda text: warned.append(text)
    taskpanels.warn = lambda text: log.append("refused: " + text)
    opened = []  # panels the mesh commands opened for their new item

    class RecordedPanel(taskpanels.ItemPanel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            opened.append(self)

    taskpanels.ItemPanel = RecordedPanel

    def ok(size=None, elements=None):
        panel = opened.pop()
        assert panel.new and Gui.Control.activeDialog()
        if size is not None:
            panel.size.setValue(size)
        if elements is not None:
            panel.elements.setValue(elements)
        assert panel.accept()

    commands.ask_study = lambda: ("Study", "3D")

    doc = App.newDocument("Smoke")
    for name, x in (("A", 0), ("B", 10), ("Outside", 40)):  # Outside never joins the main geometry
        box = doc.addObject("Part::Box", name)
        box.Placement.Base = App.Vector(x, 0, 0)
    doc.recompute()

    Gui.runCommand("EMS_NewStudy")
    study = objects.find_study(doc)
    assert study is not None, "no study"
    assert study.MainMode == "Unassigned"
    for folder in (study.MaterialsGroup, study.ExcitationsGroup, study.MeshSizesGroup):
        view = taskpanels.FolderView(folder)  # keep it: its widgets go with it
        texts = [w.text() for w in view.form.findChildren(QtWidgets.QLabel)]
        assert objects.NO_MAIN_GEOMETRY in texts and not any(t.startswith("Only assignments") for t in texts), texts
    for name, sub in (("EMS_Material", ""), ("EMS_Excitation", "Face1"), ("EMS_MeshSize", "Face1")):
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(doc.Name, "A", sub)
        Gui.runCommand(name)
        assert warned[-1:] == [objects.NO_MAIN_GEOMETRY], (name, warned)
        assert [o.Name for o in Gui.Selection.getSelection()] == [study.Name], (name, "the Study was not selected")
    assert not asked and not objects.excitations(study) and not objects.mesh_sizes(study), "assigned without geometry"
    study.MainMode, study.MainObjects = "Manual", [doc.A, doc.B]
    outside_message = (
        "Not in the Study's main geometry: Outside. Add them to it in the Study panel or select other bodies."
    )
    for name, sub in (("EMS_Material", ""), ("EMS_Excitation", "Face1"), ("EMS_MeshSize", "")):
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(doc.Name, "A", sub)
        Gui.Selection.addSelection(doc.Name, "Outside", sub)
        Gui.runCommand(name)
        assert warned[-1:] == [outside_message], (name, warned)
    assert not asked and not objects.excitations(study) and not objects.mesh_sizes(study), "assigned outside geometry"
    log.append("main geometry gate ok")
    doc.saveAs(os.path.join(tempfile.mkdtemp(), "Smoke.FCStd"))  # the simulation folder
    log.append("study ok")

    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A")
    Gui.Selection.addSelection(doc.Name, "B")
    Gui.Selection.addSelection(doc.Name, study.MaterialsGroup.Name)  # must be ignored
    Gui.runCommand("EMS_Material")
    Gui.runCommand("EMS_MeshSize")
    ok(size=3.0)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A", "Face1")
    Gui.runCommand("EMS_Excitation")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A", "Edge1")
    Gui.Selection.addSelection(doc.Name, "B", "Vertex8")
    Gui.runCommand("EMS_MeshSize")
    ok(size=3.0)
    Gui.Selection.clearSelection()
    Gui.runCommand("EMS_MeshSize")  # nothing selected: the panel opens empty
    panel = opened.pop()
    assert panel.refs.count() == 0 and not panel.accept(), "an empty item was made"
    assert log[-1].startswith("refused: Select geometry"), log[-1]
    panel.add_selection()
    assert log[-1].startswith("refused: Nothing is selected"), log[-1]
    hint = "Click faces, edges or vertices in the 3D view, or a solid in the tree."
    assert any(w.text().startswith(hint) for w in panel.form.findChildren(QtWidgets.QLabel)), "no 3D hint"
    for name in (study.Name, "Outside"):  # the gate: not geometry, not main geometry
        Gui.Selection.addSelection(doc.Name, name)
    assert Gui.Selection.getSelection() == [], "the gate let a pick through"
    Gui.Selection.addSelection(doc.Name, "A", "Face1")
    panel.add_selection()
    panel.add_selection()
    assert log[-1].startswith("refused: Nothing new to add"), log[-1]
    assert panel.refs.count() == 1, panel.refs.count()
    panel.refs.item(0).setSelected(True)
    assert highlight.shown() is not None, "the selected row is not highlighted"
    panel.reject()
    assert highlight.shown() is None, "Cancel kept the highlight"
    assert len(objects.mesh_sizes(study)) == 2, "Cancel kept the new item"
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "Outside")
    assert [o.Name for o in Gui.Selection.getSelection()] == ["Outside"], "Cancel kept the gate"
    Gui.Selection.clearSelection()
    assert asked == [["A", "B"]], asked
    assert objects.materials(study) == [], "the command assigned before the dialog"
    (exc,) = objects.excitations(study)
    size, fine = objects.mesh_sizes(study)
    assert exc.References == [(doc.A, ("Face1",))], exc.References
    assert size.Size.Value == 3.0
    assert size.References == [(doc.A, ("",)), (doc.B, ("",))], size.References
    assert fine.References == [(doc.A, ("Edge1",)), (doc.B, ("Vertex8",))], fine.References
    for item in (exc, size, fine):  # the tree would grey them out as hidden
        assert item.ViewObject.isVisible(), item.Name
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, exc.Name)
    Gui.runCommand("Std_ToggleVisibility")
    for _ in range(3):  # shown again from a timer
        Gui.updateGui()
    assert exc.ViewObject.isVisible(), "the eye hid an item"
    log.append("commands ok")

    Gui.Selection.addSelection(doc.Name, "Outside")  # selected before the panel: the gate does not drop it
    panel = taskpanels.ItemPanel(fine)
    Gui.Selection.addSelection(doc.Name, "B", "Face2")
    Gui.Selection.addSelection(doc.Name, "A")
    panel.add_selection()
    assert log[-1] == "refused: " + outside_message, log[-1]
    Gui.Control.showDialog(panel)
    panel.accept()
    Gui.Selection.addSelection(doc.Name, study.Name)
    assert study in Gui.Selection.getSelection(), "OK kept the gate"
    Gui.Selection.clearSelection()
    refs = {(b.Name, s) for b, subs in fine.References for s in subs}
    assert refs == {("A", "Edge1"), ("A", ""), ("B", "Vertex8"), ("B", "Face2")}, refs
    fine.References = [(doc.A, "Edge1"), (doc.B, "Vertex8"), (doc.B, "Face2")]
    log.append("mesh size panel ok")

    def task_buttons():
        boxes = Gui.getMainWindow().findChildren(QtWidgets.QDialogButtonBox)
        return sorted(b.text().replace("&", "") for box in boxes if box.isVisible() for b in box.buttons())

    def select(*names):
        Gui.Selection.clearSelection()
        for name in names:
            Gui.Selection.addSelection(doc.Name, name)
        for _ in range(5):  # the watcher panel and the workbench switch follow the selection
            Gui.updateGui()

    first_column = {
        "Name": "Material Library",
        "Body": "Materials",
        "Excitation": "Excitations",
        "Mesh size": "Mesh Sizes",
        "Air region": "Air Regions",
    }

    def shown_folders():
        """{folder name: table} for the folder panels visible in the Tasks tab."""
        tables = Gui.getMainWindow().findChildren(QtWidgets.QTableWidget)
        return {
            first_column[t.horizontalHeaderItem(0).text()]: t
            for t in tables
            if t.isVisible() and t.horizontalHeaderItem(0).text() in first_column
        }

    rows = {"Material Library": 0, "Materials": 2, "Excitations": 1, "Mesh Sizes": 2, "Air Regions": 0}
    for folder in (
        study.MaterialLibraryGroup,
        study.MaterialsGroup,
        study.ExcitationsGroup,
        study.MeshSizesGroup,
        study.AirRegionsGroup,
    ):
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
    assert asked[-1] == ["B"], ("Assign dialog not asked for the row's body", asked)
    select(study.ExcitationsGroup.Name)
    shown_folders()["Excitations"].cellDoubleClicked.emit(0, 0)
    for _ in range(5):
        Gui.updateGui()
    assert task_buttons() == ["Cancel", "OK"], ("item panel did not open from the row", task_buttons())
    assert shown_folders() == {}, "folder panel shown beside the edit dialog"
    Gui.Control.closeDialog()
    for _ in range(5):
        Gui.updateGui()
    assert list(shown_folders()) == ["Excitations"], "folder panel not back after the edit"
    from emsolution import materialstandins, studymaterials
    from ems_material import JsonMaterialRepository, MaterialManager, material_from_dict

    def record(material_id, name):
        return material_from_dict(
            {
                "schema": "ems_material",
                "schema_version": "1.0",
                "material_id": material_id,
                "material_version": "1.0.0",
                "identity": {
                    "name": name,
                    "family": "generic",
                    "manufacturer": None,
                    "grade": None,
                    "description": None,
                    "aliases": [],
                    "tags": [],
                },
                "properties": {
                    "electromagnetic": {"relative_permeability": {"type": "scalar", "value": 1, "unit": "1"}}
                },
                "provenance": {"source_type": "USER_INPUT", "reference": None, "date": None, "notes": None},
                "version_metadata": {"author": "smoke", "updated_at": "2026-10-13T00:00:00+00:00", "change_note": "x"},
            }
        )

    root = tempfile.mkdtemp()
    master = JsonMaterialRepository(root)
    master.create(record("user:air", "Air"))
    master.create(record("user:iron", "Iron"))
    (lib,) = studymaterials.import_materials(study, [record("user:air", "Air")])
    assert isinstance(lib.ViewObject.Proxy, taskpanels.ViewProviderLibraryMaterial)
    picker = materialstandins.MaterialPicker(MaterialManager(repository=master), {"user:air"})
    items = [picker.list.item(i) for i in range(picker.list.count())]
    disabled = [i.text() for i in items if not i.flags() & taskpanels.QtCore.Qt.ItemIsEnabled]
    assert len(items) == 2 and len(disabled) == 1 and disabled[0].startswith("Air"), [i.text() for i in items]
    next(i for i in items if i.text().startswith("Iron")).setSelected(True)
    assert [m.material_id for m in picker.selected()] == ["user:iron"]
    picker.reject()
    window = materialstandins.open_editor(study, "user:air")
    assert window.isVisible() and materialstandins.open_editor(study) is window
    window.close()
    dialog = taskpanels.AssignDialog(study, [doc.A, doc.B])
    assert dialog.material.currentData() == lib.Name, "an unassigned body did not default to the first material"
    dialog.potential.setValue(2)
    dialog.accept()
    mat, mat_b = objects.materials(study)
    assert (mat.Body, mat.LibraryMaterial, mat.Potential, mat.Label) == (doc.A, lib, 2, "A: Air"), mat.Label
    assert doc.UndoNames[0] == "Assign material", doc.UndoNames
    dialog = taskpanels.AssignDialog(study, [doc.B])
    assert (dialog.material.currentData(), dialog.potential.value()) == (lib.Name, 2)
    dialog.material.setCurrentIndex(dialog.material.findData(""))
    dialog.accept()
    assert objects.materials(study) == [mat] and doc.UndoNames[0] == "Remove material", doc.UndoNames
    doc.undo()
    assert [m.Body for m in objects.materials(study)] == [doc.A, doc.B], "undo did not bring the assignment back"
    materials_view = taskpanels.FolderView(study.MaterialsGroup)
    assert materials_view.missing.isHidden(), materials_view.missing.text()
    taskpanels.apply_assignment(study, [doc.B], None, 0)
    materials_view.fill()
    missing = materials_view.missing
    assert not missing.isHidden() and missing.text().endswith(": B"), (missing.isHidden(), missing.text())
    doc.undo()
    materials_view.fill()
    assert materials_view.missing.isHidden(), "stale No material line after assigning"
    select(study.MaterialsGroup.Name)
    shown_folders()["Materials"].selectAll()
    (assign_button,) = [
        b for b in Gui.getMainWindow().findChildren(QtWidgets.QPushButton) if b.isVisible() and b.text() == "Assign…"
    ]
    assign_button.click()
    assert asked[-1] == ["A", "B"], asked
    extra = doc.addObject("Part::Box", "Extra")
    doc.recompute()
    dialog = taskpanels.AssignDialog(study, [extra])
    dialog.material.setCurrentIndex(dialog.material.findData(""))
    dialog.accept()
    assert objects.assignment_of(study).get("Extra") is None
    dialog = taskpanels.AssignDialog(study, [extra])  # the first library material
    dialog.accept()
    assert objects.assignment_of(study).get("Extra") is None, "assigned a body outside the main geometry"
    assert log[-1].startswith("refused: Not in the Study's main geometry: Extra"), log[-1]
    dialog.reject()
    doc.removeObject("Extra")
    select(study.MaterialLibraryGroup.Name)
    assert shown_folders()["Material Library"].item(0, 3).text() == "A, B"
    taskpanels.warn = lambda text: log.append("refused: " + text)
    assert lib.ViewObject.Proxy.onDelete(lib.ViewObject, []) is False, "deleted a used material"
    assert objects.library_materials(study) == [lib]
    library_view = taskpanels.FolderView(study.MaterialLibraryGroup)
    dead_view = taskpanels.FolderView(study.MaterialLibraryGroup)
    from shiboken6 import Shiboken

    Shiboken.delete(dead_view.form)  # its widgets are gone, the Python object is not
    other_doc = App.newDocument("OtherLibrary")
    closed_view = taskpanels.FolderView(objects.make_study(other_doc).MaterialLibraryGroup)
    App.closeDocument(other_doc.Name)
    App.setActiveDocument(doc.Name)
    repository = studymaterials.StudyMaterialRepository(study, on_change=taskpanels.refresh_library_views)
    repository.create(record("user:iron", "Iron"))  # on_change refreshes every open library panel
    assert library_view.table.rowCount() == 2, library_view.table.rowCount()
    repository.delete("user:iron")
    assert library_view.table.rowCount() == 1, library_view.table.rowCount()
    undo_before = list(doc.UndoNames)
    library_view.delete_materials()  # nothing selected
    assert list(doc.UndoNames) == undo_before, doc.UndoNames
    assert dead_view not in taskpanels._library_views and closed_view not in taskpanels._library_views
    labels = [w.text() for w in library_view.form.findChildren(QtWidgets.QLabel)]
    assert not any(t.startswith("Only assignments") for t in labels), labels
    excitations_view = taskpanels.FolderView(study.ExcitationsGroup)
    assert excitations_view.table.horizontalHeaderItem(3).text() == "SMAT_ID"
    labels = [w.text() for w in excitations_view.form.findChildren(QtWidgets.QLabel)]
    assert any(t.startswith("Only assignments") for t in labels), labels
    log.append("folder notices and headers ok")

    # Change Material Manager root: only a folder with manager.config.json is remembered (no real dialogs).
    os.environ["EMS_MATERIAL_MANAGER_SETTINGS_PATH"] = os.path.join(tempfile.mkdtemp(), "settings.json")
    os.environ.pop("EMS_MATERIAL_MANAGER_ROOT", None)
    not_root, manager_root = tempfile.mkdtemp(), tempfile.mkdtemp()
    with open(os.path.join(manager_root, "manager.config.json"), "w", encoding="utf-8") as fh:
        fh.write("{}")
    picked = []
    real_get_directory = QtWidgets.QFileDialog.getExistingDirectory
    QtWidgets.QFileDialog.getExistingDirectory = staticmethod(lambda *args, **kwargs: picked.pop(0))
    try:
        (change,) = [
            b for b in library_view.form.findChildren(QtWidgets.QPushButton) if b.text().startswith("Change Material")
        ]
        picked.append(not_root)
        change.click()
        assert log[-1].startswith("refused: Not a Material Manager root"), log[-1]
        assert studymaterials.library_root() is None, "remembered a folder without manager.config.json"
        picked.append(not_root)
        assert materialstandins.pick_materials(study, library_view.form) == []
        assert studymaterials.library_root() is None
        picked.append(manager_root)
        change.click()
        assert os.path.samefile(studymaterials.library_root(), manager_root)
        picked.append(not_root)
        change.click()  # a wrong pick keeps the good root
        assert os.path.samefile(studymaterials.library_root(), manager_root)
        assert picked == [], picked
    finally:
        QtWidgets.QFileDialog.getExistingDirectory = real_get_directory
    log.append("manager root ok")

    # A closed document's Names are reused: the editor must not reuse the old window.
    reused = App.newDocument("Reused")
    reused_study = objects.make_study(reused)
    studymaterials.import_materials(reused_study, [record("user:air", "Air")])
    old_window = materialstandins.open_editor(reused_study)
    App.closeDocument(reused.Name)
    reused = App.newDocument("Reused")
    assert reused.Name == "Reused", reused.Name
    reused_study = objects.make_study(reused)
    studymaterials.import_materials(reused_study, [record("user:iron", "Iron")])
    new_window = materialstandins.open_editor(reused_study)
    for _ in range(5):
        Gui.updateGui()
    taskpanels.QtCore.QCoreApplication.sendPostedEvents(None, taskpanels.QtCore.QEvent.DeferredDelete)
    assert new_window is not old_window, "reused a closed document's editor"
    assert list(new_window._material_items) == ["user:iron"], list(new_window._material_items)
    assert materialstandins.open_editor(reused_study) is new_window
    new_window.close()
    App.closeDocument(reused.Name)
    App.setActiveDocument(doc.Name)
    log.append("editor after document reuse ok")
    log.append("material library ok")
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
    assert shown_refs[-1] == [("A", "")], shown_refs
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
    highlight.show = real_show
    log.append("highlight ok")

    Gui.activateWorkbench("PartWorkbench")
    select("A")
    assert Gui.activeWorkbench().name() == "PartWorkbench", "a body switched the workbench"
    exc_panel = taskpanels.ItemPanel(exc)
    Gui.Control.showDialog(exc_panel)
    select(study.ExcitationsGroup.Name)
    assert Gui.activeWorkbench().name() == "PartWorkbench", "switched during an edit"
    exc_panel.reject()
    select(study.ExcitationsGroup.Name)
    assert Gui.activeWorkbench().name() == "EMSolutionWorkbench", Gui.activeWorkbench().name()
    assert list(shown_folders()) == ["Excitations"], list(shown_folders())
    log.append("workbench switch ok")

    dialog = taskpanels.IdTableDialog(study)
    assert [r[2] for r in dialog.rows] == ["A", "B", "Terminal_In_A"], dialog.rows
    dialog.table.item(0, 2).setText("7")
    assert study.MatIds["A"] == "7"
    log.append("id table ok")

    run = runner.start(study)
    assert run is not None, "start failed"
    assert run.proc.waitForFinished(120000), "mesher timed out"
    App.Gui.updateGui()
    assert not runner.busy(), "run did not finish"
    assert run.error == "", run.error
    assert study.MeshResult is not None and study.MeshResult.FemMesh.VolumeCount > 0
    assert os.path.isfile(jobwriter.mesh_file(study)), "no pre_geom.msh beside the document"
    assert os.path.isfile(os.path.join(jobwriter.scratch_folder(study), "mesh.unv"))
    assert not run.replaced
    log.append(f"mesh ok: {study.MeshResult.FemMesh.VolumeCount} volumes")

    validations = []  # panels the Validate command opened

    class RecordedValidation(taskpanels.ValidationPanel):
        def __init__(self, *args, **kwargs):
            validations.append(self)  # before run(), which starts the geometry check
            super().__init__(*args, **kwargs)

    taskpanels.ValidationPanel = RecordedValidation
    assert commands.COMMANDS["EMS_Validate"].IsActive()
    Gui.runCommand("EMS_Validate")
    (checking,) = validations
    check = runner._run
    assert check is not None and check.proc.waitForFinished(120000), "geometry check timed out"
    App.Gui.updateGui()
    assert not runner.busy(), "geometry check did not finish"
    rows = [checking.list.item(i).text() for i in range(checking.list.count())]
    assert any(r.startswith("The mesher's geometry checks passed") for r in rows), rows
    checking.list.setCurrentRow(0)  # selecting a row must not crash
    App.Gui.updateGui()
    checking.reject()
    App.Gui.updateGui()
    assert not Gui.Control.activeDialog()
    log.append(f"validate ok: {len(rows)} rows")

    # Air Region: command, panel, view, folder, picks and mesh.
    import json

    console = []
    real_print = App.Console.PrintMessage
    App.Console.PrintMessage = lambda text: (console.append(text), real_print(text))
    air_panels = []  # panels the Air Region command and its double-click opened

    class RecordedAirPanel(taskpanels.AirRegionPanel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            air_panels.append(self)

    taskpanels.AirRegionPanel = RecordedAirPanel
    select(study.Name)
    assert commands.COMMANDS["EMS_AddAirRegion"].IsActive()
    Gui.runCommand("EMS_AddAirRegion")
    panel = air_panels.pop()
    assert panel.new and Gui.Control.activeDialog(), "the Air Region panel did not open"
    (air,) = objects.air_regions(study)
    assert isinstance(air.ViewObject.Proxy, taskpanels.ViewProviderAir)
    assert (air.ViewObject.Transparency, air.ViewObject.DisplayMode) == (80, "Flat Lines")
    for body in (doc.A, doc.B):
        assert air.Shape.BoundBox.isInside(body.Shape.BoundBox), "the Air Region does not enclose " + body.Name
    assert [panel.shape.itemText(i) for i in range(panel.shape.count())] == ["Box", "Sector", "Custom"]
    assert panel.groups["Sector"].isHidden() and not panel.groups["Box"].isHidden()
    panel.shape.setCurrentIndex(panel.shape.findData("Sector"))
    assert not panel.groups["Sector"].isHidden() and panel.groups["Box"].isHidden()
    panel.shape.setCurrentIndex(panel.shape.findData("Box"))
    assert panel.reject()
    assert objects.air_regions(study) == [] and not Gui.Control.activeDialog(), "Cancel kept the new Air Region"
    Gui.runCommand("EMS_AddAirRegion")
    panel = air_panels.pop()
    panel.padding.setValue(100)
    panel.fit()
    assert abs(panel.size["Length"].value() - 60) < 1e-6, panel.size["Length"].value()  # 20 mm of bodies, +100 % a side
    assert panel.accept() and not Gui.Control.activeDialog()
    (air,) = objects.air_regions(study)
    assert abs(air.Length.Value - 60) < 1e-6 and air.Shape.BoundBox.isInside(doc.B.Shape.BoundBox)
    assert air.ViewObject.Proxy.doubleClicked(air.ViewObject)
    panel = air_panels.pop()
    assert not panel.new and Gui.Control.activeDialog()
    panel.size["Length"].setValue(70)
    assert panel.accept() and abs(air.Length.Value - 70) < 1e-6 and doc.UndoNames[0].startswith("Edit Air"), (
        doc.UndoNames
    )
    Gui.runCommand("EMS_AddAirRegion")
    assert warned[-1] == "This Study already has an Air Region." and not air_panels, warned
    select(study.AirRegionsGroup.Name)
    assert shown_folders()["Air Regions"].rowCount() == 1
    shown_folders()["Air Regions"].cellDoubleClicked.emit(0, 0)
    assert air_panels.pop().reject() and not Gui.Control.activeDialog()
    # Air is not an Excitation pick; Mesh Size picks of it and its faces stay allowed.
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, air.Name, "Face1")
    Gui.runCommand("EMS_Excitation")
    assert warned[-1].startswith("An Air Region cannot") and len(objects.excitations(study)) == 1, warned[-1]
    panel = taskpanels.ItemPanel(exc)
    opened.pop()
    Gui.Control.showDialog(panel)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, air.Name, "Face1")
    assert Gui.Selection.getSelection() == [], "the Excitation gate let the Air Region through"
    panel.reject()
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, air.Name)
    Gui.runCommand("EMS_MeshSize")
    assert opened[-1].current == [(air, "")], opened[-1].current
    Gui.Selection.addSelection(doc.Name, air.Name, "Face1")
    assert Gui.Selection.getSelection() == [air], "the Mesh Size gate refused the Air Region"
    ok(size=4.0)
    air_size = objects.mesh_sizes(study)[-1]
    run = runner.start(study)
    assert run is not None and run.proc.waitForFinished(120000), "mesher timed out"
    Gui.updateGui()
    assert run.error == "" and not runner.busy(), run.error
    air_id = int(study.MatIds[air.Name])
    assert any(f"MAT_ID  {air_id:>6}  {objects.volume_name(air)}" in line for line in console), (
        "no Air MAT_ID line in the log"
    )
    with open(run.job, encoding="utf-8") as fh:
        air_job = json.load(fh)["air"]
    assert (air_job["mat_id"], air_job["size"]) == (air_id, 4.0), air_job
    App.Console.PrintMessage = real_print
    doc.removeObject(air_size.Name)
    doc.removeObject(air.Name)
    log.append("air region ok")

    # A Study saved before the Air Regions folder existed gets it back when the document opens in the GUI.
    old = App.newDocument("OldAir")
    old_study = objects.make_study(old)
    old.removeObject(old_study.AirRegionsGroup.Name)
    old_study.removeProperty("AirRegionsGroup")
    old_path = os.path.join(tempfile.mkdtemp(), "OldAir.FCStd")
    old.saveAs(old_path)
    App.closeDocument(old.Name)
    old = App.openDocument(old_path)
    for _ in range(3):
        Gui.updateGui()
    old_study = objects.find_study(old)
    folder = old_study.AirRegionsGroup
    assert folder is not None and folder.Label == "Air Regions" and folder in old_study.Group
    assert isinstance(folder.ViewObject.Proxy, taskpanels.ViewProviderFolder), "no folder view in the reopened document"
    assert folder.ViewObject.Proxy.doubleClicked(folder.ViewObject)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(old.Name, folder.Name)
    for _ in range(5):
        Gui.updateGui()
    assert list(shown_folders()) == ["Air Regions"], list(shown_folders())
    old_air = objects.make_air_region(old_study, "Box")
    old.recompute()
    assert not old_air.Shape.isNull() and isinstance(old_air.ViewObject.Proxy, taskpanels.ViewProviderAir)
    App.closeDocument(old.Name)
    App.setActiveDocument(doc.Name)
    log.append("old document gets the Air Regions folder ok")

    # 2D panels: a rectangle or a sector in XY; only a rectangle or a half disc in ZX.
    import Part

    flat = App.newDocument("Air2D")
    for normal, shapes in (
        (App.Vector(0, 0, 1), ["Rectangle", "Sector", "Custom"]),
        (App.Vector(0, 1, 0), ["Rectangle", "Half disc"]),
    ):
        flat_study = objects.make_study(flat, "2D")
        flat_study.MainMode = "Manual"
        face = flat.addObject("Part::Feature", "Face")
        face.Shape = Part.makePlane(10, 10, App.Vector(0, 0, 0), normal)
        flat_study.MainObjects = [face]
        flat.recompute()
        flat_air = objects.make_air_region(flat_study, "Sector", OuterRadius=50)
        flat.recompute()
        flat_panel = taskpanels.AirRegionPanel(flat_air)
        assert [flat_panel.shape.itemText(i) for i in range(flat_panel.shape.count())] == shapes
        flat_panel.shape.setCurrentIndex(flat_panel.shape.findData("Box"))
        flat_panel.fit()
        assert flat_panel.accept() and not flat_air.Shape.isNull() and flat_air.AirShape == "Box"
        flat.removeObject(flat_study.Name)
    App.closeDocument(flat.Name)
    App.setActiveDocument(doc.Name)
    log.append("2D air panels ok")

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
    assert commands.COMMANDS["EMS_Material"].IsActive() and commands.COMMANDS["EMS_MeshSize"].IsActive()
    assert not commands.COMMANDS["EMS_Excitation"].IsActive(), "excitations are 3D-only for now"
    assert commands.COMMANDS["EMS_RunMesh"].IsActive()
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
    second.MainMode, second.MainSource = "Container", source
    view.refresh()
    assert view.diagnostics.text() == "", view.diagnostics.text()
    assert view.run_button.isEnabled()
    assert view.export_notice.text() == f"Writes {jobwriter.mesh_file(second)}", view.export_notice.text()
    run2d = runner.start(second)
    assert run2d is not None and run2d.proc.waitForFinished(120000)
    Gui.updateGui()
    assert run2d.error == "" and not runner.busy(), run2d.error
    assert os.path.basename(run2d.mesh_file) == "pre_geom2D.msh" and os.path.isfile(run2d.mesh_file)
    assert second.MeshResult.FemMesh.NodeCount > 0
    log.append("2D mesh ok")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, section.Name)
    Gui.runCommand("EMS_TransfiniteBody")
    texts = [w.text() for w in opened[-1].form.findChildren(QtWidgets.QLabel)]
    assert any(t.startswith("Click a region") for t in texts), texts
    ok()
    Gui.Selection.clearSelection()
    for k in range(1, 5):
        Gui.Selection.addSelection(doc.Name, section.Name, f"Edge{k}")
    Gui.runCommand("EMS_TransfiniteEdges")
    Gui.Selection.addSelection(doc.Name, section.Name, "Face1")
    assert "Face1" not in Gui.Selection.getSelectionEx()[0].SubElementNames, "the edge gate let a face through"
    ok(elements=4)
    (tb,) = objects.transfinite_bodies(second)
    (te,) = objects.transfinite_edges(second)
    assert tb.References == [(section, ("",))], tb.References
    assert te.Elements == 4 and len(te.References[0][1]) == 4, te.References
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, section.Name)
    Gui.runCommand("EMS_Recombine")
    ok()
    (rc,) = objects.recombine_items(second)
    assert rc.References == [(section, ("",))], rc.References
    second.MeshSizesGroup.RecombinationAlgorithm = "Blossom full-quad"
    run_tf = runner.start(second)
    assert run_tf is not None and run_tf.proc.waitForFinished(120000)
    Gui.updateGui()
    assert run_tf.error == "" and not runner.busy(), run_tf.error
    log.append("2D transfinite mesh ok")
    for item in (tb, te, rc):  # leave the Study as the rest of the smoke test expects it
        doc.removeObject(item.Name)
    second.MeshSizesGroup.RecombinationAlgorithm = "Blossom"
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
    assert view.run_button.isEnabled(), "a 2D Study with a main geometry can mesh"
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
    assert study.MainMode == "Manual"
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
    assert second_settings.settings.box.isEnabled()
    assert "RecombinationAlgorithm" in second_settings.settings.algorithms
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
    taskpanels.apply_assignment(study, [doc.A], None, 0)
    view.refresh()
    assert view.diagnostics.text() == "", view.diagnostics.text()  # meshing does not need materials
    assert view.run_button.isEnabled(), "a body without a material disabled generation"
    assert view.export_notice.text() == f"Writes {jobwriter.mesh_file(study)}", view.export_notice.text()
    run = runner.start(study)
    assert run is not None and run.proc.waitForFinished(120000)
    Gui.updateGui()
    assert run.error == "" and not runner.busy()
    assert run.replaced, "the second run did not replace pre_geom.msh"
    import json

    with open(run.job, encoding="utf-8") as fh:
        selected_job = json.load(fh)
    assert [v["name"] for v in selected_job["volumes"]] == ["A"]
    assert study.MeshResult.FemMesh.VolumeCount > 0
    log.append("selected geometry mesh without materials ok")
    log.append("Study isolation and lifecycle ok")

    # Deleting: a leftover library material can go; a folder alone cannot; the Study takes all it owns.
    lone = objects.make_study(doc)
    stray = objects.make_library_material(lone, json.dumps(json.loads(lib.Record)))
    doc.removeObject(lone.Name)  # a script delete leaves the folders and the library material behind
    stray_name = stray.Name
    select(stray_name)
    Gui.runCommand("Std_Delete")
    assert doc.getObject(stray_name) is None, "a library material without a Study could not be deleted"
    study_name, folder_name = study.Name, study.MaterialsGroup.Name
    owned = [o.Name for o in objects.study_contents(study)]
    select(folder_name)
    Gui.runCommand("Std_Delete")
    assert doc.getObject(folder_name) is not None, "a Study folder was deleted on its own"
    assert log[-1].startswith("refused: "), log[-1]
    select(study_name)
    Gui.runCommand("Std_Delete")
    for _ in range(3):
        Gui.updateGui()
    left = [n for n in owned + [study_name] if doc.getObject(n) is not None]
    assert left == [], ("left after deleting the Study", left)
    assert doc.UndoNames[0] == "Delete", doc.UndoNames
    doc.undo()
    assert all(doc.getObject(n) is not None for n in owned + [study_name]), "undo did not bring the Study back"
    restored = doc.getObject(study_name)
    select(study_name, folder_name, objects.materials(restored)[0].Name)  # a mixed selection must not crash
    Gui.runCommand("Std_Delete")
    for _ in range(3):
        Gui.updateGui()
    left = [n for n in owned + [study_name] if doc.getObject(n) is not None]
    assert left == [], ("left after deleting a mixed selection", left)
    log.append("study delete ok")
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
