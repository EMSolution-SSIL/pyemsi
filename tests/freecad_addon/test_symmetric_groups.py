"""Symmetric Group item: its rules, rows and the drawing of all the copies.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py"""

import json
import math
import os
import subprocess
import sys
import time

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


def test_rows_are_one_per_cell_object(stator):
    rows = objects.rows_of(stator)
    assert [r["cell"] for r in rows] == ["StatorIronCell", "CoilCell", "StatorAirCell"]
    assert all(r["solid"] is None and r["mode"] == "one" and r["material"] == "" for r in rows)
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


def test_fragments_cell_has_one_row_until_split(study):
    doc = study.Document
    frag = symcases.coil_fragments(doc)
    (stator,) = objects.symmetric_groups(study)
    cells = [doc.getObject("StatorIronCell"), frag, doc.getObject("StatorAirCell")]
    stator.Cells = cells
    objects.sync_rows(stator)
    doc.recompute()
    assert [r["solid"] for r in objects.rows_of(stator) if r["cell"] == "CoilFragments"] == [None]
    assert len(stator.Shape.Faces) == 4 * 24
    # the winding of the whole coil goes by the centre of both its blocks, as for the coil drawn as one face
    whole = objects.winding_table(stator, 1, STATOR_RULES[1], 12, 1, per_coil=True, layer="whole")
    assert whole[:4] == ["Coil01", "Coil01", "Coil02", "Coil02"] and whole[-1] == "Coil12"
    assert objects.split_row(stator, 1)
    doc.recompute()
    assert [r["solid"] for r in objects.rows_of(stator) if r["cell"] == "CoilFragments"] == [0, 1]
    assert len(stator.Shape.Faces) == 4 * 24
    assert objects.row_label(stator, objects.rows_of(stator)[1]) != objects.row_label(
        stator, objects.rows_of(stator)[2]
    )


# ---- a cell object of several faces: one row, split into blocks on request (D-01)


@pytest.fixture
def transformer(tmp_path):
    """(study, group) of the D-01 transformer quarter: the core a Fragments of three faces, the coil, the air."""
    doc = App.newDocument("Transformer")
    cells = symcases.transformer_doc(doc)
    study = objects.make_study(doc, "2D")
    item = objects.make_symmetric_group(
        study, [cells["core"], cells["coil"], cells["air"]], rules=symcases.TRANSFORMER_RULES, name="Transformer"
    )
    doc.recompute()
    doc.saveAs(str(tmp_path / "transformer.FCStd"))
    yield study, item
    for name in list(App.listDocuments()):
        App.closeDocument(name)


def _cells_and_solids(item):
    return [(r["cell"], r["solid"]) for r in objects.rows_of(item)]


def test_a_cell_object_of_three_faces_has_one_row(transformer):
    study, item = transformer
    assert _cells_and_solids(item) == [("CoreCell", None), ("CoilCell", None), ("AirCell", None)]
    core = objects.rows_of(item)[0]
    assert objects.row_label(item, core) == "CoreCell"
    assert len(objects.row_pieces(item, core)) == 3
    assert objects.row_shape(item, core).Area == pytest.approx(42 * 32 - 19 * 22)
    assert len(item.Shape.Faces) == 5 * 4
    assert not objects.stale_drawing(item)


@pytest.mark.parametrize(
    "mode, across, names",
    [
        ("one", [], ["CoreCell"] * 4),
        ("each", [], ["CoreCell_1", "CoreCell_2", "CoreCell_3", "CoreCell_4"]),
        ("across", [0], ["CoreCell_1", "CoreCell_1", "CoreCell_2", "CoreCell_2"]),
    ],
)
def test_copies_of_a_whole_cell_object_give_a_part_per_the_rows_mode(transformer, mode, across, names):
    study, item = transformer
    rows = objects.rows_of(item)
    rows[0].update(mode=mode, across=across)
    objects.set_rows(item, rows)
    assert objects.row_parts(item, rows[0]) == names
    objects.sync_parts(study)
    core = sorted(m.GroupName for m in objects.part_assignments(study) if m.GroupName.startswith("Core"))
    assert core == sorted(set(names))


def test_split_into_blocks_and_join_again(transformer):
    study, item = transformer
    lib = library(study)
    rows = objects.rows_of(item)
    rows[0]["mode"] = "each"
    objects.set_rows(item, rows)
    objects.set_row_material(study, item, 0, lib)
    objects.sync_parts(study)
    assert len(objects.part_assignments(study)) == 4 + 1 + 1
    first = [f.CenterOfMass for f in item.Shape.Faces[:5]]
    assert objects.split_row(item, 0)
    study.Document.recompute()
    assert _cells_and_solids(item)[:3] == [("CoreCell", 0), ("CoreCell", 1), ("CoreCell", 2)]
    blocks = objects.rows_of(item)[:3]
    assert all(r["mode"] == "each" and r["material"] == lib.Name for r in blocks)
    assert [objects.row_label(item, r) for r in blocks] == ["CoreCell_1", "CoreCell_2", "CoreCell_3"]
    assert [f.CenterOfMass for f in item.Shape.Faces[:5]] == first  # the drawing is the same, in the same order
    removed = objects.sync_parts(study)
    assert len(removed) == 4 and len(objects.part_assignments(study)) == 3 * 4 + 1 + 1
    assert not objects.split_row(item, 3)  # the coil has one face: nothing to split
    assert not objects.join_rows(item, 3)
    blocks[1]["mode"] = "one"
    objects.set_rows(item, blocks + objects.rows_of(item)[3:])
    assert objects.join_rows(item, 1)  # the joined row takes the settings of the block it was asked on
    study.Document.recompute()
    assert _cells_and_solids(item) == [("CoreCell", None), ("CoilCell", None), ("AirCell", None)]
    assert objects.rows_of(item)[0]["mode"] == "one"
    objects.sync_parts(study)
    assert sorted(m.GroupName for m in objects.part_assignments(study)) == ["AirCell", "CoilCell", "CoreCell"]


def per_solid(item):
    """The rows of item as a document saved before cell objects had one row: a row per face of the core."""
    rows = objects.rows_of(item)
    old = [{**rows[0], "solid": i} for i in range(3)] + rows[1:]
    objects.set_rows(item, old)
    return old


def test_an_old_per_solid_document_keeps_its_rows_and_validates(transformer):
    study, item = transformer
    old = per_solid(item)
    objects.sync_rows(item)
    assert objects.rows_of(item) == old  # not joined silently
    study.Document.recompute()
    ready(study)
    assert texts(study) == []
    assert sorted(m.GroupName for m in objects.part_assignments(study))[:3] == ["AirCell", "CoilCell", "CoreCell_1"]
    assert len(objects.part_assignments(study)) == 5


def test_a_lone_block_row_of_an_old_document_stays_one_row_when_its_cell_gains_faces(transformer):
    """A document from before cell objects had one row saved every one-face cell as its block 0, as the user's D-01
    file does for its coil and air. Such a row is the whole object: a face added later is in it, not a new part."""
    study, item = transformer
    old = per_solid(item)
    old = old[:3] + [{**row, "solid": 0} for row in old[3:]]
    objects.set_rows(item, old)
    assert _cells_and_solids(item)[3:] == [("CoilCell", None), ("AirCell", None)]
    coil = item.Cells[1]
    left = symcases._polygon((15, 0), (22.5, 0), (22.5, 20), (15, 20))
    coil.Shape = Part.makeCompound([left, symcases._polygon((22.5, 0), (30, 0), (30, 20), (22.5, 20))])
    objects.sync_rows(item)
    study.Document.recompute()
    assert _cells_and_solids(item) == [
        ("CoreCell", 0),
        ("CoreCell", 1),
        ("CoreCell", 2),
        ("CoilCell", None),
        ("AirCell", None),
    ]
    assert objects.row_parts(item, objects.rows_of(item)[3]) == ["CoilCell"] * 4
    assert len(item.Shape.Faces) == (3 + 2 + 1) * 4
    ready(study)
    assert texts(study) == []
    assert [r["file"] is None for r in load_job(study)["symmetric"]["groups"][0]["rows"]] == [False] * 3 + [True] * 2


def test_sync_rows_keeps_the_whole_row_of_a_cell_with_block_rows_besides(transformer):
    study, item = transformer
    rows = objects.rows_of(item)
    rows[0].update(mode="each")
    objects.set_rows(item, [{**rows[0], "solid": 1, "mode": "one"}] + rows)
    objects.sync_rows(item)
    assert _cells_and_solids(item) == [("CoreCell", None), ("CoilCell", None), ("AirCell", None)]
    assert objects.rows_of(item)[0]["mode"] == "each"


def test_a_cell_with_a_whole_row_and_block_rows_is_refused(transformer):
    study, item = transformer
    ready(study)
    objects.set_rows(item, [{**objects.rows_of(item)[0], "solid": 1}] + objects.rows_of(item))
    study.Document.recompute()
    assert any("CoreCell" in t and "whole" in t for t in texts(study)), texts(study)


def test_element_owner_and_part_refs_of_a_whole_cell_object(transformer):
    study, item = transformer
    # each copy draws the core's three faces, then the coil, then the air
    assert [objects.element_owner(item, f"Face{k}") for k in (1, 3, 4, 5, 6, 20)] == [
        (0, 0),
        (0, 0),
        (1, 0),
        (2, 0),
        (0, 1),
        (2, 3),
    ]
    assert objects.element_owner(item, "Face21") is None
    objects.sync_parts(study)
    (core,) = [m for m in objects.part_assignments(study) if m.GroupName == "CoreCell"]
    refs = objects.part_refs(core)
    assert [s for _, s in refs] == [f"Face{5 * c + k}" for c in range(4) for k in (1, 2, 3)]
    assert sum(item.Shape.getElement(s).Area for _, s in refs) == pytest.approx(4 * (42 * 32 - 19 * 22))
    assert objects.by_copy(refs) == [refs[3 * c : 3 * c + 3] for c in range(4)]  # the Material panel's lines
    assert objects.part_of_pick(study, item, "Face7") == (core, 0)
    (coil,) = [m for m in objects.part_assignments(study) if m.GroupName == "CoilCell"]
    assert [s for _, s in objects.part_refs(coil)] == ["Face4", "Face9", "Face14", "Face19"]


def test_element_owner_and_part_refs_of_a_whole_cell_object_in_3d():
    """A box cut in two by a Boolean Fragments, mirrored: each copy of its one row is two solids."""
    import BOPTools.SplitFeatures

    doc = App.newDocument("Blocks3d")
    try:
        box = symcases.feature(doc, "Box", Part.makeBox(10, 10, 10))
        wall = symcases.feature(
            doc,
            "Wall",
            Part.Face(Part.makePolygon([App.Vector(6, y, z) for y, z in ((0, 0), (10, 0), (10, 10), (0, 10), (0, 0))])),
        )
        frag = BOPTools.SplitFeatures.makeBooleanFragments(name="TwoBlocks")
        frag.Objects = [box, wall]
        frag.Mode = "Standard"
        doc.recompute()
        assert len(frag.Shape.Solids) == 2
        study = objects.make_study(doc, "3D")
        item = objects.make_symmetric_group(study, [frag], rules=[MIRROR_X0], name="Blocks")
        doc.recompute()
        assert _cells_and_solids(item) == [("TwoBlocks", None)] and len(item.Shape.Solids) == 4
        assert [objects.element_owner(item, f"Solid{k}") for k in range(1, 6)] == [(0, 0), (0, 0), (0, 1), (0, 1), None]
        faces = [f"Face{i}" for i in range(1, len(item.Shape.Faces) + 1)]
        inner = next(f for f in faces if objects.face_solids(item.Shape, f) == ["Solid1", "Solid2"])
        assert objects.element_owner(item, inner) == (0, 0)
        assert [objects.part_name_of(item, s) for s in ("Solid1", "Solid2")] == ["TwoBlocks", "TwoBlocks"]
        objects.sync_parts(study)
        (m,) = objects.part_assignments(study)
        refs = objects.part_refs(m)
        assert refs == [(item, f"Solid{k}") for k in range(1, 5)]
        assert objects.by_copy(refs) == [refs[:2], refs[2:]]
        rows = objects.rows_of(item)
        rows[0]["mode"] = "each"
        objects.set_rows(item, rows)
        objects.sync_parts(study)
        (second,) = [m for m in objects.part_assignments(study) if m.GroupName == "TwoBlocks_2"]
        assert objects.part_refs(second) == [(item, "Solid3"), (item, "Solid4")]
        assert objects.part_name_of(item, "Solid1") != objects.part_name_of(item, "Solid3")
    finally:
        App.closeDocument(doc.Name)


def structured_core(study, item):
    """Transfinite Body and Recombine on the core's faces, 4 elements on each of its edges, as the user set it."""
    core = item.Cells[0]
    faces = [(core, f"Face{i}") for i in range(1, len(core.Shape.Faces) + 1)]
    objects.make_transfinite_body(study, []).References = faces
    objects.make_transfinite_edges(study, 4, [(core, f"Edge{i}") for i in range(1, len(core.Shape.Edges) + 1)])
    objects.make_recombine(study, []).References = faces
    study.Document.recompute()


def mesh_parts(study):
    """{part name: element count} of the meshed Study, and the element type names."""
    r = run_mesher(study, jobwriter.write_job(study))
    assert r.returncode == 0, r.stderr
    path = jobwriter.mesh_file(study)
    kinds, inverted, _ = mesh_check(path, ())
    assert inverted == 0
    return {name: n for name, n in meshreport.groups(path).values()}, kinds


def test_a_whole_cell_object_of_three_faces_meshes_as_one_part(transformer):
    study, item = transformer
    structured_core(study, item)
    ready(study)
    assert texts(study) == []
    job = load_job(study)
    (group,) = job["symmetric"]["groups"]
    assert [(r["cell"], r["file"]) for r in group["rows"]] == [(1, None), (2, None), (3, None)]
    whole, kinds = mesh_parts(study)
    assert sorted(whole) == ["AirCell", "CoilCell", "CoreCell"]
    assert any(k.startswith("Quadrilateral") for k in kinds), kinds
    assert whole["CoreCell"] == 4 * 3 * 4 * 4  # four copies of three structured faces of 4 x 4 quads
    # the same Study saved with a row per face of the core meshes the same, with a part per face
    per_solid(item)
    study.Document.recompute()
    ready(study)
    assert texts(study) == []
    group = load_job(study)["symmetric"]["groups"][0]
    assert [r["cell"] for r in group["rows"]] == [1, 1, 1, 2, 3] and all(r["file"] for r in group["rows"][:3])
    split, _ = mesh_parts(study)
    assert sorted(split) == ["AirCell", "CoilCell", "CoreCell_1", "CoreCell_2", "CoreCell_3"]
    assert sum(split[f"CoreCell_{k}"] for k in (1, 2, 3)) == whole["CoreCell"]
    assert (split["AirCell"], split["CoilCell"]) == (whole["AirCell"], whole["CoilCell"])


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


def test_air_region_round_the_copies_validates(study):
    ready(study)
    objects.make_air_region(study, "Sector", OuterRadius=90)
    study.Document.recompute()
    assert texts(study) == []


def test_air_region_smaller_than_the_copies_names_the_group(study):
    ready(study)
    objects.make_air_region(study, "Sector", OuterRadius=50)
    study.Document.recompute()
    assert any("Stator" in t and "not fully inside Air Region" in t for t in texts(study))


def test_custom_air_on_a_cell_object_is_refused(study):
    ready(study)
    objects.make_air_region(study, "Custom", Source=study.Document.getObject("CoilCell"))
    study.Document.recompute()
    assert any("CoilCell is the Custom shape of Air Region" in t for t in texts(study))


def test_two_air_regions_are_refused_in_a_grouped_study(study):
    ready(study)
    for _ in range(2):
        objects.make_air_region(study, "Sector", OuterRadius=90)
    study.Document.recompute()
    assert any(t.startswith("Only one Air Region per Study") for t in texts(study))


def test_padding_air_sizes_round_the_drawing(study, stator):
    ready(study)
    air = objects.make_air_region(study, "Sector", SizeMode="Padding", PadOuterPercent=20)
    study.Document.recompute()
    assert [o.Name for o in air.SizedBy] == [stator.Name]  # the group, not its cell objects
    assert air.OuterRadius.Value == pytest.approx(60 * 1.2)  # the drawing reaches r 60; one cell alone would too,
    assert air.Shape.BoundBox.isInside(stator.Shape.BoundBox)  # but only the drawing covers the full circle


def test_padding_air_follows_a_moved_drawing_on_validate(study, stator):  # Review Focus 1
    doc = study.Document
    ready(study)
    part = doc.addObject("App::Part", "Holder")
    for cell in stator.Cells:
        part.addObject(cell)
    air = objects.make_air_region(study, "Sector", SizeMode="Padding", PadOuterPercent=20)
    doc.recompute()
    assert air.OuterRadius.Value == pytest.approx(60 * 1.2)
    part.Placement = App.Placement(App.Vector(5, 0, 0), App.Rotation())
    doc.recompute()
    validation.validate(study)
    reach = airshapes.radial_extent([stator.Shape])[1]
    assert reach > 60 + 1  # the drawing moved with the Part
    assert air.OuterRadius.Value == pytest.approx(reach * 1.2)


def test_air_has_one_mat_id_key_when_sliding(study):
    sliding(study)
    ready(study)
    air = objects.make_air_region(study, "Sector", InnerRadius=60, OuterRadius=90)
    study.Document.recompute()
    assert air.Name in objects.volume_keys(study) and f"{air.Name}#fixed" not in objects.volume_keys(study)


def test_sliding_interface_keeps_its_radius_beside_an_air_region(study):  # Review Focus 3
    sliding(study)
    air = objects.make_air_region(study, "Sector", InnerRadius=60, OuterRadius=90)
    (iface,) = objects.sliding_interfaces(study)
    assert iface.AirRegion is None
    iface.AirRegion = air  # an older document
    study.Document.recompute()
    assert iface.Shape.Edges[0].Curve.Radius == pytest.approx(35)


def test_air_region_across_the_sliding_surface_is_a_limit_of_the_tool(study):
    sliding(study)
    ready(study)
    objects.make_air_region(study, "Sector", OuterRadius=90)
    study.Document.recompute()
    assert any("Air Region" in t and "Sliding Interface" in t and "a limit of the tool" in t for t in texts(study))


def test_transfinite_air_region_is_refused_with_groups(study):
    ready(study)
    air = objects.make_air_region(study, "Sector", OuterRadius=90)
    objects.make_transfinite_body(study, [air])
    study.Document.recompute()
    found = [t for t in texts(study) if "Transfinite" in t and "Air" in t]
    assert len(found) == 1, found  # air_refusal says it, once


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


def test_copies_that_overlap_each_other_but_not_the_cell_are_refused(tmp_path):
    """A mirror whose line neither passes through nor is square to the rotation's centre: the rules do not close, so
    copies 1 and 3 overlap each other by half their area although no copy overlaps the drawn cell."""
    doc = App.newDocument("SymOpen")
    try:
        face = Part.Face(Part.makePolygon([V(1, 1, 0), V(3, 1, 0), V(3, 2, 0), V(1, 2, 0), V(1, 1, 0)]))
        cell = symcases.feature(doc, "Cell", face)
        study = objects.make_study(doc, "2D")
        lib = symcases.libraries(study)
        rules = [
            {"kind": "mirror", "point": [1, 0.75, 0], "normal": [2, 1.5, 0]},
            {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 90, "count": 2},
        ]
        item = symcases.group(study, "G", [cell], rules, rows={"Cell": {"mode": "each"}})
        objects.sync_parts(study)
        objects.set_row_material(study, item, 0, lib["Steel"])
        doc.recompute()
        doc.saveAs(str(tmp_path / "t.FCStd"))
        faces = item.Shape.Faces
        assert faces[1].common(faces[3]).Area == pytest.approx(1.0)
        found = [t for t in texts(study) if "overlaps" in t]
        assert found and "Symmetric Group G" in found[0] and "1 mm²" in found[0], texts(study)
        assert "copy 2 of cell body Cell overlaps copy 4 of Cell" in found[0], found[0]
        assert faces[1].common(faces[3]).CenterOfMass.Length == pytest.approx(0, abs=1e-9)
        assert "near (0, 0)" in found[0], found[0]  # where the two copies lie, not where the cell is drawn
    finally:
        App.closeDocument(doc.Name)


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


def test_free_body_over_the_copies_is_refused(study):
    ready(study)
    free_body(study, "FreeAir", Part.Face(Part.Wire(Part.makeCircle(80))))
    (text,) = [t for t in texts(study) if t.startswith("Free object")]
    assert "FreeAir overlaps the copies of Symmetric Group Stator" in text and "Custom shape of the Air Region" in text


def test_free_body_flush_against_the_copies_validates(study):
    ready(study)
    ring = Part.Face(Part.Wire(Part.makeCircle(90))).cut(Part.Face(Part.Wire(Part.makeCircle(60)))).Faces[0]
    free_body(study, "Ring", ring)
    assert texts(study) == []


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
    assert any("crosses it" in t for t in texts(study_3d)), texts(study_3d)  # the drawn air cell crosses


def test_copies_turned_about_x_across_the_interface_are_not_said_to_cross(study_3d):  # T-07
    """A rule about X is refused for the interface. Its copies lie across the cylinder about Z though the cell objects
    are drawn clear of it: the crossing is not reported besides, as splitting the cell objects would not help."""
    (stator,) = objects.symmetric_groups(study_3d)
    objects.set_rules(stator, [{"kind": "rotate", "point": [0, 0, 0], "axis": [1, 0, 0], "step": 90, "count": 4}])
    study_3d.Movement = "Sliding motion"
    objects.make_sliding_interface(study_3d, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    study_3d.Document.recompute()
    assert validation._reach(stator, 35, True) == "crosses"
    assert not any(validation._drawn_cross(c, 35, True) for c in stator.Cells)
    assert any("about Z" in t for t in texts(study_3d)), texts(study_3d)
    assert not any("crosses it" in t for t in texts(study_3d)), texts(study_3d)


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


def test_groups_apart_in_overlapping_boxes_skip_the_contact_search(monkeypatch):
    import types

    def searched(*args):
        raise AssertionError("searched for contact between solids that are apart")

    monkeypatch.setattr(validation, "_contact", searched)
    ell = Part.makeBox(3, 1, 1).fuse(Part.makeBox(1, 3, 1)).removeSplitter()  # an L round the corner (1, 1)
    near = Part.makeBox(1.9, 1.9, 1, App.Vector(1.1, 1.1, 0))  # in the L's box, 0.1 from it
    a = types.SimpleNamespace(Shape=Part.makeCompound([ell]), Label="A")
    b = types.SimpleNamespace(Shape=Part.makeCompound([near]), Label="B")
    r = validation._Report()
    validation._touch_groups(a, b, True, r)
    assert r.problems == []


def test_mesh_size_on_the_drawing_of_a_group_is_refused(study, stator):
    ready(study)
    objects.make_mesh_size(study, 1.5, [(stator, "")])
    found = [t for t in texts(study) if "copies are not meshed" in t]
    assert found and "Put it on the cell objects" in found[0], texts(study)


# ---- last round: a refusal that is a limit of the tool says so (spec section 1)


def test_an_empty_table_name_says_removing_a_copy_is_a_limit_of_the_tool(study, stator):  # M2-09
    ready(study)
    break_empty_table_name(study, stator)
    found = [t for t in texts(study) if "empty name" in t]
    assert found and "(copy 24)" in found[0], texts(study)
    assert "removing a copy is not handled yet, a limit of the tool" in found[0], found[0]


def test_linear_sliding_with_a_group_says_it_is_a_limit_of_the_tool(study):  # M2-14, M3-04
    _, iface = sliding(study)
    ready(study)
    iface.Kind = "Linear"
    found = [t for t in texts(study) if "slides Rotational only" in t]
    assert found and "not handled yet, a limit of the tool" in found[0], texts(study)


def test_touching_groups_say_it_is_a_limit_of_the_tool(study, stator):  # M3-08
    ready(study)
    break_groups_touch(study, stator)
    ready(study)
    found = [t for t in texts(study) if "one group, or draw" in t]
    assert found and " touch, " in found[0], texts(study)
    assert "touch directly are not handled yet, a limit of the tool" in found[0], found[0]


# ---- last round, fix round 1


def test_a_drawn_cell_across_the_interface_is_reported_beside_a_refused_rule(study_3d):
    """A step along Z is refused for the interface, and the air cell is drawn across r = 35 besides: both are said,
    as the cell object itself has to be split whatever the rules."""
    (stator,) = objects.symmetric_groups(study_3d)
    objects.set_rules(stator, [*STATOR_RULES, {"kind": "translate", "vector": [0, 0, 10], "count": 2}])
    study_3d.Document.getObject("StatorAirCell").Shape = symcases.sector(33, 36, 0, 15).extrude(V(0, 0, 10))
    study_3d.Movement = "Sliding motion"
    objects.make_sliding_interface(study_3d, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    study_3d.Document.recompute()
    found = texts(study_3d)
    assert any("Rule 3 (translate) is not a rotation about Z" in t for t in found), found
    assert any("Symmetric Group Stator crosses it" in t for t in found), found


def test_a_tessellated_cell_overlapping_its_copy_is_refused(tmp_path):
    """A tessellated shape's BoundBox lies inside its triangles, below the true circle: a disk R 10 moved by a little
    less than 20 overlaps its copy, though the BoundBoxes are apart. The exact box finds it."""
    doc = App.newDocument("SymTess")
    try:
        disk = Part.Face(Part.Wire(Part.makeCircle(10)))
        disk.rotate(V(), V(0, 0, 1), 37)
        disk.tessellate(0.5)
        cell = symcases.feature(doc, "Disk", disk)
        shrink = 10 - geometry.global_shape(cell).BoundBox.YMax
        assert shrink > 1e-3
        study = objects.make_study(doc, "2D")
        gap = 20 - 1.5 * shrink
        rules = [{"kind": "translate", "vector": [0, gap, 0], "count": 2}]
        item = symcases.group(study, "G", [cell], rules)
        doc.recompute()
        r = validation._Report()
        validation._overlaps(item, [cell], rules, r)
        assert [p.text for p in r.problems if "overlaps a copy moved by" in p.text], [p.text for p in r.problems]
    finally:
        App.closeDocument(doc.Name)


def test_two_far_copies_that_overlap_are_found_though_far_pairs_are_dropped(tmp_path):
    """A block x 0..4, Translate (10, 0) x 20, then Mirror x = 100.5: the mirrored copy of block a lies at x
    197 - 10a..201 - 10a, over block 20 - a by 1 mm². The drawn cell overlaps no copy, most pairs are far apart and
    dropped, and the first overlapping pair is copies 2 and 40 (blocks 1 and the mirror of block 19)."""
    doc = App.newDocument("SymFar")
    try:
        cell = symcases.feature(doc, "Cell", Part.makePlane(4, 1))
        study = objects.make_study(doc, "2D")
        lib = symcases.libraries(study)
        rules = [
            {"kind": "translate", "vector": [10, 0, 0], "count": 20},
            {"kind": "mirror", "point": [100.5, 0, 0], "normal": [1, 0, 0]},
        ]
        item = symcases.group(study, "G", [cell], rules, rows={"Cell": {"mode": "each"}})
        objects.sync_parts(study)
        objects.set_row_material(study, item, 0, lib["Steel"])
        doc.recompute()
        doc.saveAs(str(tmp_path / "t.FCStd"))
        box = (0, 0, 0, 4, 1, 0)
        assert len(symmetry.relative_transforms(rules, box)) < len(symmetry.relative_transforms(rules)) / 4
        found = [t for t in texts(study) if "overlaps" in t]
        assert found and "copy 2 of cell body Cell overlaps copy 40 of Cell" in found[0], texts(study)
        assert "by 1 mm²" in found[0], found[0]
        faces = item.Shape.Faces
        assert faces[1].common(faces[39]).Area == pytest.approx(1.0)
    finally:
        App.closeDocument(doc.Name)


@pytest.mark.parametrize("order", ["MRU", "URM"])
def test_overlaps_of_5000_sectors_that_reach_the_axis_are_checked_quickly(order):
    """Mirror, 250 turns and 10 steps along Z of a sector from the axis, in either order: every copy of a layer meets
    the others on the axis, and Validate took 12 s (on the GUI thread, and again on Mesh). It takes about 2 s; the
    bound is generous for a loaded machine."""
    doc = App.newDocument("SymAxis")
    try:
        half = 360 / 250 / 2
        a = math.radians(half)
        wire = Part.Wire(
            [
                Part.makeLine(V(0, 0, 0), V(50, 0, 0)),
                Part.makeCircle(50, V(0, 0, 0), V(0, 0, 1), 0, half),
                Part.makeLine(V(50 * math.cos(a), 50 * math.sin(a), 0), V(0, 0, 0)),
            ]
        )
        cell = symcases.feature(doc, "Sector", Part.Face(wire).extrude(V(0, 0, 10)))
        study = objects.make_study(doc, "3D")
        rules = [
            {"kind": "mirror", "point": [0, 0, 0], "normal": [0, 1, 0]},
            {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 2 * half, "count": 250},
            {"kind": "translate", "vector": [0, 0, 10], "count": 10},
        ]
        rules = [rules["MRU".index(c)] for c in order]
        item = symcases.group(study, "G", [cell], [])  # no drawing of the 5000 copies
        r = validation._Report()
        start = time.perf_counter()
        validation._overlaps(item, [cell], rules, r, True)
        assert time.perf_counter() - start < 10
        assert r.problems == []
    finally:
        App.closeDocument(doc.Name)


def test_one_sliding_interface_says_more_is_a_limit_of_the_tool(study):  # M2-13
    sliding(study)
    ready(study)
    objects.make_sliding_interface(study, "Rotational", Radius=36, Divisions=144, CrossDivisions=2)
    found = [t for t in texts(study) if "only one Sliding Interface" in t]
    assert found and "more than one is not handled yet, a limit of the tool" in found[0], texts(study)
    assert "Delete Sliding Interface" in found[0], found[0]


def test_a_linear_interface_in_a_symmetric_study_says_it_is_a_limit_of_the_tool(study):
    _, iface = sliding(study)
    iface.Kind = "Linear"
    with pytest.raises(ValueError, match="slides Rotational only. Linear sliding with Symmetric Groups is not handled"):
        iface.Proxy.execute(iface)


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
    blocks = objects.make_symmetric_group(study, [cell], name="Blocks")
    assert objects.split_row(blocks, 0)
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


def test_air_region_goes_to_the_fixed_free_job(study):
    ready(study)
    air = objects.make_air_region(study, "Sector", OuterRadius=90)
    objects.make_mesh_size(study, 4.0, [(air, "")])
    objects.make_mesh_size(study, 2.0, [(air, "Edge1")])
    study.Document.recompute()
    (free,) = load_job(study)["symmetric"]["free"]
    assert free["side"] == "fixed" and free["job"]["bodies"] == []
    entry = free["job"]["air"]
    assert entry["mat_id"] == int(study.MatIds[air.Name]) and entry["name"] == "Air" and entry["size"] == 4.0
    assert os.path.exists(os.path.join(jobwriter.scratch_folder(study), entry["file"]))
    assert [s["size"] for s in free["job"]["sizes"]] == [2.0]


def test_ring_air_round_a_sliding_motor_validates(study):
    sliding(study)
    ready(study)
    objects.make_air_region(study, "Sector", InnerRadius=60, OuterRadius=90)
    study.Document.recompute()
    assert texts(study) == []


def test_air_gets_a_fixed_job_when_free_bodies_are_only_moving(study):
    sliding(study)
    ready(study)
    objects.make_air_region(study, "Sector", InnerRadius=60, OuterRadius=90)
    free_body(study, "Bore", Part.Face(Part.Wire(Part.makeCircle(8))), side="Moving")
    study.Document.recompute()
    free = {f["side"]: f["job"] for f in load_job(study)["symmetric"]["free"]}
    assert "air" in free["fixed"] and "air" not in free["moving"]


def test_a_study_without_free_bodies_has_no_free(study, stator):
    ready(study)
    assert "free" not in load_job(study)["symmetric"]


def test_z_range_with_sliding(study_3d, tmp_path):
    (stator,) = objects.symmetric_groups(study_3d)
    objects.set_rules(stator, [*STATOR_RULES, MIRROR_Z])
    rotor_group(study_3d, rules=[ROTATE_Z, MIRROR_Z], side="Moving")
    study_3d.Movement = "Sliding motion"
    objects.make_sliding_interface(study_3d, "Rotational", Radius=35, Divisions=144, CrossDivisions=2)
    ready(study_3d)
    study_3d.Document.saveAs(str(tmp_path / "t3.FCStd"))
    block = load_job(study_3d)["symmetric"]
    assert block["slide"]["z_range"] == [-10, 10] and block["slide"]["cross_divisions"] == 2
    assert [len(g["transforms"]) for g in block["groups"]] == [48, 32]
    assert not any("turns" in g for g in block["groups"])  # validation checks the turns; the mesher has no use for them


def test_turns_are_the_rotations_about_z_only():
    assert symmetry.turns_about_z(STATOR_RULES) == 12
    assert symmetry.turns_about_z([*STATOR_RULES, MIRROR_Z]) == 12
    assert (
        symmetry.turns_about_z([{"kind": "rotate", "point": [0, 0, 0], "axis": [1, 0, 0], "step": 90, "count": 4}]) == 1
    )
    assert symmetry.turns_about_z([]) == 1


def test_no_z_range_without_sliding(study, stator):
    ready(study)
    block = load_job(study)["symmetric"]
    assert "slide" not in block


def test_2d_sliding_has_no_z_range(study, stator):
    sliding(study)
    ready(study)
    block = load_job(study)["symmetric"]
    assert "z_range" not in block["slide"] and not any("turns" in g for g in block["groups"])


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


def test_a_finished_mesh_run_shows_the_mesher_notes(monkeypatch):
    """The poor elements are a NOTE: line of the mesher (test_meshgroups); the runner shows the notes once the mesh is
    loaded, and says nothing more when there are none."""
    from emsolution import runner

    shown = []
    monkeypatch.setattr(runner, "notify", shown.append)

    class Run:
        cancelled, error = False, ""
        _close = load_result = lambda self: None

    run = Run()
    for notes in ([], ["Poor elements  North  3 of 120 have a minimum SICN below 0.1"]):
        run.notes = notes
        runner.MeshRun._finished(run, 0, None)
    assert len(shown) == 1 and "Poor elements  North  3 of 120" in shown[0], shown
