"""Study tree objects and the ID table. No GUI code here, apart from attaching view providers."""

import re

# Gmsh algorithm numbers; the first entry is the default
ALGORITHMS_2D = {"Frontal-Delaunay": 6, "Delaunay": 5, "MeshAdapt": 1, "Automatic": 2}
ALGORITHMS_3D = {"Delaunay": 1, "Frontal": 4, "HXT": 10}


def clean(text):
    return re.sub(r"[^A-Za-z0-9_-]", "_", text)


def display_name(item):
    return getattr(item, "GroupName", "") or item.Label


def item_name(item, body):
    if isinstance(item.Proxy, Material):
        return clean(body.Label)
    return f"{clean(display_name(item))}_{clean(body.Label)}"


def ref_label(body, sub):
    return f"{body.Label}.{sub}" if sub else body.Label


class _Proxy:
    def dumps(self):
        return None

    def loads(self, state):
        return None


class Folder(_Proxy):
    """A study folder with a fixed Label."""

    LABEL = ""

    def __init__(self, obj):
        obj.Proxy = self

    def onBeforeChangeLabel(self, obj, new_label):
        return self.LABEL  # FreeCAD uses the returned text instead of the typed one


class MaterialsFolder(Folder):
    LABEL = "Materials"


class ExcitationsFolder(Folder):
    LABEL = "Excitations"


class MeshSizesFolder(Folder):
    """Also holds the mesh settings that apply to the whole study."""

    LABEL = "Mesh Sizes"

    def __init__(self, obj):
        super().__init__(obj)
        add = obj.addProperty
        add("App::PropertyLength", "DefaultMeshSize", "Mesh", "Mesh size for bodies without a Mesh Size item")
        obj.DefaultMeshSize = 5.0
        add("App::PropertyEnumeration", "SurfaceAlgorithm", "Mesh", "Gmsh algorithm for the faces")
        obj.SurfaceAlgorithm = list(ALGORITHMS_2D)
        add("App::PropertyEnumeration", "VolumeAlgorithm", "Mesh", "Gmsh algorithm for the volumes")
        obj.VolumeAlgorithm = list(ALGORITHMS_3D)
        add("App::PropertyFloatConstraint", "SizeFactor", "Mesh", "Multiplies every mesh size")
        obj.SizeFactor = (1.0, 0.01, 100.0, 0.1)
        add("App::PropertyLength", "MinSize", "Mesh", "Smallest element size, 0 = no limit")
        add("App::PropertyLength", "MaxSize", "Mesh", "Largest element size, 0 = no limit")
        add("App::PropertyIntegerConstraint", "SmoothingSteps", "Mesh", "Smoothing passes over the face meshes")
        obj.SmoothingSteps = (1, 0, 100, 1)
        add("App::PropertyBool", "OptimizeNetgen", "Mesh", "Improve element quality with Netgen (slower)")


FOLDERS = (
    ("MaterialsGroup", MaterialsFolder),
    ("ExcitationsGroup", ExcitationsFolder),
    ("MeshSizesGroup", MeshSizesFolder),
)


class Study(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty(
            "App::PropertyString", "OutputFolder", "EMSolution", "Empty = folder <document>_mesh next to the .FCStd"
        )
        obj.addProperty("App::PropertyEnumeration", "MshVersion", "EMSolution", "Gmsh file format version (ASCII)")
        obj.MshVersion = ["4.1", "2.2"]
        obj.addProperty("App::PropertyMap", "VolumeIds", "IDs", "Body Name -> volume ID")
        obj.addProperty("App::PropertyMap", "SurfaceIds", "IDs", "'Excitation Name|Body Name' -> surface ID")
        obj.addProperty("App::PropertyInteger", "NextVolumeId", "IDs", "Next volume ID")
        obj.NextVolumeId = 1
        obj.addProperty("App::PropertyInteger", "NextSurfaceId", "IDs", "Next surface ID")
        obj.NextSurfaceId = 1001
        for prop, _ in FOLDERS:
            obj.addProperty("App::PropertyLink", prop, "EMSolution", "")
        obj.addProperty("App::PropertyLink", "MeshResult", "EMSolution", "")
        for prop in ("VolumeIds", "SurfaceIds", "NextVolumeId", "NextSurfaceId"):
            obj.setEditorMode(prop, 1)  # read-only: edit through the ID table
        for prop in [g for g, _ in FOLDERS] + ["MeshResult"]:
            obj.setEditorMode(prop, 2)  # hidden
        self.add_setup(obj)

    @staticmethod
    def add_setup(obj, legacy=False):
        """Add missing properties only; restoring an old file must not reset its settings."""
        if "Dimension" not in obj.PropertiesList:
            obj.addProperty("App::PropertyEnumeration", "Dimension", "Setup")
            obj.Dimension = ["3D", "2D"]
        obj.setEditorMode("Dimension", 1)  # choose at creation; assignments depend on it
        if "Movement" not in obj.PropertiesList:
            obj.addProperty("App::PropertyEnumeration", "Movement", "Setup")
            obj.Movement = ["No movement", "Sliding motion"]
        for region in ("Main", "Moving"):
            mode, source, refs = region + "Mode", region + "Source", region + "Objects"
            if mode not in obj.PropertiesList:
                obj.addProperty("App::PropertyEnumeration", mode, "Geometry")
                choices = ["Unassigned", "Container", "Manual"]
                if region == "Main":
                    choices.append("Materials")
                setattr(obj, mode, choices)
                if region == "Main" and legacy:
                    setattr(obj, mode, "Materials")
            if source not in obj.PropertiesList:
                obj.addProperty("App::PropertyLinkGlobal", source, "Geometry")
            if refs not in obj.PropertiesList:
                obj.addProperty("App::PropertyLinkListGlobal", refs, "Geometry")
            for prop in (mode, source, refs):
                obj.setEditorMode(prop, 2)  # edit together in the Study panel
        if "LegacyOutput" not in obj.PropertiesList:
            obj.addProperty("App::PropertyBool", "LegacyOutput", "Setup")
            obj.LegacyOutput = legacy
        obj.setEditorMode("LegacyOutput", 2)

    def onDocumentRestored(self, obj):
        self.add_setup(obj, legacy=True)


class _Named(_Proxy):
    """GroupName holds the typed name: FreeCAD renames a Label that is already taken."""

    def add_group_name(self, obj):
        obj.addProperty("App::PropertyString", "GroupName", "EMSolution", "Name used in the mesh group names")

    def onChanged(self, obj, prop):
        if prop == "Label" and hasattr(obj, "GroupName") and not obj.Document.Restoring:
            obj.GroupName = obj.Label


class Material(_Named):
    def __init__(self, obj):
        obj.Proxy = self
        self.add_group_name(obj)
        obj.addProperty("App::PropertyLinkListGlobal", "References", "EMSolution", "Bodies made of this material")


class Excitation(_Named):
    def __init__(self, obj):
        obj.Proxy = self
        self.add_group_name(obj)
        obj.addProperty("App::PropertyLinkSubListGlobal", "References", "EMSolution", "Body faces of this excitation")


class MeshSize(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLength", "Size", "EMSolution", "Element size")
        obj.addProperty(
            "App::PropertyLinkSubListGlobal",
            "References",
            "EMSolution",
            "Bodies (empty sub-element), faces, edges and vertices meshed with this size",
        )


def _make_folder(study, prop, cls):
    folder = study.Document.addObject("App::DocumentObjectGroupPython", prop.replace("Group", ""))
    cls(folder)
    folder.Label = cls.LABEL
    study.addObject(folder)
    setattr(study, prop, folder)
    if getattr(folder, "ViewObject", None) is not None:  # GUI running
        from . import taskpanels

        taskpanels.ViewProviderFolder(folder.ViewObject)
    return folder


def make_study(doc, dimension="3D", label=None):
    if dimension not in ("2D", "3D"):
        raise ValueError("Study dimension must be 2D or 3D")
    study = doc.addObject("App::DocumentObjectGroupPython", "Study")
    Study(study)
    study.Dimension = dimension
    if dimension == "2D":
        study.MainMode = "Unassigned"
    if label:
        study.Label = label
    for prop, cls in FOLDERS:
        _make_folder(study, prop, cls)
    return study


def studies(doc):
    return [o for o in doc.Objects if isinstance(getattr(o, "Proxy", None), Study)]


def find_study(doc):
    """Convenience for a document with exactly one Study; never guess between several."""
    found = studies(doc)
    return found[0] if len(found) == 1 else None


def owner_study(obj):
    """Follow group membership, not the links in material/geometry references."""
    while obj is not None:
        if isinstance(getattr(obj, "Proxy", None), Study):
            return obj
        obj = obj.getParentGroup()
    return None


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


def is_study_object(obj):
    """The Study, a folder or an item made by this addon."""
    return isinstance(getattr(obj, "Proxy", None), _Proxy)


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


def is_item(obj):
    return isinstance(getattr(obj, "Proxy", None), (Material, Excitation, MeshSize))


def item_refs(item):
    """[(body, sub)] of a Material, Excitation or Mesh Size; sub "" = the whole body."""
    if isinstance(item.Proxy, Material):
        return [(b, "") for b in item.References]
    return [(b, s) for b, subs in item.References for s in subs]


def material_rows(study):
    """Rows for the Materials panel: (material, refs, [name, body, volume ID])."""
    rows = []
    for m in materials(study):
        rows += [
            (m, [(b, "")], [display_name(m), b.Label, study.VolumeIds.get(b.Name, "–")]) for b in m.References
        ] or [(m, [], [display_name(m), "", ""])]
    return rows


def excitation_rows(study):
    """Rows for the Excitations panel: (excitation, refs, [name, body, faces, surface ID])."""
    rows = []
    for e in excitations(study):
        rows += [
            (
                e,
                [(b, f) for f in faces],
                [display_name(e), b.Label, ", ".join(faces), study.SurfaceIds.get(f"{e.Name}|{b.Name}", "–")],
            )
            for b, faces in subs_by_body(e)
        ] or [(e, [], [display_name(e), "", "", ""])]
    return rows


def mesh_size_rows(study):
    """Rows for the Mesh Sizes panel: (mesh size, refs, [name, size, applies to])."""
    return [
        (
            s,
            item_refs(s),
            [display_name(s), f"{s.Size.Value:g} mm", ", ".join(ref_label(b, sub) for b, sub in item_refs(s))],
        )
        for s in mesh_sizes(study)
    ]


def bodies_without_material(study):
    """Selected bodies without materials, or referenced bodies in the legacy workflow."""
    have = {b.Name for m in materials(study) for b in m.References}
    if study.MainMode != "Materials":
        from . import geometry

        return [b for b in geometry.region(study, "Main")[0] if b.Name not in have]
    out = {}
    for item in excitations(study) + mesh_sizes(study):
        for b, _ in subs_by_body(item):
            if b.Name not in have:
                out.setdefault(b.Name, b)
    return list(out.values())


def volume_keys(study):
    if study.MainMode != "Materials":
        from . import geometry

        return [b.Name for b in geometry.region(study, "Main")[0]]
    return list(dict.fromkeys(b.Name for m in materials(study) for b in m.References))


def surface_keys(study):
    included = set(volume_keys(study)) if study.MainMode != "Materials" else None
    return list(
        dict.fromkeys(
            f"{e.Name}|{b.Name}"
            for e in excitations(study)
            for b, _ in subs_by_body(e)
            if included is None or b.Name in included
        )
    )


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
    taken = {
        int(v) for t in ("VolumeIds", "SurfaceIds") for k, v in getattr(study, t).items() if (t, k) != (table, key)
    }
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
    if study.MainMode != "Materials":
        material_of = {b.Name: m for m in materials(study) for b in m.References}
        for name in volume_keys(study):
            if name in study.VolumeIds:
                body = study.Document.getObject(name)
                mat = material_of.get(name)
                label = item_name(mat, body) if mat else f"No material: {body.Label}"
                rows.append(("VolumeIds", name, label, int(study.VolumeIds[name])))
    for m in materials(study):
        for b in m.References:
            if study.MainMode == "Materials" and b.Name in study.VolumeIds:
                rows.append(("VolumeIds", b.Name, item_name(m, b), int(study.VolumeIds[b.Name])))
    for e in excitations(study):
        for b, _ in subs_by_body(e):
            key = f"{e.Name}|{b.Name}"
            if key in study.SurfaceIds:
                rows.append(("SurfaceIds", key, item_name(e, b), int(study.SurfaceIds[key])))
    return rows
