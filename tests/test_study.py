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

    def test_group_names_keep_the_typed_name_when_freecad_renames_the_label(self):
        air, a, b = self.box("Air"), self.box("A", 10), self.box("B", 20)
        objects.make_material(self.study, "Air", [air])  # label taken by the body: Air001
        objects.make_material(self.study, "Copper", [a])
        objects.make_material(self.study, "Copper", [b])  # label taken: Copper001
        objects.update_ids(self.study)
        names = ["Air_Air", "Copper_A", "Copper_B"]
        self.assertEqual([r[2] for r in objects.id_rows(self.study)], names)
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        self.assertEqual([r[2] for r in objects.id_rows(study)], names)

    # --- tree objects ------------------------------------------------------

    def test_pad_face_resolves_to_body(self):
        body = self.doc.addObject("PartDesign::Body", "Body")
        cube = body.newObject("PartDesign::AdditiveBox", "Cube")
        self.doc.recompute()
        self.assertEqual(objects.owning_body(cube).Name, "Body")
        self.assertEqual(objects.owning_body(body).Name, "Body")

    def test_only_solid_bodies_can_be_picked(self):
        body = self.doc.addObject("PartDesign::Body", "Body")
        cube = body.newObject("PartDesign::AdditiveBox", "Cube")
        box = self.box("A")
        mat = objects.make_material(self.study, "Copper", [box])
        part = self.doc.addObject("App::Part", "Part")
        self.assertEqual(objects.pick_body(cube).Name, "Body")
        self.assertEqual(objects.pick_body(box).Name, "A")
        # a material linking to its own folder would be a loop in the document
        for obj in (self.study, self.study.MaterialsGroup, mat, part):
            self.assertIsNone(objects.pick_body(obj), obj.Name)

    def test_items_may_link_to_bodies_inside_a_part(self):
        # plain links may not reach into an App::Part; FreeCAD warns on every recompute
        items = [objects.make_material(self.study, "Copper", []),
                 objects.make_excitation(self.study, "In", []),
                 objects.make_mesh_size(self.study, 1.0, [])]
        for item in items:
            self.assertTrue(item.getTypeIdOfProperty("References").endswith("Global"), item.Name)

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

    def test_folders_keep_their_names(self):
        folder = self.study.MaterialsGroup
        folder.Label = "Stuff"
        self.assertEqual(folder.Label, "Materials")
        self.assertEqual([f.Label for f in self.study.Group],
                         ["Materials", "Excitations", "Mesh Sizes"])

    def test_old_plain_folders_are_converted_on_load(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 2.0, [(a, "")])
        for prop, cls in objects.FOLDERS:  # as written by earlier versions
            new = getattr(self.study, prop)
            items = new.Group
            new.Group = []
            self.study.removeObject(new)
            self.doc.removeObject(new.Name)
            old = self.doc.addObject("App::DocumentObjectGroup", prop.replace("Group", ""))
            old.Label = cls.LABEL
            old.Group = items
            self.study.addObject(old)
            setattr(self.study, prop, old)
        self.study.addProperty("App::PropertyLength", "DefaultMeshSize", "EMSolution", "")
        self.study.DefaultMeshSize = 3.0
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        for prop, cls in objects.FOLDERS:
            self.assertIsInstance(getattr(study, prop).Proxy, cls)
        self.assertEqual([f.Label for f in study.Group], ["Materials", "Excitations", "Mesh Sizes"])
        self.assertEqual(objects.materials(study)[0].Label, "Copper")
        self.assertEqual(len(objects.mesh_sizes(study)), 1)
        self.assertFalse(hasattr(study, "DefaultMeshSize"))
        self.assertEqual(study.MeshSizesGroup.DefaultMeshSize.Value, 3.0)
        self.assertEqual(len([o for o in self.doc.Objects if o.TypeId == "App::DocumentObjectGroup"]), 0)

    def test_folder_overview_rows(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        mat = objects.make_material(self.study, "Copper", [a, b])
        empty = objects.make_material(self.study, "Iron", [])
        exc = objects.make_excitation(self.study, "In", [(a, "Face1"), (a, "Face2")])
        size = objects.make_mesh_size(self.study, 1.5, [(a, ""), (c, "Edge1")])
        objects.update_ids(self.study)
        self.assertEqual(objects.material_rows(self.study), [
            (mat, ["Copper", "A", "1"]), (mat, ["Copper", "B", "2"]), (empty, ["Iron", "", ""])])
        self.assertEqual(objects.excitation_rows(self.study),
                         [(exc, ["In", "A", "Face1, Face2", "1001"])])
        self.assertEqual(objects.mesh_size_rows(self.study),
                         [(size, ["MeshSize", "1.5 mm", "A, C.Edge1"])])
        self.assertEqual([x.Name for x in objects.bodies_without_material(self.study)], ["C"])
        d = self.box("D", 30)
        mat.References += [d]
        self.assertEqual(objects.material_rows(self.study)[2], (mat, ["Copper", "D", "–"]))

    def test_mesh_settings_go_to_the_job(self):
        objects.make_material(self.study, "Copper", [self.box("A")])
        settings = self.study.MeshSizesGroup
        settings.SurfaceAlgorithm = "Delaunay"
        settings.VolumeAlgorithm = "HXT"
        settings.SizeFactor = 0.5
        settings.MinSize = 0.1
        settings.MaxSize = 2.0
        settings.SmoothingSteps = 3
        settings.OptimizeNetgen = True
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["options"], {
                "Mesh.Algorithm": 5, "Mesh.Algorithm3D": 10, "Mesh.MeshSizeFactor": 0.5,
                "Mesh.Smoothing": 3, "Mesh.OptimizeNetgen": 1,
                "Mesh.MeshSizeMin": 0.1, "Mesh.MeshSizeMax": 2.0})

    # --- checks ------------------------------------------------------------

    def test_check_min_size_above_max_size(self):
        objects.make_material(self.study, "Copper", [self.box("A")])
        self.study.MeshSizesGroup.MinSize = 3.0
        self.study.MeshSizesGroup.MaxSize = 2.0
        self.assertStudyError("larger than the maximum")

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
        objects.make_mesh_size(self.study, 1.0, [(b, "")])
        self.assertStudyError("mesh size but no material")

    def test_check_zero_size(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 0.0, [(a, "")])
        self.assertStudyError("greater than 0")

    def test_check_missing_face(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face60")])  # a box has 6 faces
        self.assertStudyError("has no Face60")

    def test_check_part_container_is_refused(self):
        part = self.doc.addObject("App::Part", "Part")
        part.addObject(self.box("A"))
        objects.make_material(self.study, "Copper", [part])
        self.assertStudyError("Part is not a solid body")

    def test_check_link_is_refused(self):
        link = self.doc.addObject("App::Link", "Link")
        link.LinkedObject = self.box("A")
        objects.make_material(self.study, "Copper", [link])
        self.assertStudyError("Link is not a solid body")

    def test_output_folder_with_persian_letters(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        self.study.OutputFolder = os.path.join(self.tmp.name, "مدل")
        path = jobwriter.write_job(self.study)
        self.assertTrue(os.path.exists(path))

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
        objects.make_mesh_size(self.study, 3.0, [(a, "")])
        objects.make_mesh_size(self.study, 2.0, [(a, "")])
        volumes = jobwriter.check(self.study)[0]
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
        objects.make_mesh_size(self.study, 2.0, [(a, "")])
        self.study.Label = "My Study"
        path = jobwriter.write_job(self.study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual(job, {
            "model_name": "My_Study", "msh_version": 4.1,
            "options": {"Mesh.Algorithm": 6, "Mesh.Algorithm3D": 1, "Mesh.MeshSizeFactor": 1.0,
                        "Mesh.Smoothing": 1, "Mesh.OptimizeNetgen": 0},
            "volumes": [
                {"id": 1, "name": "Copper_A", "file": "geometry/vol_1.brep", "size": 2.0},
                {"id": 2, "name": "Air_B", "file": "geometry/vol_2.brep", "size": 5.0}],
            "surfaces": [
                {"id": 1001, "name": "Terminal_In_A", "volume_id": 1,
                 "files": ["geometry/surf_1001_1.brep", "geometry/surf_1001_2.brep"]}],
            "sizes": []})
        for rel in ("vol_1.brep", "vol_2.brep", "surf_1001_1.brep", "surf_1001_2.brep"):
            self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "geometry", rel)))

    def test_face_edge_and_vertex_sizes_go_to_the_job(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a, b])
        objects.make_mesh_size(self.study, 1.0, [(a, "Face6"), (a, "Edge1"), (b, "Vertex1")])
        objects.make_mesh_size(self.study, 2.0, [(a, "")])
        path = jobwriter.write_job(self.study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        # only the whole-body item sets a body size
        self.assertEqual([v["size"] for v in job["volumes"]], [2.0, 5.0])
        self.assertEqual(job["sizes"], [
            {"name": "MeshSize", "size": 1.0,
             "files": ["geometry/size_1_1.brep", "geometry/size_1_2.brep"]},
            {"name": "MeshSize", "size": 1.0, "files": ["geometry/size_2_1.brep"]}])
        vertex = Part.Shape()
        vertex.read(os.path.join(self.tmp.name, "geometry", "size_2_1.brep"))
        self.assertEqual(vertex.ShapeType, "Vertex")
        self.assertEqual(vertex.Vertexes[0].Point, b.Shape.Vertex1.Point)

    def test_check_missing_edge(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 1.0, [(a, "Edge99")])  # a box has 12 edges
        self.assertStudyError("has no Edge99")

    def test_old_mesh_size_with_body_list_is_converted_on_load(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        old = objects.make_mesh_size(self.study, 2.0, [])
        old.removeProperty("References")  # as written by earlier versions
        old.addProperty("App::PropertyLinkListGlobal", "References", "EMSolution", "")
        old.References = [a]
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        size, = objects.mesh_sizes(objects.find_study(self.doc))
        self.assertEqual(size.getTypeIdOfProperty("References"), "App::PropertyLinkSubListGlobal")
        self.assertEqual(size.References, [(self.doc.A, ("",))])
        volumes = jobwriter.check(objects.find_study(self.doc))[0]
        self.assertEqual(volumes[0][2], 2.0)

    def test_written_job_meshes(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_material(self.study, "Air", [b])
        objects.make_excitation(self.study, "T", [(a, "Face1")])  # x = 0 face
        objects.make_mesh_size(self.study, 1.0, [(a, "Face1"), (a, "Edge1"), (b, "Vertex8")])
        settings = self.study.MeshSizesGroup
        settings.DefaultMeshSize = 4.0
        settings.VolumeAlgorithm = "HXT"
        settings.SizeFactor = 0.8
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "Study.msh")))


if __name__ == "__main__":
    unittest.main()
