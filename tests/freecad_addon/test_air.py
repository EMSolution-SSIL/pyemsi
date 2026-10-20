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
        self.study.Movement = "No movement"
        objects.update_ids(self.study)
        rows = {r[2][0]: r[2] for r in objects.material_rows(self.study)}
        self.assertEqual(rows["Air"][2], self.study.MatIds[air.Name])

    def test_sliding_with_air_is_not_written_yet(self):
        self.sliding(["A"], ["M"])
        objects.make_air_region(self.study, "Box", Center=App.Vector(20, 5, 5), Length=80, Width=30, Height=30)
        with self.assertRaisesRegex(jobwriter.StudyError, "Sliding-motion meshing with an Air Region is not complete"):
            jobwriter.write_job(self.study)
