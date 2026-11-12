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
    assert shown(doc) == ["Magnet", "Air"]  # Coil is a cut tool


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


def test_the_tool_of_a_join_cutout_is_not_meshed(doc):
    air_box, coil = box(doc, "AirBox", 0, 30), box(doc, "Coil", 10)
    cut = JoinFeatures.makeCutout(name="AirCut")
    cut.Base, cut.Tool = air_box, coil
    assert shown(doc) == ["AirCut"]
    assert geometry.cut_tools(doc) == {"Coil": cut}


def test_a_link_to_a_cut_tool_is_a_body(doc):
    air_box, coil = box(doc, "AirBox", 0, 30), box(doc, "Coil", 10)
    cut = doc.addObject("Part::Cut", "Air")
    cut.Base, cut.Tool = air_box, coil
    link = doc.addObject("App::Link", "CoilLink")
    link.LinkedObject = coil
    doc.recompute()
    assert shown(doc) == ["Air", "CoilLink"]
    assert geometry.link_target(link) is coil


def test_a_link_body_does_not_consume_its_target(doc):
    coil = box(doc, "Coil", 10)
    link = doc.addObject("App::Link", "CoilCopy")
    link.LinkedObject = coil
    link.LinkPlacement.Base = App.Vector(50, 0, 0)
    doc.recompute()
    assert shown(doc) == ["Coil", "CoilCopy"]
    assert abs(geometry.global_shape(link).BoundBox.XMin - 50) < 1e-6  # the link's placement replaces Coil's
    link.LinkTransform = True
    doc.recompute()
    assert abs(geometry.global_shape(link).BoundBox.XMin - 60) < 1e-6  # Coil starts at x = 10: they compose


def test_a_link_in_a_moved_part_is_where_it_is_seen(doc):
    coil = box(doc, "Coil", 10)
    part = doc.addObject("App::Part", "Holder")
    part.Placement.Base = App.Vector(0, 100, 0)
    link = doc.addObject("App::Link", "CoilLink")
    link.LinkedObject = coil
    part.addObject(link)
    doc.recompute()
    assert abs(geometry.global_shape(link).BoundBox.YMin - 100) < 1e-6


def test_a_link_array_and_a_link_to_a_part_are_not_bodies(doc):
    coil = box(doc, "Coil", 10)
    arr = doc.addObject("App::Link", "Arr")
    arr.LinkedObject, arr.ElementCount = coil, 3
    part = doc.addObject("App::Part", "P")
    to_part = doc.addObject("App::Link", "ToPart")
    to_part.LinkedObject = part
    doc.recompute()
    assert geometry.link_target(arr) is None and geometry.link_target(to_part) is None
    assert "Arr" not in shown(doc) and "ToPart" not in shown(doc)


def test_a_part_used_as_a_tool_makes_its_bodies_cut_tools(doc):
    air_box = box(doc, "AirBox", 0, 30)
    holder = doc.addObject("App::Part", "Coils")
    a, b = box(doc, "CoilA", 5, 3), box(doc, "CoilB", 15, 3)
    holder.addObject(a)
    holder.addObject(b)
    cut = doc.addObject("Part::Cut", "Air")
    cut.Base, cut.Tool = air_box, holder
    doc.recompute()
    assert set(geometry.cut_tools(doc)) == {"CoilA", "CoilB"}


def test_the_tool_of_a_join_embed_is_inside_it(doc):
    air_box, coil = box(doc, "AirBox", 0, 30), box(doc, "Coil", 10)
    embed = JoinFeatures.makeEmbed(name="Embedded")
    embed.Base, embed.Tool = air_box, coil
    assert shown(doc) == ["Embedded"]


def test_what_a_cut_tool_is_made_of_is_not_meshed(doc):
    air_box, a, b = box(doc, "AirBox", 0, 30), box(doc, "A", 5, 3), box(doc, "B", 15, 3)
    tool = doc.addObject("Part::Fuse", "Tool")
    tool.Base, tool.Tool = a, b
    cut = doc.addObject("Part::Cut", "Air")
    cut.Base, cut.Tool = air_box, tool
    assert shown(doc) == ["Air"]
    assert geometry.collect([air_box, a, b, tool, cut], "3D") == ([cut], [])


def test_a_top_level_link_with_a_subname_names_that_body(doc):
    stator = doc.addObject("App::Part", "Stator")
    magnet = box(doc, "Magnet", 40)
    stator.addObject(magnet)
    link = doc.addObject("App::Link", "MagnetLink")
    link.setLink(stator, "Magnet.")
    edge = doc.addObject("App::Link", "MagnetEdge")
    edge.setLink(stator, "Magnet.Edge3")
    whole = doc.addObject("App::Link", "StatorLink")
    whole.setLink(stator)
    doc.recompute()
    assert geometry.link_target(link) is magnet
    assert geometry.link_target(edge) is None and geometry.link_target(whole) is None
    assert shown(doc) == ["Magnet", "MagnetLink"]  # not MagnetEdge (an element) or StatorLink (a Part)
    assert abs(geometry.global_shape(link).BoundBox.XMin - 40) < 1e-6


def test_a_link_used_as_a_cut_tool_is_left_out(doc):
    air_box, coil = box(doc, "AirBox", 0, 30), box(doc, "Coil", 10)
    link = doc.addObject("App::Link", "CoilLink")
    link.LinkedObject = coil
    cut = doc.addObject("Part::Cut", "Air")
    cut.Base, cut.Tool = air_box, link
    doc.recompute()
    assert shown(doc) == ["Coil", "Air"]
    assert [o.Name for o in geometry.collect([air_box, coil, link, cut], "3D")[0]] == ["Coil", "Air"]
