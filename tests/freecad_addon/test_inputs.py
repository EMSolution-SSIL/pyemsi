"""Which bodies another body is made from (geometry.inputs), so the Study geometry tree hides them.
The examples in experiments/hidden_inputs_examples show these cases in FreeCAD."""

import pytest

import FreeCAD as App
import Draft  # after FreeCAD, which puts its modules on the path
from BOPTools import JoinFeatures

from emsolution import geometry


@pytest.fixture
def doc():
    doc = App.newDocument("Inputs")
    yield doc
    App.closeDocument(doc.Name)


def box(doc, name, x=0.0, size=10.0):
    b = doc.addObject("Part::Box", name)
    b.Length = b.Width = b.Height = size
    b.Placement.Base = App.Vector(x, 0, 0)
    return b


def shown(doc):
    """Labels of the bodies the 3D geometry tree offers, containers flattened."""

    def flat(nodes):
        return [label for obj, ch in nodes for label in (flat(ch) if ch else [obj.Label])]

    doc.recompute()
    return flat(geometry.tree(doc, "3D"))


def test_a_link_with_a_subname_is_the_object_it_names(doc):
    stator = doc.addObject("App::Part", "Stator")
    air_box, magnet = box(doc, "AirBox", 0, 30), box(doc, "Magnet", 40)
    stator.addObject(air_box)
    stator.addObject(magnet)  # in the same Part, but not linked: stays a body
    coil = box(doc, "Coil", 10)
    link = doc.addObject("App::Link", "AirBoxLink")
    link.setLink(stator, "AirBox.")
    air = doc.addObject("Part::Cut", "Air")
    air.Base, air.Tool = link, coil
    assert shown(doc) == ["Magnet", "Coil", "Air"]


def test_a_link_to_an_edge_is_a_reference(doc):
    coil = box(doc, "Coil", 10)
    ruled = doc.addObject("Part::RuledSurface", "Ruled")
    ruled.Curve1, ruled.Curve2 = (coil, ["Edge1"]), (coil, ["Edge3"])
    doc.recompute()
    assert coil.Name not in geometry.inputs(ruled)


def test_a_moved_draft_clone_leaves_its_original_a_body(doc):
    rod = doc.addObject("Part::Cylinder", "Rod")
    doc.recompute()
    clone = Draft.make_clone(rod)
    clone.Label = "RodClone"
    clone.Placement.Base = App.Vector(30, 0, 0)
    assert shown(doc) == ["Rod", "RodClone"]


def test_a_draft_array_holds_its_base(doc):
    rod = doc.addObject("Part::Cylinder", "Rod")
    doc.recompute()
    array = Draft.make_ortho_array(rod, App.Vector(10, 0, 0), App.Vector(0, 10, 0), App.Vector(0, 0, 10), 3, 1, 1)
    array.Label = "Rods"
    assert shown(doc) == ["Rods"]


def test_the_tool_of_a_join_cutout_stays_a_body(doc):
    air_box, coil = box(doc, "AirBox", 0, 30), box(doc, "Coil", 10)
    cut = JoinFeatures.makeCutout(name="AirCut")
    cut.Base, cut.Tool = air_box, coil
    assert shown(doc) == ["Coil", "AirCut"]


def test_the_tool_of_a_join_embed_is_inside_it(doc):
    air_box, coil = box(doc, "AirBox", 0, 30), box(doc, "Coil", 10)
    embed = JoinFeatures.makeEmbed(name="Embedded")
    embed.Base, embed.Tool = air_box, coil
    assert shown(doc) == ["Embedded"]
