"""Study tree objects and the ID table. No GUI code here."""
import re

GROUPS = (("MaterialsGroup", "Materials"),
          ("ExcitationsGroup", "Excitations"),
          ("MeshSizesGroup", "Mesh Sizes"))


def clean(text):
    return re.sub(r"[^A-Za-z0-9_-]", "_", text)


def item_name(item, body):
    return f"{clean(getattr(item, 'GroupName', '') or item.Label)}_{clean(body.Label)}"


class _Proxy:
    def dumps(self):
        return None

    def loads(self, state):
        return None


class Study(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyString", "OutputFolder", "EMSolution",
                        "Empty = folder <document>_mesh next to the .FCStd")
        obj.addProperty("App::PropertyLength", "DefaultMeshSize", "EMSolution",
                        "Mesh size for bodies without a Mesh Size item")
        obj.DefaultMeshSize = 5.0
        obj.addProperty("App::PropertyEnumeration", "MshVersion", "EMSolution",
                        "Gmsh file format version (ASCII)")
        obj.MshVersion = ["4.1", "2.2"]
        obj.addProperty("App::PropertyMap", "VolumeIds", "IDs", "Body Name -> volume ID")
        obj.addProperty("App::PropertyMap", "SurfaceIds", "IDs",
                        "'Excitation Name|Body Name' -> surface ID")
        obj.addProperty("App::PropertyInteger", "NextVolumeId", "IDs", "Next volume ID")
        obj.NextVolumeId = 1
        obj.addProperty("App::PropertyInteger", "NextSurfaceId", "IDs", "Next surface ID")
        obj.NextSurfaceId = 1001
        for prop, _ in GROUPS:
            obj.addProperty("App::PropertyLink", prop, "EMSolution", "")
        obj.addProperty("App::PropertyLink", "MeshResult", "EMSolution", "")
        for prop in ("VolumeIds", "SurfaceIds", "NextVolumeId", "NextSurfaceId"):
            obj.setEditorMode(prop, 1)  # read-only: edit through the ID table
        for prop in [g for g, _ in GROUPS] + ["MeshResult"]:
            obj.setEditorMode(prop, 2)  # hidden


class _Named(_Proxy):
    """GroupName holds the typed name: FreeCAD renames a Label that is already taken."""

    def add_group_name(self, obj):
        obj.addProperty("App::PropertyString", "GroupName", "EMSolution",
                        "Name used in the mesh group names")

    def onChanged(self, obj, prop):
        if prop == "Label" and hasattr(obj, "GroupName") and not obj.Document.Restoring:
            obj.GroupName = obj.Label


class Material(_Named):
    def __init__(self, obj):
        obj.Proxy = self
        self.add_group_name(obj)
        obj.addProperty("App::PropertyLinkListGlobal", "References", "EMSolution",
                        "Bodies made of this material")


class Excitation(_Named):
    def __init__(self, obj):
        obj.Proxy = self
        self.add_group_name(obj)
        obj.addProperty("App::PropertyLinkSubListGlobal", "References", "EMSolution",
                        "Body faces of this excitation")


class MeshSize(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLength", "Size", "EMSolution", "Element size")
        self.add_references(obj)

    def add_references(self, obj):
        obj.addProperty("App::PropertyLinkSubListGlobal", "References", "EMSolution",
                        "Bodies (empty sub-element), faces, edges and vertices meshed with this size")

    def onDocumentRestored(self, obj):
        if obj.getTypeIdOfProperty("References") == "App::PropertyLinkListGlobal":  # older files
            bodies = obj.References
            obj.removeProperty("References")
            self.add_references(obj)
            obj.References = [(b, "") for b in bodies]


def make_study(doc):
    study = doc.addObject("App::DocumentObjectGroupPython", "Study")
    Study(study)
    for prop, label in GROUPS:
        group = doc.addObject("App::DocumentObjectGroup", prop.replace("Group", ""))
        group.Label = label
        study.addObject(group)
        setattr(study, prop, group)
    return study


def find_study(doc):
    return next((o for o in doc.Objects if isinstance(getattr(o, "Proxy", None), Study)), None)


def _add(study, group_prop, proxy_cls, label):
    obj = study.Document.addObject("App::FeaturePython", proxy_cls.__name__)
    proxy_cls(obj)
    obj.Label = label
    if hasattr(obj, "GroupName"):
        obj.GroupName = label
    getattr(study, group_prop).addObject(obj)
    return obj


def make_material(study, label, bodies):
    obj = _add(study, "MaterialsGroup", Material, label)
    obj.References = bodies
    return obj


def make_excitation(study, label, faces):
    """faces: list of (body, "FaceN")."""
    obj = _add(study, "ExcitationsGroup", Excitation, label)
    obj.References = faces
    return obj


def make_mesh_size(study, size, refs):
    """refs: list of (body, sub), sub = "" for the whole body or "FaceN", "EdgeN", "VertexN"."""
    obj = _add(study, "MeshSizesGroup", MeshSize, "MeshSize")
    obj.Size = size
    obj.References = refs
    return obj


def materials(study):
    return list(study.MaterialsGroup.Group)


def excitations(study):
    return list(study.ExcitationsGroup.Group)


def mesh_sizes(study):
    return list(study.MeshSizesGroup.Group)


def owning_body(obj):
    """A face picked in the 3D view resolves to a PartDesign feature; use its Body."""
    parent = obj.getParentGeoFeatureGroup()
    if parent is not None and parent.isDerivedFrom("PartDesign::Body"):
        return parent
    return obj


def pick_body(obj):
    """The solid body behind a picked object; None for tree folders, study items and containers."""
    body = owning_body(obj)
    return body if body.isDerivedFrom("Part::Feature") else None


def subs_by_body(item):
    """[(body, [sub-element names])] in reference order, one entry per body."""
    out = {}
    for body, subs in item.References:
        out.setdefault(body.Name, (body, []))[1].extend(subs)
    return list(out.values())


def volume_keys(study):
    return list(dict.fromkeys(b.Name for m in materials(study) for b in m.References))


def surface_keys(study):
    return list(dict.fromkeys(f"{e.Name}|{b.Name}"
                              for e in excitations(study) for b, _ in subs_by_body(e)))


def update_ids(study):
    """Give every body and (excitation, body) pair an ID; drop entries that are gone.

    Counters only grow, so a dropped ID is never handed out again.
    """
    vkeys, skeys = volume_keys(study), surface_keys(study)
    vol = {k: v for k, v in study.VolumeIds.items() if k in vkeys}
    surf = {k: v for k, v in study.SurfaceIds.items() if k in skeys}
    used = {int(v) for v in list(vol.values()) + list(surf.values())}

    def give(table, keys, counter):
        for key in keys:
            if key not in table:
                while counter in used:
                    counter += 1
                table[key] = str(counter)
                used.add(counter)
                counter += 1
        return counter

    study.NextVolumeId = give(vol, vkeys, study.NextVolumeId)
    study.NextSurfaceId = give(surf, skeys, study.NextSurfaceId)
    study.VolumeIds, study.SurfaceIds = vol, surf


def set_id(study, table, key, new_id):
    """table: "VolumeIds" or "SurfaceIds". Raises ValueError for a bad or duplicate ID."""
    ids = dict(getattr(study, table))
    if key not in ids:
        raise ValueError(f"unknown entry {key}")
    if new_id < 1:
        raise ValueError("IDs must be 1 or more")
    taken = {int(v) for t in ("VolumeIds", "SurfaceIds")
             for k, v in getattr(study, t).items() if (t, k) != (table, key)}
    if new_id in taken:
        raise ValueError(f"ID {new_id} is already used")
    ids[key] = str(new_id)
    setattr(study, table, ids)
    counter = "NextVolumeId" if table == "VolumeIds" else "NextSurfaceId"
    top = max(int(v) for v in ids.values())
    setattr(study, counter, max(getattr(study, counter), top + 1))


def id_rows(study):
    """Rows for the ID table dialog: (table, key, name, id), volumes first."""
    rows = []
    for m in materials(study):
        for b in m.References:
            if b.Name in study.VolumeIds:
                rows.append(("VolumeIds", b.Name, item_name(m, b), int(study.VolumeIds[b.Name])))
    for e in excitations(study):
        for b, _ in subs_by_body(e):
            key = f"{e.Name}|{b.Name}"
            if key in study.SurfaceIds:
                rows.append(("SurfaceIds", key, item_name(e, b), int(study.SurfaceIds[key])))
    return rows
