"""Symmetric Group item: its rules, rows and the drawing of all the copies.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py"""

import json
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


# ---- one Material per part


def six_copies(stator, rows=None):
    """The stator turned 6 times by 60 degrees; rows: {cell name: table or None}."""
    objects.set_rules(stator, [{"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 60, "count": 6}])
    rows = rows or {}
    objects.set_rows(
        stator,
        [
            {**r, "mode": "table", "table": rows[r["cell"]]} if rows.get(r["cell"]) else r
            for r in objects.rows_of(stator)
        ],
    )


def library(study):
    from .materialdata import STEEL, record

    return objects.make_library_material(study, json.dumps(record("user:steel", "Steel", "electrical_steel", STEEL)))


def test_each_part_has_one_assignment(study, stator):
    objects.set_rows(stator, [{**r, "mode": "each"} if r["cell"] == "CoilCell" else r for r in objects.rows_of(stator)])
    parts = objects.study_parts(study)
    assert len(parts) == 24 + 2
    assert parts["fixed|CoilCell_3"] == [(stator, 1, 2)]
    assert objects.sync_parts(study) == []
    found = objects.part_assignments(study)
    assert sorted(m.PartKey for m in found) == sorted(parts)
    assert {display for display in (objects.display_name(m) for m in found)} == {k.split("|")[1] for k in parts}
    assert objects.sync_parts(study) == []
    assert len(objects.part_assignments(study)) == 26


def test_same_name_on_two_rows_is_one_part(study, stator):
    six_copies(stator, {"CoilCell": ["A+"] * 6, "StatorIronCell": ["A+"] * 6})
    assert len(objects.study_parts(study)["fixed|A+"]) == 2 * 6


def test_same_name_on_the_two_sides_is_two_parts(study, stator):
    study.Movement = "Sliding motion"
    six_copies(stator, {"CoilCell": ["A+"] * 6})
    rotor = objects.make_symmetric_group(
        study, [study.Document.getObject("RotorIronCell")], name="Rotor", side="Moving"
    )
    objects.set_rows(rotor, [{**r, "mode": "table", "table": ["A+"] * 8} for r in objects.rows_of(rotor)])
    objects.set_rules(rotor, [{"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 45, "count": 8}])
    parts = objects.study_parts(study)
    assert "fixed|A+" in parts and "moving|A+" in parts
    objects.sync_parts(study)
    names = [m.GroupName for m in objects.part_assignments(study) if m.PartKey.endswith("|A+")]
    assert len(names) == 2 and len(set(names)) == 2


def test_no_sliding_means_every_part_is_fixed(study, stator):
    study.Movement = "No movement"
    stator.Side = "Moving"
    assert all(k.startswith("fixed|") for k in objects.study_parts(study))


def test_parts_gone_remove_their_assignment_and_are_reported(study, stator):
    objects.set_rows(stator, [{**r, "mode": "each"} if r["cell"] == "CoilCell" else r for r in objects.rows_of(stator)])
    objects.sync_parts(study)
    objects.set_rows(stator, [{**r, "mode": "one"} if r["cell"] == "CoilCell" else r for r in objects.rows_of(stator)])
    removed = objects.sync_parts(study)
    assert len(removed) == 24 and "CoilCell_2" in removed
    assert len(objects.part_assignments(study)) == 3
    assert not [o for o in study.Document.Objects if getattr(o, "PartKey", "") == "fixed|CoilCell_2"]


def test_removed_name_is_reported(study, stator):
    six_copies(stator, {"CoilCell": ["Coil_1", "Coil_2"] * 3})
    objects.sync_parts(study)
    six_copies(stator, {"CoilCell": ["Coil_1"] * 6})
    assert objects.sync_parts(study) == ["Coil_2"]


def test_rename_keeps_key_and_changes_mesh_name(study, stator):
    objects.sync_parts(study)
    m = next(m for m in objects.part_assignments(study) if m.PartKey == "fixed|CoilCell")
    objects.set_material_name(m, "Winding")
    assert m.PartKey == "fixed|CoilCell"
    assert objects.volume_name(m) == "Winding"
    assert objects.sync_parts(study) == []
    assert m.GroupName == "Winding"


def test_sync_keeps_library_material_and_potential(study, stator):
    lib = library(study)
    objects.sync_parts(study)
    m = next(m for m in objects.part_assignments(study) if m.PartKey == "fixed|CoilCell")
    m.LibraryMaterial, m.Potential = lib, 3
    objects.sync_parts(study)
    assert m.LibraryMaterial == lib and m.Potential == 3


def test_set_row_material_covers_all_its_parts(study, stator):
    lib = library(study)
    objects.set_rows(stator, [{**r, "mode": "each"} if r["cell"] == "CoilCell" else r for r in objects.rows_of(stator)])
    objects.sync_parts(study)
    objects.set_row_material(study, stator, 1, lib)
    coils = [m for m in objects.part_assignments(study) if m.PartKey.startswith("fixed|CoilCell_")]
    assert len(coils) == 24 and all(m.LibraryMaterial == lib for m in coils)
    assert objects.rows_of(stator)[1]["material"] == lib.Name
    others = [m for m in objects.part_assignments(study) if not m.PartKey.startswith("fixed|CoilCell_")]
    assert all(m.LibraryMaterial is None for m in others)


def test_new_part_takes_the_library_material_of_its_row(study, stator):
    lib = library(study)
    objects.set_row_material(study, stator, 0, lib)
    objects.sync_parts(study)
    m = next(m for m in objects.part_assignments(study) if m.PartKey == "fixed|StatorIronCell")
    assert m.LibraryMaterial == lib


def test_part_refs_and_item_refs(study, stator):
    six_copies(stator, {"CoilCell": ["A+", "B+"] * 3})
    objects.sync_parts(study)
    m = next(m for m in objects.part_assignments(study) if m.PartKey == "fixed|B+")
    assert objects.part_refs(m) == [(stator, "Face5"), (stator, "Face11"), (stator, "Face17")]
    assert objects.item_refs(m) == objects.part_refs(m)


def test_one_mat_id_per_part(study, stator):
    study.Movement = "Sliding motion"
    iface = objects.make_sliding_interface(study)
    objects.sync_parts(study)
    objects.update_ids(study)
    assert set(study.MatIds) == {m.Name for m in objects.part_assignments(study)} | {iface.Name}


def test_material_rows_list_free_bodies_and_parts(study, stator):
    lib = library(study)
    objects.sync_parts(study)
    objects.set_row_material(study, stator, 1, lib)
    objects.update_ids(study)
    rows = objects.material_rows(study)
    parts = objects.part_assignments(study)
    tail = rows[len(rows) - len(parts) :]
    assert [r[0] for r in tail] == parts
    assert stator not in [r[0] for r in rows]
    coil = next(r for r in tail if r[0].PartKey == "fixed|CoilCell")
    assert coil[2] == ["CoilCell", lib.Label, study.MatIds[coil[0].Name], "0"]
    assert coil[1] == objects.part_refs(coil[0])


def test_excitation_on_a_group_is_kept():
    doc = App.newDocument("SymGroupsExc")
    try:
        info = symcases.group_motor_doc(doc, height=10)
        study = objects.make_study(doc, "3D")
        item = objects.make_symmetric_group(study, info["stator_cells"], rules=STATOR_RULES)
        doc.recompute()
        exc = objects.make_excitation(study, "Coil", [(item, "Face2")])
        objects.sync_parts(study)
        objects.update_ids(study)
        assert f"{exc.Name}|{item.Name}" in study.SmatIds
    finally:
        App.closeDocument(doc.Name)
