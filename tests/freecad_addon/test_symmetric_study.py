"""The motor as two Symmetric Groups in a 2D Study: parts and their MAT_IDs, picks on the drawing, validation, the job.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py"""

import json
import math
import os
import subprocess
import sys

import pytest

import FreeCAD as App
import Part

from emsolution import icon, jobwriter, objects

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


def _part(study, name):
    return next(m for m in objects.part_assignments(study) if m.GroupName == name)


def _drawing(study):
    """The stator's group, whose drawing is the full stator."""
    return objects.symmetric_groups(study)[0]


def test_groups_hold_cells_and_copies(motor):
    stator, rotor = objects.symmetric_groups(motor)
    assert len(stator.Cells) == 3 and len(objects.group_transforms(stator)) == 24
    assert len(rotor.Cells) == 3 and len(objects.group_transforms(rotor)) == 16
    assert objects.is_grouped(motor)
    assert len(objects.cell_bodies(motor)) == 6
    assert objects._size_text(stator) == "symmetric group"


def test_part_assignment_gets_one_mat_id_keyed_by_itself(motor):
    objects.update_ids(motor)
    parts = objects.part_assignments(motor)
    names = {m.Name for m in parts}
    (iface,) = objects.sliding_interfaces(motor)
    assert len(names) == 18
    assert set(motor.MatIds) == names | {iface.Name}
    assert len(set(motor.MatIds.values())) == 19
    assert [m.GroupName for m in parts].count("Coil01") == 1
    rows = objects.material_rows(motor)
    assert [r[0] for r in rows] == parts
    assert {r[2][2] for r in rows} == {motor.MatIds[n] for n in names}
    assert all(r[2][1] == "Steel" and r[2][3] == "0" for r in rows)
    assert [r[2][0] for r in rows] == [m.GroupName for m in parts]


def test_part_assignment_label_shows_name_and_material(motor):
    (lib,) = objects.library_materials(motor)
    lib.Label = "Renamed"
    objects.sync_labels(motor)
    coil = _part(motor, "Coil01")
    assert coil.Label == "Coil01: Renamed"
    assert len(objects.item_refs(coil)) == 2  # the coil and its mirrored copy in the first slot


def test_suggest_name_for_faces(motor):
    (lib,) = objects.library_materials(motor)
    stator = _drawing(motor)
    name = objects.suggest_name(motor, [(stator, "Face1")], lib)
    assert name.startswith("Steel") and not objects.name_taken(motor, name)
    assert objects.suggest_name(motor, [(stator, "Face1")], None).startswith(objects.display_name(stator))


def test_mesh_size_on_a_cell_body_is_allowed(motor):
    cell = next(b for b in objects.cell_bodies(motor) if b.Name == "CoilCell")
    assert objects.assignment_problem(motor, [cell]) == ""


def test_save_reload_keeps_parts_and_groups(motor, tmp_path):
    objects.update_ids(motor)
    ids = dict(motor.MatIds)
    rules = [objects.rules_of(g) for g in objects.symmetric_groups(motor)]
    doc = motor.Document
    path = os.path.join(str(tmp_path), "t.FCStd")
    doc.saveAs(path)
    App.closeDocument(doc.Name)
    doc = App.openDocument(path)
    study = objects.find_study(doc)
    assert len(objects.part_assignments(study)) == 18
    coil = _part(study, "Coil01")
    assert coil.PartKey == "Coil01" and coil.Body is None and len(objects.item_refs(coil)) == 2
    assert [objects.rules_of(g) for g in objects.symmetric_groups(study)] == rules
    assert dict(study.MatIds) == ids


def _same(a, b):
    return (a.CenterOfMass - b.CenterOfMass).Length < 1e-6 and abs(a.Mass - b.Mass) < 1e-6


def _named(shape, kind, wanted):
    """The name ("Edge3") of a sub-element of shape whose geometry equals wanted. The drawing keeps a separate copy of
    an edge on each side of a wall, so there may be two; either is what a click picks."""
    items = shape.Edges if kind == "Edge" else shape.Faces
    return f"{kind}{next(k for k, e in enumerate(items) if _same(e, wanted)) + 1}"


def test_picks_on_the_drawing_point_at_the_cell(motor):
    top, coil = _drawing(motor), motor.Document.getObject("CoilCell")
    edge = coil.Shape.Edge1
    on_top = _named(top.Shape, "Edge", edge)  # the same edge, picked on the drawing in the cell's place
    face = coil.Shape.Face1.copy()
    face.rotate(App.Vector(), App.Vector(0, 0, 1), 90)  # the coil's copy in the 90..105° pitch
    copy = _named(top.Shape, "Face", face)
    other = motor.Document.getObject("RotorIronCell")
    wall = objects.to_cells(motor, [(top, on_top)])  # the slot wall is an edge of both CoilCell and StatorIronCell
    assert {b.Name for b, _ in wall} == {"CoilCell", "StatorIronCell"}
    assert all(_same(b.Shape.getElement(s), edge) for b, s in wall)
    mapped = objects.to_cells(motor, [(top, copy), (other, "Edge1"), (top, "")])
    assert mapped == [(coil, "Face1"), (other, "Edge1"), (top, "")]  # not on a drawing, or a whole one: left alone
    assert objects.to_cells(motor, [(top, copy)], whole=True) == [(coil, "")]


def _mesh(path, three=False):
    mesher = os.path.join(os.path.dirname(jobwriter.__file__), "mesher.py" if three else "mesher2d.py")
    return subprocess.run([sys.executable, mesher, path], capture_output=True, encoding="utf-8", errors="replace")


def test_structured_cell_from_edges_picked_on_the_drawing(motor):
    """Edges a cell shares with another cell are picked on the drawing: the structured cell still counts them."""
    top, coil = _drawing(motor), motor.Document.getObject("CoilCell")
    picks = [(top, _named(top.Shape, "Edge", e)) for e in coil.Shape.Edges]
    objects.make_transfinite_body(motor, [coil])
    objects.make_transfinite_edges(motor, 6, objects.to_cells(motor, picks))
    motor.Document.recompute()
    assert not _has(motor, "has edges without"), _texts(motor)
    # The mesher takes a curve set on two bodies' edges once; a transfinite face that falls back is an error there.
    r = _mesh(jobwriter.write_job(motor))
    assert r.returncode == 0, r.stderr


def test_face_picks_on_a_cell_carry_its_local_id(motor):
    """Transfinite Body and Recombine on a face of a cell object: their entries in the group's job have the cell's
    local id, the one of its body entry; the cells have no MAT_ID of their own."""
    top, coil = _drawing(motor), motor.Document.getObject("CoilCell")
    picks = [(top, _named(top.Shape, "Edge", e)) for e in coil.Shape.Edges]
    objects.make_transfinite_body(motor, []).References = [(coil, "Face1")]
    objects.make_transfinite_edges(motor, 6, objects.to_cells(motor, picks))
    objects.make_recombine(motor, []).References = [(coil, "Face1")]
    motor.Document.recompute()
    path = jobwriter.write_job(motor)
    with open(path, encoding="utf-8") as fh:
        job = json.load(fh)
    cell_job = job["symmetric"]["groups"][0]["job"]
    local = next(b["mat_id"] for b in cell_job["bodies"] if b["name"] == objects.volume_name(coil))
    (entry,) = cell_job["transfinite"]["bodies"]
    assert entry["mat_id"] == local and [f["face"] for f in entry["faces"]] == ["Face1"]
    (face,) = cell_job["recombine_faces"]
    assert face["mat_id"] == local and "recombine" not in cell_job
    r = _mesh(path)
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


def _cell(study, name="CoilCell"):
    return next(b for b in objects.cell_bodies(study) if b.Name == name)


def _free_ring(study):
    """A free body on the fixed side, outside the stator."""
    ring = Part.Face(Part.Wire(Part.makeCircle(110))).cut(Part.Face(Part.Wire(Part.makeCircle(100))))
    return symcases.add_free(study, "FreeRing", ring, symcases.libraries(study)["Steel"])


def _job_of(study):
    with open(jobwriter.write_job(study), encoding="utf-8") as fh:
        return json.load(fh)


def _refine_keys(job):
    sym = job["symmetric"]
    return [g["job"].get("refine") for g in sym["groups"]], [f["job"].get("refine") for f in sym.get("free", [])]


def test_air_grading_on_a_free_object_is_allowed_and_on_a_cell_refused(motor):
    body = _free_ring(motor)
    objects.make_air_grading(motor, [(body, "")], 5.0)
    assert not [t for t in _texts(motor) if t.startswith("Air Grading")]
    cell = _cell(motor)
    item = objects.make_air_grading(motor, [(cell, "")], 5.0)
    assert (
        f"Air Grading {item.Label}: {objects.display_name(cell)} is not an air. Pick the Air Region (or, in a Study"
        " with Symmetric Groups, a free object that is air)." in _texts(motor)
    )


def test_skin_layer_quads_on_a_free_object_warns(motor):
    body = _free_ring(motor)
    item = objects.make_skin_layer(motor, [(body, "")])
    item.QuadLayers = True
    assert [t for t in _texts(motor, "warning") if t.startswith(f"Skin Layer {item.Label}")] == [
        f"Skin Layer {item.Label}: quad layers are not made on free objects of a Study with Symmetric Groups;"
        f" {objects.display_name(body)} gets graded triangles."
    ]


def test_skin_layer_quads_on_a_cell_cut_by_a_seam_not(tmp_path):
    """A half wire on the mirror seam, in an iron cell: its edge on the seam is a cut to the cell job, not a surface, so
    the 90 degree corners where the seam meets the arc are not sharp corners of the layer."""
    doc = App.newDocument("SeamSkin")
    try:
        study = objects.make_study(doc, "2D")
        half = Part.Face(
            Part.Wire(
                [
                    Part.makeCircle(5, App.Vector(20, 0, 0), App.Vector(0, 0, 1), 0, 180),
                    Part.makeLine((15, 0, 0), (25, 0, 0)),
                ]
            )
        )
        wire = symcases.feature(doc, "WireCell", half)
        iron = symcases.feature(doc, "IronCell", symcases.sector(10, 30, 0, 30).cut(half).Faces[0])
        symcases.group(study, "G", [iron, wire], [symcases.mirror_rule(0), symcases.rotate_rule(60, 6)])
        symcases.add_air_region(study, Center=App.Vector(), Length=100, Width=100)
        item = objects.make_skin_layer(study, [(wire, "")])
        item.QuadLayers = True
        assert not [t for t in _texts(study, "warning") if t.startswith(f"Skin Layer {item.Label}")]
    finally:
        App.closeDocument(doc.Name)


@pytest.fixture
def bar_study(tmp_path):
    """A 2D group (mirror at 0 degrees, six turns of 60) whose cell is iron r 10..30 over 0..30 degrees holding a bar
    r 25..30 over 0..10 degrees (its arc r 30 faces the Air Region, its line at 0 degrees is a seam with its mirror
    image, its other edges lie against the iron) and a round wire r 2 inside the iron, in a 100 mm Air Region box.
    Yields (study, bar, wire)."""
    doc = App.newDocument("BarSkin")
    try:
        study = objects.make_study(doc, "2D")
        libs = symcases.libraries(study)
        bar_face = symcases.sector(25, 30, 0, 10)
        centre = App.Vector(18 * math.cos(math.radians(15)), 18 * math.sin(math.radians(15)), 0)
        wire_face = Part.Face(Part.Wire(Part.makeCircle(2, centre)))
        bar = symcases.feature(doc, "BarCell", bar_face)
        wire = symcases.feature(doc, "WireCell", wire_face)
        iron = symcases.feature(doc, "IronCell", symcases.sector(10, 30, 0, 30).cut(bar_face).cut(wire_face).Faces[0])
        lib = {iron.Name: libs["Steel"], bar.Name: libs["Copper"], wire.Name: libs["Copper"]}
        rows = {c.Name: {"mode": "table", "table": [c.Name[:-4]] * 12} for c in (iron, bar, wire)}
        rules = [symcases.mirror_rule(0), symcases.rotate_rule(60, 6)]
        symcases.group(study, "G", [iron, bar, wire], rules, rows=rows, lib=lib)
        symcases.add_air_region(study, libs["Air"], Center=App.Vector(), Length=100, Width=100)
        symcases.finish(study, str(tmp_path / "bar.FCStd"))
        yield study, bar, wire
    finally:
        for name in list(App.listDocuments()):
            App.closeDocument(name)


def _arc_radius(shape):
    (edge,) = shape.Edges
    return getattr(edge.Curve, "Radius", None)


def test_free_faces_of_a_cell_conductor(bar_study):
    from emsolution import geometry, validation

    study, bar, wire = bar_study
    (group,) = objects.symmetric_groups(study)
    edges = geometry.global_shape(bar).Edges
    (outer,) = [f"Edge{i}" for i, e in enumerate(edges, 1) if getattr(e.Curve, "Radius", 0) == pytest.approx(30)]
    assert validation.free_faces(study, group, bar) == [outer]
    assert validation.free_faces(study, group, wire) == []
    (air,) = objects.air_regions(study)
    air.AirShape, air.InnerRadius, air.OuterRadius = "Sector", 30, 60  # round the copies: its inner arc meets the bar
    study.Document.recompute()
    assert validation.free_faces(study, group, bar) == [outer]
    # a half model: three turns of the cell and its mirror image at 30 degrees, in a box above y = 0. The bar's line at
    # 0 degrees lies on the box's side, a cut of the domain
    objects.set_rules(group, [symcases.mirror_rule(30), symcases.rotate_rule(60, 3)])
    air.AirShape, air.Center, air.Length, air.Width = "Box", App.Vector(0, 50, 0), 200, 100
    study.Document.recompute()
    assert validation.free_faces(study, group, bar) == [outer]
    air.Center = App.Vector(0, 49, 0)  # the box reaches 1 mm below y = 0: that line now faces its air
    study.Document.recompute()
    line = next(f"Edge{i}" for i, e in enumerate(edges, 1) if abs(e.CenterOfMass.y) < 1e-9)
    assert validation.free_faces(study, group, bar) == sorted([outer, line], key=lambda n: int(n[4:]))


def test_skin_on_a_cell_conductor_lists_its_free_faces(bar_study):
    study, bar, wire = bar_study
    objects.make_skin_layer(study, [(bar, "")], 1.0)
    objects.make_skin_layer(study, [(wire, "")], 1.0)
    assert not _texts(study)
    path = jobwriter.write_job(study)
    with open(path, encoding="utf-8") as fh:
        job = json.load(fh)
    (group,) = objects.symmetric_groups(study)
    on_bar, on_wire = job["symmetric"]["groups"][0]["job"]["skin"]
    n = list(group.Cells).index(bar) + 1
    (face,) = on_bar["faces"]
    assert face["mat_id"] == n and on_bar["mat_ids"] == [n]
    assert _arc_radius(Part.read(os.path.join(os.path.dirname(path), face["file"]))) == pytest.approx(30)
    assert "faces" not in on_wire


def test_refine_near_whole_cell_body_gets_its_free_faces(bar_study):
    study, bar, _ = bar_study
    objects.make_refine_near(study, [(bar, "")])
    path = jobwriter.write_job(study)
    with open(path, encoding="utf-8") as fh:
        job = json.load(fh)
    (group,) = objects.symmetric_groups(study)
    (entry,) = job["symmetric"]["groups"][0]["job"]["refine"]
    assert entry["whole"] == [list(group.Cells).index(bar) + 1]
    (file,) = entry["files"]
    assert _arc_radius(Part.read(os.path.join(os.path.dirname(path), file))) == pytest.approx(30)


def test_skin_layer_quads_on_a_cell_conductor_facing_the_air(tmp_path):
    """A lens-shaped bar at the iron's outer arc: its arc against the iron is smooth on its own, but where its free arc
    r 30 meets it the surface turns sharply, so Validate warns as the mesher would find it."""
    doc = App.newDocument("LensSkin")
    try:
        study = objects.make_study(doc, "2D")
        centre = App.Vector(30 * math.cos(math.radians(15)), 30 * math.sin(math.radians(15)), 0)
        sector = symcases.sector(10, 30, 0, 30)
        disk = Part.Face(Part.Wire(Part.makeCircle(4, centre)))
        lens = symcases.feature(doc, "LensCell", sector.common(disk).Faces[0])
        iron = symcases.feature(doc, "IronCell", sector.cut(disk).Faces[0])
        symcases.group(study, "G", [iron, lens], [symcases.mirror_rule(0), symcases.rotate_rule(60, 6)])
        symcases.add_air_region(study, Center=App.Vector(), Length=100, Width=100)
        item = objects.make_skin_layer(study, [(lens, "")], 0.5)
        item.QuadLayers = True
        assert [t for t in _texts(study, "warning") if t.startswith(f"Skin Layer {item.Label}")] == [
            f"Skin Layer {item.Label}: {objects.display_name(lens)} has sharp corners on its surface; quad layers need"
            " a smooth surface, so it gets graded triangles."
        ]
    finally:
        App.closeDocument(doc.Name)


def test_air_grading_goes_to_the_free_job_of_its_air(motor):
    air = symcases.add_air_region(
        motor, symcases.libraries(motor)["Air"], AirShape="Sector", InnerRadius=60, OuterRadius=130
    )
    body = _free_ring(motor)
    objects.make_air_grading(motor, [(air, "")], 7.0, 3.0)
    objects.make_air_grading(motor, [(body, "")], 9.0, 4.0)
    assert not [t for t in _texts(motor) if t.startswith("Air Grading")]
    job = _job_of(motor)
    assert not any(g["job"].get("air_grading") for g in job["symmetric"]["groups"])
    (free,) = [f["job"] for f in job["symmetric"]["free"] if f["side"] == "fixed"]
    ids = motor.MatIds
    assert free["air_grading"] == [
        {"name": "AirGrading", "mat_ids": [int(ids[air.Name])], "growth": 7.0, "far": 3.0},
        {"name": "AirGrading001", "mat_ids": [int(ids[body.Name])], "growth": 9.0, "far": 4.0},
    ]


def test_refine_near_on_a_cell_goes_to_the_cell_job(motor):
    cell = _cell(motor)
    objects.make_refine_near(motor, [(cell, "")])
    assert not _texts(motor)
    job = _job_of(motor)
    cells, free = _refine_keys(job)
    group = objects.symmetric_groups(motor)[0]
    assert cells[0][0]["whole"] == [list(group.Cells).index(cell) + 1]
    assert cells[1] is None and not any(free)


def test_refine_near_on_a_free_body_goes_to_the_free_job(motor):
    body = _free_ring(motor)
    objects.make_refine_near(motor, [(body, "Edge1")])
    assert not _texts(motor)
    cells, free = _refine_keys(_job_of(motor))
    assert not any(cells)
    (entry,) = free[0]
    assert len(entry["files"]) == 1 and entry["files"][0].startswith("geometry/free_fixed_refine_")


def test_skin_goes_to_the_cell_job(motor):
    cell = _cell(motor)
    objects.make_skin_layer(motor, [(cell, "")], 2.0)
    job = _job_of(motor)
    group = objects.symmetric_groups(motor)[0]
    skins = [g["job"].get("skin") for g in job["symmetric"]["groups"]]
    n = list(group.Cells).index(cell) + 1
    assert skins[0] == [
        {"name": "SkinLayer", "mat_ids": [n], "depth": 2.0, "per_depth": 2.0, "layer": 3.0, "quads": False}
    ]
    assert skins[1] is None and not any(f["job"].get("skin") for f in job["symmetric"].get("free", []))


def test_skin_on_a_free_object_has_no_quads(motor):
    body = _free_ring(motor)
    item = objects.make_skin_layer(motor, [(body, "")], 2.0)
    item.QuadLayers = True
    job = _job_of(motor)
    assert not any(g["job"].get("skin") for g in job["symmetric"]["groups"])
    (free,) = [f["job"] for f in job["symmetric"]["free"] if f["side"] == "fixed"]
    mat_id = int(motor.MatIds[body.Name])
    assert free["skin"] == [
        {"name": "SkinLayer", "mat_ids": [mat_id], "depth": 2.0, "per_depth": 2.0, "layer": 3.0, "quads": False}
    ]


def test_refine_near_on_a_cell_and_a_free_body_goes_to_both_jobs(motor):
    body = _free_ring(motor)
    objects.make_refine_near(motor, [(_cell(motor), "Edge1"), (body, "Edge1")])
    cells, free = _refine_keys(_job_of(motor))
    assert len(cells[0]) == 1 and cells[1] is None and len(free[0]) == 1
    files = cells[0][0]["files"] + free[0][0]["files"]
    assert files and len(set(files)) == len(files)


def test_refine_near_limit_to_across_parts_warns(motor):
    air = symcases.add_air_region(
        motor, symcases.libraries(motor)["Air"], AirShape="Sector", InnerRadius=60, OuterRadius=90
    )
    item = objects.make_refine_near(motor, [(_cell(motor), "Edge1")], limit_to=[air])
    assert not _texts(motor)
    assert (
        f"Refine Near {item.Label}: no body in Limit to is meshed with its picks; the refinement is skipped."
        in _texts(motor, "warning")
    )
    cells, free = _refine_keys(_job_of(motor))
    assert not any(cells) and not any(free)


def test_refine_near_limit_to_partly_across_parts_warns(motor):
    cell = _cell(motor)
    air = symcases.add_air_region(
        motor, symcases.libraries(motor)["Air"], AirShape="Sector", InnerRadius=60, OuterRadius=90
    )
    item = objects.make_refine_near(motor, [(cell, "Edge1")], limit_to=[cell, air])
    assert (
        f"Refine Near {item.Label}: {objects.display_name(air)} in Limit to is meshed apart from its picks (a Symmetric"
        " Group's cell objects are meshed on their own); it has no effect there."
    ) in _texts(motor, "warning")
    cells, _ = _refine_keys(_job_of(motor))
    assert cells[0][0]["limit_to"] == [list(objects.symmetric_groups(motor)[0].Cells).index(cell) + 1]


def _sector_air(study):
    return symcases.add_air_region(
        study, symcases.libraries(study)["Air"], AirShape="Sector", InnerRadius=60, OuterRadius=90
    )


def _air_edge(air, radius):
    """The name of the Air Region's arc at radius (its shape as the mesh gets it)."""
    shape = jobwriter.meshed_shape(air)
    return next(
        f"Edge{i}"
        for i, e in enumerate(shape.Edges, 1)
        if hasattr(e.Curve, "Radius") and e.Curve.Radius == pytest.approx(radius)
    )


def test_refine_near_whole_free_body_warns_about_the_copies(motor):
    air = _sector_air(motor)
    item = objects.make_refine_near(motor, [(air, "")])
    assert (
        f"Refine Near {item.Label}: in a Study with Symmetric Groups, {objects.display_name(air)} is refined only where"
        " it meets other free objects, not where it meets the copies of a Symmetric Group."
    ) in _texts(motor, "warning")


def test_refine_near_on_the_copies_warns(motor):
    air = _sector_air(motor)
    inner, outer = _air_edge(air, 60), _air_edge(air, 90)
    item = objects.make_refine_near(motor, [(air, inner)])
    text = (
        f"Refine Near {item.Label}: {inner} of {objects.display_name(air)} lies on the copies of a Symmetric Group,"
        " which are meshed apart; it is not refined there."
    )
    assert text in _texts(motor, "warning")
    item.References = [(air, outer)]  # the outer arc meets no copy
    assert not [t for t in _texts(motor, "warning") if t.startswith(f"Refine Near {item.Label}")]


def test_refine_near_on_a_broken_air_region_leaves_it_to_its_error(motor):
    air = _sector_air(motor)
    objects.make_refine_near(motor, [(air, _air_edge(air, 60))])
    air.AirShape = "Custom"  # and no Source: air_shape raises
    motor.Document.recompute()
    assert _has(motor, "choose a body for the Custom shape")


def test_refine_near_pick_apart_from_every_limit_to_warns(motor):
    body, cell = _free_ring(motor), _cell(motor)
    item = objects.make_refine_near(motor, [(cell, "Edge1"), (body, "Edge1")], limit_to=[cell])
    assert (
        f"Refine Near {item.Label}: {objects.display_name(body)} is meshed apart from every body in Limit to; it has"
        " no effect there."
    ) in _texts(motor, "warning")
    _, free = _refine_keys(_job_of(motor))
    assert not any(free)  # the free job leaves the entry out


def _texts(study, severity="error"):
    return [p.text for p in _problems(study, severity)]


def _has(study, *words, severity="error"):
    return any(all(w in t for w in words) for t in _texts(study, severity))


def test_motor_study_validates_clean(motor):
    assert [(p.severity, p.text) for p in _problems(motor)] == []


def test_air_region_is_refused(motor):
    objects.make_air_region(motor)
    assert _has(motor, "Air Region")


def test_whole_body_assignment_on_a_drawing_is_refused(motor):
    (m,) = objects.assign(motor, [_drawing(motor)], objects.library_materials(motor)[0], 0)
    found = [p for p in _problems(motor, "error") if "through its parts" in p.text]
    assert found and found[0].item == m


def test_whole_body_assignment_on_a_cell_body_warns(motor):
    cell = next(b for b in objects.cell_bodies(motor) if b.Name == "CoilCell")
    objects.assign(motor, [cell], objects.library_materials(motor)[0], 0)
    assert _has(motor, "not used", "parts", severity="warning")
    assert not [t for t in _texts(motor) if "CoilCell" in t]


def test_part_without_material_is_an_error(motor):
    _part(motor, "Coil01").LibraryMaterial = None
    assert _has(motor, "Parts with no Material", "Coil01")


def test_part_name_on_both_sides_is_refused(motor):
    rotor = objects.symmetric_groups(motor)[1]
    rows = objects.rows_of(rotor)
    rows[0]["table"] = ["Coil01"] * 16
    objects.set_rows(rotor, rows)
    objects.sync_parts(motor)
    assert _has(motor, "both sides", "Coil01")


@pytest.mark.parametrize("make", ["size", "recombine"])
def test_mesh_setting_on_a_drawing_is_refused(motor, make):
    top = _drawing(motor)
    if make == "size":
        objects.make_mesh_size(motor, 1.0, [(top, "Face1")])
    else:
        objects.make_recombine(motor, [top])
    assert _has(motor, "copies are not meshed")


def test_transfinite_on_a_drawing_is_refused(motor):
    objects.make_transfinite_edges(motor, 5, [(_drawing(motor), "Edge1")])
    assert _has(motor, "copies are not meshed")


def test_mesh_size_on_a_cell_body_is_fine(motor):
    cell = next(b for b in objects.cell_bodies(motor) if b.Name == "CoilCell")
    objects.make_mesh_size(motor, 1.0, [(cell, "")])
    assert _problems(motor) == []


def test_linear_interface_is_refused(motor):
    (iface,) = objects.sliding_interfaces(motor)
    iface.Kind = "Linear"
    assert _has(motor, "Rotational")


def test_divisions_must_fit_the_turns(motor):
    (iface,) = objects.sliding_interfaces(motor)
    iface.Divisions = 146  # the stator cell turns 12 times
    assert _has(motor, "divisions", "multiple of the 12 turns")


def test_changing_the_rotation_count_reports_the_tables(motor):
    stator = _drawing(motor)
    objects.set_rules(stator, [symcases.mirror_rule(15), symcases.rotate_rule(60, 6)])
    motor.Document.recompute()
    assert _has(motor, "has 24 names, the group makes 12 copies")


def test_deleted_cell_body_is_an_error(motor):
    stator = _drawing(motor)
    motor.Document.removeObject("CoilCell")
    motor.Document.recompute()
    assert [p for p in _problems(motor, "error") if p.item == stator]


def test_cell_body_without_a_face_is_refused(motor):
    """A sketch or line put in a group is not a cell object: Validate Study says so before the mesher reads it."""
    doc = motor.Document
    line = symcases.feature(doc, "StrayLine", Part.LineSegment(App.Vector(61, 0, 0), App.Vector(62, 0, 0)).toShape())
    stator = _drawing(motor)
    stator.Cells = [*stator.Cells, line]
    doc.recompute()
    found = [p for p in _problems(motor, "error") if p.item == stator and "has no face" in p.text]
    assert found and "StrayLine" in found[0].text and "Boolean Fragments" in found[0].text, _texts(motor)


def _overlap(study):
    stator = _drawing(study)
    return [p for p in _problems(study, "error") if p.item == stator and "overlaps" in p.text]


def test_cell_body_past_the_mirror_line_is_refused(motor):
    """The coil drawn 10..17 deg in the 0..15 deg cell overlaps its own mirrored copy. Validate Study names it, and
    where, before the mesher fails with only a point (examples/5_coil_past_mirror_line)."""
    doc = motor.Document
    coil = doc.getObject("CoilCell")
    coil.Shape = symcases.sector(37, 50, 10, 17)
    doc.getObject("StatorIronCell").Shape = symcases.sector(36, 60, 0, 15).cut(coil.Shape).Faces[0]
    doc.recompute()
    (found,) = _overlap(motor)
    assert "CoilCell overlaps a mirrored copy of CoilCell" in found.text, found.text
    r, a = _near(found.text)
    assert 13 < a < 17 and 37 < r < 50  # in the overlap, 13..17 deg
    assert (coil, "") in found.refs


def _near(text):
    """(radius, angle in deg) of the point "near (x, y)" in text."""
    x, y = (float(v) for v in text.split("near (")[1].split(")")[0].split(", "))
    return math.hypot(x, y), math.degrees(math.atan2(y, x))


def test_rotation_with_too_many_copies_is_refused(motor):
    """13 copies of the 30 deg slot pitch are 27.7 deg apart, so each overlaps the next (examples/6_thirteen_copies)."""
    objects.set_rules(_drawing(motor), [symcases.mirror_rule(15), symcases.rotate_rule(360 / 13, 13)])
    motor.Document.recompute()
    (found,) = _overlap(motor)
    assert "rotation's step and count" in found.text, found.text
    assert 0 < _near(found.text)[1] < 30 - 360 / 13  # where the last copy reaches over the first: 0..2.3 deg


def test_copies_that_only_touch_do_not_overlap(motor):
    assert not [p for p in _problems(motor, "error") if "overlaps" in p.text]


def _steel(study):
    return objects.make_library_material(study, json.dumps(record("user:steel", "Steel", "electrical_steel", STEEL)))


def test_cell_cut_by_a_fragments_meshes_per_block(tmp_path):
    """A Boolean Fragments cell object (the coil cut by an arc) has two blocks, a row each once split. Face picks
    structure and recombine one block only, and each block takes the Material of its part."""
    doc = App.newDocument("SymSplit")
    try:
        info = symcases.group_motor_doc(doc)
        frag = symcases.coil_fragments(doc)
        iron, _, air = info["stator_cells"]
        study = objects.make_study(doc, "2D")
        objects.set_excluded(study, info["rotor_cells"])  # only the stator is meshed
        stator = objects.make_symmetric_group(study, [iron, frag, air], rules=symcases.STATOR_RULES, name="Stator")
        assert objects.split_row(stator, 1)
        outer_area = symcases.sector(43, 50, 10, 15).Area
        block = next(f"Face{i}" for i, f in enumerate(frag.Shape.Faces, 1) if abs(f.Area - outer_area) < 1e-6)
        rows = []
        for row in objects.rows_of(stator):
            outer = row["cell"] == frag.Name and f"Face{row['solid'] + 1}" == block
            rows.append({**row, "mode": "table", "table": ["OuterCoil" if outer else "Stator"] * 24})
        objects.set_rows(stator, rows)
        lib = _steel(study)
        for r in range(len(rows)):
            objects.set_row_material(study, stator, r, lib)
        objects.sync_parts(study)
        own = frag.Shape.getElement(block).Edges
        edges = [(frag, f"Edge{i}") for i, e in enumerate(frag.Shape.Edges, 1) if any(e.isSame(g) for g in own)]
        assert len(edges) == 4
        objects.make_transfinite_body(study, []).References = [(frag, block)]
        objects.make_transfinite_edges(study, 4, edges)
        objects.make_recombine(study, []).References = [(frag, block)]
        doc.recompute()
        doc.saveAs(str(tmp_path / "split.FCStd"))
        path = jobwriter.write_job(study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        (entry,) = job["symmetric"]["groups"][0]["job"]["transfinite"]["bodies"]
        assert entry["name"] == objects.volume_name(frag) and [f["face"] for f in entry["faces"]] == [block]
        r = _mesh(path)
        assert r.returncode == 0, r.stderr
        found = meshreport.groups(job["mesh_file"])
        assert {name for name, _ in found.values()} == {"OuterCoil", "Stator"}
        kinds, inverted, loose = mesh_check(job["mesh_file"], (35, 60))
        assert inverted == 0 and loose == 0 and any(k.startswith("Quadrilateral") for k in kinds), (kinds, loose)
    finally:
        for name in list(App.listDocuments()):
            App.closeDocument(name)


def test_duplicate_part_names_are_refused(motor):
    a, b = objects.part_assignments(motor)[:2]
    a.GroupName, b.GroupName = "Coil 01", "Coil_01"
    assert _has(motor, "group names are the same")


def test_every_item_type_has_its_tree_icon(motor):
    for name in ("symmetricmesh", type(objects.part_assignments(motor)[0].Proxy).__name__.lower()):
        assert os.path.exists(icon(name))


def test_two_transfinite_bodies_on_one_cell_body_are_refused(motor):
    cell = next(b for b in objects.cell_bodies(motor) if b.Name == "CoilCell")
    objects.make_transfinite_body(motor, [cell])
    objects.make_transfinite_body(motor, [cell])
    assert _has(motor, "CoilCell", "is in Transfinite Body")


def test_two_sliding_interfaces_are_refused(motor):
    objects.make_sliding_interface(motor, "Rotational", Radius=35, Divisions=144)
    assert _has(motor, "only one Sliding Interface")


def test_groups_are_not_listed_without_material(motor):
    assert objects.bodies_without_material(motor) == []


def test_job_has_groups_and_their_parts(motor):
    path = jobwriter.write_job(motor)
    with open(path, encoding="utf-8") as fh:
        job = json.load(fh)
    stator, rotor = job["symmetric"]["groups"]
    assert (stator["side"], rotor["side"]) == ("fixed", "moving")
    assert (len(stator["transforms"]), len(rotor["transforms"])) == (24, 16)
    assert all(len(t) == 16 for t in stator["transforms"])
    assert [b["mat_id"] for g in (stator, rotor) for b in g["job"]["bodies"]] == [1, 2, 3, 1, 2, 3]
    folder = os.path.dirname(path)
    assert all(os.path.exists(os.path.join(folder, b["file"])) for g in (stator, rotor) for b in g["job"]["bodies"])
    parts = stator["parts"] + rotor["parts"]
    assert {p["mat_id"] for p in parts} == {int(motor.MatIds[m.Name]) for m in objects.part_assignments(motor)}
    assert len({p["mat_id"] for p in parts}) == 18
    assert all(len(row["parts"]) == len(g["transforms"]) for g in (stator, rotor) for row in g["rows"])
    slide = job["symmetric"]["slide"]
    assert slide["divisions"] == 144 and slide["radius"] == 35 and slide["full"]
    assert slide["slide_mat_id"] == int(motor.MatIds[objects.sliding_interfaces(motor)[0].Name])
    assert not {"air", "slides", "moving", "periodic", "bodies"} & set(job)
    assert job["rotor_file"] == jobwriter.rotor_file(motor)


def test_symmetric_job_meshes_into_both_files(motor):
    path = jobwriter.write_job(motor)
    with open(path, encoding="utf-8") as fh:
        job = json.load(fh)
    mesher = os.path.join(os.path.dirname(jobwriter.__file__), "mesher2d.py")
    r = subprocess.run([sys.executable, mesher, path, "--check"], capture_output=True, encoding="utf-8")
    assert r.returncode == 0 and "CHECK OK" in r.stdout, r.stderr
    r = _mesh(path)
    assert r.returncode == 0, r.stderr
    groups = job["symmetric"]["groups"]
    ids = {p["mat_id"] for g in groups for p in g["parts"]}
    assert set(meshreport.groups(job["mesh_file"])) | set(meshreport.groups(job["rotor_file"])) == ids
    assert meshreport._point(job["rotor_file"]) is not None

    def on_slide(p):
        return abs(math.hypot(p[0], p[1]) - 35) < 1e-6

    assert meshreport.slide_check(job["mesh_file"], job["rotor_file"], on_slide) == (144, 144, True)

    label = {int(motor.MatIds[m.Name]): m.GroupName for m in objects.part_assignments(motor)}
    for group, msh in zip(groups, (job["mesh_file"], job["rotor_file"])):
        found = meshreport.groups(msh)
        assert {name for name, _ in found.values()} == {label[p["mat_id"]] for p in group["parts"]}
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
        info = symcases.group_motor_doc(doc)
        study = objects.make_study(doc, "2D")
        objects.set_excluded(study, info["rotor_cells"])  # only the stator is meshed
        stator = objects.make_symmetric_group(study, info["stator_cells"], rules=symcases.STATOR_RULES, name="Stator")
        objects.set_rows(stator, [{**r, "mode": "table", "table": ["Stator"] * 24} for r in objects.rows_of(stator)])
        lib = _steel(study)
        for r in range(3):
            objects.set_row_material(study, stator, r, lib)
        objects.sync_parts(study)
        doc.recompute()
        doc.saveAs(str(tmp_path / "s.FCStd"))
        path = jobwriter.write_job(study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        assert "rotor_file" not in job and len(job["symmetric"]["groups"]) == 1
        assert "slide" not in job["symmetric"]
        r = _mesh(path)
        assert r.returncode == 0, r.stderr
        assert os.path.exists(job["mesh_file"])
        found = meshreport.groups(job["mesh_file"])
        assert {name for name, _ in found.values()} == {"Stator"} and all(c > 0 for _, c in found.values())
        assert meshreport._marker(job["mesh_file"], 0) is None
    finally:
        for name in list(App.listDocuments()):
            App.closeDocument(name)
