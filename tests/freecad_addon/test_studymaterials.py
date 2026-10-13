"""Study Material Library tests. Run from the repo root: pixi run pytest tests/freecad_addon/test_studymaterials.py"""

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

from .materialdata import AIR, COPPER, STEEL, record


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
        mat = objects.make_material(self.study, "Gap", [self.box("A")])
        mat.LibraryMaterial = lib
        self.assertFalse(self.repo.is_deletable("user:air"))
        with self.assertRaisesRegex(ReadOnlyMaterialError, "Gap"):
            self.repo.delete("user:air")
        mat.LibraryMaterial = None
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


if __name__ == "__main__":
    unittest.main()
