"""Run inside an isolated FreeCAD process; write JSON results and an FCStd file.

Set FREECAD_SKILL_RUNTIME_OUTPUT to a disposable writable directory. Execute this
file with FreeCADCmd -P <this directory>, or import run() from a GUI macro. Set
FREECAD_SKILL_RUNTIME_RESTORE=1 for a separate-process reopening check.
"""

import importlib
import json
import math
import os
from pathlib import Path
import sys
import traceback
import uuid

import FreeCAD as App
import Part


class SmokeProxy:
    """Stable importable class; constructor deliberately leaves unsaved state."""

    def __init__(self, obj):
        self.constructor_only = True
        self.tag = "freecad-addon-api-smoke"
        obj.addProperty("App::PropertyLength", "Size", "Smoke")
        obj.Size = "3 mm"
        obj.Proxy = self

    def execute(self, obj):
        size = obj.Size.Value
        obj.Shape = Part.makeBox(size, size, size)

    def dumps(self):
        return {"tag": self.tag}

    def loads(self, state):
        self.tag = state["tag"]
        self.loaded = True

    def onDocumentRestored(self, obj):
        self.document_restored = True


class SmokeViewProxy:
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.object_name = vobj.Object.Name

    def dumps(self):
        return None

    def loads(self, state):
        self.loaded = True

    def finishRestoring(self):
        self.finished = True


def run(output_directory=None, restore_only=False):
    """Run smoke checks against owned documents only; no existing docs permitted."""
    output = Path(output_directory or os.environ["FREECAD_SKILL_RUNTIME_OUTPUT"])
    output.mkdir(parents=True, exist_ok=True)
    report = {"version": list(App.Version()), "gui": bool(App.GuiUp), "checks": []}
    owned_documents = set()
    document_path = output / "smoke.FCStd"

    def check(name, operation):
        try:
            operation()
        except Exception:
            report["checks"].append({"name": name, "status": "failed", "error": traceback.format_exc()})
            return False
        report["checks"].append({"name": name, "status": "passed"})
        return True

    def reopen():
        restored = App.openDocument(str(document_path))
        owned_documents.add(restored.Name)
        obj = restored.getObject("ProxyBox")
        assert obj is not None and obj.Proxy is not None
        assert obj.Proxy.tag == "freecad-addon-api-smoke"
        assert obj.Proxy.loaded and obj.Proxy.document_restored
        assert not hasattr(obj.Proxy, "constructor_only"), "Restore called constructor or saved excluded state"
        restored.recompute()
        assert obj.isValid() and obj.Shape.isValid()
        assert math.isclose(obj.Shape.Volume, 27.0, rel_tol=1e-9)

    try:
        if App.listDocuments():
            raise RuntimeError("Use a separate empty FreeCAD process; existing documents are present")
        if restore_only:
            check("fresh_process_proxy_restore", reopen)
        else:
            doc = App.newDocument("SkillSmoke" + uuid.uuid4().hex[:8])
            owned_documents.add(doc.Name)
            # Older installed releases require this; the source snapshot's setter
            # is a no-op. This is an owned disposable document, not user state.
            report["undo_mode_before"] = doc.UndoMode
            doc.UndoMode = 1
            report["undo_mode_for_test"] = doc.UndoMode

            def native_box():
                doc.openTransaction("Skill native box")
                try:
                    box = doc.addObject("Part::Box", "NativeBox")
                    box.Length, box.Width, box.Height = "2 cm", "10 mm", "5 mm"
                    box.Placement = App.Placement(App.Vector(20, 5, 0), App.Rotation(App.Vector(0, 0, 1), 90))
                    doc.recompute()
                    assert box.isValid(), box.getStatusString()
                    assert not box.Shape.isNull() and box.Shape.isValid()
                    assert math.isclose(box.Shape.Volume, 1000.0, rel_tol=1e-9)
                    assert math.isclose(box.Length.Value, 20.0)
                    assert math.isclose(box.Placement.Base.x, 20.0)
                    assert math.isclose(box.Placement.Rotation.multVec(App.Vector(1, 0, 0)).y, 1.0)
                except Exception:
                    doc.abortTransaction()
                    raise
                doc.commitTransaction()

            if check("native_box_units_placement_recompute", native_box):
                def undo_redo():
                    doc.undo()
                    assert doc.getObject("NativeBox") is None
                    doc.redo()
                    doc.recompute()
                    assert doc.getObject("NativeBox").Shape.isValid()
                check("native_box_undo_redo", undo_redo)

            def document_observer():
                class Observer:
                    count = 0
                    def slotCreatedObject(self, obj):
                        if obj.Document.Name == doc.Name:
                            self.count += 1
                observer = Observer()
                App.addDocumentObserver(observer)
                try:
                    doc.addObject("App::FeaturePython", "Observed")
                    assert observer.count == 1
                finally:
                    App.removeDocumentObserver(observer)
                doc.addObject("App::FeaturePython", "Unobserved")
                assert observer.count == 1
            check("document_observer_cleanup", document_observer)

            def persistence():
                stable = importlib.import_module("check_runtime")
                obj = doc.addObject("Part::FeaturePython", "ProxyBox")
                stable.SmokeProxy(obj)
                if App.GuiUp:
                    stable.SmokeViewProxy(obj.ViewObject)
                doc.recompute()
                assert obj.Shape.isValid()
                doc.saveAs(str(document_path))
                name = doc.Name
                App.closeDocument(name)
                owned_documents.discard(name)
                reopen()
            check("proxy_save_reopen", persistence)

            if App.GuiUp:
                import FreeCADGui as Gui

                def view_proxy_restore():
                    obj = App.activeDocument().getObject("ProxyBox")
                    assert obj is not None and obj.ViewObject is not None
                    assert obj.ViewObject.Proxy.loaded and obj.ViewObject.Proxy.finished
                check("view_proxy_restore", view_proxy_restore)

                def command_bool():
                    class Command:
                        def __init__(self, active):
                            self.active = active
                            self.called = False
                        def GetResources(self):
                            return {"MenuText": "Skill smoke", "CmdType": "NoTransaction"}
                        def IsActive(self):
                            return self.active
                        def Activated(self):
                            self.called = True
                    prefix = "SkillSmoke_" + uuid.uuid4().hex
                    yes, integer = Command(True), Command(1)
                    Gui.addCommand(prefix + "_yes", yes)
                    Gui.addCommand(prefix + "_integer", integer)
                    assert Gui.Command.get(prefix + "_yes").isActive() is True
                    assert Gui.Command.get(prefix + "_integer").isActive() is False
                    Gui.runCommand(prefix + "_yes")
                    assert yes.called
                check("gui_command_boolean_and_activation", command_bool)

                def selection_observer():
                    class Observer:
                        count = 0
                        def addSelection(self, doc_name, obj_name, sub_name, point):
                            self.count += 1
                    current = App.activeDocument()
                    obj = current.getObject("ProxyBox")
                    assert obj is not None
                    observer = Observer()
                    Gui.Selection.clearSelection(current.Name)
                    Gui.Selection.addObserver(observer)
                    try:
                        Gui.Selection.addSelection(obj)
                        assert observer.count == 1
                    finally:
                        Gui.Selection.removeObserver(observer)
                    Gui.Selection.clearSelection(current.Name)
                    Gui.Selection.addSelection(obj)
                    assert observer.count == 1
                    Gui.Selection.clearSelection(current.Name)
                check("gui_selection_observer_cleanup", selection_observer)
            else:
                for name in ("gui_command_boolean_and_activation", "gui_selection_observer_cleanup", "view_proxy_restore"):
                    report["checks"].append({"name": name, "status": "skipped", "reason": "App.GuiUp is false"})
    except Exception:
        report["checks"].append({"name": "setup", "status": "failed", "error": traceback.format_exc()})
    finally:
        for name in owned_documents:
            App.closeDocument(name)
        report["success"] = all(item["status"] != "failed" for item in report["checks"])
        report_path = output / ("restore-result.json" if restore_only else "result.json")
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
    return report


# FreeCADCmd imports positional .py files as modules instead of setting __main__.
if __name__ == "__main__" or any(Path(arg).resolve() == Path(__file__).resolve() for arg in sys.argv[1:]):
    run(restore_only=os.environ.get("FREECAD_SKILL_RUNTIME_RESTORE") == "1")
