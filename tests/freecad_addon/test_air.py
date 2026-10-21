"""Air Region item and its shapes. Run from the repo root: pixi run pytest tests/freecad_addon/test_air.py"""

import json
import math
import os
import tempfile
import unittest
from unittest import mock

import FreeCAD as App
import Part
import pytest

from emsolution import airshapes, objects, validation, jobwriter, studymaterials

from .materialdata import AIR, STEEL, record


class AirTest(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("T")
        self.tmp = tempfile.TemporaryDirectory()
        self.study = objects.make_study(self.doc)
        self.study.MainMode = "Manual"
        self.doc.saveAs(os.path.join(self.tmp.name, "T.FCStd"))

    def tearDown(self):
        App.closeDocument(self.doc.Name)
        self.tmp.cleanup()

    def study_2d(self, normal):
        """A 2D Study with one square face body in z = 0 (normal along z) or y = 0 (normal along y)."""
        self.doc.removeObject(self.study.Name)
        self.study = objects.make_study(self.doc, "2D")
        self.study.MainMode = "Manual"
        body = self.doc.addObject("Part::Feature", "Face")
        body.Shape = Part.makePlane(10, 10, App.Vector(0, 0, 0), normal)
        self.study.MainObjects = [body]
        self.doc.recompute()
        return body

    def test_new_study_has_air_regions_folder(self):
        self.assertEqual(self.study.AirRegionsGroup.Label, "Air Regions")
        self.assertEqual(objects.air_regions(self.study), [])

    def test_restored_old_study_gets_air_folder_and_keeps_ids(self):
        box = self.doc.addObject("Part::Box", "A")
        self.study.MainObjects = [box]
        self.doc.recompute()
        objects.update_ids(self.study)
        ids = dict(self.study.MatIds)
        self.assertTrue(ids)
        self.doc.removeObject(self.study.AirRegionsGroup.Name)  # an old file has no such folder
        self.study.removeProperty("AirRegionsGroup")
        path = os.path.join(self.tmp.name, "old.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        self.assertEqual(study.AirRegionsGroup.Label, "Air Regions")
        self.assertIn(study.AirRegionsGroup, study.Group)
        self.assertEqual(dict(study.MatIds), ids)

    def test_air_region_survives_save_and_reload(self):
        objects.make_air_region(self.study, "Box", Length=20, Width=10, Height=4)
        path = os.path.join(self.tmp.name, "air.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        (air,) = objects.air_regions(objects.find_study(self.doc))
        self.assertEqual(air.Label, "Air")
        self.assertIsInstance(air.Proxy, objects.AirRegion)
        self.doc.recompute()
        self.assertEqual(air.Shape.Volume, pytest.approx(800))

    def test_box_air_3d_is_centred_solid(self):
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 0, 0), Length=20, Width=10, Height=4)
        self.doc.recompute()
        self.assertEqual(air.Shape.Volume, pytest.approx(800))
        box = air.Shape.BoundBox
        self.assertEqual((box.XMin, box.XMax), (pytest.approx(-5), pytest.approx(15)))
        self.assertEqual((box.YMin, box.YMax), (pytest.approx(-5), pytest.approx(5)))
        self.assertEqual((box.ZMin, box.ZMax), (pytest.approx(-2), pytest.approx(2)))
        self.assertEqual(objects.air_regions(self.study), [air])

    def test_box_air_2d_xy_and_zx_rectangles(self):
        self.study_2d(App.Vector(0, 0, 1))
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 1, 0), Length=20, Width=10)
        self.doc.recompute()
        box = air.Shape.BoundBox
        self.assertEqual(air.Shape.Area, pytest.approx(200))
        self.assertEqual((box.XMin, box.XMax, box.YMin, box.YMax), tuple(pytest.approx(v) for v in (-5, 15, -4, 6)))
        self.assertEqual((box.ZMin, box.ZMax), (pytest.approx(0), pytest.approx(0)))
        self.study_2d(App.Vector(0, 1, 0))
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 0, 1), Length=20, Width=10)
        self.doc.recompute()
        box = air.Shape.BoundBox
        self.assertEqual(air.Shape.Area, pytest.approx(200))
        self.assertEqual((box.XMin, box.XMax, box.ZMin, box.ZMax), tuple(pytest.approx(v) for v in (-5, 15, -4, 6)))
        self.assertEqual((box.YMin, box.YMax), (pytest.approx(0), pytest.approx(0)))

    def test_sector_air_3d_extrudes_from_zmin(self):
        air = objects.make_air_region(
            self.study, "Sector", InnerRadius=10, OuterRadius=20, StartAngle=0, EndAngle=90, Height=8, ZMin=-3
        )
        self.doc.recompute()
        self.assertEqual(air.Shape.Volume, pytest.approx(math.pi * 300 / 4 * 8))
        self.assertEqual((air.Shape.BoundBox.ZMin, air.Shape.BoundBox.ZMax), (pytest.approx(-3), pytest.approx(5)))

    def test_sector_air_2d_xy_quarter_ring_area(self):
        self.study_2d(App.Vector(0, 0, 1))
        air = objects.make_air_region(self.study, "Sector", InnerRadius=10, OuterRadius=20, StartAngle=0, EndAngle=90)
        self.doc.recompute()
        self.assertEqual(air.Shape.Area, pytest.approx(math.pi * (400 - 100) / 4))
        self.assertTrue(all(v.Z == pytest.approx(0) for v in air.Shape.Vertexes))
        box = air.Shape.BoundBox
        self.assertEqual((box.XMin, box.YMin), (pytest.approx(0), pytest.approx(0)))

    def test_sector_air_2d_xy_rotated_start_angle(self):
        self.study_2d(App.Vector(0, 0, 1))
        air = objects.make_air_region(self.study, "Sector", OuterRadius=20, StartAngle=90, EndAngle=180)
        self.doc.recompute()
        box = air.Shape.BoundBox
        self.assertEqual(air.Shape.Area, pytest.approx(math.pi * 400 / 4))
        self.assertEqual((box.XMin, box.XMax), (pytest.approx(-20), pytest.approx(0)))
        self.assertEqual((box.YMin, box.YMax), (pytest.approx(0), pytest.approx(20)))

    def test_sector_air_zx_is_half_disc_on_axis(self):
        self.study_2d(App.Vector(0, 1, 0))
        air = objects.make_air_region(self.study, "Sector", OuterRadius=30)
        self.doc.recompute()
        box = air.Shape.BoundBox
        self.assertEqual((box.XMin, box.XMax), (pytest.approx(0), pytest.approx(30)))
        self.assertEqual((box.YMin, box.YMax), (pytest.approx(0), pytest.approx(0)))
        self.assertEqual((box.ZMin, box.ZMax), (pytest.approx(-30), pytest.approx(30)))
        self.assertEqual(air.Shape.Area, pytest.approx(math.pi * 900 / 2))

    def test_custom_air_uses_the_source_body(self):
        body = self.doc.addObject("Part::Box", "Outer")
        body.Placement.Base = App.Vector(1, 2, 3)
        air = objects.make_air_region(self.study, "Custom", Source=body)
        self.doc.recompute()
        self.assertEqual(air.Shape.Volume, pytest.approx(1000))
        self.assertEqual(air.Shape.BoundBox.XMin, pytest.approx(1))

    def test_custom_air_without_source_raises(self):
        air = objects.make_air_region(self.study, "Custom")
        self.doc.recompute()
        self.assertIn("Invalid", air.State)
        with self.assertRaises(ValueError) as ctx:
            airshapes.air_shape(air, "3D")
        self.assertIn("choose a body", str(ctx.exception))
        self.assertIn("Air", str(ctx.exception))

    def test_study_plane(self):
        self.assertEqual(airshapes.study_plane(self.study), "3D")
        self.study_2d(App.Vector(0, 1, 0))
        self.assertEqual(airshapes.study_plane(self.study), "ZX")
        self.study_2d(App.Vector(0, 0, 1))
        self.assertEqual(airshapes.study_plane(self.study), "XY")

    def bodies(self, *names):
        boxes = [self.doc.addObject("Part::Box", n) for n in names]
        self.study.MainObjects = boxes
        self.doc.recompute()
        return boxes

    def steel(self):
        return objects.make_library_material(self.study, json.dumps(record("user:steel", "Steel", "Steel", STEEL)))

    def test_air_gets_mat_id_after_bodies(self):
        self.bodies("A", "B")
        air = objects.make_air_region(self.study, "Box")
        objects.update_ids(self.study)
        self.assertEqual(dict(self.study.MatIds), {"A": "1", "B": "2", air.Name: "3"})
        self.assertEqual(objects.id_rows(self.study)[-1][2], "Air")

    def test_air_id_survives_rename_and_is_not_reused_after_delete(self):
        self.bodies("A", "B")
        air = objects.make_air_region(self.study, "Box")
        objects.update_ids(self.study)
        air.Label = "Surroundings"
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds[air.Name], "3")
        self.assertEqual(objects.id_rows(self.study)[-1][2], "Surroundings")
        self.doc.removeObject(air.Name)
        c = self.doc.addObject("Part::Box", "C")
        self.study.MainObjects = [*self.study.MainObjects, c]
        self.doc.recompute()
        objects.update_ids(self.study)
        self.assertEqual(dict(self.study.MatIds), {"A": "1", "B": "2", "C": "4"})

    def test_air_region_can_get_a_material(self):
        self.bodies("A")
        air = objects.make_air_region(self.study, "Box")
        self.assertEqual(objects.assignment_problem(self.study, [air]), "")
        objects.assign(self.study, [air], self.steel(), 0)
        objects.update_ids(self.study)
        rows = {r[2][0]: r[2] for r in objects.material_rows(self.study)}
        self.assertEqual(rows["Air"][1:3], ["Steel", self.study.MatIds[air.Name]])

    def test_missing_air_material_is_warned(self):
        (a,) = self.bodies("A")
        air = objects.make_air_region(self.study, "Box")
        self.assertEqual(objects.bodies_without_material(self.study), [a, air])
        objects.assign(self.study, [air], self.steel(), 0)
        self.assertEqual(objects.bodies_without_material(self.study), [a])

    def test_air_keys_and_key_names(self):
        (a,) = self.bodies("A")
        air = objects.make_air_region(self.study, "Box")
        air.Label = "Air gap"
        self.assertEqual(objects.air_keys(self.study), [air.Name])
        self.assertEqual(objects.key_name(self.study, a.Name), "A")
        self.assertEqual(objects.key_name(self.study, air.Name), "Air_gap")
        self.study.Movement = "Sliding motion"
        self.assertEqual(objects.air_keys(self.study), [f"{air.Name}#fixed", f"{air.Name}#moving"])
        self.assertEqual(objects.key_name(self.study, f"{air.Name}#fixed"), "Air_gap_fixed")
        self.assertEqual(objects.key_name(self.study, f"{air.Name}#moving"), "Air_gap_moving")

    def air_errors(self):
        return [p.text for p in validation.errors(validation.validate(self.study))]

    def air_problems(self):
        return [t for t in self.air_errors() if "Air Region" in t]

    def test_two_air_regions_is_an_error(self):
        self.bodies("A")
        first = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5))
        second = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5))
        problems = validation.validate(self.study)
        text = f"Only one Air Region per Study: {first.Label}, {second.Label}. Delete the others."
        self.assertIn(text, [p.text for p in validation.errors(problems)])
        (problem,) = [p for p in problems if p.text == text]
        self.assertIs(problem.item, second)

    def test_body_outside_air_is_an_error_naming_it(self):
        (a,) = self.bodies("A")
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=4, Width=4, Height=4)
        problems = validation.validate(self.study)
        text = f"{a.Label} is not fully inside Air Region {air.Label}."
        self.assertIn(text, [p.text for p in validation.errors(problems)])
        (problem,) = [p for p in problems if p.text == text]
        self.assertIs(problem.item, air)
        self.assertEqual(problem.refs, [(a, "")])

    def test_body_inside_air_passes(self):
        self.bodies("A")
        objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.assertEqual(self.air_problems(), [])

    def test_body_outside_air_2d_is_an_error(self):
        body = self.study_2d(App.Vector(0, 0, 1))
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 0), Length=4, Width=4)
        self.assertIn(f"{body.Label} is not fully inside Air Region {air.Label}.", self.air_errors())
        air.Length = air.Width = 30
        self.assertEqual(self.air_problems(), [])

    def test_zx_box_left_of_axis_is_an_error(self):
        self.study_2d(App.Vector(0, 1, 0))
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(0, 0, 5), Length=40, Width=30)
        text = f"Air Region {air.Label}: in a ZX (axisymmetric) Study use a half disc or a rectangle starting on the Z axis."
        self.assertIn(text, self.air_errors())
        air.Center = App.Vector(15, 0, 5)
        air.Length = 30
        self.assertEqual(self.air_problems(), [])

    def test_zx_custom_is_an_error(self):
        self.study_2d(App.Vector(0, 1, 0))
        source = self.doc.addObject("Part::Feature", "Outer")
        source.Shape = Part.makePlane(30, 30, App.Vector(0, 0, 0), App.Vector(0, 1, 0))
        air = objects.make_air_region(self.study, "Custom", Source=source)
        text = f"Air Region {air.Label}: in a ZX (axisymmetric) Study use a half disc or a rectangle starting on the Z axis."
        self.assertIn(text, self.air_errors())

    def test_zx_half_disc_passes(self):
        self.study_2d(App.Vector(0, 1, 0))
        objects.make_air_region(self.study, "Sector", OuterRadius=30)
        self.assertEqual(self.air_problems(), [])

    def test_custom_without_source_is_an_error(self):
        self.bodies("A")
        air = objects.make_air_region(self.study, "Custom")
        self.assertEqual(self.air_problems(), [f"Air Region {air.Label}: choose a body for the Custom shape"])

    def test_bad_radii_and_angles_are_errors(self):
        self.bodies("A")
        air = objects.make_air_region(self.study, "Sector", InnerRadius=20, OuterRadius=10)
        text = f"Air Region {air.Label}: the outer radius must be larger than the inner radius."
        self.assertEqual(self.air_problems(), [text])
        air.InnerRadius = 0
        air.StartAngle, air.EndAngle = 90, 30
        text = f"Air Region {air.Label}: the end angle must be larger than the start angle (at most 360\N{DEGREE SIGN} more)."
        self.assertEqual(self.air_problems(), [text])

    def air_job(self):
        """Write the job of one 10 mm box inside an Air Region; returns the job."""
        self.bodies("A")
        objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.doc.recompute()
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            return json.load(fh)

    def test_job_has_air_with_default_size(self):
        job = self.air_job()
        self.assertEqual(job["air"], {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 5.0})
        self.assertTrue(os.path.exists(os.path.join(jobwriter.scratch_folder(self.study), "geometry", "air.brep")))

    def test_job_air_is_current_without_a_recompute(self):
        self.bodies("A")
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.doc.recompute()
        air.Length = 50  # touched, not recomputed
        jobwriter.write_job(self.study)
        self.assertAlmostEqual(self.exported_air().XLength, 50)
        self.doc.removeObject(air.Name)
        fresh = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.assertTrue(fresh.Shape.isNull())  # never recomputed
        jobwriter.write_job(self.study)
        self.assertAlmostEqual(self.exported_air().XLength, 30)

    def exported_air(self):
        """Bound box of the air BREP the last job wrote."""
        return Part.read(os.path.join(jobwriter.scratch_folder(self.study), "geometry", "air.brep")).BoundBox

    def test_job_without_air_has_no_air_key(self):
        self.bodies("A")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("air", json.load(fh))

    def test_air_mesh_size_item_applies(self):
        self.bodies("A")
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.doc.recompute()
        objects.make_mesh_size(self.study, 2, [(air, "")])
        self.assertEqual(jobwriter.air_size(self.study), 2.0)
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["air"]["size"], 2.0)

    def test_air_face_mesh_size_is_exported(self):
        self.bodies("A")
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.doc.recompute()
        objects.make_mesh_size(self.study, 1, [(air, "Face1")])
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        (item,) = job["sizes"]
        self.assertEqual((item["size"], len(item["files"])), (1.0, 1))
        self.assertEqual(job["air"]["size"], 5.0)  # a face size does not change the air's size

    def test_air_is_a_material_row_after_the_bodies(self):
        (a,) = self.bodies("A")
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.doc.recompute()
        air.Label = "Air gap"
        steel = self.steel()
        objects.assign(self.study, [a, air], steel, 1)
        rows = studymaterials.study_material_rows(self.study)
        self.assertEqual(
            [(r[0], r[1], r[2], r[3].material_id) for r in rows],
            [(1, "A", 1, "user:steel"), (2, "Air_gap", 1, "user:steel")],
        )

    def test_air_name_ignores_a_taken_label(self):
        (a,) = self.bodies("A")
        lib = objects.make_library_material(self.study, json.dumps(record("user:air", "Air", "generic", AIR)))
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.doc.recompute()
        self.assertNotEqual(air.Label, "Air")  # the library material has it
        objects.assign(self.study, [a, air], lib, 0)
        rows = studymaterials.study_material_rows(self.study)
        self.assertEqual([r[1] for r in rows], ["A", "Air"])
        self.assertEqual(objects.key_name(self.study, air.Name), "Air")
        self.assertEqual([r[2] for r in objects.id_rows(self.study)], ["A", "Air"])
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["air"]["name"], "Air")
        self.study.Movement = "Sliding motion"
        self.assertEqual(objects.key_name(self.study, f"{air.Name}#fixed"), "Air_fixed")
        self.assertEqual(objects.key_name(self.study, f"{air.Name}#moving"), "Air_moving")

    def test_air_without_a_material_joins_the_missing_error(self):
        (a,) = self.bodies("A")
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.doc.recompute()
        air.Label = "Air gap"
        objects.assign(self.study, [a], self.steel(), 0)
        with self.assertRaisesRegex(jobwriter.StudyError, "no material from the Material Library: Air gap$"):
            studymaterials.study_material_rows(self.study)

    def sliding(self, fixed, moving):
        """Slide: fixed and moving are lists of box names."""
        self.bodies(*fixed)
        boxes = [self.doc.addObject("Part::Box", n) for n in moving]
        for k, box in enumerate(boxes):
            box.Placement.Base = App.Vector(20 + 20 * k, 0, 0)
        self.study.MovingMode, self.study.MovingObjects = "Manual", boxes
        self.study.Movement = "Sliding motion"
        self.doc.recompute()
        return boxes

    def test_moving_bodies_get_ids_after_main_bodies(self):
        self.sliding(["A", "B"], ["M"])
        objects.update_ids(self.study)
        self.assertEqual(dict(self.study.MatIds), {"A": "1", "B": "2", "M": "3"})
        self.assertEqual([r[2] for r in objects.id_rows(self.study)], ["A", "B", "M"])
        self.study.Movement = "No movement"
        objects.update_ids(self.study)
        self.assertEqual(dict(self.study.MatIds), {"A": "1", "B": "2"})

    def test_moving_body_can_get_a_material(self):
        (m,) = self.sliding(["A"], ["M"])
        self.assertEqual(objects.assignment_problem(self.study, [m]), "")
        objects.assign(self.study, [m], self.steel(), 0)
        objects.update_ids(self.study)
        rows = {r[2][0]: r[2] for r in objects.material_rows(self.study)}
        self.assertEqual(rows["M"][1:3], ["Steel", self.study.MatIds[m.Name]])
        self.assertEqual(objects.bodies_without_material(self.study), [self.study.MainObjects[0]])
        self.study.Movement = "No movement"
        self.assertIn("Not in the Study's main geometry: M", objects.assignment_problem(self.study, [m]))

    def test_study_bodies_have_no_duplicates(self):
        (m,) = self.sliding(["A"], ["M"])
        self.assertEqual([b.Name for b in objects.study_bodies(self.study)], ["A", "M"])
        self.study.MainObjects = [*self.study.MainObjects, m]  # both: setup reports it, the list stays unique
        self.assertEqual([b.Name for b in objects.study_bodies(self.study)], ["A", "M"])

    def test_job_lists_moving_mat_ids(self):
        self.sliding(["A", "B"], ["M"])
        objects.make_air_region(self.study, "Box", Center=App.Vector(20, 5, 5), Length=80, Width=30, Height=30)
        objects.make_sliding_interface(self.study, "Linear", NormalAxis="X", Position=15, MotionAxis="Y")
        self.doc.recompute()
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual([v["mat_id"] for v in job["volumes"]], [1, 2, 3])
        self.assertEqual(job["moving"], [3])

    def test_static_job_has_no_moving_key(self):
        self.bodies("A")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("moving", json.load(fh))

    def test_sliding_air_gets_a_fixed_and_a_moving_id(self):
        self.sliding(["A"], ["M"])
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(20, 5, 5), Length=80, Width=30, Height=30)
        objects.update_ids(self.study)
        fixed, moving = f"{air.Name}#fixed", f"{air.Name}#moving"
        self.assertEqual(dict(self.study.MatIds), {"A": "1", "M": "2", fixed: "3", moving: "4"})
        self.assertEqual([r[2] for r in objects.id_rows(self.study)], ["A", "M", "Air_fixed", "Air_moving"])
        self.study.Movement = "No movement"
        objects.update_ids(self.study)
        self.assertEqual(dict(self.study.MatIds), {"A": "1", air.Name: "5"})
        self.study.Movement = "Sliding motion"
        objects.update_ids(self.study)
        self.assertEqual(dict(self.study.MatIds), {"A": "1", "M": "2", fixed: "3", moving: "4"})

    def test_sliding_air_row_shows_both_ids(self):
        self.sliding(["A"], ["M"])
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(20, 5, 5), Length=80, Width=30, Height=30)
        rows = {r[2][0]: r[2] for r in objects.material_rows(self.study)}
        self.assertEqual(rows["Air"][2], "–")  # no IDs yet
        objects.update_ids(self.study)
        rows = {r[2][0]: r[2] for r in objects.material_rows(self.study)}
        self.assertEqual(rows["Air"][2], "3 / 4")
        self.assertEqual(objects.air_region_rows(self.study)[0][2], ["Air", "Box", "3 / 4"])
        self.study.Movement = "No movement"
        objects.update_ids(self.study)
        rows = {r[2][0]: r[2] for r in objects.material_rows(self.study)}
        self.assertEqual(rows["Air"][2], self.study.MatIds[air.Name])

    def test_sliding_with_air_writes_the_slide_job(self):
        self.box_slide()
        iface = objects.sliding_interfaces(self.study)[0]
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        folder = jobwriter.scratch_folder(self.study)
        air = objects.air_regions(self.study)[0]
        ids = self.study.MatIds
        self.assertEqual(job["rotor_file"], os.path.join(jobwriter.simulation_folder(self.study), "rotor_mesh.msh"))
        self.assertEqual(
            job["air"]["sides"],
            {
                "fixed": {"mat_id": int(ids[f"{air.Name}#fixed"]), "name": "Air_fixed"},
                "moving": {"mat_id": int(ids[f"{air.Name}#moving"]), "name": "Air_moving"},
            },
        )
        self.assertNotIn("mat_id", job["air"])
        self.assertNotIn("name", job["air"])
        self.assertEqual(len(job["moving_cells"]), 1)
        (slide,) = job["slides"]
        self.assertEqual(
            (slide["kind"], slide["divisions"], slide["cross_divisions"], slide["full"]), ("linear", 90, 10, False)
        )
        self.assertEqual(slide["slide_mat_id"], int(ids[iface.Name]))
        self.assertEqual(job["periodic"], {"kind": "translation", "vector": [0.0, 30.0, 0.0], "start": -10.0})
        for rel in [*job["moving_cells"], *slide["files"], slide["marker"]]:
            self.assertTrue(os.path.exists(os.path.join(folder, rel)), rel)

    def interface(self, plane, air_shape, air_props, kind, **props):
        """A sliding Study in plane ("XY" or "3D") with an Air Region and one Sliding Interface, recomputed."""
        if plane == "XY":
            self.study_2d(App.Vector(0, 0, 1))
        self.study.Movement = "Sliding motion"
        objects.make_air_region(self.study, air_shape, **air_props)
        iface = objects.make_sliding_interface(self.study, kind, **props)
        self.doc.recompute()
        return iface

    def test_full_circle_interface_is_two_half_arcs(self):
        iface = self.interface("XY", "Sector", {"OuterRadius": 100}, "Rotational", Radius=42.5)
        self.assertEqual(len(iface.Shape.Edges), 2)
        self.assertAlmostEqual(iface.Shape.Length, 2 * math.pi * 42.5)
        ends = sorted((round(v.X, 6), round(v.Y, 6)) for e in iface.Shape.Edges for v in e.Vertexes)
        self.assertEqual(ends, [(-42.5, 0), (-42.5, 0), (42.5, 0), (42.5, 0)])  # split at 0 and 180 degrees

    def test_sector_interface_spans_the_sector(self):
        air = {"OuterRadius": 100, "EndAngle": 45}
        iface = self.interface("XY", "Sector", air, "Rotational", Radius=80.575)
        self.assertEqual(len(iface.Shape.Edges), 1)
        self.assertAlmostEqual(iface.Shape.Length, math.pi / 4 * 80.575)

    def test_linear_interface_spans_box(self):
        air = {"Center": App.Vector(40, 0, 0), "Length": 80, "Width": 40}
        iface = self.interface("XY", "Box", air, "Linear", NormalAxis="Y", Position=11, MotionAxis="X")
        (edge,) = iface.Shape.Edges
        ends = sorted((round(v.X, 6), round(v.Y, 6), round(v.Z, 6)) for v in edge.Vertexes)
        self.assertEqual(ends, [(0, 11, 0), (80, 11, 0)])

    def test_cylinder_interface_3d_halves(self):
        air = {"OuterRadius": 100, "Height": 100, "ZMin": -50}
        iface = self.interface("3D", "Sector", air, "Rotational", Radius=42.5)
        self.assertEqual(len(iface.Shape.Faces), 2)
        self.assertAlmostEqual(iface.Shape.Area, 2 * math.pi * 42.5 * 100)
        (air,) = objects.air_regions(self.study)
        self.assertEqual(len(airshapes.cells(air.Shape, [iface.Shape])), 2)

    def test_marker_2d_is_point_at_start_angle(self):
        air = {"OuterRadius": 100, "StartAngle": 30, "EndAngle": 75}
        iface = self.interface("XY", "Sector", air, "Rotational", Radius=42.5)
        marker = airshapes.slide_marker(iface, iface.Shape, "XY")
        self.assertIsInstance(marker, Part.Vertex)
        a = math.radians(30)
        self.assertEqual(
            (marker.X, marker.Y, marker.Z), (pytest.approx(42.5 * math.cos(a)), pytest.approx(42.5 * math.sin(a)), 0)
        )

    def test_marker_2d_linear_is_the_start_end(self):
        air = {"Center": App.Vector(40, 0, 0), "Length": 80, "Width": 40}
        iface = self.interface("XY", "Box", air, "Linear", NormalAxis="Y", Position=11, MotionAxis="X")
        marker = airshapes.slide_marker(iface, iface.Shape, "XY")
        self.assertEqual((marker.X, marker.Y), (pytest.approx(0), pytest.approx(11)))

    def test_marker_3d_is_vertical_generatrix(self):
        air = {"OuterRadius": 100, "EndAngle": 90, "Height": 100, "ZMin": -50}
        iface = self.interface("3D", "Sector", air, "Rotational", Radius=42.5)
        marker = airshapes.slide_marker(iface, iface.Shape, "3D")
        self.assertIsInstance(marker, Part.Edge)
        ends = sorted((round(v.X, 6), round(v.Y, 6), round(v.Z, 6)) for v in marker.Vertexes)
        self.assertEqual(ends, [(42.5, 0, -50), (42.5, 0, 50)])

    def disc(self, outer, inner=0):
        face = Part.Face(Part.Wire(Part.makeCircle(outer)))
        return face.cut(Part.Face(Part.Wire(Part.makeCircle(inner)))) if inner else face

    def motor_cells(self, radius=42.5):
        iface = self.interface("XY", "Sector", {"OuterRadius": 100}, "Rotational", Radius=radius)
        (air,) = objects.air_regions(self.study)
        return airshapes.cells(air.Shape, [iface.Shape])

    def test_cells_and_cell_of(self):
        cells = self.motor_cells()
        self.assertEqual(len(cells), 2)
        inner = min(range(2), key=lambda k: cells[k].Area)
        self.assertAlmostEqual(cells[inner].Area, math.pi * 42.5**2)
        self.assertEqual(airshapes.cell_of(self.disc(40), cells), inner)
        self.assertEqual(airshapes.cell_of(self.disc(80, 45), cells), 1 - inner)
        self.assertIsNone(airshapes.cell_of(self.disc(44), cells))

    def test_body_on_slide_surface_is_not_crossing(self):
        cells = self.motor_cells()
        inner = min(range(2), key=lambda k: cells[k].Area)
        self.assertEqual(airshapes.cell_of(self.disc(42.5), cells), inner)
        self.assertEqual(airshapes.cell_of(self.disc(80, 42.5), cells), 1 - inner)

    def test_period_sector_and_linear(self):
        self.interface("XY", "Sector", {"OuterRadius": 100, "EndAngle": 45}, "Rotational", Radius=42.5)
        self.assertEqual(airshapes.period(self.study), {"kind": "rotation", "angle": 45.0, "start": 0.0})
        (air,) = objects.air_regions(self.study)
        air.EndAngle = 360
        self.assertIsNone(airshapes.period(self.study))
        air.AirShape, air.Center, air.Length, air.Width = "Box", App.Vector(40, 0, 0), 80, 40
        self.assertIsNone(airshapes.period(self.study))  # a Rotational interface in a Box: no period
        (iface,) = objects.sliding_interfaces(self.study)
        iface.Kind, iface.NormalAxis, iface.MotionAxis = "Linear", "Y", "X"
        self.assertEqual(airshapes.period(self.study), {"kind": "translation", "vector": [80, 0, 0], "start": 0.0})

    def test_interface_gets_slide_mat_id(self):
        self.sliding(["A"], ["M"])
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(20, 5, 5), Length=80, Width=30, Height=30)
        iface = objects.make_sliding_interface(self.study, "Linear", NormalAxis="X", Position=15, MotionAxis="Y")
        self.assertIs(iface.AirRegion, air)
        self.assertEqual(objects.air_regions(self.study), [air])
        self.assertEqual(objects.sliding_interfaces(self.study), [iface])
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds[iface.Name], "5")
        self.assertEqual([r[2] for r in objects.id_rows(self.study)][-1], "Sliding_Interface")
        self.study.Movement = "No movement"
        objects.update_ids(self.study)
        self.assertNotIn(iface.Name, self.study.MatIds)

    def test_axial_gap_interface_is_two_half_discs(self):
        air = {"OuterRadius": 100, "Height": 100, "ZMin": -50}
        iface = self.interface("3D", "Sector", air, "Axial gap", Position=20)
        self.assertEqual(len(iface.Shape.Faces), 2)
        self.assertAlmostEqual(iface.Shape.Area, math.pi * 100**2)
        for face in iface.Shape.Faces:
            self.assertAlmostEqual(face.BoundBox.ZMin, 20)
            self.assertAlmostEqual(face.BoundBox.ZMax, 20)
        marker = airshapes.slide_marker(iface, iface.Shape, "3D")
        self.assertIsInstance(marker, Part.Edge)
        ends = sorted((round(v.X, 6), round(v.Y, 6), round(v.Z, 6)) for v in marker.Vertexes)
        self.assertEqual(ends, [(0, 0, 20), (100, 0, 20)])  # radial, at the start angle

    def test_linear_interface_3d_is_a_plane_across_the_box(self):
        air = {"Center": App.Vector(40, 0, 0), "Length": 80, "Width": 40, "Height": 30}
        iface = self.interface("3D", "Box", air, "Linear", NormalAxis="Y", Position=11, MotionAxis="X")
        (face,) = iface.Shape.Faces
        self.assertAlmostEqual(face.Area, 80 * 30)
        box = face.BoundBox
        self.assertEqual((box.XMin, box.XMax), (pytest.approx(0), pytest.approx(80)))
        self.assertEqual((box.YMin, box.YMax), (pytest.approx(11), pytest.approx(11)))
        marker = airshapes.slide_marker(iface, iface.Shape, "3D")
        ends = sorted((round(v.X, 6), round(v.Y, 6), round(v.Z, 6)) for v in marker.Vertexes)
        self.assertEqual(ends, [(0, 11, -15), (0, 11, 15)])  # across the motion, at its minimum

    def motor(self, rotor_radius=40, extra=()):
        """A 2D sliding Study: a ring stator (45..80) fixed, a disc rotor moving, a Sector air of radius 100
        with a Rotational interface at 42.5 and more at the radii in extra."""
        self.doc.removeObject(self.study.Name)
        self.study = objects.make_study(self.doc, "2D")
        self.study.MainMode = self.study.MovingMode = "Manual"
        stator, rotor = self.doc.addObject("Part::Feature", "Stator"), self.doc.addObject("Part::Feature", "Rotor")
        stator.Shape = self.disc(80, 45)
        rotor.Shape = self.disc(rotor_radius)
        self.study.MainObjects, self.study.MovingObjects = [stator], [rotor]
        self.study.Movement = "Sliding motion"
        objects.make_air_region(self.study, "Sector", OuterRadius=100)
        for radius in (42.5, *extra):
            objects.make_sliding_interface(self.study, "Rotational", Radius=radius)
        self.doc.recompute()
        return stator, rotor

    def box_slide(self, moving_x=20):
        """A 3D sliding Study: box A fixed at x = 0..10, box M moving, a Linear interface at x = 15."""
        self.sliding(["A"], ["M"])
        self.study.MovingObjects[0].Placement.Base = App.Vector(moving_x, 0, 0)
        objects.make_air_region(self.study, "Box", Center=App.Vector(20, 5, 5), Length=80, Width=30, Height=30)
        iface = objects.make_sliding_interface(self.study, "Linear", NormalAxis="X", Position=15, MotionAxis="Y")
        self.doc.recompute()
        return iface

    def test_valid_2d_motor_has_no_slide_problems(self):
        self.motor()
        self.assertEqual(self.air_errors(), [])
        self.assertEqual([p.text for p in validation.validate(self.study) if "Sliding" in p.text], [])

    def test_valid_3d_linear_slide_has_no_slide_problems(self):
        self.box_slide()
        self.assertEqual(self.air_errors(), [])

    def test_sliding_needs_an_air_region_and_an_interface(self):
        text = "Sliding motion needs an Air Region and at least one Sliding Interface."
        self.sliding(["A"], ["M"])
        self.assertIn(text, self.air_errors())
        objects.make_air_region(self.study, "Box", Center=App.Vector(20, 5, 5), Length=80, Width=30, Height=30)
        self.assertIn(text, self.air_errors())
        objects.make_sliding_interface(self.study, "Linear", NormalAxis="X", Position=15, MotionAxis="Y")
        self.assertNotIn(text, self.air_errors())

    def test_interface_without_movement_is_a_warning(self):
        iface = self.box_slide()
        self.study.Movement = "No movement"
        problems = validation.validate(self.study)
        text = f"Sliding Interface {iface.Label} is not used: the Study has no movement."
        self.assertEqual([p.severity for p in problems if p.text == text], [validation.WARNING])

    def test_sliding_in_a_zx_study_is_an_error(self):
        self.study_2d(App.Vector(0, 1, 0))
        self.study.Movement = "Sliding motion"
        objects.make_air_region(self.study, "Sector", OuterRadius=30)
        objects.make_sliding_interface(self.study, "Rotational", Radius=5)
        self.assertIn("Sliding motion is not supported in a ZX (axisymmetric) Study.", self.air_errors())

    def test_linear_interface_needs_a_box_air(self):
        self.motor()
        (iface,) = objects.sliding_interfaces(self.study)
        iface.Kind, iface.NormalAxis, iface.MotionAxis = "Linear", "Y", "X"
        self.assertIn(f"Sliding Interface {iface.Label}: a Linear interface needs a Box Air Region.", self.air_errors())

    def test_odd_divisions_of_a_full_turn_is_an_error(self):
        self.motor()
        (iface,) = objects.sliding_interfaces(self.study)
        text = (
            f"Sliding Interface {iface.Label}: Divisions must be even for a full 360° interface"
            " (it is meshed in two halves)."
        )
        self.assertNotIn(text, self.air_errors())
        iface.Divisions = 91
        self.assertIn(text, self.air_errors())
        objects.air_regions(self.study)[0].EndAngle = 90  # not a full turn: any count is fine
        self.assertNotIn(text, self.air_errors())

    def test_interfaces_with_the_same_name_are_an_error(self):
        self.motor(extra=(60,))  # both keep the default Label, so both become Sliding_Interface
        text = "These group names are the same after removing special characters: Sliding_Interface."
        self.assertIn(text + " Rename the items or bodies.", self.air_errors())
        objects.sliding_interfaces(self.study)[1].GroupName = "Second"
        self.assertNotIn(text + " Rename the items or bodies.", self.air_errors())

    def test_body_named_like_an_air_side_is_an_error(self):
        _, rotor = self.motor()
        rotor.Label = "Air moving"
        self.assertIn(
            "These group names are the same after removing special characters: Air_moving. Rename the items or bodies.",
            self.air_errors(),
        )

    def test_interface_missing_the_air_is_an_error(self):
        self.motor()
        (iface,) = objects.sliding_interfaces(self.study)
        iface.Radius = 200
        self.assertIn(f"Sliding Interface {iface.Label} does not cut the Air Region.", self.air_errors())

    def test_body_crossing_an_interface_is_an_error(self):
        _, rotor = self.motor(rotor_radius=44)
        hint = " Rotation is about the global Z axis; put the machine axis on Z."
        errors = self.air_errors()
        self.assertIn(f"{rotor.Label} crosses a Sliding Interface." + hint, errors)
        self.assertFalse([t for t in errors if "holds no body" in t])

    def test_crossing_a_linear_interface_has_no_axis_hint(self):
        self.box_slide(moving_x=10)  # M spans x = 10..20 across the plane at x = 15
        self.assertIn("M crosses a Sliding Interface.", self.air_errors())

    def test_body_outside_the_air_is_not_reported_as_crossing(self):
        _, rotor = self.motor(rotor_radius=120)
        errors = self.air_errors()
        self.assertIn(f"{rotor.Label} is not fully inside Air Region Air.", errors)
        self.assertFalse([t for t in errors if "crosses" in t])
        self.assertFalse([t for t in errors if "holds no body" in t or "same side" in t])

    def test_moving_and_fixed_body_on_the_same_side_is_an_error(self):
        stator, rotor = self.motor()
        stator.Shape = self.disc(30)
        rotor.Shape = self.disc(20)
        names = f"Moving body {rotor.Label} and fixed body {stator.Label}"
        self.assertIn(f"{names} are on the same side of the Sliding Interfaces.", self.air_errors())

    def test_air_cell_without_a_body_is_an_error(self):
        stator, _ = self.motor(extra=(60,))  # three cells; the ring between 42.5 and 60 holds nothing
        stator.Shape = self.disc(90, 65)
        inner, outer = objects.sliding_interfaces(self.study)
        text = f"Part of the air next to Sliding Interfaces {inner.Label}, {outer.Label} holds no body; its side is unknown."
        self.assertIn(text + " Move an interface or add the body.", self.air_errors())

    def test_no_body_in_the_moving_geometry_is_an_error(self):
        self.motor()
        self.study.MovingObjects = []
        self.assertIn("No body is in the moving geometry.", self.air_errors())

    def does_not_span(self, iface):
        text = f"Sliding Interface {iface.Label} does not span the Air Region: its surface is cut into pieces by the air boundary."
        return [t for t in self.air_errors() if "does not span" in t], text

    def test_interface_cut_into_pieces_by_the_air_is_an_error(self):
        self.motor()
        air = objects.air_regions(self.study)[0]
        air.AirShape, air.Center, air.Length, air.Width = "Box", App.Vector(0, 0, 0), 100, 100
        (iface,) = objects.sliding_interfaces(self.study)
        iface.Radius = 60  # four arcs inside the square
        found, text = self.does_not_span(iface)
        self.assertEqual(found, [text])

    def test_2d_slide_point_off_the_surface_is_an_error(self):
        self.motor()
        air = objects.air_regions(self.study)[0]
        air.AirShape, air.Center, air.Length, air.Width = "Box", App.Vector(-40, 0, 0), 40, 100
        (iface,) = objects.sliding_interfaces(self.study)
        iface.Radius = 40  # one arc around 180 degrees; the slide point at 0 degrees is outside the air
        found, text = self.does_not_span(iface)
        self.assertEqual(found, [text])

    def test_axial_gap_full_turn_needs_even_divisions_and_two_halves(self):
        air = {"OuterRadius": 100, "Height": 100, "ZMin": -50}
        iface = self.interface("3D", "Sector", air, "Axial gap", Position=20)
        text = f"Sliding Interface {iface.Label}: Divisions must be even for a full 360° interface (it is meshed in two halves)."
        iface.Divisions = 91
        self.assertIn(text, self.air_errors())
        iface.Divisions = 90
        self.assertEqual([t for t in self.air_errors() if "Sliding Interface" in t], [])

    def test_slide_job_2d_sector(self):
        """The 45 degree machine: shaft and rotor move, the stator is fixed, one interface in the gap."""
        self.doc.removeObject(self.study.Name)
        self.study = objects.make_study(self.doc, "2D")
        self.study.MainMode = self.study.MovingMode = "Manual"
        parts = {}
        for name, inner, outer in (("Shaft", 0, 30), ("Rotor", 30, 78), ("Stator", 82, 149)):
            parts[name] = self.doc.addObject("Part::Feature", name)
            parts[name].Shape = airshapes._bottom_face(airshapes._ring_sector(inner, outer, 0, 45, 0, 1), 0)
        self.study.MainObjects = [parts["Stator"]]
        self.study.MovingObjects = [parts["Shaft"], parts["Rotor"]]
        self.study.Movement = "Sliding motion"
        objects.make_air_region(self.study, "Sector", OuterRadius=200, EndAngle=45)
        objects.make_sliding_interface(self.study, "Rotational", Radius=80.575, Divisions=90)
        self.doc.recompute()
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        folder = jobwriter.scratch_folder(self.study)
        self.assertEqual(job["rotor_file"], os.path.join(jobwriter.simulation_folder(self.study), "rotor_mesh2D.msh"))
        self.assertEqual(jobwriter.rotor_file(self.study), job["rotor_file"])
        (slide,) = job["slides"]
        self.assertEqual((slide["divisions"], slide["full"], slide["kind"]), (90, False, "rotational"))
        self.assertNotIn("cross_divisions", slide)
        self.assertEqual(job["periodic"], {"kind": "rotation", "angle": 45.0, "start": 0.0})
        self.assertEqual(job["moving"], [2, 3])  # the stator is 1
        (cell,) = job["moving_cells"]
        self.assertAlmostEqual(Part.read(os.path.join(folder, cell)).Area, math.pi * 80.575**2 / 8)
        for rel in [cell, *slide["files"], slide["marker"]]:
            self.assertTrue(os.path.exists(os.path.join(folder, rel)), rel)

    def slide_job(self):
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        (slide,) = job["slides"]
        marker = Part.read(os.path.join(jobwriter.scratch_folder(self.study), slide["marker"]))
        return job, slide, marker

    def test_slide_job_2d_full_turn(self):
        """A full turn: two half arcs, no period; the slide point is one vertex at 0° on the slide circle."""
        self.motor()
        job, slide, marker = self.slide_job()
        self.assertIs(slide["full"], True)
        self.assertEqual(len(slide["files"]), 2)
        self.assertNotIn("periodic", job)
        self.assertEqual((len(marker.Vertexes), len(marker.Edges)), (1, 0))
        (v,) = marker.Vertexes
        self.assertEqual((v.X, v.Y, v.Z), (pytest.approx(42.5), pytest.approx(0), pytest.approx(0)))

    def test_slide_job_2d_marker_at_start_angle(self):
        """A sector from 30° to 75°: the slide point is one vertex at 30° on the slide circle."""
        stator, rotor = self.motor()
        stator.Shape = airshapes._bottom_face(airshapes._ring_sector(45, 80, 30, 45, 0, 1), 0)
        rotor.Shape = airshapes._bottom_face(airshapes._ring_sector(0, 40, 30, 45, 0, 1), 0)
        air = objects.air_regions(self.study)[0]
        air.StartAngle, air.EndAngle = 30, 75
        self.doc.recompute()
        job, slide, marker = self.slide_job()
        self.assertIs(slide["full"], False)
        self.assertEqual(job["periodic"], {"kind": "rotation", "angle": 45.0, "start": 30.0})
        self.assertEqual((len(marker.Vertexes), len(marker.Edges)), (1, 0))
        (v,) = marker.Vertexes
        a = math.radians(30)
        self.assertEqual((v.X, v.Y, v.Z), (pytest.approx(42.5 * math.cos(a)), pytest.approx(42.5 * math.sin(a)), 0))

    def test_a_moved_placement_does_not_detach_the_air(self):
        """The properties place the air and the slide surface: Placement is hidden and a recompute resets it."""
        iface = self.box_slide()
        air = objects.air_regions(self.study)[0]
        moved = App.Placement(App.Vector(100, 0, 0), App.Rotation())
        for obj in (air, iface):
            self.assertIn("Hidden", obj.getEditorMode("Placement"))
            before = obj.Shape.BoundBox.XMin
            obj.Placement = moved
            self.doc.recompute()
            self.assertEqual(obj.Placement, App.Placement())
            self.assertAlmostEqual(obj.Shape.BoundBox.XMin, before)
        air.Placement = moved  # after the last recompute
        jobwriter.write_job(self.study)
        self.assertAlmostEqual(self.exported_air().XMin, -20)
        self.assertEqual(air.Placement, App.Placement())

    def air_box(self):
        """Box A (0..10) inside a 30 mm Box Air Region, recomputed."""
        self.bodies("A")
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.doc.recompute()
        return air

    def test_mesh_size_on_the_air_is_checked_like_a_body(self):
        air = self.air_box()
        size = objects.make_mesh_size(self.study, 2, [(air, "")])
        self.assertEqual([p.text for p in validation.validate(self.study) if size.Label in p.text], [])
        size.Size = 0
        self.assertIn(f"Mesh size {size.Label} must be greater than 0.", self.air_errors())
        size.Size = 2
        size.References = [(air, "Face99")]
        self.assertIn(f"Mesh Size {size.Label}: body {air.Label} has no Face99. Reselect it.", self.air_errors())
        with self.assertRaisesRegex(jobwriter.StudyError, "has no Face99"):
            jobwriter.write_job(self.study)

    def test_air_cannot_be_recombined_structured_or_excited(self):
        air = self.air_box()
        refused = f"Air Region {air.Label} cannot be recombined or structured."
        items = [
            objects.make_recombine(self.study, [air]),
            objects.make_transfinite_body(self.study, [air]),
            objects.make_transfinite_edges(self.study, 10, [(air, "Edge1")]),
        ]
        errors = self.air_errors()
        for item in items:
            self.assertEqual(objects.air_refusal(type(item.Proxy), [air]), refused)
            self.assertIn(f"{validation._kind(item)} {item.Label}: {refused} Remove it from the item.", errors)
        coil = objects.make_excitation(self.study, "Coil", [(air, "Face1")])
        refused = f"Air Region {air.Label} cannot be an Excitation."
        self.assertIn(f"Excitation {coil.Label}: {refused} Remove it from the item.", self.air_errors())
        self.assertEqual(objects.air_refusal(objects.MeshSize, [air]), "")
        self.assertEqual(objects.air_refusal(objects.Recombine, self.study.MainObjects), "")

    def test_custom_source_in_the_study_geometry_is_an_error(self):
        (a,) = self.bodies("A")
        outer = self.doc.addObject("Part::Box", "OuterBox")
        outer.Length = outer.Width = outer.Height = 40
        outer.Placement.Base = App.Vector(-15, -15, -15)
        self.study.MainObjects = [a, outer]
        air = objects.make_air_region(self.study, "Custom", Source=outer)
        self.doc.recompute()
        text = f"OuterBox is the Custom shape of Air Region {air.Label}; take it out of the main geometry."
        self.assertIn(text, self.air_errors())
        self.study.MainObjects = [a]
        self.assertEqual(self.air_problems(), [])
        self.study.Movement, self.study.MovingMode, self.study.MovingObjects = "Sliding motion", "Manual", [outer]
        text = f"OuterBox is the Custom shape of Air Region {air.Label}; take it out of the moving geometry."
        self.assertIn(text, self.air_errors())

    def test_custom_source_of_the_wrong_kind_is_an_error(self):
        self.bodies("A")
        sheet = self.doc.addObject("Part::Feature", "Sheet")
        sheet.Shape = Part.makePlane(40, 40, App.Vector(-15, -15, 0))
        air = objects.make_air_region(self.study, "Custom", Source=sheet)
        self.assertEqual(self.air_problems(), [f"Air Region {air.Label}: the Custom body Sheet must be a solid."])
        self.study_2d(App.Vector(0, 0, 1))
        solid = self.doc.addObject("Part::Box", "Block")
        solid.Length = solid.Width = 40
        solid.Placement.Base = App.Vector(-15, -15, -5)
        lifted = self.doc.addObject("Part::Feature", "Lifted")
        lifted.Shape = Part.makePlane(40, 40, App.Vector(-15, -15, 5))
        air = objects.make_air_region(self.study, "Custom", Source=solid)
        self.doc.recompute()
        name = objects.display_name(air)  # the 3D Study's Air Region keeps the Label
        for source in (solid, lifted):
            air.Source = source
            text = f"Air Region {name}: the Custom body {source.Label} must be a face in the Study's XY plane."
            self.assertEqual(self.air_problems(), [text])
        sheet.Shape = Part.makePlane(40, 40, App.Vector(-15, -15, 0))
        air.Source = sheet
        self.assertEqual(self.air_problems(), [])

    def test_one_motion_per_study(self):
        first = self.box_slide()  # Linear along Y
        second = objects.make_sliding_interface(self.study, "Linear", NormalAxis="X", Position=-15, MotionAxis="Z")
        text = (
            f"Sliding Interfaces {first.Label}, {second.Label} move in different ways: a Study has one motion,"
            " a rotation about Z (Rotational, Axial gap) or a translation along one axis (Linear)."
        )
        self.assertIn(text, self.air_errors())
        second.MotionAxis = "Y"
        self.assertNotIn(text, self.air_errors())
        second.Kind = "Rotational"
        self.assertIn(text, self.air_errors())

    def test_interface_follows_the_studys_air_region(self):
        self.motor()
        (iface,) = objects.sliding_interfaces(self.study)
        self.doc.removeObject(objects.air_regions(self.study)[0].Name)
        self.assertIsNone(iface.AirRegion)
        air = objects.make_air_region(self.study, "Sector", OuterRadius=100)
        self.assertIs(iface.AirRegion, air)  # linked again
        iface.AirRegion = None
        self.doc.recompute()
        self.assertNotIn("Invalid", iface.State)
        self.assertEqual(len(iface.Shape.Edges), 2)
        self.assertEqual(self.air_errors(), [])
        air.StartAngle = 30
        self.assertEqual(airshapes._start(iface), 30)

    def test_default_interface_kind_follows_the_air_shape(self):
        self.sliding(["A"], ["M"])
        air = objects.make_air_region(self.study, "Box")
        for shape, kind in (("Box", "Linear"), ("Sector", "Rotational"), ("Custom", "Rotational")):
            air.AirShape = shape
            self.assertEqual(objects.make_sliding_interface(self.study).Kind, kind)

    def padded(self, bodies, shape="Box", **props):
        """An Air Region in Padding mode sized by bodies (the Study's main geometry)."""
        self.study.MainObjects = list(bodies)
        air = objects.make_air_region(self.study, shape, **props)
        air.SizeMode = "Padding"
        air.SizedBy = list(bodies)
        self.doc.recompute()
        return air

    def assertSize(self, air, **expected):
        for name, value in expected.items():
            actual = getattr(air, name)
            actual = tuple(actual) if name == "Center" else getattr(actual, "Value", actual)
            want = tuple(pytest.approx(v) for v in value) if name == "Center" else pytest.approx(value)
            self.assertEqual(actual, want, name)

    def test_padded_box_percent_and_mm(self):
        (body,) = self.bodies("B")
        body.Length, body.Width, body.Height = 10, 20, 30
        self.doc.recompute()
        air = self.padded([body], PadXPlusPercent=20, PadXMinus=5, PadZPlusPercent=10, PadZMinusPercent=10)
        self.assertNotIn("Invalid", air.State)
        self.assertSize(air, Center=(3.5, 10, 15), Length=17, Width=20, Height=36)
        box = air.Shape.BoundBox
        self.assertEqual((box.XMin, box.XMax, box.ZMin, box.ZMax), tuple(pytest.approx(v) for v in (-5, 12, -3, 33)))

    def test_padded_rectangle_xy(self):
        body = self.study_2d(App.Vector(0, 0, 1))
        air = self.padded([body], PadXPlusPercent=10, PadXMinus=2, PadYPlusPercent=20, PadYMinusPercent=20)
        self.assertSize(air, Center=(4.5, 5, 0), Length=13, Width=14)
        self.assertEqual(air.Shape.Area, pytest.approx(13 * 14))

    def test_padded_rectangle_zx_left_edge_on_axis(self):
        body = self.study_2d(App.Vector(0, 1, 0))
        body.Shape = Part.makePlane(10, 10, App.Vector(5, 0, 0), App.Vector(0, 1, 0))
        air = self.padded([body], PadXPlusPercent=10, PadXMinusPercent=50, PadZPlus=1, PadZMinus=1)
        self.assertSize(air, Center=(8, 0, 5), Length=16, Width=12)  # x from 0 (not from 5 - padding) to 15 + 1
        self.assertEqual(air.Shape.BoundBox.XMin, pytest.approx(0))

    def ring(self):
        body = self.doc.addObject("Part::Feature", "Ring")
        body.Shape = Part.makeCylinder(50, 10).cut(Part.makeCylinder(30, 10))
        return body

    def test_padded_sector_ring_from_bodies(self):
        air = self.padded(
            [self.ring()], "Sector", StartAngle=10, EndAngle=100, PadOuterPercent=10, PadInner=2, InnerFromBodies=True
        )
        air.PadZPlus = air.PadZMinus = 1
        self.doc.recompute()
        self.assertSize(air, InnerRadius=28, OuterRadius=55, ZMin=-1, Height=12, StartAngle=10, EndAngle=100)

    def test_padded_sector_disc_ignores_inner(self):
        body = self.doc.addObject("Part::Cylinder", "Disc")
        body.Radius, body.Height = 50, 10
        air = self.padded([body], "Sector", PadInner=2, InnerRadius=7, PadZPlus=1)
        self.assertSize(air, InnerRadius=0, OuterRadius=50, ZMin=0, Height=11)
        air.InnerFromBodies = True  # the bodies reach the axis: still a full disc
        self.doc.recompute()
        self.assertSize(air, InnerRadius=0)

    def test_padded_half_disc_zx(self):
        body = self.study_2d(App.Vector(0, 1, 0))
        body.Shape = Part.makePlane(24, 32, App.Vector(0, 0, 10), App.Vector(0, 1, 0))
        air = self.padded([body], "Sector", Center=App.Vector(0, 0, 10), PadOuter=5)
        self.assertSize(air, OuterRadius=45, Center=(0, 0, 10))

    def test_flat_body_without_length_padding_is_an_error(self):
        body = self.doc.addObject("Part::Feature", "Flat")
        body.Shape = Part.makePlane(10, 10)
        air = self.padded([body], PadXPlusPercent=10, PadXMinusPercent=10, PadYPlusPercent=10, PadYMinusPercent=10)
        self.assertIn("Invalid", air.State)
        with self.assertRaises(ValueError) as ctx:
            airshapes.padded_size(air, [body], "3D")
        self.assertEqual(str(ctx.exception), "Air Region Air: padding gives no size along Z; add a length padding.")
        air.PadZPlus = 1
        self.doc.recompute()
        self.assertNotIn("Invalid", air.State)
        self.assertSize(air, Height=1)

    def test_custom_padding_is_an_error(self):
        (body,) = self.bodies("B")
        air = self.padded([body], "Custom", Source=body)
        self.assertIn("Invalid", air.State)
        with self.assertRaises(ValueError) as ctx:
            airshapes.padded_size(air, [body], "3D")
        self.assertEqual(str(ctx.exception), "Air Region Air: Padding is not available for a Custom shape.")

    def test_padding_follows_a_varset_expression(self):
        (body,) = self.bodies("B")
        varset = self.doc.addObject("App::VarSet", "VarSet")
        varset.addProperty("App::PropertyLength", "Gap")
        varset.Gap = 3
        air = self.padded([body])
        air.setExpression("PadXPlus", "VarSet.Gap * 2")
        self.doc.recompute()
        self.assertSize(air, Length=16)
        varset.Gap = 5
        self.doc.recompute()
        self.assertSize(air, Length=20)

    def test_size_properties_read_only_in_padding(self):
        (body,) = self.bodies("B")
        air = objects.make_air_region(self.study, "Box")
        names = ("Center", "Length", "Width", "Height", "InnerRadius", "OuterRadius", "ZMin")
        self.assertEqual(air.SizeMode, "Manual")
        for name in names:
            self.assertNotIn("ReadOnly", air.getEditorMode(name))
        air.SizeMode = "Padding"
        for name in names:
            self.assertIn("ReadOnly", air.getEditorMode(name))
        air.SizeMode = "Manual"
        for name in names:
            self.assertNotIn("ReadOnly", air.getEditorMode(name))
        self.assertEqual(air.getGroupOfProperty("SizeMode"), "Padding")
        self.assertIn("Hidden", air.getEditorMode("SizedBy"))

    def test_old_air_region_opens_manual_with_same_size(self):
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(1, 2, 3), Length=20, Width=10, Height=4)
        for name in objects.PADDING_PROPERTIES:
            air.removeProperty(name)
        self.assertFalse(hasattr(air, "SizeMode"))
        path = os.path.join(self.tmp.name, "old_air.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        (air,) = objects.air_regions(objects.find_study(self.doc))
        self.assertEqual(air.SizeMode, "Manual")
        self.assertEqual(air.PadXPlusPercent, 0)
        self.assertEqual(air.SizedBy, [])
        self.doc.recompute()
        self.assertSize(air, Center=(1, 2, 3), Length=20, Width=10, Height=4)
        self.assertEqual(air.Shape.Volume, pytest.approx(800))

    def padding_air(self, shape="Box", **props):
        """An Air Region made in Padding mode: nothing sets SizedBy by hand."""
        air = objects.make_air_region(self.study, shape, **props)
        air.SizeMode = "Padding"
        self.doc.recompute()
        return air

    def test_air_follows_an_edited_body(self):
        (body,) = self.bodies("B")
        air = self.padding_air(PadXPlus=2)
        self.assertSize(air, Length=12)
        body.Length = 30
        self.doc.recompute()
        self.assertSize(air, Length=32)

    def test_air_grows_when_a_body_joins_main_geometry(self):
        (body,) = self.bodies("B")
        air = self.padding_air()
        self.assertSize(air, Length=10)
        other = self.doc.addObject("Part::Box", "C")
        other.Placement.Base = App.Vector(20, 0, 0)
        self.doc.recompute()  # a body without a shape cannot be listed yet
        self.study.MainObjects = [body, other]
        self.doc.recompute()
        self.assertEqual([o.Name for o in air.SizedBy], ["B", "C"])
        self.assertSize(air, Length=30)
        self.study.MainObjects = [body]
        self.doc.recompute()
        self.assertSize(air, Length=10)

    def test_air_follows_moving_geometry_when_sliding(self):
        self.sliding(["A"], ["M"])
        air = self.padding_air()
        self.assertEqual([o.Name for o in air.SizedBy], ["A", "M"])
        self.assertSize(air, Length=30)
        self.study.Movement = "No movement"
        self.doc.recompute()
        self.assertEqual([o.Name for o in air.SizedBy], ["A"])
        self.assertSize(air, Length=10)

    def test_body_added_to_container_source_is_picked_up_at_validate(self):
        part = self.doc.addObject("App::Part", "Part")
        first = self.doc.addObject("Part::Box", "First")
        part.addObject(first)
        self.study.MainMode, self.study.MainSource = "Container", part
        self.doc.recompute()
        air = self.padding_air()
        self.assertEqual([o.Name for o in air.SizedBy], ["First"])
        second = self.doc.addObject("Part::Box", "Second")
        second.Placement.Base = App.Vector(20, 0, 0)
        part.addObject(second)  # no property of the Study changes
        self.doc.recompute()
        self.assertSize(air, Length=10)
        self.assertEqual(self.air_problems(), [])
        self.assertEqual([o.Name for o in air.SizedBy], ["First", "Second"])
        self.assertSize(air, Length=30)
        self.assertNotIn("Touched", air.State)

    def test_validate_sees_a_body_edited_without_recompute(self):
        (body,) = self.bodies("B")
        air = self.padding_air()
        body.Length = 30
        self.assertEqual(self.air_problems(), [])
        self.assertSize(air, Length=30)

    def test_padding_without_bodies_is_an_error(self):
        air = self.padding_air()
        self.assertEqual(air.SizedBy, [])
        self.assertIn("Air Region Air: Padding needs bodies in the main or moving geometry.", self.air_errors())

    def test_negative_padding_is_an_error(self):
        self.bodies("B")
        air = self.padding_air()
        self.assertEqual(self.air_problems(), [])
        air.PadXMinusPercent = -1
        air.setExpression("PadZPlus", "-2 mm")  # a length property clamps a typed negative, an expression does not
        self.doc.recompute()
        negative = "Air Region Air: padding must not be negative (%s)."
        self.assertEqual(self.air_problems(), [negative % "-X", negative % "+Z"])
        air.PadXMinusPercent = 0
        air.setExpression("PadZPlus", None)
        air.PadZPlus = 0
        self.doc.recompute()
        self.assertEqual(self.air_problems(), [])

    def test_negative_sector_padding_names_outer_and_inner(self):
        self.bodies("B")
        air = self.padding_air("Sector", PadInnerPercent=-5)
        air.setExpression("PadOuter", "-1 mm")
        self.doc.recompute()
        negative = "Air Region Air: padding must not be negative (%s)."
        self.assertEqual(self.air_problems(), [negative % "outer", negative % "inner"])

    def test_padding_without_size_is_reported_like_a_shape_error(self):
        self.bodies("B")
        self.padding_air()
        text = "Air Region Air: padding gives no size along Z; add a length padding."
        with mock.patch.object(airshapes, "padded_size", side_effect=ValueError(text)):  # as for a flat body
            self.assertEqual(self.air_problems(), [text])

    def test_custom_padding_is_reported(self):
        (body,) = self.bodies("B")
        self.padding_air("Custom", Source=body)
        self.assertIn("Air Region Air: Padding is not available for a Custom shape.", self.air_problems())

    def test_manual_air_has_no_sized_by(self):
        (body,) = self.bodies("B")
        air = self.padding_air()
        self.assertEqual(air.SizedBy, [body])
        air.SizeMode = "Manual"
        self.assertEqual(air.SizedBy, [])
        self.study.MainObjects = []
        self.study.MainObjects = [body]
        self.assertEqual(air.SizedBy, [])
        objects.refresh_sized_by(self.study)
        self.assertEqual(air.SizedBy, [])

    def test_sliding_sector_padding_keeps_period(self):
        self.doc.removeObject(self.study.Name)
        self.study = objects.make_study(self.doc, "2D")
        self.study.MainMode = self.study.MovingMode = "Manual"
        parts = {}
        for name, inner, outer in (("Shaft", 0, 30), ("Rotor", 30, 78), ("Stator", 82, 149)):
            parts[name] = self.doc.addObject("Part::Feature", name)
            parts[name].Shape = airshapes._bottom_face(airshapes._ring_sector(inner, outer, 0, 45, 0, 1), 0)
        self.study.MainObjects = [parts["Stator"]]
        self.study.MovingObjects = [parts["Shaft"], parts["Rotor"]]
        self.study.Movement = "Sliding motion"
        air = objects.make_air_region(self.study, "Sector", OuterRadius=200, EndAngle=45)
        objects.make_sliding_interface(self.study, "Rotational", Radius=80.575, Divisions=90)
        self.doc.recompute()
        manual = airshapes.period(self.study)
        self.assertEqual(manual, {"kind": "rotation", "angle": 45.0, "start": 0.0})
        air.SizeMode, air.PadOuter = "Padding", 20
        self.doc.recompute()
        self.assertEqual([o.Name for o in air.SizedBy], ["Stator", "Shaft", "Rotor"])
        self.assertSize(air, OuterRadius=169, InnerRadius=0)
        self.assertEqual(airshapes.period(self.study), manual)
        self.assertEqual(self.air_errors(), [])
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual(job["periodic"], manual)

    def test_padded_half_disc_zx_writes_a_zero_inner_radius(self):
        body = self.study_2d(App.Vector(0, 1, 0))
        body.Shape = Part.makePlane(24, 32, App.Vector(0, 0, 10), App.Vector(0, 1, 0))
        air = objects.make_air_region(self.study, "Sector", Center=App.Vector(0, 0, 10), InnerRadius=7, PadOuter=5)
        air.SizeMode = "Padding"
        self.doc.recompute()
        self.assertSize(air, OuterRadius=45, InnerRadius=0)

    def test_saved_padding_air_keeps_size_properties_read_only(self):
        self.bodies("B")
        self.padding_air(PadXPlus=2)
        path = os.path.join(self.tmp.name, "padding.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        (air,) = objects.air_regions(objects.find_study(self.doc))
        self.assertEqual(air.SizeMode, "Padding")
        for name in objects.SIZE_PROPERTIES:
            self.assertIn("ReadOnly", air.getEditorMode(name), name)
        self.assertEqual([o.Name for o in air.SizedBy], ["B"])
        self.doc.recompute()
        self.assertSize(air, Length=12)

    def test_body_that_depends_on_the_air_cannot_size_it(self):
        body, other = self.bodies("B", "Other")
        other.Placement.Base = App.Vector(20, 0, 0)
        air = objects.make_air_region(self.study, "Box")
        body.setExpression("Height", "Air.Height / 10")  # B now depends on the air: it must not be linked back
        self.doc.recompute()
        air.SizeMode = "Padding"
        self.doc.recompute()
        self.assertEqual(air.SizedBy, [])  # no link closes a cycle, and none hides Other as an input of B
        text = "Air Region Air: body B depends on the Air Region; it cannot size it."
        for _ in range(2):  # stable: validating again changes nothing
            self.assertEqual(self.air_problems(), [text])
            self.assertEqual(air.SizedBy, [])
        self.assertEqual([b.Name for b in objects.study_bodies(self.study)], ["B", "Other"])
        body.setExpression("Height", None)
        self.doc.recompute()
        self.assertEqual(self.air_problems(), [])
        self.assertEqual([o.Name for o in air.SizedBy], ["B", "Other"])

    def test_padding_sides_by_shape_and_plane(self):
        def keys(shape, plane):
            return [key for key, _ in airshapes.padding_sides(shape, plane)]

        self.assertEqual(keys("Box", "3D"), ["XPlus", "XMinus", "YPlus", "YMinus", "ZPlus", "ZMinus"])
        self.assertEqual(keys("Box", "XY"), ["XPlus", "XMinus", "YPlus", "YMinus"])
        self.assertEqual(keys("Box", "ZX"), ["XPlus", "ZPlus", "ZMinus"])
        self.assertEqual(keys("Sector", "3D"), ["Outer", "Inner", "ZPlus", "ZMinus"])
        self.assertEqual(keys("Sector", "XY"), ["Outer", "Inner"])
        self.assertEqual(keys("Sector", "ZX"), ["Outer"])
        self.assertEqual(keys("Custom", "3D"), [])
        air = objects.make_air_region(self.study, "Box")
        for shape, plane in (("Box", "3D"), ("Sector", "3D"), ("Sector", "ZX")):
            for key in keys(shape, plane):
                self.assertTrue(hasattr(air, f"Pad{key}Percent") and hasattr(air, f"Pad{key}"), key)

    def test_padding_air_made_before_a_body_is_recomputed(self):
        fresh = self.doc.addObject("Part::Box", "Fresh")  # not recomputed: no shape yet
        self.study.MainObjects = [fresh]
        with mock.patch.object(App.Console, "PrintWarning") as warning:
            air = objects.make_air_region(self.study, "Box", SizeMode="Padding")
            self.assertTrue(warning.called, "the failure was swallowed silently")
            self.assertIn(air, objects.air_regions(self.study))  # the Air Region is not left half made
            self.assertEqual((air.SizeMode, air.SizedBy), ("Padding", []))
            warning.reset_mock()
            air.SizeMode = "Manual"
            self.assertFalse(warning.called)
            air.SizeMode = "Padding"  # the SizeMode change does not raise either
            self.assertTrue(warning.called)
        self.doc.recompute()
        self.assertEqual(self.air_problems(), [])  # Validate refreshes again
        self.assertEqual([o.Name for o in air.SizedBy], ["Fresh"])

    def nested_parts(self):
        """B in an inner App::Part in an outer one, the outer the Study's main container; a Padding air."""
        outer, inner = self.doc.addObject("App::Part", "Outer"), self.doc.addObject("App::Part", "Inner")
        body = self.doc.addObject("Part::Box", "B")
        outer.addObject(inner)
        inner.addObject(body)
        self.study.MainMode, self.study.MainSource = "Container", outer
        self.doc.recompute()
        air = self.padding_air()
        self.assertSize(air, Center=(5, 5, 5))
        return outer, inner, air

    def test_air_follows_a_moved_container(self):
        outer, inner, air = self.nested_parts()
        inner.Placement.Base = App.Vector(100, 0, 0)  # neither the body nor its link changes
        self.doc.recompute()
        self.assertSize(air, Center=(105, 5, 5))
        outer.Placement.Base = App.Vector(0, 50, 0)
        self.doc.recompute()
        self.assertSize(air, Center=(105, 55, 5))
        self.assertNotIn("Touched", air.State)
        self.assertEqual(self.air_problems(), [])

    def test_validate_follows_a_moved_container_it_was_not_told_about(self):
        _, inner, air = self.nested_parts()
        inner.Placement.Base = App.Vector(100, 0, 0)
        inner.purgeTouched()  # as if the move reached no link: the sizes differ from the padding all the same
        self.assertEqual(self.air_problems(), [])
        self.assertSize(air, Center=(105, 5, 5))

    def test_run_mesh_follows_a_moved_container(self):
        _, inner, air = self.nested_parts()
        inner.Placement.Base = App.Vector(100, 0, 0)
        inner.purgeTouched()
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            json.load(fh)
        self.assertSize(air, Center=(105, 5, 5))

    def test_container_that_depends_on_the_air_is_not_linked(self):
        part = self.doc.addObject("App::Part", "Part")
        body, reader = self.doc.addObject("Part::Box", "B"), self.doc.addObject("Part::Box", "Reader")
        part.addObject(body)
        part.addObject(reader)
        self.study.MainObjects = [body]
        self.doc.recompute()
        air = objects.make_air_region(self.study, "Box")
        reader.setExpression("Height", "Air.Height / 10")  # the Part now depends on the air through Reader
        self.doc.recompute()
        air.SizeMode = "Padding"
        self.doc.recompute()
        self.assertEqual([o.Name for o in air.SizedBy], ["B"])
        self.assertEqual(air.SizedByContainers, [])
        self.assertNotIn("Invalid", air.State)
        self.assertEqual(self.air_problems(), [])

    def test_manual_air_links_no_container(self):
        _, _, air = self.nested_parts()
        self.assertEqual([o.Name for o in air.SizedByContainers], ["Inner", "Outer"])
        self.assertIn("Hidden", air.getEditorMode("SizedByContainers"))
        air.SizeMode = "Manual"
        self.assertEqual(air.SizedByContainers, [])

    def test_air_names_a_body_that_depends_on_it(self):
        (body,) = self.bodies("B")
        air = objects.make_air_region(self.study, "Box")
        body.setExpression("Height", "Air.Height / 10")
        self.doc.recompute()
        air.SizeMode = "Padding"
        self.doc.recompute()
        self.assertIn("Invalid", air.State)
        self.assertEqual(air.getStatusString(), "Air Region Air: body B depends on the Air Region; it cannot size it.")

    def test_reopened_old_air_region_is_not_touched(self):
        objects.make_air_region(self.study, "Box", Length=20)
        self.doc.recompute()
        (air,) = objects.air_regions(self.study)
        for name in objects.PADDING_PROPERTIES:
            air.removeProperty(name)
        path = os.path.join(self.tmp.name, "old_touch.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        (air,) = objects.air_regions(objects.find_study(self.doc))
        self.assertTrue(hasattr(air, "SizeMode"))
        self.assertNotIn("Touched", air.State)

    def test_padding_drops_the_formulas_of_the_sizes_it_writes(self):
        self.bodies("B")
        air = objects.make_air_region(self.study, "Box")
        air.setExpression("Length", "3 mm * 7")
        air.setExpression("Center.x", "3 mm")
        air.setExpression("PadXPlus", "1 mm")  # a padding formula stays
        self.doc.recompute()
        with mock.patch.object(App.Console, "PrintMessage") as message:
            air.SizeMode = "Padding"
        self.assertEqual([path for path, _ in air.ExpressionEngine], ["PadXPlus"])
        text = message.call_args[0][0]
        self.assertIn("Air Region Air", text)
        self.assertIn("Center", text)
        self.assertIn("Length", text)
        self.doc.recompute()
        self.assertSize(air, Length=11, Center=(5.5, 5, 5))

    def test_padding_keeps_the_formulas_of_manual_sector_values(self):
        self.bodies("B")
        air = objects.make_air_region(self.study, "Sector")
        air.setExpression("EndAngle", "45 deg * 2")
        air.setExpression("OuterRadius", "70 mm")
        self.doc.recompute()
        with mock.patch.object(App.Console, "PrintMessage"):
            air.SizeMode = "Padding"
        self.assertEqual([path for path, _ in air.ExpressionEngine], ["EndAngle"])
        with mock.patch.object(App.Console, "PrintMessage") as message:
            air.SizeMode = "Manual"
            air.SizeMode = "Padding"  # nothing left to drop: no message
        self.assertFalse(message.called)

    def test_padding_keeps_the_centre_z_formula_of_a_zx_half_disc(self):
        self.study_2d(App.Vector(0, 1, 0))
        air = objects.make_air_region(self.study, "Sector")
        air.setExpression("Center.z", "4 mm")
        air.setExpression("OuterRadius", "70 mm")
        self.doc.recompute()
        with mock.patch.object(App.Console, "PrintMessage"):
            air.SizeMode = "Padding"
        self.assertEqual([path for path, _ in air.ExpressionEngine], [".Center.z"])

    def test_validate_recomputes_only_what_the_air_depends_on(self):
        (body,) = self.bodies("B")
        air = self.padding_air()
        other = self.doc.addObject("Part::Box", "Unrelated")
        self.doc.recompute()
        body.Length, other.Length = 30, 40
        self.assertEqual(self.air_problems(), [])
        self.assertSize(air, Length=30)
        self.assertIn("Touched", other.State)

    def test_seed_padding_for_the_sides_a_shape_change_brings(self):
        air = objects.make_air_region(self.study, "Box")
        airshapes.seed_padding(air, "Custom", "Box", "3D")  # a new Box: 20 % on every side
        sides = [key for key, _ in airshapes.padding_sides("Box", "3D")]
        self.assertEqual([getattr(air, f"Pad{s}Percent") for s in sides], [20] * 6)
        airshapes.seed_padding(air, "Box", "Sector", "3D")  # the radial sides are new: 20 % on the outer one
        self.assertEqual((air.PadOuterPercent, air.PadInnerPercent), (20, 0))
        air.PadOuterPercent, air.PadOuter = 0, 3
        air.PadXPlusPercent = air.PadXMinusPercent = air.PadYPlusPercent = air.PadYMinusPercent = 0
        air.PadYPlus = 1
        airshapes.seed_padding(air, "Box", "Sector", "3D")  # a padding of its own: kept
        self.assertEqual((air.PadOuterPercent, air.PadOuter.Value), (0, 3))
        airshapes.seed_padding(air, "Sector", "Box", "3D")
        self.assertEqual((air.PadXPlusPercent, air.PadYPlus.Value), (0, 1))
        airshapes.seed_padding(air, "Box", "Box", "3D")  # no new sides
        self.assertEqual(air.PadXPlusPercent, 0)

    def test_padded_properties_are_what_padded_size_writes(self):
        (body,) = self.bodies("B")
        air = objects.make_air_region(self.study, "Box")
        for shape, plane in (("Box", "3D"), ("Box", "XY"), ("Box", "ZX"), ("Sector", "3D"), ("Sector", "XY")):
            air.AirShape = shape
            size = airshapes.padded_size(air, [body], plane)
            self.assertEqual(sorted(airshapes.padded_properties(shape, plane)), sorted(size), (shape, plane))
        air.AirShape = "Sector"
        size = airshapes.padded_size(air, [body], "ZX")  # InnerRadius 0: a half disc; its centre z stays manual
        self.assertEqual(sorted(airshapes.padded_properties("Sector", "ZX")), sorted(size))
        self.assertEqual(airshapes.padded_properties("Custom", "3D"), [])

    def test_validate_leaves_a_formula_reading_the_air_alone(self):
        self.bodies("B")
        air = self.padding_air()
        varset = self.doc.addObject("App::VarSet", "VarSet")
        varset.addProperty("App::PropertyLength", "AirLength")
        varset.setExpression("AirLength", "Air.Length")
        self.doc.recompute()
        for _ in range(2):  # the VarSet depends on the air, but no body does: the links stay as they are
            self.assertEqual(self.air_problems(), [])
            self.assertEqual([o.Name for o in air.SizedBy], ["B"])
            self.assertEqual([o.Name for o in self.doc.Objects if "Touched" in o.State], [])
