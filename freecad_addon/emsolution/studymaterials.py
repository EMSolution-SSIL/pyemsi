"""Study Material Library <-> EMS Material Manager (ems_material). No GUI code here."""

import copy
import os
from dataclasses import replace

from ems_material import (
    MaterialAlreadyExistsError,
    MaterialConflictError,
    MaterialNotFoundError,
    ReadOnlyMaterialError,
    VersionMetadata,
    load_material,
    material_from_json,
    material_to_json,
    save_material,
)

from ems_material.adapters import EMSolutionInputAdapter

from . import jobwriter, objects
from .jobwriter import StudyError

SOURCE = "Study"
ROOT_ENV = "EMS_MATERIAL_MANAGER_ROOT"


def record_material(lib):
    return material_from_json(lib.Record)


def is_manager_root(path):
    """True for a Material Manager root: a folder with manager.config.json."""
    return bool(path) and os.path.isfile(os.path.join(path, "manager.config.json"))


def library_root():
    """The Material Manager root shared with eMotorSolution, or None when none is set."""
    env = os.environ.get(ROOT_ENV)
    if env and os.path.isdir(env):
        return env
    from ems_material.gui.product_exchange import remembered_library_root  # imports qtpy

    root = remembered_library_root()
    return str(root) if root else None


def _transaction(study, title, change):
    doc = study.Document
    doc.openTransaction(title)
    try:
        result = change()
    except Exception:
        doc.abortTransaction()
        raise
    doc.commitTransaction()
    doc.recompute()
    return result


def import_materials(study, materials):
    """Copy library materials into the Material Library as one undo step. Returns the new objects."""
    have = {o.MaterialId for o in objects.library_materials(study)}
    taken = [m.material_id for m in materials if m.material_id in have]
    if taken:
        raise MaterialAlreadyExistsError("Already in the Material Library: " + ", ".join(taken))
    texts = [material_to_json(m) for m in materials]
    return _transaction(study, "Import materials", lambda: [objects.make_library_material(study, t) for t in texts])


class StudyMaterialRepository:
    """The ems_material MaterialRepository protocol over a Study's Material Library.

    Every write is one FreeCAD transaction; on_change() runs after it is committed.
    """

    def __init__(self, study, on_change=None):
        self.study = study
        self.on_change = on_change

    def _objects(self):
        return {o.MaterialId: o for o in objects.library_materials(self.study)}

    def _object(self, material_id):
        obj = self._objects().get(material_id)
        if obj is None:
            raise MaterialNotFoundError(f"Material not found in the Material Library: {material_id}")
        return obj

    def _write(self, title, change):
        result = _transaction(self.study, title, change)
        if self.on_change is not None:
            self.on_change()
        return result

    def list(self):
        return tuple(record_material(o) for o in objects.library_materials(self.study))

    def get(self, material_id):
        return record_material(self._object(material_id))

    def create(self, material):
        if material.material_id in self._objects():
            raise MaterialAlreadyExistsError(f"Material already in the Material Library: {material.material_id}")
        text = material_to_json(material)
        self._write("Add material", lambda: objects.make_library_material(self.study, text))
        return material

    def update(self, material, *, expected_version=None):
        obj = self._object(material.material_id)
        current = record_material(obj)
        if expected_version is not None and current.material_version != expected_version:
            raise MaterialConflictError(
                f"Expected {expected_version}, found {current.material_version} for {material.material_id}"
            )
        text = material_to_json(material)

        def change():
            obj.Record = text
            obj.Label = material.name

        self._write("Edit material", change)
        return material

    def duplicate(self, source_id, *, new_material_id, new_name, author, updated_at, change_note="Duplicated material"):
        source = self.get(source_id)
        origin = f"{source.material_id}@{source.material_version}"
        copy = replace(
            source,
            material_id=new_material_id,
            material_version="1.0.0",
            identity=replace(source.identity, name=new_name),
            provenance=replace(
                source.provenance,
                source_type="USER_INPUT",
                reference=origin,
                notes="Duplicated from an existing material",
            ),
            version_metadata=VersionMetadata(author, updated_at, change_note),
            parent_ref=origin,
        )
        return self.create(copy)

    def delete(self, material_id):
        obj = self._object(material_id)
        users = objects.material_users(obj)
        if users:
            raise ReadOnlyMaterialError(f"{obj.Label} is used by: " + ", ".join(objects.user_labels(obj)))
        self._write("Delete material", lambda: self.study.Document.removeObject(obj.Name))

    def search(self, *, family=None, text=None, manufacturer=None, tags=()):
        text_query = text.casefold() if text else None
        tag_query = {t.casefold() for t in tags}
        found = []
        for m in self.list():
            identity = m.identity
            if family and identity.family.casefold() != family.casefold():
                continue
            if manufacturer and (identity.manufacturer or "").casefold() != manufacturer.casefold():
                continue
            if tag_query and not tag_query <= {t.casefold() for t in identity.tags}:
                continue
            words = [m.material_id, identity.name, identity.grade or "", identity.manufacturer or ""]
            haystack = " ".join(words + list(identity.aliases) + list(identity.tags)).casefold()
            if text_query and text_query not in haystack:
                continue
            found.append(m)
        return tuple(found)

    def import_json(self, source):
        return self.create(load_material(source))

    def export_json(self, material_id, destination):
        save_material(self.get(material_id), destination)

    def source_for(self, material_id):
        self._object(material_id)
        return SOURCE

    def is_writable(self, material_id):
        self._object(material_id)
        return True

    def is_deletable(self, material_id):
        return not objects.material_users(self._object(material_id))

    def list_sources(self):
        return (SOURCE,)


def study_material_rows(study):
    """[(MAT_ID, MAT_NAME, POTENTIAL, material)] for the Study's bodies, in MAT_ID order."""
    volumes, _, _ = jobwriter.check(study)
    objects.update_ids(study)
    have = objects.assignment_of(study)
    missing = [b.Label for b, _ in volumes if b.Name not in have or have[b.Name].LibraryMaterial is None]
    if missing:
        raise StudyError("These bodies have no material from the Material Library: " + ", ".join(missing))
    rows = [
        (
            int(study.MatIds[b.Name]),
            objects.volume_name(b),
            have[b.Name].Potential,
            record_material(have[b.Name].LibraryMaterial),
        )
        for b, _ in volumes
    ]
    return sorted(rows, key=lambda r: r[0])


def material_properties(rows):
    """16_Material_Properties.16_1_3D_Element_Properties and 20_BH_Curve for rows of study_material_rows().

    One entry per row; B-H curves once per material, numbered from 1 in first-use order.
    """
    adapter = EMSolutionInputAdapter()
    entries, curves, entry_of = [], [], {}
    for mat_id, mat_name, potential, material in rows:
        if material.material_id not in entry_of:
            try:
                payload = adapter.export_material(material).payload
            except (ValueError, TypeError) as exc:
                raise StudyError(f"Material {material.name}: {exc}") from None
            renumber = {}
            for curve in payload["bh_curves"]:
                renumber[curve["BH_CURVE_ID"]] = len(curves) + 1
                curves.append({**copy.deepcopy(curve), "BH_CURVE_ID": len(curves) + 1})
            entry = copy.deepcopy(payload["material"])
            magnetic = entry.get("MagneticProperty", {})
            if "BH_CURVE_ID" in magnetic:
                magnetic["BH_CURVE_ID"] = renumber[magnetic["BH_CURVE_ID"]]
            if "BH_CURVE_XYZ" in magnetic:
                xyz = magnetic["BH_CURVE_XYZ"]
                xyz["BH_XYZ_ID"] = [renumber[i] for i in xyz["BH_XYZ_ID"]]
            entry_of[material.material_id] = entry
        entry = copy.deepcopy(entry_of[material.material_id])
        entry.update(MAT_ID=mat_id, MAT_NAME=mat_name, POTENTIAL=potential)
        entries.append(entry)
    return {"16_Material_Properties": {"16_1_3D_Element_Properties": entries}, "20_BH_Curve": curves}
