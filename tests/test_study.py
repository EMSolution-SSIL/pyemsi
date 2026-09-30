"""Study, ID table and job writer tests. Run from the repo root with FreeCAD's python.exe:
    python.exe -m unittest tests.test_study -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

_BIN = os.path.dirname(sys.executable)
sys.path[:0] = [_BIN, os.path.join(_BIN, "..", "lib")]

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402

from emsolution import jobwriter, objects  # noqa: E402

MESHER = os.path.join(os.path.dirname(__file__), "..", "emsolution", "mesher.py")


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

    def assertStudyError(self, text):
        with self.assertRaises(jobwriter.StudyError) as ctx:
            jobwriter.check(self.study)
        self.assertIn(text, str(ctx.exception))

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

    # --- checks ------------------------------------------------------------

    def test_check_no_materials(self):
        self.assertStudyError("no materials")

    def test_check_two_materials(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_material(self.study, "Iron", [a])
        self.assertStudyError("more than one material")

    def test_check_not_one_solid(self):
        two = self.doc.addObject("Part::Feature", "Two")
        two.Shape = Part.makeCompound([Part.makeBox(1, 1, 1),
                                       Part.makeBox(1, 1, 1, App.Vector(5, 0, 0))])
        objects.make_material(self.study, "Copper", [two])
        self.assertStudyError("exactly one solid")

    def test_check_excitation_on_body_without_material(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_excitation(self.study, "T", [(b, "Face1")])
        self.assertStudyError("which has no material")

    def test_check_mesh_size_on_body_without_material(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 1.0, [b])
        self.assertStudyError("mesh size but no material")

    def test_check_zero_size(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 0.0, [a])
        self.assertStudyError("greater than 0")

    def test_check_missing_face(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face60")])  # a box has 6 faces
        self.assertStudyError("has no Face60")

    def test_check_unsaved_document(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        self.study.OutputFolder = ""
        with self.assertRaises(jobwriter.StudyError) as ctx:
            jobwriter.write_job(self.study)
        self.assertIn("Save the document", str(ctx.exception))

    def test_smallest_mesh_size_wins(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 3.0, [a])
        objects.make_mesh_size(self.study, 2.0, [a])
        volumes, _ = jobwriter.check(self.study)
        self.assertEqual(volumes[0][2], 2.0)

    def test_names_equal_after_cleanup_are_refused(self):
        a = self.box("A")
        b = self.box("B", 10)
        b.Label = "A!"   # cleans to "A_"
        a.Label = "A?"   # cleans to "A_" too
        objects.make_material(self.study, "Cu", [a, b])
        self.assertStudyError("Cu_A_")

    # --- geometry and job file ----------------------------------------------

    def test_body_in_app_part_is_exported_in_global_coordinates(self):
        part = self.doc.addObject("App::Part", "Part")
        part.Placement.Base = App.Vector(100, 0, 0)
        a = self.box("A")
        a.Placement.Base = App.Vector(0, 50, 0)
        part.addObject(a)
        self.doc.recompute()
        objects.make_material(self.study, "Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face6")])  # top face, z = 10
        jobwriter.write_job(self.study)
        vol = Part.Shape()
        vol.read(os.path.join(self.tmp.name, "geometry", "vol_1.brep"))
        self.assertEqual((vol.BoundBox.XMin, vol.BoundBox.YMin), (100, 50))
        face = Part.Shape()
        face.read(os.path.join(self.tmp.name, "geometry", "surf_1001_1.brep"))
        self.assertAlmostEqual(face.BoundBox.XMin, 100)
        self.assertAlmostEqual(face.BoundBox.ZMin, 10)

    def test_job_json_contents(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_material(self.study, "Air", [b])
        objects.make_excitation(self.study, "Terminal In", [(a, "Face1"), (a, "Face2")])
        objects.make_mesh_size(self.study, 2.0, [a])
        self.study.Label = "My Study"
        path = jobwriter.write_job(self.study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual(job, {
            "model_name": "My_Study", "msh_version": 4.1,
            "volumes": [
                {"id": 1, "name": "Copper_A", "file": "geometry/vol_1.brep", "size": 2.0},
                {"id": 2, "name": "Air_B", "file": "geometry/vol_2.brep", "size": 5.0}],
            "surfaces": [
                {"id": 1001, "name": "Terminal_In_A", "volume_id": 1,
                 "files": ["geometry/surf_1001_1.brep", "geometry/surf_1001_2.brep"]}]})
        for rel in ("vol_1.brep", "vol_2.brep", "surf_1001_1.brep", "surf_1001_2.brep"):
            self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "geometry", rel)))

    def test_written_job_meshes(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_material(self.study, "Air", [b])
        objects.make_excitation(self.study, "T", [(a, "Face1")])  # x = 0 face
        self.study.DefaultMeshSize = 4.0
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "Study.msh")))


if __name__ == "__main__":
    unittest.main()
