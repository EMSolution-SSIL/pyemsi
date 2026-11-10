"""Symmetric Group item: its rules, rows and the drawing of all the copies.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py"""

import json
import math
import os
import subprocess
import sys

import pytest

import FreeCAD as App
import Part

from emsolution import airshapes, geometry, jobwriter, objects, symmetry, validation

from . import meshreport, symcases
from .test_meshsym import mesh_check
from .test_meshsym3d import mesh_check_3d, surface_group

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


def test_drawing_follows_a_moved_part_on_validate(study, stator):
    """Cells links the cells only: moving the App::Part they sit in does not mark the group for recompute."""
    doc = study.Document
    part = doc.addObject("App::Part", "Holder")
    for cell in stator.Cells:
        part.addObject(cell)
    doc.recompute()
    part.Placement = App.Placement(App.Vector(0, 0, 5), App.Rotation())
    doc.recompute()
    assert objects.stale_drawing(stator)
    validation.refresh_padding(study)
    assert stator.Shape.BoundBox.ZMin == pytest.approx(5)
    assert not objects.stale_drawing(stator)


def test_winding_table_names_each_copy_by_its_slot(stator):
    """Both halves of a mirrored coil are in one slot: the slot comes from the angle of the copy's centre."""
    names = objects.winding_table(stator, 1, STATOR_RULES[1], 12, 1, span=6)
    assert len(names) == 24 and names[:6] == ["A+", "A+", "C-", "C-", "C-", "C-"]
    coils = objects.winding_table(stator, 1, STATOR_RULES[1], 12, 1, per_coil=True, layer="whole")
    assert coils[:4] == ["Coil01", "Coil01", "Coil02", "Coil02"] and coils[-1] == "Coil12"


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


def test_part_of_pick_finds_the_part_and_row_of_a_clicked_copy(study, stator):
    six_copies(stator, {"CoilCell": ["A+", "B+"] * 3})
    objects.sync_parts(study)
    m, row = objects.part_of_pick(study, stator, "Face11")  # copy 3 of row 1, a "B+"
    assert m.PartKey == "fixed|B+" and row == 1
    m, row = objects.part_of_pick(study, stator, "Face1")
    assert m.PartKey == "fixed|StatorIronCell" and row == 0
    assert objects.part_of_pick(study, stator, "Face99") is None


def test_part_of_pick_without_an_assignment_gives_none_for_it(study, stator):
    assert objects.part_of_pick(study, stator, "Face2") == (None, 1)


def test_part_row_is_the_row_of_the_first_copy(study, stator):
    six_copies(stator, {"CoilCell": ["A+", "B+"] * 3})
    objects.sync_parts(study)
    m = next(m for m in objects.part_assignments(study) if m.PartKey == "fixed|B+")
    assert objects.part_row(m) == (stator, 1)
    m.PartKey = "fixed|nothing"
    assert objects.part_row(m) is None


def test_apply_part_material_keeps_the_key(study, stator):
    lib = library(study)
    objects.sync_parts(study)
    m = next(m for m in objects.part_assignments(study) if m.PartKey == "fixed|CoilCell")
    objects.apply_part_material(m, "Winding", lib, 4)
    assert (m.PartKey, m.GroupName, m.LibraryMaterial, m.Potential) == ("fixed|CoilCell", "Winding", lib, 4)
    assert m.Label == "Winding: Steel"


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


# ---- Validate Study (spec section 6)

V = App.Vector
ROTATE_Z = {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 22.5, "count": 16}
MIRROR_Z = {"kind": "mirror", "point": [0, 0, 0], "normal": [0, 0, 1]}


def problems(study, severity="error"):
    from emsolution import validation

    return [p for p in validation.validate(study) if severity is None or p.severity == severity]


def texts(study, severity="error"):
    return [p.text for p in problems(study, severity)]


def ready(study):
    """Every row gets a library material and every part an assignment: the Study validates clean."""
    lib = library(study)
    for item in objects.symmetric_groups(study):
        for r in range(len(objects.rows_of(item))):
            objects.set_row_material(study, item, r, lib)
    objects.sync_parts(study)
    study.Document.recompute()


def rotor_group(study, rules=(ROTATE_Z,), side="Fixed"):
    cells = [study.Document.getObject(n) for n in ("RotorIronCell", "MagnetCell", "RotorAirCell")]
    return objects.make_symmetric_group(study, cells, rules=rules, name="Rotor", side=side)


def sliding(study):
    study.Movement = "Sliding motion"
    rotor = rotor_group(study, side="Moving")
    iface = objects.make_sliding_interface(study, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    return rotor, iface


@pytest.fixture
def study_3d():
    doc = App.newDocument("SymGroups3dV")
    info = symcases.group_motor_doc(doc, height=10)
    study = objects.make_study(doc, "3D")
    objects.make_symmetric_group(study, info["stator_cells"], rules=STATOR_RULES, name="Stator")
    doc.recompute()
    yield study
    App.closeDocument(doc.Name)


def free_body(study, name, shape, side="Main"):
    body = symcases.feature(study.Document, name, shape)
    setattr(study, side + "Mode", "Manual")
    setattr(study, side + "Objects", [*getattr(study, side + "Objects"), body])
    study.Document.recompute()
    return body


def test_the_ready_study_validates_clean(study):
    ready(study)
    assert [(p.severity, p.text) for p in problems(study, None)] == []


def break_zero_normal(study, stator):
    objects.set_rules(stator, [{"kind": "mirror", "point": [0, 0, 0], "normal": [0, 0, 0]}])


def break_2d_axis(study, stator):
    objects.set_rules(stator, [{**ROTATE_Z, "axis": [1, 0, 0]}])


def break_same_mirror_twice(study, stator):
    objects.set_rules(stator, [MIRROR_X0, MIRROR_X0])


def break_coil_past_the_line(study, stator):
    coil = study.Document.getObject("CoilCell")
    coil.Shape = symcases.sector(37, 50, 10, 17)
    study.Document.getObject("StatorIronCell").Shape = symcases.sector(36, 60, 0, 15).cut(coil.Shape).Faces[0]


def break_cells_overlap_in_place(study, stator):
    study.Document.getObject("CoilCell").Shape = symcases.sector(37, 52, 10, 15)  # into the iron above the slot


def break_step_smaller_than_cell(study, stator):
    objects.set_rules(stator, [{"kind": "translate", "vector": [5, 0, 0], "count": 3}])


def break_groups_touch(study, stator):
    rotor_group(study)  # no Sliding motion: both groups are on the fixed side, and their air cells meet at r = 35


def break_part_without_material(study, stator):
    next(iter(objects.part_assignments(study))).LibraryMaterial = None


def break_name_on_both_sides(study, stator):
    rotor, _ = sliding(study)
    for item, n in ((stator, 24), (rotor, 16)):
        rows = objects.rows_of(item)
        objects.set_rows(item, [{**rows[0], "mode": "table", "table": ["A+"] * n}, *rows[1:]])
    ready(study)


def break_table_wrong_length(study, stator):
    objects.set_rows(stator, [{**r, "mode": "table", "table": ["A"] * 5} for r in objects.rows_of(stator)])


def break_empty_table_name(study, stator):
    objects.set_rows(stator, [{**r, "mode": "table", "table": ["A"] * 23 + [""]} for r in objects.rows_of(stator)])


def break_body_in_two_groups(study, stator):
    objects.make_symmetric_group(study, [study.Document.getObject("CoilCell")], rules=[], name="Second")


def break_cell_also_in_main(study, stator):
    study.MainMode, study.MainObjects = "Manual", [study.Document.getObject("CoilCell")]


def break_air_region(study, stator):
    objects.make_air_region(study, "Box")


def break_free_crosses_sliding(study, stator):
    sliding(study)
    free_body(study, "Gap", symcases.sector(30, 40, 0, 90))


def break_free_transfinite(study, stator):
    body = free_body(study, "Plate", Part.makePlane(10, 10, V(100, 0, 0)))
    objects.make_transfinite_body(study, [body])


def break_deleted_cell(study, stator):
    study.Document.removeObject("CoilCell")


def break_names_equal_in_mesh(study, stator):
    rows = objects.rows_of(stator)
    tables = {0: ["A+"] * 24, 1: ["A_"] * 24}
    objects.set_rows(
        stator, [{**r, "mode": "table", "table": tables[i]} if i in tables else r for i, r in enumerate(rows)]
    )


@pytest.mark.parametrize(
    "case,phrase",
    [
        (break_zero_normal, "normal"),
        (break_2d_axis, "axis"),
        (break_same_mirror_twice, "identical"),
        (break_coil_past_the_line, "overlaps"),  # T-04
        (break_step_smaller_than_cell, "overlaps"),  # T-05
        (break_cells_overlap_in_place, "StatorIronCell overlaps CoilCell near"),
        (break_groups_touch, "one group, or draw"),
        (break_part_without_material, "no Material"),
        (break_name_on_both_sides, "both sides"),
        (break_table_wrong_length, "table"),
        (break_empty_table_name, "table"),
        (break_body_in_two_groups, "two groups"),
        (break_cell_also_in_main, "Main"),
        (break_air_region, "Air Region"),
        (break_free_crosses_sliding, "Sliding Interface"),
        (break_free_transfinite, "Transfinite"),
        (break_deleted_cell, "was deleted"),  # Review Focus 3
        (break_names_equal_in_mesh, "in the mesh"),  # Review Focus 5
    ],
)
def test_refused(study, stator, case, phrase):
    ready(study)
    case(study, stator)
    study.Document.recompute()
    assert any(phrase in t for t in texts(study)), texts(study)


def test_cell_without_solid_is_refused(study_3d):
    study_3d.Document.getObject("CoilCell").Shape = symcases.sector(37, 50, 10, 15)
    study_3d.Document.recompute()
    assert any("has no solid" in t for t in texts(study_3d)), texts(study_3d)


def test_sliding_axis_x_is_refused_naming_the_rule(study_3d):  # T-07
    (stator,) = objects.symmetric_groups(study_3d)
    objects.set_rules(stator, [{"kind": "rotate", "point": [0, 0, 0], "axis": [1, 0, 0], "step": 180, "count": 2}])
    study_3d.Movement = "Sliding motion"
    objects.make_sliding_interface(study_3d, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    study_3d.Document.recompute()
    found = [t for t in texts(study_3d) if "about Z" in t]
    assert found and "Rule 1" in found[0] and "limit of the tool" in found[0], texts(study_3d)


def test_free_transfinite_says_it_is_a_limit_of_the_tool(study):
    ready(study)
    break_free_transfinite(study, None)
    found = [t for t in texts(study) if "free object" in t]
    assert found and "limit of the tool" in found[0], texts(study)


def test_the_overlap_message_does_not_talk_of_mirrors_or_arrays(study, stator):
    ready(study)
    break_step_smaller_than_cell(study, stator)
    (found,) = [t for t in texts(study) if "overlaps" in t]
    assert "Symmetric Group Stator" in found and "Polar Array" not in found and "Mirror's line" not in found


def test_divisions_are_a_multiple_of_the_turns_about_z(study, stator):
    sliding(study)
    ready(study)
    assert texts(study) == []
    iface = objects.sliding_interfaces(study)[0]
    iface.Divisions = 100  # not a multiple of the 12 turns of the stator
    assert any("multiple" in t and "Stator" in t for t in texts(study)), texts(study)


def test_rotation_that_does_not_close_is_a_warning(study, stator):
    objects.set_rules(stator, [{**ROTATE_Z, "step": 30, "count": 6}])
    ready(study)
    assert texts(study) == []
    assert any("not 360" in t for t in texts(study, "warning"))


@pytest.mark.parametrize("vector", [[30, 0, 0], [0, 30, 0], [0, 0, 10]])
def test_translation_through_any_axis_validates(study_3d, vector):
    (stator,) = objects.symmetric_groups(study_3d)
    objects.set_rules(stator, [{"kind": "translate", "vector": vector, "count": 2}])
    ready(study_3d)
    assert texts(study_3d) == []


def test_free_air_and_copies_validate(study):
    ready(study)
    free_body(study, "FreeAir", Part.Face(Part.Wire(Part.makeCircle(80))))
    assert texts(study) == []  # the free air may be drawn right over the copies; a missing Material only warns
    assert any("No material" in t and "FreeAir" in t for t in texts(study, "warning"))


def test_x_axis_rules_validate_without_sliding(study_3d):
    (stator,) = objects.symmetric_groups(study_3d)
    objects.set_rules(stator, [{"kind": "rotate", "point": [0, 0, 0], "axis": [1, 0, 0], "step": 180, "count": 2}])
    ready(study_3d)
    assert texts(study_3d) == []


def test_z_mirror_with_sliding_validates(study_3d):
    (stator,) = objects.symmetric_groups(study_3d)
    objects.set_rules(stator, [*STATOR_RULES, MIRROR_Z])
    rotor_group(study_3d, rules=[ROTATE_Z, MIRROR_Z], side="Moving")
    study_3d.Movement = "Sliding motion"
    objects.make_sliding_interface(study_3d, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    ready(study_3d)
    assert texts(study_3d) == []


def test_zx_study_with_a_z_mirror_validates():
    doc = App.newDocument("SymGroupsZX")
    try:
        cell = symcases.feature(doc, "Cell", Part.makePlane(10, 5, V(0, 0, 1), V(0, -1, 0), V(1, 0, 0)))
        study = objects.make_study(doc, "2D")
        objects.make_symmetric_group(study, [cell], rules=[MIRROR_Z])
        doc.recompute()
        ready(study)
        assert texts(study) == []
    finally:
        App.closeDocument(doc.Name)


def test_old_item_is_refused(study, tmp_path):
    """A document saved with the older Symmetric Mesh item opens; Validate asks for a Symmetric Group in its place, and
    the Study's groups are checked as usual."""
    ready(study)
    doc = study.Document
    top = symcases.feature(doc, "OldTop", symcases.sector(36, 60, 0, 15))
    old = doc.addObject("App::FeaturePython", "SymmetricMesh")  # as the older version saved it
    old.Proxy = objects.SymmetricMesh()
    old.addProperty("App::PropertyLinkGlobal", "Top", "EMSolution", "")
    old.Top, old.Label = top, "Old"
    study.MeshSizesGroup.addObject(old)
    name, path = old.Name, str(tmp_path / "old.FCStd")
    doc.saveAs(path)
    App.closeDocument(doc.Name)
    again = objects.find_study(App.openDocument(path))
    found = problems(again)
    assert [p.text for p in found] == [
        "Symmetric Mesh Old is from an older version. Add a Symmetric Group; Read from drawing fills it from OldTop."
    ]
    assert found[0].item.Name == name
    assert [row[2][1] for row in objects.mesh_size_rows(again)] == ["symmetric group", "older version"]


def test_mesh_size_on_a_cell_object_and_excitation_on_the_drawing_are_fine(study_3d):
    (stator,) = objects.symmetric_groups(study_3d)
    study_3d.MeshSizesGroup.DefaultMeshSize = 1.5  # finer than the thinnest cell: no coarse-mesh warning
    ready(study_3d)
    objects.make_mesh_size(study_3d, 1.5, [(study_3d.Document.getObject("CoilCell"), "")])
    objects.make_excitation(study_3d, "Coil", [(stator, "Face2")])
    assert [(p.severity, p.text) for p in problems(study_3d, None)] == []


def test_free_objects_are_checked_as_ordinary_bodies(study):
    ready(study)
    free_body(study, "One", Part.makePlane(10, 10, V(100, 0, 0)))
    free_body(study, "Two", Part.makePlane(10, 10, V(105, 0, 0)))
    assert any("overlap" in t and "One" in t and "Two" in t for t in texts(study)), texts(study)


# ---- fix round 1


def test_a_group_crossing_the_interface_is_refused(study):
    sliding(study)
    ready(study)
    study.Document.getObject("StatorAirCell").Shape = symcases.sector(33, 36, 0, 15)  # across r = 35
    study.Document.recompute()
    found = [t for t in texts(study) if "Sliding Interface" in t and "crosses it" in t]
    assert found and "Stator" in found[0], texts(study)


def test_a_group_crossing_the_interface_still_gets_its_rules_checked(study_3d):  # T-07
    (stator,) = objects.symmetric_groups(study_3d)
    objects.set_rules(stator, [{"kind": "rotate", "point": [0, 0, 0], "axis": [1, 0, 0], "step": 180, "count": 2}])
    study_3d.Document.getObject("StatorAirCell").Shape = symcases.sector(33, 36, 0, 15).extrude(V(0, 0, 10))
    study_3d.Movement = "Sliding motion"
    objects.make_sliding_interface(study_3d, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    study_3d.Document.recompute()
    assert any("about Z" in t for t in texts(study_3d)), texts(study_3d)


@pytest.mark.parametrize("missing,side", [("Rotor", "moving"), ("Stator", "fixed")])
def test_sliding_needs_a_group_reaching_the_interface_on_each_side(study, stator, missing, side):
    sliding(study)
    ready(study)
    assert texts(study) == []
    study.Document.removeObject(next(g for g in objects.symmetric_groups(study) if g.Label == missing).Name)
    objects.sync_parts(study)
    assert any(f"on the {side} side reaches it" in t for t in texts(study)), texts(study)


def test_a_contact_check_that_fails_is_reported(study, stator, monkeypatch):
    from emsolution import validation

    def fails(*args):
        raise Part.OCCError("forced")

    ready(study)
    rotor_group(study)  # same side as the stator: their air cells meet
    ready(study)
    monkeypatch.setattr(validation, "_contact", fails)
    assert not any("one group, or draw" in t for t in texts(study))
    assert any("Could not check contact between" in t and "Stator" in t for t in texts(study, "warning"))


def test_mesh_size_on_the_drawing_of_a_group_is_refused(study, stator):
    ready(study)
    objects.make_mesh_size(study, 1.5, [(stator, "")])
    found = [t for t in texts(study) if "copies are not meshed" in t]
    assert found and "Put it on the cell objects" in found[0], texts(study)


# ---- writing the job (spec section 8)


def load_job(study):
    with open(jobwriter.write_job(study), encoding="utf-8") as fh:
        return json.load(fh)


def run_mesher(study, job_path):
    mesher = os.path.join(
        os.path.dirname(jobwriter.__file__), "mesher2d.py" if study.Dimension == "2D" else "mesher.py"
    )
    return subprocess.run([sys.executable, mesher, job_path], capture_output=True, encoding="utf-8", errors="replace")


def outer_ring():
    """Free air around the stator (r 60): a ring from r 62 to r 90."""
    return Part.Face(Part.Wire(Part.makeCircle(90))).cut(Part.Face(Part.Wire(Part.makeCircle(62)))).Faces[0]


def mat_ids(study, side):
    return {int(study.MatIds[m.Name]) for m in objects.part_assignments(study) if m.PartKey.startswith(side + "|")}


def test_job_holds_a_mini_job_per_group(study, stator):
    sliding(study)
    ready(study)
    job = load_job(study)
    block = job["symmetric"]
    assert [g["name"] for g in block["groups"]] == ["Stator", "Rotor"]
    stator_job, rotor_job = block["groups"]
    assert [g["side"] for g in block["groups"]] == ["fixed", "moving"]
    assert len(stator_job["transforms"]) == 24 and len(rotor_job["transforms"]) == 16
    assert stator_job["transforms"][0] == symmetry.ID
    assert stator_job["cells"] == [1, 2, 3]
    assert [b["mat_id"] for b in stator_job["job"]["bodies"]] == [1, 2, 3]
    assert [b["name"] for b in stator_job["job"]["bodies"]] == ["StatorIronCell", "CoilCell", "StatorAirCell"]
    assert "bodies" not in job and "sizes" not in job and "volumes" not in job
    assert job["dimension"] == "2D" and job["rotor_file"] == jobwriter.rotor_file(study)
    (iface,) = objects.sliding_interfaces(study)
    assert block["slide"]["radius"] == 35 and block["slide"]["name"] == objects.volume_name(iface)
    assert block["slide"]["slide_mat_id"] == int(study.MatIds[iface.Name])
    for g in block["groups"]:
        for body in g["job"]["bodies"]:
            assert os.path.exists(os.path.join(jobwriter.scratch_folder(study), body["file"]))
    assert len({b["file"] for g in block["groups"] for b in g["job"]["bodies"]}) == 6  # no two groups share a file


def test_row_parts_index_the_group_parts(study, stator):
    six_copies(stator, {"CoilCell": ["A+", "B+"] * 3})
    ready(study)
    (group,) = load_job(study)["symmetric"]["groups"]
    ids = {objects.volume_name(m): int(study.MatIds[m.Name]) for m in objects.part_assignments(study)}
    assert [p["name"] for p in group["parts"]] == [
        "StatorIronCell",
        "A_",
        "B_",
        "StatorAirCell",
    ]  # names are cleaned for the mesh
    assert all(p["mat_id"] == ids[p["name"]] for p in group["parts"])
    iron, coil, air = group["rows"]
    assert (iron["cell"], coil["cell"], air["cell"]) == (1, 2, 3)
    assert coil["parts"] == [1, 2, 1, 2, 1, 2] and iron["parts"] == [0] * 6 and air["parts"] == [3] * 6
    assert iron["file"] is None and coil["file"] is None


def test_a_cell_with_several_rows_has_a_file_per_row(study):
    cell = symcases.feature(
        study.Document,
        "TwoBlocks",
        Part.makeCompound([symcases.sector(70, 80, 0, 10), symcases.sector(70, 80, 10, 20)]),
    )
    objects.make_symmetric_group(study, [cell], name="Blocks")
    study.Document.recompute()
    ready(study)
    assert texts(study) == []
    blocks = load_job(study)["symmetric"]["groups"][1]
    assert blocks["name"] == "Blocks" and blocks["cells"] == [1]
    assert [r["cell"] for r in blocks["rows"]] == [1, 1] and all(r["file"] for r in blocks["rows"])
    assert blocks["rows"][0]["file"] != blocks["rows"][1]["file"]
    folder = jobwriter.scratch_folder(study)
    areas = [Part.read(os.path.join(folder, r["file"])).Area for r in blocks["rows"]]
    assert all(abs(a - symcases.sector(70, 80, 0, 10).Area) < 1e-6 for a in areas)


def test_free_bodies_go_to_free_with_final_mat_ids(study, stator):
    sliding(study)
    ready(study)
    free_body(study, "FreeAir", outer_ring())
    free_body(study, "Bore", Part.Face(Part.Wire(Part.makeCircle(8))), side="Moving")
    study.Document.recompute()
    job = load_job(study)
    free = {f["side"]: f["job"] for f in job["symmetric"]["free"]}
    assert sorted(free) == ["fixed", "moving"]
    (air,) = free["fixed"]["bodies"]
    (bore,) = free["moving"]["bodies"]
    assert air["mat_id"] == int(study.MatIds["FreeAir"]) and air["name"] == "FreeAir"
    assert bore["mat_id"] == int(study.MatIds["Bore"])
    assert os.path.exists(os.path.join(jobwriter.scratch_folder(study), air["file"]))
    assert air["file"] != bore["file"] and free["fixed"]["sizes"] == []


def test_a_study_without_free_bodies_has_no_free(study, stator):
    ready(study)
    assert "free" not in load_job(study)["symmetric"]


def test_z_range_and_turns_with_sliding(study_3d, tmp_path):
    (stator,) = objects.symmetric_groups(study_3d)
    objects.set_rules(stator, [*STATOR_RULES, MIRROR_Z])
    rotor_group(study_3d, rules=[ROTATE_Z, MIRROR_Z], side="Moving")
    study_3d.Movement = "Sliding motion"
    objects.make_sliding_interface(study_3d, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    ready(study_3d)
    study_3d.Document.saveAs(str(tmp_path / "t3.FCStd"))
    block = load_job(study_3d)["symmetric"]
    assert block["slide"]["z_range"] == [-10, 10] and block["slide"]["cross_divisions"] == 2
    assert [g["turns"] for g in block["groups"]] == [12, 16]
    assert [len(g["transforms"]) for g in block["groups"]] == [48, 32]


def test_turns_are_the_rotations_about_z_only():
    assert symmetry.turns_about_z(STATOR_RULES) == 12
    assert symmetry.turns_about_z([*STATOR_RULES, MIRROR_Z]) == 12
    assert (
        symmetry.turns_about_z([{"kind": "rotate", "point": [0, 0, 0], "axis": [1, 0, 0], "step": 90, "count": 4}]) == 1
    )
    assert symmetry.turns_about_z([]) == 1


def test_no_turns_and_no_z_range_without_sliding(study, stator):
    ready(study)
    block = load_job(study)["symmetric"]
    assert "slide" not in block and "turns" not in block["groups"][0]


def test_2d_sliding_has_turns_but_no_z_range(study, stator):
    sliding(study)
    ready(study)
    block = load_job(study)["symmetric"]
    assert "z_range" not in block["slide"] and [g["turns"] for g in block["groups"]] == [12, 16]


def test_mesh_settings_go_with_their_cell(study, stator):
    ready(study)
    coil = study.Document.getObject("CoilCell")
    free = free_body(study, "FreeAir", outer_ring())
    objects.make_mesh_size(study, 1.5, [(coil, "")])
    objects.make_mesh_size(study, 0.9, [(coil, "Edge1")])
    objects.make_mesh_size(study, 3.5, [(free, "")])
    objects.make_transfinite_body(study, [coil])
    objects.make_transfinite_edges(study, 6, [(coil, f"Edge{i}") for i in (1, 2, 3, 4)])
    objects.make_recombine(study, [coil])
    study.Document.recompute()
    assert texts(study) == []
    job = load_job(study)
    assert "transfinite" not in job and "recombine" not in job and "sizes" not in job
    (group,) = job["symmetric"]["groups"]
    cell = group["job"]
    assert [(b["name"], b["size"]) for b in cell["bodies"]][1] == ("CoilCell", 1.5)
    assert cell["recombine"] == [2]
    (entry,) = cell["transfinite"]["bodies"]
    assert entry["mat_id"] == 2 and len(cell["transfinite"]["edges"][0]["files"]) == 4
    assert [len(s["files"]) for s in cell["sizes"]] == [1] and cell["sizes"][0]["size"] == 0.9
    (free_job,) = [f["job"] for f in job["symmetric"]["free"]]
    assert free_job["bodies"][0]["size"] == 3.5
    assert "transfinite" not in free_job and "recombine" not in free_job


def test_study_plane_of_a_study_of_groups_is_the_validation_plane():
    doc = App.newDocument("SymGroupsPlane")
    try:
        cell = symcases.feature(doc, "Cell", Part.makePlane(10, 5, V(0, 0, 1), V(0, -1, 0), V(1, 0, 0)))
        study = objects.make_study(doc, "2D")
        objects.make_symmetric_group(study, [cell], rules=[MIRROR_Z])
        doc.recompute()
        assert airshapes.study_plane(study) == "ZX"
        r = validation._Report()
        assert validation._group_plane(study, [cell], [], r) == "ZX" and not r.problems
    finally:
        App.closeDocument(doc.Name)


def test_a_zx_study_of_groups_runs(tmp_path):
    doc = App.newDocument("SymGroupsZXRun")
    try:
        cell = symcases.feature(doc, "Cell", Part.makePlane(10, 5, V(0, 0, 1), V(0, -1, 0), V(1, 0, 0)))
        study = objects.make_study(doc, "2D")
        objects.make_symmetric_group(study, [cell], rules=[MIRROR_Z])
        doc.recompute()
        ready(study)
        doc.saveAs(str(tmp_path / "zx.FCStd"))
        path = jobwriter.write_job(study)
        with open(path, encoding="utf-8") as fh:
            body = json.load(fh)["symmetric"]["groups"][0]["job"]["bodies"][0]
        shape = Part.read(os.path.join(os.path.dirname(path), body["file"]))
        assert all(abs(v.Point.y) < 1e-9 for v in shape.Vertexes)
        r = run_mesher(study, path)
        assert r.returncode == 0, r.stderr
        assert sorted(meshreport.groups(jobwriter.mesh_file(study))) == sorted(mat_ids(study, "fixed"))
    finally:
        App.closeDocument(doc.Name)


def test_group_motor_runs_end_to_end_2d(study, stator):
    sliding(study)
    ready(study)
    free_body(study, "FreeAir", outer_ring())
    study.Document.recompute()
    r = run_mesher(study, jobwriter.write_job(study))
    assert r.returncode == 0, r.stderr
    free = int(study.MatIds["FreeAir"])
    fixed, moving = jobwriter.mesh_file(study), jobwriter.rotor_file(study)
    assert set(meshreport.groups(fixed)) == mat_ids(study, "fixed") | {free}
    assert set(meshreport.groups(moving)) == mat_ids(study, "moving")
    assert [mesh_check(f, ())[1] for f in (fixed, moving)] == [0, 0]


def test_group_motor_runs_end_to_end_3d(study_3d, tmp_path):
    (stator,) = objects.symmetric_groups(study_3d)
    study_3d.MeshSizesGroup.DefaultMeshSize = 1.5
    objects.set_rules(stator, [*STATOR_RULES, MIRROR_Z])
    rotor_group(study_3d, rules=[ROTATE_Z, MIRROR_Z], side="Moving")
    study_3d.Movement = "Sliding motion"
    objects.make_sliding_interface(study_3d, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    ready(study_3d)
    study_3d.Document.saveAs(str(tmp_path / "t3.FCStd"))
    r = run_mesher(study_3d, jobwriter.write_job(study_3d))
    assert r.returncode == 0, r.stderr
    assert set(meshreport.groups(jobwriter.mesh_file(study_3d))) == mat_ids(study_3d, "fixed")
    assert set(meshreport.groups(jobwriter.rotor_file(study_3d))) == mat_ids(study_3d, "moving")
    assert mesh_check_3d(jobwriter.mesh_file(study_3d), (), ())[1] == 0
    assert mesh_check_3d(jobwriter.rotor_file(study_3d), (), ())[1] == 0


def test_excitation_on_the_drawing_is_copied(study_3d, tmp_path):
    (stator,) = objects.symmetric_groups(study_3d)
    study_3d.MeshSizesGroup.DefaultMeshSize = 1.5
    ready(study_3d)
    ends = [
        f"Face{i}"
        for i, face in enumerate(stator.Shape.Faces, 1)
        if abs(face.CenterOfMass.z - 10) < 1e-6 and objects.element_owner(stator, f"Face{i}") == (1, 0)
    ]
    assert ends
    exc = objects.make_excitation(study_3d, "Coil", [(stator, f) for f in ends])
    study_3d.Document.recompute()
    study_3d.Document.saveAs(str(tmp_path / "t3.FCStd"))
    path = jobwriter.write_job(study_3d)
    with open(path, encoding="utf-8") as fh:
        (group,) = json.load(fh)["symmetric"]["groups"]
    smat = int(study_3d.SmatIds[f"{exc.Name}|{stator.Name}"])
    (entry,) = group["excitations"]
    assert entry["smat_id"] == smat and entry["name"] == objects.item_name(exc, stator)
    assert len(entry["files"]) == len(ends)
    r = run_mesher(study_3d, path)
    assert r.returncode == 0, r.stderr
    name, count, _ = surface_group(jobwriter.mesh_file(study_3d), smat)
    assert name == entry["name"] and count > 0
    assert mesh_check_3d(jobwriter.mesh_file(study_3d), (), ())[1] == 0


def test_excitation_on_a_cell_object_is_refused(study_3d):
    ready(study_3d)
    coil = study_3d.Document.getObject("CoilCell")
    objects.make_excitation(study_3d, "Coil", [(coil, "Face2")])
    found = [t for t in texts(study_3d) if "Excitation Coil" in t and "Pick the faces on the drawing" in t]
    assert found and "CoilCell" in found[0], texts(study_3d)
