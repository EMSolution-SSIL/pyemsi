"""Symmetric Mesh in a 3D Study: validation, solids as pieces, excitations on tops, the sliding cylinder.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_study3d.py"""

import math

import pytest

import FreeCAD as App
import Part

from emsolution import objects

from . import symcases
from .test_symmetric_study import _has, _problems, _texts


@pytest.fixture
def motor3d(tmp_path):
    doc = App.newDocument("SymStudy3D")
    study = symcases.motor_study_3d(doc)
    doc.saveAs(str(tmp_path / "t.FCStd"))
    yield study
    for name in list(App.listDocuments()):
        App.closeDocument(name)


def test_motor_3d_validates_clean(motor3d):
    assert [(p.severity, p.text) for p in _problems(motor3d)] == []


def test_chain_reads_24_and_16_copies_of_solids(motor3d):
    stator, rotor = objects.symmetric_items(motor3d)
    assert stator.Steps == ["mirror (0, 0) 15°", "rotate (0, 0) 30° × 12"]
    assert rotor.Steps == ["mirror (0, 0) 22.5°", "rotate (0, 0) 45° × 8"]
    assert len(stator.Cells) == 3 and all(c.Shape.Solids for c in objects.cell_bodies(motor3d))
    assert len(stator.Top.Shape.Solids) == 24 * 3 and len(rotor.Top.Shape.Solids) == 16 * 3
    assert objects.piece_kind(motor3d) == "Solid"


def test_mirror_error_does_not_say_2d(motor3d):
    mirror = motor3d.Document.getObject("StatorMirror")
    n = mirror.Normal
    mirror.Normal = App.Vector(n.x, n.y, 0.3)
    motor3d.Document.recompute()
    texts = [t for t in _texts(motor3d) if "contain the Z axis" in t]
    assert texts and not any("2D" in t for t in texts)


def test_cell_body_that_is_a_face_is_refused(motor3d):
    motor3d.Document.getObject("CoilCell").Shape = symcases.sector(37, 50, 10, 15)
    assert _has(motor3d, "CoilCell", "has no solid")


def test_overlap_is_measured_by_volume(motor3d):
    doc = motor3d.Document
    coil = doc.getObject("CoilCell")
    coil.Shape = symcases.sector(37, 50, 10, 17).extrude(App.Vector(0, 0, 10))
    doc.recompute()
    found = [t for t in _texts(motor3d) if "overlaps a mirrored copy" in t]
    assert found and "mm³" in found[0]
    x, y, z = (float(v) for v in found[0].split("near (")[1].split(")")[0].split(", "))
    assert 13 < math.degrees(math.atan2(y, x)) < 17 and 0 < z < 10


def test_solid_without_material_is_an_error(motor3d):
    doc = motor3d.Document
    doc.removeObject(next(m for m in objects.piece_assignments(motor3d) if m.GroupName == "Coil05").Name)
    doc.recompute()
    assert _has(motor3d, "Pieces with no Material: StatorFragments.Solid")


def test_excitation_on_a_top_gets_a_smat_id(motor3d):
    objects.update_ids(motor3d)
    (exc,) = objects.excitations(motor3d)
    top = objects.symmetric_items(motor3d)[0].Top
    assert f"{exc.Name}|{top.Name}" in motor3d.SmatIds


def test_excitation_on_a_cell_body_is_refused(motor3d):
    cell = next(b for b in objects.cell_bodies(motor3d) if b.Name == "CoilCell")
    (exc,) = objects.excitations(motor3d)
    exc.References = [(cell, "Face1")]
    assert _has(motor3d, "Excitation Coil01Ends refers to CoilCell", "Pick the faces on the drawing")


def test_sliding_interface_shape_is_the_cylinder(motor3d):
    (iface,) = objects.sliding_interfaces(motor3d)
    iface.recompute()
    (face,) = iface.Shape.Faces
    assert isinstance(face.Surface, Part.Cylinder) and face.Surface.Radius == pytest.approx(35)
    assert face.BoundBox.ZMin == pytest.approx(0) and face.BoundBox.ZMax == pytest.approx(10)


def test_sliding_cylinder_follows_the_tops(motor3d):
    """Moving the cells up 2 mm moves the tops; no link tells the interface, so validation refreshes it."""
    doc = motor3d.Document
    for cell in objects.cell_bodies(motor3d):
        cell.Shape = Part.makeCompound([s.translated(App.Vector(0, 0, 2)) for s in cell.Shape.Solids])
    doc.recompute()
    (iface,) = objects.sliding_interfaces(motor3d)
    assert iface.Shape.BoundBox.ZMax == pytest.approx(10)  # stale until validated
    assert [t for t in _texts(motor3d) if "overlap" in t] == []
    box = iface.Shape.BoundBox
    assert box.ZMin == pytest.approx(2) and box.ZMax == pytest.approx(12)


def test_tops_without_items_have_no_z_range(motor3d):
    for item in objects.symmetric_items(motor3d):
        item.Top = None
    with pytest.raises(ValueError, match="needs a top object"):
        objects._tops_z(motor3d)


def test_divisions_must_fit_the_copy_count_3d(motor3d):
    (iface,) = objects.sliding_interfaces(motor3d)
    iface.Divisions = 100
    assert _has(motor3d, "multiple of the 24 copies")


def test_2d_motor_still_validates_clean(tmp_path):
    doc = App.newDocument("SymStudy2D")
    try:
        study = symcases.motor_study(doc)
        assert objects.piece_kind(study) == "Face"
        assert [(p.severity, p.text) for p in _problems(study)] == []
    finally:
        for name in list(App.listDocuments()):
            App.closeDocument(name)
