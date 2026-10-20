"""Air Region item and its shapes. Run from the repo root: pixi run pytest tests/freecad_addon/test_air.py"""

import math
import os
import tempfile
import unittest

import FreeCAD as App
import Part
import pytest

from emsolution import airshapes, objects


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
