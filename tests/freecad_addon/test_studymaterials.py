"""Study Material Library tests.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_studymaterials.py"""

import dataclasses
import json
import os
import tempfile
import unittest
from unittest import mock

import FreeCAD as App

from ems_material import (
    MaterialAlreadyExistsError,
    MaterialConflictError,
    MaterialManager,
    MaterialNotFoundError,
    ReadOnlyMaterialError,
    material_from_dict,
)
from emsolution import objects, studymaterials
from emsolution.jobwriter import StudyError

from .materialdata import AIR, COPPER, STEEL, STEEL_XYZ, record


def material(material_id, name, properties, family="generic"):
    return material_from_dict(record(material_id, name, family, properties))


class StudyCase(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("M")
        self.doc.UndoMode = 1
        self.tmp = tempfile.TemporaryDirectory()
        self.study = objects.make_study(self.doc)
        self.study.MainMode = "Manual"
        self.changes = []
        self.repo = studymaterials.StudyMaterialRepository(self.study, on_change=lambda: self.changes.append(1))

    def tearDown(self):
        App.closeDocument(self.doc.Name)
        self.tmp.cleanup()

    def box(self, name, x=0.0):
        b = self.doc.addObject("Part::Box", name)
        b.Placement.Base = App.Vector(x, 0, 0)
        self.doc.recompute()
        return b


class RepositoryTest(StudyCase):
    def test_create_get_list_and_search(self):
        steel = material("user:steel", "Steel", STEEL, "electrical_steel")
        self.repo.create(steel)
        self.repo.create(material("user:air", "Air", AIR))
        self.assertEqual(self.repo.get("user:steel"), steel)
        self.assertEqual([m.material_id for m in self.repo.list()], ["user:steel", "user:air"])
        self.assertEqual([m.material_id for m in self.repo.search(text="ste")], ["user:steel"])
        self.assertEqual([m.material_id for m in self.repo.search(family="generic")], ["user:air"])
        self.assertEqual(self.repo.list_sources(), ("Study",))
        self.assertEqual(self.repo.source_for("user:air"), "Study")
        self.assertTrue(self.repo.is_writable("user:air"))
        self.assertEqual(len(self.changes), 2)
        with self.assertRaises(MaterialNotFoundError):
            self.repo.get("user:nothing")

    def test_create_refuses_a_duplicate_id(self):
        self.repo.create(material("user:air", "Air", AIR))
        with self.assertRaises(MaterialAlreadyExistsError):
            self.repo.create(material("user:air", "Other air", AIR))
        self.assertEqual(len(objects.library_materials(self.study)), 1)

    def test_update_checks_the_expected_version_and_renames(self):
        air = self.repo.create(material("user:air", "Air", AIR))
        newer = dataclasses.replace(
            air, material_version="1.0.1", identity=dataclasses.replace(air.identity, name="Air gap")
        )
        self.repo.update(newer, expected_version="1.0.0")
        (lib,) = objects.library_materials(self.study)
        self.assertEqual((lib.Label, self.repo.get("user:air").material_version), ("Air gap", "1.0.1"))
        with self.assertRaises(MaterialConflictError):
            self.repo.update(newer, expected_version="1.0.0")

    def test_duplicate_makes_a_user_copy(self):
        self.repo.create(material("user:steel", "Steel", STEEL, "electrical_steel"))
        copy = self.repo.duplicate(
            "user:steel", new_material_id="user:steel_b", new_name="Steel B", author="me", updated_at="2026-10-13"
        )
        self.assertEqual((copy.name, copy.material_version, copy.parent_ref), ("Steel B", "1.0.0", "user:steel@1.0.0"))
        self.assertEqual(copy.properties, self.repo.get("user:steel").properties)

    def test_delete_is_refused_while_an_assignment_uses_the_material(self):
        self.repo.create(material("user:air", "Air", AIR))
        (lib,) = objects.library_materials(self.study)
        a = self.box("A")
        objects.assign(self.study, [a], lib, 0)
        self.assertFalse(self.repo.is_deletable("user:air"))
        with self.assertRaisesRegex(ReadOnlyMaterialError, "used by: A$"):
            self.repo.delete("user:air")
        objects.unassign(self.study, [a])
        self.repo.delete("user:air")
        self.assertEqual(objects.library_materials(self.study), [])

    def test_each_write_is_one_undo_step(self):
        air = self.repo.create(material("user:air", "Air", AIR))
        self.repo.update(dataclasses.replace(air, material_version="1.0.1"))
        self.doc.undo()
        self.assertEqual(self.repo.get("user:air").material_version, "1.0.0")
        self.doc.undo()
        self.assertEqual(objects.library_materials(self.study), [])

    def test_json_export_and_import(self):
        self.repo.create(material("user:air", "Air", AIR))
        path = os.path.join(self.tmp.name, "air.material.json")
        self.repo.export_json("user:air", path)
        self.repo.delete("user:air")
        self.assertEqual(self.repo.import_json(path).material_id, "user:air")

    def test_material_manager_accepts_the_repository(self):
        manager = MaterialManager(repository=self.repo)
        steel = manager.repository.create(material("user:steel", "Steel", STEEL, "electrical_steel"))
        self.assertEqual(manager.update(steel).material_id, "user:steel")
        self.assertEqual([m.name for m in manager.list()], ["Steel"])


class ImportTest(StudyCase):
    def test_import_copies_records_unchanged(self):
        steel = material("ieej:50a350", "50A350", STEEL, "electrical_steel")
        (lib,) = studymaterials.import_materials(self.study, [steel])
        self.assertEqual(studymaterials.record_material(lib), steel)
        self.assertEqual(lib.Label, "50A350")
        self.assertEqual(self.doc.UndoNames[:1], ["Import materials"])

    def test_import_refuses_ids_already_in_the_study(self):
        studymaterials.import_materials(self.study, [material("user:air", "Air", AIR)])
        with self.assertRaisesRegex(MaterialAlreadyExistsError, "user:air"):
            studymaterials.import_materials(
                self.study, [material("user:copper", "Copper", COPPER), material("user:air", "Air", AIR)]
            )
        self.assertEqual([o.MaterialId for o in objects.library_materials(self.study)], ["user:air"])


class LibraryRootTest(unittest.TestCase):
    def test_environment_then_remembered_root(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as other:
            settings = os.path.join(other, "settings.json")
            env = {"EMS_MATERIAL_MANAGER_ROOT": root, "EMS_MATERIAL_MANAGER_SETTINGS_PATH": settings}
            with mock.patch.dict(os.environ, env):
                self.assertTrue(os.path.samefile(studymaterials.library_root(), root))
            env["EMS_MATERIAL_MANAGER_ROOT"] = ""
            with mock.patch.dict(os.environ, env):
                self.assertIsNone(studymaterials.library_root())
                with open(settings, "w", encoding="utf-8") as fh:
                    json.dump(
                        {
                            "schema": "ems_material_product_exchange_settings",
                            "schema_version": "1.0",
                            "library_root": other,
                        },
                        fh,
                    )
                self.assertTrue(os.path.samefile(studymaterials.library_root(), other))

    def test_manager_root_needs_manager_config(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertFalse(studymaterials.is_manager_root(root))
            self.assertFalse(studymaterials.is_manager_root(os.path.join(root, "missing")))
            self.assertFalse(studymaterials.is_manager_root(""))
            with open(os.path.join(root, "manager.config.json"), "w", encoding="utf-8") as fh:
                fh.write("{}")
            self.assertTrue(studymaterials.is_manager_root(root))


STEEL_ENTRY = {
    "ElectricProperty": {"conductivity": {"SIGMA": 2e6}},
    "MagneticProperty": {
        "MU": 1.0,
        "BH_CURVE_ID": 1,
        "IRON_LOSS": {"COORD_ID": 0, "MASS_DENSITY": 7650.0, "KE": 5e-5, "KH": 0.02},
    },
}
STEEL_CURVE = {"H": [0.0, 100.0, 1000.0], "B": [0.0, 1.0, 1.5]}


class BuilderTest(unittest.TestCase):
    def test_three_bodies_share_one_material_and_one_curve(self):
        steel = material("user:steel", "Steel", STEEL, "electrical_steel")
        rows = [(1, "Stator", 0, steel), (2, "Rotor", 1, steel), (3, "Shaft", 0, steel)]
        out = studymaterials.material_properties(rows)
        entries = out["16_Material_Properties"]["16_1_3D_Element_Properties"]
        self.assertEqual(
            entries,
            [
                {"MAT_ID": 1, "MAT_NAME": "Stator", "POTENTIAL": 0, **STEEL_ENTRY},
                {"MAT_ID": 2, "MAT_NAME": "Rotor", "POTENTIAL": 1, **STEEL_ENTRY},
                {"MAT_ID": 3, "MAT_NAME": "Shaft", "POTENTIAL": 0, **STEEL_ENTRY},
            ],
        )
        self.assertEqual(out["20_BH_Curve"], [{"BH_CURVE_ID": 1, "BH_CURVE_NAME": "Steel", "data": STEEL_CURVE}])
        entries[0]["MagneticProperty"]["MU"] = 5.0
        self.assertEqual(entries[1]["MagneticProperty"]["MU"], 1.0, "entries share a dict")

    def test_curve_ids_are_sequential_across_materials(self):
        a = material("user:a", "Steel A", STEEL, "electrical_steel")
        b = material("user:b", "Steel B", STEEL, "electrical_steel")
        out = studymaterials.material_properties([(1, "X", 0, a), (2, "Y", 0, b), (3, "Z", 0, a)])
        entries = out["16_Material_Properties"]["16_1_3D_Element_Properties"]
        self.assertEqual([e["MagneticProperty"]["BH_CURVE_ID"] for e in entries], [1, 2, 1])
        self.assertEqual(
            [(c["BH_CURVE_ID"], c["BH_CURVE_NAME"]) for c in out["20_BH_Curve"]], [(1, "Steel A"), (2, "Steel B")]
        )

    def test_anisotropic_curves_are_renumbered_after_an_earlier_material(self):
        steel = material("user:steel", "Steel", STEEL, "electrical_steel")
        xyz = material("user:xyz", "Aniso", STEEL_XYZ, "electrical_steel")
        out = studymaterials.material_properties([(1, "A", 0, steel), (2, "B", 0, xyz)])
        entries = out["16_Material_Properties"]["16_1_3D_Element_Properties"]
        self.assertEqual(entries[1]["MagneticProperty"]["BH_CURVE_XYZ"]["BH_XYZ_ID"], [2, 3, 4])
        self.assertEqual([c["BH_CURVE_ID"] for c in out["20_BH_Curve"]], [1, 2, 3, 4])
        self.assertEqual([c["BH_CURVE_NAME"] for c in out["20_BH_Curve"]], ["Steel", "Aniso_x", "Aniso_y", "Aniso_z"])

    def test_material_without_magnetic_data_is_linear(self):
        out = studymaterials.material_properties(
            [(4, "Coil", 0, material("user:copper", "Copper", COPPER)), (5, "Gap", 0, material("user:air", "Air", AIR))]
        )
        self.assertEqual(
            out["16_Material_Properties"]["16_1_3D_Element_Properties"],
            [
                {
                    "MAT_ID": 4,
                    "MAT_NAME": "Coil",
                    "POTENTIAL": 0,
                    "ElectricProperty": {"conductivity": {"SIGMA": 5.8e7}},
                    "MagneticProperty": {"MU": 1.0},
                },
                {"MAT_ID": 5, "MAT_NAME": "Gap", "POTENTIAL": 0, "MagneticProperty": {"MU": 1.0}},
            ],
        )
        self.assertEqual(out["20_BH_Curve"], [])

    def test_adapter_errors_name_the_material(self):
        props = json.loads(json.dumps(STEEL))
        del props["general"]
        with self.assertRaisesRegex(StudyError, "Bad steel.*density"):
            studymaterials.material_properties([(1, "A", 0, material("user:bad", "Bad steel", props))])


class StudyRowsTest(StudyCase):
    def test_rows_follow_mat_ids_with_body_names_and_potential(self):
        a, b = self.box("A"), self.box("B", 10)
        self.study.MainObjects = [a, b]
        (lib,) = studymaterials.import_materials(self.study, [material("user:steel", "Steel", STEEL)])
        objects.assign(self.study, [a, b], lib, 1)
        rows = studymaterials.study_material_rows(self.study)
        self.assertEqual(
            [(r[0], r[1], r[2], r[3].material_id) for r in rows], [(1, "A", 1, "user:steel"), (2, "B", 1, "user:steel")]
        )

    def test_body_without_an_assignment_is_named(self):
        a, b = self.box("A"), self.box("B", 10)
        self.study.MainObjects = [a, b]
        (lib,) = studymaterials.import_materials(self.study, [material("user:air", "Air", AIR)])
        objects.assign(self.study, [a], lib, 0)
        with self.assertRaisesRegex(StudyError, "no material from the Material Library: B$"):
            studymaterials.study_material_rows(self.study)

    def test_assignment_without_a_material_is_named(self):
        a = self.box("A")
        self.study.MainObjects = [a]
        (lib,) = studymaterials.import_materials(self.study, [material("user:air", "Air", AIR)])
        objects.assign(self.study, [a], lib, 0)[0].LibraryMaterial = None
        with self.assertRaisesRegex(StudyError, "no material from the Material Library: A$"):
            studymaterials.study_material_rows(self.study)

    def test_deleted_library_material_is_reported(self):
        a = self.box("A")
        self.study.MainObjects = [a]
        (lib,) = studymaterials.import_materials(self.study, [material("user:air", "Air", AIR)])
        objects.assign(self.study, [a], lib, 0)
        self.doc.removeObject(lib.Name)
        with self.assertRaisesRegex(StudyError, "no material from the Material Library: A$"):
            studymaterials.study_material_rows(self.study)


if __name__ == "__main__":
    unittest.main()
