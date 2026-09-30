"""Study, ID table and job writer tests. Run from the repo root with FreeCAD's python.exe:
    python.exe -m unittest tests.test_study -v
"""
import os
import sys
import tempfile
import unittest

_BIN = os.path.dirname(sys.executable)
sys.path[:0] = [_BIN, os.path.join(_BIN, "..", "lib")]

import FreeCAD as App  # noqa: E402

from emsolution import objects  # noqa: E402


class StudyTest(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("T")
        self.tmp = tempfile.TemporaryDirectory()
        self.study = objects.make_study(self.doc)
        self.study.OutputFolder = self.tmp.name

    def tearDown(self):
        App.closeDocument(self.doc.Name)
        self.tmp.cleanup()

    def box(self, name, x=0.0, size=10.0):
        b = self.doc.addObject("Part::Box", name)
        b.Length = b.Width = b.Height = size
        b.Placement.Base = App.Vector(x, 0, 0)
        self.doc.recompute()
        return b

    def ids(self):
        return dict(self.study.VolumeIds), dict(self.study.SurfaceIds)

    # --- IDs ---------------------------------------------------------------

    def test_ids_follow_tree_order_and_stay_after_adding_a_body(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        objects.make_material(self.study, "Copper", [b, a])
        objects.make_material(self.study, "Iron", [c])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "1", "A": "2", "C": "3"})
        d = self.box("D", 30)
        objects.make_material(self.study, "Air", [d])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "1", "A": "2", "C": "3", "D": "4"})

    def test_surface_ids_one_per_excitation_and_body(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a, b])
        objects.make_excitation(self.study, "Terminal", [(a, "Face1"), (a, "Face2"), (b, "Face1")])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[1], {"Excitation|A": "1001", "Excitation|B": "1002"})

    def test_rename_keeps_id_and_changes_name(self):
        a = self.box("A")
        mat = objects.make_material(self.study, "Copper", [a])
        objects.update_ids(self.study)
        a.Label = "Coil"
        mat.Label = "Iron"
        objects.update_ids(self.study)
        self.assertEqual(objects.id_rows(self.study), [("VolumeIds", "A", "Iron_Coil", 1)])

    def test_deleted_body_id_is_not_reused(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a, b])
        objects.update_ids(self.study)
        self.doc.removeObject("B")
        c = self.box("C", 20)
        objects.materials(self.study)[0].References += [c]
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"A": "1", "C": "3"})

    def test_set_id_refuses_duplicates_and_raises_counter(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a, b])
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        with self.assertRaises(ValueError):
            objects.set_id(self.study, "VolumeIds", "A", 2)
        with self.assertRaises(ValueError):
            objects.set_id(self.study, "VolumeIds", "A", 1001)
        objects.set_id(self.study, "VolumeIds", "A", 50)
        self.assertEqual(self.study.NextVolumeId, 51)
        c = self.box("C", 20)
        objects.materials(self.study)[0].References += [c]
        objects.update_ids(self.study)
        self.assertEqual(self.study.VolumeIds["C"], "51")

    def test_new_volume_ids_skip_numbers_used_by_surfaces(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        objects.set_id(self.study, "SurfaceIds", "Excitation|A", 2)
        objects.materials(self.study)[0].References += [b]
        objects.update_ids(self.study)
        self.assertEqual(self.study.VolumeIds["B"], "3")

    # --- tree objects ------------------------------------------------------

    def test_pad_face_resolves_to_body(self):
        body = self.doc.addObject("PartDesign::Body", "Body")
        cube = body.newObject("PartDesign::AdditiveBox", "Cube")
        self.doc.recompute()
        self.assertEqual(objects.owning_body(cube).Name, "Body")
        self.assertEqual(objects.owning_body(body).Name, "Body")

    def test_study_survives_save_and_reload(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.update_ids(self.study)
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        self.assertIsNotNone(study)
        self.assertIsInstance(objects.materials(study)[0].Proxy, objects.Material)
        self.assertEqual(study.VolumeIds, {"A": "1"})


if __name__ == "__main__":
    unittest.main()
