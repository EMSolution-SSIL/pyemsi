"""Which side of a Sliding Interface a shape is on. Run from the repo root:
pixi run -e addon pytest tests/freecad_addon/test_sides.py"""

import FreeCAD as App
import Part
import pytest

from emsolution import airshapes, objects, sides

V = App.Vector


@pytest.fixture
def doc():
    doc = App.newDocument("Sides")
    yield doc
    App.closeDocument(doc.Name)


@pytest.fixture
def study2d(doc):
    return objects.make_study(doc, "2D")


@pytest.fixture
def study3d(doc):
    return objects.make_study(doc, "3D")


def disc(r0, r1):
    return Part.Face(Part.Wire(Part.makeCircle(r1)))


def ring(r0, r1):
    return Part.Face(Part.Wire(Part.makeCircle(r1))).cut(Part.Face(Part.Wire(Part.makeCircle(r0))))


def square(x, y, size):
    return Part.makePlane(size, size, V(x, y, 0))


def cut_disc(radius, radii):
    """The air disc cut by circles at radii (inner first) and the circles."""
    surfaces = [Part.makeCompound([Part.makeCircle(r)]) for r in radii]
    pieces = airshapes.cells(Part.Face(Part.Wire(Part.makeCircle(radius))), surfaces)
    return sorted(pieces, key=lambda p: p.BoundBox.XMax), surfaces


def test_rotational_inside_moves(study2d):
    i = objects.make_sliding_interface(study2d, "Rotational", Radius=50)
    assert sides.side_of(disc(0, 40), i, "XY") == "moving"
    assert sides.side_of(ring(60, 70), i, "XY") == "fixed"
    assert sides.side_of(ring(40, 60), i, "XY") is None
    i.MovingSide = "Outside"
    assert sides.side_of(ring(60, 70), i, "XY") == "moving"


def test_choices_follow_the_kind(study2d):
    i = objects.make_sliding_interface(study2d, "Rotational", Radius=50)
    assert i.getEnumerationsOfProperty("MovingSide") == ["Inside", "Outside"]
    i.MovingSide = "Outside"
    i.Kind = "Linear"
    assert i.getEnumerationsOfProperty("MovingSide") == ["Positive", "Negative"]
    assert i.MovingSide == "Negative"  # the index is kept


def test_axial_gap_above_moves(study3d):
    i = objects.make_sliding_interface(study3d, "Axial gap", Position=5)
    assert sides.side_of(Part.makeBox(10, 10, 10, V(0, 0, 10)), i, "3D") == "moving"
    assert sides.side_of(Part.makeBox(10, 10, 4, V(0, 0, 0)), i, "3D") == "fixed"


def test_linear_negative_moves(study2d):
    i = objects.make_sliding_interface(study2d, "Linear", Position=0, NormalAxis="Y", MovingSide="Negative")
    assert sides.side_of(square(0, -5, 4), i, "XY") == "moving"
    assert sides.side_of(square(0, 1, 4), i, "XY") == "fixed"


def test_rotational_in_3d(study3d):
    i = objects.make_sliding_interface(study3d, "Rotational", Radius=50)
    assert sides.side_of(Part.makeCylinder(40, 10), i, "3D") == "moving"
    assert sides.side_of(Part.makeCylinder(70, 10).cut(Part.makeCylinder(60, 10)), i, "3D") == "fixed"


def test_double_air_gap(study2d):
    a = objects.make_sliding_interface(study2d, "Rotational", Radius=30, MovingSide="Outside")
    b = objects.make_sliding_interface(study2d, "Rotational", Radius=50, MovingSide="Inside")
    pieces, surfaces = cut_disc(100, [30, 50])
    assert sides.piece_sides(pieces, [a, b], surfaces, "XY") == (["fixed", "moving", "fixed"], [])
    b.MovingSide = "Outside"
    found, errors = sides.piece_sides(pieces, [a, b], surfaces, "XY")
    assert found[1] is None and len(errors) == 1 and "disagree" in errors[0][0]


def test_axial_gap_far_from_the_shape(study3d):
    i = objects.make_sliding_interface(study3d, "Axial gap", Position=-5000)
    assert sides.side_of(Part.makeBox(10, 10, 10), i, "3D") == "moving"


def test_rotational_far_along_z(study3d):
    i = objects.make_sliding_interface(study3d, "Rotational", Radius=50)
    assert sides.side_of(Part.makeCylinder(40, 10, V(0, 0, 5000)), i, "3D") == "moving"
