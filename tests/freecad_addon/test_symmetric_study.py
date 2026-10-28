"""Symmetric Mesh item, Materials on pieces and their MAT_IDs.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py"""

import json
import math
import os
import subprocess
import sys

import pytest

import FreeCAD as App

from emsolution import jobwriter, objects

from . import meshreport, symcases
from .materialdata import STEEL, record
from .test_meshsym import mesh_check


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
    assert [r[0] for r in rows] == objects.piece_assignments(motor)
    assert all(r[2][1] == "Steel" and r[2][3] == "0" for r in rows)


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


def _same(a, b):
    return (a.CenterOfMass - b.CenterOfMass).Length < 1e-6 and abs(a.Mass - b.Mass) < 1e-6


def _named(shape, kind, wanted):
    """The name ("Edge3") of a sub-element of shape whose geometry equals wanted. Fragments keeps a separate
    copy of an edge on each side of a seam, so there may be two; either is what a click picks."""
    items = shape.Edges if kind == "Edge" else shape.Faces
    return f"{kind}{next(k for k, e in enumerate(items) if _same(e, wanted)) + 1}"


def test_picks_on_the_top_point_at_the_cell(motor):
    top, coil = motor.MainObjects[0], motor.Document.getObject("CoilCell")
    edge = coil.Shape.Edge1
    on_top = _named(top.Shape, "Edge", edge)  # the same edge, picked on the Fragments in the cell's place
    face = coil.Shape.Face1.copy()
    face.rotate(App.Vector(), App.Vector(0, 0, 1), 90)  # the coil's copy in the 90..105° pitch
    copy = _named(top.Shape, "Face", face)
    other = motor.Document.getObject("RotorIronCell")
    wall = objects.to_cells(motor, [(top, on_top)])  # the slot wall is an edge of both CoilCell and StatorIronCell
    assert {b.Name for b, _ in wall} == {"CoilCell", "StatorIronCell"}
    assert all(_same(b.Shape.getElement(s), edge) for b, s in wall)
    mapped = objects.to_cells(motor, [(top, copy), (other, "Edge1"), (top, "")])
    assert mapped == [(coil, "Face1"), (other, "Edge1"), (top, "")]  # not on a top, or a whole top: left alone
    assert objects.to_cells(motor, [(top, copy)], whole=True) == [(coil, "")]


def test_structured_cell_from_edges_picked_on_the_top(motor):
    """Edges a cell shares with another cell are picked on the Fragments: the structured cell still counts them."""
    top, coil = motor.MainObjects[0], motor.Document.getObject("CoilCell")
    picks = [(top, _named(top.Shape, "Edge", e)) for e in coil.Shape.Edges]
    objects.make_transfinite_body(motor, [coil])
    objects.make_transfinite_edges(motor, 6, objects.to_cells(motor, picks))
    motor.Document.recompute()
    assert not _has(motor, "has edges without"), _texts(motor)
    # The mesher takes a curve set on two bodies' edges once; a transfinite face that falls back is an error there.
    path = jobwriter.write_job(motor)
    mesher = os.path.join(os.path.dirname(jobwriter.__file__), "mesher2d.py")
    r = subprocess.run([sys.executable, mesher, path], capture_output=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stderr


def test_face_picks_on_a_cell_carry_its_local_id(motor):
    """Transfinite Body and Recombine on a face of a cell body: their job entries have the cell's local id, the one
    of its body entry; the cells have no MAT_ID of their own."""
    top, coil = motor.MainObjects[0], motor.Document.getObject("CoilCell")
    picks = [(top, _named(top.Shape, "Edge", e)) for e in coil.Shape.Edges]
    objects.make_transfinite_body(motor, []).References = [(coil, "Face1")]
    objects.make_transfinite_edges(motor, 6, objects.to_cells(motor, picks))
    objects.make_recombine(motor, []).References = [(coil, "Face1")]
    motor.Document.recompute()
    path = jobwriter.write_job(motor)
    with open(path, encoding="utf-8") as fh:
        job = json.load(fh)
    local = next(b["mat_id"] for b in job["bodies"] if b["name"] == objects.volume_name(coil))
    (entry,) = job["transfinite"]["bodies"]
    assert entry["mat_id"] == local and [f["face"] for f in entry["faces"]] == ["Face1"]
    (face,) = job["recombine_faces"]
    assert face["mat_id"] == local and "recombine" not in job
    mesher = os.path.join(os.path.dirname(jobwriter.__file__), "mesher2d.py")
    r = subprocess.run([sys.executable, mesher, path], capture_output=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stderr
    kinds, inverted, _ = mesh_check(job["mesh_file"], (35,))
    assert inverted == 0 and any(k.startswith("Quadrilateral") for k in kinds), kinds


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


def test_every_item_type_has_its_tree_icon(motor):
    from emsolution import icon

    for item in objects.symmetric_items(motor) + objects.piece_assignments(motor)[:1]:
        assert os.path.exists(icon(type(item.Proxy).__name__.lower()))


def test_empty_compound_in_the_chain_is_an_error_not_a_crash(motor):
    stator, _ = objects.symmetric_items(motor)
    motor.Document.getObject("StatorPitch").Links = []
    found = [p for p in _problems(motor, "error") if "StatorPitch" in p.text]
    assert found and found[0].item == stator


def test_two_transfinite_bodies_on_one_cell_body_are_refused(motor):
    cell = next(b for b in objects.cell_bodies(motor) if b.Name == "CoilCell")
    objects.make_transfinite_body(motor, [cell])
    objects.make_transfinite_body(motor, [cell])
    assert _has(motor, "CoilCell", "is in Transfinite Body")


def test_two_sliding_interfaces_are_refused(motor):
    objects.make_sliding_interface(motor, "Rotational", Radius=35, Divisions=144)
    assert _has(motor, "only one Sliding Interface")


def test_swapped_pieces_warn(motor):
    coil1, coil2 = [m for m in objects.piece_assignments(motor) if m.Label in ("Coil01", "Coil02")]
    coil1.Pieces, coil2.Pieces = list(coil2.Pieces), list(coil1.Pieces)
    texts = _texts(motor, "warning")
    moved = [t for t in texts if "has moved: reassign it" in t]
    assert any("of Coil01" in t for t in moved) and any("of Coil02" in t for t in moved)
    assert all("StatorFragments.Face" in t for t in moved)
    assert _texts(motor) == []


def test_piece_centres_are_kept_on_reload(motor, tmp_path):
    coil = next(m for m in objects.piece_assignments(motor) if m.Label == "Coil01")
    assert len(coil.PieceCentres) == 2
    path = str(tmp_path / "t.FCStd")
    motor.Document.saveAs(path)
    App.closeDocument(motor.Document.Name)
    study = objects.find_study(App.openDocument(path))
    coil = next(m for m in objects.piece_assignments(study) if m.Label == "Coil01")
    assert len(coil.PieceCentres) == 2
    assert _problems(study) == []


def test_pieces_without_a_symmetric_mesh_warn(motor):
    for item in objects.symmetric_items(motor):
        motor.Document.removeObject(item.Name)
    assert _has(motor, "has pieces but the Study has no Symmetric Mesh", severity="warning")


def test_tops_are_not_listed_without_material(motor):
    assert objects.bodies_without_material(motor) == []


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
    assert job["rotor_file"] == jobwriter.rotor_file(motor)


def test_symmetric_job_meshes_into_both_files(motor):
    path = jobwriter.write_job(motor)
    with open(path, encoding="utf-8") as fh:
        job = json.load(fh)
    mesher = os.path.join(os.path.dirname(jobwriter.__file__), "mesher2d.py")
    r = subprocess.run([sys.executable, mesher, path, "--check"], capture_output=True, encoding="utf-8")
    assert r.returncode == 0 and "CHECK OK" in r.stdout, r.stderr
    r = subprocess.run([sys.executable, mesher, path], capture_output=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stderr
    ids = {p["mat_id"] for s in job["symmetric"]["sides"] for p in s["pieces"]}
    assert set(meshreport.groups(job["mesh_file"])) | set(meshreport.groups(job["rotor_file"])) == ids
    assert meshreport._point(job["rotor_file"]) is not None

    def on_slide(p):
        return abs(math.hypot(p[0], p[1]) - 35) < 1e-6

    assert meshreport.slide_check(job["mesh_file"], job["rotor_file"], on_slide) == (144, 144, True)

    label = {int(motor.MatIds[m.Name]): m.Label for m in objects.piece_assignments(motor)}
    for side, msh in zip(job["symmetric"]["sides"], (job["mesh_file"], job["rotor_file"])):
        found = meshreport.groups(msh)
        assert {name for name, _ in found.values()} == {label[p["mat_id"]] for p in side["pieces"]}
        assert all(count > 0 for _, count in found.values())
    fixed_names = {name for name, _ in meshreport.groups(job["mesh_file"]).values()}
    assert fixed_names == {"StatorIron", "StatorAir"} | {f"Coil{i:02d}" for i in range(1, 13)}
    assert sum(line.startswith("MAT_ID") for line in r.stdout.splitlines()) == 18
    for msh in (job["mesh_file"], job["rotor_file"]):
        assert mesh_check(msh, (35,))[1] == 0
    marker = job["symmetric"]["slide"]["slide_mat_id"]
    assert meshreport._point(job["rotor_file"], marker) is not None
    assert meshreport._point(job["mesh_file"], marker) is None


def test_static_study_writes_one_file(tmp_path):
    doc = App.newDocument("SymStatic")
    try:
        info = symcases.motor_doc(doc)
        study = objects.make_study(doc, "2D")
        study.MainMode, study.MainObjects = "Manual", [info["stator_top"]]
        study.Movement = "No movement"
        objects.make_symmetric_mesh(study, info["stator_top"])
        lib = objects.make_library_material(study, json.dumps(record("user:steel", "Steel", "electrical_steel", STEEL)))
        objects.assign_pieces(
            study,
            "Stator",
            [(info["stator_top"], f"Face{i + 1}") for i in range(len(info["stator_top"].Shape.Faces))],
            lib,
            0,
        )
        doc.recompute()
        doc.saveAs(str(tmp_path / "s.FCStd"))
        path = jobwriter.write_job(study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        assert "rotor_file" not in job and len(job["symmetric"]["sides"]) == 1
        assert "slide" not in job["symmetric"]
        mesher = os.path.join(os.path.dirname(jobwriter.__file__), "mesher2d.py")
        r = subprocess.run([sys.executable, mesher, path], capture_output=True, encoding="utf-8", errors="replace")
        assert r.returncode == 0, r.stderr
        assert os.path.exists(job["mesh_file"])
        found = meshreport.groups(job["mesh_file"])
        assert {name for name, _ in found.values()} == {"Stator"} and all(c > 0 for _, c in found.values())
        assert meshreport._marker(job["mesh_file"], 0) is None
    finally:
        for name in list(App.listDocuments()):
            App.closeDocument(name)
