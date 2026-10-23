"""Reading the copy transforms from the Mirror / Polar Array / Boolean Fragments chain of a symmetric drawing."""

import pytest

import FreeCAD as App
import Part

from emsolution import symmetry

from . import symcases


@pytest.fixture
def motor():
    doc = App.newDocument("SymTest")
    info = symcases.motor_doc(doc)
    info["doc"] = doc
    yield info
    App.closeDocument(doc.Name)


def inner_point(face):
    """A point inside face (the centre of mass of a concave face can lie outside it): a triangle's centroid."""
    points, triangles = face.tessellate(0.5)
    a, b, c = (points[i] for i in triangles[0])
    return (a + b + c) * (1 / 3)


def assert_lands(cells, transforms, top):
    """Every moved cell face sits on a face of top, and the cell areas on each face add up to the face area."""
    sums = {}
    for body in cells:
        for face in body.Shape.Faces:
            c = inner_point(face)
            for t in transforms:
                p = Part.Vertex(App.Vector(*symmetry.apply(t, (c.x, c.y, c.z))))
                hits = [i for i, f in enumerate(top.Shape.Faces) if p.distToShape(f)[0] < 1e-6]
                assert len(hits) == 1
                sums[hits[0]] = sums.get(hits[0], 0.0) + face.Area
    for i, f in enumerate(top.Shape.Faces):
        assert sums[i] == pytest.approx(f.Area, rel=1e-6)


def test_stator_chain_gives_24_copies_of_3_cells(motor):
    cells, transforms = symmetry.read_chain(motor["stator_top"])
    assert cells == motor["stator_cells"]
    assert len(transforms) == 24
    assert symmetry.apply(transforms[0], (1, 2, 3)) == pytest.approx([1, 2, 3])
    assert sum(symmetry.det(t) < 0 for t in transforms) == 12


def test_rotor_chain_gives_16_copies(motor):
    cells, transforms = symmetry.read_chain(motor["rotor_top"])
    assert cells == motor["rotor_cells"]
    assert len(transforms) == 16
    assert sum(symmetry.det(t) < 0 for t in transforms) == 8


def test_copies_land_on_the_fragments(motor):
    for part in ("stator", "rotor"):
        cells, transforms = symmetry.read_chain(motor[f"{part}_top"])
        assert_lands(cells, transforms, motor[f"{part}_top"])


def test_moved_drawing_still_lands(motor):
    array = motor["doc"].getObjectsByLabel("StatorArray")[0]
    array.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 0, 1), 10))
    motor["doc"].recompute()
    cells, transforms = symmetry.read_chain(motor["stator_top"])
    assert_lands(cells, transforms, motor["stator_top"])


def test_unknown_object_in_chain_is_refused(motor):
    doc = motor["doc"]
    cut = doc.addObject("Part::Cut", "TheCut")
    cut.Base = doc.getObject("StatorPitch")
    cut.Tool = doc.getObject("CoilCell")
    array = doc.getObjectsByLabel("StatorArray")[0]
    array.Base = cut
    doc.recompute()
    with pytest.raises(symmetry.SymmetryError, match=r"TheCut.*Part::Cut"):
        symmetry.read_chain(motor["stator_top"])


def test_leaves_with_different_copies_are_refused(motor):
    doc = motor["doc"]
    stray = symcases.feature(doc, "StrayBody", symcases.sector(60, 62, 0, 15))
    pitch = doc.getObject("StatorPitch")
    pitch.Links = list(pitch.Links) + [stray]
    doc.recompute()
    with pytest.raises(symmetry.SymmetryError, match="StrayBody"):
        symmetry.read_chain(motor["stator_top"])


def test_mirror_out_of_plane_is_refused(motor):
    mirror = motor["doc"].getObject("StatorMirror")
    mirror.Normal = App.Vector(0, 0, 1)
    with pytest.raises(symmetry.SymmetryError, match="StatorMirror"):
        symmetry.read_chain(motor["stator_top"])


def test_array_axis_other_than_z_is_refused(motor):
    array = motor["doc"].getObjectsByLabel("StatorArray")[0]
    array.Axis = App.Vector(1, 0, 0)
    with pytest.raises(symmetry.SymmetryError, match="StatorArray"):
        symmetry.read_chain(motor["stator_top"])
