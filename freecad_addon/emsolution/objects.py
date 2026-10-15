"""Study tree objects and the ID table. No GUI code here, apart from attaching view providers."""

import json
import re

# Gmsh algorithm numbers; the first entry is the default
ALGORITHMS_2D = {"Frontal-Delaunay": 6, "Delaunay": 5, "MeshAdapt": 1, "Automatic": 2}
ALGORITHMS_3D = {"Delaunay": 1, "Frontal": 4, "HXT": 10}


def clean(text):
    return re.sub(r"[^A-Za-z0-9_-]", "_", text)


def display_name(item):
    return getattr(item, "GroupName", "") or item.Label


def volume_name(body):
    """MAT_NAME and the volume's mesh group name."""
    return clean(body.Label)


def item_name(item, body):
    """An excitation's surface group name on one body."""
    return f"{clean(display_name(item))}_{clean(body.Label)}"


def ref_label(body, sub):
    return f"{body.Label}.{sub}" if sub else body.Label


NO_MATERIAL = "— none —"


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


class MaterialLibraryFolder(Folder):
    LABEL = "Material Library"


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
    ("MaterialLibraryGroup", MaterialLibraryFolder),
    ("MaterialsGroup", MaterialsFolder),
    ("ExcitationsGroup", ExcitationsFolder),
    ("MeshSizesGroup", MeshSizesFolder),
)


class Study(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyEnumeration", "MshVersion", "EMSolution", "Gmsh file format version (ASCII)")
        obj.MshVersion = ["4.1", "2.2"]
        obj.addProperty("App::PropertyMap", "MatIds", "IDs", "Body Name -> MAT_ID")
        obj.addProperty("App::PropertyMap", "SmatIds", "IDs", "'Excitation Name|Body Name' -> SMAT_ID")
        obj.addProperty("App::PropertyInteger", "NextMatId", "IDs", "Next MAT_ID")
        obj.NextMatId = 1
        obj.addProperty("App::PropertyInteger", "NextSmatId", "IDs", "Next SMAT_ID")
        obj.NextSmatId = 1001
        for prop, _ in FOLDERS:
            obj.addProperty("App::PropertyLink", prop, "EMSolution", "")
        obj.addProperty("App::PropertyLink", "MeshResult", "EMSolution", "")
        for prop in ("MatIds", "SmatIds", "NextMatId", "NextSmatId"):
            obj.setEditorMode(prop, 1)  # read-only: edit through the ID table
        for prop in [g for g, _ in FOLDERS] + ["MeshResult"]:
            obj.setEditorMode(prop, 2)  # hidden
        obj.addProperty("App::PropertyEnumeration", "Dimension", "Setup")
        obj.Dimension = ["3D", "2D"]
        obj.setEditorMode("Dimension", 1)  # choose at creation; assignments depend on it
        obj.addProperty("App::PropertyEnumeration", "Movement", "Setup")
        obj.Movement = ["No movement", "Sliding motion"]
        for region in ("Main", "Moving"):
            mode, source, refs = region + "Mode", region + "Source", region + "Objects"
            obj.addProperty("App::PropertyEnumeration", mode, "Geometry")
            setattr(obj, mode, ["Unassigned", "Container", "Manual"])
            obj.addProperty("App::PropertyLinkGlobal", source, "Geometry")
            obj.addProperty("App::PropertyLinkListGlobal", refs, "Geometry")
            for prop in (mode, source, refs):
                obj.setEditorMode(prop, 2)  # edit together in the Study panel


class _Named(_Proxy):
    """GroupName holds the typed name: FreeCAD renames a Label that is already taken."""

    def add_group_name(self, obj):
        obj.addProperty("App::PropertyString", "GroupName", "EMSolution", "Name used in the mesh group names")

    def onChanged(self, obj, prop):
        if prop == "Label" and hasattr(obj, "GroupName") and not obj.Document.Restoring:
            obj.GroupName = obj.Label


class Material(_Proxy):
    """An assignment: one body, its Material Library entry and its potential region. Made by assign()."""

    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkGlobal", "Body", "EMSolution", "Body made of this material")
        obj.addProperty("App::PropertyLink", "LibraryMaterial", "EMSolution", "Material from the Material Library")
        obj.addProperty("App::PropertyIntegerConstraint", "Potential", "EMSolution", "POTENTIAL: 0 total, 1+ reduced")
        obj.Potential = (0, 0, 1000000, 1)


class LibraryMaterial(_Proxy):
    """A Study copy of a material: canonical ems_material JSON, edited in the Study."""

    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyString", "Record", "EMSolution", "Canonical material JSON")
        obj.addProperty("App::PropertyString", "MaterialId", "EMSolution", "material_id in the record")
        obj.addProperty("App::PropertyString", "Family", "EMSolution", "Material family in the record")
        obj.setEditorMode("Record", 2)  # hidden: edit through the Material Library
        for prop in ("MaterialId", "Family"):
            obj.setEditorMode(prop, 1)

    def onChanged(self, obj, prop):
        if prop == "Record" and obj.Record and not obj.Document.Restoring:
            data = json.loads(obj.Record)
            obj.MaterialId = data["material_id"]
            obj.Family = data["identity"]["family"]
        elif prop == "Label" and getattr(obj, "Record", "") and not obj.Document.Restoring:
            data = json.loads(obj.Record)  # the record's name is the source; a tree rename writes it
            if data["identity"]["name"] != obj.Label:
                data["identity"]["name"] = obj.Label
                obj.Record = json.dumps(data, ensure_ascii=False, indent=2) + "\n"


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


def study_contents(study):
    """Everything the Study owns: folders after their items, Materials before the Material Library."""
    out = []
    for obj in reversed(study.Group):
        out += list(getattr(obj, "Group", []))
        out.append(obj)
    return out


def delete_contents(study):
    """Remove everything the Study owns, but not the Study itself. No transaction."""
    for obj in study_contents(study):
        study.Document.removeObject(obj.Name)


def _add(study, group_prop, proxy_cls, label):
    obj = study.Document.addObject("App::FeaturePython", proxy_cls.__name__)
    proxy_cls(obj)
    obj.Label = label
    if hasattr(obj, "GroupName"):
        obj.GroupName = label
    getattr(study, group_prop).addObject(obj)
    return obj


def make_library_material(study, record_json):
    """record_json: canonical ems_material JSON. The Label is the material's name."""
    name = json.loads(record_json)["identity"]["name"]
    obj = _add(study, "MaterialLibraryGroup", LibraryMaterial, name)
    obj.Record = record_json
    if getattr(obj, "ViewObject", None) is not None:  # GUI running
        from . import taskpanels

        taskpanels.ViewProviderLibraryMaterial(obj.ViewObject)
    return obj


def assignment_of(study):
    """{body Name: assignment} for the Study's assignments whose body still exists."""
    return {m.Body.Name: m for m in materials(study) if m.Body is not None}


def assignment_label(m):
    """The tree label "<body>: <material>"; FreeCAD keeps labels unique, so it cannot be the body's label."""
    lib = m.LibraryMaterial.Label if m.LibraryMaterial else NO_MATERIAL
    return f"{m.Body.Label}: {lib}" if m.Body else m.Label


def assign(study, bodies, lib, potential):
    """Give each body lib and potential, updating its assignment or adding one. Returns them in body order."""
    have = assignment_of(study)
    out = []
    for body in bodies:
        m = have.get(body.Name)
        if m is None:
            m = _add(study, "MaterialsGroup", Material, body.Label)
            m.Body = body
            if getattr(m, "ViewObject", None) is not None:  # GUI running
                from . import taskpanels

                taskpanels.ViewProviderItem(m.ViewObject)
            have[body.Name] = m
        m.LibraryMaterial, m.Potential = lib, potential
        m.Label = assignment_label(m)
        out.append(m)
    return out


def unassign(study, bodies):
    """Remove the assignments of bodies; bodies without one are skipped."""
    have = assignment_of(study)
    for body in bodies:
        m = have.pop(body.Name, None)
        if m is not None:
            study.Document.removeObject(m.Name)


def sync_labels(study):
    """Rewrite assignment labels after a body or material was renamed."""
    for m in materials(study):
        label = assignment_label(m)
        if m.Label != label:
            m.Label = label


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


def library_materials(study):
    return list(study.MaterialLibraryGroup.Group)


def material_users(lib):
    """Assignments of lib's Study that link to it; none once its Study is gone."""
    study = owner_study(lib)
    return [m for m in materials(study) if m.LibraryMaterial == lib] if study else []


def user_labels(lib):
    """For messages: the body label of each assignment using lib, or the assignment label if the body is gone."""
    return [m.Body.Label if m.Body else m.Label for m in material_users(lib)]


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
        return [(item.Body, "")] if item.Body else []
    return [(b, s) for b, subs in item.References for s in subs]


def material_rows(study):
    """Rows for the Materials panel: (body, refs, [body, material, MAT_ID, POTENTIAL]).

    Every main-geometry body, then bodies outside it that still have an assignment.
    """
    have = assignment_of(study)
    main = _main_bodies(study)
    inside = {b.Name for b in main}
    rows = []
    for b in main + [m.Body for m in have.values() if m.Body.Name not in inside]:
        m = have.get(b.Name)
        lib = m.LibraryMaterial.Label if m and m.LibraryMaterial else NO_MATERIAL
        name = b.Label if b.Name in inside else f"{b.Label} (not in main geometry)"
        rows.append((b, [(b, "")], [name, lib, study.MatIds.get(b.Name, "–"), str(m.Potential) if m else ""]))
    return rows


def library_rows(study):
    """Rows for the Material Library panel: (material, refs of its users, [name, family, ID, used by])."""
    rows = []
    for lib in library_materials(study):
        users = material_users(lib)
        refs = [(m.Body, "") for m in users if m.Body]
        rows.append((lib, refs, [lib.Label, lib.Family, lib.MaterialId, ", ".join(user_labels(lib))]))
    return rows


def excitation_rows(study):
    """Rows for the Excitations panel: (excitation, refs, [name, body, faces, SMAT_ID])."""
    rows = []
    for e in excitations(study):
        rows += [
            (
                e,
                [(b, f) for f in faces],
                [display_name(e), b.Label, ", ".join(faces), study.SmatIds.get(f"{e.Name}|{b.Name}", "–")],
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
    """Main-geometry bodies without an assignment."""
    have = assignment_of(study)
    return [b for b in _main_bodies(study) if b.Name not in have]


def _main_bodies(study):
    from . import geometry

    return geometry.region(study, "Main")[0]


NO_MAIN_GEOMETRY = "Choose the Study's main geometry first: a Part, a Group or Manual selection in the Study panel."


def assignment_problem(study, bodies):
    """Why bodies cannot get Materials, Excitations or Mesh Sizes, or "" when they can."""
    main = {b.Name for b in _main_bodies(study)}
    if not main:
        return NO_MAIN_GEOMETRY
    outside = list(dict.fromkeys(b.Label for b in bodies if b.Name not in main))
    if outside:
        return (
            "Not in the Study's main geometry: "
            + ", ".join(outside)
            + ". Add them to it in the Study panel or select other bodies."
        )
    return ""


def volume_keys(study):
    return [b.Name for b in _main_bodies(study)]


def surface_keys(study):
    if study.Dimension == "2D":
        return []  # 2D Studies have no excitations yet
    included = set(volume_keys(study))
    return list(
        dict.fromkeys(
            f"{e.Name}|{b.Name}" for e in excitations(study) for b, _ in subs_by_body(e) if b.Name in included
        )
    )


def update_ids(study):
    """Give every body and (excitation, body) pair an ID; drop entries that are gone.

    Counters only grow, so a dropped ID is never handed out again.
    """
    vkeys, skeys = volume_keys(study), surface_keys(study)
    vol = {k: v for k, v in study.MatIds.items() if k in vkeys}
    surf = {k: v for k, v in study.SmatIds.items() if k in skeys}
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

    study.NextMatId = give(vol, vkeys, study.NextMatId)
    study.NextSmatId = give(surf, skeys, study.NextSmatId)
    study.MatIds, study.SmatIds = vol, surf


def set_id(study, table, key, new_id):
    """table: "MatIds" or "SmatIds". Raises ValueError for a bad or duplicate ID."""
    ids = dict(getattr(study, table))
    if key not in ids:
        raise ValueError(f"unknown entry {key}")
    if new_id < 1:
        raise ValueError("IDs must be 1 or more")
    taken = {int(v) for t in ("MatIds", "SmatIds") for k, v in getattr(study, t).items() if (t, k) != (table, key)}
    if new_id in taken:
        raise ValueError(f"ID {new_id} is already used")
    ids[key] = str(new_id)
    setattr(study, table, ids)
    counter = "NextMatId" if table == "MatIds" else "NextSmatId"
    top = max(int(v) for v in ids.values())
    setattr(study, counter, max(getattr(study, counter), top + 1))


def id_rows(study):
    """Rows for the ID table dialog: (table, key, name, id), volumes first."""
    rows = []
    for name in volume_keys(study):
        if name in study.MatIds:
            body = study.Document.getObject(name)
            rows.append(("MatIds", name, volume_name(body), int(study.MatIds[name])))
    for e in excitations(study):
        for b, _ in subs_by_body(e):
            key = f"{e.Name}|{b.Name}"
            if key in study.SmatIds:
                rows.append(("SmatIds", key, item_name(e, b), int(study.SmatIds[key])))
    return rows
