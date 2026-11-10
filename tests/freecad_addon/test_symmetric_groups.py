"""Symmetric Group item: its rules, rows and the drawing of all the copies.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py"""

import math

import pytest

import FreeCAD as App

from emsolution import geometry, objects

from . import symcases

# the stator cell (0..15 degrees) mirrored about its edge at 15 degrees, then turned 12 times by 30 degrees
STATOR_RULES = [
    {
        "kind": "mirror",
        "point": [0, 0, 0],
        "normal": [-math.sin(math.radians(15)), math.cos(math.radians(15)), 0],
    },
    {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 30, "count": 12},
]
MIRROR_X0 = {"kind": "mirror", "point": [0, 0, 0], "normal": [1, 0, 0]}
TRANSLATE_24 = {"kind": "translate", "vector": [24, 0, 0], "count": 2}


@pytest.fixture
def study(tmp_path):
    doc = App.newDocument("SymGroups")
    info = symcases.group_motor_doc(doc)
    study = objects.make_study(doc, "2D")
    objects.make_symmetric_group(study, info["stator_cells"], rules=STATOR_RULES, name="Stator")
    doc.recompute()
    doc.saveAs(str(tmp_path / "t.FCStd"))
    yield study
    for name in list(App.listDocuments()):  # a test may have reopened the document under another name
        App.closeDocument(name)


@pytest.fixture
def stator(study):
    (item,) = objects.symmetric_groups(study)
    return item


def test_drawing_has_a_solid_per_row_per_copy(study, stator):
    assert len(stator.Shape.Faces) == 3 * 24
    assert objects.is_grouped(study)
    assert not objects.is_symmetric(study)
    assert stator.Label == "Stator"
    assert stator.Side == "Fixed"


def test_rows_are_one_per_face_of_each_cell(stator):
    rows = objects.rows_of(stator)
    assert [r["cell"] for r in rows] == ["StatorIronCell", "CoilCell", "StatorAirCell"]
    assert all(r["solid"] == 0 and r["mode"] == "one" and r["material"] == "" for r in rows)
    assert all(r["across"] == [] and r["table"] == [] for r in rows)


def test_empty_rules_draw_the_cell(study, stator):
    objects.set_rules(stator, [])
    study.Document.recompute()
    assert len(stator.Shape.Faces) == 3
    assert objects.rules_of(stator) == []


def test_the_drawing_follows_the_rules(study, stator):
    objects.set_rules(stator, [STATOR_RULES[0], {**STATOR_RULES[1], "step": 60, "count": 6}])
    study.Document.recompute()
    assert len(stator.Shape.Faces) == 3 * 12


def test_order_of_rules_is_visible_in_the_drawing(study, stator):
    objects.set_rules(stator, [MIRROR_X0, TRANSLATE_24])  # T-01
    study.Document.recompute()
    first = stator.Shape.BoundBox
    objects.set_rules(stator, [TRANSLATE_24, MIRROR_X0])  # T-02
    study.Document.recompute()
    second = stator.Shape.BoundBox
    assert len(stator.Shape.Faces) == 3 * 4
    assert (first.XMin, first.XMax) != pytest.approx((second.XMin, second.XMax))


def test_huge_count_leaves_the_drawing_empty(study, stator):
    objects.set_rules(stator, [{"kind": "translate", "vector": [1, 0, 0], "count": 100000}])
    study.Document.recompute()
    assert stator.Shape.isNull() or not stator.Shape.Faces


def test_deleted_cell_does_not_raise_on_recompute(study, stator):
    study.Document.removeObject("CoilCell")
    study.Document.recompute()
    assert "Invalid" not in stator.State
    assert stator.Shape.isNull() or not stator.Shape.Faces


def test_cell_in_a_moved_part_is_copied_from_where_it_shows(study, stator):
    doc = study.Document
    part = doc.addObject("App::Part", "Holder")
    part.Placement = App.Placement(App.Vector(0, 0, 5), App.Rotation())
    for cell in stator.Cells:
        part.addObject(cell)
    objects.set_rules(stator, [])
    doc.recompute()
    assert stator.Shape.BoundBox.ZMin == pytest.approx(5)
    assert stator.Shape.BoundBox.ZMax == pytest.approx(5)


def test_group_survives_save_and_reopen(study, stator, tmp_path):
    objects.set_rows(stator, [{**r, "mode": "table", "table": ["A"] * 24} for r in objects.rows_of(stator)])
    study.Document.recompute()
    rules, rows, faces = objects.rules_of(stator), objects.rows_of(stator), len(stator.Shape.Faces)
    path = str(tmp_path / "again.FCStd")
    study.Document.saveAs(path)
    App.closeDocument(study.Document.Name)
    reopened = App.openDocument(path)
    (again,) = objects.symmetric_groups(next(o for o in reopened.Objects if o.Name == "Study"))
    assert objects.rules_of(again) == rules
    assert objects.rows_of(again) == rows
    assert objects.rows_of(again)[0]["table"] == ["A"] * 24
    assert len(again.Shape.Faces) == faces
    assert again.Side == "Fixed"


def test_fragments_cell_has_one_row_per_face(study):
    doc = study.Document
    frag = symcases.coil_fragments(doc)
    (stator,) = objects.symmetric_groups(study)
    cells = [doc.getObject("StatorIronCell"), frag, doc.getObject("StatorAirCell")]
    stator.Cells = cells
    objects.sync_rows(stator)
    doc.recompute()
    assert len([r for r in objects.rows_of(stator) if r["cell"] == "CoilFragments"]) == 2
    assert len(stator.Shape.Faces) == 4 * 24
    assert objects.row_label(stator, objects.rows_of(stator)[1]) != objects.row_label(
        stator, objects.rows_of(stator)[2]
    )


def test_sync_keeps_existing_rows(study, stator):
    rows = objects.rows_of(stator)
    rows[1]["mode"] = "each"
    objects.set_rows(stator, rows)
    objects.sync_rows(stator)
    assert objects.rows_of(stator)[1]["mode"] == "each"
    stator.Cells = [c for c in stator.Cells if c.Name != "StatorAirCell"]
    objects.sync_rows(stator)
    assert [r["cell"] for r in objects.rows_of(stator)] == ["StatorIronCell", "CoilCell"]


def test_row_shape_label_and_parts(stator):
    row = objects.rows_of(stator)[1]
    assert objects.row_shape(stator, row).Area == pytest.approx(stator.Cells[1].Shape.Area)
    assert objects.row_label(stator, row) == "CoilCell"
    assert objects.row_parts(stator, row) == ["CoilCell"] * 24
    assert len(objects.group_transforms(stator)) == 24
    row["mode"] = "each"
    assert objects.row_parts(stator, row)[:2] == ["CoilCell_1", "CoilCell_2"]


def test_element_owner(study, stator):
    assert objects.element_owner(stator, f"Face{3 * 2 + 2}") == (1, 2)
    assert objects.element_owner(stator, "Face1") == (0, 0)
    assert objects.element_owner(stator, "Face72") == (2, 23)
    assert objects.element_owner(stator, "Face73") is None


def test_empty_main_is_fine_with_groups(study):
    assert geometry.setup(study)[2] == []
    assert objects.assignment_problem(study, [study.Document.getObject("CoilCell")]) == ""
    assert objects.assignment_problem(study, [study.Document.getObject("Study")]) != ""


def test_empty_main_is_still_refused_without_groups():
    doc = App.newDocument("NoGroups")
    try:
        study = objects.make_study(doc, "2D")
        assert geometry.setup(study)[2] != []
        assert objects.assignment_problem(study, []) == objects.NO_MAIN_GEOMETRY
    finally:
        App.closeDocument(doc.Name)


def test_cell_bodies_and_assignable_include_groups(study, stator):
    assert [c.Name for c in objects.cell_bodies(study)] == ["StatorIronCell", "CoilCell", "StatorAirCell"]
    assert stator in objects.assignable(study)


def test_to_cells_moves_a_pick_on_the_drawing_to_the_cell(study, stator):
    coil = study.Document.getObject("CoilCell")
    shape = geometry.global_shape(stator)
    pick = f"Face{3 * 5 + 2}"  # the coil in the sixth copy
    assert shape.getElement(pick).CenterOfMass.distanceToPoint(geometry.global_shape(coil).CenterOfMass) > 1
    (got,) = objects.to_cells(study, [(stator, pick)])
    assert got[0].Name == "CoilCell" and got[1] == "Face1"
    (whole,) = objects.to_cells(study, [(stator, pick)], whole=True)
    assert whole == (coil, "")


def test_item_helpers(stator):
    assert objects.is_item(stator)
    assert objects.item_refs(stator) == [(c, "") for c in stator.Cells]
    assert objects._size_text(stator) == "symmetric group"


def test_mirrored_solids_are_valid_and_positive(tmp_path):
    doc = App.newDocument("SymGroups3d")
    try:
        info = symcases.group_motor_doc(doc, height=10)
        study = objects.make_study(doc, "3D")
        item = objects.make_symmetric_group(study, info["stator_cells"], rules=STATOR_RULES)
        doc.recompute()
        solids = item.Shape.Solids
        assert len(solids) == 3 * 24
        assert all(s.isValid() and s.Volume > 0 for s in solids)
        assert objects.element_owner(item, "Solid8") == (1, 2)
        names = [f"Face{i}" for i, f in enumerate(item.Shape.Faces, 1) if any(f.isSame(g) for g in solids[7].Faces)]
        own = [n for n in names if objects.face_solids(item.Shape, n) == ["Solid8"]]
        assert own and all(objects.element_owner(item, n) == (1, 2) for n in own)
    finally:
        App.closeDocument(doc.Name)
