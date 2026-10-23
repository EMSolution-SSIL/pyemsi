"""Toolbar and menu commands."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from . import airshapes, geometry, icon, objects, runner, studymaterials, taskpanels


def ask_study():
    dialog = QtWidgets.QDialog(Gui.getMainWindow())
    dialog.setWindowTitle("New EMSolution Study")
    layout = QtWidgets.QFormLayout(dialog)
    name = QtWidgets.QLineEdit("EMSolution Study")
    dimension = QtWidgets.QComboBox()
    dimension.addItems(["3D", "2D"])
    layout.addRow("Name", name)
    layout.addRow("Dimension", dimension)
    buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addRow(buttons)
    if dialog.exec() == QtWidgets.QDialog.Accepted:
        return name.text().strip() or "EMSolution Study", dimension.currentText()
    return None


def ask_text(title, label, default):
    text, ok = QtWidgets.QInputDialog.getText(Gui.getMainWindow(), title, label, text=default)
    return text.strip() if ok and text.strip() else None


def warn(text):
    QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "EMSolution", text)


def active_study():
    return taskpanels.active_study()


def assignment_study():
    study = active_study()
    if study is None:
        warn("Select the Study you want to edit first.")
    return study


def _create(study, title, make):
    doc = study.Document
    doc.openTransaction(title)
    obj = make()
    taskpanels.attach_view_provider(obj)
    doc.commitTransaction()
    doc.recompute()
    return obj


def _create_and_edit(study, title, make):
    """Make the item and open its panel; the transaction stays open until OK or Cancel."""
    doc = study.Document
    doc.openTransaction(title)
    obj = make()
    taskpanels.attach_view_provider(obj)
    doc.recompute()
    Gui.Control.showDialog(taskpanels.ItemPanel(obj, new=True))


def gate(study, bodies, item_cls=None):
    """Warn and return False unless bodies can get assignments (of an item of class item_cls, which may refuse the
    air); with no main geometry, select the Study."""
    problem = objects.assignment_problem(study, bodies) or objects.air_refusal(item_cls, bodies)
    if problem == objects.NO_MAIN_GEOMETRY:
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(study)  # its panel shows the main geometry choice
    if problem:
        warn(problem)
    return not problem


class _StudyCommand:
    def IsActive(self):
        return active_study() is not None and not Gui.Control.activeDialog()


class NewStudy:
    def GetResources(self):
        return {
            "Pixmap": icon("study"),
            "MenuText": "New Study",
            "ToolTip": "Create an EMSolution study in this document",
        }

    def IsActive(self):
        return App.ActiveDocument is not None and not Gui.Control.activeDialog()

    def Activated(self):
        doc = App.ActiveDocument
        choice = ask_study()
        if choice is None:
            return
        label, dimension = choice
        doc.openTransaction("New Study")
        study = objects.make_study(doc, dimension, label)
        taskpanels.attach_view_provider(study)
        doc.commitTransaction()
        doc.recompute()
        taskpanels.set_active_study(study)
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(study)


class AssignMaterial(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("material"),
            "MenuText": "Assign Material",
            "ToolTip": "Give the selected bodies a material from the Material Library",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        bodies = taskpanels.selected_bodies()
        if not bodies:
            return warn("Select one or more bodies first.")
        tops = {item.Top.Name for item in objects.symmetric_items(study) if item.Top is not None}
        pieces = [(b, s) for b, s in taskpanels.selected_faces() if b.Name in tops]
        if pieces:
            if gate(study, [b for b, _ in pieces]):
                taskpanels.ask_piece_assignment(study, pieces)
            return
        whole = [b for b in bodies if b.Name in tops]
        if whole:
            return warn(f"Materials go on the faces (pieces) of {objects.display_name(whole[0])}: select faces first.")
        if gate(study, bodies):
            taskpanels.ask_assignment(study, bodies)


class AddExcitation(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("excitation"),
            "MenuText": "Excitation",
            "ToolTip": "Make the selected faces an excitation surface",
        }

    def IsActive(self):  # 2D Studies get field sources later
        study = active_study()
        return study is not None and study.Dimension == "3D" and not Gui.Control.activeDialog()

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        faces = taskpanels.selected_faces()
        if not faces:
            if any(taskpanels.is_air(b) for b, _ in taskpanels.selected_subs(("Face",))):
                return warn("An Air Region cannot be an Excitation: pick the faces of a body.")
            return warn("Select one or more faces first.")
        if not gate(study, [b for b, _ in faces]):
            return
        name = ask_text("Excitation", "Excitation name:", "Excitation")
        if name:
            _create(study, "Add Excitation", lambda: objects.make_excitation(study, name, faces))


class AddMeshSize(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("meshsize"),
            "MenuText": "Mesh Size",
            "ToolTip": "Set the mesh size of the selected bodies, faces, edges or vertices",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        refs = taskpanels.selected_mesh_refs()
        if gate(study, [b for b, _ in refs]):
            size = study.MeshSizesGroup.DefaultMeshSize.Value
            _create_and_edit(study, "Add Mesh Size", lambda: objects.make_mesh_size(study, size, refs))


class AddAirRegion(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("airregion"),
            "MenuText": "Air Region",
            "ToolTip": "Add the air around the model: a box that fits the bodies, a sector or a body of your own",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        if objects.air_regions(study):
            return warn("This Study already has an Air Region.")
        doc = study.Document
        try:
            bodies = objects.study_bodies(study)  # main and moving geometry
        except Exception as exc:  # a body not recomputed yet has no shape: start with the manual defaults
            App.Console.PrintWarning(f"EMSolution: the Air Region starts Manual, the bodies are not ready ({exc}).\n")
            bodies = []
        doc.openTransaction("Add Air Region")  # stays open until OK or Cancel
        lib = studymaterials.default_air_material(study)
        air = objects.make_air_region(study, "Box")
        if bodies:  # padding of 20 % on every side the shape offers, following the bodies
            airshapes.seed_padding(air, "Custom", "Box", airshapes.study_plane(study))
            air.SizeMode = "Padding"
        objects.assign(study, [air], lib, 0)  # Cancel undoes the material and this as well
        doc.recompute()
        Gui.Control.showDialog(taskpanels.AirRegionPanel(air, new=True))


class AddSlidingInterface(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("slidinginterface"),
            "MenuText": "Sliding Interface",
            "ToolTip": "Add the surface between the fixed and the moving air (Study with sliding motion)",
        }

    def IsActive(self):
        study = active_study()
        return study is not None and study.Movement == "Sliding motion" and not Gui.Control.activeDialog()

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        airs = objects.air_regions(study)
        if not airs:
            return warn("Add an Air Region first.")
        doc = study.Document
        doc.openTransaction("Add Sliding Interface")  # stays open until OK or Cancel
        iface = objects.make_sliding_interface(study)  # Linear in a Box Air Region, else Rotational
        doc.recompute()
        Gui.Control.showDialog(taskpanels.SlidingInterfacePanel(iface, new=True))


class AddTransfiniteBody(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("transfinitebody"),
            "MenuText": "Transfinite Body",
            "ToolTip": "Mesh the selected bodies as a structured grid; selected vertices become face corners",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        bodies = taskpanels.selected_bodies()
        if gate(study, bodies, objects.TransfiniteBody):
            corners = taskpanels.selected_subs(("Vertex",))
            _create_and_edit(
                study, "Add Transfinite Body", lambda: objects.make_transfinite_body(study, bodies, corners)
            )


class AddTransfiniteEdges(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("transfiniteedges"),
            "MenuText": "Transfinite Edges",
            "ToolTip": "Give the selected edges a fixed number of elements",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        edges = taskpanels.selected_subs(("Edge",))
        if gate(study, [b for b, _ in edges], objects.TransfiniteEdges):
            _create_and_edit(study, "Add Transfinite Edges", lambda: objects.make_transfinite_edges(study, 10, edges))


class AddRecombine(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("recombine"),
            "MenuText": "Recombine",
            "ToolTip": "Mesh the selected bodies with quads (2D) or quad faces and hexahedra (3D)",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        bodies = taskpanels.selected_bodies()
        if gate(study, bodies, objects.Recombine):
            _create_and_edit(study, "Add Recombine", lambda: objects.make_recombine(study, bodies))


class AddSymmetricMesh(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("symmetricmesh"),
            "MenuText": "Symmetric Mesh",
            "ToolTip": "Mesh one cell of a Mirror / Polar Array drawing and copy the mesh around",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        picked = Gui.Selection.getSelection()
        names = {b.Name for b in objects.study_bodies(study)}
        if len(picked) != 1 or picked[0].Name not in names:
            return warn("Select the object built from the cell (the Fragments or Array) first.")
        top = picked[0]
        _create(study, "Add Symmetric Mesh", lambda: objects.make_symmetric_mesh(study, top))


class ValidateStudy(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("validate"),
            "MenuText": "Validate Study",
            "ToolTip": "List every problem of the Study, then run the mesher's geometry checks without meshing",
        }

    def IsActive(self):
        return active_study() is not None and not runner.busy() and not Gui.Control.activeDialog()

    def Activated(self):
        study = active_study()
        if study is None:
            return warn("Select the Study you want to validate first.")
        Gui.Control.showDialog(taskpanels.ValidationPanel(study))


class RunMesh(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("runmesh"), "MenuText": "Run Mesh", "ToolTip": "Write the .msh file with Gmsh"}

    def IsActive(self):
        study = active_study()
        return (
            study is not None
            and not geometry.export_unavailable(study)
            and not runner.busy()
            and not Gui.Control.activeDialog()
        )

    def Activated(self):
        study = active_study()
        if study is None:
            return warn("Select the Study you want to mesh first.")
        runner.start(study)


COMMANDS = {
    "EMS_NewStudy": NewStudy(),
    "EMS_Material": AssignMaterial(),
    "EMS_Excitation": AddExcitation(),
    "EMS_MeshSize": AddMeshSize(),
    "EMS_AddAirRegion": AddAirRegion(),
    "EMS_AddSlidingInterface": AddSlidingInterface(),
    "EMS_TransfiniteBody": AddTransfiniteBody(),
    "EMS_TransfiniteEdges": AddTransfiniteEdges(),
    "EMS_Recombine": AddRecombine(),
    "EMS_SymmetricMesh": AddSymmetricMesh(),
    "EMS_Validate": ValidateStudy(),
    "EMS_RunMesh": RunMesh(),
}
for _name, _cmd in COMMANDS.items():
    Gui.addCommand(_name, _cmd)
NAMES = list(COMMANDS)
