"""Air Region item and its shapes. Run from the repo root: pixi run pytest tests/freecad_addon/test_air.py"""

import json
import math
import os
import tempfile
import unittest

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

    def test_fit_box_adds_padding(self):
        a = self.doc.addObject("Part::Box", "A")
        b = self.doc.addObject("Part::Box", "B")
        a.Length = a.Width = a.Height = b.Length = b.Width = b.Height = 10
        b.Placement.Base = App.Vector(10, 0, 0)
        self.doc.recompute()
        center, length, width, height = airshapes.fit_box([a, b], 50, "3D")
        self.assertEqual((center.x, center.y, center.z), tuple(pytest.approx(v) for v in (10, 5, 5)))
        self.assertEqual((length, width, height), tuple(pytest.approx(v) for v in (40, 20, 20)))

    def test_fit_box_2d_has_no_height(self):
        body = self.study_2d(App.Vector(0, 1, 0))
        center, length, width, height = airshapes.fit_box([body], 10, "ZX")
        self.assertEqual((center.x, center.y, center.z), tuple(pytest.approx(v) for v in (5, 0, 5)))
        self.assertEqual((length, width, height), tuple(pytest.approx(v) for v in (12, 12, 0)))

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
        text = "Part of the air between Sliding Interfaces holds no body; its side is unknown."
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
