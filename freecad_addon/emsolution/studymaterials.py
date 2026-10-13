"""Study Material Library <-> EMS Material Manager (ems_material). No GUI code here."""

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

from . import objects

SOURCE = "Study"
ROOT_ENV = "EMS_MATERIAL_MANAGER_ROOT"


def record_material(lib):
    return material_from_json(lib.Record)


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
            raise ReadOnlyMaterialError(f"{obj.Label} is used by: " + ", ".join(m.Label for m in users))
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
