"""Study tree objects and the ID table. No GUI code here, apart from attaching view providers."""

import json
import re

# Gmsh algorithm numbers; the first entry is the default
ALGORITHMS_2D = {"Frontal-Delaunay": 6, "Delaunay": 5, "MeshAdapt": 1, "Automatic": 2}
ALGORITHMS_3D = {"Delaunay": 1, "Frontal": 4, "HXT": 10}
RECOMBINATION_ALGORITHMS = {"Blossom": 1, "Simple": 0, "Blossom full-quad": 3, "Simple full-quad": 2}


def clean(text):
    return re.sub(r"[^A-Za-z0-9_-]", "_", text)


def display_name(item):
    return getattr(item, "GroupName", "") or item.Label


def volume_name(body):
    """MAT_NAME and the volume's mesh group name: a body's Label, an Air Region's typed name."""
    return clean(display_name(body))


def item_name(item, body):
    """An excitation's surface group name on one body."""
    return f"{clean(display_name(item))}_{clean(body.Label)}"


def ref_label(body, sub):
    return f"{display_name(body)}.{sub}" if sub else display_name(body)


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
        add_recombination_algorithm(obj)

    def onDocumentRestored(self, obj):
        add_recombination_algorithm(obj)  # documents saved before the Recombine item existed


def add_recombination_algorithm(folder):
    """Adds the algorithm setting if missing; drops the old global Recombine switch."""
    if not hasattr(folder, "RecombinationAlgorithm"):
        folder.addProperty(
            "App::PropertyEnumeration",
            "RecombinationAlgorithm",
            "Mesh",
            "Gmsh recombination algorithm for bodies in Recombine items",
        )
        folder.RecombinationAlgorithm = list(RECOMBINATION_ALGORITHMS)
    if hasattr(folder, "Recombine"):
        folder.removeProperty("Recombine")


class AirRegionsFolder(Folder):
    LABEL = "Air Regions"


FOLDERS = (
    ("MaterialLibraryGroup", MaterialLibraryFolder),
    ("MaterialsGroup", MaterialsFolder),
    ("ExcitationsGroup", ExcitationsFolder),
    ("MeshSizesGroup", MeshSizesFolder),
    ("AirRegionsGroup", AirRegionsFolder),
)


SIZING_PROPERTIES = (
    "MainMode",
    "MainSource",
    "MainObjects",
    "MovingMode",
    "MovingSource",
    "MovingObjects",
    "Movement",
)  # what decides study_bodies: a change refreshes the Air Regions' SizedBy


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
            add_folder_property(obj, prop)
        obj.addProperty("App::PropertyLink", "MeshResult", "EMSolution", "")
        add_id_memory(obj)
        for prop in ("MatIds", "SmatIds", "NextMatId", "NextSmatId"):
            obj.setEditorMode(prop, 1)  # read-only: edit through the ID table
        obj.setEditorMode("MeshResult", 2)  # hidden
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

    def onChanged(self, obj, prop):
        if (
            prop in SIZING_PROPERTIES
            and not obj.Document.Restoring
            and getattr(obj, "AirRegionsGroup", None) is not None
        ):
            safe_refresh_sized_by(obj)

    def onDocumentRestored(self, obj):
        ensure_folders(obj)  # Studies saved before a folder existed


def add_folder_property(study, prop):
    study.addProperty("App::PropertyLink", prop, "EMSolution", "")
    study.setEditorMode(prop, 2)  # hidden


def ensure_folders(study):
    """Adds the folders the Study lacks, also to Studies saved before they existed."""
    for prop, cls in FOLDERS:
        if not hasattr(study, prop):
            add_folder_property(study, prop)
        if getattr(study, prop) is None:
            _make_folder(study, prop, cls)


def add_id_memory(study):
    """Added on first use, also to Studies saved before IDs were remembered."""
    if not hasattr(study, "IdOwners"):
        study.addProperty("App::PropertyMap", "IdOwners", "IDs", "'table:key' -> 'object IDs:ID', also after removal")
        study.setEditorMode("IdOwners", 2)  # hidden


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


class TransfiniteBody(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty(
            "App::PropertyLinkSubListGlobal", "References", "EMSolution", "Bodies meshed as a structured grid"
        )
        obj.addProperty(
            "App::PropertyLinkSubListGlobal",
            "Corners",
            "EMSolution",
            "Vertices used as corners of faces with more than 4 boundary points",
        )


class TransfiniteEdges(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty(
            "App::PropertyLinkSubListGlobal", "References", "EMSolution", "Edges with a fixed element count"
        )
        obj.addProperty("App::PropertyIntegerConstraint", "Elements", "EMSolution", "Elements on each edge")
        obj.Elements = (10, 1, 100000, 1)
        obj.addProperty("App::PropertyEnumeration", "Distribution", "EMSolution", "Node spacing along the edge")
        obj.Distribution = ["Uniform", "Bump"]
        obj.addProperty(
            "App::PropertyFloat", "BumpCoefficient", "EMSolution", "Gmsh Bump coefficient; below 1 refines both ends"
        )
        obj.BumpCoefficient = 0.5


class Recombine(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty(
            "App::PropertyLinkSubListGlobal",
            "References",
            "EMSolution",
            "Bodies meshed with quads (2D) or quad faces and hexahedra (3D)",
        )


def _unplaced(obj):
    """Reset the Placement of an object its properties place: a moved Placement would detach its Shape from the
    mesh, which is built from the properties."""
    import FreeCAD as App

    if obj.Placement != App.Placement():
        obj.Placement = App.Placement()


SIDES = ("XPlus", "XMinus", "YPlus", "YMinus", "ZPlus", "ZMinus")
PADDING_PROPERTIES = (
    ["SizeMode"]
    + [f"Pad{s}Percent" for s in SIDES]
    + [f"Pad{s}" for s in SIDES]
    + ["PadOuterPercent", "PadInnerPercent", "PadOuter", "PadInner", "InnerFromBodies", "SizedBy"]
)
SIZE_PROPERTIES = ("Center", "Length", "Width", "Height", "InnerRadius", "OuterRadius", "ZMin")


def add_padding(air):
    """Adds the padding properties the Air Region lacks (Manual size, zero padding), also to documents saved before."""
    add = air.addProperty
    if not hasattr(air, "SizeMode"):
        add("App::PropertyEnumeration", "SizeMode", "Padding", "Manual: the size properties; Padding: from the bodies")
        air.SizeMode = ["Manual", "Padding"]
    for side in SIDES:
        axis, sign = side[0], "+" if side.endswith("Plus") else "-"
        if not hasattr(air, f"Pad{side}Percent"):
            add(
                "App::PropertyFloat", f"Pad{side}Percent", "Padding", f"Padding on the {sign}{axis} side, % of the size"
            )
        if not hasattr(air, f"Pad{side}"):
            add("App::PropertyLength", f"Pad{side}", "Padding", f"Padding on the {sign}{axis} side, added to the %")
    for name, text in (("Outer", "outer radius"), ("Inner", "inner radius")):
        if not hasattr(air, f"Pad{name}Percent"):
            add("App::PropertyFloat", f"Pad{name}Percent", "Padding", f"Padding of the {text}, % of the outer radius")
        if not hasattr(air, f"Pad{name}"):
            add("App::PropertyLength", f"Pad{name}", "Padding", f"Padding of the {text}, added to the %")
    if not hasattr(air, "InnerFromBodies"):
        add(
            "App::PropertyBool", "InnerFromBodies", "Padding", "Sector: ring from the bodies' inner radius, else a disc"
        )
    if not hasattr(air, "SizedBy"):
        add("App::PropertyLinkListGlobal", "SizedBy", "Padding", "Bodies that size the air in Padding mode")
        air.setEditorMode("SizedBy", 2)  # hidden
    set_size_modes(air)


def set_size_modes(air):
    """The size properties are read-only in Padding mode: the recompute writes them."""
    mode = 1 if air.SizeMode == "Padding" else 0
    for name in SIZE_PROPERTIES:
        air.setEditorMode(name, mode)


def dependents_of(air):
    """Names of the objects outside the Study that depend on the Air Region (an expression, a Boolean)."""
    try:
        found = air.InListRecursive
    except IndexError:  # a cycle through SizedBy already: look again without the links
        air.SizedBy = []
        found = air.InListRecursive
    return {o.Name for o in found if not is_study_object(o)}


def refresh_sized_by(study):
    """SizedBy of each Air Region: the Study's bodies in Padding mode, none in Manual mode. A body that depends on the
    air would close a cycle (and links make study_bodies see the bodies as made from each other): then none. Only a
    change is written."""
    airs = air_regions(study)
    padding = [a for a in airs if a.SizeMode == "Padding"]
    loops = {a.Name: dependents_of(a) for a in padding}
    for air in padding:
        if loops[air.Name] and air.SizedBy:
            air.SizedBy = []  # study_bodies must not follow the links
    bodies = study_bodies(study) if padding else []
    names = {b.Name for b in bodies}
    for air in airs:
        want = bodies if air in padding and not names & loops[air.Name] else []
        if [o.Name for o in air.SizedBy] != [o.Name for o in want]:
            air.SizedBy = want


def safe_refresh_sized_by(study):
    """refresh_sized_by for a change event: a body not recomputed yet has no shape, and raising there would leave the
    change half made. The failure is a console warning; Validate and Run Mesh refresh again. True if it worked."""
    try:
        refresh_sized_by(study)
    except Exception as exc:
        import FreeCAD as App

        App.Console.PrintWarning(f"EMSolution: Air Region not linked to the bodies yet ({exc}); Validate retries.\n")
        return False
    return True


def _differs(current, value):
    """True if the property value current is not the new size value (a float in mm, or a Vector for Center)."""
    if hasattr(value, "x"):
        return (current - value).Length > 1e-9
    return abs(getattr(current, "Value", current) - value) > 1e-9


class AirRegion(_Named):
    """The outer shape of the air around the model; the mesher fills it. Shape is built from the properties."""

    def __init__(self, obj):
        obj.Proxy = self
        self.add_group_name(obj)
        obj.setEditorMode("Placement", 2)  # hidden: the properties place the air
        add = obj.addProperty
        add("App::PropertyEnumeration", "AirShape", "Air", "Outer shape of the air")
        obj.AirShape = ["Box", "Sector", "Custom"]
        add("App::PropertyVector", "Center", "Air", "Centre of a Box")
        add("App::PropertyLength", "Length", "Air", "Box size along x")
        add("App::PropertyLength", "Width", "Air", "Box size along y (z in a ZX plane study)")
        add("App::PropertyLength", "Height", "Air", "Box size along z; height of a 3D Sector")
        for prop in ("Length", "Width", "Height"):
            setattr(obj, prop, 100.0)
        add("App::PropertyLength", "InnerRadius", "Air", "Inner radius of a Sector")
        add("App::PropertyLength", "OuterRadius", "Air", "Outer radius of a Sector")
        obj.OuterRadius = 100.0
        add("App::PropertyAngle", "StartAngle", "Air", "Sector start angle about the Z axis")
        add("App::PropertyAngle", "EndAngle", "Air", "Sector end angle about the Z axis")
        obj.EndAngle = 360.0
        add("App::PropertyDistance", "ZMin", "Air", "Bottom of a 3D Sector")
        obj.ZMin = -50.0
        add("App::PropertyLinkGlobal", "Source", "Air", "Body that gives a Custom shape")
        add_padding(obj)

    def execute(self, obj):
        from . import airshapes

        study = owner_study(obj)
        plane = airshapes.study_plane(study) if study else "3D"
        _unplaced(obj)
        if obj.SizeMode == "Padding":
            for name, value in airshapes.padded_size(obj, list(obj.SizedBy), plane).items():
                if _differs(getattr(obj, name), value):
                    setattr(obj, name, value)
        obj.Shape = airshapes.air_shape(obj, plane)

    def onChanged(self, obj, prop):
        super().onChanged(obj, prop)
        if prop == "SizeMode" and not obj.Document.Restoring:
            set_size_modes(obj)
            study = owner_study(obj)
            if study is not None:
                safe_refresh_sized_by(study)

    def onDocumentRestored(self, obj):
        obj.setEditorMode("Placement", 2)
        add_padding(obj)  # documents saved before the padding existed


AXES = ["X", "Y", "Z"]


class SlidingInterface(_Named):
    """The surface between the fixed and the moving air; it spans its Air Region. Shape is the slide surface."""

    def __init__(self, obj):
        obj.Proxy = self
        self.add_group_name(obj)
        obj.setEditorMode("Placement", 2)  # hidden: the properties place the surface
        add = obj.addProperty
        add("App::PropertyEnumeration", "Kind", "Sliding", "Rotational about the Z axis, Axial gap (3D) or Linear")
        obj.Kind = ["Rotational", "Axial gap", "Linear"]
        add("App::PropertyLink", "AirRegion", "Sliding", "Air Region the surface spans")
        add("App::PropertyLength", "Radius", "Sliding", "Radius of a Rotational interface")
        obj.Radius = 50.0
        add("App::PropertyDistance", "Position", "Sliding", "Normal-axis coordinate of an Axial gap or Linear plane")
        add("App::PropertyEnumeration", "NormalAxis", "Sliding", "Normal of a Linear interface")
        obj.NormalAxis = AXES
        obj.NormalAxis = "Y"
        add("App::PropertyEnumeration", "MotionAxis", "Sliding", "Motion direction of a Linear interface")
        obj.MotionAxis = AXES
        obj.MotionAxis = "X"
        add("App::PropertyIntegerConstraint", "Divisions", "Sliding", "SLIDE_NDIV: divisions along the motion")
        obj.Divisions = (90, 2, 100000, 2)
        add("App::PropertyIntegerConstraint", "CrossDivisions", "Sliding", "Divisions across the motion (3D)")
        obj.CrossDivisions = (10, 1, 100000, 1)

    def execute(self, obj):
        from . import airshapes

        air = air_of(obj)
        if air is None:
            raise ValueError(f"Sliding Interface {display_name(obj)}: it needs an Air Region")
        study = owner_study(obj)
        plane = airshapes.study_plane(study) if study else "3D"
        _unplaced(obj)
        obj.Shape = airshapes.slide_surface(obj, airshapes.air_shape(air, plane), plane)

    def onDocumentRestored(self, obj):
        obj.setEditorMode("Placement", 2)


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


def make_air_region(study, shape="Box", **props):
    """Adds an Air Region: its outer shape and the properties that size it (see AirRegion)."""
    obj = study.Document.addObject("Part::FeaturePython", "AirRegion")
    AirRegion(obj)
    obj.Label = "Air"
    obj.GroupName = "Air"
    obj.AirShape = shape
    for name, value in props.items():
        setattr(obj, name, value)
    study.AirRegionsGroup.addObject(obj)
    for iface in sliding_interfaces(study):  # left without one when the old Air Region was deleted
        if iface.AirRegion is None:
            iface.AirRegion = obj
    safe_refresh_sized_by(study)
    if getattr(obj, "ViewObject", None) is not None:  # GUI running
        from . import taskpanels

        if hasattr(taskpanels, "ViewProviderAir"):
            taskpanels.ViewProviderAir(obj.ViewObject)
    return obj


def make_sliding_interface(study, kind=None, **props):
    """Adds a Sliding Interface of kind on the Study's Air Region (see SlidingInterface). The default kind is
    Linear for a Box Air Region (a Linear interface needs one), else Rotational."""
    airs = air_regions(study)
    if kind is None:
        kind = "Linear" if airs and airs[0].AirShape == "Box" else "Rotational"
    obj = study.Document.addObject("Part::FeaturePython", "SlidingInterface")
    SlidingInterface(obj)
    obj.Label = "Sliding Interface"
    obj.GroupName = "Sliding Interface"
    obj.Kind = kind
    obj.AirRegion = airs[0] if airs else None
    for name, value in props.items():
        setattr(obj, name, value)
    study.AirRegionsGroup.addObject(obj)
    if getattr(obj, "ViewObject", None) is not None:  # GUI running
        from . import taskpanels

        if hasattr(taskpanels, "ViewProviderSlidingInterface"):
            taskpanels.ViewProviderSlidingInterface(obj.ViewObject)
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
    return f"{display_name(m.Body)}: {lib}" if m.Body else m.Label


def assign(study, bodies, lib, potential):
    """Give each body lib and potential, updating its assignment or adding one. Returns them in body order."""
    have = assignment_of(study)
    out = []
    for body in bodies:
        m = have.get(body.Name)
        if m is None:
            m = _add(study, "MaterialsGroup", Material, display_name(body))
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


def make_transfinite_body(study, bodies, corners=()):
    """bodies: list of bodies; corners: list of (body, "VertexN")."""
    obj = _add(study, "MeshSizesGroup", TransfiniteBody, "TransfiniteBody")
    obj.References = [(b, "") for b in bodies]
    obj.Corners = list(corners)
    return obj


def make_transfinite_edges(study, elements, edges, distribution="Uniform", coef=0.5):
    """edges: list of (body, "EdgeN")."""
    obj = _add(study, "MeshSizesGroup", TransfiniteEdges, "TransfiniteEdges")
    obj.Elements, obj.Distribution, obj.BumpCoefficient = elements, distribution, coef
    obj.References = list(edges)
    return obj


def make_recombine(study, bodies):
    obj = _add(study, "MeshSizesGroup", Recombine, "Recombine")
    obj.References = [(b, "") for b in bodies]
    return obj


def materials(study):
    return list(study.MaterialsGroup.Group)


def excitations(study):
    return list(study.ExcitationsGroup.Group)


def mesh_sizes(study):
    return [o for o in study.MeshSizesGroup.Group if isinstance(o.Proxy, MeshSize)]


def transfinite_bodies(study):
    return [o for o in study.MeshSizesGroup.Group if isinstance(o.Proxy, TransfiniteBody)]


def transfinite_edges(study):
    return [o for o in study.MeshSizesGroup.Group if isinstance(o.Proxy, TransfiniteEdges)]


def recombine_items(study):
    return [o for o in study.MeshSizesGroup.Group if isinstance(o.Proxy, Recombine)]


def air_regions(study):
    return [o for o in study.AirRegionsGroup.Group if isinstance(getattr(o, "Proxy", None), AirRegion)]


def sliding_interfaces(study):
    return [o for o in study.AirRegionsGroup.Group if isinstance(getattr(o, "Proxy", None), SlidingInterface)]


def air_of(iface):
    """The Air Region a Sliding Interface spans: its Study's (one per Study), not the link, which a deleted Air
    Region leaves empty."""
    study = owner_study(iface)
    airs = air_regions(study) if study is not None else []
    return airs[0] if airs else iface.AirRegion


def is_air(obj):
    return isinstance(getattr(obj, "Proxy", None), AirRegion)


def air_refusal(item_cls, bodies):
    """Why an item of class item_cls cannot take bodies, because some are Air Regions; "" when it can. The air
    takes Materials and Mesh Sizes: it is not recombined or structured, and an excitation goes on a body."""
    airs = list(dict.fromkeys(display_name(b) for b in bodies if is_air(b)))
    if not airs or item_cls not in (Excitation, TransfiniteBody, TransfiniteEdges, Recombine):
        return ""
    what = "an Excitation" if item_cls is Excitation else "recombined or structured"
    return f"Air Region {', '.join(airs)} cannot be {what}."


def library_materials(study):
    return list(study.MaterialLibraryGroup.Group)


def material_users(lib):
    """Assignments of lib's Study that link to it; none once its Study is gone."""
    study = owner_study(lib)
    return [m for m in materials(study) if m.LibraryMaterial == lib] if study else []


def user_labels(lib):
    """For messages: the body label of each assignment using lib, or the assignment label if the body is gone."""
    return [display_name(m.Body) if m.Body else m.Label for m in material_users(lib)]


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
    proxies = (Material, Excitation, MeshSize, TransfiniteBody, TransfiniteEdges, Recombine)
    return isinstance(getattr(obj, "Proxy", None), proxies)


def item_refs(item):
    """[(body, sub)] of a Material, Excitation, Mesh Size, Recombine or transfinite item; sub "" = the whole body."""
    if isinstance(item.Proxy, Material):
        return [(item.Body, "")] if item.Body else []
    refs = [(b, s) for b, subs in item.References for s in subs]
    if isinstance(item.Proxy, TransfiniteBody):
        refs += [(b, s) for b, subs in item.Corners for s in subs]
    return refs


def material_rows(study):
    """Rows for the Materials panel: (body, refs, [body, material, MAT_ID, POTENTIAL]).

    Every main- and moving-geometry body and Air Region, then bodies outside them that still have an assignment.
    """
    have = assignment_of(study)
    main = assignable(study)
    inside = {b.Name for b in main}
    rows = []
    for b in main + [m.Body for m in have.values() if m.Body.Name not in inside]:
        m = have.get(b.Name)
        lib = m.LibraryMaterial.Label if m and m.LibraryMaterial else NO_MATERIAL
        name = display_name(b) if b.Name in inside else f"{display_name(b)} (not in main geometry)"
        rows.append((b, [(b, "")], [name, lib, _id_text(study, b), str(m.Potential) if m else ""]))
    return rows


def _id_text(study, body):
    """The MAT_ID of a body or Air Region for the Materials panel: "fixed / moving" for a sliding air, "–" if none."""
    keys = [k for k in air_keys(study) if k.partition("#")[0] == body.Name] or [body.Name]
    ids = [study.MatIds.get(k) for k in keys]
    return " / ".join(ids) if all(ids) else "–"


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


def air_region_rows(study):
    """Rows for the Air Regions panel: (air region, refs, [name, shape, MAT_ID])."""
    return [(a, [(a, "")], [display_name(a), a.AirShape, _id_text(study, a)]) for a in air_regions(study)]


def _size_text(item):
    if isinstance(item.Proxy, MeshSize):
        return f"{item.Size.Value:g} mm"
    if isinstance(item.Proxy, TransfiniteBody):
        return "structured"
    if isinstance(item.Proxy, Recombine):
        return "recombine"
    bump = f" {item.BumpCoefficient:g}" if item.Distribution == "Bump" else ""
    return f"{item.Elements} el, {item.Distribution}{bump}"


def mesh_size_rows(study):
    """Rows for the Mesh Sizes panel: (item, refs, [name, size, applies to])."""
    return [
        (s, item_refs(s), [display_name(s), _size_text(s), ", ".join(ref_label(b, sub) for b, sub in item_refs(s))])
        for s in study.MeshSizesGroup.Group
    ]


def bodies_without_material(study):
    """Main-geometry bodies and Air Regions without an assignment."""
    have = assignment_of(study)
    return [b for b in assignable(study) if b.Name not in have]


def _main_bodies(study):
    from . import geometry

    return geometry.region(study, "Main")[0]


def study_bodies(study):
    """The Study's meshed bodies: the main geometry, then the moving geometry when the Study slides."""
    from . import geometry

    bodies = _main_bodies(study)
    if study.Movement == "Sliding motion":
        bodies = bodies + geometry.region(study, "Moving")[0]
    return list({b.Name: b for b in bodies}.values())


def assignable(study):
    """What can get a Material: the main- and moving-geometry bodies, then the Air Regions."""
    return study_bodies(study) + air_regions(study)


NO_MAIN_GEOMETRY = "Choose the Study's main geometry first: a Part, a Group or Manual selection in the Study panel."


def assignment_problem(study, bodies):
    """Why bodies cannot get Materials, Excitations or Mesh Sizes, or "" when they can."""
    if not _main_bodies(study):
        return NO_MAIN_GEOMETRY
    main = {b.Name for b in assignable(study)}
    outside = list(dict.fromkeys(display_name(b) for b in bodies if b.Name not in main))
    if outside:
        return (
            "Not in the Study's main geometry: "
            + ", ".join(outside)
            + ". Add them to it in the Study panel or select other bodies."
        )
    return ""


def air_keys(study):
    """ID table keys of the Air Regions: one each, or a fixed and a moving half when the Study slides."""
    if study.Movement == "Sliding motion":
        return [f"{a.Name}#{half}" for a in air_regions(study) for half in ("fixed", "moving")]
    return [a.Name for a in air_regions(study)]


def volume_keys(study):
    """MAT_ID keys: bodies, Air Regions (or their halves), then the Sliding Interfaces' SLIDE_MAT_IDs when sliding."""
    keys = [b.Name for b in study_bodies(study)] + air_keys(study)
    if study.Movement == "Sliding motion":
        keys += [i.Name for i in sliding_interfaces(study)]
    return keys


def key_name(study, key):
    """The volume name of a volume key: a body's, Air Region's or Sliding Interface's name, with _fixed or _moving
    for an air half."""
    name, _, half = key.partition("#")
    return volume_name(study.Document.getObject(name)) + (f"_{half}" if half else "")


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

    Counters only grow, so a dropped ID is never handed out again. It comes back with its own object:
    a body that returns to the main geometry, or is restored by undo, gets its old ID if it is still free.
    """
    add_id_memory(study)
    vkeys, skeys = volume_keys(study), surface_keys(study)
    vol = {k: v for k, v in study.MatIds.items() if k in vkeys}
    surf = {k: v for k, v in study.SmatIds.items() if k in skeys}
    used = {int(v) for v in list(vol.values()) + list(surf.values())}
    memory = study.IdOwners

    def give(name, table, keys, counter):
        for key in keys:
            if key in table:
                continue
            owner, _, old = memory.get(f"{name}:{key}", "").rpartition(":")
            if owner and owner == _owner(study, key) and int(old) not in used:
                table[key] = old
                used.add(int(old))
                continue
            while counter in used:
                counter += 1
            table[key] = str(counter)
            used.add(counter)
            counter += 1
        return counter

    study.NextMatId = give("MatIds", vol, vkeys, study.NextMatId)
    study.NextSmatId = give("SmatIds", surf, skeys, study.NextSmatId)
    study.MatIds, study.SmatIds = vol, surf
    _remember(study)


def _owner(study, key):
    """The FreeCAD object IDs behind an ID table key. A new object that reuses a deleted one's Name has
    another object ID, so it never inherits the old MAT_ID; undo and reload keep the object ID."""
    found = [study.Document.getObject(n) for n in key.split("#")[0].split("|")]
    return ",".join(str(o.ID) for o in found) if all(found) else ""


def _remember(study):
    """Record who owns each current ID; entries of removed keys stay, so the ID can come back."""
    memory = dict(study.IdOwners)
    for name in ("MatIds", "SmatIds"):
        for key, value in getattr(study, name).items():
            memory[f"{name}:{key}"] = f"{_owner(study, key)}:{value}"
    if memory != study.IdOwners:
        study.IdOwners = memory


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
    add_id_memory(study)
    _remember(study)


def id_rows(study):
    """Rows for the ID table dialog: (table, key, name, id), volumes first."""
    rows = []
    for name in volume_keys(study):
        if name in study.MatIds:
            rows.append(("MatIds", name, key_name(study, name), int(study.MatIds[name])))
    for e in excitations(study):
        for b, _ in subs_by_body(e):
            key = f"{e.Name}|{b.Name}"
            if key in study.SmatIds:
                rows.append(("SmatIds", key, item_name(e, b), int(study.SmatIds[key])))
    return rows
