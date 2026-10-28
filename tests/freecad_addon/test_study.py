"""Study, ID table and job writer tests.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_study.py"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

import FreeCAD as App
import Part
import gmsh
from BOPTools import SplitAPI

from emsolution import geometry, jobwriter, objects, validation

from .materialdata import STEEL, record

MESHER = os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution", "mesher.py")
MESHER2D = os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution", "mesher2d.py")


def msh_element_types(path, dim):
    """Gmsh element type numbers of the dim-D entity blocks in an ASCII msh 4.1 file."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("$Elements\n", 1)[1].split("$EndElements", 1)[0].splitlines()
    types, k = set(), 1  # line 0: numEntityBlocks numElements minTag maxTag
    while k < len(lines):
        d, _, t, n = map(int, lines[k].split())  # block header: entityDim entityTag elementType numElements
        if d == dim:
            types.add(t)
        k += n + 1
    return types


class StudyTest(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("T")
        self.tmp = tempfile.TemporaryDirectory()
        self.study = objects.make_study(self.doc)
        self.study.MainMode = "Manual"  # bodies join the main geometry through self.include()
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

    def steel(self):
        """The Study's Steel library material, made on first use."""
        found = [o for o in objects.library_materials(self.study) if o.MaterialId == "user:steel"]
        return found[0] if found else self.lib()

    def assign(self, bodies, potential=0, lib=None):
        """Assignments on bodies that are also in the main geometry; lib defaults to Steel."""
        self.include(*bodies)
        return objects.assign(self.study, bodies, lib or self.steel(), potential)

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
        self.include(b, a)
        self.include(c)
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "1", "A": "2", "C": "3"})
        d = self.box("D", 30)
        self.include(d)
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "1", "A": "2", "C": "3", "D": "4"})

    def test_surface_ids_one_per_excitation_and_body(self):
        a, b = self.box("A"), self.box("B", 10)
        self.include(a, b)
        objects.make_excitation(self.study, "Terminal", [(a, "Face1"), (a, "Face2"), (b, "Face1")])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[1], {"Excitation|A": "1001", "Excitation|B": "1002"})

    def test_rename_keeps_id_and_changes_name(self):
        a = self.box("A")
        self.include(a)
        objects.update_ids(self.study)
        a.Label = "Coil"
        objects.update_ids(self.study)
        self.assertEqual(objects.id_rows(self.study), [("MatIds", "A", "Coil", 1)])

    def test_deleted_body_id_is_not_reused(self):
        a, b = self.box("A"), self.box("B", 10)
        self.include(a, b)
        objects.update_ids(self.study)
        self.doc.removeObject("B")
        c = self.box("C", 20)
        self.include(c)
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"A": "1", "C": "3"})

    def test_set_id_refuses_duplicates_and_raises_counter(self):
        a, b = self.box("A"), self.box("B", 10)
        self.include(a, b)
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
        self.include(a)
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        objects.set_id(self.study, "SmatIds", "Excitation|A", 2)
        self.include(b)
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds["B"], "3")

    def test_volume_names_are_body_labels_and_survive_reload(self):
        air, a, b = self.box("Air"), self.box("A", 10), self.box("B", 20)
        self.include(air, a, b)
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
        (mat,) = self.assign([box])
        part = self.doc.addObject("App::Part", "Part")
        self.assertEqual(objects.pick_body(cube).Name, "Body")
        self.assertEqual(objects.pick_body(box).Name, "A")
        # a material linking to its own folder would be a loop in the document
        for obj in (self.study, self.study.MaterialsGroup, mat, part):
            self.assertIsNone(objects.pick_body(obj), obj.Name)

    def test_items_may_link_to_bodies_inside_a_part(self):
        # plain links may not reach into an App::Part; FreeCAD warns on every recompute
        (mat,) = self.assign([self.box("A")])
        self.assertEqual(mat.getTypeIdOfProperty("Body"), "App::PropertyLinkGlobal")
        for item in (objects.make_excitation(self.study, "In", []), objects.make_mesh_size(self.study, 1.0, [])):
            self.assertTrue(item.getTypeIdOfProperty("References").endswith("Global"), item.Name)

    def test_study_survives_save_and_reload(self):
        a = self.box("A")
        self.assign([a])
        objects.update_ids(self.study)
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        self.assertIsNotNone(study)
        self.assertIsInstance(objects.materials(study)[0].Proxy, objects.Material)
        self.assertEqual(objects.materials(study)[0].Body.Name, "A")
        self.assertEqual(study.MatIds, {"A": "1"})

    def test_folders_keep_their_names(self):
        folder = self.study.MaterialsGroup
        folder.Label = "Stuff"
        self.assertEqual(folder.Label, "Materials")
        self.assertEqual(
            [f.Label for f in self.study.Group],
            ["Material Library", "Materials", "Excitations", "Mesh Sizes", "Air Regions"],
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

    def test_deleting_a_study_takes_everything_it_owns(self):
        a = self.box("A")
        self.assign([a])
        objects.make_excitation(self.study, "In", [(a, "Face1")])
        objects.make_mesh_size(self.study, 1.0, [(a, "")])
        result = self.doc.addObject("App::FeaturePython", "MeshResult")  # stands in for the Fem mesh
        self.study.addObject(result)
        self.study.MeshResult = result
        second = objects.make_study(self.doc)
        objects.make_library_material(second, json.dumps(record("user:air", "Air")))
        keep = {"A", second.Name} | {o.Name for o in objects.study_contents(second)}
        owned = objects.study_contents(self.study)
        self.assertEqual(len(owned), 5 + 5)  # five folders; assignment, library material, excitation, size, result
        objects.delete_contents(self.study)
        self.doc.removeObject(self.study.Name)
        self.assertEqual({o.Name for o in self.doc.Objects}, keep)

    def test_library_material_left_without_a_study_has_no_users(self):
        lib = self.lib()
        self.doc.removeObject(self.study.Name)  # its folders and items stay behind
        self.assertEqual(objects.material_users(lib), [])
        self.assertEqual(objects.user_labels(lib), [])

    def test_renaming_a_library_material_renames_its_record(self):
        lib = self.lib()
        lib.Label = "Silicon steel"
        data = json.loads(lib.Record)
        self.assertEqual(data["identity"]["name"], "Silicon steel")
        self.assertEqual((data["material_id"], lib.MaterialId), ("user:steel", "user:steel"))
        record_before = lib.Record
        lib.Label = "Silicon steel"
        self.assertEqual(lib.Record, record_before)

    def test_assign_makes_one_assignment_per_body(self):
        a, b = self.box("A"), self.box("B", 10)
        steel, air = self.lib(), self.lib("user:air", "Air", "generic")
        first = self.assign([a, b], 2, steel)
        self.assertEqual([(m.Body, m.LibraryMaterial, m.Potential) for m in first], [(a, steel, 2), (b, steel, 2)])
        self.assertEqual([m.Label for m in first], ["A: Steel", "B: Steel"])
        self.assertFalse(hasattr(first[0], "GroupName") or hasattr(first[0], "References"))
        again = objects.assign(self.study, [b, b], air, 0)
        self.assertEqual(again, [first[1], first[1]])
        self.assertEqual(objects.materials(self.study), first)
        self.assertEqual((first[1].LibraryMaterial, first[1].Potential, first[1].Label), (air, 0, "B: Air"))
        self.assertEqual(objects.material_users(steel), [first[0]])
        self.assertEqual(objects.user_labels(steel), ["A"])
        self.assertEqual(objects.assignment_of(self.study), {"A": first[0], "B": first[1]})
        objects.unassign(self.study, [a, self.box("C", 20)])
        self.assertEqual(objects.materials(self.study), [first[1]])
        self.assertEqual(objects.library_rows(self.study)[1], (air, [(b, "")], ["Air", "generic", "user:air", "B"]))

    def test_assignment_label_follows_renamed_body_and_material(self):
        a = self.box("A")
        (m,) = self.assign([a])
        a.Label = "Core"
        m.LibraryMaterial.Label = "M330"
        objects.sync_labels(self.study)
        self.assertEqual(m.Label, "Core: M330")

    def test_assignment_of_a_deleted_body_is_ignored(self):
        a, b = self.box("A"), self.box("B", 10)
        lib = self.steel()
        self.assign([a, b], lib=lib)
        self.doc.removeObject("B")
        self.assertEqual(list(objects.assignment_of(self.study)), ["A"])
        self.assertEqual([r[2][0] for r in objects.material_rows(self.study)], ["A"])
        self.assertEqual(objects.bodies_without_material(self.study), [])
        self.assertEqual(objects.user_labels(lib), ["A", "B: Steel"])
        objects.sync_labels(self.study)  # must not fail on the orphan

    def test_body_outside_the_main_geometry_keeps_its_row(self):
        a, outside = self.box("A"), self.box("Outside", 20)
        self.include(a)
        objects.assign(self.study, [outside], self.steel(), 1)
        objects.update_ids(self.study)
        self.assertEqual(
            objects.material_rows(self.study),
            [
                (a, [(a, "")], ["A", "— none —", "1", ""]),
                (outside, [(outside, "")], ["Outside (not in main geometry)", "Steel", "–", "1"]),
            ],
        )
        self.assertEqual(objects.bodies_without_material(self.study), [a])

    def test_assignments_need_bodies_in_the_main_geometry(self):
        a, b = self.box("A"), self.box("B", 10)
        self.study.MainMode = "Unassigned"
        self.assertEqual(objects.assignment_problem(self.study, [a]), objects.NO_MAIN_GEOMETRY)
        self.study.MainMode = "Manual"  # with an empty manual list
        self.assertEqual(objects.assignment_problem(self.study, [a]), objects.NO_MAIN_GEOMETRY)
        self.include(a)
        self.assertEqual(objects.assignment_problem(self.study, [a, a]), "")
        self.assertEqual(
            objects.assignment_problem(self.study, [a, b, b]),
            "Not in the Study's main geometry: B. Add them to it in the Study panel or select other bodies.",
        )

    def test_library_material_survives_save_and_reload(self):
        lib = objects.make_library_material(
            self.study, json.dumps(record("user:copper", "銅 مس Copper", "conductor"), ensure_ascii=False)
        )
        self.assign([self.box("A")], 3, lib)
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
        ma, _mb = self.assign([a, b])
        exc = objects.make_excitation(self.study, "In", [(a, "Face1"), (a, "Face2")])
        size = objects.make_mesh_size(self.study, 1.5, [(a, ""), (c, "Edge1")])
        self.include(c)
        objects.update_ids(self.study)
        self.assertEqual(
            objects.material_rows(self.study),
            [
                (a, [(a, "")], ["A", "Steel", "1", "0"]),
                (b, [(b, "")], ["B", "Steel", "2", "0"]),
                (c, [(c, "")], ["C", "— none —", "3", ""]),
            ],
        )
        self.assertEqual(
            objects.excitation_rows(self.study),
            [(exc, [(a, "Face1"), (a, "Face2")], ["In", "A", "Face1, Face2", "1001"])],
        )
        self.assertEqual(
            objects.mesh_size_rows(self.study), [(size, [(a, ""), (c, "Edge1")], ["MeshSize", "1.5 mm", "A, C.Edge1"])]
        )
        self.assertEqual(objects.item_refs(ma), [(a, "")])
        self.assertTrue(objects.is_item(size) and not objects.is_item(self.study.MeshSizesGroup))
        self.assertEqual([x.Name for x in objects.bodies_without_material(self.study)], ["C"])
        d = self.box("D", 30)
        objects.assign(self.study, [d], ma.LibraryMaterial, 4)
        self.assertEqual(
            objects.material_rows(self.study)[3], (d, [(d, "")], ["D (not in main geometry)", "Steel", "–", "4"])
        )

    def test_transfinite_items_are_listed_with_mesh_sizes(self):
        a = self.box("A")
        self.include(a)
        size = objects.make_mesh_size(self.study, 1.5, [(a, "")])
        body = objects.make_transfinite_body(self.study, [a], [(a, "Vertex1")])
        edges = objects.make_transfinite_edges(self.study, 4, [(a, "Edge1"), (a, "Edge2")], "Bump", 0.2)
        self.assertEqual(objects.mesh_sizes(self.study), [size])
        self.assertEqual(objects.transfinite_bodies(self.study), [body])
        self.assertEqual(objects.transfinite_edges(self.study), [edges])
        self.assertTrue(objects.is_item(body) and objects.is_item(edges))
        self.assertEqual(objects.item_refs(body), [(a, ""), (a, "Vertex1")])
        self.assertEqual(
            objects.mesh_size_rows(self.study),
            [
                (size, [(a, "")], ["MeshSize", "1.5 mm", "A"]),
                (body, [(a, ""), (a, "Vertex1")], ["TransfiniteBody", "structured", "A, A.Vertex1"]),
                (edges, [(a, "Edge1"), (a, "Edge2")], ["TransfiniteEdges", "4 el, Bump 0.2", "A.Edge1, A.Edge2"]),
            ],
        )
        self.assertEqual(self.study.MeshSizesGroup.RecombinationAlgorithm, "Blossom")
        self.assertFalse(hasattr(self.study.MeshSizesGroup, "Recombine"))

    def test_recombine_item_is_listed_with_mesh_sizes(self):
        a, b = self.box("A"), self.box("B", 10)
        self.include(a, b)
        item = objects.make_recombine(self.study, [a, b])
        self.assertEqual(objects.recombine_items(self.study), [item])
        self.assertEqual(objects.mesh_sizes(self.study), [])
        self.assertTrue(objects.is_item(item))
        self.assertEqual(objects.item_refs(item), [(a, ""), (b, "")])
        self.assertEqual(
            objects.mesh_size_rows(self.study), [(item, [(a, ""), (b, "")], ["Recombine", "recombine", "A, B"])]
        )

    def test_recombination_algorithms_are_the_gmsh_values(self):
        self.assertEqual(
            self.study.MeshSizesGroup.getEnumerationsOfProperty("RecombinationAlgorithm"),
            ["Blossom", "Simple", "Blossom full-quad", "Simple full-quad"],
        )
        self.assertEqual(
            objects.RECOMBINATION_ALGORITHMS, {"Blossom": 1, "Simple": 0, "Blossom full-quad": 3, "Simple full-quad": 2}
        )

    def test_transfinite_items_survive_save_and_reload(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_edges(self.study, 7, [(a, "Edge1")], "Bump", 0.3)
        objects.make_recombine(self.study, [a])
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        (body,) = objects.transfinite_bodies(study)
        (edges,) = objects.transfinite_edges(study)
        self.assertIsInstance(body.Proxy, objects.TransfiniteBody)
        self.assertEqual((edges.Elements, edges.Distribution, edges.BumpCoefficient), (7, "Bump", 0.3))
        (rec,) = objects.recombine_items(study)
        self.assertIsInstance(rec.Proxy, objects.Recombine)

    def test_folder_saved_with_the_old_recombine_switch_loads_without_it(self):
        folder = self.study.MeshSizesGroup
        folder.removeProperty("RecombinationAlgorithm")
        folder.addProperty("App::PropertyBool", "Recombine", "Mesh", "")  # as saved by the global switch
        folder.Recombine = True
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        folder = objects.find_study(self.doc).MeshSizesGroup
        self.assertFalse(hasattr(folder, "Recombine"))
        self.assertEqual(folder.RecombinationAlgorithm, "Blossom")
        self.study = objects.find_study(self.doc)
        self.include(self.box("A"))
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            options = json.load(fh)["options"]
        self.assertNotIn("Mesh.RecombineAll", options)
        self.assertEqual(options["Mesh.RecombinationAlgorithm"], 1)

    def test_mesh_settings_go_to_the_job(self):
        self.include(self.box("A"))
        settings = self.study.MeshSizesGroup
        settings.SurfaceAlgorithm = "Delaunay"
        settings.VolumeAlgorithm = "HXT"
        settings.SizeFactor = 0.5
        settings.MinSize = 0.1
        settings.MaxSize = 2.0
        settings.SmoothingSteps = 3
        settings.OptimizeNetgen = True
        settings.RecombinationAlgorithm = "Simple full-quad"
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertEqual(
                json.load(fh)["options"],
                {
                    "Mesh.RecombinationAlgorithm": 2,
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
        self.include(self.box("A"))
        self.study.MeshSizesGroup.MinSize = 3.0
        self.study.MeshSizesGroup.MaxSize = 2.0
        self.assertStudyError("larger than the maximum")

    def test_check_no_solid(self):
        self.include(self.face("Sheet"))
        self.assertStudyError("at least one solid")

    def test_check_zero_size(self):
        a = self.box("A")
        self.include(a)
        objects.make_mesh_size(self.study, 0.0, [(a, "")])
        self.assertStudyError("greater than 0")

    def test_check_missing_face(self):
        a = self.box("A")
        self.include(a)
        objects.make_excitation(self.study, "T", [(a, "Face60")])  # a box has 6 faces
        self.assertStudyError("has no Face60")

    def test_smallest_mesh_size_wins(self):
        a = self.box("A")
        self.include(a)
        objects.make_mesh_size(self.study, 3.0, [(a, "")])
        objects.make_mesh_size(self.study, 2.0, [(a, "")])
        volumes = jobwriter.check(self.study)[0]
        self.assertEqual(volumes[0][1], 2.0)

    def test_names_equal_after_cleanup_are_refused(self):
        a = self.box("A")
        b = self.box("B", 10)
        b.Label = "A!"  # cleans to "A_"
        a.Label = "A?"  # cleans to "A_" too
        self.include(a, b)
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
        with self.assertRaisesRegex(jobwriter.StudyError, "Save the document in the simulation folder first"):
            jobwriter.write_job(study)
        self.assertEqual(study.MatIds, {})

    def test_simulation_folder_with_spaces_and_persian_letters(self):
        self.include(self.box("A"))
        folder = os.path.join(self.tmp.name, "my model مدل")
        os.mkdir(folder)
        self.doc.saveAs(os.path.join(folder, "موتور.FCStd"))
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(folder, "pre_geom.msh")))
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))

    def test_second_study_replaces_the_mesh_and_keeps_its_own_scratch_folder(self):
        self.include(self.box("A"))
        second = objects.make_study(self.doc)
        b = self.box("B", 10)
        second.MainMode, second.MainObjects = "Manual", [b]
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
        self.include(a)
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
        self.include(a)
        self.include(b)
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
                    "Mesh.RecombinationAlgorithm": 1,
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
        self.include(a, b)
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
        self.include(a)
        objects.make_mesh_size(self.study, 1.0, [(a, "Edge99")])  # a box has 12 edges
        self.assertStudyError("has no Edge99")

    def all_edges(self, body):
        return [(body, f"Edge{i}") for i in range(1, len(body.Shape.Edges) + 1)]

    def test_transfinite_items_go_to_the_job(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_body(self.study, [a], [(a, "Vertex1")])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a), "Bump", 0.4)
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        tf = job["transfinite"]
        self.assertEqual(tf["bodies"], [{"name": "A", "mat_id": 1, "corner_files": ["geometry/corner_1_1.brep"]}])
        (edges,) = tf["edges"]
        self.assertEqual(
            (edges["name"], edges["nodes"], edges["distribution"], edges["coef"]), ("TransfiniteEdges", 4, "Bump", 0.4)
        )
        self.assertEqual(len(edges["files"]), 12)
        edge = Part.Shape()
        edge.read(self.scratch("geometry", "tedge_1_1.brep"))
        self.assertEqual(edge.ShapeType, "Edge")
        self.assertNotIn("Mesh.RecombineAll", job["options"])

    def test_job_without_transfinite_items_has_no_transfinite_key(self):
        self.include(self.box("A"))
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("transfinite", json.load(fh))

    def test_structured_body_edge_without_item_is_refused(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a)[:11])
        self.assertStudyError("edges without Transfinite Edges: Edge12")

    def test_edge_in_two_transfinite_edges_is_refused(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_edges(self.study, 3, [(a, "Edge1")])
        objects.make_transfinite_edges(self.study, 4, [(a, "Edge1")])
        self.assertStudyError("A.Edge1 is in Transfinite Edges")

    def test_body_in_two_transfinite_bodies_is_refused(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_body(self.study, [a])
        self.assertStudyError("Body A is in Transfinite Body")

    def test_corner_on_another_body_is_refused(self):
        a, b = self.box("A"), self.box("B", 10)
        self.include(a, b)
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        objects.make_transfinite_body(self.study, [a], [(b, "Vertex1")])
        self.assertStudyError("is not on one of its bodies")

    def assertStudyErrorIn(self, study, text):
        with self.assertRaises(jobwriter.StudyError) as ctx:
            jobwriter.check(study)
        self.assertIn(text, str(ctx.exception))

    def two_blocks(self, name):
        """Two 10 x 10 faces side by side that share the edge x = 10."""
        obj = self.doc.addObject("Part::Feature", name)
        obj.Shape = Part.makePlane(10, 10).generalFuse([Part.makePlane(10, 10, App.Vector(10, 0, 0))])[0]
        return obj

    def face_edges(self, body, face):
        edges = body.Shape.getElement(face).Edges
        return [(body, f"Edge{i}") for i, e in enumerate(body.Shape.Edges, 1) if any(e.isSame(f) for f in edges)]

    def scratch_of(self, study, *parts):
        return os.path.join(jobwriter.scratch_folder(study), *parts)

    def test_picked_faces_go_to_the_job(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        right = self.face_at(b, 15, 5)
        objects.make_transfinite_edges(study, 4, self.face_edges(b, right))
        t = objects.make_transfinite_body(study, [])
        t.References = [(b, right), (b, right)]  # twice: one entry
        objects.make_recombine(study, []).References = [(b, right)]
        with open(jobwriter.write_job(study), encoding="utf-8") as fh:
            job = json.load(fh)
        (entry,) = job["transfinite"]["bodies"]
        self.assertEqual(entry["faces"], [{"face": right, "file": "geometry/tface_1_1.brep"}])
        self.assertEqual(
            job["recombine_faces"],
            [{"name": "B", "mat_id": entry["mat_id"], "face": right, "file": "geometry/rface_1_1.brep"}],
        )
        self.assertNotIn("recombine", job)
        shape = Part.Shape()
        shape.read(self.scratch_of(study, "geometry", "tface_1_1.brep"))
        self.assertEqual(shape.ShapeType, "Face")
        self.assertAlmostEqual(shape.Faces[0].CenterOfMass.x, 15)

    def test_whole_body_and_its_face_in_one_item_write_the_whole_body(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        objects.make_transfinite_edges(study, 4, self.all_edges(b))
        objects.make_transfinite_body(study, []).References = [(b, "Face1"), (b, "")]
        objects.make_recombine(study, [b])
        objects.make_recombine(study, []).References = [(b, "Face1")]
        with open(jobwriter.write_job(study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertNotIn("faces", job["transfinite"]["bodies"][0])
        self.assertNotIn("recombine_faces", job)

    def test_corners_stay_with_their_item(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        objects.make_transfinite_edges(study, 4, self.all_edges(b))
        left, right = self.face_at(b, 5, 5), self.face_at(b, 15, 5)
        shared = next(f"Vertex{i}" for i, v in enumerate(b.Shape.Vertexes, 1) if abs(v.Point.x - 10) < 1e-6)
        objects.make_transfinite_body(study, [], [(b, shared)]).References = [(b, left)]
        objects.make_transfinite_body(study, []).References = [(b, right)]
        with open(jobwriter.write_job(study), encoding="utf-8") as fh:
            first, second = json.load(fh)["transfinite"]["bodies"]
        self.assertEqual(first["corner_files"], ["geometry/corner_1_1.brep"])
        self.assertEqual(second["corner_files"], [])

    def test_transfinite_picks_split_into_references_and_corners(self):
        b = self.two_blocks("B")
        picks = [(b, "Face2"), (b, "Vertex3"), (b, ""), (b, "Vertex1")]
        self.assertEqual(objects.split_corners(picks), ([(b, "Face2"), (b, "")], [(b, "Vertex3"), (b, "Vertex1")]))

    def test_face_picks_whole_body_wins_over_its_faces(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        t = objects.make_transfinite_body(study, [b])
        t.References = [(b, "Face2"), (b, ""), (b, "Face2")]
        self.assertEqual(objects.face_picks(t), [(b, [])])
        t.References = [(b, "Face2"), (b, "Face1"), (b, "Face2")]
        self.assertEqual(objects.face_picks(t), [(b, ["Face1", "Face2"])])

    def test_picked_face_needs_only_its_own_edges(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        right = self.face_at(b, 15, 5)
        t = objects.make_transfinite_body(study, [])
        t.References = [(b, right)]
        objects.make_transfinite_edges(study, 4, self.face_edges(b, right)[:3])
        self.assertStudyErrorIn(study, f"B {right} has edges without Transfinite Edges: ")
        objects.make_transfinite_edges(study, 4, self.face_edges(b, right)[3:])
        jobwriter.check(study)  # the left face's other edges are not required

    def test_face_in_two_transfinite_bodies_is_refused(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        objects.make_transfinite_edges(study, 4, self.all_edges(b))
        right = self.face_at(b, 15, 5)
        t1 = objects.make_transfinite_body(study, [b])
        t2 = objects.make_transfinite_body(study, [])
        t2.References = [(b, right)]
        self.assertStudyErrorIn(study, f"B.{right} is in Transfinite Body {t1.Label} and {t2.Label}.")

    def test_faces_of_one_body_in_two_transfinite_bodies_are_fine(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        objects.make_transfinite_edges(study, 4, self.all_edges(b))
        for x in (5, 15):
            objects.make_transfinite_body(study, []).References = [(b, self.face_at(b, x, 5))]
        jobwriter.check(study)

    def test_missing_face_on_transfinite_body_and_recombine_is_refused(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        objects.make_transfinite_body(study, []).References = [(b, "Face7")]
        self.assertStudyErrorIn(study, "Transfinite Body TransfiniteBody: body B has no Face7. Reselect it.")
        objects.make_recombine(study, []).References = [(b, "Face9")]
        self.assertStudyErrorIn(study, "Recombine Recombine: body B has no Face9. Reselect it.")

    def test_whole_body_in_two_recombine_items_is_still_fine(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        objects.make_recombine(study, [b])
        objects.make_recombine(study, []).References = [(b, "Face1")]
        jobwriter.check(study)

    def test_corner_on_no_structured_face_of_its_item_is_refused(self):
        b = self.two_blocks("B")
        study = self.make_2d_study(b)
        right = self.face_at(b, 15, 5)
        objects.make_transfinite_edges(study, 4, self.face_edges(b, right))
        far = next(f"Vertex{i}" for i, v in enumerate(b.Shape.Vertexes, 1) if v.Point.x < 1e-6)  # on the left face only
        t = objects.make_transfinite_body(study, [], [(b, far)])
        t.References = [(b, right)]
        self.assertStudyErrorIn(
            study, f"Transfinite Body {t.Label}: corner B.{far} is on none of its structured faces."
        )
        problem = next(p for p in validation.validate(study) if "is on none of its structured faces" in p.text)
        self.assertEqual(problem.refs, [(b, far)])

    def test_two_shared_faces_are_named_in_one_message(self):
        core = self.three_blocks()
        study = self.make_2d_study(core)
        faces = [self.nearest_face(core, 15, 5), self.nearest_face(core, 5, 5)]
        t1 = objects.make_transfinite_body(study, [])
        t1.References = [(core, f) for f in faces]
        t2 = objects.make_transfinite_body(study, [])
        t2.References = [(core, f) for f in faces]
        a, b = sorted(faces, key=lambda f: int(f[4:]))
        text = f"Core.{a}, Core.{b} are in Transfinite Body {t1.Label} and {t2.Label}."
        problems = [p for p in validation.validate(study) if " are in Transfinite Body " in p.text]
        self.assertEqual([p.text for p in problems], [text])
        self.assertEqual(sorted(s for _, s in problems[0].refs), [a, b])

    def test_face_picks_in_a_3d_study_are_refused(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        objects.make_transfinite_body(self.study, []).References = [(a, "Face1")]
        objects.make_recombine(self.study, []).References = [(a, "Face2")]
        self.assertStudyError("Transfinite Body TransfiniteBody: pick whole solids in a 3D Study (A.Face1).")
        self.assertStudyError("Recombine Recombine: pick whole solids in a 3D Study (A.Face2).")

    def test_structured_box_job_meshes_to_hexahedra(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        objects.make_recombine(self.study, [a])
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Structured      A", r.stdout)
        self.assertEqual(msh_element_types(os.path.join(self.tmp.name, "pre_geom.msh"), 3), {5}, "only hexahedra")

    def test_2d_structured_face_job_meshes_to_quads(self):
        a = self.face("A")
        study = self.make_2d_study(a)
        objects.make_transfinite_body(study, [a])
        objects.make_transfinite_edges(study, 4, self.all_edges(a))
        objects.make_recombine(study, [a])
        path = jobwriter.write_job(study)
        r = subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(msh_element_types(os.path.join(self.tmp.name, "pre_geom2D.msh"), 2), {3}, "only quadrangles")

    def test_recombine_items_go_to_the_job(self):
        a, b, c, d = self.box("A"), self.box("B", 10), self.box("C", 20), self.box("D", 40)
        self.include(a, b, c)  # D is outside the main geometry: skipped
        objects.make_recombine(self.study, [c, a, d])
        objects.make_recombine(self.study, [a])  # twice: listed once
        self.study.MeshSizesGroup.VolumeAlgorithm = "HXT"  # no longer refused here
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        ids = {v["name"]: v["mat_id"] for v in job["volumes"]}
        self.assertEqual(job["recombine"], [ids["A"], ids["C"]])
        self.assertEqual(job["options"]["Mesh.RecombinationAlgorithm"], 1)
        self.assertNotIn("Mesh.RecombineAll", job["options"])

    def test_job_without_recombine_items_has_no_recombine_key(self):
        self.include(self.box("A"))
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("recombine", json.load(fh))

    def test_2d_job_gets_recombine_and_meshes_quads_only_there(self):
        a, b = self.face("A"), self.face("B")
        b.Placement.Base = App.Vector(10, 0, 0)
        study = self.make_2d_study(a, b)
        study.MeshSizesGroup.RecombinationAlgorithm = "Blossom full-quad"
        objects.make_recombine(study, [a])
        path = jobwriter.write_job(study)
        r = subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Recombined      A", r.stdout)
        self.assertEqual(
            msh_element_types(os.path.join(self.tmp.name, "pre_geom2D.msh"), 2), {2, 3}, "triangles and quads"
        )

    def three_blocks(self):
        """Two squares and a pentagon in a row, fused so they share the edges x = 10 and x = 20."""
        pts = [(20, 0), (30, 0), (30, 10), (25, 13), (20, 10)]
        pentagon = Part.Face(Part.makePolygon([App.Vector(x, y, 0) for x, y in pts + pts[:1]]))
        parts = [Part.makePlane(10, 10, App.Vector(10, 0, 0)), pentagon]
        obj = self.doc.addObject("Part::Feature", "Core")
        obj.Shape = Part.makePlane(10, 10).generalFuse(parts)[0]
        return obj

    def vertex_at(self, body, x, y):
        for i, v in enumerate(body.Shape.Vertexes, 1):
            if abs(v.Point.x - x) < 1e-6 and abs(v.Point.y - y) < 1e-6:
                return f"Vertex{i}"
        raise AssertionError(f"no vertex at {(x, y)}")

    def nearest_face(self, body, x, y):
        faces = body.Shape.Faces
        best = min(range(len(faces)), key=lambda i: faces[i].CenterOfMass.distanceToPoint(App.Vector(x, y, 0)))
        return f"Face{best + 1}"

    def run_mesher2d(self, study):
        r = subprocess.run(
            [sys.executable, MESHER2D, jobwriter.write_job(study)],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r, os.path.join(self.tmp.name, "pre_geom2D.msh")

    def faces_of_msh(self, msh):
        """{centre x (5, 15 or 25) of a face entity: [(element type, signed area of its corner nodes), ...]}"""
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(msh)
            xy = {}
            for tag in gmsh.model.mesh.getNodes()[0]:
                xy[int(tag)] = gmsh.model.mesh.getNode(int(tag))[0][:2]
            out = {}
            for _, ent in gmsh.model.getEntities(2):
                types, _, nodes = gmsh.model.mesh.getElements(2, ent)
                elements, xs = [], []
                for t, ns in zip(types, nodes):
                    k = 3 if t == 2 else 4
                    for j in range(0, len(ns), k):
                        pts = [xy[int(n)] for n in ns[j : j + k]]
                        area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1])) / 2
                        elements.append((int(t), area))
                        xs += [p[0] for p in pts]
                out[round((sum(xs) / len(xs) - 5) / 10) * 10 + 5] = elements  # the block: 5, 15 or 25
            return out
        finally:
            gmsh.finalize()

    def assert_no_inverted(self, msh):
        for x, elements in self.faces_of_msh(msh).items():
            areas = [a for _, a in elements]
            self.assertTrue(all(abs(a) > 1e-9 for a in areas), f"degenerate element near x = {x}")
            self.assertTrue(all(a > 0 for a in areas) or all(a < 0 for a in areas), f"inverted element near x = {x}")

    def test_all_blocks_structured_with_corners_on_the_pentagon(self):  # A1
        core = self.three_blocks()
        study = self.make_2d_study(core)
        corners = [self.vertex_at(core, x, y) for x, y in ((20, 0), (30, 0), (30, 10), (20, 10))]
        objects.make_transfinite_body(study, [core], [(core, v) for v in corners])
        edges = self.all_edges(core)
        roof = [e for e in edges if core.Shape.getElement(e[1]).BoundBox.YMax > 10.5]
        self.assertEqual(len(roof), 2)
        objects.make_transfinite_edges(study, 2, roof)
        objects.make_transfinite_edges(study, 4, [e for e in edges if e not in roof])
        objects.make_recombine(study, [core])
        r, msh = self.run_mesher2d(study)
        self.assertIn("Structured      Core", r.stdout)
        self.assertEqual(msh_element_types(msh, 2), {3}, "only quadrangles")
        self.assertEqual(sorted(self.faces_of_msh(msh)), [5, 15, 25])
        self.assert_no_inverted(msh)

    def test_only_the_middle_block_structured(self):  # A2
        core = self.three_blocks()
        study = self.make_2d_study(core)
        middle = self.nearest_face(core, 15, 5)
        objects.make_transfinite_body(study, []).References = [(core, middle)]
        objects.make_transfinite_edges(study, 4, self.face_edges(core, middle))
        objects.make_recombine(study, []).References = [(core, middle)]
        r, msh = self.run_mesher2d(study)
        self.assertIn(f"Structured      Core {middle}", r.stdout)
        faces = self.faces_of_msh(msh)
        self.assertEqual(sorted(faces), [5, 15, 25])
        self.assertEqual({t for t, _ in faces[15]}, {3}, "middle block: quadrangles only")
        self.assertEqual({t for t, _ in faces[5]}, {2}, "left block: triangles only")
        self.assertEqual({t for t, _ in faces[25]}, {2}, "pentagon: triangles only")
        self.assert_no_inverted(msh)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(msh)
            tags, coords, _ = gmsh.model.mesh.getNodes()
            for x in (10, 20):
                on_line = [int(t) for t, c in zip(tags, zip(coords[0::3], coords[1::3])) if abs(c[0] - x) < 1e-6]
                self.assertEqual(len(on_line), 5, f"x = {x}")
        finally:
            gmsh.finalize()

    def test_recombine_on_one_face_only(self):  # A3
        core = self.three_blocks()
        study = self.make_2d_study(core)
        objects.make_recombine(study, []).References = [(core, self.nearest_face(core, 15, 5))]
        r, msh = self.run_mesher2d(study)
        faces = self.faces_of_msh(msh)
        self.assertIn(3, {t for t, _ in faces[15]}, "middle block has quadrangles")
        self.assertEqual({t for t, _ in faces[5]}, {2})
        self.assertEqual({t for t, _ in faces[25]}, {2})

    def test_uniform_items_on_a_shared_edge_ignore_their_bump_coefficient(self):
        a, b = self.face("A"), self.face("B")
        b.Placement.Base = App.Vector(10, 0, 0)  # touches A along x = 10
        study = self.make_2d_study(a, b)
        objects.make_transfinite_body(study, [a, b])
        objects.make_transfinite_edges(study, 4, self.all_edges(a), "Uniform", 0.5)
        objects.make_transfinite_edges(study, 4, self.all_edges(b), "Uniform", 0.3)  # e.g. Bump tried, then undone
        path = jobwriter.write_job(study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual([e["coef"] for e in job["transfinite"]["edges"]], [1.0, 1.0])
        r = subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_written_job_meshes(self):
        a, b = self.box("A"), self.box("B", 10)
        self.include(a)
        self.include(b)
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
        (material,) = self.assign([a])
        copper = objects.make_library_material(second, json.dumps(record("user:copper", "Copper", "conductor")))
        (other,) = objects.assign(second, [a], copper, 0)
        objects.update_ids(self.study)
        self.assertIsNone(objects.find_study(self.doc))
        self.assertEqual(objects.owner_study(material), self.study)
        self.assertEqual(objects.owner_study(other), second)
        self.assertEqual(objects.owner_study(second.MeshSizesGroup), second)
        self.assertIsNone(objects.owner_study(a))  # a reference does not imply ownership
        self.assertEqual(second.MatIds, {})
        self.assertEqual(objects.assignment_of(second), {"A": other})
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
        a, b = self.face("A"), self.face("B", 5)  # b is lifted to z = 5
        part = self.doc.addObject("App::Part", "Part")
        part.addObject(a)
        part.Placement.Base = App.Vector(0, 0, 5)  # and so is a, by its Part
        self.doc.recompute()
        for lifted in (a, b):
            found, errors = geometry.collect([lifted], "2D")
            self.assertEqual(found, [])
            self.assertIn("XY plane", errors[0])
            self.assertIn(lifted.Label, errors[0])
        part.Placement = App.Placement()
        self.doc.recompute()
        self.assertEqual(geometry.collect([a], "2D"), ([a], []))
        self.assertIn("at least one solid", geometry.collect([b], "3D")[1][0])
        self.assertIn("without solids", geometry.collect([self.box("Solid")], "2D")[1][0])

    def sketched_face_aligned_to(self, other):
        """A Part::Face of a sketch that uses other's Edge1 as external geometry: a reference, not an input."""
        sketch = self.doc.addObject("Sketcher::SketchObject", "Sketch")
        sketch.addExternal(other.Name, "Edge1")
        sketch.addGeometry(
            [
                Part.LineSegment(App.Vector(0, 0, 0), App.Vector(10, 0, 0)),
                Part.LineSegment(App.Vector(10, 0, 0), App.Vector(10, -10, 0)),
                Part.LineSegment(App.Vector(10, -10, 0), App.Vector(0, -10, 0)),
                Part.LineSegment(App.Vector(0, -10, 0), App.Vector(0, 0, 0)),
            ]
        )
        face = self.doc.addObject("Part::Face", "Aligned")
        face.Sources = [sketch]
        self.doc.recompute()
        self.assertIn(other, face.OutListRecursive)  # the reference FreeCAD records
        return face

    def test_body_a_sketch_only_references_stays_a_body(self):
        coil = self.face("Coil")
        aligned = self.sketched_face_aligned_to(coil)
        self.assertEqual(geometry.collect([aligned, coil], "2D"), ([aligned, coil], []))

    def test_2d_faces_may_be_in_the_zx_plane_but_not_in_both(self):
        xy, zx = self.face("XY"), self.face("ZX")
        zx.Placement = App.Placement(
            App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90)
        )  # (x, y, 0) -> (x, 0, y)
        self.doc.recompute()
        self.assertEqual(geometry.collect([zx], "2D"), ([zx], []))
        found, errors = geometry.collect([xy, zx], "2D")
        self.assertEqual(found, [xy])
        self.assertIn("share one plane", errors[0])

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
        self.include(self.box("A"))
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

    def test_sliding_without_moving_geometry_cannot_change_ids_or_write_files(self):
        self.include(self.box("A"))
        self.study.Movement = "Sliding motion"
        self.assertEqual(geometry.export_unavailable(self.study), "")
        with self.assertRaisesRegex(jobwriter.StudyError, "Moving geometry: No geometry chosen"):
            jobwriter.write_job(self.study)
        self.assertEqual(self.study.MatIds, {})
        self.assertFalse(os.path.exists(self.scratch("job.json")))

    def test_sliding_motion_is_no_longer_refused_as_a_later_phase(self):
        study = objects.make_study(self.doc, "2D", "Section")
        self.assertEqual(geometry.export_unavailable(study), "")
        study.Movement = "Sliding motion"
        self.assertEqual(geometry.export_unavailable(study), "")
        texts = [p.text for p in validation.validate(study)]
        self.assertNotIn("later phase", " ".join(texts))
        self.assertIn("Sliding motion needs an Air Region and at least one Sliding Interface.", texts)

    def test_new_study_requires_geometry_even_when_materials_exist(self):
        study = objects.make_study(self.doc)
        self.assertEqual(study.MainMode, "Unassigned")
        steel = objects.make_library_material(
            study, json.dumps(record("user:steel", "Steel", "electrical_steel", STEEL))
        )
        objects.assign(study, [self.box("A")], steel, 0)
        with self.assertRaisesRegex(jobwriter.StudyError, "No geometry chosen. Select the Study"):
            jobwriter.check(study)

    def test_selected_geometry_controls_export_and_filters_other_assignments(self):
        a, b, outside = self.box("A"), self.box("B", 10), self.box("Outside", 20)
        source = self.doc.addObject("App::Part", "Stator")
        source.addObject(b)
        source.addObject(a)
        self.study.MainMode, self.study.MainSource = "Container", source
        # Invalid assignments outside the source must not affect its mesh.
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

    def make_2d_study(self, *faces):
        study = objects.make_study(self.doc, "2D", "Section")
        study.MainMode, study.MainObjects = "Manual", list(faces)
        study.MeshSizesGroup.DefaultMeshSize = 5
        return study

    def test_2d_study_writes_a_2d_job_and_meshes_it(self):
        a, b = self.face("A"), self.face("B")
        b.Placement.Base = App.Vector(10, 0, 0)  # touches A along x = 10
        study = self.make_2d_study(a, b)
        objects.make_mesh_size(study, 1.0, [(a, "Edge1")])
        path = jobwriter.write_job(study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual(job["dimension"], "2D")
        self.assertEqual([(v["mat_id"], v["name"]) for v in job["bodies"]], [(1, "A"), (2, "B")])
        self.assertNotIn("volumes", job)
        self.assertNotIn("surfaces", job)
        self.assertEqual(len(job["sizes"]), 1)
        self.assertNotIn("Mesh.Algorithm3D", job["options"])
        self.assertEqual(job["mesh_file"], os.path.join(self.tmp.name, "pre_geom2D.msh"))
        result = subprocess.run(
            [sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with open(job["mesh_file"], encoding="utf-8") as fh:
            names = fh.read().split("$PhysicalNames\n", 1)[1].split("$EndPhysicalNames", 1)[0]
        self.assertIn('2 1 "A"', names)
        self.assertIn('2 2 "B"', names)

    def test_3d_job_keeps_its_old_shape(self):
        self.include(self.box("A"))
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertNotIn("dimension", job)
        self.assertEqual([v["name"] for v in job["volumes"]], ["A"])
        self.assertIn("Mesh.Algorithm3D", job["options"])

    def test_2d_study_ignores_excitation_items(self):
        a = self.face("A")
        study = self.make_2d_study(a)
        objects.make_excitation(study, "Terminal", [(a, "Face1")])
        with open(jobwriter.write_job(study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertNotIn("surfaces", job)
        self.assertEqual(study.SmatIds, {})

    def test_2d_body_outside_the_planes_is_a_study_error(self):
        study = self.make_2d_study(self.face("Lifted", 5))
        with self.assertRaisesRegex(jobwriter.StudyError, "XY plane"):
            jobwriter.check(study)

    def test_bodies_without_materials_are_meshed_and_listed(self):
        a, b = self.box("A"), self.box("B", 10)
        self.study.MainMode, self.study.MainObjects = "Manual", [a, b]
        self.assertEqual(geometry.export_unavailable(self.study), "")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual([(v["mat_id"], v["name"]) for v in job["volumes"]], [(1, "A"), (2, "B")])
        self.assertEqual(objects.bodies_without_material(self.study), [a, b])
        self.assign([a])
        self.assertEqual(objects.bodies_without_material(self.study), [b])

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

    # --- Bodies of several solids -------------------------------------------

    def sliced_coil(self, name="Coil", two_d=False):
        """An L of three 10 mm cubes (or squares at z = 0), one body: sliced like Part Slice, so the pieces
        share their faces (edges)."""
        if two_d:
            ell = Part.makePlane(20, 10).fuse(Part.makePlane(10, 20)).removeSplitter()
        else:
            ell = Part.makeBox(20, 10, 10).fuse(Part.makeBox(10, 20, 10)).removeSplitter()
        cuts = [
            [(10, -5, -5), (10, 25, -5), (10, 25, 15), (10, -5, 15)],
            [(-5, 10, -5), (25, 10, -5), (25, 10, 15), (-5, 10, 15)],
        ]
        tools = [Part.Face(Part.makePolygon([App.Vector(*p) for p in c + c[:1]])) for c in cuts]
        obj = self.doc.addObject("Part::Feature", name)
        obj.Shape = SplitAPI.slice(ell, tools, "Split")
        self.doc.recompute()
        return obj

    def face_at(self, body, x, y, z=0):
        """Name of the face of body whose center is at (x, y, z)."""
        for i, f in enumerate(body.Shape.Faces, 1):
            if f.CenterOfMass.distanceToPoint(App.Vector(x, y, z)) < 1e-6:
                return f"Face{i}"
        raise AssertionError(f"no face at {(x, y, z)}")

    def run_mesher(self):
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), r

    def test_body_of_three_solids_is_one_mat_id(self):
        coil = self.sliced_coil()
        self.assertEqual(len(coil.Shape.Solids), 3)
        self.include(coil, self.box("Iron", 40))
        job, r = self.run_mesher()
        self.assertEqual(self.study.MatIds, {"Coil": "1", "Iron": "2"})
        self.assertEqual([v["name"] for v in job["volumes"]], ["Coil", "Iron"])
        self.assertIn("MAT_ID       1  Coil", r.stdout)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(os.path.join(self.tmp.name, "pre_geom.msh"))
            self.assertEqual(sorted(t for d, t in gmsh.model.getPhysicalGroups() if d == 3), [1, 2])
            self.assertEqual(len(gmsh.model.getEntitiesForPhysicalGroup(3, 1)), 3, "every piece")
        finally:
            gmsh.finalize()

    def test_transfinite_body_of_three_solids_meshes_to_hexahedra(self):
        coil = self.sliced_coil()
        self.include(coil)
        objects.make_transfinite_body(self.study, [coil])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(coil))
        objects.make_recombine(self.study, [coil])
        self.run_mesher()
        msh = os.path.join(self.tmp.name, "pre_geom.msh")
        self.assertEqual(msh_element_types(msh, 3), {5}, "only hexahedra, also on the faces between the pieces")
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(msh)
            hexes = sum(
                len(gmsh.model.mesh.getElements(3, v)[1][0]) for v in gmsh.model.getEntitiesForPhysicalGroup(3, 1)
            )
            self.assertEqual(hexes, 3 * 27)
        finally:
            gmsh.finalize()

    def test_unsliced_piece_of_a_transfinite_body_is_named(self):
        ell = Part.makeBox(20, 10, 10).fuse(Part.makeBox(10, 20, 10)).removeSplitter()
        body = self.doc.addObject("Part::Feature", "Coil")
        body.Shape = ell.generalFuse([Part.makeBox(10, 10, 10, App.Vector(20, 0, 0))])[0]  # 8 faces + 6 faces
        self.doc.recompute()
        self.include(body)
        objects.make_transfinite_body(self.study, [body])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(body))
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("structured body Coil: piece at (", r.stderr)
        self.assertIn("has 8 faces, needs 5 or 6", r.stderr)

    def test_excitation_faces_on_two_pieces_are_one_smat_id(self):
        coil = self.sliced_coil()
        self.include(coil)
        ends = [(coil, self.face_at(coil, 20, 5, 5)), (coil, self.face_at(coil, 5, 20, 5))]
        objects.make_excitation(self.study, "T", ends)
        job, r = self.run_mesher()
        (surface,) = job["surfaces"]
        self.assertEqual((surface["name"], len(surface["files"])), ("T_Coil", 2))
        self.assertEqual(len(self.study.SmatIds), 1)
        self.assertIn("SMAT_ID", r.stdout)

    def test_transfinite_compound_of_touching_solids_is_refused(self):
        coil = self.doc.addObject("Part::Feature", "Coil")
        coil.Shape = Part.makeCompound([Part.makeBox(10, 10, 10), Part.makeBox(10, 10, 10, App.Vector(10, 0, 0))])
        self.include(coil)
        objects.make_transfinite_body(self.study, [coil])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(coil))
        self.assertStudyError("touch without sharing faces. Make it with Part Slice or Boolean Fragments")

    def test_2d_body_of_three_faces_is_one_mat_id_and_meshes_to_quads(self):
        coil = self.sliced_coil(two_d=True)
        self.assertEqual((len(coil.Shape.Faces), len(coil.Shape.Solids)), (3, 0))
        study = self.make_2d_study(coil)
        objects.make_transfinite_body(study, [coil])
        objects.make_transfinite_edges(study, 3, self.all_edges(coil))
        objects.make_recombine(study, [coil])
        path = jobwriter.write_job(study)
        r = subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(study.MatIds, {"Coil": "1"})
        msh = os.path.join(self.tmp.name, "pre_geom2D.msh")
        self.assertEqual(msh_element_types(msh, 2), {3}, "only quadrangles, also along the edges between the pieces")
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(msh)
            faces = gmsh.model.getEntitiesForPhysicalGroup(2, 1)
            self.assertEqual(len(faces), 3, "every piece")
            self.assertEqual(sum(len(gmsh.model.mesh.getElements(2, f)[1][0]) for f in faces), 3 * 9)
        finally:
            gmsh.finalize()

    def test_2d_unsliced_piece_of_a_transfinite_body_is_named(self):
        ell = Part.makePlane(20, 10).fuse(Part.makePlane(10, 20)).removeSplitter()
        body = self.doc.addObject("Part::Feature", "Coil")
        body.Shape = ell.generalFuse([Part.makePlane(10, 10, App.Vector(20, 0, 0))])[0]  # 6 corners + 4 corners
        self.doc.recompute()
        study = self.make_2d_study(body)
        objects.make_transfinite_body(study, [body])
        objects.make_transfinite_edges(study, 3, self.all_edges(body))
        path = jobwriter.write_job(study)
        r = subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("structured body Coil: face at (", r.stderr)
        self.assertIn("it needs 3 or 4", r.stderr)

    def test_2d_transfinite_compound_of_touching_faces_is_refused(self):
        coil = self.doc.addObject("Part::Feature", "Coil")
        coil.Shape = Part.makeCompound([Part.makePlane(10, 10), Part.makePlane(10, 10, App.Vector(10, 0, 0))])
        study = self.make_2d_study(coil)
        objects.make_transfinite_body(study, [coil])
        objects.make_transfinite_edges(study, 3, self.all_edges(coil))
        with self.assertRaises(jobwriter.StudyError) as ctx:
            jobwriter.check(study)
        self.assertIn("the faces of Coil touch without sharing edges. Make it with Part Slice", str(ctx.exception))

    # --- Validation -----------------------------------------------------------

    def problems(self, severity):
        return [p.text for p in validation.validate(self.study) if p.severity == severity]

    def test_deleting_a_body_leaves_empty_items_that_refuse_the_mesh(self):
        a, b = self.box("A"), self.box("B", 10)
        self.assign([a, b])
        objects.make_excitation(self.study, "OnlyA", [(a, "Face1")])
        objects.make_excitation(self.study, "Both", [(a, "Face1"), (b, "Face2")])
        objects.make_mesh_size(self.study, 1.0, [(a, "")])
        objects.make_transfinite_body(self.study, [a], [(a, "Vertex1")])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        objects.make_recombine(self.study, [a])
        self.doc.removeObject("A")
        self.doc.recompute()
        errors = self.problems(validation.ERROR)
        for kind in ("Excitation OnlyA", "Mesh Size MeshSize", "Transfinite Body", "Transfinite Edges", "Recombine"):
            self.assertTrue(any(e.startswith(kind) and "refers to nothing" in e for e in errors), (kind, errors))
        self.assertFalse(any("Both" in e for e in errors), "an item that keeps a body is fine")
        self.assertIn("Material assignment A: Steel has no body", self.problems(validation.WARNING)[0])
        with self.assertRaises(jobwriter.StudyError) as ctx:
            jobwriter.check(self.study)
        self.assertEqual(str(ctx.exception).count("refers to nothing"), 5, "every problem, not only the first")

    def test_items_on_bodies_outside_the_main_geometry_are_a_warning(self):
        a, outside = self.box("A"), self.box("Outside", 20)
        self.include(a)
        objects.make_recombine(self.study, [a, outside])
        self.assertEqual(self.problems(validation.ERROR), [])
        self.assertIn(
            "Recombine Recombine is not used for Outside: not in the main geometry.", self.problems("warning")
        )
        jobwriter.check(self.study)

    def test_validation_lists_every_error(self):
        a = self.box("A")
        self.include(a)
        self.study.MeshSizesGroup.DefaultMeshSize = 0
        objects.make_mesh_size(self.study, 0.0, [(a, "Face1")])
        objects.make_excitation(self.study, "Gone", [])
        errors = self.problems(validation.ERROR)
        self.assertEqual(len(errors), 3, errors)

    def test_body_picked_together_with_a_cut_made_from_it_is_a_warning(self):
        air, coil = self.box("AirBox", 0, 30), self.box("Coil", 10)
        cut = self.doc.addObject("Part::Cut", "Air")
        cut.Base, cut.Tool = air, coil
        self.doc.recompute()
        self.include(cut, coil)
        (warning,) = [w for w in self.problems(validation.WARNING) if "not meshed on its own" in w]
        self.assertTrue(warning.startswith("Coil is not meshed on its own: Air is made from it."), warning)

    def test_body_a_sketch_only_references_is_not_reported_as_skipped(self):
        coil = self.doc.addObject("Part::Feature", "Coil")
        coil.Shape = Part.makePlane(10, 10)
        aligned = self.sketched_face_aligned_to(coil)
        study = objects.make_study(self.doc, "2D", "Section")
        study.MainMode, study.MainObjects = "Manual", [aligned, coil]
        self.assertEqual(objects.study_bodies(study), [aligned, coil])
        texts = [p.text for p in validation.validate(study) if "not meshed on its own" in p.text]
        self.assertEqual(texts, [])

    def test_bodies_without_material_are_a_warning(self):
        self.include(self.box("A"))
        self.assertEqual(
            self.problems(validation.WARNING), ["No material (the input file needs one for every body): A"]
        )

    def test_ids_come_back_after_undo_but_not_to_a_new_object_with_the_same_name(self):
        self.doc.UndoMode = 1
        a, b = self.box("A"), self.box("B", 10)
        self.include(a, b)
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        before = self.ids()
        self.doc.openTransaction("Delete A")
        self.doc.removeObject("A")
        self.doc.commitTransaction()
        objects.update_ids(self.study)  # e.g. a mesh run in between
        self.assertEqual(self.ids(), ({"B": "2"}, {}))
        self.doc.undo()
        objects.update_ids(self.study)
        self.assertEqual(self.ids(), before)
        self.doc.openTransaction("Delete A")
        self.doc.removeObject("A")
        self.doc.commitTransaction()
        objects.update_ids(self.study)
        new = self.box("A", 20)  # FreeCAD gives the free name A again
        self.assertEqual(new.Name, "A")
        self.include(new)
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "2", "A": "3"})

    def test_id_comes_back_when_a_body_returns_to_the_main_geometry(self):
        a, b = self.box("A"), self.box("B", 10)
        self.include(a, b)
        objects.update_ids(self.study)
        self.study.MainObjects = [b]
        objects.update_ids(self.study)
        c = self.box("C", 20)
        self.study.MainObjects = [b, c, a]
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "2", "C": "3", "A": "1"})

    def test_mesher_check_only_writes_nothing(self):
        coil = self.sliced_coil()
        self.include(coil)
        path = jobwriter.write_job(self.study)
        r = subprocess.run(
            [sys.executable, MESHER, path, "--check"], capture_output=True, encoding="utf-8", errors="replace"
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("CHECK OK", r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "pre_geom.msh")))
        self.assertFalse(os.path.exists(self.scratch("mesh.unv")))

    def test_mesher_check_only_finds_a_piece_that_cannot_be_structured(self):
        for two_d, script, shape in (
            (False, MESHER, lambda: Part.makeBox(20, 10, 10).fuse(Part.makeBox(10, 20, 10)).removeSplitter()),
            (True, MESHER2D, lambda: Part.makePlane(20, 10).fuse(Part.makePlane(10, 20)).removeSplitter()),
        ):
            with self.subTest(two_d=two_d):
                body = self.doc.addObject("Part::Feature", "L2" if two_d else "L")
                body.Shape = shape()
                self.doc.recompute()
                study = self.make_2d_study(body) if two_d else self.study
                if not two_d:
                    self.include(body)
                objects.make_transfinite_body(study, [body])
                objects.make_transfinite_edges(study, 3, self.all_edges(body))
                path = jobwriter.write_job(study)
                r = subprocess.run(
                    [sys.executable, script, path, "--check"], capture_output=True, encoding="utf-8", errors="replace"
                )
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("ERROR: structured body", r.stderr)


if __name__ == "__main__":
    unittest.main()
