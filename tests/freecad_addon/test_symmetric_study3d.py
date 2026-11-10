"""The motor as two Symmetric Groups in a 3D Study: validation, solids as parts, excitations on the drawing, the
sliding cylinder.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_symmetric_study3d.py"""

import json
import math
import os
import subprocess
import sys

import pytest

import FreeCAD as App
import Part

from emsolution import jobwriter, objects

from . import meshreport, symcases
from .test_meshsym3d import mesh_check_3d, slide_nodes, surface_group
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


def test_drawings_hold_24_and_16_copies_of_solids(motor3d):
    stator, rotor = objects.symmetric_groups(motor3d)
    assert len(stator.Cells) == 3 and all(c.Shape.Solids for c in objects.cell_bodies(motor3d))
    assert len(stator.Shape.Solids) == 24 * 3 and len(rotor.Shape.Solids) == 16 * 3


def test_cell_body_that_is_a_face_is_refused(motor3d):
    motor3d.Document.getObject("CoilCell").Shape = symcases.sector(37, 50, 10, 15)
    assert _has(motor3d, "CoilCell", "has no solid", "a cutting face or solid")
    assert not [t for t in _texts(motor3d) if "sketch" in t]


def test_overlap_is_measured_by_volume(motor3d):
    doc = motor3d.Document
    coil = doc.getObject("CoilCell")
    coil.Shape = symcases.sector(37, 50, 10, 17).extrude(App.Vector(0, 0, 10))
    doc.recompute()
    found = [t for t in _texts(motor3d) if "overlaps a mirrored copy" in t]
    assert found and "mm³" in found[0]
    x, y, z = (float(v) for v in found[0].split("near (")[1].split(")")[0].split(", "))
    assert 13 < math.degrees(math.atan2(y, x)) < 17 and 0 < z < 10


def test_part_without_material_is_an_error(motor3d):
    doc = motor3d.Document
    doc.removeObject(next(m for m in objects.part_assignments(motor3d) if m.GroupName == "Coil05").Name)
    doc.recompute()
    assert _has(motor3d, "Parts with no Material: Coil05")


def test_excitation_on_a_drawing_gets_a_smat_id(motor3d):
    objects.update_ids(motor3d)
    (exc,) = objects.excitations(motor3d)
    stator = objects.symmetric_groups(motor3d)[0]
    assert f"{exc.Name}|{stator.Name}" in motor3d.SmatIds


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


def test_sliding_cylinder_follows_the_drawings(motor3d):
    """Moving the cells up 2 mm moves the drawings; no link tells the interface, so validation refreshes it."""
    doc = motor3d.Document
    for cell in objects.cell_bodies(motor3d):
        cell.Shape = Part.makeCompound([s.translated(App.Vector(0, 0, 2)) for s in cell.Shape.Solids])
    doc.recompute()
    (iface,) = objects.sliding_interfaces(motor3d)
    assert iface.Shape.BoundBox.ZMax == pytest.approx(10)  # stale until validated
    assert [t for t in _texts(motor3d) if "overlap" in t] == []
    box = iface.Shape.BoundBox
    assert box.ZMin == pytest.approx(2) and box.ZMax == pytest.approx(12)


def test_empty_drawings_have_no_z_range(motor3d):
    for item in objects.symmetric_groups(motor3d):
        item.Cells = []
        objects.sync_rows(item)
    motor3d.Document.recompute()
    assert objects._drawings_z(motor3d) == (0.0, 0.0)
    (iface,) = objects.sliding_interfaces(motor3d)
    iface.touch()
    motor3d.Document.recompute([iface])
    assert "Invalid" not in iface.State and iface.Shape.isNull()


def test_divisions_must_fit_the_turns_3d(motor3d):
    (iface,) = objects.sliding_interfaces(motor3d)
    iface.Divisions = 100
    assert _has(motor3d, "multiple of the 12 turns")


def test_job_3d_has_groups_solids_and_excitations(motor3d):
    with open(jobwriter.write_job(motor3d), encoding="utf-8") as fh:
        job = json.load(fh)
    assert "dimension" not in job and "volumes" not in job
    stator, rotor = job["symmetric"]["groups"]
    assert [v["mat_id"] for g in (stator, rotor) for v in g["job"]["volumes"]] == [1, 2, 3, 1, 2, 3]
    assert (stator["side"], rotor["side"]) == ("fixed", "moving")
    assert (len(stator["transforms"]), len(rotor["transforms"])) == (24, 16)
    assert len(stator["parts"]) + len(rotor["parts"]) == 18
    group = objects.symmetric_groups(motor3d)[0]
    (exc,) = objects.excitations(motor3d)
    smat = int(motor3d.SmatIds[f"{exc.Name}|{group.Name}"])
    name = objects.item_name(exc, group)  # as a non-symmetric Study names it: <excitation>_<body>
    assert name == f"Coil01Ends_{objects.clean(group.Label)}"
    files = [f"geometry/g1_exc_{smat}_1.brep", f"geometry/g1_exc_{smat}_2.brep"]
    assert stator["excitations"] == [{"smat_id": smat, "name": name, "files": files}]
    assert rotor["excitations"] == []
    assert job["symmetric"]["slide"]["cross_divisions"] == 2


def test_both_copies_of_an_internal_face_give_one_excitation_file(motor3d):
    group = objects.symmetric_groups(motor3d)[0]
    shape = _top_shape(motor3d)
    name, _, _ = _duplicates(shape)["Plane"]
    tol = 1e-6 * shape.BoundBox.DiagonalLength
    face = shape.getElement(name)
    twin = next(
        f"Face{i}"
        for i, f in enumerate(shape.Faces, 1)
        if f"Face{i}" != name and objects.coincident_faces(face, f, tol)
    )
    (exc,) = objects.excitations(motor3d)
    exc.References = [(group, (name, twin))]
    motor3d.Document.recompute()
    with open(jobwriter.write_job(motor3d), encoding="utf-8") as fh:
        job = json.load(fh)
    (entry,) = job["symmetric"]["groups"][0]["excitations"]
    assert len(entry["files"]) == 1


def test_symmetric_3d_job_meshes_into_both_files(motor3d):
    motor3d.MeshSizesGroup.DefaultMeshSize = 4  # coarser than the fixture: warnings are fine, errors are not
    path = jobwriter.write_job(motor3d)
    with open(path, encoding="utf-8") as fh:
        job = json.load(fh)
    mesher = os.path.join(os.path.dirname(jobwriter.__file__), "mesher.py")
    r = subprocess.run([sys.executable, mesher, path, "--check"], capture_output=True, encoding="utf-8")
    assert r.returncode == 0 and "CHECK OK" in r.stdout, r.stdout + r.stderr
    r = subprocess.run([sys.executable, mesher, path], capture_output=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr
    fixed_msh, rotor_msh = job["mesh_file"], job["rotor_file"]
    groups = job["symmetric"]["groups"]
    ids = {p["mat_id"] for g in groups for p in g["parts"]}
    assert set(meshreport.groups(fixed_msh)) | set(meshreport.groups(rotor_msh)) == ids
    exc = groups[0]["excitations"][0]["smat_id"]
    assert surface_group(fixed_msh, exc)[1] > 0 and surface_group(rotor_msh, exc) is None
    assert len(slide_nodes(fixed_msh, 35)) > 0 and slide_nodes(fixed_msh, 35) == slide_nodes(rotor_msh, 35)
    for msh in (fixed_msh, rotor_msh):
        assert mesh_check_3d(msh, (35,), (0, 10))[1] == 0
    assert meshreport._marker(rotor_msh, 1) is not None and meshreport._marker(fixed_msh, 1) is None


def _owners(shape, face_name):
    face = shape.getElement(face_name)
    return [k + 1 for k, solid in enumerate(shape.Solids) if any(face.isSame(f) for f in solid.Faces)]


def _top_shape(study):
    from emsolution import geometry

    return geometry.global_shape(objects.symmetric_groups(study)[0])  # the stator's drawing


def test_outer_face_gives_its_solid(motor3d):
    shape = _top_shape(motor3d)
    outer = next(
        f"Face{i + 1}"
        for i, face in enumerate(shape.Faces)
        if abs(getattr(face.Surface, "Radius", 0) - 60) < 1e-6 and len(_owners(shape, f"Face{i + 1}")) == 1
    )
    (owner,) = _owners(shape, outer)
    assert objects.piece_solid(shape, outer, None, None) == f"Solid{owner}"


def _duplicates(shape):
    """{surface kind: (face name, its isSame owner, the owner of the coincident copy)}: internal walls that are two
    coincident faces, one per solid, as the drawing of a group (a compound of the copies) has them."""
    faces = shape.Faces
    owners = [[k for k, s in enumerate(shape.Solids, 1) if any(f.isSame(g) for g in s.Faces)] for f in faces]
    singles = [i for i, own in enumerate(owners) if len(own) == 1]
    found = {}
    for i in singles:
        a = faces[i]
        for j in singles:
            b = faces[j]
            if (
                j != i
                and abs(a.Area - b.Area) < 1e-6 * a.Area
                and a.CenterOfMass.distanceToPoint(b.CenterOfMass) < 1e-6
            ):
                found.setdefault(type(a.Surface).__name__, (f"Face{i + 1}", owners[i][0], owners[j][0]))
    return found


def test_coincident_duplicate_face_has_both_solids(motor3d):
    shape = _top_shape(motor3d)
    found = _duplicates(shape)
    assert {"Plane", "Cylinder"} <= set(found), found
    for name, own, other in found.values():
        assert own != other
        assert sorted(objects.face_solids(shape, name)) == sorted([f"Solid{own}", f"Solid{other}"])
        picked = shape.getElement(name).CenterOfMass
        for owner in (own, other):  # the far side from the camera, from both view directions
            view = shape.Solids[owner - 1].CenterOfMass - picked
            assert objects.piece_solid(shape, name, picked, view) == f"Solid{owner}"
        assert objects.piece_solid(shape, name, None, None) is None


def test_sliding_interface_on_flat_drawings_has_no_cylinder(motor3d):
    """2D cells in a 3D Study: the drawings have no height. The cylinder is not built; validation says why."""
    doc = motor3d.Document
    for cell in objects.cell_bodies(motor3d):
        cell.Shape = Part.makeCompound([f for f in cell.Shape.Faces if f.BoundBox.ZMax < 1e-9])
    doc.recompute()
    (iface,) = objects.sliding_interfaces(motor3d)
    iface.touch()
    doc.recompute([iface])
    assert "Invalid" not in iface.State and iface.Shape.isNull()
    assert _has(motor3d, "has no solid")


def test_curved_shared_face_with_a_pick_off_the_surface():
    import math

    import FreeCAD as App

    radius = 36.0
    inner = Part.makeCylinder(radius, 10, App.Vector(0, 0, 0), App.Vector(0, 0, 1), 15)
    outer = Part.makeCylinder(radius + 10, 10, App.Vector(0, 0, 0), App.Vector(0, 0, 1), 15).cut(inner)
    shape = inner.generalFuse([outer])[0]  # two solids sharing the cylinder wall
    (name,) = [
        f"Face{i + 1}"
        for i, face in enumerate(shape.Faces)
        if type(face.Surface).__name__ == "Cylinder" and len(_owners(shape, f"Face{i + 1}")) == 2
    ]
    face = shape.getElement(name)
    centre = face.CenterOfMass  # on the chord side of the wall, as a pick on the tessellation is
    assert abs(math.hypot(centre.x, centre.y) - radius) > 0.1
    radial = App.Vector(centre.x, centre.y, 0).normalize()
    on_surface = App.Vector(radial.x * radius, radial.y * radius, centre.z)
    owners = _owners(shape, name)
    inside = next(k for k in owners if shape.Solids[k - 1].isInside(on_surface - radial * 1e-3, 0, True))
    outside = next(k for k in owners if shape.Solids[k - 1].isInside(on_surface + radial * 1e-3, 0, True))
    assert inside != outside
    assert objects.piece_solid(shape, name, centre, radial) == f"Solid{outside}"  # from the bore, looking out
    assert objects.piece_solid(shape, name, centre, -radial) == f"Solid{inside}"  # from outside, looking in
