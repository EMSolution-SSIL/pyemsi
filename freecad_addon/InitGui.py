import FreeCADGui as Gui

import emsolution  # the Mod folder is on sys.path
from emsolution import taskpanels


class EMSolutionWorkbench(Gui.Workbench):
    # FreeCAD exec()s this file inside a function, so the class body and methods
    # cannot see names imported above. Import inside methods; set Icon below.
    MenuText = "EMSolution"
    ToolTip = "Configure EMSolution studies and prepare meshes"

    def Initialize(self):
        from emsolution import commands

        for title, names in commands.TOOLBARS:
            self.appendToolbar(title, names)
        self.appendMenu("EMSolution", commands.MENU)

    def ContextMenu(self, recipient):
        from emsolution import commands

        names = commands.context_menu()
        if names:
            self.appendContextMenu("", "Separator")
            self.appendContextMenu("EMSolution", names)

    def Activated(self):
        import FreeCADGui
        from emsolution import taskpanels

        FreeCADGui.Control.addTaskWatcher(taskpanels.folder_watchers())

    def Deactivated(self):
        import FreeCADGui

        FreeCADGui.Control.clearTaskWatcher()

    def GetClassName(self):
        return "Gui::PythonWorkbench"


EMSolutionWorkbench.Icon = emsolution.icon("emsolution")
Gui.addWorkbench(EMSolutionWorkbench())
taskpanels.install_selection_observer()  # highlight and workbench switch, in any workbench
taskpanels.install_open_observer()  # view providers for documents built without the GUI
