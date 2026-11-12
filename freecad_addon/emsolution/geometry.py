"""Geometry sources and setup validation. No GUI or mesh generation here."""

import FreeCAD as App
import Part

from . import objects


def link_target(obj):
    """The body an App::Link names, or None: not a link, a link array, or a link to anything but one body (a
    Part::Feature or a PartDesign Body; not a link, a sketch, a Study object or a container)."""
    if obj.TypeId != "App::Link" or obj.ElementCount:
        return None
    named = obj.LinkedObject
    subs = named[1] if isinstance(named, tuple) and len(named) > 1 else ""
    if any(sub.rsplit(".", 1)[-1] for sub in ([subs] if isinstance(subs, str) else subs)):
        return None  # names an edge, face or vertex
    target = obj.getLinkedObject(True)
    if target is None or target == obj or target.TypeId == "App::Link" or objects.is_study_object(target):
        return None
    if not target.isDerivedFrom("Part::Feature") or target.isDerivedFrom("Sketcher::SketchObject"):
        return None
    return target


def body_shape(obj):
    """What obj.Shape is for a Part::Feature; for a link body the linked shape in the link's own coordinates
    (its placement applied, those of the Parts around it not)."""
    return Part.getShape(obj) if link_target(obj) is not None else obj.Shape


def global_shape(obj):
    """Shape where the user sees it, including the placements of containing Parts. A link shows its target's
    shape as FreeCAD displays it (the link's own placement and those of the Parts around it)."""
    target = link_target(obj)
    if target is not None:
        path, parent = [obj.Name], obj.getParentGeoFeatureGroup()
        while parent is not None:
            path.insert(0, parent.Name)
            parent = parent.getParentGeoFeatureGroup()
        top = obj.Document.getObject(path[0])
        # FreeCAD's own display: the link's placement replaces the target's, or composes with it (LinkTransform)
        return Part.getShape(top, ".".join(path[1:]) + ".", transform=True) if len(path) > 1 else Part.getShape(obj)
    shape = obj.getPropertyOfGeometry().transformed(App.Placement().Matrix)
    shape.Placement = obj.getGlobalPlacement()
    return shape


def is_container(obj):
    return not objects.is_study_object(obj) and (
        obj.isDerivedFrom("App::Part") or obj.isDerivedFrom("App::DocumentObjectGroup")
    )


def is_source(obj):
    """A source cannot contain Study objects: linking it would create a dependency cycle."""
    return is_container(obj) and not any(objects.is_study_object(o) for o in obj.OutListRecursive)


PLANE_TOL = 1e-6


def plane_of(face):
    """ "XY" for a face in the plane z = 0, "ZX" for a face in the plane y = 0, else None."""
    box = face.BoundBox
    if max(abs(box.ZMin), abs(box.ZMax)) < PLANE_TOL:
        return "XY"
    if max(abs(box.YMin), abs(box.YMax)) < PLANE_TOL:
        return "ZX"
    return None


# The input whose volume the result leaves out, by TypeId or, for a Python feature, by its Proxy class: a Cut's tool,
# a mirror image's source and a Draft Clone's original (a copy placed elsewhere), a Part Join Cutout's tool.
OUTSIDE = {"Part::Cut": "Tool", "Part::Mirroring": "Source", "Clone": "Objects", "FeatureCutout": "Tool"}
COPIES = ("Part::Mirroring", "Clone")  # the kinds of OUTSIDE whose input is copied, not cut away


def _kind(obj):
    proxy = getattr(obj, "Proxy", None)
    return type(proxy).__name__ if proxy is not None else obj.TypeId


def _linked(item):
    """The objects a link value names as a whole: an object, or (object, subnames) where a subname ending in "."
    names an object inside it (a Link into a Part: "AirBox.") and one ending in an element ("Edge3") is a reference."""
    if not isinstance(item, tuple):
        return [item]
    obj, subs = item[0], item[1] if len(item) > 1 else ()
    subs = [subs] if isinstance(subs, str) else list(subs)
    if not any(subs):
        return [obj]
    return [obj.getSubObject(s, retType=1) for s in subs if s and not s.rsplit(".", 1)[-1]]


def _made_from(obj, outside=False):
    """The objects whose volume obj holds: those it links as a whole. A link to an edge, face or vertex (a ruled
    surface's curves), an expression, a hidden back-link (a PartDesign feature's Body) and the input in OUTSIDE
    only shape or place obj (outside=True follows that one too; a collection of kinds follows it for those kinds)."""
    kind = _kind(obj)
    follow = outside is True or (bool(outside) and kind in outside)
    out, skip, found = obj.OutList, None if follow else OUTSIDE.get(kind), []
    for prop in obj.PropertiesList:
        kind = obj.getTypeIdOfProperty(prop)
        if prop == skip or not (kind.startswith("App::PropertyLink") or kind.startswith("App::PropertyXLink")):
            continue
        value = obj.getPropertyByName(prop)
        for item in value if isinstance(value, list) else [value]:
            if not (isinstance(item, tuple) and item[0] in out) and item not in out:
                continue
            found += [o for o in _linked(item) if isinstance(o, App.DocumentObject)]
    return found


def inputs(obj, outside=False):
    """Names of the objects obj is made from, in its document: the walk follows _made_from and does not go through a
    sketch, whose links (external geometry, attachment) only align it, nor through a Study object (the bodies an Air
    Region's SizedBy links only size it). The tool of a Cut, which the Cut leaves out, and a body a sketch or a ruled
    surface only traces are not inputs, unless outside=True (or names the kind of the object that has them, as
    COPIES does)."""
    found, stack = set(), [obj]
    while stack:
        for dep in _made_from(stack.pop(), outside):
            if dep.Name in found or dep.Document != obj.Document:
                continue
            found.add(dep.Name)
            if not dep.isDerivedFrom("Sketcher::SketchObject") and not objects.is_study_object(dep):
                stack.append(dep)
    return found


def _is_link(obj):
    return obj.TypeId == "App::Link"


def _consumed(bodies):
    """Names of the objects the bodies are made from; a link body does not consume its target."""
    return {name for obj in bodies if not _is_link(obj) for name in inputs(obj)}


def _cut_pairs(doc):
    """[(cut, tool)] for every Part Cut and Join Cutout of doc that has a tool."""
    return [
        (o, o.Tool)
        for o in doc.Objects
        if (o.TypeId == "Part::Cut" or _kind(o) == "FeatureCutout") and getattr(o, "Tool", None) is not None
    ]


def cut_tools(doc):
    """{body Name: the Cut or Join Cutout it is the Tool of}. A Part or Group tool gives every body in it, of either
    dimension; a link tool gives none (the link is not a body, its target stays one)."""
    found = {}
    for cut, tool in _cut_pairs(doc):
        if _is_link(tool):
            continue
        bodies, _ = _bodies([tool])
        consumed = _consumed(bodies)
        for obj in bodies:
            if obj.Name not in consumed:
                found.setdefault(obj.Name, cut)
    return found


def _left_out(doc):
    """Names no Study meshes: the tools of Cuts and Join Cutouts, and a link used as one."""
    return set(cut_tools(doc)) | {tool.Name for _, tool in _cut_pairs(doc) if _is_link(tool)}


def collect(roots, dimension):
    """Return final geometry objects and diagnostics, in source order.

    Bodies are atomic. A Part result consumes its inputs, so a Fuse and its operands do not become three
    overlapping regions; the tool of a Cut or Join Cutout is never a body (a Link to it is). A link to one body is a
    body and does not consume its target. Visibility is irrelevant.
    """
    candidates, errors = _bodies(roots)
    consumed = _consumed(candidates)  # a cut tool still consumes what it is made of
    if candidates:
        left_out = _left_out(candidates[0].Document)
        candidates = [obj for obj in candidates if obj.Name not in left_out]
    return _checked(candidates, consumed, errors, dimension)


def _bodies(roots):
    """(candidates, errors): the body objects under roots, containers resolved, before cut tools are dropped and
    before any check of the shape. A link is a body when it links one."""
    candidates, errors, visited = [], [], set()

    def visit(obj):
        key = (obj.Document.Name, obj.Name)
        if key in visited:
            return
        visited.add(key)
        if objects.is_study_object(obj) or obj.isDerivedFrom("Fem::FemMeshObject"):
            errors.append(f"{obj.Label}: study objects and mesh results are not geometry.")
        elif is_container(obj):
            for child in obj.Group:
                visit(child)
        elif obj.isDerivedFrom("App::Origin") or obj.isDerivedFrom("App::OriginFeature"):
            return
        elif obj.isDerivedFrom("Sketcher::SketchObject"):
            return  # sketches are construction inputs; this phase does not fill wires
        elif obj.isDerivedFrom("Part::Feature") and not obj.isDerivedFrom("App::Link"):
            candidates.append(obj)
        elif link_target(obj) is not None:
            candidates.append(obj)
        else:
            errors.append(f"{obj.Label}: unsupported geometry object ({obj.TypeId}).")

    for obj in roots:
        visit(obj)
    return candidates, errors


def _checked(candidates, consumed, errors, dimension):
    """(bodies, errors): candidates nothing consumes that are right for dimension."""
    result, plane = [], None
    for obj in candidates:
        if obj.Name in consumed:
            continue
        shape = global_shape(obj)
        if dimension == "3D":
            if not shape.Solids:
                errors.append(f"{obj.Label}: 3D geometry must contain at least one solid.")
                continue
        else:
            if shape.Solids or not shape.Faces:
                errors.append(f"{obj.Label}: 2D geometry must contain filled planar faces without solids.")
                continue
            valid = True
            for face in shape.Faces:
                if not face.Surface.isPlanar():
                    errors.append(f"{obj.Label}: 2D faces must be planar.")
                    valid = False
                    break
                found = plane_of(face)
                if found is None:
                    errors.append(f"{obj.Label}: 2D faces must lie in the XY plane (z = 0) or the ZX plane (y = 0).")
                    valid = False
                    break
                if plane is None:
                    plane = found
                elif found != plane:
                    errors.append(f"{obj.Label}: 2D faces must share one plane.")
                    valid = False
                    break
            if not valid:
                continue
        result.append(obj)
    return result, errors


def tree(doc, dimension):
    """[(obj, children)] for the Study geometry tree: Parts and Groups as in FreeCAD's tree (children a list) and
    the bodies collect() meshes in dimension (children None). Study objects, sketches, bodies another body is made
    from, cut tools, bodies of the other dimension and containers left empty are not shown. A link to one body is
    shown as a body."""
    shapes = {
        o.Name
        for o in doc.Objects
        if (
            (o.isDerivedFrom("Part::Feature") and not o.isDerivedFrom("Sketcher::SketchObject"))
            or link_target(o) is not None
        )
        and not objects.is_study_object(o)
        and objects.owning_body(o) is o
    }
    consumed = _consumed(doc.getObject(name) for name in shapes)  # a cut tool still consumes what it is made of
    shapes -= _left_out(doc)

    def fits(obj):
        shape = body_shape(obj)
        return bool(shape.Solids) if dimension == "3D" else not shape.Solids and bool(shape.Faces)

    def nodes(objs):
        out = []
        for obj in objs:
            if is_container(obj):
                children = nodes(obj.Group)
                if children:
                    out.append((obj, children))
            elif obj.Name in shapes and obj.Name not in consumed and fits(obj):
                out.append((obj, None))
        return out

    return nodes([o for o in doc.Objects if o.getParentGroup() is None and o.getParentGeoFeatureGroup() is None])


def is_excluded(study, obj):
    """True if obj, or a Part or Group it is in, is in the Study's Excluded list."""
    excluded = {o.Name for o in study.Excluded}
    stack, seen = [obj], set()
    while stack:
        obj = stack.pop()
        if obj is None or obj.Name in seen:
            continue
        if obj.Name in excluded:
            return True
        seen.add(obj.Name)
        stack += [obj.getParentGroup(), obj.getParentGeoFeatureGroup()]
    return False


def air_sources(study):
    """{body Name: its Custom Air Region}: the bodies the Study meshes as air, not as bodies."""
    return {
        a.Source.Name: a
        for a in objects.air_regions(study)
        if a.AirShape == "Custom" and getattr(a, "Source", None) is not None
    }


WHY = {  # reason: (gate text, Material warning, item warning); {b} the body, {o} the other object
    "excluded": (
        "{b} is excluded from the Study: tick it in the Study panel.",
        "Material {m} is on {b}, which is excluded from the Study.",
        "{k} {i} is not used for {b}, which is excluded from the Study.",
    ),
    "cut tool": (
        "{b} is the tool of {o} and is not meshed. To mesh it, make a Link to it.",
        "Material {m} is on {b}, the tool of {o}, which is not meshed. To mesh it, make a Link to it.",
        "{k} {i} is not used for {b}, the tool of {o}, which is not meshed. To mesh it, make a Link to it.",
    ),
    "made from": (
        "{b} is not meshed on its own: {o} is made from it.",
        "Material {m} is on {b}, which {o} is now made from: assign it to {o}.",
        "{k} {i} is not used for {b}, which {o} is now made from: put it on {o}.",
    ),
    "air shape": (
        "{b} is the Custom shape of Air Region {o}.",
        None,  # the Air Region has its own Material
        "{k} {i} is not used for {b}, the Custom shape of Air Region {o}: put it on the Air Region.",
    ),
    "drawing": (
        "{b} is the drawing of Symmetric Group {o}: pick its copies on the group.",
        "Material {m} is on {b}, the drawing of Symmetric Group {o}: the group's parts take the Materials.",
        "{k} {i} is not used for {b}, the drawing of Symmetric Group {o}: put it on the cell objects.",
    ),
    "not a body": (
        "{b} is not a body of the Study.",
        "Material {m} is on {b}, which is not a body of the Study.",
        "{k} {i} is not used for {b}, which is not a body of the Study.",
    ),
}


def not_meshed(study, obj):
    """None when obj is a Study body, a cell object or a group (also an Air Region); else (reason, other): why the Study
    does not mesh obj, and the object to name. Reasons: "excluded", "cut tool" (other: the Cut), "made from" (other:
    the meshed body made from obj), "air shape" (other: the Air Region), "drawing" (other: the group), "not a body"."""
    bodies = study_geometry(study)[0]
    meshed = {o.Name for o in bodies + objects.cell_bodies(study) + objects.symmetric_groups(study)}
    if obj.Name in meshed or obj.Name in {a.Name for a in objects.air_regions(study)}:
        return None
    if is_excluded(study, obj):
        return "excluded", None
    for reason, found in (
        ("cut tool", cut_tools(study.Document)),
        ("air shape", air_sources(study)),
        ("drawing", group_drawings(study)),
    ):
        if obj.Name in found:
            return reason, found[obj.Name]
    other = next((b for b in bodies if obj.Name in inputs(b)), None)
    if other is not None:
        return "made from", other
    return "not a body", None


def not_meshed_text(column, obj, reason, other, **names):
    """The text of WHY for column 0 (gate), 1 (Material warning) or 2 (item warning), or None."""
    text = WHY[reason][column]
    if text is None:
        return None
    return text.format(b=objects.display_name(obj), o=objects.display_name(other) if other is not None else "", **names)


def _leaves(nodes):
    """The bodies of tree() nodes, in tree order."""
    out = []
    for obj, children in nodes:
        out += [obj] if children is None else _leaves(children)
    return out


def group_drawings(study, leaves=None):
    """{body Name: Symmetric Group} for each body of the Study's tree, not a cell object, made from a cell object of
    a group (following also a Mirror's source and a Clone's original, not a Cut's tool: a body cut round the copies
    is a real body): the drawing of that group's copies, which the copies replace in the mesh."""
    owner = {}
    for item in objects.symmetric_groups(study):
        for cell in item.Cells:
            owner.setdefault(cell.Name, item)
    if not owner:
        return {}
    if leaves is None:
        leaves = _leaves(tree(study.Document, study.Dimension))
    found = {}
    for body in leaves:
        if body.Name in owner:
            continue
        made_from = inputs(body, outside=COPIES)
        cell = next((name for name in owner if name in made_from), None)
        if cell is not None:
            found[body.Name] = owner[cell]
    return found


def study_geometry(study):
    """(bodies, errors): the Study's free bodies in tree order (every body of its dimension in the document, less the
    excluded ones, the Custom air shapes, the cell objects of Symmetric Groups and their drawings) and the errors
    collect() finds in them."""
    leaves = _leaves(tree(study.Document, study.Dimension))
    left_out = set(air_sources(study)) | {b.Name for b in objects.cell_bodies(study)}
    left_out |= set(group_drawings(study, leaves))
    return collect([b for b in leaves if b.Name not in left_out and not is_excluded(study, b)], study.Dimension)


def export_unavailable(study):
    """Why the Study cannot be meshed at all, or "". Nothing blocks it now; kept for the callers that ask."""
    return ""
