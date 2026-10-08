"""Study, ID table and job writer tests. Run from the repo root: pixi run pytest tests/freecad_addon/test_study.py"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

import FreeCAD as App
import Part

from emsolution import geometry, jobwriter, objects

MESHER = os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution", "mesher.py")


class StudyTest(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("T")
        self.tmp = tempfile.TemporaryDirectory()
        self.study = objects.make_study(self.doc)
        self.study.MainMode = "Materials"  # retain coverage of the legacy workflow
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
        self.assertEqual(objects.id_rows(self.study), [("VolumeIds", "A", "Coil", 1)])

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
        names = ["Air", "A", "B"]
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
        items = [
            objects.make_material(self.study, "Copper", []),
            objects.make_excitation(self.study, "In", []),
            objects.make_mesh_size(self.study, 1.0, []),
        ]
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
        self.assertEqual([f.Label for f in self.study.Group], ["Materials", "Excitations", "Mesh Sizes"])

    def test_folder_overview_rows(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        mat = objects.make_material(self.study, "Copper", [a, b])
        empty = objects.make_material(self.study, "Iron", [])
        exc = objects.make_excitation(self.study, "In", [(a, "Face1"), (a, "Face2")])
        size = objects.make_mesh_size(self.study, 1.5, [(a, ""), (c, "Edge1")])
        objects.update_ids(self.study)
        self.assertEqual(
            objects.material_rows(self.study),
            [
                (mat, [(a, "")], ["Copper", "A", "1"]),
                (mat, [(b, "")], ["Copper", "B", "2"]),
                (empty, [], ["Iron", "", ""]),
            ],
        )
        self.assertEqual(
            objects.excitation_rows(self.study),
            [(exc, [(a, "Face1"), (a, "Face2")], ["In", "A", "Face1, Face2", "1001"])],
        )
        self.assertEqual(
            objects.mesh_size_rows(self.study), [(size, [(a, ""), (c, "Edge1")], ["MeshSize", "1.5 mm", "A, C.Edge1"])]
        )
        self.assertEqual(objects.item_refs(mat), [(a, ""), (b, "")])
        self.assertTrue(objects.is_item(size) and not objects.is_item(self.study.MeshSizesGroup))
        self.assertEqual([x.Name for x in objects.bodies_without_material(self.study)], ["C"])
        d = self.box("D", 30)
        mat.References += [d]
        self.assertEqual(objects.material_rows(self.study)[2], (mat, [(d, "")], ["Copper", "D", "–"]))

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
            self.assertEqual(
                json.load(fh)["options"],
                {
                    "Mesh.Algorithm": 5,
                    "Mesh.Algorithm3D": 10,
                    "Mesh.MeshSizeFactor": 0.5,
                    "Mesh.Smoothing": 3,
                    "Mesh.OptimizeNetgen": 1,
                    "Mesh.MeshSizeMin": 0.1,
                    "Mesh.MeshSizeMax": 2.0,
                },
            )

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
        two.Shape = Part.makeCompound([Part.makeBox(1, 1, 1), Part.makeBox(1, 1, 1, App.Vector(5, 0, 0))])
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
        b.Label = "A!"  # cleans to "A_"
        a.Label = "A?"  # cleans to "A_" too
        objects.make_material(self.study, "Cu", [a, b])
        self.assertStudyError("A_")

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
        self.assertEqual(
            job,
            {
                "model_name": "My_Study",
                "msh_version": 4.1,
                "options": {
                    "Mesh.Algorithm": 6,
                    "Mesh.Algorithm3D": 1,
                    "Mesh.MeshSizeFactor": 1.0,
                    "Mesh.Smoothing": 1,
                    "Mesh.OptimizeNetgen": 0,
                },
                "volumes": [
                    {"id": 1, "name": "A", "file": "geometry/vol_1.brep", "size": 2.0},
                    {"id": 2, "name": "B", "file": "geometry/vol_2.brep", "size": 5.0},
                ],
                "surfaces": [
                    {
                        "id": 1001,
                        "name": "Terminal_In_A",
                        "volume_id": 1,
                        "files": ["geometry/surf_1001_1.brep", "geometry/surf_1001_2.brep"],
                    }
                ],
                "sizes": [],
            },
        )
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
        self.assertEqual(
            job["sizes"],
            [
                {"name": "MeshSize", "size": 1.0, "files": ["geometry/size_1_1.brep", "geometry/size_1_2.brep"]},
                {"name": "MeshSize", "size": 1.0, "files": ["geometry/size_2_1.brep"]},
            ],
        )
        vertex = Part.Shape()
        vertex.read(os.path.join(self.tmp.name, "geometry", "size_2_1.brep"))
        self.assertEqual(vertex.ShapeType, "Vertex")
        self.assertEqual(vertex.Vertexes[0].Point, b.Shape.Vertex1.Point)

    def test_check_missing_edge(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 1.0, [(a, "Edge99")])  # a box has 12 edges
        self.assertStudyError("has no Edge99")

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

    # --- Study setup --------------------------------------------------------

    def face(self, name, z=0.0):
        obj = self.doc.addObject("Part::Feature", name)
        obj.Shape = Part.makePlane(10, 10)
        obj.Placement.Base = App.Vector(0, 0, z)
        return obj

    def test_multiple_studies_have_independent_ownership_and_ids(self):
        second = objects.make_study(self.doc, "2D", "Cross-section")
        a = self.box("A")
        material = objects.make_material(self.study, "Iron", [a])
        other = objects.make_material(second, "Copper", [a])
        objects.update_ids(self.study)
        self.assertIsNone(objects.find_study(self.doc))
        self.assertEqual(objects.owner_study(material), self.study)
        self.assertEqual(objects.owner_study(other), second)
        self.assertEqual(objects.owner_study(second.MeshSizesGroup), second)
        self.assertIsNone(objects.owner_study(a))  # a reference does not imply ownership
        self.assertEqual(second.VolumeIds, {})
        self.assertEqual(len(objects.material_rows(second)), 1)

    def test_nested_sources_use_body_tip_and_final_boolean_result(self):
        root = self.doc.addObject("App::DocumentObjectGroup", "Geometry")
        part = self.doc.addObject("App::Part", "Part")
        root.addObject(part)
        body = self.doc.addObject("PartDesign::Body", "Body")
        body.newObject("PartDesign::AdditiveBox", "Feature")
        part.addObject(body)
        a, tool = self.box("A", 20), self.box("Tool", 25)
        cut = self.doc.addObject("Part::Cut", "Cut")
        cut.Base, cut.Tool = a, tool
        for obj in (a, tool, cut):
            root.addObject(obj)
        self.doc.recompute()
        body.Visibility = False  # hidden final geometry must still be included
        found, errors = geometry.collect([root, part, body], "3D")
        self.assertEqual([obj.Name for obj in found], [body.Name, cut.Name])
        self.assertEqual(errors, [])

    def test_planar_sources_are_checked_in_global_coordinates(self):
        a, b = self.face("A"), self.face("B", 5)
        part = self.doc.addObject("App::Part", "Part")
        part.addObject(a)
        part.Placement.Base = App.Vector(0, 0, 5)
        self.doc.recompute()
        self.assertEqual(geometry.collect([a, b], "2D"), ([a, b], []))
        part.Placement.Base.z = 10
        self.doc.recompute()
        found, errors = geometry.collect([a, b], "2D")
        self.assertEqual(found, [a])
        self.assertIn("share one plane", errors[0])
        self.assertIn("exactly one solid", geometry.collect([b], "3D")[1][0])
        self.assertIn("without solids", geometry.collect([self.box("Solid")], "2D")[1][0])

    def test_sources_update_after_rename_addition_and_deletion(self):
        source = self.doc.addObject("App::DocumentObjectGroup", "Geometry")
        a = self.box("A")
        source.addObject(a)
        self.study.MainMode, self.study.MainSource = "Container", source
        source.Label = "Renamed"
        b = self.box("B", 10)
        source.addObject(b)
        self.doc.recompute()
        self.assertEqual(geometry.region(self.study, "Main"), ([a, b], []))
        self.doc.removeObject(source.Name)
        found, errors = geometry.region(self.study, "Main")
        self.assertEqual(found, [])
        self.assertIn("missing", errors[0])
        self.assertEqual(self.study.MainMode, "Container")

    def test_a_container_with_study_objects_is_not_a_geometry_source(self):
        group = self.doc.addObject("App::DocumentObjectGroup", "Everything")
        group.addObject(self.study)
        self.assertTrue(geometry.is_container(group))
        self.assertFalse(geometry.is_source(group))
        self.assertFalse(geometry.is_source(self.study.MaterialsGroup))

    def test_sliding_setup_checks_assignments_and_ignores_disabled_region(self):
        a = self.box("A")
        self.study.MainMode = self.study.MovingMode = "Manual"
        self.study.MainObjects = self.study.MovingObjects = [a]
        self.assertEqual(geometry.setup(self.study), ([a], [], []))
        self.study.Movement = "Sliding motion"
        self.assertIn("both fixed and moving", geometry.setup(self.study)[2][0])
        self.assertEqual(self.study.MovingObjects, [a])

    def test_two_studies_restore_their_sources_settings_and_ids(self):
        second = objects.make_study(self.doc, "2D", "Cross-section")
        source = self.doc.addObject("App::DocumentObjectGroup", "Faces")
        source.addObject(self.face("Section"))
        second.MainMode, second.MainSource = "Container", source
        second.MeshSizesGroup.DefaultMeshSize = 1.5
        objects.make_material(self.study, "Iron", [self.box("A")])
        objects.update_ids(self.study)
        path = os.path.join(self.tmp.name, "setup.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        first, second = objects.studies(self.doc)
        self.study = first
        self.assertEqual(first.VolumeIds, {"A": "1"})
        self.assertEqual(second.Dimension, "2D")
        self.assertEqual(second.MainSource.Name, "Faces")
        self.assertEqual(second.MeshSizesGroup.DefaultMeshSize.Value, 1.5)
        self.assertEqual(geometry.region(second, "Main")[1], [])
        self.assertFalse(first.LegacyOutput)
        code = """import sys
import FreeCAD as App
from emsolution import geometry, objects
doc = App.openDocument(sys.argv[1])
first, second = objects.studies(doc)
assert first.VolumeIds == {'A': '1'}
assert second.Dimension == '2D' and second.MainSource.Name == 'Faces'
assert geometry.region(second, 'Main')[1] == []
App.closeDocument(doc.Name)
print('RESTORE PASS')
"""
        result = subprocess.run(
            [sys.executable, "-c", code, path], capture_output=True, encoding="utf-8", errors="replace"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("RESTORE PASS", result.stdout)

    def test_old_study_upgrade_preserves_settings_ids_and_default_output(self):
        objects.make_material(self.study, "Iron", [self.box("A")])
        objects.update_ids(self.study)
        self.study.MeshSizesGroup.DefaultMeshSize = 1.25
        self.study.OutputFolder = ""
        for prop in (
            "Dimension",
            "Movement",
            "LegacyOutput",
            "MainMode",
            "MovingMode",
            "MainSource",
            "MovingSource",
            "MainObjects",
            "MovingObjects",
        ):
            self.study.removeProperty(prop)
        path = os.path.join(self.tmp.name, "old.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        self.study = objects.find_study(self.doc)
        self.study.Proxy.onDocumentRestored(self.study)  # repeat must not reset data
        self.assertEqual(self.study.VolumeIds, {"A": "1"})
        self.assertEqual(self.study.MeshSizesGroup.DefaultMeshSize.Value, 1.25)
        self.assertEqual(self.study.OutputFolder, "")
        self.assertTrue(self.study.LegacyOutput)
        self.assertEqual(
            os.path.normpath(jobwriter.output_folder(self.study)), os.path.normpath(os.path.splitext(path)[0] + "_mesh")
        )
        self.assertEqual(geometry.export_unavailable(self.study), "")
        self.assertTrue(os.path.isfile(jobwriter.write_job(self.study)))

    def test_new_output_directories_are_independent_and_stable_under_rename(self):
        second = objects.make_study(self.doc)
        self.study.OutputFolder = ""
        path = os.path.join(self.tmp.name, "model.FCStd")
        self.doc.saveAs(path)
        folder = jobwriter.output_folder(self.study)
        self.study.Label = "Renamed"
        self.assertEqual(folder, jobwriter.output_folder(self.study))
        self.assertNotEqual(folder, jobwriter.output_folder(second))
        second.OutputFolder = self.study.OutputFolder = self.tmp.name
        objects.make_material(self.study, "Iron", [self.box("A")])
        with self.assertRaisesRegex(jobwriter.StudyError, "also used"):
            jobwriter.write_job(self.study)
        self.assertEqual(self.study.VolumeIds, {})
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "job.json")))

    def test_deferred_export_cannot_change_ids_or_write_files(self):
        objects.make_material(self.study, "Iron", [self.box("A")])
        for prop, value, message in (
            ("Dimension", "2D", "2D mesh generation"),
            ("Movement", "Sliding motion", "Sliding-motion"),
        ):
            old = getattr(self.study, prop)
            setattr(self.study, prop, value)
            with self.assertRaisesRegex(jobwriter.StudyError, message):
                jobwriter.write_job(self.study)
            self.assertEqual(self.study.VolumeIds, {})
            self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "job.json")))
            setattr(self.study, prop, old)

    def test_new_study_requires_geometry_even_when_materials_exist(self):
        study = objects.make_study(self.doc)
        self.assertEqual(study.MainMode, "Unassigned")
        objects.make_material(study, "Iron", [self.box("A")])
        with self.assertRaisesRegex(jobwriter.StudyError, "No geometry assigned"):
            jobwriter.check(study)

    def test_selected_geometry_controls_export_and_filters_other_assignments(self):
        a, b, outside = self.box("A"), self.box("B", 10), self.box("Outside", 20)
        source = self.doc.addObject("App::Part", "Stator")
        source.addObject(b)
        source.addObject(a)
        self.study.MainMode, self.study.MainSource = "Container", source
        objects.make_material(self.study, "Copper", [outside, a, b])
        # Conflicting/invalid assignments outside the source must not affect its mesh.
        objects.make_material(self.study, "Unused", [outside])
        objects.make_excitation(self.study, "Terminal", [(outside, "Face60"), (b, "Face1")])
        objects.make_mesh_size(self.study, 0.5, [(outside, "Face60"), (a, "Face1")])
        objects.make_mesh_size(self.study, 0.0, [(outside, "")])
        path = jobwriter.write_job(self.study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual([v["name"] for v in job["volumes"]], ["B", "A"])
        self.assertEqual([s["name"] for s in job["surfaces"]], ["Terminal_B"])
        self.assertEqual(len(job["sizes"]), 1)
        self.assertEqual(self.study.VolumeIds, {"B": "1", "A": "2"})
        self.assertEqual(self.study.SurfaceIds, {"Excitation|B": "1001"})
        result = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp.name, "Study.unv")))
        with open(os.path.join(self.tmp.name, "Study.msh"), encoding="utf-8") as fh:
            physical_names = fh.read().split("$PhysicalNames\n", 1)[1].split("$EndPhysicalNames", 1)[0]
        self.assertIn('3 1 "B"', physical_names)
        self.assertIn('3 2 "A"', physical_names)
        self.assertNotIn("Copper", physical_names)

    def test_missing_selected_materials_are_named_before_ids_or_files_change(self):
        a, b = self.box("A"), self.box("B", 10)
        self.study.MainMode, self.study.MainObjects = "Manual", [a, b]
        self.assertEqual(geometry.export_unavailable(self.study), "")
        with self.assertRaisesRegex(jobwriter.StudyError, r"A \(A\), B \(B\)"):
            jobwriter.write_job(self.study)
        self.assertEqual(self.study.VolumeIds, {})
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "job.json")))
        self.assertEqual(objects.bodies_without_material(self.study), [a, b])
        objects.make_material(self.study, "Copper", [a])
        self.assertEqual(objects.bodies_without_material(self.study), [b])
        self.assertStudyError("B (B)")

    def test_selection_ids_survive_material_changes_and_follow_live_membership(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        source = self.doc.addObject("App::DocumentObjectGroup", "Stator")
        source.addObject(a)
        source.addObject(b)
        self.study.MainMode, self.study.MainSource = "Container", source
        mat = objects.make_material(self.study, "Copper", [c, b, a])
        objects.update_ids(self.study)
        original = dict(self.study.VolumeIds)
        mat.References = [c]
        objects.update_ids(self.study)
        self.assertEqual(self.study.VolumeIds, original)
        self.assertEqual(len(objects.id_rows(self.study)), 2)
        self.assertIn("No material: A", objects.id_rows(self.study)[0][2])
        source.removeObject(b)
        source.addObject(c)
        objects.update_ids(self.study)
        self.assertEqual(self.study.VolumeIds, {"A": "1", "C": "3"})

    def test_selected_geometry_rejects_conflicting_materials_and_invalid_sources(self):
        a = self.box("A")
        self.study.MainMode, self.study.MainObjects = "Manual", [a]
        objects.make_material(self.study, "Copper", [a])
        objects.make_material(self.study, "Iron", [a])
        self.assertStudyError("more than one material")
        self.study.MainMode = "Container"
        self.assertStudyError("Selected container is missing")


if __name__ == "__main__":
    unittest.main()
