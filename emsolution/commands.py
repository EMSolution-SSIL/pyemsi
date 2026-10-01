"""Toolbar and menu commands."""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from . import icon, objects, runner, taskpanels


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
    return objects.find_study(App.ActiveDocument) if App.ActiveDocument else None


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
        return active_study() is not None


class NewStudy:
    def GetResources(self):
        return {"Pixmap": icon("study"), "MenuText": "New Study",
                "ToolTip": "Create an EMSolution study in this document"}

    def IsActive(self):
        return App.ActiveDocument is not None and active_study() is None

    def Activated(self):
        doc = App.ActiveDocument
        doc.openTransaction("New Study")
        study = objects.make_study(doc)
        taskpanels.ViewProviderStudy(study.ViewObject)
        doc.commitTransaction()
        doc.recompute()


class AddMaterial(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("material"), "MenuText": "Material",
                "ToolTip": "Give the selected bodies a material"}

    def Activated(self):
        bodies = taskpanels.selected_bodies()
        if not bodies:
            return warn("Select one or more bodies first.")
        name = ask_text("Material", "Material name:", "Material")
        if name:
            _create(active_study(), "Add Material",
                    lambda: objects.make_material(active_study(), name, bodies))


class AddExcitation(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("excitation"), "MenuText": "Excitation",
                "ToolTip": "Make the selected faces an excitation surface"}

    def Activated(self):
        faces = taskpanels.selected_faces()
        if not faces:
            return warn("Select one or more faces first.")
        name = ask_text("Excitation", "Excitation name:", "Excitation")
        if name:
            _create(active_study(), "Add Excitation",
                    lambda: objects.make_excitation(active_study(), name, faces))


class AddMeshSize(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("meshsize"), "MenuText": "Mesh Size",
                "ToolTip": "Set the mesh size of the selected bodies, faces, edges or vertices"}

    def Activated(self):
        refs = taskpanels.selected_mesh_refs()
        if not refs:
            return warn("Select one or more bodies, faces, edges or vertices first.")
        size = ask_size(active_study().DefaultMeshSize.Value)
        if size:
            _create(active_study(), "Add Mesh Size",
                    lambda: objects.make_mesh_size(active_study(), size, refs))


class RunMesh(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("runmesh"), "MenuText": "Run Mesh",
                "ToolTip": "Write the .msh file with Gmsh"}

    def IsActive(self):
        return super().IsActive() and not runner.busy()

    def Activated(self):
        runner.start(active_study())


COMMANDS = {"EMS_NewStudy": NewStudy(), "EMS_Material": AddMaterial(),
            "EMS_Excitation": AddExcitation(), "EMS_MeshSize": AddMeshSize(),
            "EMS_RunMesh": RunMesh()}
for _name, _cmd in COMMANDS.items():
    Gui.addCommand(_name, _cmd)
NAMES = list(COMMANDS)
