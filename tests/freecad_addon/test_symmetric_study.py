"""Symmetric Mesh item, Materials on pieces and their MAT_IDs.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py"""

import json
import os

import pytest

import FreeCAD as App

from emsolution import jobwriter, objects

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


# ---- validation


def _problems(study, severity=None):
    from emsolution import validation

    return [p for p in validation.validate(study) if severity in (None, p.severity)]


def _texts(study, severity="error"):
    return [p.text for p in _problems(study, severity)]


def _has(study, *words, severity="error"):
    return any(all(w in t for w in words) for t in _texts(study, severity))


def _tops(study):
    return [i.Top for i in objects.symmetric_items(study)]


def test_motor_study_validates_clean(motor):
    assert [(p.severity, p.text) for p in _problems(motor)] == []


def test_item_without_top_is_an_error(motor):
    stator, _ = objects.symmetric_items(motor)
    stator.Top = None
    found = [p for p in _problems(motor, "error") if "has no top object" in p.text]
    assert found and found[0].item == stator


def test_unreadable_chain_gives_the_symmetry_error_on_the_item(motor):
    stator, _ = objects.symmetric_items(motor)
    array = next(o for o in motor.Document.Objects if o.Label == "StatorArray")
    array.ArrayType = "ortho"
    problems = [p for p in _problems(motor, "error") if "only polar arrays" in p.text]
    assert problems and problems[0].item == stator


def test_two_items_on_one_side_are_refused(motor):
    objects.make_symmetric_mesh(motor, _tops(motor)[0])
    assert _has(motor, "only one Symmetric Mesh per side")


def test_extra_body_in_main_is_refused(motor):
    import Part

    extra = symcases.feature(
        motor.Document, "Extra", Part.Face(Part.makePolygon([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 0, 0)]))
    )
    motor.MainObjects = [*motor.MainObjects, extra]
    assert _has(motor, "only one Symmetric Mesh per side")


def test_air_region_is_refused(motor):
    objects.make_air_region(motor)
    assert _has(motor, "Air Region")


def test_zx_plane_is_refused(motor, monkeypatch):
    from emsolution import airshapes

    monkeypatch.setattr(airshapes, "study_plane", lambda study: "ZX")
    assert _has(motor, "XY plane")


def test_whole_body_assignment_on_a_top_is_refused(motor):
    objects.assign(motor, [_tops(motor)[0]], motor.MaterialsGroup.Group[0].LibraryMaterial, 0)
    assert _has(motor, "pieces")


def test_whole_body_assignment_on_a_cell_body_warns(motor):
    cell = next(b for b in objects.cell_bodies(motor) if b.Name == "CoilCell")
    objects.assign(motor, [cell], motor.MaterialsGroup.Group[0].LibraryMaterial, 0)
    assert _has(motor, "not used", "pieces", severity="warning")
    assert not [t for t in _texts(motor) if "CoilCell" in t]


def test_face_without_material_is_an_error(motor):
    coil = next(m for m in objects.piece_assignments(motor) if m.Label == "Coil01")
    coil.Pieces = []
    motor.Document.recompute()
    assert _has(motor, "no Material", "Face")


def test_face_with_two_materials_is_an_error(motor):
    coil1, coil2 = [m for m in objects.piece_assignments(motor) if m.Label in ("Coil01", "Coil02")]
    coil2.Pieces = [*coil2.Pieces, *coil1.Pieces]
    assert _has(motor, "two Materials", "Face")


def test_assignment_on_both_sides_is_refused(motor):
    stator_top, rotor_top = _tops(motor)
    coil = next(m for m in objects.piece_assignments(motor) if m.Label == "Coil01")
    coil.Pieces = [*coil.Pieces, (rotor_top, ("Face1",))]
    assert _has(motor, "both sides")


def test_piece_on_a_body_that_is_not_a_top_is_refused(motor):
    cell = next(b for b in objects.cell_bodies(motor) if b.Name == "CoilCell")
    coil = next(m for m in objects.piece_assignments(motor) if m.Label == "Coil01")
    coil.Pieces = [*coil.Pieces, (cell, ("Face1",))]
    assert _has(motor, "not a Symmetric Mesh top")


@pytest.mark.parametrize("make", ["size", "recombine"])
def test_mesh_setting_on_a_top_is_refused(motor, make):
    top = _tops(motor)[0]
    if make == "size":
        objects.make_mesh_size(motor, 1.0, [(top, "Face1")])
    else:
        objects.make_recombine(motor, [top])
    assert _has(motor, "copies are not meshed")


def test_transfinite_on_a_top_is_refused(motor):
    top = _tops(motor)[0]
    objects.make_transfinite_edges(motor, 5, [(top, "Edge1")])
    assert _has(motor, "copies are not meshed")


def test_mesh_size_on_a_cell_body_is_fine(motor):
    cell = next(b for b in objects.cell_bodies(motor) if b.Name == "CoilCell")
    objects.make_mesh_size(motor, 1.0, [(cell, "")])
    assert _problems(motor) == []


def test_linear_interface_is_refused(motor):
    (iface,) = objects.sliding_interfaces(motor)
    iface.Kind = "Linear"
    assert _has(motor, "Rotational")


def test_divisions_must_fit_the_copy_count(motor):
    (iface,) = objects.sliding_interfaces(motor)
    iface.Divisions = 146  # 24 copies of the stator cell
    assert _has(motor, "divisions", "24")


def test_changing_array_count_reports_pieces(motor):
    array = next(o for o in motor.Document.Objects if o.Label == "StatorArray")
    array.NumberPolar = 6
    motor.Document.recompute()
    assert _has(motor, "no Material") or _has(motor, "two Materials")


def test_deleted_cell_body_is_an_error(motor):
    stator, _ = objects.symmetric_items(motor)
    motor.Document.removeObject("CoilCell")
    motor.Document.recompute()
    assert [p for p in _problems(motor, "error") if p.item == stator]


def test_duplicate_assignment_labels_are_refused(motor):
    a, b = objects.piece_assignments(motor)[:2]
    a.Label, b.Label = "Coil 01", "Coil_01"
    assert _has(motor, "group names are the same")


def test_job_has_cell_bodies_and_symmetric_block(motor):
    with open(jobwriter.write_job(motor), encoding="utf-8") as fh:
        job = json.load(fh)
    assert [b["mat_id"] for b in job["bodies"]] == [1, 2, 3, 4, 5, 6]
    fixed, moving = job["symmetric"]["sides"]
    assert (fixed["side"], moving["side"]) == ("fixed", "moving")
    assert (len(fixed["transforms"]), len(moving["transforms"])) == (24, 16)
    assert all(len(t) == 16 for t in fixed["transforms"])
    pieces = fixed["pieces"] + moving["pieces"]
    assert len(pieces) == 120
    folder = os.path.dirname(jobwriter.write_job(motor))
    assert all(os.path.exists(os.path.join(folder, p["file"])) for p in pieces)
    assert {p["mat_id"] for p in pieces} == {int(motor.MatIds[m.Name]) for m in objects.piece_assignments(motor)}
    assert len({p["mat_id"] for p in pieces}) == 18
    slide = job["symmetric"]["slide"]
    assert slide["divisions"] == 144 and slide["radius"] == 35 and slide["full"]
    assert slide["slide_mat_id"] == int(motor.MatIds[objects.sliding_interfaces(motor)[0].Name])
    assert not {"air", "slides", "moving", "periodic"} & set(job)
