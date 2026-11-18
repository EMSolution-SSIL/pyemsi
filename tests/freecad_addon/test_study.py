"""Study, ID table and job writer tests.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_study.py"""

import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import FreeCAD as App
import Part
import gmsh
from BOPTools import SplitAPI

from emsolution import geometry, jobwriter, objects, sweeps, validation

from .materialdata import STEEL, record
from .test_sweeps import helix_pipe, racetrack
from .test_mesher import inner_free_faces

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

    def exclude(self, *bodies):
        """Leave bodies (or containers) out of the Study."""
        objects.set_excluded(self.study, [*self.study.Excluded, *bodies])

    def replace_study(self, dimension="2D", label="Section"):
        """A new Study in place of self.study: one Study per document."""
        objects.delete_contents(self.study)
        self.doc.removeObject(self.study.Name)
        self.study = objects.make_study(self.doc, dimension, label)
        return self.study

    def steel(self):
        """The Study's Steel library material, made on first use."""
        found = [o for o in objects.library_materials(self.study) if o.MaterialId == "user:steel"]
        return found[0] if found else self.lib()

    def assign(self, bodies, potential=0, lib=None):
        """Assignments on bodies; lib defaults to Steel."""
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

    def test_refine_near_defaults_and_row(self):
        a = self.box("A")
        self.study.MeshSizesGroup.DefaultMeshSize = 4.0
        item = objects.make_refine_near(self.study, [(a, "Edge1")])
        self.assertEqual((item.FineSize.Value, item.CoarseSize.Value, item.GrowthDistance.Value), (2.0, 4.0, 10.0))
        self.assertEqual(item.FineDistance.Value, 0.0)
        self.assertEqual(objects.refine_items(self.study), [item])
        self.assertTrue(objects.is_item(item))
        self.assertEqual(objects.item_refs(item), [(a, "Edge1")])
        self.assertEqual(
            objects.mesh_size_rows(self.study),
            [(item, [(a, "Edge1")], ["RefineNear", "2 → 4 mm over 10 mm", "A.Edge1"])],
        )

    def test_refine_near_row_names_its_limit(self):
        a = self.box("A")
        objects.make_refine_near(self.study, [(a, "Face2")], 0.4, 4, 10, limit_to=[a])
        self.assertEqual(objects.mesh_size_rows(self.study)[0][2][1], "0.4 → 4 mm over 10 mm in A")

    def test_ids_follow_tree_order_and_stay_after_adding_a_body(self):
        for name, x in (("A", 0), ("B", 10), ("C", 20)):
            self.box(name, x)
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"A": "1", "B": "2", "C": "3"})
        self.box("D", 30)
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"A": "1", "B": "2", "C": "3", "D": "4"})

    def test_surface_ids_one_per_excitation_and_body(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_excitation(self.study, "Terminal", [(a, "Face1"), (a, "Face2"), (b, "Face1")])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[1], {"Excitation|A": "1001", "Excitation|B": "1002"})

    def test_rename_keeps_id_and_changes_name(self):
        a = self.box("A")
        objects.update_ids(self.study)
        a.Label = "Coil"
        objects.update_ids(self.study)
        self.assertEqual(objects.id_rows(self.study), [("MatIds", "A", "Coil", 1)])

    def test_deleted_body_id_is_not_reused(self):
        self.box("A"), self.box("B", 10)
        objects.update_ids(self.study)
        self.doc.removeObject("B")
        self.box("C", 20)
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"A": "1", "C": "3"})

    def test_set_id_refuses_duplicates_and_raises_counter(self):
        a, _ = self.box("A"), self.box("B", 10)
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        with self.assertRaises(ValueError):
            objects.set_id(self.study, "MatIds", "A", 2)
        with self.assertRaises(ValueError):
            objects.set_id(self.study, "MatIds", "A", 1001)
        objects.set_id(self.study, "MatIds", "A", 50)
        self.assertEqual(self.study.NextMatId, 51)
        self.box("C", 20)
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds["C"], "51")

    def test_study_is_made_with_the_chosen_movement(self):
        self.assertEqual(self.study.Movement, "No movement")
        sliding = objects.make_study(self.doc, "2D", "Slider", "Sliding motion")
        self.assertEqual((sliding.Dimension, sliding.Movement), ("2D", "Sliding motion"))
        with self.assertRaises(ValueError):
            objects.make_study(self.doc, "2D", "Bad", "Spinning")

    def test_study_has_mat_and_smat_tables_only(self):
        for prop in ("MatIds", "SmatIds", "NextMatId", "NextSmatId"):
            self.assertIn(prop, self.study.PropertiesList)
        for prop in ("VolumeIds", "SurfaceIds", "NextVolumeId", "NextSurfaceId"):
            self.assertNotIn(prop, self.study.PropertiesList)
        self.assertEqual((self.study.NextMatId, self.study.NextSmatId), (1, 1001))

    def test_new_volume_ids_skip_numbers_used_by_surfaces(self):
        a, b = self.box("A"), self.box("B", 10)
        self.exclude(b)
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        objects.set_id(self.study, "SmatIds", "Excitation|A", 2)
        objects.set_excluded(self.study, [])
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds["B"], "3")

    def test_volume_names_are_body_labels_and_survive_reload(self):
        self.box("Air"), self.box("A", 10), self.box("B", 20)
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

    def test_an_old_study_drops_its_geometry_lists_and_gets_excluded(self):
        a, _ = self.box("A"), self.box("B", 20)
        self.study.removeProperty("Excluded")
        self.study.addProperty("App::PropertyEnumeration", "MainMode", "Geometry")
        self.study.MainMode = ["Unassigned", "Container", "Manual"]
        self.study.addProperty("App::PropertyLinkListGlobal", "MainObjects", "Geometry")
        self.study.MainObjects = [a]  # saved before the whole document was the geometry: not converted
        path = os.path.join(self.tmp.name, "old.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        self.study = objects.find_study(self.doc)
        self.assertNotIn("MainMode", self.study.PropertiesList)
        self.assertNotIn("MainObjects", self.study.PropertiesList)
        self.assertEqual((self.study.Excluded, self.study.getEditorMode("Excluded")), ([], ["Hidden"]))
        self.assertEqual([o.Name for o in objects.study_bodies(self.study)], ["A", "B"])

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
        self.assertEqual(first[0].GroupName, "A")
        self.assertFalse(hasattr(first[0], "References"))
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

    def test_assignment_label_follows_material_not_body(self):
        a = self.box("A")
        (m,) = self.assign([a])
        a.Label = "Core"
        m.LibraryMaterial.Label = "M330"
        objects.sync_labels(self.study)
        self.assertEqual((m.Label, m.GroupName), ("A: M330", "A"))

    def test_suggest_name(self):
        a, b = self.box("A"), self.box("B", 10)
        b.Label = "Coil"
        lib = self.steel()
        self.assertEqual(objects.suggest_name(self.study, [(b, "")], lib), "Coil")
        (m,) = objects.assign(self.study, [a], lib, 0, name="Coil")
        self.assertEqual(objects.suggest_name(self.study, [(b, "")], lib), "Coil_2")
        self.assertEqual(objects.suggest_name(self.study, [(b, "")], lib, own=m), "Coil")
        self.assertEqual(objects.suggest_name(self.study, [], lib), "")

    def job_volume_names(self):
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            return [v["name"] for v in json.load(fh)["volumes"]]

    def test_mesh_name_is_the_material_name(self):
        a = self.box("A")
        objects.assign(self.study, [a], self.steel(), 0, name="Core")
        self.assertEqual(self.job_volume_names(), ["Core"])
        self.assertEqual(objects.key_name(self.study, "A"), "Core")

    def test_mesh_name_without_material_is_the_body_label(self):
        self.box("A")
        self.assertEqual(self.job_volume_names(), ["A"])

    def test_renaming_the_body_keeps_the_mesh_name(self):
        a = self.box("A")
        (m,) = objects.assign(self.study, [a], self.steel(), 0, name="Core")
        a.Label = "Other"
        objects.sync_labels(self.study)
        self.assertEqual((objects.key_name(self.study, "A"), m.Label), ("Core", "Core: Steel"))

    def test_material_names_equal_after_clean_are_refused(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.assign(self.study, [a], self.steel(), 0, name="Coil 1")
        objects.assign(self.study, [b], self.steel(), 0, name="Coil_1")
        self.assertTrue(any("group names are the same" in t for t in self.problems("error")))

    def test_air_grading_defaults_and_row(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        self.study.MeshSizesGroup.DefaultMeshSize = 4.0
        item = objects.make_air_grading(self.study)
        self.assertEqual(objects.item_refs(item), [(air, "")])
        self.assertEqual((item.GrowthDistance.Value, item.FarSize.Value), (40.0, 0.0))
        self.assertEqual(objects.air_gradings(self.study), [item])
        self.assertTrue(objects.is_item(item))
        self.assertEqual(objects.mesh_size_rows(self.study)[-1][2][1], "grows over 40 mm to 4 mm")

    def test_air_grading_far_size_reads_the_air_size(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        objects.make_mesh_size(self.study, 12.0, [(air, "")])
        item = objects.make_air_grading(self.study, growth=50.0)
        self.assertEqual(objects.far_size(item), 12.0)
        item.FarSize = 30.0
        self.assertEqual(objects._size_text(item), "grows over 50 mm to 30 mm")

    def test_skin_depth_formula(self):
        self.assertAlmostEqual(objects.skin_depth(50, 5.8e7, 1), 9.35, places=2)
        self.assertAlmostEqual(objects.skin_depth(1000, 3.5e7, 1), 2.69, places=2)

    def test_skin_layer_defaults_and_row(self):
        a = self.box("A")
        item = objects.make_skin_layer(self.study, [(a, "")], 2.69)
        self.assertEqual(item.SkinDepth.Value, 2.69)
        self.assertEqual((item.ElementsPerDepth, item.LayerDepth, item.QuadLayers), (2.0, 3.0, False))
        self.assertEqual((item.Frequency, item.Conductivity, item.RelativePermeability), (50.0, 5.8e7, 1.0))
        self.assertEqual(objects.skin_layers(self.study), [item])
        self.assertTrue(objects.is_item(item))
        self.assertEqual(objects.mesh_size_rows(self.study)[-1][2][1], "δ 2.69 mm, 2/δ, 3δ")
        item.QuadLayers = True
        self.assertEqual(objects.mesh_size_rows(self.study)[-1][2][1], "δ 2.69 mm, 2/δ, 3δ, quads")

    def test_skin_layer_refuses_the_air(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        self.assertEqual(
            objects.air_refusal(objects.SkinLayer, [air]),
            f"Air Region {objects.display_name(air)} cannot have a Skin Layer.",
        )

    def test_swept_body_defaults_and_row(self):
        a = self.box("A")
        item = objects.make_swept_body(self.study, [(a, "")])
        self.assertEqual((item.PathSize.Value, item.SectionSize.Value), (0.0, 0.0))
        self.assertEqual(list(item.StartFace), [])
        self.assertEqual(objects.swept_bodies(self.study), [item])
        self.assertTrue(objects.is_item(item))
        self.assertEqual(objects.mesh_size_rows(self.study)[-1][2][1], "along body size")
        item.PathSize = 2.0
        item.SectionSize = 0.5
        self.assertEqual(objects._size_text(item), "along 2 mm, section 0.5 mm")
        objects.make_skin_layer(self.study, [(a, "")], 2.69)
        self.assertEqual(objects._size_text(item), "along 2 mm, section 0.5 mm, skin")

    def test_swept_body_refuses_the_air(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        self.assertEqual(
            objects.air_refusal(objects.SweptBody, [air]),
            f"Air Region {objects.display_name(air)} cannot be a Swept Body.",
        )

    def test_skin_layer_mu_r_from_the_material(self):
        a, b = self.box("A"), self.box("B", 10)
        props = {"electromagnetic": {"relative_permeability": {"type": "scalar", "value": 1000, "unit": "1"}}}
        lib = objects.make_library_material(self.study, json.dumps(record("user:iron", "Iron", "generic", props)))
        objects.assign(self.study, [a], lib, 0)
        self.assertEqual(objects.body_mu_r(self.study, a), 1000)
        self.assertIsNone(objects.body_mu_r(self.study, b))
        self.assertEqual(objects.make_skin_layer(self.study, [(a, "")]).RelativePermeability, 1000)
        self.assertEqual(objects.make_skin_layer(self.study, [(b, "")]).RelativePermeability, 1)

    def test_air_keeps_its_own_mesh_name(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        objects.assign(self.study, [air], self.steel(), 0, name="X")
        self.assertEqual(objects.key_name(self.study, air.Name), "Air")

    def test_material_owners_and_emptied(self):
        a, b = self.box("A"), self.box("B", 10)
        (copper,) = objects.assign(self.study, [a], self.steel(), 0, name="Copper")
        (steel,) = objects.assign(self.study, [b], self.steel(), 0, name="Steel")
        refs = [(a, ""), (b, "")]
        self.assertEqual(objects.material_owners(self.study, refs), [((a, ""), copper), ((b, ""), steel)])
        self.assertEqual(objects.material_owners(self.study, refs, own=copper), [((b, ""), steel)])
        self.assertEqual(objects.emptied_by(self.study, refs), [copper, steel])

    def test_apply_material_moves_a_body(self):
        a = self.box("A")
        lib = self.steel()
        (copper,) = objects.assign(self.study, [a], lib, 0, name="Copper")
        m = objects.make_material(self.study)
        self.assertEqual((m.Body, objects.item_refs(m)), (None, []))
        objects.apply_material(self.study, m, "Iron", lib, 2, [(a, "")])
        self.assertEqual((m.Body, m.Label, m.Potential), (a, "Iron: Steel", 2))
        self.assertEqual(objects.materials(self.study), [m])
        self.assertIs(objects.assignment_of(self.study)["A"], m)

    def test_bulk_assign_replaces_but_keeps_air_name(self):
        a = self.box("A")
        air = objects.make_air_region(self.study)
        objects.assign(self.study, [a], self.steel(), 0, name="Core")
        objects.assign(self.study, [air], self.steel(), 0, name="Air")
        lib2 = self.lib("user:air", "Vacuum", "generic")
        objects.assign(self.study, [a, air], lib2, 1)
        have = objects.assignment_of(self.study)
        self.assertEqual((have["A"].GroupName, have["A"].LibraryMaterial), ("A", lib2))
        self.assertEqual((have[air.Name].GroupName, have[air.Name].LibraryMaterial), ("Air", lib2))
        self.assertEqual((have[air.Name].Potential, len(objects.materials(self.study))), (1, 2))
        self.assertIs(objects.air_material(self.study, air), have[air.Name])

    def test_renaming_air_renames_its_material(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        (m,) = objects.assign(self.study, [air], self.steel(), 0, name="Air")
        objects.rename_air_region(self.study, air, "Gap")
        self.assertEqual((air.GroupName, m.GroupName, m.Label), ("Gap", "Gap", "Gap: Steel"))
        self.assertEqual(objects.key_name(self.study, air.Name), "Gap")

    def test_suggest_name_ignores_a_material_about_to_be_removed(self):
        a = self.box("A")
        lib = self.steel()
        (m,) = objects.assign(self.study, [a], lib, 0)  # named "A"
        self.assertEqual(objects.suggest_name(self.study, [(a, "")], lib, ignore=[m]), "A")
        self.assertFalse(objects.name_taken(self.study, "A", ignore=[m]))

    def test_names_equal_after_clean_are_taken(self):
        a, b = self.box("A"), self.box("B", 10)
        b.Label = "Coil 1"
        lib = self.steel()
        objects.assign(self.study, [a], lib, 0, name="Coil_1")  # the same mesh group name as "Coil 1"
        self.assertTrue(objects.name_taken(self.study, "Coil 1"))
        self.assertEqual(objects.suggest_name(self.study, [(b, "")], lib), "Coil 1_2")

    def test_apply_material_refuses_bodies_mixed_with_faces(self):
        a = self.box("A")
        m = objects.make_material(self.study)
        with self.assertRaises(ValueError):
            objects.apply_material(self.study, m, "M", self.steel(), 0, [(a, ""), (a, "Face1")])

    def test_assign_takes_a_name(self):
        (m,) = objects.assign(self.study, [self.box("A")], self.steel(), 0, name="Core")
        self.assertEqual((m.GroupName, m.Label), ("Core", "Core: Steel"))

    def test_old_material_gets_group_name_on_restore(self):
        a = self.box("A")
        (m,) = self.assign([a])
        m.removeProperty("GroupName")
        m.Label = "A: Steel"
        m.Proxy.onDocumentRestored(m)
        self.assertEqual((m.GroupName, m.Label), ("A", "A: Steel"))
        m.removeProperty("GroupName")
        self.doc.removeObject("A")  # an orphan: its body is gone
        m.Proxy.onDocumentRestored(m)
        self.assertEqual(m.GroupName, "A: Steel")

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

    def test_body_outside_the_study_keeps_its_row(self):
        a, outside = self.box("A"), self.box("Outside", 20)
        self.exclude(outside)
        objects.assign(self.study, [outside], self.steel(), 1)
        objects.update_ids(self.study)
        self.assertEqual(
            objects.material_rows(self.study),
            [
                (a, [(a, "")], ["A", "— none —", "1", ""]),
                (outside, [(outside, "")], ["Outside (not meshed by the Study)", "Steel", "–", "1"]),
            ],
        )
        self.assertEqual(objects.bodies_without_material(self.study), [a])

    def test_assignments_need_bodies_the_study_meshes(self):
        a, b = self.box("A"), self.box("B", 10)
        self.assertEqual(objects.assignment_problem(self.study, [a, b]), "")
        self.exclude(b)
        self.assertEqual(objects.assignment_problem(self.study, [a, a]), "")
        self.assertEqual(
            objects.assignment_problem(self.study, [a, b, b]),
            "B is excluded from the Study: tick it in the Study panel.",
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
        self.exclude(d)
        objects.assign(self.study, [d], ma.LibraryMaterial, 4)
        self.assertEqual(
            objects.material_rows(self.study)[3],
            (d, [(d, "")], ["D (not meshed by the Study)", "Steel", "–", "4"]),
        )

    def test_transfinite_items_are_listed_with_mesh_sizes(self):
        a = self.box("A")
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
        self.box("A")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            options = json.load(fh)["options"]
        self.assertNotIn("Mesh.RecombineAll", options)
        self.assertEqual(options["Mesh.RecombinationAlgorithm"], 1)

    def test_mesh_settings_go_to_the_job(self):
        self.box("A")
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
        self.box("A")
        self.study.MeshSizesGroup.MinSize = 3.0
        self.study.MeshSizesGroup.MaxSize = 2.0
        self.assertStudyError("larger than the maximum")

    def test_check_no_solid(self):
        self.face("Sheet")  # a 3D Study ignores a face: nothing is left to mesh
        self.assertStudyError("No body to mesh")

    def test_check_zero_size(self):
        a = self.box("A")
        objects.make_mesh_size(self.study, 0.0, [(a, "")])
        self.assertStudyError("greater than 0")

    def test_check_missing_face(self):
        a = self.box("A")
        objects.make_excitation(self.study, "T", [(a, "Face60")])  # a box has 6 faces
        self.assertStudyError("has no Face60")

    def test_smallest_mesh_size_wins(self):
        a = self.box("A")
        objects.make_mesh_size(self.study, 3.0, [(a, "")])
        objects.make_mesh_size(self.study, 2.0, [(a, "")])
        volumes = jobwriter.check(self.study)[0]
        self.assertEqual(volumes[0][1], 2.0)

    def test_names_equal_after_cleanup_are_refused(self):
        a = self.box("A")
        b = self.box("B", 10)
        b.Label = "A!"  # cleans to "A_"
        a.Label = "A?"  # cleans to "A_" too
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
        doc.addObject("Part::Box", "A")
        doc.recompute()
        with self.assertRaisesRegex(jobwriter.StudyError, "Save the document in the simulation folder first"):
            jobwriter.write_job(study)
        self.assertEqual(study.MatIds, {})

    def test_simulation_folder_with_spaces_and_persian_letters(self):
        self.box("A")
        folder = os.path.join(self.tmp.name, "my model مدل")
        os.mkdir(folder)
        self.doc.saveAs(os.path.join(folder, "موتور.FCStd"))
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(folder, "pre_geom.msh")))
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))

    def test_body_in_app_part_is_exported_in_global_coordinates(self):
        part = self.doc.addObject("App::Part", "Part")
        part.Placement.Base = App.Vector(100, 0, 0)
        a = self.box("A")
        a.Placement.Base = App.Vector(0, 50, 0)
        part.addObject(a)
        self.doc.recompute()
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
        a, _ = self.box("A"), self.box("B", 10)
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
        objects.make_mesh_size(self.study, 1.0, [(a, "Edge99")])  # a box has 12 edges
        self.assertStudyError("has no Edge99")

    def all_edges(self, body):
        return [(body, f"Edge{i}") for i in range(1, len(body.Shape.Edges) + 1)]

    def test_transfinite_items_go_to_the_job(self):
        a = self.box("A")
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
        self.box("A")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("transfinite", json.load(fh))

    def test_structured_body_edge_without_item_is_refused(self):
        a = self.box("A")
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a)[:11])
        self.assertStudyError("edges without Transfinite Edges: Edge12")

    def test_edge_in_two_transfinite_edges_is_refused(self):
        a = self.box("A")
        objects.make_transfinite_edges(self.study, 3, [(a, "Edge1")])
        objects.make_transfinite_edges(self.study, 4, [(a, "Edge1")])
        self.assertStudyError("A.Edge1 is in Transfinite Edges")

    def test_body_in_two_transfinite_bodies_is_refused(self):
        a = self.box("A")
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_body(self.study, [a])
        self.assertStudyError("Body A is in Transfinite Body")

    def test_corner_on_another_body_is_refused(self):
        a, b = self.box("A"), self.box("B", 10)
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
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        objects.make_transfinite_body(self.study, []).References = [(a, "Face1")]
        objects.make_recombine(self.study, []).References = [(a, "Face2")]
        self.assertStudyError("Transfinite Body TransfiniteBody: pick whole solids in a 3D Study (A.Face1).")
        self.assertStudyError("Recombine Recombine: pick whole solids in a 3D Study (A.Face2).")

    def test_structured_box_job_meshes_to_hexahedra(self):
        a = self.box("A")
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
        a, _, c, d = self.box("A"), self.box("B", 10), self.box("C", 20), self.box("D", 40)
        self.exclude(d)  # D is not meshed: skipped
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
        self.box("A")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("recombine", json.load(fh))

    def test_job_without_skin_has_no_skin_key(self):
        self.box("A")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("skin", json.load(fh))

    def test_skin_goes_to_the_job(self):
        a = self.box("A")
        objects.make_skin_layer(self.study, [(a, "")], 2.69)
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        mat_id = job["volumes"][0]["mat_id"]
        self.assertEqual(
            job["skin"],
            [{"name": "SkinLayer", "mat_ids": [mat_id], "depth": 2.69, "per_depth": 2.0, "layer": 3.0, "quads": False}],
        )

    def test_skin_lists_a_body_once(self):
        a = self.box("A")
        item = objects.make_skin_layer(self.study, [(a, "")], 2.69)
        item.References = [(a, ""), (a, "")]
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual(job["skin"][0]["mat_ids"], [job["volumes"][0]["mat_id"]])

    def test_skin_quads_only_in_2d(self):
        a = self.box("A")
        item = objects.make_skin_layer(self.study, [(a, "")], 2.69)
        item.QuadLayers = True
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertIs(json.load(fh)["skin"][0]["quads"], False)
        f = self.face("F")
        study = self.make_2d_study(f)
        item = objects.make_skin_layer(study, [(f, "")], 2.69)
        item.QuadLayers = True
        with open(jobwriter.write_job(study), encoding="utf-8") as fh:
            self.assertIs(json.load(fh)["skin"][0]["quads"], True)

    def test_job_without_swept_has_no_swept_key(self):
        self.box("A")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("swept", json.load(fh))

    def swept_job(self, shape=None, path_size=0):
        bar = self.shape_body("Bar", shape or Part.makeBox(10, 4, 40))
        self.study.MeshSizesGroup.DefaultMeshSize = 2
        item = objects.make_swept_body(self.study, [(bar, "")])
        item.PathSize = path_size
        return bar, item

    def read_job(self):
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            return json.load(fh)

    def test_swept_goes_to_the_job(self):
        self.swept_job(path_size=4)
        job = self.read_job()
        (entry,) = job["swept"]
        self.assertEqual(entry["mat_id"], job["volumes"][0]["mat_id"])
        self.assertEqual((entry["path_size"], entry["section_size"], entry["skin"]), (4, 2, None))
        self.assertIs(entry["recombine"], False)
        (solid,) = entry["solids"]
        (piece,) = solid["pieces"]
        self.assertAlmostEqual(piece["advance"], 40)
        self.assertEqual(piece["angle"], 0)
        self.assertAlmostEqual(abs(piece["axis"][2]), 1)
        self.assertEqual(len(piece["origin"]), 3)
        face = Part.read(os.path.join(jobwriter.scratch_folder(self.study), solid["profile"]))
        self.assertEqual(len(face.Faces), 1)
        self.assertTrue(isinstance(face.Faces[0].Surface, Part.Plane))
        self.assertAlmostEqual(face.Area, 40)

    def test_swept_takes_the_skin(self):
        bar, _ = self.swept_job()
        objects.make_skin_layer(self.study, [(bar, "")], 1)
        job = self.read_job()
        self.assertEqual(job["swept"][0]["skin"], {"depth": 1.0, "per_depth": 2.0, "layer": 3.0})
        self.assertNotIn("skin", job)

    def tube(self, outer=15, inner=10, height=8):
        return Part.makeCylinder(outer, height).cut(Part.makeCylinder(inner, height))

    def test_swept_ring_goes_to_the_job(self):
        self.swept_job(self.tube())
        (entry,) = self.read_job()["swept"]
        (solid,) = entry["solids"]
        self.assertIs(solid["closed"], True)
        (piece,) = solid["pieces"]
        self.assertEqual((piece["angle"], piece["advance"]), (360, 0))
        face = Part.read(os.path.join(jobwriter.scratch_folder(self.study), solid["profile"]))
        self.assertEqual(len(face.Faces), 1)
        plane = face.Faces[0].Surface
        self.assertTrue(isinstance(plane, Part.Plane))
        self.assertAlmostEqual(App.Vector(plane.Axis).dot(App.Vector(*piece["axis"])), 0)
        self.assertAlmostEqual(face.Area, 5 * 8)

    def test_swept_bend_goes_to_the_job(self):
        pts = [App.Vector(x, 0, z) for x, z in [(10, 0), (14, 0), (14, 4), (10, 4), (10, 0)]]
        bend = Part.Face(Part.makePolygon(pts)).revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90)
        self.swept_job(bend)
        (entry,) = self.read_job()["swept"]
        (solid,) = entry["solids"]
        self.assertIs(solid["closed"], False)
        (piece,) = solid["pieces"]
        self.assertAlmostEqual(piece["angle"], 90)
        self.assertEqual(piece["advance"], 0)

    def test_swept_placed_bend_is_global(self):
        pts = [App.Vector(x, 0, z) for x, z in [(10, 0), (14, 0), (14, 4), (10, 4), (10, 0)]]
        bend = Part.Face(Part.makePolygon(pts)).revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90)
        body, _ = self.swept_job(bend)
        body.Placement = App.Placement(App.Vector(100, 50, 0), App.Rotation(App.Vector(1, 0, 0), 30))
        self.doc.recompute()
        (solid,) = self.read_job()["swept"][0]["solids"]
        (piece,) = solid["pieces"]
        placement = body.Placement
        axis = placement.Rotation.multVec(App.Vector(0, 0, 1))
        self.assertLess((App.Vector(*piece["origin"]) - placement.multVec(App.Vector(0, 0, 2))).Length, 1e-6)
        self.assertAlmostEqual(abs(App.Vector(*piece["axis"]).dot(axis)), 1)
        face = Part.read(os.path.join(jobwriter.scratch_folder(self.study), solid["profile"]))
        ends = [f.CenterOfMass for f in body.Shape.Faces if isinstance(f.Surface, Part.Plane)]
        self.assertTrue(any((face.Faces[0].CenterOfMass - c).Length < 1e-6 for c in ends))

    def test_swept_straight_is_not_closed(self):
        self.swept_job()
        self.assertIs(self.read_job()["swept"][0]["solids"][0]["closed"], False)

    def test_swept_tube_start_face_makes_it_straight(self):
        tube, item = self.swept_job(self.tube(10, 8, 20))
        face = next(k for k, f in enumerate(tube.Shape.Faces, 1) if isinstance(f.Surface, Part.Plane))
        item.StartFace = [(tube, (f"Face{face}",))]
        (piece,) = self.read_job()["swept"][0]["solids"][0]["pieces"]
        self.assertAlmostEqual(piece["advance"], 20)
        self.assertEqual(piece["angle"], 0)

    def test_swept_two_solids(self):
        shape = Part.makeCompound([Part.makeBox(10, 4, 40), Part.makeBox(10, 4, 40, App.Vector(30, 0, 0))])
        self.swept_job(shape)
        (entry,) = self.read_job()["swept"]
        self.assertEqual(len(entry["solids"]), 2)
        self.assertEqual(len({s["profile"] for s in entry["solids"]}), 2)

    def test_swept_helix_goes_to_the_job(self):
        self.swept_job(helix_pipe(10, 15, 1.2, ("circle", 0.45)))
        (piece,) = self.read_job()["swept"][0]["solids"][0]["pieces"]
        self.assertAlmostEqual(piece["angle"], 540, places=4)
        self.assertAlmostEqual(piece["advance"], 15, places=5)
        self.assertAlmostEqual(abs(piece["axis"][2]), 1, places=6)

    def test_swept_chain_goes_to_the_job(self):
        path = Part.Wire(
            [
                Part.makeLine(App.Vector(0, 0, 0), App.Vector(30, 0, 0)),
                Part.Edge(
                    Part.ArcOfCircle(Part.Circle(App.Vector(30, 20, 0), App.Vector(0, 0, 1), 20), -math.pi / 2, 0)
                ),
                Part.makeLine(App.Vector(50, 20, 0), App.Vector(50, 50, 0)),
            ]
        )
        profile = Part.makePolygon([App.Vector(0, y, z) for y, z in ((-5, -2), (5, -2), (5, 2), (-5, 2), (-5, -2))])
        bar, item = self.swept_job(path.makePipeShell([profile], True, True))
        start = next(k for k, f in enumerate(bar.Shape.Faces, 1) if abs(f.CenterOfMass.x) < 1e-9)
        item.StartFace = [(bar, (f"Face{start}",))]
        first, arc, last = self.read_job()["swept"][0]["solids"][0]["pieces"]
        self.assertEqual((first["angle"], arc["advance"], last["angle"]), (0, 0, 0))
        self.assertAlmostEqual(arc["angle"], 90, places=6)
        # the profile's centre, moved by each piece: piece 2 turns it from where piece 1 ended, piece 3 starts there
        c = App.Vector(*first["origin"]) + App.Vector(*first["axis"]) * first["advance"]
        o, d = App.Vector(*arc["origin"]), App.Vector(*arc["axis"])
        self.assertLess(abs(d.dot(c - o)), 1e-6)
        self.assertAlmostEqual((c - o).Length, 20, places=6)
        c = o + App.Rotation(d, arc["angle"]).multVec(c - o)
        self.assertLess((App.Vector(*last["origin"]) - c).Length, 1e-6)
        c += App.Vector(*last["axis"]) * last["advance"]
        self.assertLess((c - App.Vector(50, 50, 0)).Length, 1e-6)

    def test_swept_racetrack_goes_to_the_job(self):
        _, item = self.swept_job(racetrack())
        objects.make_air_region(self.study)
        self.assertFalse(self.swept_texts(item))
        (solid,) = self.read_job()["swept"][0]["solids"]
        self.assertIs(solid["closed"], True)
        self.assertEqual([round(p["angle"], 6) for p in solid["pieces"]], [0, 180, 0, 180])
        face = Part.read(os.path.join(jobwriter.scratch_folder(self.study), solid["profile"]))
        self.assertAlmostEqual(face.Area, 8)

    def test_swept_rebuilt_strand_exports_the_rebuilt_solid(self):
        strand = helix_pipe(10, 15, 1.2, ("circle", 0.45), frenet=False)
        self.assertTrue(sweeps.recognise(strand).rebuild)
        self.swept_job(strand)
        job = self.read_job()
        vol = Part.read(os.path.join(jobwriter.scratch_folder(self.study), job["volumes"][0]["file"]))
        (solid,) = vol.Solids
        sweep = sweeps.recognise(solid)
        self.assertIsInstance(sweep, sweeps.Sweep)
        self.assertFalse(sweep.rebuild)  # its seam follows the screw
        self.assertAlmostEqual(sweep.pieces[0].angle, 540, places=3)
        self.assertLess(abs(solid.Volume - strand.Volume), 1e-6 * strand.Volume)

    def test_swept_job_recognises_and_rebuilds_once(self):
        # validation's check and the job it then writes share one recognition and one rebuild of the body
        self.swept_job(helix_pipe(10, 15, 1.2, ("circle", 0.45), frenet=False))
        with (
            mock.patch.object(sweeps, "_recognise", wraps=sweeps._recognise) as recognise,
            mock.patch.object(sweeps, "_rebuilt", wraps=sweeps._rebuilt) as rebuilt,
        ):
            self.read_job()
        self.assertEqual((recognise.call_count, rebuilt.call_count), (1, 1))
        self.assertIsNone(sweeps.memo)  # kept only while write_job writes the job
        with mock.patch.object(sweeps, "_recognise", wraps=sweeps._recognise) as recognise:
            self.read_job()
        self.assertEqual(recognise.call_count, 1)  # a new job recognises it anew

    def rebuilt_strand_with_excitation(self):
        """A Standard-mode strand (its seam twists: rebuilt) with an excitation on the original body's far end face.
        Returns the body and that face."""
        bar, item = self.swept_job(helix_pipe(10, 15, 1.2, ("circle", 0.45), frenet=False))
        k, end = max(
            ((k, f) for k, f in enumerate(bar.Shape.Faces, 1) if f.Surface.TypeId == "Part::GeomPlane"),
            key=lambda kf: kf[1].CenterOfMass.z,
        )
        objects.make_excitation(self.study, "In", [(bar, f"Face{k}")])
        return bar, item, end

    def test_swept_rebuilt_strand_exports_faces_of_the_rebuild(self):
        _, _, end = self.rebuilt_strand_with_excitation()
        job = self.read_job()
        folder = jobwriter.scratch_folder(self.study)
        (solid,) = Part.read(os.path.join(folder, job["volumes"][0]["file"])).Solids
        (face,) = Part.read(os.path.join(folder, job["surfaces"][0]["files"][0])).Faces
        rebuilt = min(solid.Faces, key=lambda f: f.CenterOfMass.distanceToPoint(end.CenterOfMass))
        # the seam vertex: the rebuild's follows the screw, the original's is 0.55 mm away (its seam twists)
        (vertex,) = face.Vertexes
        self.assertLess(vertex.Point.distanceToPoint(rebuilt.Vertexes[0].Point), 1e-9)
        self.assertGreater(vertex.Point.distanceToPoint(end.Vertexes[0].Point), 0.1)

    def test_swept_rebuilt_strand_excitation(self):
        bar, item, end = self.rebuilt_strand_with_excitation()
        self.study.MeshSizesGroup.DefaultMeshSize = 0.6
        item.PathSize, item.SectionSize = 0.4, 0.2  # as the mesher's strand test, which gmsh meets every time
        air = objects.make_air_region(self.study)
        air.SizeMode = "Manual"
        air.Center, air.Length, air.Width, air.Height = App.Vector(0, 0, 7.5), 6, 6, 25
        self.doc.recompute()
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        smat_id = self.read_job()["surfaces"][0]["smat_id"]
        gmsh.initialize()
        self.addCleanup(gmsh.finalize)
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(jobwriter.mesh_file(self.study))
        tags, xyz = gmsh.model.mesh.getNodesForPhysicalGroup(2, smat_id)
        self.assertGreater(len(tags), 10)
        normal = end.normalAt(*end.Surface.parameter(end.CenterOfMass))
        for k in range(0, len(xyz), 3):  # on the strand's end face: its plane, within its circle
            p = App.Vector(*xyz[k : k + 3])
            self.assertLess(abs((p - end.CenterOfMass).dot(normal)), 1e-4)
            self.assertLess((p - end.CenterOfMass).Length, 0.45 + 1e-4)

    def test_standard_coil_with_leads_rebuilt(self):
        # a Standard-mode round coil of 2 turns (its seam twists) with a straight lead 5 long piped on at each end
        coil = helix_pipe(10, 20, 1.2, ("circle", 0.45), frenet=False)
        start, end = sorted(
            (f for f in coil.Faces if isinstance(f.Surface, Part.Plane)), key=lambda f: f.CenterOfMass.z
        )
        tangent = App.Vector(0, 1.2, 10 / (2 * math.pi)).normalize()
        (shape,) = coil.fuse([start.extrude(tangent * -5), end.extrude(tangent * 5)]).Solids
        sweep = sweeps.recognise(shape)
        self.assertTrue(sweep.rebuild)
        self.assertEqual([round(p.angle, 3) for p in sweep.pieces], [0, 720, 0])
        bar, item = self.swept_job(shape)
        k, lead = max(
            ((k, f) for k, f in enumerate(bar.Shape.Faces, 1) if isinstance(f.Surface, Part.Plane)),
            key=lambda kf: kf[1].CenterOfMass.z,
        )
        objects.make_excitation(self.study, "In", [(bar, f"Face{k}")])
        self.study.MeshSizesGroup.DefaultMeshSize = 0.6
        item.PathSize, item.SectionSize = 0.4, 0.2  # as the rebuilt strand
        air = objects.make_air_region(self.study)
        air.SizeMode = "Manual"
        air.Center, air.Length, air.Width, air.Height = App.Vector(0, 0, 10), 8, 12, 40
        self.doc.recompute()
        self.assertEqual(len(self.read_job()["swept"][0]["solids"][0]["pieces"]), 3)
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        smat_id = self.read_job()["surfaces"][0]["smat_id"]
        gmsh.initialize()
        self.addCleanup(gmsh.finalize)
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(jobwriter.mesh_file(self.study))
        tags, xyz = gmsh.model.mesh.getNodesForPhysicalGroup(2, smat_id)
        self.assertGreater(len(tags), 10)
        for k in range(0, len(xyz), 3):  # on the lead's end face: its plane, within its circle
            p = App.Vector(*xyz[k : k + 3])
            self.assertLess(abs((p - lead.CenterOfMass).dot(tangent)), 1e-4)
            self.assertLess((p - lead.CenterOfMass).Length, 0.45 + 1e-4)

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
        self.assertEqual([obj.Name for obj in found], [body.Name, cut.Name], "a Cut's tool is not meshed")
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

    def air_cut_by(self, tool):
        """An air box around the coil at x = 10 with tool cut out of it."""
        box = self.box("AirBox", 0, 30)
        cut = self.doc.addObject("Part::Cut", "Air")
        cut.Base, cut.Tool = box, tool
        self.doc.recompute()
        return box, cut

    def test_the_tool_of_a_cut_is_not_meshed(self):
        coil = self.box("Coil", 10)
        box, air = self.air_cut_by(coil)
        self.assertEqual(geometry.collect([air, coil], "3D"), ([air], []))
        self.assertEqual(geometry.collect([air, box], "3D"), ([air], []), "the base is inside the result")
        self.assertEqual(geometry.tree(self.doc, "3D"), [(air, None)])

    def test_a_link_to_the_tool_of_a_cut_keeps_the_tool_a_body(self):
        coil = self.box("Coil", 10)
        link = self.doc.addObject("App::Link", "CoilLink")
        link.LinkedObject = coil
        _, air = self.air_cut_by(link)
        self.assertEqual(geometry.collect([air, coil], "3D"), ([air, coil], []))

    def coil_link(self):
        coil = self.box("Coil", 10)
        self.air_cut_by(coil)
        link = self.doc.addObject("App::Link", "CoilLink")
        link.LinkedObject = coil
        link.LinkTransform = True  # the link composes with Coil's own placement, so it stays where Coil is
        self.doc.recompute()
        return link

    def test_a_link_takes_a_material_and_a_face_size(self):
        link = self.coil_link()
        self.assign([link])
        objects.make_mesh_size(self.study, 1.0, [(link, "Face1")])
        volumes, _, elements = jobwriter.check(self.study)
        self.assertIn(link, [b for b, _ in volumes])
        self.assertEqual([(b, subs) for _, b, subs in elements], [(link, ["Face1"])])
        self.assertIs(objects.pick_body(link), link)

    def test_a_missing_face_on_a_link_is_reported(self):
        link = self.coil_link()
        self.assign([link])
        objects.make_mesh_size(self.study, 1.0, [(link, "Face99")])
        self.assertStudyError("body CoilLink has no Face99. Reselect it.")

    def test_a_link_is_written_where_it_is_displayed(self):
        link = self.coil_link()
        self.assign([link])
        jobwriter.write_job(self.study)
        found = []
        for name in os.listdir(self.scratch("geometry")):
            shape = Part.Shape()
            shape.read(self.scratch("geometry", name))
            found.append(shape.BoundBox.XMin)
        self.assertIn(10, [round(x, 6) for x in found])
        self.assertAlmostEqual(geometry.global_shape(link).BoundBox.XMin, geometry.body_shape(link).BoundBox.XMin)

    def test_the_global_shape_of_a_link_in_a_part_is_its_body_shape_moved_by_the_part(self):
        link = self.coil_link()
        part = self.doc.addObject("App::Part", "Part")
        part.Placement.Base = App.Vector(100, 0, 0)
        part.addObject(link)
        self.doc.recompute()
        self.assertAlmostEqual(geometry.global_shape(link).BoundBox.XMin, geometry.body_shape(link).BoundBox.XMin + 100)

    def test_a_body_only_an_edge_or_an_expression_refers_to_stays_a_body(self):
        coil = self.box("Coil", 10)
        ruled = self.doc.addObject("Part::RuledSurface", "Ruled")
        ruled.Curve1, ruled.Curve2 = (coil, ["Edge1"]), (coil, ["Edge3"])
        sized = self.box("Sized", 50)
        sized.setExpression("Length", "Coil.Length * 2")
        self.doc.recompute()
        self.assertNotIn(coil.Name, geometry.inputs(ruled))
        self.assertNotIn(coil.Name, geometry.inputs(sized))
        self.assertEqual(geometry.collect([sized, coil], "3D"), ([sized, coil], []))

    def test_the_source_of_a_mirror_stays_a_body(self):
        coil = self.box("Coil", 10)
        mirror = self.doc.addObject("Part::Mirroring", "Mirror")
        mirror.Source, mirror.Normal = coil, App.Vector(1, 0, 0)
        self.doc.recompute()
        self.assertEqual(geometry.collect([coil, mirror], "3D"), ([coil, mirror], []))

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

    def test_an_excluded_group_follows_rename_addition_and_deletion(self):
        source = self.doc.addObject("App::DocumentObjectGroup", "Geometry")
        a = self.box("A")
        source.addObject(a)
        self.exclude(source)
        source.Label = "Renamed"
        b = self.box("B", 10)
        source.addObject(b)
        self.doc.recompute()
        self.assertEqual(geometry.study_geometry(self.study), ([], []))
        self.doc.removeObject(source.Name)  # its bodies stay, and are meshed again
        self.assertEqual(geometry.study_geometry(self.study), ([a, b], []))
        self.assertEqual(self.study.Excluded, [])

    def test_geometry_tree_shows_containers_and_meshable_bodies(self):
        part = self.doc.addObject("App::Part", "Stator")
        a, b, c = self.box("A"), self.box("B", 20), self.box("C", 40)
        cut = self.doc.addObject("Part::Cut", "Cut")
        cut.Base, cut.Tool = b, c
        part.addObject(a)
        self.doc.addObject("App::DocumentObjectGroup", "Empty")
        flat = self.face("Flat")
        self.doc.recompute()
        self.assertEqual(geometry.tree(self.doc, "3D"), [(part, [(a, None)]), (cut, None)])
        self.assertEqual(geometry.tree(self.doc, "2D"), [(flat, None)])

    # --- the whole document is the Study's geometry ---------------------------

    def test_every_body_is_meshed_and_one_drawn_later_too(self):
        a, b = self.box("A"), self.box("B", 20)
        self.assertEqual(objects.study_bodies(self.study), [a, b])
        c = self.box("C", 40)
        self.assertEqual(objects.study_bodies(self.study), [a, b, c])

    def test_a_hidden_body_is_meshed(self):
        a = self.box("A")
        a.Visibility = False
        self.assertEqual(objects.study_bodies(self.study), [a])

    def test_an_excluded_part_keeps_out_a_body_added_later(self):
        part = self.doc.addObject("App::Part", "Helpers")
        part.addObject(self.box("H1"))
        keep = self.box("Keep", 40)
        self.exclude(part)
        part.addObject(self.box("H2", 20))
        self.assertEqual(objects.study_bodies(self.study), [keep])

    def test_an_excluded_body_stays_listed_once(self):
        a, b = self.box("A"), self.box("B", 20)
        self.exclude(b, b)
        self.assertEqual((self.study.Excluded, objects.study_bodies(self.study)), ([b], [a]))
        self.assertTrue(geometry.is_excluded(self.study, b) and not geometry.is_excluded(self.study, a))

    def test_objects_that_are_not_bodies_are_ignored(self):
        self.assign([self.box("A")])
        self.doc.addObject("Spreadsheet::Sheet", "Sheet")
        self.doc.addObject("Sketcher::SketchObject", "Sketch")
        self.doc.addObject("Fem::FemMeshObject", "Mesh")
        import Draft

        Draft.make_linear_dimension(App.Vector(0, 0, 0), App.Vector(10, 0, 0), App.Vector(5, -5, 0))
        self.doc.recompute()
        self.assertEqual(validation.errors(validation.validate(self.study)), [])
        self.assertEqual([b.Name for b in objects.study_bodies(self.study)], ["A"])

    def test_a_2d_study_ignores_solids(self):
        doc = App.newDocument("Flat")
        self.addCleanup(App.closeDocument, doc.Name)
        flat = objects.make_study(doc, "2D")
        doc.addObject("Part::Box", "Solid")
        face = doc.addObject("Part::Feature", "Face")
        face.Shape = Part.makePlane(10, 10)  # in z = 0
        doc.recompute()
        self.assertEqual(objects.study_bodies(flat), [face])
        a = self.box("A")
        self.face("Sheet", 20)
        self.doc.recompute()
        self.assertEqual(objects.study_bodies(self.study), [a], "a 3D Study ignores a face")

    def test_a_second_study_is_refused(self):
        objects.make_study(self.doc, "2D", "Other")
        texts = [p.text for p in validation.errors(validation.validate(self.study))]
        self.assertIn(f"This document has two Studies, {self.study.Label} and Other: delete one.", texts)

    def test_three_studies_are_refused(self):
        objects.make_study(self.doc, "2D", "Other")
        objects.make_study(self.doc, "3D", "Third")
        texts = [p.text for p in validation.errors(validation.validate(self.study))]
        self.assertIn(f"This document has 3 Studies, {self.study.Label}, Other and Third: delete all but one.", texts)

    def test_generate_mesh_is_refused_with_two_studies(self):
        self.box("A")
        objects.make_study(self.doc, "2D", "Other")
        with self.assertRaisesRegex(jobwriter.StudyError, "This document has two Studies"):
            jobwriter.check(self.study)

    def test_a_container_with_study_objects_is_not_a_geometry_source(self):
        group = self.doc.addObject("App::DocumentObjectGroup", "Everything")
        group.addObject(self.study)
        self.assertTrue(geometry.is_container(group))
        self.assertFalse(geometry.is_source(group))
        self.assertFalse(geometry.is_source(self.study.MaterialsGroup))

    def test_sliding_without_interfaces_cannot_change_ids_or_write_files(self):
        self.box("A")
        self.study.Movement = "Sliding motion"
        self.assertEqual(geometry.export_unavailable(self.study), "")
        with self.assertRaisesRegex(jobwriter.StudyError, "Sliding motion needs an Air Region"):
            jobwriter.write_job(self.study)
        self.assertEqual(self.study.MatIds, {})
        self.assertFalse(os.path.exists(self.scratch("job.json")))

    def test_sliding_motion_is_no_longer_refused_as_a_later_phase(self):
        study = self.replace_study()
        self.assertEqual(geometry.export_unavailable(study), "")
        study.Movement = "Sliding motion"
        self.assertEqual(geometry.export_unavailable(study), "")
        texts = [p.text for p in validation.validate(study)]
        self.assertNotIn("later phase", " ".join(texts))
        self.assertIn("Sliding motion needs an Air Region and at least one Sliding Interface.", texts)

    def test_study_requires_a_body_even_when_materials_exist(self):
        a = self.box("A")
        objects.assign(self.study, [a], self.steel(), 0)
        self.exclude(a)
        with self.assertRaisesRegex(jobwriter.StudyError, "No body to mesh"):
            jobwriter.check(self.study)

    def test_selected_geometry_controls_export_and_filters_other_assignments(self):
        a, b, outside = self.box("A"), self.box("B", 10), self.box("Outside", 20)
        source = self.doc.addObject("App::Part", "Stator")
        source.addObject(b)
        source.addObject(a)
        self.exclude(outside)
        # Invalid assignments on a body the Study does not mesh must not affect its mesh.
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
        """A 2D Study in place of the 3D one; faces: the document's faces, all meshed."""
        study = self.replace_study()
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
        self.box("A")
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
        self.assertEqual(geometry.export_unavailable(self.study), "")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual([(v["mat_id"], v["name"]) for v in job["volumes"]], [(1, "A"), (2, "B")])
        self.assertEqual(objects.bodies_without_material(self.study), [a, b])
        self.assign([a])
        self.assertEqual(objects.bodies_without_material(self.study), [b])

    def test_ids_follow_live_membership_of_the_study_geometry(self):
        _, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        source = self.doc.addObject("App::DocumentObjectGroup", "Helpers")
        source.addObject(c)
        self.exclude(source)
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds, {"A": "1", "B": "2"})
        self.assertEqual([r[2] for r in objects.id_rows(self.study)], ["A", "B"])
        source.removeObject(c)
        source.addObject(b)
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds, {"A": "1", "C": "3"})

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
        self.box("Iron", 40)
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
        objects.make_transfinite_body(self.study, [body])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(body))
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("structured body Coil: piece at (", r.stderr)
        self.assertIn("has 8 faces, needs 5 or 6", r.stderr)

    def test_excitation_faces_on_two_pieces_are_one_smat_id(self):
        coil = self.sliced_coil()
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

    def problems(self, severity=None):
        return [p.text for p in validation.validate(self.study) if severity is None or p.severity == severity]

    def test_refine_near_settings_are_checked(self):
        a = self.box("A")
        item = objects.make_refine_near(self.study, [(a, "Edge1")], 0.0, 1.0, 0.0)
        texts = self.problems()
        for end in ("the fine size must be greater than 0.", "the growth distance must be greater than 0."):
            self.assertIn(f"Refine Near {item.Label}: {end}", texts)
        item.FineSize, item.CoarseSize, item.GrowthDistance, item.FineDistance = 2.0, 1.0, 5.0, 0.0
        self.assertIn(
            f"Refine Near {item.Label}: the coarse size must not be smaller than the fine size.", self.problems()
        )

    def test_air_grading_settings_are_checked(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        item = objects.make_air_grading(self.study, [(air, "")], 0.0)
        self.assertIn(f"Air Grading {item.Label}: the growth distance must be greater than 0.", self.problems())
        item.GrowthDistance = 5.0
        self.assertFalse([t for t in self.problems() if t.startswith(f"Air Grading {item.Label}")])

    def test_air_grading_on_a_body_is_refused(self):
        a = self.box("A")
        item = objects.make_air_grading(self.study, [(a, "")], 5.0)
        self.assertIn(
            f"Air Grading {item.Label}: A is not an air. Pick the Air Region (or, in a Study with Symmetric Groups,"
            " a free object that is air).",
            self.problems("error"),
        )

    def test_air_grading_on_an_air_face_is_refused(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        item = objects.make_air_grading(self.study, [(air, "Face1")], 5.0)
        self.assertIn(f"Air Grading {item.Label}: pick the whole air, not {air.Label}.Face1.", self.problems("error"))

    def test_two_air_gradings_on_one_air(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        first = objects.make_air_grading(self.study, [(air, "")], 5.0)
        second = objects.make_air_grading(self.study, [(air, "")], 6.0)
        texts = self.problems("error")
        self.assertIn(
            f"Air Grading {second.Label}: {objects.display_name(air)} already has Air Grading {first.Label}; one per"
            " air.",
            texts,
        )
        self.assertFalse([t for t in texts if t.startswith(f"Air Grading {first.Label}:")])

    def skin_texts(self, item, severity=None):
        return [t for t in self.problems(severity) if t.startswith(f"Skin Layer {item.Label}")]

    def shape_body(self, name, shape):
        body = self.doc.addObject("Part::Feature", name)
        body.Shape = shape
        self.doc.recompute()
        return body

    def disk(self, name, radius):
        return self.shape_body(name, Part.Face(Part.Wire(Part.makeCircle(radius))))

    def test_skin_layer_settings_are_checked(self):
        """The FloatConstraints stop ElementsPerDepth and LayerDepth at 0.01, so only the skin depth can reach 0."""
        a = self.box("A")
        item = objects.make_skin_layer(self.study, [(a, "")], 0.0)
        self.assertIn(f"Skin Layer {item.Label}: the skin depth must be greater than 0.", self.problems("error"))
        item.ElementsPerDepth = 0.0
        self.assertEqual(item.ElementsPerDepth, 0.01)
        item.SkinDepth = 1.0
        self.assertFalse(self.skin_texts(item, "error"))

    def test_skin_layer_on_a_face_is_refused(self):
        a = self.box("A")
        item = objects.make_skin_layer(self.study, [(a, "Face1")])
        self.assertIn(f"Skin Layer {item.Label}: pick whole conductors, not A.Face1.", self.problems("error"))

    def test_skin_layer_on_the_air_is_refused(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        item = objects.make_skin_layer(self.study, [(air, "")])
        self.assertIn(
            f"Skin Layer {item.Label}: Air Region {objects.display_name(air)} cannot have a Skin Layer. Remove it from"
            " the item.",
            self.problems("error"),
        )

    def test_skin_layer_quads_in_3d_warns(self):
        a = self.box("A")
        item = objects.make_skin_layer(self.study, [(a, "")])
        self.assertFalse(self.skin_texts(item))
        item.QuadLayers = True
        self.assertEqual(
            self.skin_texts(item),
            [f"Skin Layer {item.Label}: quad layers are made in 2D Studies only; ignored."],
        )

    def test_skin_layer_filling_the_body_warns(self):
        self.make_2d_study()
        wire = self.disk("Wire", 2)
        item = objects.make_skin_layer(self.study, [(wire, "")])
        self.assertEqual(
            self.skin_texts(item),
            [
                f"Skin Layer {item.Label}: the layer (3 mm) is deeper than half of Wire (about 4 mm thick); the whole"
                " body is skin, so a Mesh Size of 0.5 mm on it does the same."
            ],
        )
        item.LayerDepth = 1.0
        self.assertFalse(self.skin_texts(item))

    def test_skin_layer_quads_on_a_bar_warns_and_on_a_wire_not(self):
        self.make_2d_study()
        bar = self.shape_body("Bar", Part.makePlane(20, 10))
        wire = self.disk("Wire", 5)
        wire.Placement.Base = App.Vector(40, 5, 0)
        objects.make_air_region(self.study, Center=App.Vector(20, 5, 0), Length=100, Width=60)
        self.doc.recompute()
        on_bar = objects.make_skin_layer(self.study, [(bar, "")])
        on_wire = objects.make_skin_layer(self.study, [(wire, "")])
        on_bar.QuadLayers = on_wire.QuadLayers = True
        self.assertEqual(
            self.skin_texts(on_bar),
            [
                f"Skin Layer {on_bar.Label}: Bar has sharp corners on its surface; quad layers need a smooth surface,"
                " so it gets graded triangles."
            ],
        )
        self.assertFalse(self.skin_texts(on_wire))
        on_wire.LayerDepth = 6.0  # the wire's radius 5 is below the layer's 6 mm (and the layer fills the wire)
        self.assertIn(
            f"Skin Layer {on_wire.Label}: Wire has sharp corners on its surface; quad layers need a smooth surface, so"
            " it gets graded triangles.",
            self.skin_texts(on_wire),
        )

    def test_skin_layer_quads_on_a_half_wire_not(self):
        self.make_2d_study()
        half = Part.Face(
            Part.Wire(
                [Part.makeCircle(5, App.Vector(), App.Vector(0, 0, 1), 0, 180), Part.makeLine((-5, 0, 0), (5, 0, 0))]
            )
        )
        wire = self.shape_body("Half", half)
        objects.make_air_region(self.study, Center=App.Vector(0, 25, 0), Length=100, Width=50)
        self.doc.recompute()
        item = objects.make_skin_layer(self.study, [(wire, "")])
        item.QuadLayers = True
        self.assertFalse(self.skin_texts(item))

    def test_skin_layer_quads_on_a_bar_beside_another_body_warns(self):
        """Without an Air Region, the bar's edge shared with the other body is a layer edge; it meets no other one."""
        self.make_2d_study()
        bar = self.shape_body("Bar", Part.makePlane(20, 10))
        self.shape_body("Other", Part.makePlane(20, 10, App.Vector(20, 0, 0)))
        item = objects.make_skin_layer(self.study, [(bar, "")])
        item.QuadLayers = True
        self.assertFalse(self.skin_texts(item))
        objects.make_air_region(self.study, Center=App.Vector(20, 5, 0), Length=100, Width=60)
        self.doc.recompute()
        self.assertTrue(self.skin_texts(item))

    def test_skin_layer_on_a_structured_body_warns(self):
        self.make_2d_study()
        bar = self.shape_body("Bar", Part.makePlane(20, 10))
        objects.make_transfinite_body(self.study, [bar])
        item = objects.make_skin_layer(self.study, [(bar, "")])
        self.assertEqual(
            self.skin_texts(item),
            [f"Skin Layer {item.Label}: Bar is structured, and that wins; the Skin Layer does nothing there."],
        )

    # --- Swept Body validation ---------------------------------------------------

    def swept_texts(self, item, severity=None):
        return [t for t in self.problems(severity) if t.startswith(f"Swept Body {item.Label}:")]

    def block(self, name, size, base=(0, 0, 0)):
        return self.shape_body(name, Part.makeBox(*size, App.Vector(*base)))

    def test_swept_body_on_a_face_is_refused(self):
        a = self.box("A")
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(a, "Face1")])
        self.assertIn(f"Swept Body {item.Label}: pick whole bodies, not A.Face1.", self.problems("error"))

    def test_swept_body_on_the_air_is_refused(self):
        self.box("A")
        air = objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(air, "")])
        self.assertIn(
            f"Swept Body {item.Label}: Air Region {objects.display_name(air)} cannot be a Swept Body. Remove it from"
            " the item.",
            self.problems("error"),
        )

    def test_swept_body_in_2d_is_refused(self):
        self.make_2d_study()
        bar = self.shape_body("Bar", Part.makePlane(20, 10))
        item = objects.make_swept_body(self.study, [(bar, "")])
        self.assertIn(
            f"Swept Body {item.Label}: a 2D Study is already a cross-section; Swept Body is for 3D Studies.",
            self.problems("error"),
        )

    def test_swept_body_not_a_sweep(self):
        sphere = self.shape_body("Ball", Part.makeSphere(5))
        item = objects.make_swept_body(self.study, [(sphere, "")])
        self.assertIn(f"Swept Body {item.Label}: Ball is not a sweep: {sweeps.NO_END}.", self.problems("error"))

    def test_swept_body_rebuilt_unlike_the_original_is_refused(self):
        strand = self.shape_body("Strand", helix_pipe(10, 15, 1.2, ("circle", 0.45), frenet=False))
        item = objects.make_swept_body(self.study, [(strand, "")])
        self.assertFalse(self.swept_texts(item, "error"))  # the rebuild matches the strand
        with mock.patch.object(sweeps, "rebuilt", return_value=None):
            self.assertIn(f"Swept Body {item.Label}: Strand is not a sweep: {sweeps.TWISTS}.", self.problems("error"))

    def test_swept_body_twice_is_refused(self):
        a = self.box("A")
        objects.make_air_region(self.study)
        first = objects.make_swept_body(self.study, [(a, "")])
        second = objects.make_swept_body(self.study, [(a, "")])
        self.assertIn(f"Swept Body {second.Label}: A is already in Swept Body {first.Label}.", self.problems("error"))
        self.assertFalse(self.swept_texts(first, "error"))

    def test_swept_body_with_transfinite_is_refused(self):
        a = self.box("A")
        objects.make_air_region(self.study)
        t = objects.make_transfinite_body(self.study, [a])
        item = objects.make_swept_body(self.study, [(a, "")])
        self.assertIn(
            f"Swept Body {item.Label}: A also has Transfinite Body {t.Label}; a body is swept or structured, not both.",
            self.problems("error"),
        )

    def test_swept_bodies_touching_are_refused(self):
        a, b = self.box("A"), self.box("B", x=10)
        objects.make_air_region(self.study)
        first = objects.make_swept_body(self.study, [(a, "")])
        second = objects.make_swept_body(self.study, [(b, "")])
        texts = self.problems("error")
        self.assertEqual(
            [t for t in texts if "touches" in t],
            [
                f"Swept Body {first.Label}: A touches B, which is swept; a swept body may touch only the air and"
                " unstructured bodies."
            ],
        )
        self.assertFalse(self.swept_texts(second, "error"))

    def test_swept_body_touching_a_structured_or_recombined_body_is_refused(self):
        a, b = self.box("A"), self.box("B", x=10)
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(a, "")])
        t = objects.make_transfinite_body(self.study, [b])
        text = (
            f"Swept Body {item.Label}: A touches B, which is structured; a swept body may touch only the air and"
            " unstructured bodies."
        )
        self.assertIn(text, self.problems("error"))
        self.doc.removeObject(t.Name)
        objects.make_recombine(self.study, [b])
        self.assertIn(text.replace("structured", "recombined", 1), self.problems("error"))

    def test_swept_body_solids_touching_each_other_are_refused(self):
        shape = Part.makeCompound([Part.makeBox(10, 10, 10), Part.makeBox(10, 10, 10, App.Vector(10, 0, 0))])
        both = self.shape_body("Pair", shape)
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(both, "")])
        self.assertIn(
            f"Swept Body {item.Label}: Pair touches Pair, which is swept; a swept body may touch only the air and"
            " unstructured bodies.",
            self.problems("error"),
        )

    def test_swept_body_on_a_tet_block_is_fine(self):
        self.block("Block", (30, 30, 10), (-10, -10, 0))
        bar = self.block("Bar", (10, 4, 40), (0, 0, 10))
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(bar, "")])
        self.assertFalse(self.swept_texts(item))

    def test_swept_body_partial_contact_is_refused(self):
        bar = self.block("Bar", (10, 4, 40))
        self.block("Block", (10, 4, 20), (10, 0, 0))  # touches half of the bar's face x = 10
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(bar, "")])
        self.assertEqual(
            [t for t in self.swept_texts(item, "error") if "touches only part" in t],
            [
                f"Swept Body {item.Label}: Block touches only part of Bar.Face2 of Bar; a swept body's faces must be"
                " touched whole or not at all."
            ],
        )

    def test_swept_body_alone_in_the_air_is_fine(self):
        bar = self.block("Bar", (10, 4, 40))
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(bar, "")])
        self.assertFalse(self.swept_texts(item))

    def test_swept_body_on_a_sliding_interface_is_refused(self):
        a = self.box("A", x=-5)
        objects.make_air_region(self.study, Center=App.Vector(0, 0, 5), Length=100, Width=100, Height=60)
        iface = objects.make_sliding_interface(self.study)
        self.study.Movement = "Sliding motion"
        item = objects.make_swept_body(self.study, [(a, "")])
        text = (
            f"Swept Body {item.Label}: A touches the sliding interface {iface.Label}; swept bodies must keep clear of"
            " it."
        )
        self.assertEqual([t for t in self.problems("error") if "sliding interface" in t], [text])

    def test_swept_body_wins_over_mesh_size(self):
        a = self.box("A")
        objects.make_air_region(self.study)
        objects.make_swept_body(self.study, [(a, "")])
        size = objects.make_mesh_size(self.study, 2.0, [(a, "Face1")])
        near = objects.make_refine_near(self.study, [(a, "Face1")])
        texts = self.problems("warning")
        self.assertIn(
            f"Mesh Size {size.Label}: A is swept, and that wins; the Mesh Size does nothing inside it.", texts
        )
        self.assertIn(
            f"Refine Near {near.Label}: A is swept, and that wins; the Refine Near does nothing inside it.", texts
        )

    def test_swept_body_wins_over_transfinite_edges(self):
        a = self.box("A")
        objects.make_air_region(self.study)
        objects.make_swept_body(self.study, [(a, "")])
        edges = objects.make_transfinite_edges(self.study, 4, [(a, "Edge1")])
        self.assertIn(
            f"Transfinite Edges {edges.Label}: A is swept, and that wins; the Transfinite Edges does nothing inside it.",
            self.problems("warning"),
        )

    def test_swept_start_face_on_another_body_is_refused(self):
        a, b = self.box("A"), self.box("B", x=30)
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(a, "")])
        item.StartFace = [(b, ("Face1",))]
        self.assertIn(
            f"Swept Body {item.Label}: the start face B.Face1 is not on one of its bodies.", self.problems("error")
        )

    def test_swept_stale_start_face_is_refused(self):
        a = self.box("A")
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(a, "")])
        item.StartFace = [(a, ("Face99",))]
        texts = self.problems("error")  # no IndexError from recognise_body
        self.assertIn(f"Swept Body {item.Label}: A has no Face99. Reselect the start face.", texts)
        self.assertFalse([t for t in texts if "is not a sweep" in t])

    def test_swept_ring_start_face_is_refused(self):
        ring = self.shape_body("Ring", Part.makeTorus(20, 3))
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(ring, "")])
        item.StartFace = [(ring, ("Face1",))]
        self.assertIn(
            f"Swept Body {item.Label}: Ring is a closed ring; it has no start face. Remove the start face.",
            self.problems("error"),
        )

    def test_swept_start_face_beside_a_ring_is_not_called_a_ring(self):
        # a torus and a cylinder in one body, the start face on the cylinder's side: only that solid is wrong
        shape = Part.makeCompound([Part.makeTorus(20, 3), Part.makeCylinder(3, 20, App.Vector(50, 0, 0))])
        body = self.shape_body("Ring", shape)
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(body, "")])
        item.StartFace = [(body, ("Face2",))]
        texts = self.problems("error")
        self.assertFalse([t for t in texts if "closed ring" in t])
        self.assertTrue([t for t in texts if t.startswith(f"Swept Body {item.Label}: Ring is not a sweep: solid 2:")])

    def test_swept_ring_is_valid(self):
        ring = self.shape_body("Ring", self.tube())
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(ring, "")])
        self.assertFalse(self.swept_texts(item))

    def test_swept_body_whole_mesh_size_is_fine(self):
        a = self.box("A")
        objects.make_air_region(self.study)
        objects.make_swept_body(self.study, [(a, "")])
        objects.make_mesh_size(self.study, 2.0, [(a, "")])
        self.assertFalse([t for t in self.problems("warning") if "is swept" in t])

    def test_swept_body_with_skin_quads_has_no_3d_warning(self):
        a, b = self.box("A"), self.box("B", x=30)
        objects.make_air_region(self.study)
        objects.make_swept_body(self.study, [(a, "")])
        on_swept = objects.make_skin_layer(self.study, [(a, "")])
        on_plain = objects.make_skin_layer(self.study, [(b, "")])
        on_swept.QuadLayers = on_plain.QuadLayers = True
        self.assertFalse([t for t in self.skin_texts(on_swept) if f"Skin Layer {on_swept.Label}:" in t])
        self.assertEqual(
            [t for t in self.skin_texts(on_plain) if f"Skin Layer {on_plain.Label}:" in t],
            [f"Skin Layer {on_plain.Label}: quad layers are made in 2D Studies only; ignored."],
        )

    def test_swept_body_recombine_is_fine(self):
        a = self.box("A")
        objects.make_air_region(self.study)
        item = objects.make_swept_body(self.study, [(a, "")])
        objects.make_recombine(self.study, [a])
        self.assertFalse(self.swept_texts(item))
        self.assertFalse([t for t in self.problems() if t.startswith("Recombine")])

    def ring_piece(self, name, r0, r1, z0, z1, start=0, angle=45):
        """A body: the rectangle r0..r1 × z0..z1 (radial × axial) revolved by angle about z from the angle start."""
        pts = [App.Vector(r0, 0, z0), App.Vector(r1, 0, z0), App.Vector(r1, 0, z1), App.Vector(r0, 0, z1)]
        face = Part.Face(Part.makePolygon(pts + pts[:1]))
        face.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), start)
        return self.shape_body(name, face.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle))

    def swept_beside_iron(self):
        """A swept 22.5° sector (0°..22.5°) and an iron sector of the same ring drawn at 67.5°..90°, cells of one group
        of 8 rotations by 45°: the two touch only in other frames, the iron's copies filling the sector's gaps."""
        cell = self.ring_piece("Sector", 19, 21, -2, 2, angle=22.5)
        iron = self.ring_piece("Iron", 19, 21, -2, 2, start=67.5, angle=22.5)
        rotate = {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 45, "count": 8}
        objects.make_symmetric_group(self.study, [cell, iron], rules=[rotate], name="Ring")
        objects.make_air_region(self.study, "Box", SizeMode="Padding")
        item = objects.make_swept_body(self.study, [(cell, "")])
        self.doc.recompute()
        return cell, iron, item

    def test_swept_cell_beside_a_copy_of_another_cell_is_fine(self):
        _, _, item = self.swept_beside_iron()
        self.assertFalse(self.swept_texts(item))

    def test_swept_cell_beside_a_copy_of_a_structured_cell_is_refused(self):
        _, iron, item = self.swept_beside_iron()
        objects.make_transfinite_body(self.study, [iron])
        self.doc.recompute()
        self.assertIn(
            f"Swept Body {item.Label}: Sector touches Iron, which is structured; a swept body may touch only the air"
            " and unstructured bodies.",
            self.swept_texts(item, "error"),
        )

    def test_swept_cell_touched_in_part_by_a_free_object(self):
        cell, item = self.swept_sector()
        self.block("Lid", (2, 1, 2), (-3, 19.5, 2))  # on the top of the copy rotated by 90°, over part of it
        shape = geometry.global_shape(cell)
        (n,) = [n for n, f in enumerate(shape.Faces, 1) if abs(f.CenterOfMass.z - 2) < 1e-6]
        self.assertIn(
            f"Swept Body {item.Label}: Lid touches only part of Sector.Face{n} of Sector; a swept body's faces must be"
            " touched whole or not at all.",
            self.swept_texts(item, "error"),
        )

    def swept_sector(self):
        """The cell of a group of 8 rotations by 45°: a 2 × 4 sector at rc 20, in a Padding Box air, swept."""
        cell = self.ring_piece("Sector", 19, 21, -2, 2)
        rotate = {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 45, "count": 8}
        objects.make_symmetric_group(self.study, [cell], rules=[rotate], name="Ring")
        objects.make_air_region(self.study, "Box", SizeMode="Padding")
        item = objects.make_swept_body(self.study, [(cell, "")])
        self.doc.recompute()
        return cell, item

    def test_swept_cell_validates(self):
        _, item = self.swept_sector()
        self.assertFalse(self.swept_texts(item))

    def test_swept_cell_job_has_free_faces(self):
        """The sector's faces toward the free side are its inner, outer, top and bottom faces, not its two cuts."""
        self.swept_sector()
        (air,) = objects.air_regions(self.study)
        for side in objects.SIDES:  # 6 mm of air all round: the top and bottom are no cuts of the domain
            setattr(air, f"Pad{side}", 6)
        (ring,) = objects.symmetric_groups(self.study)
        objects.set_row_material(self.study, ring, 0, self.steel())
        objects.sync_parts(self.study)
        self.doc.recompute()
        (group,) = self.read_job()["symmetric"]["groups"]
        (entry,) = group["job"]["swept"]
        self.assertEqual(entry["free_faces"], [f"geometry/g1_swept_free_1_{n}.brep" for n in range(1, 5)])
        folder = jobwriter.scratch_folder(self.study)
        kinds = []
        for rel in entry["free_faces"]:
            (face,) = Part.read(os.path.join(folder, rel)).Faces
            if isinstance(face.Surface, Part.Plane):
                kinds.append(f"z {round(face.CenterOfMass.z)}")
            else:
                kinds.append(f"r {round(face.Surface.Radius)}")
        self.assertEqual(sorted(kinds), ["r 19", "r 21", "z -2", "z 2"])

    def test_swept_rebuilt_strand_cell_meshes(self):
        """A Standard-mode strand (rebuilt: its seam twists) as the cell of 6 rotations by 60°: its faces toward the
        free side come from the rebuild, and its copies mesh with the skin on them, conformal in the air."""
        strand = self.shape_body("Strand", helix_pipe(10, 15, 1.2, ("circle", 0.45), frenet=False))
        rotate = {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 60, "count": 6}
        ring = objects.make_symmetric_group(self.study, [strand], rules=[rotate], name="Litz")
        air = objects.make_air_region(self.study, "Box", SizeMode="Padding")
        for side in objects.SIDES:  # 3 mm of air all round: the strand's ends are no cuts of the domain
            setattr(air, f"Pad{side}", 3)
        self.study.MeshSizesGroup.DefaultMeshSize = 0.6
        item = objects.make_swept_body(self.study, [(strand, "")])
        item.PathSize, item.SectionSize = 0.4, 0.2
        layer = objects.make_skin_layer(self.study, [(strand, "")], 0.2)
        layer.LayerDepth = 2.0
        objects.set_row_material(self.study, ring, 0, self.steel())
        objects.sync_parts(self.study)
        self.doc.recompute()
        path = jobwriter.write_job(self.study)
        with open(path, encoding="utf-8") as fh:
            (group,) = json.load(fh)["symmetric"]["groups"]
        folder = jobwriter.scratch_folder(self.study)
        (solid,) = Part.read(os.path.join(folder, group["job"]["volumes"][0]["file"])).Solids
        (entry,) = group["job"]["swept"]
        self.assertEqual(len(entry["free_faces"]), 3)  # its side and both ends
        for rel in entry["free_faces"]:
            (face,) = Part.read(os.path.join(folder, rel)).Faces
            twin = min(solid.Faces, key=lambda f: f.CenterOfMass.distanceToPoint(face.CenterOfMass))
            self.assertLess(twin.CenterOfMass.distanceToPoint(face.CenterOfMass), 1e-6)
            self.assertAlmostEqual(twin.Area, face.Area, delta=1e-6 * face.Area)
            for v in face.Vertexes:  # the rebuild's seam vertices, not the original's
                self.assertLess(min(v.Point.distanceToPoint(w.Point) for w in solid.Vertexes), 1e-6)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        gmsh.initialize()
        self.addCleanup(gmsh.finalize)
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(jobwriter.mesh_file(self.study))
        part = group["parts"][0]["mat_id"]
        kinds = set()
        for e in gmsh.model.getEntitiesForPhysicalGroup(3, part):
            kinds |= {gmsh.model.mesh.getElementProperties(t)[0] for t in gmsh.model.mesh.getElements(3, e)[0]}
        self.assertEqual(kinds, {"Hexahedron 8", "Prism 6"})  # the hexahedra: the skin on the free faces
        xyz = gmsh.model.mesh.getNodes()[1].reshape(-1, 3)
        lo, hi = xyz.min(axis=0), xyz.max(axis=0)
        self.assertEqual(inner_free_faces([*lo, *(hi - lo)]), [])

    def test_swept_entry_unchanged_outside_groups(self):
        self.swept_job()
        (entry,) = self.read_job()["swept"]
        self.assertNotIn("free_faces", entry)

    def test_skin_kept_for_unswept_body(self):
        """A body of a Swept Body item that is no sweep gets no swept entry, so it keeps its Skin Layer entry."""
        ball = self.shape_body("Ball", Part.makeSphere(5))
        bar = self.shape_body("Bar", Part.makeBox(10, 4, 40))
        objects.make_swept_body(self.study, [(ball, ""), (bar, "")])
        objects.make_skin_layer(self.study, [(ball, ""), (bar, "")], 1)
        (skin,) = jobwriter.skin_entries(self.study, {"Ball": [1], "Bar": [2]})
        self.assertEqual(skin["mat_ids"], [1])

    def test_swept_free_object_refused(self):
        cell, item = self.swept_sector()
        bar = self.block("Bar", (4, 4, 4), (40, 0, -2))
        item.References = [(cell, ""), (bar, "")]
        self.doc.recompute()
        self.assertEqual(
            self.swept_texts(item),
            [
                f"Swept Body {item.Label}: Bar is a free object; in a Study with Symmetric Groups only cell objects"
                " are swept."
            ],
        )

    def test_swept_cell_touching_part_of_a_copy(self):
        cell, item = self.swept_sector()
        # drawn at 45°..90°, so only its copy rotated by -45° touches the sector, over the half z < 0 of r = 21
        tooth = self.ring_piece("Tooth", 21, 25, -2, 0, start=45)
        rotate = {"kind": "rotate", "point": [0, 0, 0], "axis": [0, 0, 1], "step": 45, "count": 8}
        objects.make_symmetric_group(self.study, [tooth], rules=[rotate], name="Teeth")
        self.doc.recompute()
        shape = geometry.global_shape(cell)
        (n,) = [n for n, f in enumerate(shape.Faces, 1) if abs(getattr(f.Surface, "Radius", 0) - 21) < 1e-6]
        self.assertIn(
            f"Swept Body {item.Label}: Tooth touches only part of Sector.Face{n} of Sector; a swept body's faces must"
            " be touched whole or not at all.",
            self.swept_texts(item, "error"),
        )

    def test_skin_layer_quads_on_a_recombined_body_warns(self):
        """A recombined body gets the graded layer as quads, so only quad layers are lost; the depth is checked too."""
        self.make_2d_study()
        wire = self.disk("Wire", 2)
        objects.make_recombine(self.study, [wire])
        item = objects.make_skin_layer(self.study, [(wire, "")])
        item.LayerDepth = 1.0
        self.assertFalse(self.skin_texts(item))
        item.QuadLayers = True
        self.assertEqual(
            self.skin_texts(item),
            [f"Skin Layer {item.Label}: Wire is recombined; it gets the graded layer but no quad layers."],
        )
        item.LayerDepth = 3.0
        self.assertIn(
            f"Skin Layer {item.Label}: the layer (3 mm) is deeper than half of Wire (about 4 mm thick); the whole body"
            " is skin, so a Mesh Size of 0.5 mm on it does the same.",
            self.skin_texts(item),
        )

    def test_skin_layer_on_a_body_of_another_skin_layer_warns(self):
        self.make_2d_study()
        wire = self.disk("Wire", 5)
        first = objects.make_skin_layer(self.study, [(wire, "")])
        second = objects.make_skin_layer(self.study, [(wire, "")])
        self.assertFalse([t for t in self.problems() if t.startswith(f"Skin Layer {first.Label}:")])
        self.assertEqual(
            self.skin_texts(second),
            [
                f"Skin Layer {second.Label}: Wire already has Skin Layer {first.Label}; the smallest size wins, and"
                " only the first makes quad layers."
            ],
        )

    def test_refine_near_on_a_deleted_body_refers_to_nothing(self):
        self.box("A")
        b = self.box("B", 20)
        item = objects.make_refine_near(self.study, [(b, "Edge1")])
        self.doc.removeObject("B")
        self.doc.recompute()
        self.assertIn(
            f"Refine Near {item.Label} refers to nothing (were its bodies deleted?). Pick again or delete it.",
            self.problems(),
        )

    def test_refine_near_limit_to_an_unmeshed_body_warns(self):
        a, b, c = self.box("A"), self.box("B", 20), self.box("C", 40)
        self.assign([a])
        self.exclude(b)
        self.exclude(c)
        item = objects.make_refine_near(self.study, [(a, "Edge1")], limit_to=[b, c])
        warnings = self.problems(validation.WARNING)
        skipped = f"Refine Near {item.Label}: no body in Limit to is meshed by the Study; the refinement is skipped."
        self.assertEqual([w for w in warnings if w.startswith(f"Refine Near {item.Label}")], [skipped])
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("refine", json.load(fh), "a Limit to with no meshed body would refine everywhere")
        item.LimitTo = [a, b]
        self.assertIn(
            f"Refine Near {item.Label}: B in Limit to is not meshed by the Study; it has no effect there.",
            self.problems(validation.WARNING),
        )

    def test_job_without_refine_near_has_no_refine_key(self):
        a = self.box("A")
        self.assign([a])
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("refine", json.load(fh))

    def test_refine_near_goes_to_the_job(self):
        a, b = self.box("A"), self.box("B", 10)
        self.assign([a, b])
        objects.make_refine_near(self.study, [(a, "Edge1"), (a, "Vertex1"), (b, "")], 0.4, 4, 10, 0.5, limit_to=[a])
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        ids = self.study.MatIds
        (entry,) = job["refine"]
        self.assertEqual(entry["name"], "RefineNear")
        self.assertEqual(len(entry["files"]), 2)
        self.assertTrue(all(os.path.exists(self.scratch(f)) for f in entry["files"]))
        self.assertEqual(entry["whole"], [int(ids[b.Name])])
        self.assertEqual(entry["limit_to"], [int(ids[a.Name])])
        self.assertEqual(
            (entry["fine"], entry["fine_distance"], entry["coarse"], entry["growth"]), (0.4, 0.5, 4.0, 10.0)
        )

    def test_job_without_air_grading_has_no_air_grading_key(self):
        a = self.box("A")
        self.assign([a])
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("air_grading", json.load(fh))

    def test_air_grading_goes_to_the_job(self):
        a = self.box("A")
        self.assign([a])
        air = objects.make_air_region(self.study, "Box", Center=App.Vector(5, 5, 5), Length=30, Width=30, Height=30)
        self.doc.recompute()
        objects.make_mesh_size(self.study, 12.0, [(air, "")])
        objects.make_air_grading(self.study, growth=50.0)
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual(
            job["air_grading"],
            [{"name": "AirGrading", "mat_ids": [int(self.study.MatIds[air.Name])], "growth": 50.0, "far": 12.0}],
        )

    def test_refine_near_leaves_out_limit_bodies_the_study_does_not_mesh(self):
        a, b = self.box("A"), self.box("B", 20)
        self.assign([a])
        self.exclude(b)
        objects.make_refine_near(self.study, [(a, "Edge1")], limit_to=[a, b])
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            (entry,) = json.load(fh)["refine"]
        self.assertEqual(entry["limit_to"], [int(self.study.MatIds[a.Name])])

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

    def test_items_on_bodies_the_study_does_not_mesh_are_a_warning(self):
        a, outside = self.box("A"), self.box("Outside", 20)
        self.exclude(outside)
        objects.make_recombine(self.study, [a, outside])
        self.assertEqual(self.problems(validation.ERROR), [])
        self.assertIn(
            "Recombine Recombine is not used for Outside, which is excluded from the Study.", self.problems("warning")
        )
        jobwriter.check(self.study)

    # --- Why a body is not meshed ---------------------------------------------

    def warnings_with(self, text):
        return [t for t in self.problems("warning") if text in t]

    def mat(self):
        return objects.display_name(objects.materials(self.study)[0])

    def cut_tool_case(self):
        coil = self.box("Coil", 10)
        _, air = self.air_cut_by(coil)
        return coil, air

    def made_from_case(self):
        box = self.box("Box", 0, 30)
        tool = self.box("Tool", 10)
        cut = self.doc.addObject("Part::Cut", "Cut")
        cut.Base, cut.Tool = box, tool
        self.doc.recompute()
        self.exclude(tool)
        return box, cut

    def air_shape_case(self):
        a = self.box("A")
        shape = self.box("Shape", 20, 30)
        air = objects.make_air_region(self.study, "Custom", Source=shape)
        return a, shape, air

    def drawing_case(self):
        cell = self.box("Cell")
        drawing = self.doc.addObject("Part::Mirroring", "Drawing")
        drawing.Source, drawing.Normal = cell, App.Vector(1, 0, 0)
        self.doc.recompute()
        group = objects.make_symmetric_group(self.study, [cell], name="Rotor")
        self.doc.recompute()
        return drawing, group

    def test_the_gate_says_a_body_is_excluded(self):
        a = self.box("A")
        self.exclude(a)
        self.assertEqual(
            objects.assignment_problem(self.study, [a]), "A is excluded from the Study: tick it in the Study panel."
        )
        self.assertEqual(geometry.not_meshed(self.study, a), ("excluded", None))

    def test_the_gate_says_a_body_is_a_cut_tool(self):
        coil, air = self.cut_tool_case()
        self.assertEqual(
            objects.assignment_problem(self.study, [coil]),
            "Coil is the tool of Air and is not meshed. To mesh it, make a Link to it.",
        )
        self.assertEqual(geometry.not_meshed(self.study, coil), ("cut tool", air))

    def test_the_gate_says_a_body_is_made_into_another(self):
        box, cut = self.made_from_case()
        self.assertEqual(
            objects.assignment_problem(self.study, [box]), "Box is not meshed on its own: Cut is made from it."
        )
        self.assertEqual(geometry.not_meshed(self.study, box), ("made from", cut))

    def test_the_gate_says_a_body_is_a_custom_air_shape(self):
        _, shape, air = self.air_shape_case()
        self.assertEqual(
            objects.assignment_problem(self.study, [shape]), f"Shape is the Custom shape of Air Region {air.Label}."
        )
        self.assertEqual(geometry.not_meshed(self.study, shape), ("air shape", air))

    def test_the_gate_says_a_body_is_the_drawing_of_a_group(self):
        drawing, group = self.drawing_case()
        self.assertEqual(
            objects.assignment_problem(self.study, [drawing]),
            f"Drawing is the drawing of Symmetric Group {group.Label}: pick its copies on the group.",
        )
        self.assertEqual(geometry.not_meshed(self.study, drawing), ("drawing", group))

    def test_the_gate_joins_the_texts_and_lets_meshed_bodies_through(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        self.exclude(b, c)
        why = "is excluded from the Study: tick it in the Study panel."
        self.assertEqual(objects.assignment_problem(self.study, [a, b, c, b]), f"B {why} C {why}")
        self.assertIsNone(geometry.not_meshed(self.study, a))

    def test_a_material_on_an_excluded_body_is_warned_about(self):
        a = self.box("A")
        self.exclude(a)
        self.assign([a])
        self.assertIn(f"Material {self.mat()} is on A, which is excluded from the Study.", self.problems("warning"))

    def test_a_material_on_a_cut_tool_is_warned_about(self):
        coil, _ = self.cut_tool_case()
        self.assign([coil])
        self.assertIn(
            f"Material {self.mat()} is on Coil, the tool of Air, which is not meshed. To mesh it, make a Link to it.",
            self.problems("warning"),
        )

    def test_a_cut_tool_without_assignments_is_silent(self):
        self.cut_tool_case()
        self.assertFalse([p for p in validation.validate(self.study) if "Coil" in p.text])

    def test_a_material_on_a_consumed_body_is_warned_about(self):
        box, _ = self.made_from_case()
        self.assign([box])
        self.assertIn(
            f"Material {self.mat()} is on Box, which Cut is now made from: assign it to Cut.", self.problems("warning")
        )

    def test_a_material_on_a_custom_air_shape_is_not_warned_about(self):
        _, shape, _ = self.air_shape_case()
        self.assign([shape])
        self.assertFalse(self.warnings_with(f"Material {self.mat()} is on Shape"))

    def test_a_material_on_a_group_drawing_is_warned_about(self):
        drawing, group = self.drawing_case()
        self.assign([drawing])
        self.assertIn(
            f"Material {self.mat()} is on Drawing, the drawing of Symmetric Group {group.Label}:"
            " the group's parts take the Materials.",
            self.problems("warning"),
        )

    def test_an_item_on_an_excluded_body_is_warned_about(self):
        a, b = self.box("A"), self.box("B", 10)
        self.exclude(b)
        objects.make_recombine(self.study, [a, b])
        self.assertIn(
            "Recombine Recombine is not used for B, which is excluded from the Study.", self.problems("warning")
        )

    def test_an_item_on_a_cut_tool_is_warned_about(self):
        coil, _ = self.cut_tool_case()
        objects.make_recombine(self.study, [coil])
        self.assertIn(
            "Recombine Recombine is not used for Coil, the tool of Air, which is not meshed."
            " To mesh it, make a Link to it.",
            self.problems("warning"),
        )

    def test_an_item_on_a_consumed_body_is_warned_about(self):
        box, _ = self.made_from_case()
        objects.make_recombine(self.study, [box])
        self.assertIn(
            "Recombine Recombine is not used for Box, which Cut is now made from: put it on Cut.",
            self.problems("warning"),
        )

    def test_an_item_on_a_custom_air_shape_is_warned_about(self):
        _, shape, air = self.air_shape_case()
        objects.make_recombine(self.study, [shape])
        self.assertIn(
            f"Recombine Recombine is not used for Shape, the Custom shape of Air Region {air.Label}:"
            " put it on the Air Region.",
            self.problems("warning"),
        )

    def test_an_item_on_a_group_drawing_is_warned_about(self):
        drawing, group = self.drawing_case()
        objects.make_recombine(self.study, [drawing])
        self.assertIn(
            f"Recombine Recombine is not used for Drawing, the drawing of Symmetric Group {group.Label}:"
            " put it on the cell objects.",
            self.problems("warning"),
        )

    def test_a_link_that_is_not_one_body_is_warned_about_once(self):
        a = self.box("A")
        array = self.doc.addObject("App::Link", "Array")
        array.LinkedObject = a
        array.ElementCount = 2
        self.doc.recompute()
        text = "Array is not meshed: a Link is meshed only when it links one body."
        self.assertEqual(self.problems("warning").count(text), 1)
        (problem,) = [p for p in validation.validate(self.study) if p.text == text]
        self.assertEqual((problem.item, problem.refs), (array, [(array, "")]))

    def test_a_link_that_is_a_cut_tool_is_not_warned_about(self):
        array = self.link_array()
        cut = self.doc.addObject("Part::Cut", "Cut")
        cut.Base, cut.Tool = self.box("Base", 0, 30), array
        self.doc.recompute()
        self.assertIn(cut, objects.study_bodies(self.study))
        self.assertFalse(self.warnings_with("Array is not meshed: a Link"))

    def test_a_link_to_one_body_is_not_warned_about(self):
        self.coil_link()
        self.assertFalse(self.warnings_with("is not meshed: a Link"))

    def link_array(self):
        a = self.box("A")
        array = self.doc.addObject("App::Link", "Array")
        array.LinkedObject = a
        array.ElementCount = 2
        self.doc.recompute()
        return array

    def test_a_material_on_a_non_body_is_warned_about(self):
        array = self.link_array()
        self.assign([array])
        self.assertIn(f"Material {self.mat()} is on Array, which is not a body of the Study.", self.problems("warning"))

    def test_an_item_on_a_non_body_is_warned_about(self):
        array = self.link_array()
        objects.make_recombine(self.study, [array])
        self.assertIn(
            "Recombine Recombine is not used for Array, which is not a body of the Study.", self.problems("warning")
        )

    def test_an_excluded_cut_tool_gets_the_cut_tool_text(self):
        coil, air = self.cut_tool_case()  # the tree hides a cut tool: ticking it in the Study panel cannot help
        self.exclude(coil)
        self.assertEqual(geometry.not_meshed(self.study, coil), ("cut tool", air))
        self.assertEqual(
            objects.assignment_problem(self.study, [coil]),
            "Coil is the tool of Air and is not meshed. To mesh it, make a Link to it.",
        )

    def test_a_link_a_meshed_body_is_made_from_gets_no_link_warning(self):
        array = self.link_array()
        cut = self.doc.addObject("Part::Cut", "Cut")
        cut.Base, cut.Tool = array, self.box("Tool", 50)
        self.doc.recompute()
        self.assertIsNone(geometry.link_target(array))
        self.assertIn(cut, objects.study_bodies(self.study))
        self.assertIn(array.Name, geometry.inputs(cut))
        self.assertFalse(self.warnings_with("Array is not meshed: a Link"))

    def test_validation_lists_every_error(self):
        a = self.box("A")
        self.study.MeshSizesGroup.DefaultMeshSize = 0
        objects.make_mesh_size(self.study, 0.0, [(a, "Face1")])
        objects.make_excitation(self.study, "Gone", [])
        errors = self.problems(validation.ERROR)
        self.assertEqual(len(errors), 3, errors)

    def test_overlapping_bodies_are_an_error(self):
        for name, x in (("A", 0), ("B", 5), ("C", 10)):  # A and B overlap; A and C only touch
            self.box(name, x)
        errors = [e for e in self.problems(validation.ERROR) if "overlap" in e]
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(errors[0].startswith("Bodies A and B overlap by 500 mm³ near (7.5, 5, 5)."), errors[0])
        self.assertTrue(errors[1].startswith("Bodies B and C overlap"), errors[1])
        self.assertStudyError("Bodies A and B overlap")

    def test_overlapping_faces_are_an_error_in_2d(self):
        _, b, c = self.face("A"), self.face("B"), self.face("C")
        b.Placement.Base, c.Placement.Base = App.Vector(5, 5, 0), App.Vector(-10, 0, 0)  # C touches A
        study = self.replace_study()
        errors = [p.text for p in validation.validate(study) if "overlap" in p.text]
        self.assertEqual(len(errors), 1, errors)
        self.assertTrue(errors[0].startswith("Bodies A and B overlap by 25 mm² near (7.5, 7.5, 0)."), errors[0])

    def test_mesh_size_larger_than_a_thin_body_is_a_warning(self):
        wire = self.doc.addObject("Part::Cylinder", "Wire")
        wire.Radius, wire.Height = 0.45, 20
        self.doc.recompute()
        plate = self.box("Plate", 30)  # flat faces mesh at any size
        plate.Height = 0.5
        self.doc.recompute()
        (warning,) = [w for w in self.problems(validation.WARNING) if "thick" in w]
        self.assertTrue(warning.startswith("Mesh size 5 mm is larger than Wire is thick (about 0.88 mm)"), warning)
        objects.make_mesh_size(self.study, 0.5, [(wire, "")])
        self.assertEqual([w for w in self.problems(validation.WARNING) if "thick" in w], [])

    def test_body_a_sketch_only_references_is_meshed_with_the_face_aligned_to_it(self):
        coil = self.doc.addObject("Part::Feature", "Coil")
        coil.Shape = Part.makePlane(10, 10)
        aligned = self.sketched_face_aligned_to(coil)
        study = self.replace_study()
        self.assertEqual(objects.study_bodies(study), [coil, aligned])
        self.assertEqual(validation.errors(validation.validate(study)), [])

    def test_bodies_without_material_are_a_warning(self):
        self.box("A")
        self.assertEqual(
            self.problems(validation.WARNING), ["No material (the input file needs one for every body): A"]
        )

    def test_ids_come_back_after_undo_but_not_to_a_new_object_with_the_same_name(self):
        self.doc.UndoMode = 1
        a, _ = self.box("A"), self.box("B", 10)
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
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "2", "A": "3"})

    def test_id_comes_back_when_a_body_returns_to_the_study(self):
        a, _ = self.box("A"), self.box("B", 10)
        objects.update_ids(self.study)
        self.exclude(a)
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "2"})
        self.box("C", 20)
        objects.set_excluded(self.study, [])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "2", "C": "3", "A": "1"})

    def test_mesher_check_only_writes_nothing(self):
        self.sliced_coil()
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
