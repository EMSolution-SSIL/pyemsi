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

from .materialdata import STEEL, record

MESHER = os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution", "mesher.py")


class StudyTest(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("T")
        self.tmp = tempfile.TemporaryDirectory()
        self.study = objects.make_study(self.doc)
        self.study.MainMode = "Manual"  # bodies join the main geometry through self.mat()
        self.doc.saveAs(os.path.join(self.tmp.name, "T.FCStd"))  # the temporary folder is the simulation folder

    def tearDown(self):
        App.closeDocument(self.doc.Name)
        self.tmp.cleanup()

    def box(self, name, x=0.0, size=10.0):
        b = self.doc.addObject("Part::Box", name)
        b.Length = b.Width = b.Height = size
        b.Placement.Base = App.Vector(x, 0, 0)
        self.doc.recompute()
        return b

    def include(self, *bodies):
        """Add bodies to the Study's main geometry (Manual mode)."""
        self.study.MainObjects = list(dict.fromkeys([*self.study.MainObjects, *bodies]))

    def mat(self, label, bodies):
        """A material on bodies that are also in the main geometry."""
        self.include(*bodies)
        return objects.make_material(self.study, label, bodies)

    def ids(self):
        return dict(self.study.MatIds), dict(self.study.SmatIds)

    def scratch(self, *parts):
        return os.path.join(jobwriter.scratch_folder(self.study), *parts)

    def assertStudyError(self, text):
        with self.assertRaises(jobwriter.StudyError) as ctx:
            jobwriter.check(self.study)
        self.assertIn(text, str(ctx.exception))

    # --- IDs ---------------------------------------------------------------

    def test_ids_follow_tree_order_and_stay_after_adding_a_body(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        self.mat("Copper", [b, a])
        self.mat("Iron", [c])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "1", "A": "2", "C": "3"})
        d = self.box("D", 30)
        self.mat("Air", [d])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "1", "A": "2", "C": "3", "D": "4"})

    def test_surface_ids_one_per_excitation_and_body(self):
        a, b = self.box("A"), self.box("B", 10)
        self.mat("Copper", [a, b])
        objects.make_excitation(self.study, "Terminal", [(a, "Face1"), (a, "Face2"), (b, "Face1")])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[1], {"Excitation|A": "1001", "Excitation|B": "1002"})

    def test_rename_keeps_id_and_changes_name(self):
        a = self.box("A")
        mat = self.mat("Copper", [a])
        objects.update_ids(self.study)
        a.Label = "Coil"
        mat.Label = "Iron"
        objects.update_ids(self.study)
        self.assertEqual(objects.id_rows(self.study), [("MatIds", "A", "Coil", 1)])

    def test_deleted_body_id_is_not_reused(self):
        a, b = self.box("A"), self.box("B", 10)
        self.mat("Copper", [a, b])
        objects.update_ids(self.study)
        self.doc.removeObject("B")
        c = self.box("C", 20)
        self.include(c)
        objects.materials(self.study)[0].References += [c]
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"A": "1", "C": "3"})

    def test_set_id_refuses_duplicates_and_raises_counter(self):
        a, b = self.box("A"), self.box("B", 10)
        self.mat("Copper", [a, b])
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        with self.assertRaises(ValueError):
            objects.set_id(self.study, "MatIds", "A", 2)
        with self.assertRaises(ValueError):
            objects.set_id(self.study, "MatIds", "A", 1001)
        objects.set_id(self.study, "MatIds", "A", 50)
        self.assertEqual(self.study.NextMatId, 51)
        c = self.box("C", 20)
        self.include(c)
        objects.materials(self.study)[0].References += [c]
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds["C"], "51")

    def test_study_has_mat_and_smat_tables_only(self):
        for prop in ("MatIds", "SmatIds", "NextMatId", "NextSmatId"):
            self.assertIn(prop, self.study.PropertiesList)
        for prop in ("VolumeIds", "SurfaceIds", "NextVolumeId", "NextSurfaceId"):
            self.assertNotIn(prop, self.study.PropertiesList)
        self.assertEqual((self.study.NextMatId, self.study.NextSmatId), (1, 1001))

    def test_new_volume_ids_skip_numbers_used_by_surfaces(self):
        a, b = self.box("A"), self.box("B", 10)
        self.mat("Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        objects.set_id(self.study, "SmatIds", "Excitation|A", 2)
        self.include(b)
        objects.materials(self.study)[0].References += [b]
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds["B"], "3")

    def test_group_names_keep_the_typed_name_when_freecad_renames_the_label(self):
        air, a, b = self.box("Air"), self.box("A", 10), self.box("B", 20)
        self.mat("Air", [air])  # label taken by the body: Air001
        self.mat("Copper", [a])
        self.mat("Copper", [b])  # label taken: Copper001
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

    def test_main_geometry_has_no_materials_mode(self):
        for prop in ("MainMode", "MovingMode"):
            self.assertEqual(self.study.getEnumerationsOfProperty(prop), ["Unassigned", "Container", "Manual"])
        self.assertFalse(hasattr(self.study.Proxy, "onDocumentRestored"))

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
        mat = self.mat("Copper", [box])
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
        self.mat("Copper", [a])
        objects.update_ids(self.study)
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        self.assertIsNotNone(study)
        self.assertIsInstance(objects.materials(study)[0].Proxy, objects.Material)
        self.assertEqual(study.MatIds, {"A": "1"})

    def test_folders_keep_their_names(self):
        folder = self.study.MaterialsGroup
        folder.Label = "Stuff"
        self.assertEqual(folder.Label, "Materials")
        self.assertEqual(
            [f.Label for f in self.study.Group], ["Material Library", "Materials", "Excitations", "Mesh Sizes"]
        )

    def lib(self, material_id="user:steel", name="Steel", family="electrical_steel"):
        return objects.make_library_material(self.study, json.dumps(record(material_id, name, family, STEEL)))

    def test_library_material_mirrors_its_record(self):
        lib = self.lib()
        self.assertEqual((lib.Label, lib.MaterialId, lib.Family), ("Steel", "user:steel", "electrical_steel"))
        self.assertEqual(lib.getEditorMode("Record"), ["Hidden"])
        self.assertEqual(lib.getEditorMode("MaterialId"), ["ReadOnly"])
        self.assertEqual(objects.library_materials(self.study), [lib])
        self.assertFalse(objects.is_item(lib))
        self.assertIsNone(objects.pick_body(lib))

    def test_renaming_a_library_material_renames_its_record(self):
        lib = self.lib()
        lib.Label = "Silicon steel"
        data = json.loads(lib.Record)
        self.assertEqual(data["identity"]["name"], "Silicon steel")
        self.assertEqual((data["material_id"], lib.MaterialId), ("user:steel", "user:steel"))
        record_before = lib.Record
        lib.Label = "Silicon steel"
        self.assertEqual(lib.Record, record_before)

    def test_material_assignment_links_a_library_material_and_potential(self):
        a = self.box("A")
        lib = self.lib()
        mat = self.mat("Iron", [a])
        self.assertIsNone(mat.LibraryMaterial)
        self.assertEqual(mat.Potential, 0)
        mat.LibraryMaterial, mat.Potential = lib, 2
        self.assertEqual(objects.material_users(lib), [mat])
        objects.update_ids(self.study)
        self.assertEqual(objects.material_rows(self.study), [(mat, [(a, "")], ["Iron", "Steel", "A", "1", "2"])])
        self.assertEqual(
            objects.library_rows(self.study), [(lib, [(a, "")], ["Steel", "electrical_steel", "user:steel", "Iron"])]
        )

    def test_library_material_survives_save_and_reload(self):
        lib = objects.make_library_material(
            self.study, json.dumps(record("user:copper", "銅 مس Copper", "conductor"), ensure_ascii=False)
        )
        mat = self.mat("Coil", [self.box("A")])
        mat.LibraryMaterial, mat.Potential = lib, 3
        path = os.path.join(self.tmp.name, "lib.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        (lib,) = objects.library_materials(study)
        (mat,) = objects.materials(study)
        self.assertEqual(json.loads(lib.Record)["identity"]["name"], "銅 مس Copper")
        self.assertEqual(lib.Label, "銅 مس Copper")
        self.assertEqual((lib.MaterialId, mat.LibraryMaterial, mat.Potential), ("user:copper", lib, 3))

    def test_folder_overview_rows(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        mat = self.mat("Copper", [a, b])
        empty = self.mat("Iron", [])
        exc = objects.make_excitation(self.study, "In", [(a, "Face1"), (a, "Face2")])
        size = objects.make_mesh_size(self.study, 1.5, [(a, ""), (c, "Edge1")])
        self.include(c)
        objects.update_ids(self.study)
        self.assertEqual(
            objects.material_rows(self.study),
            [
                (mat, [(a, "")], ["Copper", "— none —", "A", "1", "0"]),
                (mat, [(b, "")], ["Copper", "— none —", "B", "2", "0"]),
                (empty, [], ["Iron", "— none —", "", "", "0"]),
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
        self.assertEqual(objects.material_rows(self.study)[2], (mat, [(d, "")], ["Copper", "— none —", "D", "–", "0"]))

    def test_mesh_settings_go_to_the_job(self):
        self.mat("Copper", [self.box("A")])
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
        self.mat("Copper", [self.box("A")])
        self.study.MeshSizesGroup.MinSize = 3.0
        self.study.MeshSizesGroup.MaxSize = 2.0
        self.assertStudyError("larger than the maximum")

    def test_check_not_one_solid(self):
        two = self.doc.addObject("Part::Feature", "Two")
        two.Shape = Part.makeCompound([Part.makeBox(1, 1, 1), Part.makeBox(1, 1, 1, App.Vector(5, 0, 0))])
        self.mat("Copper", [two])
        self.assertStudyError("exactly one solid")

    def test_check_zero_size(self):
        a = self.box("A")
        self.mat("Copper", [a])
        objects.make_mesh_size(self.study, 0.0, [(a, "")])
        self.assertStudyError("greater than 0")

    def test_check_missing_face(self):
        a = self.box("A")
        self.mat("Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face60")])  # a box has 6 faces
        self.assertStudyError("has no Face60")

    def test_smallest_mesh_size_wins(self):
        a = self.box("A")
        self.mat("Copper", [a])
        objects.make_mesh_size(self.study, 3.0, [(a, "")])
        objects.make_mesh_size(self.study, 2.0, [(a, "")])
        volumes = jobwriter.check(self.study)[0]
        self.assertEqual(volumes[0][1], 2.0)

    def test_names_equal_after_cleanup_are_refused(self):
        a = self.box("A")
        b = self.box("B", 10)
        b.Label = "A!"  # cleans to "A_"
        a.Label = "A?"  # cleans to "A_" too
        self.mat("Cu", [a, b])
        self.assertStudyError("A_")

    # --- simulation folder ----------------------------------------------------

    def test_mesh_file_is_the_emsolution_name_in_the_document_folder(self):
        folder = jobwriter.simulation_folder(self.study)
        self.assertTrue(os.path.samefile(folder, self.tmp.name))
        self.assertEqual(jobwriter.mesh_file(self.study), os.path.join(folder, "pre_geom.msh"))
        cross = objects.make_study(self.doc, "2D", "Cross-section")
        self.assertEqual(jobwriter.mesh_file(cross), os.path.join(folder, "pre_geom2D.msh"))

    def test_scratch_folder_is_per_document_and_study_and_survives_rename(self):
        second = objects.make_study(self.doc)
        folder = jobwriter.scratch_folder(self.study)
        rel = os.path.relpath(folder, jobwriter.simulation_folder(self.study))
        self.assertEqual(rel, os.path.join(".pyemsi", "freecad", "T", self.study.Name))
        self.study.Label = "Renamed"
        self.assertEqual(jobwriter.scratch_folder(self.study), folder)
        self.assertNotEqual(jobwriter.scratch_folder(second), folder)

    def test_save_as_moves_the_mesh_and_scratch_folders(self):
        other = os.path.join(self.tmp.name, "other")
        os.mkdir(other)
        self.doc.saveAs(os.path.join(other, "Moved.FCStd"))
        self.assertTrue(os.path.samefile(jobwriter.simulation_folder(self.study), other))
        self.assertEqual(os.path.dirname(jobwriter.mesh_file(self.study)), jobwriter.simulation_folder(self.study))
        self.assertIn(
            os.path.join(".pyemsi", "freecad", "Moved", self.study.Name), jobwriter.scratch_folder(self.study)
        )

    def test_unsaved_document_is_refused_before_ids_or_files_change(self):
        doc = App.newDocument("Unsaved")
        self.addCleanup(App.closeDocument, doc.Name)
        study = objects.make_study(doc)
        study.MainMode = "Manual"
        box = doc.addObject("Part::Box", "A")
        doc.recompute()
        study.MainObjects = [box]
        objects.make_material(study, "Copper", [box])
        with self.assertRaisesRegex(jobwriter.StudyError, "Save the document in the simulation folder first"):
            jobwriter.write_job(study)
        self.assertEqual(study.MatIds, {})

    def test_simulation_folder_with_spaces_and_persian_letters(self):
        self.mat("Copper", [self.box("A")])
        folder = os.path.join(self.tmp.name, "my model مدل")
        os.mkdir(folder)
        self.doc.saveAs(os.path.join(folder, "موتور.FCStd"))
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(folder, "pre_geom.msh")))
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))

    def test_second_study_replaces_the_mesh_and_keeps_its_own_scratch_folder(self):
        self.mat("Iron", [self.box("A")])
        second = objects.make_study(self.doc)
        b = self.box("B", 10)
        second.MainMode, second.MainObjects = "Manual", [b]
        objects.make_material(second, "Air", [b])
        for study in (self.study, second):
            path = jobwriter.write_job(study)
            r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
            self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.tmp.name, "pre_geom.msh"), encoding="utf-8") as fh:
            names = fh.read().split("$PhysicalNames\n", 1)[1].split("$EndPhysicalNames", 1)[0]
        self.assertIn('"B"', names)
        self.assertNotIn('"A"', names)
        self.assertNotEqual(jobwriter.scratch_folder(self.study), jobwriter.scratch_folder(second))
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))

    # --- geometry and job file ----------------------------------------------

    def test_body_in_app_part_is_exported_in_global_coordinates(self):
        part = self.doc.addObject("App::Part", "Part")
        part.Placement.Base = App.Vector(100, 0, 0)
        a = self.box("A")
        a.Placement.Base = App.Vector(0, 50, 0)
        part.addObject(a)
        self.doc.recompute()
        self.mat("Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face6")])  # top face, z = 10
        jobwriter.write_job(self.study)
        vol = Part.Shape()
        vol.read(self.scratch("geometry", "vol_1.brep"))
        self.assertEqual((vol.BoundBox.XMin, vol.BoundBox.YMin), (100, 50))
        face = Part.Shape()
        face.read(self.scratch("geometry", "surf_1001_1.brep"))
        self.assertAlmostEqual(face.BoundBox.XMin, 100)
        self.assertAlmostEqual(face.BoundBox.ZMin, 10)

    def test_job_json_contents(self):
        a, b = self.box("A"), self.box("B", 10)
        self.mat("Copper", [a])
        self.mat("Air", [b])
        objects.make_excitation(self.study, "Terminal In", [(a, "Face1"), (a, "Face2")])
        objects.make_mesh_size(self.study, 2.0, [(a, "")])
        self.study.Label = "My Study"
        path = jobwriter.write_job(self.study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        mesh_file = job.pop("mesh_file")
        self.assertEqual(os.path.basename(mesh_file), "pre_geom.msh")
        self.assertTrue(os.path.samefile(os.path.dirname(mesh_file), self.tmp.name))
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
                    {"mat_id": 1, "name": "A", "file": "geometry/vol_1.brep", "size": 2.0},
                    {"mat_id": 2, "name": "B", "file": "geometry/vol_2.brep", "size": 5.0},
                ],
                "surfaces": [
                    {
                        "smat_id": 1001,
                        "name": "Terminal_In_A",
                        "mat_id": 1,
                        "files": ["geometry/surf_1001_1.brep", "geometry/surf_1001_2.brep"],
                    }
                ],
                "sizes": [],
            },
        )
        for rel in ("vol_1.brep", "vol_2.brep", "surf_1001_1.brep", "surf_1001_2.brep"):
            self.assertTrue(os.path.exists(self.scratch("geometry", rel)))

    def test_face_edge_and_vertex_sizes_go_to_the_job(self):
        a, b = self.box("A"), self.box("B", 10)
        self.mat("Copper", [a, b])
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
        vertex.read(self.scratch("geometry", "size_2_1.brep"))
        self.assertEqual(vertex.ShapeType, "Vertex")
        self.assertEqual(vertex.Vertexes[0].Point, b.Shape.Vertex1.Point)

    def test_check_missing_edge(self):
        a = self.box("A")
        self.mat("Copper", [a])
        objects.make_mesh_size(self.study, 1.0, [(a, "Edge99")])  # a box has 12 edges
        self.assertStudyError("has no Edge99")

    def test_written_job_meshes(self):
        a, b = self.box("A"), self.box("B", 10)
        self.mat("Copper", [a])
        self.mat("Air", [b])
        objects.make_excitation(self.study, "T", [(a, "Face1")])  # x = 0 face
        objects.make_mesh_size(self.study, 1.0, [(a, "Face1"), (a, "Edge1"), (b, "Vertex8")])
        settings = self.study.MeshSizesGroup
        settings.DefaultMeshSize = 4.0
        settings.VolumeAlgorithm = "HXT"
        settings.SizeFactor = 0.8
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "pre_geom.msh")))
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))
        self.assertTrue(os.path.isfile(self.scratch("job.json")))

    # --- Study setup --------------------------------------------------------

    def face(self, name, z=0.0):
        obj = self.doc.addObject("Part::Feature", name)
        obj.Shape = Part.makePlane(10, 10)
        obj.Placement.Base = App.Vector(0, 0, z)
        return obj

    def test_multiple_studies_have_independent_ownership_and_ids(self):
        second = objects.make_study(self.doc, "2D", "Cross-section")
        a = self.box("A")
        material = self.mat("Iron", [a])
        other = objects.make_material(second, "Copper", [a])
        objects.update_ids(self.study)
        self.assertIsNone(objects.find_study(self.doc))
        self.assertEqual(objects.owner_study(material), self.study)
        self.assertEqual(objects.owner_study(other), second)
        self.assertEqual(objects.owner_study(second.MeshSizesGroup), second)
        self.assertIsNone(objects.owner_study(a))  # a reference does not imply ownership
        self.assertEqual(second.MatIds, {})
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
        self.mat("Iron", [self.box("A")])
        objects.update_ids(self.study)
        path = os.path.join(self.tmp.name, "setup.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        first, second = objects.studies(self.doc)
        self.study = first
        self.assertEqual(first.MatIds, {"A": "1"})
        self.assertEqual(second.Dimension, "2D")
        self.assertEqual(second.MainSource.Name, "Faces")
        self.assertEqual(second.MeshSizesGroup.DefaultMeshSize.Value, 1.5)
        self.assertEqual(geometry.region(second, "Main")[1], [])
        code = """import sys
import FreeCAD as App
from emsolution import geometry, objects
doc = App.openDocument(sys.argv[1])
first, second = objects.studies(doc)
assert first.MatIds == {'A': '1'}
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

    def test_deferred_export_cannot_change_ids_or_write_files(self):
        self.mat("Iron", [self.box("A")])
        for prop, value, message in (
            ("Dimension", "2D", "2D mesh generation"),
            ("Movement", "Sliding motion", "Sliding-motion"),
        ):
            old = getattr(self.study, prop)
            setattr(self.study, prop, value)
            with self.assertRaisesRegex(jobwriter.StudyError, message):
                jobwriter.write_job(self.study)
            self.assertEqual(self.study.MatIds, {})
            self.assertFalse(os.path.exists(self.scratch("job.json")))
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
        self.assertEqual(self.study.MatIds, {"B": "1", "A": "2"})
        self.assertEqual(self.study.SmatIds, {"Excitation|B": "1001"})
        result = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))
        with open(os.path.join(self.tmp.name, "pre_geom.msh"), encoding="utf-8") as fh:
            physical_names = fh.read().split("$PhysicalNames\n", 1)[1].split("$EndPhysicalNames", 1)[0]
        self.assertIn('3 1 "B"', physical_names)
        self.assertIn('3 2 "A"', physical_names)
        self.assertNotIn("Copper", physical_names)

    def test_bodies_without_materials_are_meshed_and_listed(self):
        a, b = self.box("A"), self.box("B", 10)
        self.study.MainMode, self.study.MainObjects = "Manual", [a, b]
        self.assertEqual(geometry.export_unavailable(self.study), "")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual([(v["mat_id"], v["name"]) for v in job["volumes"]], [(1, "A"), (2, "B")])
        self.assertEqual(objects.bodies_without_material(self.study), [a, b])

    def test_ids_follow_live_membership_of_the_selected_geometry(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        source = self.doc.addObject("App::DocumentObjectGroup", "Stator")
        source.addObject(a)
        source.addObject(b)
        self.study.MainMode, self.study.MainSource = "Container", source
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds, {"A": "1", "B": "2"})
        self.assertEqual([r[2] for r in objects.id_rows(self.study)], ["A", "B"])
        source.removeObject(b)
        source.addObject(c)
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds, {"A": "1", "C": "3"})

    def test_selected_geometry_rejects_a_missing_container(self):
        self.study.MainMode, self.study.MainObjects = "Manual", [self.box("A")]
        self.study.MainMode = "Container"
        self.assertStudyError("Selected container is missing")


if __name__ == "__main__":
    unittest.main()
