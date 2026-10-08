"""Toolbar and menu commands."""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from . import geometry, icon, objects, runner, taskpanels


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


def ask_size(default):
    value, ok = QtWidgets.QInputDialog.getDouble(
        Gui.getMainWindow(), "Mesh Size", "Element size (mm):", default, 0.001, 1e6, 3)
    return value if ok else None


def warn(text):
    QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "EMSolution", text)


def active_study():
    return taskpanels.active_study()


def assignment_study():
    study = active_study()
    if study is None:
        warn("Select the Study you want to edit first.")
    elif study.Dimension != "3D":
        warn("2D assignments will be added with 2D mesh generation.")
        study = None
    return study


def _create(study, title, make):
    doc = study.Document
    doc.openTransaction(title)
    obj = make()
    taskpanels.ViewProviderItem(obj.ViewObject)
    doc.commitTransaction()
    doc.recompute()
    return obj


class _StudyCommand:
    def IsActive(self):
        study = active_study()
        return study is not None and study.Dimension == "3D" and not Gui.Control.activeDialog()


class NewStudy:
    def GetResources(self):
        return {"Pixmap": icon("study"), "MenuText": "New Study",
                "ToolTip": "Create an EMSolution study in this document"}

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
        taskpanels.ViewProviderStudy(study.ViewObject)
        doc.commitTransaction()
        doc.recompute()
        taskpanels.set_active_study(study)
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(study)


class AddMaterial(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("material"), "MenuText": "Material",
                "ToolTip": "Give the selected bodies a material"}

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        bodies = taskpanels.selected_bodies()
        if not bodies:
            return warn("Select one or more bodies first.")
        name = ask_text("Material", "Material name:", "Material")
        if name:
            _create(study, "Add Material", lambda: objects.make_material(study, name, bodies))


class AddExcitation(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("excitation"), "MenuText": "Excitation",
                "ToolTip": "Make the selected faces an excitation surface"}

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        faces = taskpanels.selected_faces()
        if not faces:
            return warn("Select one or more faces first.")
        name = ask_text("Excitation", "Excitation name:", "Excitation")
        if name:
            _create(study, "Add Excitation", lambda: objects.make_excitation(study, name, faces))


class AddMeshSize(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("meshsize"), "MenuText": "Mesh Size",
                "ToolTip": "Set the mesh size of the selected bodies, faces, edges or vertices"}

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        refs = taskpanels.selected_mesh_refs()
        if not refs:
            return warn("Select one or more bodies, faces, edges or vertices first.")
        size = ask_size(study.MeshSizesGroup.DefaultMeshSize.Value)
        if size:
            _create(study, "Add Mesh Size", lambda: objects.make_mesh_size(study, size, refs))


class RunMesh(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("runmesh"), "MenuText": "Run Mesh",
                "ToolTip": "Write the .msh file with Gmsh"}

    def IsActive(self):
        study = active_study()
        return (study is not None and not geometry.export_unavailable(study)
                and not runner.busy() and not Gui.Control.activeDialog())

    def Activated(self):
        study = active_study()
        if study is None:
            return warn("Select the Study you want to mesh first.")
        runner.start(study)


COMMANDS = {"EMS_NewStudy": NewStudy(), "EMS_Material": AddMaterial(),
            "EMS_Excitation": AddExcitation(), "EMS_MeshSize": AddMeshSize(),
            "EMS_RunMesh": RunMesh()}
for _name, _cmd in COMMANDS.items():
    Gui.addCommand(_name, _cmd)
NAMES = list(COMMANDS)
