import FreeCADGui as Gui

import emsolution  # the Mod folder is on sys.path


class EMSolutionWorkbench(Gui.Workbench):
    # FreeCAD exec()s this file inside a function, so the class body and methods
    # cannot see names imported above. Import inside methods; set Icon below.
    MenuText = "EMSolution"
    ToolTip = "Prepare 3D meshes for EMSolution"

    def Initialize(self):
        from emsolution import commands

        self.appendToolbar("EMSolution", commands.NAMES)
        self.appendMenu("EMSolution", commands.NAMES)

    def GetClassName(self):
        return "Gui::PythonWorkbench"


EMSolutionWorkbench.Icon = emsolution.icon("emsolution")
Gui.addWorkbench(EMSolutionWorkbench())
