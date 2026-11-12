"""Symmetric Groups end to end on an arrangement from no catalogue: oblique rules, several groups and a free object,
built, validated, meshed and read back. And the core code knows no device.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_rules_end_to_end.py"""

import itertools
import math
import os
import re

import gmsh
import pytest

import FreeCAD as App
import Part

from emsolution import jobwriter, objects, symmetry, validation

from . import meshreport, symcases

V = App.Vector
MIRROR = {"kind": "mirror", "point": [1, 2, 3], "normal": [1, 1, 2]}
ROTATE = {"kind": "rotate", "point": [0, 3, 0], "axis": [1, 2, 2], "step": 72, "count": 5}
TRANSLATE = {"kind": "translate", "vector": [40, 7, 9], "count": 3}


def _unit(v):
    return v.multiply(1 / v.Length)


def arrangement(doc):
    """The cells of the two groups and the free box: (box, wedge, sphere, free box shape).

    The box (4 x 3 x 2) and the wedge on its top face (y 3..5, narrowing to 2 x 1) are turned 37° about (2, -1, 1) and
    put 5 mm off the mirror plane, on the side its normal points to, at the point of the plane 40 mm along
    normal x axis from (1, 2, 3): about 40 mm from the rotation axis. Nothing of the cell reaches the plane (its
    corners lie within 3.4 mm of its centre), so the cell and its mirror image are apart, and the pair spans much less
    than 72° about the axis, so the five turns of the pair are apart too. The sphere (radius 4) starts 30 mm further
    along the rotation axis than the cell, and each translation takes it 24 mm further along it. The free box is the
    bounding box of all copies, 15 mm larger on every side."""
    n, a = _unit(V(*MIRROR["normal"])), _unit(V(*ROTATE["axis"]))
    foot = V(*MIRROR["point"]) + _unit(n.cross(a)) * 40
    centre = foot + n * 5
    local = Part.makeBox(4, 3, 2)
    wedge = Part.makeWedge(0, 3, 0, 0.5, 1, 4, 5, 2, 1.5, 3)  # base: the box's top face (y = 3), top at y = 5
    turn = App.Placement(V(), App.Rotation(V(2, -1, 1), 37))
    middle = V(2, 2.5, 1)  # the middle of both together: x 0..4, y 0..5, z 0..2
    place = App.Placement(centre - turn.Rotation.multVec(middle), turn.Rotation)
    box = symcases.feature(doc, "Block", local.transformed(place.toMatrix()))
    roof = symcases.feature(doc, "Roof", wedge.transformed(place.toMatrix()))
    on_axis = V(*ROTATE["point"]) + a * ((centre - V(*ROTATE["point"])).dot(a) + 30)
    ball = symcases.feature(doc, "Ball", Part.makeSphere(4, on_axis))
    return box, roof, ball


def general_study(doc):
    """Group 1: the box and the wedge, Mirror then Rotate 72° x 5 about the oblique axis; group 2: the sphere,
    Translate (40, 7, 9) x 3; a Box Air Region around them all."""
    box, roof, ball = arrangement(doc)
    study = objects.make_study(doc, "3D")
    study.MeshSizesGroup.DefaultMeshSize = 8
    lib = symcases.libraries(study)
    symcases.group(
        study,
        "Pair",
        [box, roof],
        [MIRROR, ROTATE],
        rows={"Roof": {"mode": "each"}},
        lib={"Block": lib["Steel"], "Roof": lib["Copper"]},
    )
    symcases.group(study, "Balls", [ball], [TRANSLATE], rows={"Ball": {"mode": "each"}}, lib={"Ball": lib["Steel"]})
    for cell, size in ((box, 1.2), (roof, 1.2), (ball, 1.6)):
        objects.make_mesh_size(study, size, [(cell, "")])
    reach = App.BoundBox()
    for item in objects.symmetric_groups(study):
        reach.add(item.Shape.BoundBox)
    reach.enlarge(15)
    air = objects.make_air_region(
        study, "Box", Center=reach.Center, Length=reach.XLength, Width=reach.YLength, Height=reach.ZLength
    )
    objects.assign(study, [air], lib["Air"], 0, name="Air")
    return study


@pytest.fixture
def study(tmp_path):
    doc = App.newDocument("RulesGeneral")
    study = general_study(doc)
    symcases.finish(study, str(tmp_path / "general.FCStd"))
    yield study
    App.closeDocument(doc.Name)


def test_nothing_overlaps_and_everything_is_in_the_free_box(study):
    """How the arrangement was checked: no two solids of the drawings share volume (the box and wedge of one copy
    touch over a face, nothing else touches) and every copy lies inside the free box."""
    solids = [s for item in objects.symmetric_groups(study) for s in item.Shape.Solids]
    assert len(solids) == 2 * 10 + 3
    for a, b in itertools.combinations(solids, 2):
        assert a.common(b).Volume < 1e-9
    air = objects.air_regions(study)[0].Shape
    assert all(air.common(s).Volume == pytest.approx(s.Volume) for s in solids)
    pair = [s for s in objects.symmetric_groups(study)[0].Shape.Solids]
    gaps = [a.distToShape(b)[0] for a, b in itertools.combinations(pair, 2)]
    assert sum(g < 1e-9 for g in gaps) == 10  # only each copy's box and wedge touch
    assert min(g for g in gaps if g > 1e-9) > 1


def test_arbitrary_solids_oblique_rules_groups_and_free_body(study):
    """Group 1: a box and a touching wedge, Mirror about the plane through (1, 2, 3) with normal (1, 1, 2), then
    Rotate 72° × 5 about the axis (1, 2, 2) through (0, 3, 0). Group 2: a sphere, Translate (40, 7, 9) × 3.
    Free: one big box. Mirrored and rotated cells are chosen so that nothing overlaps."""
    assert not validation.errors(validation.validate(study))
    report = symcases.mesh_and_read(study)
    assert report.ok, report.refused
    assert report.inverted == 0 and report.faces_in_three == 0 and report.frozen_kept
    assert report.kept > 0  # the free air meets the copies: their facets are shared, not left open
    parts = {int(study.MatIds[m.Name]) for m in objects.part_assignments(study)}
    assert len(parts) == 1 + 10 + 3  # the box one part, each wedge and each sphere its own
    air = int(study.MatIds[objects.air_regions(study)[0].Name])
    assert set(meshreport.groups(jobwriter.mesh_file(study))) == parts | {air}
    assert symmetry.copy_count([MIRROR, ROTATE]) == 10 and math.isclose(symmetry.det(symmetry.rule_matrix(MIRROR)), -1)


def test_a_frozen_face_not_kept_is_seen(study):
    """The frozen-face check can fail: with the free air's elements taken out of the mesh file, the copies' surface
    faces the inside of the free box with no element there."""
    assert symcases.mesh_and_read(study).frozen_kept
    path = jobwriter.mesh_file(study)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        gmsh.model.removePhysicalGroups([(3, int(study.MatIds[objects.air_regions(study)[0].Name]))])
        gmsh.write(path)
    finally:
        gmsh.finalize()
    report = symcases.read_mesh(study)
    assert not report.frozen_kept and report.lost > 0 and report.kept == 0


def source(name):
    with open(os.path.join(os.path.dirname(jobwriter.__file__), name), encoding="utf-8") as fh:
        return fh.read()


def test_core_code_knows_no_device():
    for name in ("meshfrozen.py", "meshgroups.py", "symmetry.py", "validation.py"):
        assert not re.search(r"\b(motor|slot|stator|rotor|strand|litz|winding)\b", source(name), re.I), name
