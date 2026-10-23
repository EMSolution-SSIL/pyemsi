"""Symmetric Mesh item, Materials on pieces and their MAT_IDs.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py"""

import os

import pytest

import FreeCAD as App

from emsolution import objects

from . import symcases


@pytest.fixture
def motor(tmp_path):
    doc = App.newDocument("SymStudy")
    study = symcases.motor_study(doc)
    doc.saveAs(str(tmp_path / "t.FCStd"))
    yield study
    for name in list(App.listDocuments()):  # a test may have reopened the document under another name
        App.closeDocument(name)


def test_item_shows_cells_and_steps(motor):
    stator, rotor = objects.symmetric_items(motor)
    assert stator.Steps == ["mirror (0, 0) 15°", "rotate (0, 0) 30° × 12"]
    assert len(stator.Cells) == 3
    assert rotor.Steps == ["mirror (0, 0) 22.5°", "rotate (0, 0) 45° × 8"]
    assert objects.is_symmetric(motor)
    assert len(objects.cell_bodies(motor)) == 6
    assert objects._size_text(stator) == "symmetric"


def test_piece_assignment_gets_one_mat_id_keyed_by_itself(motor):
    objects.update_ids(motor)
    names = {m.Name for m in objects.piece_assignments(motor)}
    (iface,) = objects.sliding_interfaces(motor)
    assert len(names) == 18
    assert set(motor.MatIds) == names | {iface.Name}
    assert len(set(motor.MatIds.values())) == 19
    assert [m.Label for m in objects.piece_assignments(motor)].count("Coil01") == 1
    rows = objects.material_rows(motor)
    assert len(rows) == 18
    assert {r[2][2] for r in rows} == {motor.MatIds[n] for n in names}
    assert all(r[0] is None and r[2][1] == "Steel" and r[2][3] == "0" for r in rows)


def test_piece_assignment_label_is_kept_on_sync(motor):
    (lib,) = objects.library_materials(motor)
    lib.Label = "Renamed"
    objects.sync_labels(motor)
    coil = next(m for m in objects.piece_assignments(motor) if m.Label == "Coil01")
    assert coil.Label == "Coil01"
    assert len(objects.item_refs(coil)) == 2


def test_mesh_size_on_a_cell_body_is_allowed(motor):
    cell = next(b for b in objects.cell_bodies(motor) if b.Name == "CoilCell")
    assert objects.assignment_problem(motor, [cell]) == ""


def test_save_reload_keeps_pieces_and_item(motor, tmp_path):
    objects.update_ids(motor)
    ids = dict(motor.MatIds)
    doc = motor.Document
    path = os.path.join(str(tmp_path), "t.FCStd")
    doc.saveAs(path)
    App.closeDocument(doc.Name)
    doc = App.openDocument(path)
    study = objects.find_study(doc)
    assert len(objects.piece_assignments(study)) == 18
    coil = next(m for m in objects.piece_assignments(study) if m.Label == "Coil01")
    assert len(coil.Pieces) == 1 and len(coil.Pieces[0][1]) == 2 and coil.Body is None
    stator, _ = objects.symmetric_items(study)
    assert stator.Steps[0] == "mirror (0, 0) 15°" and len(stator.Cells) == 3
    assert dict(study.MatIds) == ids


def test_sliding_interface_without_air_has_a_circle(motor):
    (iface,) = objects.sliding_interfaces(motor)
    assert objects.air_regions(motor) == []
    iface.touch()
    motor.Document.recompute()
    (edge,) = iface.Shape.Edges
    assert edge.isClosed() and edge.Curve.Radius == pytest.approx(35)
