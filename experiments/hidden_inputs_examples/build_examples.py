"""Build the hidden-inputs example files, one folder each, and print what the Study geometry tree and Validate show.
Run from the repo root: pixi run -e addon python experiments/hidden_inputs_examples/build_examples.py"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "freecad_addon"))

import FreeCAD as App  # noqa: E402 - after the add-on path
import Draft  # noqa: E402
from BOPTools import JoinFeatures  # noqa: E402

from emsolution import geometry, objects, validation  # noqa: E402

V = App.Vector


def box(doc, name, x=0.0, size=10.0):
    b = doc.addObject("Part::Box", name)
    b.Length = b.Width = b.Height = size
    b.Placement.Base = V(x, 0, 0)
    return b


def new_doc(name):
    doc = App.newDocument(name)
    study = objects.make_study(doc, "3D", "Study")
    study.MainMode = "Manual"
    return doc, study


def labels(nodes):
    out = []
    for obj, children in nodes:
        out += labels(children) if children else [obj.Label]
    return out


def bodies(nodes):
    out = []
    for obj, children in nodes:
        out += bodies(children) if children else [obj]
    return out


def finish(doc, study, name):
    """Tick every body the geometry tree offers, as a user would, then save and report."""
    doc.recompute()
    tree = geometry.tree(doc, "3D")
    study.MainObjects = bodies(tree)
    doc.recompute()
    folder = os.path.join(HERE, name)
    os.makedirs(folder, exist_ok=True)
    doc.saveAs(os.path.join(folder, name + ".FCStd"))
    print(f"{name}\n  tree: {labels(tree)}")
    for p in validation.validate(study):
        if "No material" not in p.text:
            print(f"  {p.severity}: {p.text}")
    App.closeDocument(doc.Name)


def link_with_subname():
    """Air = AirBox (inside the Part Stator, reached by a Link with a subname) minus Coil."""
    doc, study = new_doc("1_link_with_subname")
    stator = doc.addObject("App::Part", "Stator")
    air_box = box(doc, "AirBox", 0, 30)
    stator.addObject(air_box)
    coil = box(doc, "Coil", 10)
    link = doc.addObject("App::Link", "AirBoxLink")
    link.setLink(stator, "AirBox.")
    air = doc.addObject("Part::Cut", "Air")
    air.Base, air.Tool = link, coil
    for o in (air_box, coil, link):
        o.Visibility = False
    coil.Visibility = True
    finish(doc, study, "1_link_with_subname")


def thickness():
    """Part Thickness of two 20 mm cubes, open at the top: ShellOut grows 2 mm outward and wraps SolidOut (they
    only touch), ShellIn grows 2 mm inward and lies inside SolidIn (they overlap)."""
    doc, study = new_doc("2_thickness")
    for side, x, value in (("Out", 0, 2), ("In", 50, -2)):
        solid = box(doc, "Solid" + side, x, 20)
        shell = doc.addObject("Part::Thickness", "Shell" + side)
        shell.Faces = (solid, ["Face6"])
        shell.Value = value
    finish(doc, study, "2_thickness")


def draft_clone():
    """Rod and a Draft Clone of it moved 30 mm along x: two separate rods."""
    doc, study = new_doc("3_draft_clone")
    rod = doc.addObject("Part::Cylinder", "Rod")
    rod.Radius, rod.Height = 3, 20
    doc.recompute()
    clone = Draft.make_clone(rod)
    clone.Label = "RodClone"
    clone.Placement.Base = V(30, 0, 0)
    finish(doc, study, "3_draft_clone")


def join_cutout():
    """AirCut = Part Join Cutout of AirBox with Coil: the air with the coil's room taken out."""
    doc, study = new_doc("4_join_cutout")
    air_box, coil = box(doc, "AirBox", 0, 30), box(doc, "Coil", 10)
    cut = JoinFeatures.makeCutout(name="AirCut")
    cut.Base, cut.Tool = air_box, coil
    air_box.Visibility = False
    finish(doc, study, "4_join_cutout")


if __name__ == "__main__":
    link_with_subname()
    thickness()
    draft_clone()
    join_cutout()
