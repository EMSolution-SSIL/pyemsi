"""Study tree objects and the ID table. No GUI code here, apart from attaching view providers."""

import json
import re

from . import symmetry

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
    """An assignment: one body (assign()) or faces of a symmetric drawing (assign_pieces()), its Material Library
    entry and its potential region."""

    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkGlobal", "Body", "EMSolution", "Body made of this material")
        self.add_group_name(obj)
        self.add_pieces(obj)
        obj.addProperty("App::PropertyLink", "LibraryMaterial", "EMSolution", "Material from the Material Library")
        obj.addProperty("App::PropertyIntegerConstraint", "Potential", "EMSolution", "POTENTIAL: 0 total, 1+ reduced")
        obj.Potential = (0, 0, 1000000, 1)

    @staticmethod
    def add_group_name(obj):
        """The typed name, used in the mesh group names; the Label is "<name>: <material>" (see assignment_label)."""
        obj.addProperty("App::PropertyString", "GroupName", "EMSolution", "Name used in the mesh group names")

    @staticmethod
    def add_pieces(obj):
        if not hasattr(obj, "Pieces"):
            obj.addProperty("App::PropertyLinkSubListGlobal", "Pieces", "EMSolution", "Faces made of this material")
        if not hasattr(obj, "PieceCentres"):
            obj.addProperty(
                "App::PropertyVectorList", "PieceCentres", "EMSolution", "Where each piece was when assigned (mm)"
            )
            obj.setEditorMode("PieceCentres", 2)

    def onDocumentRestored(self, obj):
        self.add_pieces(obj)  # assignments saved before pieces existed
        if not hasattr(obj, "GroupName"):  # saved before Materials were named: keep the mesh name they had
            name = display_name(obj.Body) if obj.Body is not None else obj.Label
            self.add_group_name(obj)
            obj.GroupName = name
            obj.Label = assignment_label(obj)
        obj.purgeTouched()


class SymmetricMesh(_Proxy):
    """Mesh the cell, copy the mesh: Top is the object that builds the full drawing (Boolean Fragments, Compound,
    Polar Array or Mirror). Cells and Steps show what the chain was read as."""

    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkGlobal", "Top", "EMSolution", "Top object of the Mirror / Polar Array chain")
        obj.addProperty("App::PropertyLinkListGlobal", "Cells", "EMSolution", "Cell bodies: the only ones meshed")
        obj.addProperty("App::PropertyStringList", "Steps", "EMSolution", "Copy steps, in the order they are applied")
        obj.setEditorMode("Cells", 1)
        obj.setEditorMode("Steps", 1)

    def execute(self, obj):
        cells, steps = [], []
        if obj.Top is not None:
            try:
                cells, _ = symmetry.read_chain(obj.Top)
                steps = symmetry.steps(obj.Top)
            except symmetry.SymmetryError:
                cells, steps = [], []
        obj.Cells, obj.Steps = cells, steps


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
    + ["PadOuterPercent", "PadInnerPercent", "PadOuter", "PadInner", "InnerFromBodies", "SizedBy", "SizedByContainers"]
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
    if not hasattr(air, "SizedByContainers"):
        add("App::PropertyLinkListGlobal", "SizedByContainers", "Padding", "Parts that place the bodies in SizedBy")
        air.setEditorMode("SizedByContainers", 2)  # hidden
    set_size_modes(air)


def set_size_modes(air):
    """The size properties are read-only in Padding mode: the recompute writes them."""
    mode = 1 if air.SizeMode == "Padding" else 0
    for name in SIZE_PROPERTIES:
        air.setEditorMode(name, mode)


def dependents_of(air):
    """Names of the objects outside the Study that depend on the Air Region (an expression, a Boolean)."""
    try:
        air.OutListRecursive  # raises on a cycle through the links, e.g. a reader moved into a linked container
        found = air.InListRecursive
    except IndexError:  # a cycle through the links already: look again without them
        air.SizedBy, air.SizedByContainers = [], []
        found = air.InListRecursive
    return {o.Name for o in found if not is_study_object(o)}


def readers_in_sources(air, study):
    """The objects inside the Study's container sources that read the Air Region (an expression, a Boolean): such a
    container cannot be a source, and the air cannot follow its bodies. Only the objects that read it themselves, not
    the groups that hold them."""
    regions = ["Main", "Moving"] if study.Movement == "Sliding motion" else ["Main"]
    sources = [getattr(study, n + "Source") for n in regions if getattr(study, n + "Mode") == "Container"]
    loops = dependents_of(air)
    found = {}
    for source in sources:
        if source is None or source.Document != study.Document:
            continue
        for o in source.OutListRecursive:
            if o.Name in loops and not is_study_object(o) and not any(p.Name in loops for p in o.OutList):
                found.setdefault(o.Name, o)
    return list(found.values())


def containers_of(bodies):
    """The containers that place the bodies (App::Part, PartDesign Body: GeoFeatureGroups), innermost first. Moving
    one moves its bodies without changing them."""
    found = {}
    for body in bodies:
        parent = body.getParentGeoFeatureGroup()
        while parent is not None:
            found.setdefault(parent.Name, parent)
            parent = parent.getParentGeoFeatureGroup()
    return list(found.values())


def refresh_sized_by(study):
    """SizedBy of each Air Region: the Study's bodies in Padding mode, none in Manual mode; SizedByContainers: the
    containers that place them, so that moving one recomputes the air. A body that depends on the air would close a
    cycle (and links make study_bodies see the bodies as made from each other): then no body; a container that
    depends on the air is left out. Only a change is written."""
    airs = air_regions(study)
    padding = [a for a in airs if a.SizeMode == "Padding"]
    loops = {a.Name: dependents_of(a) for a in padding}
    try:
        bodies = study_bodies(study) if padding else []
    except IndexError:  # a cycle through the links: the bodies are the Study's own, look again without them
        for air in padding:
            air.SizedBy, air.SizedByContainers = [], []
        bodies = study_bodies(study)
    tangled = [a for a in padding if loops[a.Name] & {b.Name for b in bodies} and (a.SizedBy or a.SizedByContainers)]
    if tangled:  # study_bodies must not follow the links: look again without them
        for air in tangled:
            air.SizedBy, air.SizedByContainers = [], []
        bodies = study_bodies(study)
    names = {b.Name for b in bodies}
    for air in airs:
        want = bodies if air in padding and not names & loops[air.Name] else []
        if [o.Name for o in air.SizedBy] != [o.Name for o in want]:
            air.SizedBy = want
        places = [c for c in containers_of(want) if c.Name not in loops.get(air.Name, ())]
        if [o.Name for o in air.SizedByContainers] != [o.Name for o in places]:
            air.SizedByContainers = places


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


def dependent_body(air, study):
    """The first of the Study's bodies that depends on the Air Region (so it cannot size it), or None."""
    loops = dependents_of(air)
    return next((b for b in study_bodies(study) if b.Name in loops), None)


def drop_size_formulas(air):
    """Padding writes some of the size properties: a formula on one of them would fight the recompute. Removes those
    formulas, with a console message; a formula on a size Padding leaves manual (Sector angles) stays."""
    import FreeCAD as App
    from . import airshapes

    study = owner_study(air)
    plane = airshapes.study_plane(study) if study is not None else "3D"
    written = airshapes.padded_properties(air.AirShape, plane)
    dropped = [path for path, _ in air.ExpressionEngine if path.lstrip(".").split(".")[0] in written]
    for path in dropped:
        air.setExpression(path, None)
    if dropped:
        names = ", ".join(dict.fromkeys(path.lstrip(".") for path in dropped))
        App.Console.PrintMessage(
            f"EMSolution: Air Region {display_name(air)}: Padding computes {names}; their formulas were removed.\n"
        )


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
            if not obj.SizedBy and study is not None:  # say why rather than "needs bodies"
                body = dependent_body(obj, study)
                if body is not None:
                    raise ValueError(
                        f"Air Region {display_name(obj)}: body {display_name(body)} depends on the Air Region;"
                        " it cannot size it."
                    )
            for name, value in airshapes.padded_size(obj, list(obj.SizedBy), plane).items():
                if _differs(getattr(obj, name), value):
                    setattr(obj, name, value)
        obj.Shape = airshapes.air_shape(obj, plane)

    def onChanged(self, obj, prop):
        super().onChanged(obj, prop)
        if obj.Document.Restoring or not hasattr(obj, "SizeMode"):
            return
        if prop in ("SizeMode", "AirShape") and obj.SizeMode == "Padding":
            drop_size_formulas(obj)
        if prop == "SizeMode":
            set_size_modes(obj)
            study = owner_study(obj)
            if study is not None:
                safe_refresh_sized_by(study)

    def onDocumentRestored(self, obj):
        obj.setEditorMode("Placement", 2)
        touched = "Touched" in obj.State
        add_padding(obj)  # documents saved before the padding existed
        if not touched:
            obj.purgeTouched()  # properties an old document lacked are no edit


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
        study = owner_study(obj)
        if air is None and study is not None and is_symmetric(study):
            if obj.Kind != "Rotational":
                raise ValueError(f"Sliding Interface {display_name(obj)}: a symmetric Study slides Rotational only")
            import Part

            _unplaced(obj)
            obj.Shape = Part.makeCompound([Part.makeCircle(obj.Radius.Value)])  # the full circle, no Air Region
            return
        if air is None:
            raise ValueError(f"Sliding Interface {display_name(obj)}: it needs an Air Region")
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

        taskpanels.attach_view_provider(folder)
    return folder


def make_study(doc, dimension="3D", label=None, movement="No movement"):
    if dimension not in ("2D", "3D"):
        raise ValueError("Study dimension must be 2D or 3D")
    if movement not in ("No movement", "Sliding motion"):
        raise ValueError("Study movement must be No movement or Sliding motion")
    study = doc.addObject("App::DocumentObjectGroupPython", "Study")
    Study(study)
    study.Dimension = dimension
    study.Movement = movement
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

        taskpanels.attach_view_provider(obj)
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

        taskpanels.attach_view_provider(obj)
    return obj


def make_library_material(study, record_json):
    """record_json: canonical ems_material JSON. The Label is the material's name."""
    name = json.loads(record_json)["identity"]["name"]
    obj = _add(study, "MaterialLibraryGroup", LibraryMaterial, name)
    obj.Record = record_json
    if getattr(obj, "ViewObject", None) is not None:  # GUI running
        from . import taskpanels

        taskpanels.attach_view_provider(obj)
    return obj


def assignment_of(study):
    """{body Name: assignment} for the Study's assignments whose body still exists."""
    return {m.Body.Name: m for m in materials(study) if m.Body is not None}


def assignment_label(m):
    """The tree label "<name>: <material>"; FreeCAD keeps labels unique, so it cannot be the body's label."""
    lib = m.LibraryMaterial.Label if m.LibraryMaterial else NO_MATERIAL
    return f"{display_name(m)}: {lib}"


def set_material_name(m, name):
    m.GroupName = name
    m.Label = assignment_label(m)


def name_taken(study, name, own=None, ignore=()):
    """Whether another Material of the Study already has this name, compared as mesh group names ("Coil 1" is
    "Coil_1"); ignore: Materials about to be removed."""
    return any(clean(m.GroupName) == clean(name) for m in materials(study) if m != own and m not in ignore)


def suggest_name(study, refs, lib, own=None, ignore=()):
    """A free name for a Material on refs [(body, sub)]: a whole body's name, else the library material's (faces
    have no name of their own), else the drawing's; "_2", "_3"... when taken. "" for no refs."""
    if not refs:
        return ""
    body, sub = refs[0]
    base = display_name(body) if not sub or lib is None else lib.Label
    name, n = base, 1
    while name_taken(study, name, own, ignore):
        n += 1
        name = f"{base}_{n}"
    return name


def assign(study, bodies, lib, potential, name=None):
    """Give each body a Material with lib and potential, named name (default: suggested). A body's old Material is
    replaced (reused under the new name); an Air Region's keeps its name, which follows the Air Region's.
    Returns them in body order."""
    have = assignment_of(study)
    out = []
    for body in bodies:
        m = have.get(body.Name)
        if m is None:
            m = _add(study, "MaterialsGroup", Material, name or suggest_name(study, [(body, "")], lib))
            m.Body = body
            if getattr(m, "ViewObject", None) is not None:  # GUI running
                from . import taskpanels

                taskpanels.attach_view_provider(m)
            have[body.Name] = m
        elif not isinstance(getattr(body, "Proxy", None), AirRegion):
            m.GroupName = name or suggest_name(study, [(body, "")], lib, own=m)
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
    """Rewrite assignment labels after a library material was renamed."""
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


def make_symmetric_mesh(study, top):
    """Adds a Symmetric Mesh item reading the chain below top."""
    obj = _add(study, "MeshSizesGroup", SymmetricMesh, "Symmetric Mesh")
    obj.Top = top
    obj.recompute()
    return obj


def assign_pieces(study, name, pieces, lib, potential):
    """Add an assignment named name for pieces [(body, "FaceN")], which need not be whole bodies."""
    m = _add(study, "MaterialsGroup", Material, name)
    m.Pieces = list(pieces)
    m.PieceCentres = piece_centres(m)
    m.LibraryMaterial, m.Potential = lib, potential
    set_material_name(m, name)
    if getattr(m, "ViewObject", None) is not None:  # GUI running
        from . import taskpanels

        taskpanels.attach_view_provider(m)
    return m


def make_material(study):
    """An empty Material for the Material panel to fill; the panel holds the transaction that removes it on Cancel."""
    m = _add(study, "MaterialsGroup", Material, "")
    m.Label = assignment_label(m)
    if getattr(m, "ViewObject", None) is not None:  # GUI running
        from . import taskpanels

        taskpanels.attach_view_provider(m)
    return m


def air_material(study, air):
    return assignment_of(study).get(air.Name)


def rename_air_region(study, air, name):
    """Rename an Air Region and its Material, which is named after it."""
    air.Label = name
    air.GroupName = name  # FreeCAD may have suffixed the Label
    m = air_material(study, air)
    if m is not None:
        set_material_name(m, name)


def _key(ref):
    return (ref[0].Name, ref[1])


def material_owners(study, refs, own=None):
    """[(ref, the other Material holding it)] for refs [(body, sub)], in ref order; refs nobody holds are left out."""
    held = {_key(r): m for m in materials(study) if m != own for r in item_refs(m)}
    return [(r, held[_key(r)]) for r in refs if _key(r) in held]


def emptied_by(study, refs, own=None):
    """The other Materials that would have nothing left once refs leave them."""
    taking = {_key(r) for r in refs}
    owners = dict.fromkeys(m for _, m in material_owners(study, refs, own))
    return [m for m in owners if all(_key(r) in taking for r in item_refs(m))]


def _set_pieces(m, refs, centres):
    """Pieces = refs [(body, "FaceN")]; centres: (body Name, sub) -> stored centre, the others are measured now."""
    m.Pieces = list(refs)
    now = piece_centres(m)
    m.PieceCentres = [centres.get(_key(r), c) for r, c in zip(item_refs(m), now)]


def apply_material(study, m, name, lib, potential, refs, kept=frozenset()):
    """Make m cover refs (a whole body [(body, "")] or faces [(body, "FaceN")]), taking them from other Materials,
    which are removed when left empty. Faces in kept, (body Name, sub), keep the centre m stored for them; the others
    are measured now. No transaction: the caller holds it."""
    whole = [r for r in refs if r[1] == ""]
    if whole and (len(whole) > 1 or len(refs) > 1):
        raise ValueError("a Material covers one whole body or faces, not both")
    taking = {_key(r) for r in refs}
    for other in emptied_by(study, refs, own=m):
        study.Document.removeObject(other.Name)
    for other in dict.fromkeys(o for _, o in material_owners(study, refs, own=m)):
        left = [r for r in item_refs(other) if _key(r) not in taking]  # only piece Materials get here
        stored = dict(zip(map(_key, item_refs(other)), other.PieceCentres))
        _set_pieces(other, left, stored)
    if whole:
        m.Body = refs[0][0]
    else:
        stored = dict(zip(map(_key, item_refs(m)), getattr(m, "PieceCentres", [])))
        m.Body = None  # a whole-body Material left from before the drawing was symmetric
        _set_pieces(m, refs, {k: v for k, v in stored.items() if k in kept})
    m.LibraryMaterial, m.Potential = lib, potential
    set_material_name(m, name)


def piece_centres(m):
    """Global centre of mass of each piece of the assignment m, in the order of its flattened Pieces."""
    from . import geometry

    return [geometry.global_shape(b).getElement(s).CenterOfMass for b, subs in m.Pieces for s in subs]


def make_transfinite_body(study, bodies, corners=()):
    """bodies: list of bodies; corners: list of (body, "VertexN")."""
    obj = _add(study, "MeshSizesGroup", TransfiniteBody, "TransfiniteBody")
    obj.References = [(b, "") for b in bodies]
    obj.Corners = list(corners)
    return obj


def split_corners(picks):
    """(References, Corners) of a Transfinite Body from picks [(body, sub)]: the VertexN picks are its corners."""
    corners = [(b, s) for b, s in picks if s.startswith("Vertex")]
    return [(b, s) for b, s in picks if not s.startswith("Vertex")], corners


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


def symmetric_items(study):
    return [o for o in study.MeshSizesGroup.Group if isinstance(o.Proxy, SymmetricMesh)]


def is_symmetric(study):
    return bool(symmetric_items(study))


def cell_bodies(study):
    """The leaves (cell bodies) of every Symmetric Mesh item whose chain reads, once each."""
    found = {}
    for item in symmetric_items(study):
        try:
            cells, _ = symmetry.read_chain(item.Top) if item.Top is not None else ([], [])
        except symmetry.SymmetryError:
            continue
        for body in cells:
            found.setdefault(body.Name, body)
    return list(found.values())


def to_cells(study, refs, whole=False):
    """Mesh setting picks [(body, sub)] with those on the top of a Symmetric Mesh item moved to the cell: a face,
    edge or vertex of any copy becomes the cell bodies' own ones that the copy came from (whole: the cell bodies).
    An edge two cell bodies share is the edge of both, so it gives one pick on each: a structured body counts it.
    Picks on other bodies, a whole top, or a sub-element no copy comes from stay as they are; validation explains
    those."""
    from . import geometry

    chains = {}
    for item in symmetric_items(study):
        try:
            if item.Top is not None:
                cells, transforms = symmetry.read_chain(item.Top)
                chains[item.Top.Name] = ([(c, geometry.global_shape(c)) for c in cells], transforms)
        except symmetry.SymmetryError:
            continue
    out = []
    for body, sub in refs:
        found = _cell_of(chains[body.Name], geometry.global_shape(body), sub) if sub and body.Name in chains else []
        out += [(c, "") if whole else (c, s) for c, s in found] or [(body, sub)]
    return list(dict.fromkeys(out))


def _cell_of(chain, shape, sub):
    """[(cell body, sub-element name)] that a copy step puts onto sub of shape, the top: every cell body that has
    that element, for the first copy that has one; [] if none does."""
    import FreeCAD as App

    cells, transforms = chain
    kind = sub.rstrip("0123456789")
    picked = shape.getElement(sub)
    tol = 1e-6 * shape.BoundBox.DiagonalLength
    for m in transforms:  # the identity first: a pick in the cell's own place
        back = picked.transformed(App.Matrix(*m).inverse())
        found = [
            (cell, f"{kind}{k + 1}")
            for cell, cell_shape in cells
            for k, item in enumerate(getattr(cell_shape, {"Face": "Faces", "Edge": "Edges"}.get(kind, "Vertexes")))
            if _coincide(item, back, tol)
        ]
        if found:
            return found
    return []


def _coincide(a, b, tol):
    if hasattr(a, "Point") and hasattr(b, "Point"):  # vertices
        return (a.Point - b.Point).Length < tol
    return (a.CenterOfMass - b.CenterOfMass).Length < tol and abs(a.Mass - b.Mass) < tol * max(1.0, a.Mass)


def piece_assignments(study):
    """The assignments made of pieces: they have no Body."""
    return [m for m in materials(study) if m.Body is None and len(getattr(m, "Pieces", [])) > 0]


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


def face_picks(item):
    """[(body, [FaceN])] in reference order, one entry per body. An empty list means the whole body: a whole-body
    reference wins over face references to the same body. Other sub-elements are ignored."""
    out = []
    for body, subs in subs_by_body(item):
        if "" in subs:
            out.append((body, []))
            continue
        faces = sorted({s for s in subs if s.startswith("Face")}, key=lambda s: int(s[4:]))
        if faces:
            out.append((body, faces))
    return out


def structured_faces(body, faces):
    """The faces of a face pick: the picked ones, or every face of the body for a whole-body pick."""
    return list(faces) or [f"Face{i}" for i in range(1, len(body.Shape.Faces) + 1)]


def is_item(obj):
    proxies = (Material, Excitation, MeshSize, TransfiniteBody, TransfiniteEdges, Recombine, SymmetricMesh)
    return isinstance(getattr(obj, "Proxy", None), proxies)


def item_refs(item):
    """[(body, sub)] of a Material, Excitation, Mesh Size, Recombine or transfinite item; sub "" = the whole body."""
    if isinstance(item.Proxy, Material):
        if item.Body is None:
            return [(b, s) for b, subs in item.Pieces for s in subs]
        return [(item.Body, "")]
    if isinstance(item.Proxy, SymmetricMesh):
        return [(b, "") for b in item.Cells]
    refs = [(b, s) for b, subs in item.References for s in subs]
    if isinstance(item.Proxy, TransfiniteBody):
        refs += [(b, s) for b, subs in item.Corners for s in subs]
    return refs


def material_rows(study):
    """Rows for the Materials panel: (body, refs, [body, material, MAT_ID, POTENTIAL]).

    Every main- and moving-geometry body and Air Region, then bodies outside them that still have an assignment.
    A symmetric Study lists its piece assignments instead: (assignment, its pieces, [name, ...]).
    """
    if is_symmetric(study):
        rows = []
        for m in piece_assignments(study):
            lib = m.LibraryMaterial.Label if m.LibraryMaterial else NO_MATERIAL
            rows.append((m, item_refs(m), [display_name(m), lib, study.MatIds.get(m.Name, "–"), str(m.Potential)]))
        return rows
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
    if isinstance(item.Proxy, SymmetricMesh):
        return "symmetric"
    bump = f" {item.BumpCoefficient:g}" if item.Distribution == "Bump" else ""
    return f"{item.Elements} el, {item.Distribution}{bump}"


def mesh_size_rows(study):
    """Rows for the Mesh Sizes panel: (item, refs, [name, size, applies to])."""
    return [
        (s, item_refs(s), [display_name(s), _size_text(s), ", ".join(ref_label(b, sub) for b, sub in item_refs(s))])
        for s in study.MeshSizesGroup.Group
    ]


def bodies_without_material(study):
    """Main-geometry bodies and Air Regions without an assignment; not the tops of Symmetric Mesh items, whose
    Materials are on their pieces."""
    have = assignment_of(study)
    tops = {i.Top.Name for i in symmetric_items(study) if i.Top is not None}
    return [b for b in assignable(study) if b.Name not in have and b.Name not in tops]


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


NO_MAIN_GEOMETRY = "Choose the Study's main geometry first: tick it in the Study panel's geometry tree."


def assignment_problem(study, bodies):
    """Why bodies cannot get Materials, Excitations or Mesh Sizes, or "" when they can."""
    if not _main_bodies(study):
        return NO_MAIN_GEOMETRY
    main = {b.Name for b in assignable(study) + cell_bodies(study)}
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
    """MAT_ID keys: bodies, Air Regions (or their halves), then the Sliding Interfaces' SLIDE_MAT_IDs when sliding.
    A symmetric Study has the piece assignments instead of the bodies and Air Regions."""
    if is_symmetric(study):
        keys = [m.Name for m in piece_assignments(study)]  # one MAT_ID per assignment; no bodies, no Air Region
    else:
        keys = [b.Name for b in study_bodies(study)] + air_keys(study)
    if study.Movement == "Sliding motion":
        keys += [i.Name for i in sliding_interfaces(study)]
    return keys


def key_name(study, key):
    """The volume name of a volume key: a body's, Air Region's or Sliding Interface's name, with _fixed or _moving
    for an air half."""
    name, _, half = key.partition("#")
    return region_name(study, study.Document.getObject(name)) + (f"_{half}" if half else "")


def region_name(study, body):
    """MAT_NAME and the mesh group name of a body: its Material's name, or its own when it has none. An Air Region
    (or a Sliding Interface) keeps its own name; its Material is named after it."""
    m = assignment_of(study).get(body.Name) if not isinstance(getattr(body, "Proxy", None), AirRegion) else None
    return volume_name(m if m is not None else body)


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
