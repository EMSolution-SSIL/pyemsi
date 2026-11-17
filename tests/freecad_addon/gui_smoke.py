r"""GUI smoke test: runs inside FreeCAD, drives the commands, runs a mesh, then quits.

Needs the addon linked into a throwaway FreeCAD profile (PowerShell, repo root):
    $h = "$env:TEMP\ems_fc_home"; New-Item -ItemType Directory -Force "$h\Mod" | Out-Null
    if (-not (Test-Path "$h\Mod\EMSolution")) { New-Item -ItemType Junction -Path "$h\Mod\EMSolution" -Target "$PWD\freecad_addon" | Out-Null }
    $env:FREECAD_USER_HOME = $h
    Start-Process -Wait "$env:LOCALAPPDATA\Programs\FreeCAD 1.1\bin\FreeCAD.exe" tests\freecad_addon\gui_smoke.py
    Get-Content "$env:TEMP\ems_gui_smoke.txt"
The last line of the result file is "PASS" or "FAIL". FreeCAD may report a crash on quit after that.
For the pixi env's FreeCAD 1.1.0, replace the Start-Process line with
    pixi run -e addon freecad tests\freecad_addon\gui_smoke.py
"""

import os
import tempfile
import traceback

RESULT = os.path.join(tempfile.gettempdir(), "ems_gui_smoke.txt")
log = []


def main():
    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide import QtCore, QtWidgets

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
    asked = []  # bodies the several-bodies dialog was opened for; the modal dialog is driven directly below
    taskpanels.ask_bulk_assignment = lambda study, bodies: asked.append([b.Name for b in bodies])
    moves, move_answers = [], []  # texts of the move confirmations, and the answers to give them
    taskpanels.confirm_move = lambda text: (moves.append(text), move_answers.pop(0))[1]
    material_panels = []

    class RecordedMaterialPanel(taskpanels.MaterialPanel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            material_panels.append(self)

    taskpanels.MaterialPanel = RecordedMaterialPanel
    warned = []  # commands' warnings; panels' warnings go to the log as "refused: ..."
    commands.warn = lambda text: warned.append(text)
    taskpanels.warn = lambda text: log.append("refused: " + text)
    runner.notify = lambda text: log.append("notified: " + text)  # a finished run's message box
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

    commands.ask_study = lambda: ("Study", "3D", "No movement")

    def rows_of(tree):
        """{object Name: row} of a Study geometry tree."""
        rows = tree.findItems("*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive)
        return {i.data(0, QtCore.Qt.UserRole): i for i in rows}

    def tick(tree, obj, on=True):
        """Tick obj's row in a Study geometry tree as a click does; the panel saves on the next event loop turn."""
        rows_of(tree)[obj.Name].setCheckState(0, QtCore.Qt.Checked if on else QtCore.Qt.Unchecked)
        QtWidgets.QApplication.processEvents()
        return rows_of(tree)[obj.Name]  # the save rebuilt the tree

    doc = App.newDocument("Smoke")
    for name, x in (("A", 0), ("B", 10), ("Outside", 40)):  # Outside is excluded from the Study in its tree
        box = doc.addObject("Part::Box", name)
        box.Placement.Base = App.Vector(x, 0, 0)
    doc.recompute()

    Gui.runCommand("EMS_NewStudy")
    study = objects.find_study(doc)
    assert study is not None, "no study"
    assert study.Excluded == [] and [b.Name for b in objects.study_bodies(study)] == ["A", "B", "Outside"]
    study_view = taskpanels.StudyView(study)
    assert study_view.tree.objectName() == "Geometry" and study_view.tree.columnCount() == 2
    assert all(r.checkState(0) == QtCore.Qt.Checked and r.text(1) == "" for r in rows_of(study_view.tree).values())
    assert tick(study_view.tree, doc.Outside, False).checkState(0) == QtCore.Qt.Unchecked
    assert study.Excluded == [doc.Outside], study.Excluded
    assert "(2 objects)" in study_view.count.text(), study_view.count.text()
    outside_message = "Outside is excluded from the Study: tick it in the Study panel."
    for name, sub in (("EMS_Material", ""), ("EMS_Excitation", "Face1"), ("EMS_MeshSize", "")):
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(doc.Name, "A", sub)
        Gui.Selection.addSelection(doc.Name, "Outside", sub)
        Gui.runCommand(name)
        assert warned[-1:] == [outside_message], (name, warned)
    assert not asked and not objects.excitations(study) and not objects.mesh_sizes(study), (
        "assigned on an excluded body"
    )
    assert not material_panels, "a Material panel opened for an excluded body"
    log.append("excluded body gate ok")
    doc.saveAs(os.path.join(tempfile.mkdtemp(), "Smoke.FCStd"))  # the simulation folder
    log.append("study ok")

    bars = {b.objectName(): b for b in mw.findChildren(QtWidgets.QToolBar)}
    for title, names in commands.TOOLBARS:
        assert title in bars and bars[title].isVisible(), (title, sorted(bars))
    assert set(commands.MENU) - {"Separator"} == set(commands.NAMES) - {
        "EMS_StructuredMesh",
        "EMS_Refinement",
    }, commands.MENU
    assert Gui.Command.get("EMS_StructuredMesh") is not None and commands.COMMANDS["EMS_StructuredMesh"].IsActive()
    menus = []
    for sub in ("", "Face1", "Edge1"):
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(doc.Name, "A", sub)
        menus.append(commands.context_menu())
    Gui.Selection.clearSelection()
    menus.append(commands.context_menu())
    assert menus == [
        [
            *["EMS_Material", "Separator", "EMS_MeshSize", "EMS_RefineNear", "EMS_SkinLayer"],
            *["EMS_TransfiniteBody", "EMS_SweptBody", "EMS_Recombine", "EMS_SymmetricGroup"],
        ],
        ["EMS_Material", "EMS_Excitation", "Separator", "EMS_MeshSize", "EMS_RefineNear"],
        ["EMS_MeshSize", "EMS_RefineNear", "EMS_TransfiniteEdges"],
        [],
    ], menus
    log.append("toolbars and context menu ok")

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
    for name in (study.Name, "Outside"):  # the gate: not geometry, excluded
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

    from emsolution import validation, labels

    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A", "Edge1")
    opened.clear()  # the Mesh Size panel above was opened by hand
    Gui.runCommand("EMS_RefineNear")
    assert len(opened) == 1, (
        warned[-1:],
        commands.COMMANDS["EMS_RefineNear"].IsActive(),
        Gui.Control.activeDialog(),
        commands.active_study(),
    )
    panel = opened.pop()
    assert panel.new and Gui.Control.activeDialog(), (panel.new, Gui.Control.activeDialog(), warned[-1:])
    panel.fine.setValue(0.5)
    overlay = next(iter(labels._overlays.values()))
    overlay.tick()
    assert overlay.tags[0]["text"] == "0.5 → 5 mm", overlay.tags  # the panel's unsaved fine size, first: in focus
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "B")
    panel.add_limit()
    assert panel.limit.count() == 1, panel.limit.count()
    assert panel.accept()
    (near,) = objects.refine_items(study)
    assert near.FineSize.Value == 0.5 and near.LimitTo == [doc.B], (near.FineSize.Value, near.LimitTo)
    assert near.References == [(doc.A, ("Edge1",))], near.References
    refine_errors = [p.text for p in validation.errors(validation.validate(study)) if "Refine" in p.text]
    assert not refine_errors, refine_errors
    Gui.Selection.clearSelection()
    log.append("refine near ok")

    # Skin Layer: a whole body (a 3D-view click on a face picks it), its depth from the calculator (aluminium at 1 kHz).
    Gui.Selection.addSelection(doc.Name, "B", "Face1")
    Gui.runCommand("EMS_SkinLayer")
    assert len(opened) == 1, (warned[-1:], commands.COMMANDS["EMS_SkinLayer"].IsActive())
    panel = opened.pop()
    assert panel.new and Gui.Control.activeDialog() and panel.current == [(doc.B, "")], panel.current
    assert panel.quads is None, "quad layers offered in a 3D Study"
    panel.mu_r.setText("0")
    panel.calculate.click()
    assert panel.depth_result.text() == "Frequency, conductivity and permeability must be greater than 0."
    assert panel.depth.value() == 1.0, panel.depth.value()
    panel.frequency.setText("1000")
    panel.conductivity.setText("3.5e7")
    panel.mu_r.setText("1")
    panel.calculate.click()
    assert panel.depth_result.text() == "δ = 2.69 mm", panel.depth_result.text()
    skin_tag = labels.tag_text(panel.obj, panel.unsaved())
    assert skin_tag == "δ 2.69 mm, 2/δ, 3δ", skin_tag
    assert panel.accept()
    (skin,) = objects.skin_layers(study)
    assert abs(skin.SkinDepth.Value - 2.69) < 0.01, skin.SkinDepth.Value
    assert skin.Frequency == 1000 and skin.Conductivity == 3.5e7 and skin.References == [(doc.B, ("",))]
    skin_errors = [p.text for p in validation.errors(validation.validate(study)) if "Skin Layer" in p.text]
    assert not skin_errors, skin_errors
    doc.removeObject(skin.Name)
    Gui.Selection.clearSelection()
    log.append("skin layer ok")

    # Swept Body: a whole box body, its length along the path from the panel; a start face is a face pick.
    Gui.Selection.addSelection(doc.Name, "B")
    Gui.runCommand("EMS_SweptBody")
    assert len(opened) == 1, (warned[-1:], commands.COMMANDS["EMS_SweptBody"].IsActive())
    panel = opened.pop()
    assert panel.new and Gui.Control.activeDialog() and panel.current == [(doc.B, "")], panel.current
    assert panel.path_size.value() == 0 and panel.section_size.value() == 0
    panel.path_size.setValue(4)
    sweep_tag = labels.tag_text(panel.obj, panel.unsaved())
    assert sweep_tag == "along 4 mm", sweep_tag
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "B", "Face1")
    panel.add_start()
    assert panel.start == [(doc.B, "Face1")], panel.start
    panel.remove_start()  # nothing selected in the list: kept
    assert panel.accept()
    (swept,) = objects.swept_bodies(study)
    assert swept.PathSize.Value == 4 and swept.SectionSize.Value == 0, swept.PathSize.Value
    assert swept.References == [(doc.B, ("",))] and swept.StartFace == [(doc.B, ("Face1",))], swept.StartFace
    swept_errors = [p.text for p in validation.errors(validation.validate(study)) if "Swept Body" in p.text]
    assert not swept_errors, swept_errors
    doc.removeObject(swept.Name)
    Gui.Selection.clearSelection()
    log.append("swept body ok")

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

    rows = {"Material Library": 0, "Materials": 2, "Excitations": 1, "Mesh Sizes": 3, "Air Regions": 0}
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
    panel = material_panels.pop()  # B has no Material: a new one on it
    assert panel.new and panel.current == [(doc.B, "")] and panel.name.text() == "B", (panel.current, panel.name.text())
    assert panel.reject() and objects.materials(study) == [], "Cancel kept the row's new Material"
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
    # A failure inside the several-bodies dialog: the transaction is aborted, nothing is left behind.
    real_assign = objects.assign

    def failing_assign(*args):
        real_assign(*args)
        raise RuntimeError("smoke: assign failed")

    objects.assign = failing_assign
    undo = list(doc.UndoNames)
    try:
        taskpanels.BulkAssignDialog(study, [doc.A, doc.B]).accept()
    except RuntimeError:
        pass
    objects.assign = real_assign
    assert not objects.materials(study) and not doc.HasPendingTransaction, "a failed bulk assignment was left behind"
    assert list(doc.UndoNames) == undo, list(doc.UndoNames)
    dialog = taskpanels.BulkAssignDialog(study, [doc.A, doc.B])  # several bodies: one Material each
    assert dialog.material.currentData() == lib.Name, "an unassigned body did not default to the first material"
    dialog.potential.setValue(2)
    dialog.accept()
    mat, mat_b = objects.materials(study)
    assert (mat.Body, mat.LibraryMaterial, mat.Potential, mat.Label) == (doc.A, lib, 2, "A: Air"), mat.Label
    assert (mat.GroupName, mat_b.GroupName) == ("A", "B") and doc.UndoNames[0] == "Assign material", doc.UndoNames
    # The panel: double-click, rename; the typed name stays.
    mat.ViewObject.Proxy.doubleClicked(mat.ViewObject)
    panel = material_panels.pop()
    assert not panel.new and Gui.Control.activeDialog() and panel.name.text() == "A", panel.name.text()
    assert panel.current == [(doc.A, "")] and panel.material.currentData() == lib.Name
    panel.name.setText("Core")
    panel.name_typed("Core")
    assert panel.accept() and not Gui.Control.activeDialog()
    assert (mat.GroupName, mat.Label) == ("Core", "Core: Air") and doc.UndoNames[0] == "Edit A: Air", doc.UndoNames
    # Nothing selected: an empty panel that refuses OK; picking A asks before taking it from Core.
    Gui.Selection.clearSelection()
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    assert panel.new and panel.refs.count() == 0 and not panel.accept(), "an empty Material was made"
    assert panel.form.windowTitle() == "New Material", panel.form.windowTitle()
    assert log[-1].startswith("refused: Select geometry"), log[-1]
    Gui.Selection.addSelection(doc.Name, "A")
    move_answers.append(False)
    panel.add_selection()
    one = 'A already belongs to the Material "Core".\n\nA body can have only one Material. Move it to "A"?'
    assert moves[-1] == one, moves[-1]
    assert panel.current == [], "Cancel in the move box added the body"
    move_answers.append(True)
    panel.add_selection()
    assert panel.current == [(doc.A, "")] and not panel.note.isHidden(), panel.note.text()
    assert panel.note.text() == '"Core" will be removed: it has nothing left.', panel.note.text()
    assert panel.reject() and objects.assignment_of(study)["A"] == mat, "Cancel moved A out of Core"
    # Picked before the command: the panel opens with it, suggests its name and moves it on OK.
    select("A")
    move_answers.append(True)
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    assert panel.current == [(doc.A, "")] and panel.name.text() == "A", (panel.current, panel.name.text())
    assert panel.accept()
    mat = objects.assignment_of(study)["A"]
    assert mat.GroupName == "A" and "Core" not in [m.GroupName for m in objects.materials(study)]
    assert doc.UndoNames[0] == "Assign material", doc.UndoNames
    # Assigned again: the name of the Material it leaves, removed on OK, is free (the mesh name stays "A").
    select("A")
    move_answers.append(True)
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    assert panel.name.text() == "A" and panel.accept(), (panel.name.text(), log[-1])
    mat = objects.assignment_of(study)["A"]
    assert mat.GroupName == "A" and len(objects.materials(study)) == 2, [m.Label for m in objects.materials(study)]
    # An Air Region without a Material gets one in a new panel, named after it; its panel saves despite a clash.
    air = objects.make_air_region(study, "Box")
    doc.recompute()
    open_view = taskpanels.FolderView(study.MaterialsGroup)
    open_view.open_item([r[0] for r in open_view.rows].index(air), 0)
    panel = material_panels.pop()
    assert panel.current == [(air, "")] and panel.name.text() == objects.display_name(air), panel.name.text()
    assert panel.name.isReadOnly() and panel.accept(), log[-1]
    air_mat = objects.air_material(study, air)
    assert air_mat is not None and air_mat.GroupName == objects.display_name(air), "the Air Region got no Material"
    objects.set_material_name(mat_b, objects.display_name(air))  # another Material with the Air Region's name
    air_mat.ViewObject.Proxy.doubleClicked(air_mat.ViewObject)
    panel = material_panels.pop()
    panel.potential.setValue(7)
    assert panel.accept() and air_mat.Potential == 7, ("the Air's Material panel could not save", log[-1])
    objects.set_material_name(mat_b, "B")
    doc.removeObject(air_mat.Name)
    doc.removeObject(air.Name)
    doc.recompute()
    materials_view = taskpanels.FolderView(study.MaterialsGroup)
    assert materials_view.missing.isHidden(), materials_view.missing.text()
    doc.openTransaction("Remove material")
    objects.unassign(study, [doc.B])
    doc.commitTransaction()
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
    assert extra in objects.study_bodies(study), "a body drawn later is not in the Study"
    objects.set_excluded(study, [doc.Outside, extra])
    dialog = taskpanels.BulkAssignDialog(study, [extra])
    dialog.accept()
    assert objects.assignment_of(study).get("Extra") is None, "assigned an excluded body"
    assert log[-1] == "refused: Extra is excluded from the Study: tick it in the Study panel.", log[-1]
    dialog.reject()
    objects.set_excluded(study, [doc.Outside])
    doc.removeObject("Extra")
    select(study.MaterialLibraryGroup.Name)
    used_by = shown_folders()["Material Library"].item(0, 3).text()
    assert sorted(used_by.split(", ")) == ["A", "B"], used_by  # a moved body's Material comes last
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
    (air_mat,) = [m for m in objects.materials(study) if m.Body == air]
    assert (air_mat.LibraryMaterial, air_mat.Potential) == (lib, 0), "the new air did not reuse the Air material"
    assert air not in objects.bodies_without_material(study), "the new air still lacks a material"
    assert isinstance(air.ViewObject.Proxy, taskpanels.ViewProviderAir)
    assert (air.ViewObject.Transparency, air.ViewObject.DisplayMode) == (95, "Flat Lines")
    look = air.ViewObject
    assert all(abs(a - b) < 0.01 for a, b in zip(look.ShapeColor, taskpanels.AIR_COLOR)), look.ShapeColor
    assert all(abs(a - b) < 0.01 for a, b in zip(look.ShapeAppearance[0].DiffuseColor, taskpanels.AIR_COLOR)), (
        look.ShapeAppearance[0].DiffuseColor
    )
    assert all(abs(a - b) < 0.01 for a, b in zip(look.LineColor, taskpanels.AIR_LINE_COLOR)), look.LineColor
    sides = ("XPlus", "XMinus", "YPlus", "YMinus", "ZPlus", "ZMinus")
    assert air.SizeMode == "Padding" and panel.mode_padding.isChecked(), "a new Air Region does not start in Padding"
    assert all(getattr(air, f"Pad{s}Percent") == 20 for s in sides), "not 20 % on every side"
    assert sorted(o.Name for o in air.SizedBy) == ["A", "B"], air.SizedBy
    for body in (doc.A, doc.B):
        assert air.Shape.BoundBox.isInside(body.Shape.BoundBox), "the Air Region does not enclose " + body.Name
    assert abs(air.Length.Value - 28) < 1e-6, air.Length  # 20 mm of bodies, +20 % on each side
    assert not [b for b in panel.form.findChildren(QtWidgets.QPushButton) if b.text() == "Fit to bodies"]
    assert [panel.shape.itemText(i) for i in range(panel.shape.count())] == ["Box", "Sector", "Custom"]
    assert panel.groups["Box"].isHidden() and not panel.tables["Box"].isHidden(), "Padding shows its table"
    assert panel.groups["Sector"].isHidden() and panel.tables["Sector"].isHidden()
    assert list(panel.pad["Box"]) == list(sides), list(panel.pad["Box"])
    assert panel.result.text().startswith("Result: centre (10, 5, 5)") and "28 ×" in panel.result.text(), (
        panel.result.text()
    )
    panel.shape.setCurrentIndex(panel.shape.findData("Sector"))
    assert air.AirShape == "Sector", "the shape was not written while editing"
    assert air.PadOuterPercent == 20, "the Sector hugs the bodies: no outer padding"
    assert not panel.tables["Sector"].isHidden() and panel.tables["Box"].isHidden()
    assert list(panel.pad["Sector"]) == ["Outer", "Inner", "ZPlus", "ZMinus"], list(panel.pad["Sector"])
    assert not panel.groups["Sector"].isHidden(), "the Sector angles stay manual in Padding"
    shown = [
        a.text()
        for a in panel.groups["Sector"].findChildren(QtWidgets.QLabel)
        if a.text() and a.isVisibleTo(panel.form)
    ]
    assert shown == ["Start angle", "End angle"], shown
    assert not panel.pad["Sector"]["Inner"][0].isEnabled(), "the inner padding is on for a full disc"
    panel.ring.setChecked(True)
    assert air.InnerFromBodies and panel.pad["Sector"]["Inner"][0].isEnabled(), "the ring switch"
    panel.ring.setChecked(False)
    # An angle field (Gui::QuantitySpinBox, deg) follows a formula; the f(x) dialog cannot be driven from a script.
    air.setExpression("EndAngle", "45 deg * 2")
    for _ in range(5):
        Gui.updateGui()
    assert air.EndAngle.Value == 90 and taskpanels.field_value(panel.angles[1]) == 90, "the angle formula"
    air.setExpression("EndAngle", None)
    taskpanels.set_field_value(panel.angles[1], 360)
    panel.shape.setCurrentIndex(panel.shape.findData("Custom"))  # no body picked: nothing is applied yet
    assert (air.AirShape, air.SizeMode) == ("Sector", "Padding"), (air.AirShape, air.SizeMode)
    panel.shape.setCurrentIndex(panel.shape.findData("Box"))
    assert air.SizeMode == "Padding", "a look at Custom lost Padding"
    assert air.AirShape == "Box" and not panel.tables["Box"].isHidden() and panel.groups["Box"].isHidden()
    assert panel.reject()
    assert objects.air_regions(study) == [] and not Gui.Control.activeDialog(), "Cancel kept the new Air Region"
    bodies = sorted(m.Body.Name for m in objects.materials(study))
    assert bodies == ["A", "B"], ("Cancel kept the air's Material assignment", bodies)
    assert objects.library_materials(study) == [lib], "Cancel changed the Material Library"
    # A Study without an Air material: the command makes one, Cancel takes it away again, OK keeps it.
    fresh_doc = App.newDocument("FreshAir")
    fresh = objects.make_study(fresh_doc)
    App.setActiveDocument(fresh_doc.Name)
    select(fresh.Name)
    Gui.runCommand("EMS_AddAirRegion")
    panel = air_panels.pop()
    (fresh_air,) = objects.air_regions(fresh)
    (fresh_lib,) = objects.library_materials(fresh)
    (fresh_mat,) = objects.materials(fresh)
    fresh_record = studymaterials.record_material(fresh_lib)
    assert (fresh_record.name, fresh_lib.Label, fresh_lib.MaterialId) == ("Air (μr=1)", "Air (μr=1)", "user:air")
    assert fresh_air.Label == "Air", fresh_air.Label
    assert (fresh_mat.Body, fresh_mat.LibraryMaterial, fresh_mat.Potential) == (fresh_air, fresh_lib, 0)
    assert panel.reject()
    assert objects.air_regions(fresh) == [] and objects.library_materials(fresh) == [], "Cancel kept the Air material"
    assert objects.materials(fresh) == []
    Gui.runCommand("EMS_AddAirRegion")
    assert air_panels.pop().accept()
    (fresh_air,) = objects.air_regions(fresh)
    (fresh_lib,) = objects.library_materials(fresh)
    (fresh_mat,) = objects.materials(fresh)
    assert (fresh_mat.Body, fresh_mat.LibraryMaterial, fresh_mat.Potential) == (fresh_air, fresh_lib, 0)
    from emsolution import validation

    assert not [p for p in validation.validate(fresh) if "No material" in p.text], "the air still has no material"
    fresh_doc.undo()  # one Undo removes the air and its material together
    assert objects.air_regions(fresh) == [] and objects.library_materials(fresh) == [], "Undo left the Air material"
    App.closeDocument(fresh_doc.Name)
    App.setActiveDocument(doc.Name)
    select(study.Name)
    saved_excluded = list(study.Excluded)  # every body excluded: the new Air Region stays Manual with the old defaults
    objects.set_excluded(study, [doc.A, doc.B, doc.Outside])
    Gui.runCommand("EMS_AddAirRegion")
    panel = air_panels.pop()
    (empty,) = objects.air_regions(study)
    assert empty.SizeMode == "Manual" and panel.mode_manual.isChecked(), "no bodies: the Air Region is not Manual"
    assert (empty.Length.Value, empty.Width.Value, empty.Height.Value) == (100, 100, 100), "no bodies: not the defaults"
    assert all(getattr(empty, f"Pad{s}Percent") == 0 for s in sides), "no bodies: padding was set"
    assert panel.reject() and objects.air_regions(study) == []
    objects.set_excluded(study, saved_excluded)
    Gui.runCommand("EMS_AddAirRegion")
    panel = air_panels.pop()
    (air,) = objects.air_regions(study)
    plus, minus = panel.pad["Box"]["XPlus"], panel.pad["Box"]["XMinus"]
    panel.symmetric.setChecked(True)
    assert not minus[0].isEnabled() and plus[0].isEnabled(), "Symmetric leaves the - side editable"
    taskpanels.set_field_value(plus[0], 5)
    for _ in range(5):
        Gui.updateGui()
    assert air.PadXPlusPercent == 5 and air.PadXMinusPercent == 5, "Symmetric: - does not follow a typed +"
    # A percent field (Gui::DoubleSpinBox) follows a formula, and the - side takes the same formula.
    air.setExpression("PadXPlusPercent", "10 + 10")
    for _ in range(5):
        Gui.updateGui()
    assert taskpanels.field_value(plus[0]) == 20 and air.PadXPlusPercent == 20, "the percent formula"
    assert ("PadXMinusPercent", "10 + 10") in air.ExpressionEngine, air.ExpressionEngine
    assert air.PadXMinusPercent == 20 and taskpanels.field_value(minus[0]) == 20, "Symmetric: - does not follow"
    air.setExpression("PadXPlusPercent", "15 + 5")  # the same value: no field sends a change
    for _ in range(5):
        Gui.updateGui()
    panel.settle()
    assert ("PadXMinusPercent", "15 + 5") in air.ExpressionEngine, "Symmetric: settle did not mirror"
    assert plus[0].metaObject().className() == "Gui::DoubleSpinBox", plus[0].metaObject().className()
    assert abs(air.Length.Value - 28) < 1e-6 and "28 ×" in panel.result.text(), panel.result.text()
    # A length field (Gui::QuantitySpinBox, mm) in the padding column follows a formula too.
    air.setExpression("PadXPlus", "2 mm + 1 mm")
    for _ in range(5):
        Gui.updateGui()
    assert taskpanels.field_value(plus[1]) == 3 and air.PadXMinus.Value == 3, "the length formula"
    assert abs(air.Length.Value - 34) < 1e-6 and "34 ×" in panel.result.text(), panel.result.text()
    assert plus[1].metaObject().className() == "Gui::QuantitySpinBox", plus[1].metaObject().className()
    air.setExpression("PadXPlus", None)
    air.setExpression("PadXMinus", None)
    taskpanels.set_field_value(plus[1], 0)
    for _ in range(5):
        Gui.updateGui()
    assert abs(air.Length.Value - 28) < 1e-6, air.Length
    panel.symmetric.setChecked(False)
    assert minus[0].isEnabled()
    air.setExpression("PadXMinusPercent", None)  # the - side held the copied formula
    taskpanels.set_field_value(minus[0], 0)
    assert air.PadXMinusPercent == 0 and air.PadXPlusPercent == 20, "unchecked Symmetric ties the sides"
    taskpanels.set_field_value(minus[0], 20)
    # Convert to Manual keeps the computed sizes and shows the manual fields, which take formulas.
    sizes = (air.Center, air.Length.Value, air.Width.Value, air.Height.Value)
    panel.convert.click()
    assert air.SizeMode == "Manual" and panel.mode_manual.isChecked(), "Convert to Manual"
    assert (air.Center, air.Length.Value, air.Width.Value, air.Height.Value) == sizes, "Convert changed the sizes"
    assert not panel.groups["Box"].isHidden() and panel.tables["Box"].isHidden() and panel.foot.isHidden()
    assert abs(taskpanels.field_value(panel.size["Length"]) - 28) < 1e-6, "the Length field does not show the size"
    air.setExpression("Center.x", "5 mm + 6 mm")
    air.setExpression("Length", "20 mm + 10 mm")
    for _ in range(5):
        Gui.updateGui()
    assert air.Center.x == 11 and taskpanels.field_value(panel.center["x"]) == 11, "the Centre formula"
    assert air.Length.Value == 30 and taskpanels.field_value(panel.size["Length"]) == 30, "the Length formula"
    air.setExpression("Center.x", None)
    air.setExpression("Length", None)
    taskpanels.set_field_value(panel.center["x"], 10)
    assert panel.accept() and not Gui.Control.activeDialog()
    (air,) = objects.air_regions(study)
    assert air.SizeMode == "Manual" and air.Shape.BoundBox.isInside(doc.B.Shape.BoundBox)
    assert air.ViewObject.Proxy.doubleClicked(air.ViewObject)
    panel = air_panels.pop()
    assert not panel.new and Gui.Control.activeDialog()
    taskpanels.set_field_value(panel.size["Length"], 70)
    assert abs(air.Length.Value - 70) < 1e-6, "the Length field did not write while editing"
    assert panel.accept() and abs(air.Length.Value - 70) < 1e-6 and doc.UndoNames[0].startswith("Edit Air"), (
        doc.UndoNames
    )
    air.ViewObject.Proxy.doubleClicked(air.ViewObject)
    panel = air_panels.pop()
    taskpanels.set_field_value(panel.size["Length"], 90)
    assert abs(air.Length.Value - 90) < 1e-6
    assert panel.reject() and abs(air.Length.Value - 70) < 1e-6, "Cancel of an edit kept the change"
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
    moving = doc.addObject("Part::Box", "NewBox")  # the Excitation gate takes a body drawn later, not an excluded one
    doc.recompute()
    assert moving.Name in taskpanels.ItemGate(study, taskpanels.ANY_SUB, True, False).main, "gate: new body"
    assert "Outside" not in taskpanels.ItemGate(study, taskpanels.ANY_SUB, True, False).main, "gate: excluded body"
    doc.removeObject(moving.Name)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, air.Name)
    Gui.runCommand("EMS_MeshSize")
    assert opened[-1].current == [(air, "")], opened[-1].current
    Gui.Selection.addSelection(doc.Name, air.Name, "Face1")
    assert Gui.Selection.getSelection() == [air], "the Mesh Size gate refused the Air Region"
    ok(size=4.0)
    air_size = objects.mesh_sizes(study)[-1]
    # Air Grading: the right click of the Air Region offers it; with nothing selected the command takes the Air Region.
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, air.Name)
    assert commands.context_menu() == ["EMS_Material", "EMS_MeshSize", "EMS_RefineNear", "EMS_AirGrading"], (
        commands.context_menu()
    )
    Gui.Selection.clearSelection()
    opened.clear()
    Gui.runCommand("EMS_AirGrading")
    assert len(opened) == 1, (warned[-1:], commands.COMMANDS["EMS_AirGrading"].IsActive())
    panel = opened.pop()
    assert panel.new and Gui.Control.activeDialog() and panel.current == [(air, "")], panel.current
    assert any("the air's size (4 mm)" in w.text() for w in panel.form.findChildren(QtWidgets.QLabel)), "no far hint"
    panel.growth.setValue(30)
    panel.far.setValue(0)
    assert panel.accept()
    (grading,) = objects.air_gradings(study)
    assert grading.GrowthDistance.Value == 30 and grading.FarSize.Value == 0, grading.GrowthDistance.Value
    assert grading.References == [(air, ("",))], grading.References
    from emsolution import labels as label_text

    assert label_text.tag_text(grading, {}) == "→ 4 mm over 30", label_text.tag_text(grading, {})
    grading_errors = [p.text for p in validation.errors(validation.validate(study)) if "Air Grading" in p.text]
    assert not grading_errors, grading_errors
    doc.removeObject(grading.Name)
    log.append("air grading ok")
    # The air is not recombined or structured: the commands and an open Recombine panel refuse it.
    for command, sub in (("EMS_Recombine", ""), ("EMS_TransfiniteBody", ""), ("EMS_TransfiniteEdges", "Edge1")):
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(doc.Name, air.Name, sub)
        panels = len(opened)
        Gui.runCommand(command)
        refused = f"Air Region {objects.display_name(air)} cannot be recombined or structured."
        assert warned[-1] == refused and len(opened) == panels, (command, warned[-1])
    recombine = objects.make_recombine(study, [doc.A])
    panel = taskpanels.ItemPanel(recombine)
    opened.pop()
    Gui.Control.showDialog(panel)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, air.Name)
    assert Gui.Selection.getSelection() == [], "the Recombine gate let the Air Region through"
    panel.reject()
    doc.removeObject(recombine.Name)
    run = runner.start(study)
    assert run is not None and run.proc.waitForFinished(120000), "mesher timed out"
    Gui.updateGui()
    assert run.error == "" and not runner.busy(), run.error
    air_id = int(study.MatIds[air.Name])
    assert any(f"MAT_ID  {air_id:>6}  Air" in line for line in console), "no Air MAT_ID line in the log"
    with open(run.job, encoding="utf-8") as fh:
        air_job = json.load(fh)["air"]
    assert (air_job["mat_id"], air_job["size"]) == (air_id, 4.0), air_job
    App.Console.PrintMessage = real_print
    doc.removeObject(air_size.Name)
    doc.removeObject(air.Name)
    log.append("air region ok")

    # The Study tree: a Custom Air Region's shape is unticked and disabled, with the reason beside it.
    src_doc = App.newDocument("AirSource")
    core = src_doc.addObject("Part::Box", "Core")
    side = src_doc.addObject("Part::Box", "Side")
    side.Placement.Base = App.Vector(12, 0, 0)
    shell = src_doc.addObject("Part::Box", "Shell")
    shell.Length = shell.Width = shell.Height = 60
    shell.Placement.Base = App.Vector(-20, -20, -20)
    holder = src_doc.addObject("App::DocumentObjectGroup", "Holder")
    holder.addObject(side)
    holder.addObject(shell)
    src_study = objects.make_study(src_doc)
    src_air = objects.make_air_region(src_study, "Custom", Source=shell)
    src_doc.recompute()
    src_view = taskpanels.StudyView(src_study)
    src_rows = rows_of(src_view.tree)
    shell_row = src_rows[shell.Name]
    assert shell_row.text(1) == f"air shape of {objects.display_name(src_air)}", shell_row.text(1)
    assert shell_row.checkState(0) == QtCore.Qt.Unchecked and shell_row.isDisabled(), "the air source is choosable"
    assert src_rows[core.Name].text(1) == "" and src_rows[core.Name].checkState(0) == QtCore.Qt.Checked
    assert [b.Name for b in objects.study_bodies(src_study)] == ["Core", "Side"], objects.study_bodies(src_study)
    tick(src_view.tree, holder, False)  # the group with the air source in it, unticked and ticked again
    assert src_study.Excluded == [holder], src_study.Excluded
    holder_row = tick(src_view.tree, holder)
    assert src_study.Excluded == [] and rows_of(src_view.tree)[shell.Name].checkState(0) == QtCore.Qt.Unchecked
    assert holder_row.checkState(0) == QtCore.Qt.PartiallyChecked, "the group shows its air source ticked"
    assert src_air.Source == shell and objects.air_regions(src_study) == [src_air]
    App.closeDocument(src_doc.Name)
    App.setActiveDocument(doc.Name)
    log.append("study tree air source ok")

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

    for normal, shapes, rows, half_rows in (
        (
            App.Vector(0, 0, 1),
            ["Rectangle", "Sector", "Custom"],
            ["XPlus", "XMinus", "YPlus", "YMinus"],
            ["Outer", "Inner"],
        ),
        (App.Vector(0, 1, 0), ["Rectangle", "Half disc"], ["XPlus", "ZPlus", "ZMinus"], ["Outer"]),
    ):
        flat = App.newDocument("Air2D")  # one Study per document
        flat_study = objects.make_study(flat, "2D")
        face = flat.addObject("Part::Feature", "Face")
        face.Shape = Part.makePlane(10, 10, App.Vector(0, 0, 0), normal)
        flat.recompute()
        flat_air = objects.make_air_region(flat_study, "Sector", OuterRadius=50)
        flat.recompute()
        flat_panel = taskpanels.AirRegionPanel(flat_air)
        assert [flat_panel.shape.itemText(i) for i in range(flat_panel.shape.count())] == shapes
        flat_panel.shape.setCurrentIndex(flat_panel.shape.findData("Box"))
        assert flat_air.AirShape == "Box" and flat_air.SizeMode == "Manual"
        flat_panel.mode_padding.setChecked(True)
        assert flat_air.SizeMode == "Padding" and list(flat_panel.pad["Box"]) == rows, list(flat_panel.pad["Box"])
        assert not flat_air.Shape.isNull() and flat_air.Shape.BoundBox.isInside(face.Shape.BoundBox)
        flat_panel.shape.setCurrentIndex(flat_panel.shape.findData("Sector"))
        assert list(flat_panel.pad["Sector"]) == half_rows, list(flat_panel.pad["Sector"])
        if "Custom" in shapes:  # a Custom shape has no Padding
            flat_panel.shape.setCurrentIndex(flat_panel.shape.findData("Custom"))
            assert flat_panel.mode_box.isHidden() and (flat_air.AirShape, flat_air.SizeMode) == ("Sector", "Padding")
        flat_panel.shape.setCurrentIndex(flat_panel.shape.findData("Box"))
        assert flat_air.SizeMode == "Padding" and flat_panel.mode_padding.isChecked(), "Padding was lost"
        plus = "PadYPlusPercent" if normal.z else "PadZPlusPercent"
        assert flat_panel.symmetric.isChecked() and getattr(flat_air, plus) == 20, getattr(flat_air, plus)
        flat_air.setExpression(plus, "10 * 2")  # the same value: no field sends a change
        for _ in range(5):
            Gui.updateGui()
        flat_panel.convert.click()
        assert flat_panel.accept() and not flat_air.Shape.isNull() and flat_air.AirShape == "Box"
        assert flat_air.SizeMode == "Manual", "Convert to Manual in a 2D Study"
        assert (plus.replace("Plus", "Minus"), "10 * 2") in flat_air.ExpressionEngine, "OK did not mirror"
        App.closeDocument(flat.Name)
    App.setActiveDocument(doc.Name)
    log.append("2D air panels ok")

    # Sliding Interface: command, panel, hint in the Study panel, and a 2D sliding mesh.
    from emsolution import validation

    App.Console.PrintMessage = lambda text: (console.append(text), real_print(text))
    slide_doc = App.newDocument("Slide2D")
    slide_study = objects.make_study(slide_doc, "2D")
    taskpanels.ViewProviderStudy(slide_study.ViewObject)
    disc = lambda r: Part.Face(Part.Wire(Part.makeCircle(r)))  # noqa: E731 - a face in z = 0
    stator, rotor = (slide_doc.addObject("Part::Feature", n) for n in ("Stator", "Rotor"))
    stator.Shape, rotor.Shape = disc(80).cut(disc(45)), disc(40)
    slide_doc.recompute()
    slide_doc.saveAs(os.path.join(tempfile.mkdtemp(), "Slide2D.FCStd"))
    App.setActiveDocument(slide_doc.Name)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(slide_doc.Name, slide_study.Name)
    slide_panels = []  # panels the Sliding Interface command and its double-click opened

    class RecordedSlidePanel(taskpanels.SlidingInterfacePanel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            slide_panels.append(self)

    taskpanels.SlidingInterfacePanel = RecordedSlidePanel
    add_slide = commands.COMMANDS["EMS_AddSlidingInterface"]
    assert not add_slide.IsActive(), "Sliding Interface is active without sliding motion"
    slide_study.Movement = "Sliding motion"
    assert add_slide.IsActive()
    hint_text = "Add an Air Region and a Sliding Interface"
    study_view = taskpanels.StudyView(slide_study)
    assert study_view.slide_hint.text() == hint_text and study_view.slide_hint.isVisibleTo(study_view.form), "no hint"
    Gui.runCommand("EMS_AddSlidingInterface")
    assert warned[-1] == "Add an Air Region first." and not slide_panels, warned
    slide_air = objects.make_air_region(slide_study, "Sector", OuterRadius=100)
    slide_doc.recompute()
    Gui.runCommand("EMS_AddSlidingInterface")
    panel = slide_panels.pop()
    assert panel.new and Gui.Control.activeDialog(), "the Sliding Interface panel did not open"
    (iface,) = objects.sliding_interfaces(slide_study)
    assert iface.Kind == "Rotational" and iface.AirRegion == slide_air
    assert isinstance(iface.ViewObject.Proxy, taskpanels.ViewProviderSlidingInterface)
    assert [panel.kind.itemText(i) for i in range(panel.kind.count())] == ["Rotational", "Linear"]
    assert panel.cross is None, "Cross divisions in a 2D Study"
    taskpanels.set_field_value(panel.divisions, 72)
    assert iface.Divisions == 72, "the Divisions field did not write the property while editing"
    assert "5" in panel.step_label.text() and "deg" in panel.step_label.text(), panel.step_label.text()

    def moving_sides():
        return [panel.moving_side.itemText(i) for i in range(panel.moving_side.count())]

    assert moving_sides() == ["Inside", "Outside"] and panel.moving_side.currentText() == iface.MovingSide == "Inside"
    panel.moving_side.setCurrentText("Outside")
    assert iface.MovingSide == "Outside", "the Moving side combo did not write MovingSide"
    panel.kind.setCurrentIndex(panel.kind.findData("Linear"))  # the choices follow the Kind
    assert moving_sides() == ["Positive", "Negative"], moving_sides()
    assert iface.MovingSide == "Negative" and panel.moving_side.currentText() == "Negative", iface.MovingSide
    panel.kind.setCurrentIndex(panel.kind.findData("Rotational"))
    assert iface.MovingSide == "Outside" and panel.moving_side.currentText() == "Outside", iface.MovingSide
    assert panel.reject() and objects.sliding_interfaces(slide_study) == [], "Cancel kept the new Sliding Interface"
    assert not Gui.Control.activeDialog()
    Gui.runCommand("EMS_AddSlidingInterface")
    panel = slide_panels.pop()
    (iface,) = objects.sliding_interfaces(slide_study)
    taskpanels.set_field_value(panel.radius, 42.5)
    assert iface.Radius.Value == 42.5, "the Radius field did not write the property while editing"
    # The f(x) dialog cannot be driven from a script; with auto-apply it ends in setExpression on the property.
    iface.setExpression("Divisions", "36 * 2")
    for _ in range(5):
        Gui.updateGui()
    assert iface.Divisions == 72 and taskpanels.field_value(panel.divisions) == 72, "the formula was not followed"
    assert panel.divisions.property("minimum") == 2 and panel.radius.property("unit") == "mm"
    assert panel.accept() and not Gui.Control.activeDialog()
    assert (iface.Radius.Value, iface.Divisions) == (42.5, 72), (iface.Radius, iface.Divisions)
    assert ("Divisions", "36 * 2") in iface.ExpressionEngine, iface.ExpressionEngine
    assert len(iface.Shape.Edges) == 2, "a full turn is two half circles"
    study_view.refresh()
    assert not study_view.slide_hint.isVisibleTo(study_view.form), "the hint stayed with an Air Region and an interface"

    def notes():
        """{body: second column} of the Study tree."""
        study_view.refresh()
        return {name: r.text(1) for name, r in rows_of(study_view.tree).items()}

    assert notes() == {"Stator": "", "Rotor": "moving"}, notes()  # Inside the radius moves
    assert iface.ViewObject.Proxy.doubleClicked(iface.ViewObject)
    panel = slide_panels.pop()
    assert not panel.new and taskpanels.field_value(panel.divisions) == 72
    assert panel.moving_side.currentText() == "Inside", panel.moving_side.currentText()
    panel.moving_side.setCurrentText("Outside")
    assert iface.MovingSide == "Outside" and notes() == {"Stator": "moving", "Rotor": ""}, notes()
    taskpanels.set_field_value(panel.radius, 10)
    assert iface.Radius.Value == 10, "the edit was not live"
    assert panel.reject() and objects.sliding_interfaces(slide_study) == [iface], "Cancel of an edit removed it"
    assert iface.Radius.Value == 42.5 and ("Divisions", "36 * 2") in iface.ExpressionEngine, "Cancel kept the edit"
    assert iface.MovingSide == "Inside" and notes() == {"Stator": "", "Rotor": "moving"}, "Cancel kept the moving side"
    slide_errors = [p.text for p in validation.errors(validation.validate(slide_study))]
    assert not slide_errors, slide_errors
    slide_run = runner.start(slide_study)
    assert slide_run is not None and slide_run.proc.waitForFinished(120000), "the sliding mesher timed out"
    Gui.updateGui()
    assert slide_run.error == "" and not runner.busy(), slide_run.error
    slide_dir = os.path.dirname(slide_run.mesh_file)
    for name in ("pre_geom2D.msh", "rotor_mesh2D.msh"):
        assert os.path.isfile(os.path.join(slide_dir, name)), "no " + name
    assert any("SLIDE_NDIV 72" in line for line in console), "no SLIDE_NDIV line in the log"
    assert any("rotor_mesh2D.msh" in line and "written" in line for line in console), "no rotor file message"
    App.Console.PrintMessage = real_print
    App.closeDocument(slide_doc.Name)
    App.setActiveDocument(doc.Name)
    log.append("sliding interface ok")

    # A 2D Study in a document of its own (one Study per document): setup controls, ticks and undo.
    import Part
    from emsolution import geometry

    assert not commands.COMMANDS["EMS_NewStudy"].IsActive(), "New Study is active in a document with a Study"
    sec = App.newDocument("Section")
    sec.saveAs(os.path.join(tempfile.mkdtemp(), "Section.FCStd"))  # the simulation folder
    App.setActiveDocument(sec.Name)
    commands.ask_study = lambda: ("Cross-section", "2D", "No movement")
    Gui.runCommand("EMS_NewStudy")
    for _ in range(5):
        Gui.updateGui()
    second = objects.find_study(sec)
    assert second is not None and second.Dimension == "2D"
    assert commands.active_study() == second
    assert commands.COMMANDS["EMS_Material"].IsActive() and commands.COMMANDS["EMS_MeshSize"].IsActive()
    assert not commands.COMMANDS["EMS_Excitation"].IsActive(), "excitations are 3D-only for now"
    assert commands.COMMANDS["EMS_RunMesh"].IsActive()
    assert taskpanels.FolderView(second.MaterialsGroup).rows == []
    source = sec.addObject("App::DocumentObjectGroup", "FaceGroup")
    section = sec.addObject("Part::Feature", "Section")
    section.Shape = Part.makePlane(10, 10)
    source.addObject(section)
    part = sec.addObject("App::Part", "SolidPart")
    part.addObject(sec.addObject("Part::Box", "Solid"))
    sec.recompute()
    view = taskpanels.StudyView(second)
    tree = view.tree
    shown = [tree.topLevelItem(i).data(0, QtCore.Qt.UserRole) for i in range(tree.topLevelItemCount())]
    assert source.Name in shown and part.Name not in shown, f"a 2D tree lists faces, not solids: {shown}"
    assert view.diagnostics.text() == "", view.diagnostics.text()
    assert view.run_button.isEnabled()
    assert view.export_notice.toolTip() == f"Writes {jobwriter.mesh_file(second)}", view.export_notice.toolTip()
    long_path = view.export_notice.fontMetrics().horizontalAdvance(view.export_notice.toolTip())
    assert view.export_notice.minimumSizeHint().width() < long_path / 2, "the output path widens the panel"
    run2d = runner.start(second)
    assert run2d is not None and run2d.proc.waitForFinished(120000)
    Gui.updateGui()
    assert run2d.error == "" and not runner.busy(), run2d.error
    assert os.path.basename(run2d.mesh_file) == "pre_geom2D.msh" and os.path.isfile(run2d.mesh_file)
    assert second.MeshResult.FemMesh.NodeCount > 0
    log.append("2D mesh ok")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sec.Name, section.Name, "Face1")  # a click on a 2D body: the Skin Layer is offered
    menu2d = commands.context_menu()
    assert "EMS_SkinLayer" in menu2d, menu2d
    Gui.Selection.addSelection(sec.Name, section.Name, "Edge1")
    assert "EMS_SkinLayer" not in commands.context_menu()
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sec.Name, section.Name)
    Gui.runCommand("EMS_TransfiniteBody")
    texts = [w.text() for w in opened[-1].form.findChildren(QtWidgets.QLabel)]
    assert any(t.startswith("Click a face to structure") for t in texts), texts
    ok()
    Gui.Selection.clearSelection()
    for k in range(1, 5):
        Gui.Selection.addSelection(sec.Name, section.Name, f"Edge{k}")
    Gui.runCommand("EMS_TransfiniteEdges")
    Gui.Selection.addSelection(sec.Name, section.Name, "Face1")
    assert "Face1" not in Gui.Selection.getSelectionEx()[0].SubElementNames, "the edge gate let a face through"
    ok(elements=4)
    (tb,) = objects.transfinite_bodies(second)
    (te,) = objects.transfinite_edges(second)
    assert tb.References == [(section, ("",))], tb.References
    assert te.Elements == 4 and len(te.References[0][1]) == 4, te.References
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sec.Name, section.Name)
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
        sec.removeObject(item.Name)
    second.MeshSizesGroup.RecombinationAlgorithm = "Blossom"
    # Face picks in 2D: a clicked face of a two-face body stays a face; a tree pick and a one-face body are whole.
    blocks = sec.addObject("Part::Feature", "Blocks")
    blocks.Shape = Part.makePlane(10, 10).generalFuse([Part.makePlane(10, 10, App.Vector(10, 0, 0))])[0]
    source.addObject(blocks)
    sec.recompute()
    right = next(f"Face{i}" for i, f in enumerate(blocks.Shape.Faces, 1) if abs(f.CenterOfMass.x - 15) < 1e-6)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sec.Name, blocks.Name, right)
    Gui.runCommand("EMS_TransfiniteBody")
    texts = [w.text() for w in opened[-1].form.findChildren(QtWidgets.QLabel)]
    assert any(t.startswith("Click a face to structure that block") for t in texts), texts
    gate = opened[-1].gate  # what the 3D view may pick while the panel is open
    assert gate.allow(sec, blocks, right) and gate.allow(sec, blocks, "Vertex1"), "faces and corners"
    assert gate.allow(sec, section, "Edge1"), "an edge click on a one-face body is that region"
    assert not gate.allow(sec, blocks, "Edge1"), "an edge of a two-face body is no region"
    ok()
    (tb,) = objects.transfinite_bodies(second)
    assert tb.References == [(blocks, (right,))], tb.References
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sec.Name, blocks.Name)  # tree pick
    Gui.runCommand("EMS_Recombine")
    gate = opened[-1].gate
    assert gate.allow(sec, blocks, right) and gate.allow(sec, section, "Vertex1"), "faces, one-face regions"
    assert not gate.allow(sec, blocks, "Vertex1"), "Recombine takes no corners"
    ok()
    (rc,) = objects.recombine_items(second)
    assert rc.References == [(blocks, ("",))], rc.References
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sec.Name, section.Name, "Face1")  # one-face body: stored whole
    Gui.runCommand("EMS_Recombine")
    ok()
    assert objects.recombine_items(second)[-1].References == [(section, ("",))]
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sec.Name, section.Name, "Edge1")  # an edge click on a one-face body adds the region
    Gui.runCommand("EMS_Recombine")
    ok()
    assert objects.recombine_items(second)[-1].References == [(section, ("",))]
    for item in [tb] + objects.recombine_items(second):  # leave the Study as the rest of the smoke test expects it
        sec.removeObject(item.Name)
    source.removeObject(blocks)
    sec.removeObject(blocks.Name)
    sec.recompute()
    log.append("2D face picks ok")
    view.refresh()
    undo_before = list(sec.UndoNames)
    view.refresh()
    assert list(sec.UndoNames) == undo_before, "populating widgets changed the model"
    tick(tree, source, False)
    assert second.Excluded == [source], ("a fully unticked group is excluded as itself", second.Excluded)
    assert "0 face regions" in view.count.text(), view.count.text()
    tick(tree, source)
    assert second.Excluded == [] and "1 face region" in view.count.text(), view.count.text()
    assert view.run_button.isEnabled(), "a 2D Study with a body can mesh"
    view.movement.setCurrentText("Sliding motion")
    assert second.Movement == "Sliding motion" and study.Movement == "No movement"
    assert view.slide_hint.isVisibleTo(view.form), "no hint for a sliding Study without an interface"
    App.setActiveDocument(doc.Name)
    assert commands.active_study() == study, "the active document's Study is the target"
    App.setActiveDocument(sec.Name)
    assert commands.active_study() == second
    extra = sec.addObject("Part::Feature", "Extra")
    extra.Shape = Part.makePlane(5, 5, App.Vector(20, 0, 0))
    source.addObject(extra)
    sec.recompute()
    view.refresh()
    assert tick(tree, extra, False).parent().checkState(0) == QtCore.Qt.PartiallyChecked
    assert second.Excluded == [extra], ("a partly ticked group keeps its ticks", second.Excluded)
    sec.undo()
    assert second.Excluded == [], second.Excluded
    sec.redo()
    assert second.Excluded == [extra], second.Excluded
    source.removeObject(extra)
    sec.removeObject(extra.Name)
    sec.recompute()
    view.refresh()
    tree.setCurrentItem(tick(tree, section))
    assert highlight.shown() is not None, "a clicked row highlights its bodies"
    highlight.clear()
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sec.Name, second.Name)
    assert second.ViewObject.Proxy.doubleClicked(second.ViewObject)
    assert not Gui.Control.activeDialog(), "double-click Study opened the ID dialog"
    log.append("2D Study setup and undo ok")

    # The selected folder's settings stay isolated and targeting cannot cross documents.
    view = taskpanels.FolderView(study.MeshSizesGroup)
    view.settings.factor.setValue(0.7)
    assert study.MeshSizesGroup.SizeFactor == 0.7
    assert second.MeshSizesGroup.SizeFactor == 1.0
    second_settings = taskpanels.FolderView(second.MeshSizesGroup)
    assert second_settings.settings.box.isEnabled()
    assert "RecombinationAlgorithm" in second_settings.settings.algorithms
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sec.Name, second.Name)
    for _ in range(5):
        Gui.updateGui()
    (actual_tree,) = [
        t
        for t in Gui.getMainWindow().findChildren(QtWidgets.QTreeWidget)
        if t.isVisible() and t.objectName() == "Geometry"
    ]
    tick(actual_tree, source, False)
    assert second.Excluded == [source], second.Excluded
    tick(actual_tree, source)
    assert second.Excluded == [], second.Excluded
    Gui.activeDocument().activeView().viewTop()
    Gui.activeDocument().activeView().fitAll()
    Gui.updateGui()
    Gui.getMainWindow().grab().save(os.path.join(tempfile.gettempdir(), "study-setup.png"))
    another_doc = App.newDocument("Other")
    other_study = objects.make_study(another_doc)
    assert commands.active_study() == other_study
    App.closeDocument(another_doc.Name)
    App.setActiveDocument(sec.Name)
    objects.make_study(sec)  # two Studies in one document: no target, and Validate says why
    assert commands.active_study() is None and not commands.COMMANDS["EMS_Material"].IsActive()
    two = [p.text for p in validation.errors(validation.validate(second))]
    assert any(t.startswith("This document has two Studies") for t in two), two
    App.closeDocument(sec.Name)
    App.setActiveDocument(doc.Name)
    select("B")
    assert commands.active_study() == study, "a closed document's Study remained the target"
    Gui.activateWorkbench("PartWorkbench")
    Gui.activateWorkbench("EMSolutionWorkbench")
    select(study.Name)
    assert not geometry.export_unavailable(study)
    objects.set_excluded(study, [doc.Outside, doc.B])
    view = taskpanels.StudyView(study)
    assert commands.COMMANDS["EMS_RunMesh"].IsActive()
    assert view.run_button.isEnabled()
    doc.openTransaction("Remove material")
    objects.unassign(study, [doc.A])
    doc.commitTransaction()
    view.refresh()
    assert view.diagnostics.text() == "", view.diagnostics.text()  # meshing does not need materials
    assert view.run_button.isEnabled(), "a body without a material disabled generation"
    assert view.export_notice.toolTip() == f"Writes {jobwriter.mesh_file(study)}", view.export_notice.toolTip()
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

    # A document a script built without the GUI has no GuiDocument.xml, so no view providers: opening it must
    # attach ours. A document saved from the GUI keeps its own.
    import zipfile

    headless = App.newDocument("Headless")
    body = headless.addObject("Part::Box", "Body")
    headless.recompute()
    headless_study = objects.make_study(headless, "3D", "Headless")
    objects.make_air_region(headless_study, "Box")
    objects.make_sliding_interface(headless_study)
    material = objects.make_library_material(headless_study, json.dumps(json.loads(lib.Record)))
    objects.assign(headless_study, [body], material, 0)
    objects.make_excitation(headless_study, "Coil", [(body, "Face1")])
    objects.make_mesh_size(headless_study, 2.0, [(body, "")])
    objects.make_recombine(headless_study, [body])
    headless.recompute()
    path = os.path.join(tempfile.mkdtemp(), "Headless.FCStd")
    headless.saveAs(path)
    App.closeDocument(headless.Name)
    stripped = path + ".tmp"
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(stripped, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.namelist():
            if item != "GuiDocument.xml":
                zout.writestr(item, zin.read(item))
    os.replace(stripped, path)
    with zipfile.ZipFile(path) as zin:
        assert "GuiDocument.xml" not in zin.namelist()

    def providers(study_obj):
        """{object Name: view provider class name} for the Study, its folders and everything it owns."""
        return {o.Name: type(o.ViewObject.Proxy).__name__ for o in [study_obj, *objects.study_contents(study_obj)]}

    reopened = App.openDocument(path)
    Gui.updateGui()
    reopened_study = objects.find_study(reopened)
    by_kind = {}
    for obj in [reopened_study, *objects.study_contents(reopened_study)]:
        by_kind[type(obj.Proxy).__name__] = type(obj.ViewObject.Proxy).__name__
    assert by_kind == {
        "Study": "ViewProviderStudy",
        "MaterialLibraryFolder": "ViewProviderFolder",
        "MaterialsFolder": "ViewProviderFolder",
        "ExcitationsFolder": "ViewProviderFolder",
        "MeshSizesFolder": "ViewProviderFolder",
        "AirRegionsFolder": "ViewProviderFolder",
        "AirRegion": "ViewProviderAir",
        "SlidingInterface": "ViewProviderSlidingInterface",
        "LibraryMaterial": "ViewProviderLibraryMaterial",
        "Material": "ViewProviderItem",
        "Excitation": "ViewProviderItem",
        "MeshSize": "ViewProviderItem",
        "Recombine": "ViewProviderItem",
    }, by_kind
    names = providers(reopened_study)
    (reopened_air,) = objects.air_regions(reopened_study)
    assert (reopened_air.ViewObject.Transparency, reopened_air.ViewObject.DisplayMode) == (95, "Flat Lines")
    reopened_color = reopened_air.ViewObject.ShapeAppearance[0].DiffuseColor
    assert all(abs(a - b) < 0.01 for a, b in zip(reopened_color, taskpanels.AIR_COLOR)), reopened_color
    (reopened_slide,) = objects.sliding_interfaces(reopened_study)
    assert reopened_slide.ViewObject.LineWidth == 3
    reopened_air.ViewObject.Transparency = 50  # a user's change must survive a save from the GUI
    App.setActiveDocument(reopened.Name)
    Gui.Selection.clearSelection()
    air_panels.clear()
    assert not Gui.Control.activeDialog()
    assert reopened_air.ViewObject.Proxy.doubleClicked(reopened_air.ViewObject)
    assert len(air_panels) == 1 and Gui.Control.activeDialog(), "the Air Region double-click did not open its panel"
    Gui.Control.closeDialog()
    for _ in range(3):
        Gui.updateGui()
    slide_panels.clear()
    assert reopened_slide.ViewObject.Proxy.doubleClicked(reopened_slide.ViewObject)
    assert len(slide_panels) == 1 and Gui.Control.activeDialog(), "the Sliding Interface double-click did not open"
    Gui.Control.closeDialog()
    for _ in range(3):
        Gui.updateGui()
    reopened.save()  # saved from the GUI: the providers come back as they were, not made again
    App.closeDocument(reopened.Name)
    again = App.openDocument(path)
    Gui.updateGui()
    again_study = objects.find_study(again)
    assert providers(again_study) == names, "a GUI-saved document came back with other view providers"
    (again_air,) = objects.air_regions(again_study)
    assert again_air.ViewObject.Transparency == 50, "an existing view provider was made again"
    App.closeDocument(again.Name)
    log.append("view providers attached on open ok")
    # The motor as two Symmetric Groups: the Materials panel of its parts, and picks on the stator's drawing.
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from tests.freecad_addon import symcases

    sym_doc = App.newDocument("Symmetric")
    sym_study = symcases.motor_study(sym_doc)
    App.setActiveDocument(sym_doc.Name)
    stator_top = objects.symmetric_groups(sym_study)[0]  # its drawing is the full stator
    # An Air Region in a grouped Study: Padding round the two groups, then a ring outside the stator (r 60).
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sym_doc.Name, sym_study.Name)
    for _ in range(5):
        Gui.updateGui()
    assert commands.COMMANDS["EMS_AddAirRegion"].IsActive(), "Air Region is not active in a grouped Study"
    air_panels.clear()
    Gui.runCommand("EMS_AddAirRegion")
    panel = air_panels.pop()
    assert panel.new and Gui.Control.activeDialog(), "the Air Region panel did not open in a grouped Study"
    (sym_air,) = objects.air_regions(sym_study)
    assert sym_air.SizeMode == "Padding", sym_air.SizeMode
    groups = objects.symmetric_groups(sym_study)
    assert sorted(o.Name for o in sym_air.SizedBy) == sorted(g.Name for g in groups), sym_air.SizedBy
    for item in groups:
        assert sym_air.Shape.BoundBox.isInside(item.Shape.BoundBox), "the Air Region does not enclose " + item.Label
    assert panel.accept()
    sym_errors = [p.text for p in validation.errors(validation.validate(sym_study))]
    assert any("crosses or touches Sliding Interface" in t for t in sym_errors), sym_errors
    sym_air.SizeMode = "Manual"
    sym_air.AirShape = "Sector"
    sym_air.InnerRadius = 60
    sym_air.OuterRadius = 90
    sym_doc.recompute()
    sym_errors = [p.text for p in validation.errors(validation.validate(sym_study))]
    assert not [t for t in sym_errors if "Sliding Interface" in t], sym_errors
    (sym_air_mat,) = [m for m in objects.materials(sym_study) if m.Body == sym_air]
    sym_air_lib = sym_air_mat.LibraryMaterial
    sym_doc.removeObject(sym_air_mat.Name)
    sym_doc.removeObject(sym_air.Name)
    sym_doc.removeObject(sym_air_lib.Name)  # the command made it: the motor's library had no Air
    sym_doc.recompute()
    Gui.Selection.clearSelection()
    log.append("air region in a grouped study ok")
    # Materials panel of a grouped Study: no drawing listed without material; a row opens its part's Material.
    mat_view = taskpanels.FolderView(sym_study.MaterialsGroup)
    asked_before = len(asked)
    assert mat_view.missing.isHidden(), mat_view.missing.text()
    mat_view.open_item(0, 0)
    panel = material_panels.pop()
    first = mat_view.rows[0][0]
    assert panel.obj == first and panel.part and not panel.new, panel.obj.Label
    panel.potential.setValue(3)
    assert panel.accept()
    assert first.Potential == 3 and sym_doc.UndoNames[0].startswith("Edit "), (first.Potential, sym_doc.UndoNames)
    mat_view.table.selectRow(1)
    mat_view.assign_rows()
    panel = material_panels.pop()
    assert panel.obj == mat_view.rows[1][0], "Assign… on a part row"
    assert panel.reject()
    mat_view.table.selectAll()  # several part rows: one panel edits one Material, so none is opened
    count = len(material_panels)
    mat_view.assign_rows()
    assert len(material_panels) == count and not Gui.Control.activeDialog(), "Assign… on several part rows"
    assert log[-1].startswith("refused: Select one row"), log[-1]
    first.ViewObject.Proxy.doubleClicked(first.ViewObject)
    panel = material_panels.pop()
    panel.potential.setValue(5)
    assert panel.accept() and first.Potential == 5, "double-click on a part assignment in the tree"
    assert len(asked) == asked_before, asked  # never the several-bodies dialog
    # apply_part_material failing half way: the panel's transaction is aborted, nothing is left changed.
    real_apply = objects.apply_part_material

    def failing(*args):
        real_apply(*args)
        raise RuntimeError("smoke: apply_part_material failed")

    objects.apply_part_material = failing
    undo, potential = list(sym_doc.UndoNames), first.Potential
    first.ViewObject.Proxy.doubleClicked(first.ViewObject)
    panel = material_panels.pop()
    panel.potential.setValue(9)
    try:
        panel.accept()
    except RuntimeError:
        pass
    objects.apply_part_material = real_apply
    assert first.Potential == potential, "a failed edit was left behind"
    assert not sym_doc.HasPendingTransaction and list(sym_doc.UndoNames) == undo, list(sym_doc.UndoNames)
    assert not Gui.Control.activeDialog(), "the failed panel stayed open"
    # The panel failing as it opens: the new Material's transaction is aborted.

    def failing_refresh(panel):
        raise RuntimeError("smoke: the panel failed to open")

    taskpanels.MaterialPanel.refresh = failing_refresh
    undo, count = list(sym_doc.UndoNames), len(objects.materials(sym_study))
    try:
        taskpanels.open_material_panel(sym_study)
    except RuntimeError:
        pass
    del taskpanels.MaterialPanel.refresh
    assert len(objects.materials(sym_study)) == count, "the Material of a panel that failed to open was left behind"
    assert not sym_doc.HasPendingTransaction and list(sym_doc.UndoNames) == undo, list(sym_doc.UndoNames)
    assert not Gui.Control.activeDialog(), "a panel that failed to open was shown"
    # Item panels let the cell bodies be picked: the mesh settings belong on them.
    for air in (True, False):
        assert "CoilCell" in taskpanels.ItemGate(sym_study, ("Edge",), False, air).main, "gate: cell body"
    # Picks on the drawing point at the cell: the panels' pickers and the commands.
    cells = {b.Name for b in objects.cell_bodies(sym_study)}
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sym_doc.Name, stator_top.Name, "Face40")  # a face of some copy
    (whole,) = taskpanels.ITEM_PICKS[objects.Recombine][0](sym_study)
    assert whole[0].Name in cells and whole[1] == "", whole
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sym_doc.Name, stator_top.Name, "Edge100")
    edges = taskpanels.ITEM_PICKS[objects.TransfiniteEdges][0](sym_study)  # an edge two cells share gives both
    assert edges and all(b.Name in cells and s.startswith("Edge") for b, s in edges), edges
    Gui.runCommand("EMS_TransfiniteEdges")
    made = objects.transfinite_edges(sym_study)[-1]
    assert objects.item_refs(made) == edges, objects.item_refs(made)
    Gui.Control.closeDialog()
    # 2D face picks: a face of a copy is that block of the cell (a one-face cell: the whole cell), and a vertex two
    # cells share is a corner of the cell the selection picks only.
    face40 = stator_top.Shape.getElement("Face40")
    names = [
        f"Vertex{i}" for i, v in enumerate(stator_top.Shape.Vertexes, 1) if any(v.isSame(w) for w in face40.Vertexes)
    ]
    shared = next(n for n in names if len(objects.to_cells(sym_study, [(stator_top, n)])) > 1)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sym_doc.Name, stator_top.Name, "Face40")
    Gui.Selection.addSelection(sym_doc.Name, stator_top.Name, shared)
    picks = [(b.Name, s) for b, s in taskpanels.ITEM_PICKS_2D[objects.TransfiniteBody][0](sym_study)]
    assert len(picks) == 2 and picks[0] == (whole[0].Name, ""), picks
    assert picks[1][0] == whole[0].Name and picks[1][1].startswith("Vertex"), picks
    Gui.runCommand("EMS_TransfiniteBody")
    made = objects.transfinite_bodies(sym_study)[-1]
    assert [(b.Name, s) for b, s in objects.item_refs(made)] == picks, objects.item_refs(made)
    Gui.Control.closeDialog()
    # The cell bodies are hidden, the drawing built from them is not: the labels of items on them show.
    from emsolution import labels

    App.setActiveDocument(sym_doc.Name)
    for cell in objects.cell_bodies(sym_study):
        cell.Visibility = False
    labels.show([made])
    overlay = next(iter(labels._overlays.values()))
    overlay.tick()
    assert overlay.tags or overlay.badges, "no labels on the hidden cell"
    labels.clear()
    # A cell cut by a Boolean Fragments: a face click on a copy of one block is that block of the cell body.
    frag = symcases.coil_fragments(sym_doc)
    stator_top.Cells = [frag if c.Name == "CoilCell" else c for c in stator_top.Cells]
    objects.sync_rows(stator_top)
    sym_doc.recompute()
    outer = symcases.sector(43, 50, 10, 15).Area
    copy = next(f"Face{i}" for i, f in enumerate(stator_top.Shape.Faces, 1) if abs(f.Area - outer) < 1e-6)
    block = next(f"Face{i}" for i, f in enumerate(frag.Shape.Faces, 1) if abs(f.Area - outer) < 1e-6)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sym_doc.Name, stator_top.Name, copy)
    for cls in (objects.TransfiniteBody, objects.Recombine):
        picks = [(b.Name, s) for b, s in taskpanels.ITEM_PICKS_2D[cls][0](sym_study)]
        assert picks == [(frag.Name, block)], picks
    # An older version's Symmetric Mesh item opens as a warning, not a panel.
    old = sym_doc.addObject("App::FeaturePython", "SymmetricMesh")
    old.Proxy = objects.SymmetricMesh()
    old.Label = "Old"
    sym_study.MeshSizesGroup.addObject(old)
    taskpanels.attach_view_provider(old)
    old.ViewObject.Proxy.doubleClicked(old.ViewObject)
    assert not Gui.Control.activeDialog(), "a panel for the older item"
    assert log[-1].startswith("refused: Symmetric Mesh Old is from an older version"), log[-1]
    Gui.Selection.removeSelectionGate()  # the item panels closed above with closeDialog left their gates
    App.closeDocument(sym_doc.Name)
    App.setActiveDocument(doc.Name)
    log.append("symmetric study ok")
    # Symmetric Group: the command on the stator cells, rules through the panel's buttons, a live drawing.
    import math

    group_doc = App.newDocument("Groups")
    group_info = symcases.motor_doc(group_doc)  # the cells and, for Read from drawing, their chains
    group_study = objects.make_study(group_doc, "2D")
    App.setActiveDocument(group_doc.Name)
    group_panels, tables, windings = [], [], []
    real_group_panel = taskpanels.SymmetricGroupPanel

    class RecordedGroupPanel(real_group_panel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            group_panels.append(self)

    taskpanels.SymmetricGroupPanel = RecordedGroupPanel
    stator_cells = group_info["stator_cells"]

    def run_group_command():
        Gui.Selection.clearSelection()
        for cell in stator_cells:
            Gui.Selection.addSelection(group_doc.Name, cell.Name)
        Gui.runCommand("EMS_SymmetricGroup")
        return group_panels.pop()

    undo, visible = list(group_doc.UndoNames), [c.Visibility for c in stator_cells]
    panel = run_group_command()
    (group,) = objects.symmetric_groups(group_study)
    assert panel.new and Gui.Control.activeDialog() and list(group.Cells) == stator_cells, list(group.Cells)
    assert os.path.exists(group.ViewObject.Proxy.getIcon()), group.ViewObject.Proxy.getIcon()
    assert panel.side.isHidden(), "the side shows without Sliding motion"
    faces = [len(group.Shape.Faces)]
    assert faces == [3] and panel.summary.text() == "1 copy, 3 parts", (faces, panel.summary.text())
    panel.add_mirror.click()
    faces.append(len(group.Shape.Faces))
    panel.direction[0].setValue(-math.sin(math.radians(15)))  # the mirror at the cell's 15° edge
    panel.direction[1].setValue(math.cos(math.radians(15)))
    panel.add_rotate.click()  # 90° × 4 to start with
    faces.append(len(group.Shape.Faces))
    panel.step.setValue(30)
    assert "covers 120 degrees" in panel.problem.text(), panel.problem.text()
    panel.count.setValue(12)
    faces.append(len(group.Shape.Faces))
    assert faces == [3, 6, 24, 72], faces
    assert panel.summary.text() == "24 copies, 3 parts" and panel.problem.isHidden(), panel.summary.text()
    assert [r["kind"] for r in objects.rules_of(group)] == ["mirror", "rotate"], objects.rules_of(group)
    panel.rule_up.click()  # the order is visible: rotate first, then mirror, and back
    assert objects.rules_of(group)[0]["kind"] == "rotate" and panel.rules.currentRow() == 0
    panel.rule_down.click()
    assert objects.rules_of(group)[1]["count"] == 12 and len(group.Shape.Faces) == 72
    # A row's parts named by a table: generate a winding.
    coil = [r["cell"] for r in objects.rows_of(group)].index("CoilCell")
    mode = panel.rows.cellWidget(coil, 1)
    mode.setCurrentIndex(mode.findData("table"))
    assert objects.rows_of(group)[coil]["mode"] == "table" and panel.table_button.isEnabled()
    assert "table of CoilCell has 0 names" in panel.problem.text(), panel.problem.text()

    def drive_table(dialog):
        tables.append(dialog)
        dialog.generate.click()
        dialog.accept()
        return dialog.result()

    def drive_winding(dialog):
        windings.append(dialog)
        dialog.pole_pairs.setValue(2)
        return True

    real_ask_winding = taskpanels.ask_winding
    taskpanels.TableDialog.exec = drive_table
    taskpanels.ask_winding = drive_winding
    panel.table_button.click()
    del taskpanels.TableDialog.exec
    taskpanels.ask_winding = real_ask_winding
    assert windings[0].slots.value() == 12 and windings[0].span.value() == 3, windings[0].values()
    names = [tables[0].table.item(k, 1).text() for k in range(tables[0].table.rowCount())]
    assert len(names) == 24 and all(names) and objects.rows_of(group)[coil]["table"] == names, names
    assert panel.summary.text() == "24 copies, 8 parts" and panel.problem.isHidden(), panel.summary.text()
    # Cancel removes the new group.
    panel.reject()
    assert not objects.symmetric_groups(group_study) and list(group_doc.UndoNames) == undo, list(group_doc.UndoNames)
    assert not Gui.Control.activeDialog() and [c.Visibility for c in stator_cells] == visible, "Cancel left something"
    # Read from drawing fills the cells and the rules; OK makes a Material per part and hides the cells.
    panel = run_group_command()
    (group,) = objects.symmetric_groups(group_study)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(group_doc.Name, group_info["stator_top"].Name)
    panel.read_drawing.click()
    assert list(group.Cells) == stator_cells and len(group.Shape.Faces) == 72, list(group.Cells)
    assert [r["kind"] for r in objects.rules_of(group)] == ["mirror", "rotate"], objects.rules_of(group)
    assert panel.rules.count() == 2 and panel.summary.text() == "24 copies, 3 parts", panel.summary.text()
    panel.name.setText("Stator group")
    assert panel.accept() and not Gui.Control.activeDialog()
    assert group.Label == "Stator group" and group_doc.UndoNames[0] == "Add Symmetric Group", group_doc.UndoNames
    assert len(objects.part_assignments(group_study)) == 3, [m.Label for m in objects.part_assignments(group_study)]
    assert not any(c.Visibility for c in stator_cells) and group.Visibility, "the cells are not hidden"
    group_view = taskpanels.StudyView(group_study)  # the chain the rules were read from is the group's drawing
    drawing_row = rows_of(group_view.tree)[group_info["stator_top"].Name]
    assert drawing_row.text(1) == f"drawing of Symmetric Group {objects.display_name(group)}", drawing_row.text(1)
    assert drawing_row.isDisabled() and drawing_row.checkState(0) == QtCore.Qt.Unchecked
    del group_view
    # Double-click reopens it; a part that goes takes its Material along, and the panel says so.
    group.ViewObject.Proxy.doubleClicked(group.ViewObject)
    panel = group_panels.pop()
    assert not panel.new and Gui.Control.activeDialog() and panel.rules.count() == 2
    mode = panel.rows.cellWidget(coil, 1)
    mode.setCurrentIndex(mode.findData("each"))
    assert panel.summary.text() == "24 copies, 26 parts", panel.summary.text()
    assert panel.accept() and group_doc.UndoNames[0] == "Edit Stator group", group_doc.UndoNames
    assert len(objects.part_assignments(group_study)) == 26, len(objects.part_assignments(group_study))
    assert log[-1].startswith("refused: The parts of these Materials are gone") and "CoilCell" in log[-1], log[-1]
    sizes_view = taskpanels.FolderView(group_study.MeshSizesGroup)
    undo = list(group_doc.UndoNames)
    sizes_view.open_item([r[0] for r in sizes_view.rows].index(group), 0)
    panel = group_panels.pop()
    assert Gui.Control.activeDialog() and panel.reject() and list(group_doc.UndoNames) == undo, "Mesh Sizes panel"
    # OK on a group Validate would refuse: a table not filled in keeps the Materials of the row's parts.
    said = len(log)
    group.ViewObject.Proxy.doubleClicked(group.ViewObject)
    panel = group_panels.pop()
    mode = panel.rows.cellWidget(coil, 1)
    mode.setCurrentIndex(mode.findData("table"))
    assert "table of CoilCell has 0 names" in panel.problem.text(), panel.problem.text()
    assert panel.accept() and len(objects.part_assignments(group_study)) == 26, "OK removed the Materials of a table"
    assert len(log) == said, log[said:]
    group.ViewObject.Proxy.doubleClicked(group.ViewObject)
    panel = group_panels.pop()
    mode = panel.rows.cellWidget(coil, 1)
    mode.setCurrentIndex(mode.findData("each"))
    assert panel.accept() and len(objects.part_assignments(group_study)) == 26 and len(log) == said, log[said:]
    # Broken rules leave the drawing empty: OK shows the cells instead of hiding the model; fixed, it hides them again.
    group.ViewObject.Proxy.doubleClicked(group.ViewObject)
    panel = group_panels.pop()
    panel.rules.setCurrentRow(0)
    normal = [b.value() for b in panel.direction]
    for box in panel.direction:
        box.setValue(0)
    assert "mirror normal is zero" in panel.problem.text() and not group.Shape.Faces, panel.problem.text()
    assert panel.accept() and all(c.Visibility for c in stator_cells), "OK hid the cells of an empty drawing"
    assert len(objects.part_assignments(group_study)) == 26 and len(log) == said, log[said:]
    group.ViewObject.Proxy.doubleClicked(group.ViewObject)
    panel = group_panels.pop()
    panel.rules.setCurrentRow(0)
    for box, value in zip(panel.direction, normal):
        box.setValue(value)
    assert len(group.Shape.Faces) == 72 and panel.problem.isHidden(), panel.problem.text()
    assert panel.accept() and not any(c.Visibility for c in stator_cells), "the cells are not hidden again"
    # A cell taken out of the group shows again: no drawing shows it any more.
    group.ViewObject.Proxy.doubleClicked(group.ViewObject)
    panel = group_panels.pop()
    Gui.Selection.clearSelection()
    for cell in stator_cells[:2]:
        Gui.Selection.addSelection(group_doc.Name, cell.Name)
    panel.use_selection.click()
    assert list(group.Cells) == stator_cells[:2], list(group.Cells)
    assert panel.accept() and stator_cells[2].Visibility, "the cell taken out of the group stays hidden"
    assert not any(c.Visibility for c in stator_cells[:2]), "the cells left in the group are not hidden"
    group.ViewObject.Proxy.doubleClicked(group.ViewObject)
    panel = group_panels.pop()
    Gui.Selection.clearSelection()
    for cell in stator_cells:
        Gui.Selection.addSelection(group_doc.Name, cell.Name)
    panel.use_selection.click()
    assert panel.accept() and not any(c.Visibility for c in stator_cells) and list(group.Cells) == stator_cells
    log.append("group panel OK follows Validate ok")
    # Moving the App::Part that holds the cells: Cells links the cells only, so the drawing stays where it was until
    # the panel (or Validate) brings it along.
    holder = group_doc.addObject("App::Part", "Holder")
    for cell in stator_cells:
        holder.addObject(cell)
    group_doc.recompute()
    holder.Placement = App.Placement(App.Vector(0, 0, 5), App.Rotation())
    group_doc.recompute()
    assert objects.stale_drawing(group) and group.Shape.BoundBox.ZMin == 0, group.Shape.BoundBox
    group.ViewObject.Proxy.doubleClicked(group.ViewObject)
    panel = group_panels.pop()
    assert panel.reject() and abs(group.Shape.BoundBox.ZMin - 5) < 1e-9, group.Shape.BoundBox
    # A cell object cut into three faces by a Boolean Fragments (D-01) is one row; Split and Join through the panel.
    blocks_doc = App.newDocument("Blocks")
    blocks_cells = symcases.transformer_doc(blocks_doc)
    blocks_study = objects.make_study(blocks_doc, "2D")
    App.setActiveDocument(blocks_doc.Name)
    Gui.Selection.clearSelection()
    for key in ("core", "coil", "air"):
        Gui.Selection.addSelection(blocks_doc.Name, blocks_cells[key].Name)
    Gui.runCommand("EMS_SymmetricGroup")
    panel = group_panels.pop()
    (blocks_group,) = objects.symmetric_groups(blocks_study)

    def row_labels():
        return [panel.rows.item(k, 0).text() for k in range(panel.rows.rowCount())]

    assert row_labels() == ["CoreCell", "CoilCell", "AirCell"], row_labels()
    assert panel.summary.text() == "1 copy, 3 parts" and len(blocks_group.Shape.Faces) == 5, panel.summary.text()
    panel.rows.setCurrentCell(1, 0)  # the coil has one face: nothing to split or join
    assert not panel.split_button.isEnabled() and not panel.join_button.isEnabled()
    panel.rows.setCurrentCell(0, 0)
    assert panel.split_button.isEnabled() and not panel.join_button.isEnabled()
    panel.split_button.click()
    assert row_labels() == ["CoreCell_1", "CoreCell_2", "CoreCell_3", "CoilCell", "AirCell"], row_labels()
    assert panel.summary.text() == "1 copy, 5 parts" and len(blocks_group.Shape.Faces) == 5, panel.summary.text()
    panel.rows.setCurrentCell(2, 0)
    assert panel.join_button.isEnabled() and not panel.split_button.isEnabled()
    panel.join_button.click()
    assert row_labels() == ["CoreCell", "CoilCell", "AirCell"] and panel.rows.currentRow() == 0, row_labels()
    panel.split_button.click()  # OK with the blocks split: a Material per block
    assert panel.accept() and not Gui.Control.activeDialog()
    names = sorted(m.GroupName for m in objects.part_assignments(blocks_study))
    assert names == ["AirCell", "CoilCell", "CoreCell_1", "CoreCell_2", "CoreCell_3"], names
    blocks_group.ViewObject.Proxy.doubleClicked(blocks_group.ViewObject)
    panel = group_panels.pop()
    panel.rows.setCurrentCell(0, 0)
    panel.join_button.click()
    assert panel.accept() and log[-1].startswith("refused: The parts of these Materials are gone"), log[-1]
    names = sorted(m.GroupName for m in objects.part_assignments(blocks_study))
    assert names == ["AirCell", "CoilCell", "CoreCell"], names
    # The core part's Material lists its one copy as one line of three faces, and labels it once.
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(blocks_doc.Name, blocks_group.Name, "Face2")
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    assert panel.part and panel.obj.GroupName == "CoreCell" and len(panel.current) == 3, panel.current
    lines = [panel.refs.item(k).text() for k in range(panel.refs.count())]
    assert len(lines) == 1 and lines[0].endswith(".Face1, Face2, Face3"), lines
    assert len(labels._one_per_copy(panel.obj, panel.current)) == 1
    assert panel.reject()
    App.closeDocument(blocks_doc.Name)
    App.setActiveDocument(group_doc.Name)
    log.append("split and join ok")
    taskpanels.SymmetricGroupPanel = real_group_panel
    App.closeDocument(group_doc.Name)
    App.setActiveDocument(doc.Name)
    log.append("symmetric group ok")
    # Picking on a group's drawing: Materials, mesh settings and Excitations work on its copies.
    from tests.freecad_addon.materialdata import COPPER, STEEL, record

    rules = [
        {"kind": "mirror", "point": [0, 0, 0], "normal": [-math.sin(math.radians(15)), math.cos(math.radians(15)), 0]},
        {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 30, "count": 12},
    ]

    def click(document, item, sub):
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(document.Name, item.Name, sub)

    pick_doc = App.newDocument("Picking")
    pick_info = symcases.group_motor_doc(pick_doc)
    free_air = symcases.feature(pick_doc, "FreeAir", symcases.sector(60, 70, 0, 15))
    pick_doc.recompute()
    pick_study = objects.make_study(pick_doc, "2D")
    App.setActiveDocument(pick_doc.Name)
    objects.set_excluded(pick_study, pick_info["rotor_cells"])  # the stator group and the free air
    steel = objects.make_library_material(
        pick_study, json.dumps(record("user:steel", "Steel", "electrical_steel", STEEL))
    )
    copper = objects.make_library_material(pick_study, json.dumps(record("user:copper", "Copper", "conductor", COPPER)))
    pick_group = objects.make_symmetric_group(pick_study, pick_info["stator_cells"], rules=rules, name="Stator")
    objects.sync_parts(pick_study)
    pick_doc.recompute()
    # The Study tree: the group is a ticked row after the document's, its cell objects under it and nowhere else.
    pick_view = taskpanels.StudyView(pick_study)
    tops = [pick_view.tree.topLevelItem(i) for i in range(pick_view.tree.topLevelItemCount())]
    group_row = tops[-1]
    assert group_row.data(0, QtCore.Qt.UserRole) == pick_group.Name and group_row.isDisabled()
    assert group_row.checkState(0) == QtCore.Qt.Checked and group_row.text(1) == "", group_row.text(1)
    cell_rows = [group_row.child(i) for i in range(group_row.childCount())]
    assert [r.data(0, QtCore.Qt.UserRole) for r in cell_rows] == [c.Name for c in pick_info["stator_cells"]]
    note = f"meshed by Symmetric Group {objects.display_name(pick_group)}"
    assert all(r.text(1) == note and r.isDisabled() and r.checkState(0) == QtCore.Qt.Checked for r in cell_rows)
    names = [t.data(0, QtCore.Qt.UserRole) for t in tops[:-1]]
    assert free_air.Name in names and not set(names) & {c.Name for c in pick_info["stator_cells"]}, names
    assert all(rows_of(pick_view.tree)[c.Name].checkState(0) == QtCore.Qt.Unchecked for c in pick_info["rotor_cells"])
    del pick_view, tops, group_row, cell_rows
    pick_rows = objects.rows_of(pick_group)
    pick_coil = [r["cell"] for r in pick_rows].index("CoilCell")

    def face_of(row, copy):
        return f"Face{copy * len(pick_rows) + row + 1}"

    # A click on a coil copy opens the Material of that coil's part; its library material is changed there.
    click(pick_doc, pick_group, face_of(pick_coil, 5))
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    (coil_part,) = [m for m in objects.part_assignments(pick_study) if m.PartKey == "CoilCell"]
    assert panel.obj is coil_part and not panel.new and panel.part, panel.obj.Label
    assert panel.current == objects.part_refs(coil_part) and panel.refs.count() == 24, panel.current
    assert not panel.add_button.isEnabled() and not panel.remove_button.isEnabled()
    panel.material.setCurrentIndex(panel.material.findData(copper.Name))
    panel.potential.setValue(7)
    panel.name.setText("Coil")
    assert panel.accept() and not Gui.Control.activeDialog()
    assert (
        coil_part.LibraryMaterial == copper and coil_part.Potential == 7 and objects.display_name(coil_part) == "Coil"
    )
    assert coil_part.PartKey == "CoilCell" and len(objects.part_assignments(pick_study)) == 3
    # Cancel leaves the part as it was.
    click(pick_doc, pick_group, face_of(pick_coil, 0))
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    assert panel.obj is coil_part
    panel.material.setCurrentIndex(panel.material.findData(steel.Name))
    assert panel.reject() and coil_part.LibraryMaterial == copper
    # Two parts picked: refused, no panel.
    iron = [r["cell"] for r in pick_rows].index("StatorIronCell")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(pick_doc.Name, pick_group.Name, face_of(pick_coil, 1))
    Gui.Selection.addSelection(pick_doc.Name, pick_group.Name, face_of(iron, 1))
    warned_before = len(warned)
    Gui.runCommand("EMS_Material")
    assert not material_panels and not Gui.Control.activeDialog() and len(warned) == warned_before + 1, warned
    # "All parts of this object": every copy of the coil is a part of its own, and one click sets them all.
    pick_rows[pick_coil]["mode"] = "each"
    objects.set_rows(pick_group, pick_rows)
    pick_doc.recompute()
    objects.sync_parts(pick_study)
    click(pick_doc, pick_group, face_of(pick_coil, 7))
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    each = objects.row_parts(pick_group, pick_rows[pick_coil])
    assert panel.obj.PartKey == each[7] and panel.refs.count() == 1, panel.obj.PartKey
    panel.material.setCurrentIndex(panel.material.findData(steel.Name))
    panel.all_parts.click()
    coils = [m for m in objects.part_assignments(pick_study) if m.PartKey in each]
    irons = [m for m in objects.part_assignments(pick_study) if m.PartKey not in each]
    assert len(coils) == 24 and all(m.LibraryMaterial == steel for m in coils), [m.Label for m in coils]
    assert all(m.LibraryMaterial != steel for m in irons), [m.Label for m in irons]
    assert objects.rows_of(pick_group)[pick_coil]["material"] == steel.Name
    assert panel.accept()
    # A free body gets the ordinary Material panel.
    click(pick_doc, free_air, "Face1")
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    assert panel.new and not panel.part and panel.current == [(free_air, "")], panel.current
    assert panel.add_button.isEnabled()
    assert panel.reject()
    # Mesh settings picked on the drawing move to the cell, and their panels accept the group.
    cell_coil = pick_info["stator_cells"][1]
    click(pick_doc, pick_group, face_of(pick_coil, 9))
    Gui.runCommand("EMS_MeshSize")
    panel = opened.pop()
    assert objects.item_refs(panel.obj) == [(cell_coil, "Face1")], objects.item_refs(panel.obj)
    assert pick_group.Name in panel.gate.main
    assert panel.reject()
    gate_no_air = taskpanels.ItemGate(pick_study, ("Face",), False, air=False)
    assert pick_group.Name in gate_no_air.main and cell_coil.Name in gate_no_air.main, gate_no_air.main
    click(pick_doc, pick_group, face_of(pick_coil, 9))
    assert taskpanels.picked_bodies(pick_study) == [(cell_coil, "")], taskpanels.picked_bodies(pick_study)
    assert taskpanels.selected_face_picks(pick_study, False) == [(cell_coil, "")]
    Gui.Selection.clearSelection()
    App.closeDocument(pick_doc.Name)
    # 3D: a face of the drawing finds its solid and its part; an Excitation stays on the drawing's face.
    pick3_doc = App.newDocument("Picking3D")
    pick3_info = symcases.group_motor_doc(pick3_doc, height=10)
    pick3_study = objects.make_study(pick3_doc, "3D")
    App.setActiveDocument(pick3_doc.Name)
    group3 = objects.make_symmetric_group(pick3_study, pick3_info["stator_cells"], rules=rules, name="Stator")
    objects.sync_parts(pick3_study)
    pick3_doc.recompute()
    solid_asks, solid_answers = [], []
    real_ask_solid = taskpanels.ask_solid
    taskpanels.ask_solid = lambda face, names: (solid_asks.append((face, names)), solid_answers.pop(0))[1]
    rows3 = objects.rows_of(group3)
    faces3 = range(1, len(group3.Shape.Faces) + 1)
    single3 = next(f"Face{i}" for i in faces3 if len(objects.face_solids(group3.Shape, f"Face{i}")) == 1)

    def parts_of(face):
        return {objects.part_name_of(group3, s) for s in objects.face_solids(group3.Shape, face)}

    shared3 = next(  # a face between two solids of two parts
        f"Face{i}"
        for i in faces3
        if len(objects.face_solids(group3.Shape, f"Face{i}")) == 2 and len(parts_of(f"Face{i}")) == 2
    )
    same3 = next(  # a face between two solids of one part: the iron and its mirrored copy
        f"Face{i}"
        for i in faces3
        if len(objects.face_solids(group3.Shape, f"Face{i}")) == 2 and len(parts_of(f"Face{i}")) == 1
    )
    click(pick3_doc, group3, single3)
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    (single_owner,) = objects.face_solids(group3.Shape, single3)
    row, copy = objects.element_owner(group3, single_owner)
    want = objects.row_parts(group3, rows3[row])[copy]
    assert panel.part and panel.obj.PartKey == want and not solid_asks, (panel.obj.PartKey, want, solid_asks)
    assert panel.reject()
    click(pick3_doc, group3, shared3)  # a face of two solids without a picked point: asked
    solid_answers.append(objects.face_solids(group3.Shape, shared3)[1])
    Gui.runCommand("EMS_Material")
    panel = material_panels.pop()
    taken = objects.element_owner(group3, objects.face_solids(group3.Shape, shared3)[1])
    assert len(solid_asks) == 1 and panel.part, solid_asks
    assert panel.obj.PartKey == objects.row_parts(group3, rows3[taken[0]])[taken[1]], panel.obj.PartKey
    assert panel.reject()
    solid_answers.append(None)  # Cancel: no panel, no warning
    warned_before = len(warned)
    Gui.runCommand("EMS_Material")
    assert not material_panels and not Gui.Control.activeDialog() and len(warned) == warned_before
    click(pick3_doc, group3, same3)  # both solids are in one part: no question, either answer gives that part
    asked_before = len(solid_asks)
    picked3, cancelled3 = taskpanels.selected_group_pieces(pick3_study)
    assert len(solid_asks) == asked_before and not cancelled3 and len(picked3) == 1, (solid_asks, picked3)
    assert objects.part_name_of(group3, picked3[0][1]) == next(iter(parts_of(same3))), picked3
    # Two drawings selected, the first click on a face of two solids: the question must not hide the second drawing.
    rotor3 = objects.make_symmetric_group(
        pick3_study,
        pick3_info["rotor_cells"],
        rules=[{"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 45, "count": 8}],
        name="Rotor",
    )
    pick3_doc.recompute()
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(pick3_doc.Name, group3.Name, shared3)
    Gui.Selection.addSelection(pick3_doc.Name, rotor3.Name, "Face1")
    asked_before = len(solid_asks)
    solid_answers.append(objects.face_solids(group3.Shape, shared3)[0])
    picked3, cancelled3 = taskpanels.selected_group_pieces(pick3_study)
    assert not cancelled3 and [b.Name for b, _ in picked3] == [group3.Name, rotor3.Name], picked3
    assert len(solid_asks) == asked_before + 1, solid_asks
    taskpanels.ask_solid = real_ask_solid
    click(pick3_doc, group3, single3)
    Gui.runCommand("EMS_Excitation")
    (terminal,) = objects.excitations(pick3_study)
    assert objects.item_refs(terminal) == [(group3, single3)], objects.item_refs(terminal)
    Gui.Selection.clearSelection()
    App.closeDocument(pick3_doc.Name)
    App.setActiveDocument(doc.Name)
    log.append("picking on the drawing ok")
    App.closeDocument(doc.Name)

    # A face clicked on a link body arrives as a pick the Mesh Size panel takes, also for a link inside a Part.
    link_doc = App.newDocument("LinkPick")
    coil = link_doc.addObject("Part::Box", "Coil")
    coil_link = link_doc.addObject("App::Link", "CoilLink")
    coil_link.LinkedObject = coil
    coil_link.Placement.Base = App.Vector(50, 0, 0)
    link_holder = link_doc.addObject("App::Part", "LinkHolder")
    inner_link = link_doc.addObject("App::Link", "InnerLink")
    inner_link.LinkedObject = coil
    inner_link.Placement.Base = App.Vector(0, 50, 0)
    link_holder.addObject(inner_link)
    link_study = objects.make_study(link_doc, "3D")
    link_doc.recompute()
    App.setActiveDocument(link_doc.Name)
    assert [b.Name for b in objects.study_bodies(link_study)] == ["Coil", "CoilLink", "InnerLink"]
    Gui.Selection.clearSelection()
    Gui.runCommand("EMS_MeshSize")
    panel = opened.pop()
    forms = []
    for top, sub in (("CoilLink", "Face1"), ("LinkHolder", "InnerLink.Face1")):
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(link_doc.Name, top, sub)  # what a click in the 3D view selects, through the gate
        forms.append([(s.Object.Name, s.SubElementNames) for s in Gui.Selection.getSelectionEx()])
        panel.add_selection()
    log.append(f"link face picks arrive as {forms}")
    assert forms == [[("CoilLink", ("Face1",))], [("InnerLink", ("Face1",))]], forms
    assert [(b.Name, s) for b, s in panel.current] == [("CoilLink", "Face1"), ("InnerLink", "Face1")], panel.current
    panel.size.setValue(2.0)
    assert panel.accept()
    (link_size,) = objects.mesh_sizes(link_study)
    assert objects.item_refs(link_size) == [(coil_link, "Face1"), (inner_link, "Face1")], objects.item_refs(link_size)
    App.closeDocument(link_doc.Name)
    log.append("link face picks ok")

    label_doc = App.newDocument("Labels")
    label_box = label_doc.addObject("Part::Box", "Box")
    label_doc.recompute()
    label_study = objects.make_study(label_doc)
    App.setActiveDocument(label_doc.Name)
    App.ParamGet(labels.PREFS).RemBool("LabelsOfOthers")
    assert not labels.others_wanted(), "the labels of the other items start off"
    App.ParamGet(labels.PREFS).SetBool("LabelsOfOthers", True)
    sized = objects.make_mesh_size(label_study, 2.0, [(label_box, "Edge1"), (label_box, "Face1")])
    objects.make_mesh_size(label_study, 4.0, [(label_box, "")])
    objects.make_transfinite_edges(label_study, 7, [(label_box, "Edge2")])
    objects.make_excitation(label_study, "Terminal", [(label_box, "Face2")])  # not a mesh item: never shown with them

    def label_texts():
        overlay = next(iter(labels._overlays.values()))
        overlay.tick()  # builds the tags and badges
        return sorted(t["text"] for t in overlay.tags), [[text for _, _, text in b["items"]] for b in overlay.badges]

    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(label_doc.Name, sized.Name)  # a click on the item shows its labels only
    taskpanels._observer.update()
    assert label_texts() == (["2 mm", "2 mm"], []), label_texts()
    panel = taskpanels.ItemPanel(sized)  # its panel adds the other items' labels, as the check box says
    assert panel.others.isChecked()
    panel.size.setValue(3.0)  # typed, not saved: the tags follow
    assert label_texts() == (["3 mm", "3 mm", "7"], [["Mesh size: 4 mm"]]), label_texts()
    panel.size.setValue(2.0)
    assert label_texts() == (["2 mm", "2 mm", "7"], [["Mesh size: 4 mm"]]), label_texts()
    panel.others.setChecked(False)
    assert label_texts() == (["2 mm", "2 mm"], []), label_texts()
    panel.others.setChecked(True)
    label_box.Visibility = False  # hiding a body hides its labels
    assert label_texts() == ([], []), label_texts()
    label_box.Visibility = True
    assert label_texts() == (["2 mm", "2 mm", "7"], [["Mesh size: 4 mm"]]), label_texts()
    panel.close()
    assert not labels._overlays
    labels.show([sized])  # closing the document takes its labels with it, and a new view does not inherit them
    App.closeDocument(label_doc.Name)
    for _ in range(5):
        Gui.updateGui()
    assert not labels._overlays, labels._overlays
    label_doc = App.newDocument("Labels")
    label_box = label_doc.addObject("Part::Box", "Box")
    label_doc.recompute()
    label_study = objects.make_study(label_doc)
    sized = objects.make_mesh_size(label_study, 2.0, [(label_box, "Edge1")])
    labels.show([sized])
    overlay = next(iter(labels._overlays.values()))
    overlay.tick()
    assert [t["text"] for t in overlay.tags] == ["2 mm"], overlay.tags
    labels.clear()
    App.closeDocument(label_doc.Name)
    log.append("labels ok")


try:
    main()
    log.append("PASS")
except Exception:
    log.append(traceback.format_exc())
    log.append("FAIL")
with open(RESULT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(log) + "\n")
os._exit(0)
