"""Study validation: every problem at once, for the Validate command, the Study panel and Run Mesh.
Errors stop the mesh; warnings do not. No GUI code here."""

import math
from dataclasses import dataclass, field

import FreeCAD as App
import Part

from . import airshapes, geometry, objects, sides, symmetry

ERROR, WARNING = "error", "warning"


@dataclass
class Problem:
    severity: str
    text: str
    item: object = None  # the Study item or body to select, if any
    refs: list = field(default_factory=list)  # [(body, sub)] to highlight; sub "" = the whole body


def errors(problems):
    return [p for p in problems if p.severity == ERROR]


def loose_pieces(shape):
    """True when two vertices of shape coincide: its solids or faces touch but are not joined (a plain
    compound), so every shared edge appears twice. A Slice or Boolean Fragments result shares them once."""
    points = [v.Point for v in shape.Vertexes]
    return any(p.distanceToPoint(q) < 1e-6 for i, p in enumerate(points) for q in points[i + 1 :])


def _has(body, sub):
    try:
        body.Shape.getElement(sub)
        return True
    except Exception:
        return False


def meshed(study, bodies):
    """Names of what the mesh holds, for the items that refer to it: the bodies and the Air Region, which takes Mesh
    Sizes like a body. The job writer uses the same set."""
    return {b.Name for b in bodies} | {a.Name for a in objects.air_regions(study)}


def body_sizes(study, bodies):
    """[(body, size, item)]: the smallest whole-body Mesh Size on each body, else the default size. item is that Mesh
    Size, or the Mesh Sizes folder for the default. The job writer uses the same sizes."""
    found = {}
    for s in objects.mesh_sizes(study):
        for b, subs in objects.subs_by_body(s):
            if "" in subs and (b.Name not in found or s.Size.Value < found[b.Name][0]):
                found[b.Name] = (s.Size.Value, s)
    settings = study.MeshSizesGroup
    return [(b, *found.get(b.Name, (settings.DefaultMeshSize.Value, settings))) for b in bodies]


class _Report:
    def __init__(self):
        self.problems = []

    def error(self, text, item=None, refs=()):
        self.problems.append(Problem(ERROR, text, item, list(refs)))

    def warning(self, text, item=None, refs=()):
        self.problems.append(Problem(WARNING, text, item, list(refs)))


NO_BODY = "No body to mesh: the document has none of the Study's dimension, or the Study panel excludes them all."


def validate(study):
    """Every problem of the Study, errors and warnings, in a stable order."""
    r = _Report()
    unavailable = geometry.export_unavailable(study)
    if unavailable:
        r.error(unavailable)
        return r.problems
    found = objects.studies(study.Document)
    if len(found) > 1:  # one Study per document: the whole document is its geometry
        labels = [s.Label for s in found]
        listed = f"{', '.join(labels[:-1])} and {labels[-1]}"
        if len(labels) == 2:
            r.error(f"This document has two Studies, {listed}: delete one.")
        else:
            r.error(f"This document has {len(labels)} Studies, {listed}: delete all but one.")
        return r.problems
    refresh_padding(study)
    bodies, geometry_errors = geometry.study_geometry(study)  # with groups, the free objects
    for text in geometry_errors:
        r.error(text)
    grouped = objects.is_grouped(study)
    if not bodies and not grouped and not geometry_errors:
        r.error(NO_BODY)
    included = {b.Name for b in bodies}
    with_air = meshed(study, bodies)
    if grouped:  # mesh settings may sit on the cell objects, which are not free bodies; excitations on a drawing
        with_air |= {b.Name for b in objects.cell_bodies(study)}
        with_air |= {g.Name for g in objects.symmetric_groups(study)}
        included |= {g.Name for g in objects.symmetric_groups(study)}
    _old_items(study, r)
    _body_overlaps(bodies, study.Dimension, r)
    _links(study, with_air, r)
    _settings(study, with_air, r)
    if grouped:
        _groups(study, bodies, r)
    else:
        _air(study, bodies, r)
        _slides(study, bodies, sides.moving(study), r)
    meshed_bodies = bodies + objects.cell_bodies(study)  # with groups, the cells come besides the free objects
    _coarse(study, meshed_bodies, r)
    _transfinite(study, meshed_bodies, r)
    _names(study, bodies, included, r)
    _materials(study, r)
    return r.problems


def old_item_text(item):
    """What to do with a Symmetric Mesh item of an older version, which is not meshed."""
    top = getattr(item, "Top", None)
    return (
        f"Symmetric Mesh {item.Label} is from an older version. Add a Symmetric Group; Read from drawing fills it"
        f" from {top.Label if top is not None else 'its Mirror / Polar Array chain'}."
    )


def _old_items(study, r):
    for item in objects.old_items(study):
        r.error(old_item_text(item), item)


def _body_overlaps(bodies, dimension, r):
    """Bodies may only touch: where two overlap the mesher cannot give the region to either. Fixed and moving bodies
    alike; the Air Region is not a body, the bodies win where they overlap it."""
    unit = "mm³" if dimension == "3D" else "mm²"

    def size(shape):
        return shape.Volume if dimension == "3D" else shape.Area

    shapes = [(b, geometry.global_shape(b)) for b in bodies]
    for i, (a, sa) in enumerate(shapes):
        for b, sb in shapes[i + 1 :]:
            if not sa.BoundBox.intersect(sb.BoundBox):
                continue
            try:
                common = sa.common(sb)
            except Exception:  # OCC refuses some pairs; the mesher still reports an overlap
                continue
            amount = size(common)
            if amount <= 1e-6 * min(size(sa), size(sb)):
                continue
            pieces = common.Solids if dimension == "3D" else common.Faces
            c = max(pieces, key=size).CenterOfMass
            r.error(
                f"Bodies {objects.display_name(a)} and {objects.display_name(b)} overlap by {amount:.3g} {unit}"
                f" near ({c.x:.6g}, {c.y:.6g}, {c.z:.6g}). Bodies may only touch: make them with Part Slice or"
                " Boolean Fragments, or cut one out of the other.",
                b,
                [(a, ""), (b, "")],
            )


def _kind(item):
    return {
        objects.Excitation: "Excitation",
        objects.MeshSize: "Mesh Size",
        objects.TransfiniteBody: "Transfinite Body",
        objects.TransfiniteEdges: "Transfinite Edges",
        objects.Recombine: "Recombine",
    }[type(item.Proxy)]


def _links(study, included, r):
    """Items left empty by a deleted body, bodies the Study does not mesh, sub-elements a body no longer has."""
    items = objects.excitations(study) if study.Dimension == "3D" else []  # 2D: no excitations yet
    items += [
        i
        for i in study.MeshSizesGroup.Group
        if not isinstance(i.Proxy, (objects.SymmetricMesh, objects.SymmetricGroup))
    ]
    for item in items:
        kind, by_body = _kind(item), objects.subs_by_body(item)
        if not by_body:
            r.error(f"{kind} {item.Label} refers to nothing (were its bodies deleted?). Pick again or delete it.", item)
            continue
        refused = objects.air_refusal(type(item.Proxy), [b for b, _ in by_body])
        if refused:
            airs = [(b, "") for b, _ in by_body if objects.is_air(b)]
            r.error(f"{kind} {item.Label}: {refused} Remove it from the item.", item, airs)
        outside = [(b, subs) for b, subs in by_body if b.Name not in included]
        if outside:  # kept on purpose, e.g. to mesh only part of a model; they just do not reach this mesh
            r.warning(
                f"{kind} {item.Label} is not used for {', '.join(b.Label for b, _ in outside)}:"
                " not meshed by the Study.",
                item,
                [(b, s) for b, subs in outside for s in subs],
            )
        if study.Dimension == "3D" and isinstance(item.Proxy, (objects.TransfiniteBody, objects.Recombine)):
            faces = [(b, s) for b, subs in by_body for s in subs if s.startswith("Face")]
            if faces:
                picked = ", ".join(f"{b.Label}.{s}" for b, s in faces)
                r.error(f"{kind} {item.Label}: pick whole solids in a 3D Study ({picked}).", item, faces)
        for b, subs in by_body:
            if b.Name not in included or (refused and objects.is_air(b)):
                continue
            for sub in subs:
                if sub and not _has(b, sub):
                    r.error(f"{kind} {item.Label}: body {b.Label} has no {sub}. Reselect it.", item, [(b, "")])
        if isinstance(item.Proxy, objects.TransfiniteBody):
            refs = {b.Name for b, _ in by_body}
            for b, subs in item.Corners:
                if b.Name not in refs:
                    r.error(
                        f"Transfinite Body {item.Label}: corner {b.Label}.{subs[0]} is not on one of its bodies.", item
                    )
                elif b.Name in included:
                    for sub in subs:
                        if not _has(b, sub):
                            r.error(
                                f"Transfinite Body {item.Label}: body {b.Label} has no {sub}. Reselect it.",
                                item,
                                [(b, "")],
                            )
    for m in objects.materials(study):
        # the assignment of a part has no body
        if m.Body is None and not getattr(m, "PartKey", ""):
            r.warning(f"Material assignment {m.Label} has no body (was it deleted?). Delete the assignment.", m)


def _settings(study, included, r):
    settings = study.MeshSizesGroup
    if settings.DefaultMeshSize.Value <= 0:
        r.error("The default mesh size must be greater than 0.", settings)
    if 0 < settings.MaxSize.Value < settings.MinSize.Value:
        r.error("The minimum mesh size is larger than the maximum.", settings)
    for s in objects.mesh_sizes(study):
        if s.Size.Value <= 0 and any(b.Name in included for b, _ in s.References):
            r.error(f"Mesh size {s.Label} must be greater than 0.", s)
    for e in objects.transfinite_edges(study):
        if e.Distribution == "Bump" and e.BumpCoefficient <= 0:
            r.error(f"Transfinite Edges {e.Label}: the Bump coefficient must be greater than 0.", e)


def thickness(shape):
    """About how thick a solid is, 4 V / A: the diameter of a long round wire."""
    return 4 * shape.Volume / shape.Area if shape.Area > 0 else 0.0


def _coarse(study, bodies, r):
    """A 3D body thinner than its mesh size gets a few broken triangles on a curved face, and the 3D mesh often fails
    with overlapping facets. Flat faces and 2D Studies mesh at any size. Only whole-body sizes count; smaller sizes on
    faces or edges may still save it."""
    if study.Dimension != "3D":
        return
    settings = study.MeshSizesGroup
    for body, size, item in body_sizes(study, bodies):
        shape = geometry.global_shape(body)
        if all(f.Surface.TypeId == "Part::GeomPlane" for f in shape.Faces):
            continue
        size *= settings.SizeFactor
        if settings.MaxSize.Value > 0:
            size = min(size, settings.MaxSize.Value)
        if settings.MinSize.Value > 0:
            size = max(size, settings.MinSize.Value)
        t = thickness(shape)
        if size > 0 and 0 < t < size:
            r.warning(
                f"Mesh size {size:g} mm is larger than {objects.display_name(body)} is thick (about {t:.2g} mm):"
                " the mesher may fail with overlapping facets. Add a smaller Mesh Size for it.",
                item,
                [(body, "")],
            )


def refresh_padding(study):
    """Padding mode Air Regions follow the Study's bodies as they are now: a body drawn later, edited since the last
    recompute or moved with a container counts. Recomputes the air and what it depends on, no more.
    Sliding Interfaces and the drawings of Symmetric Groups that no link keeps up to date are recomputed too.
    Validate and Run Mesh call it. The drawings go first: a Padding mode air fits round them."""
    for item in objects.symmetric_groups(study):  # a moved container of a cell is not linked
        if objects.stale_drawing(item):
            item.touch()
            study.Document.recompute([item])
    objects.refresh_sized_by(study)
    plane = None
    for air in objects.air_regions(study):
        if air.SizeMode != "Padding":
            continue
        plane = plane or airshapes.study_plane(study)
        if _off_size(air, plane):  # e.g. a container moved that no link reports
            air.touch()
        group = [air, *air.OutListRecursive]  # an object recomputed alone does not recompute what it depends on
        if any("Touched" in o.State for o in group):
            study.Document.recompute(group)
    for iface in objects.sliding_interfaces(study):  # the tops are not linked: a new height or a moved top
        if objects.stale_sliding_cylinder(iface):
            iface.touch()
            study.Document.recompute([iface])


def _off_size(air, plane):
    """True if the size properties of a Padding mode air are not what its bodies give now."""
    try:
        size = airshapes.padded_size(air, list(air.SizedBy), plane)
    except ValueError:  # _padding reports it
        return False
    return any(objects._differs(getattr(air, name), value) for name, value in size.items())


def _padding_sides(air, plane):
    """[(side name, property key)] of the padding the Air Region's shape and plane use: "+X", "-Z", "outer"."""
    return [
        (key.lower() if key in ("Outer", "Inner") else ("+" if key.endswith("Plus") else "-") + key[0], key)
        for key, _ in airshapes.padding_sides(air.AirShape, plane)
    ]


def _padding(air, bodies, plane, r):
    """Padding mode: no negative padding and a size the bodies give. True if the air can be built."""
    prefix = f"Air Region {objects.display_name(air)}: "
    negative = [
        side
        for side, prop in _padding_sides(air, plane)
        if getattr(air, f"Pad{prop}Percent") < 0 or getattr(air, f"Pad{prop}").Value < 0
    ]
    for side in negative:
        r.error(prefix + f"padding must not be negative ({side}).", air)
    if negative:
        return False
    loops = objects.dependents_of(air)
    dependent = [b for b in bodies if b.Name in loops]
    for body in dependent:
        r.error(prefix + f"body {objects.display_name(body)} depends on the Air Region; it cannot size it.", air)
    if dependent:
        return False
    try:
        airshapes.padded_size(air, bodies, plane)
    except ValueError as e:
        text = str(e)
        r.error(text if text.startswith(prefix) else prefix + text, air)
        return False
    return True


def _air(study, bodies, r, cells=(), filled=False):
    """One Air Region, a shape the Study's plane allows, and every body inside it. cells: names of cell objects,
    which a Custom shape may not be (a Custom shape is never one of the bodies: geometry.air_sources)."""
    airs = objects.air_regions(study)
    if not airs:
        return
    if len(airs) > 1:
        r.error("Only one Air Region per Study: " + ", ".join(a.Label for a in airs) + ". Delete the others.", airs[1])
    air, plane = airs[0], airshapes.study_plane(study)
    prefix = f"Air Region {objects.display_name(air)}: "
    off_axis = air.AirShape == "Box" and air.Center.x - air.Length.Value / 2 < -airshapes.TOL
    if plane == "ZX" and (air.AirShape == "Custom" or off_axis):
        r.error(prefix + "in a ZX (axisymmetric) Study use a half disc or a rectangle starting on the Z axis.", air)
        return
    if air.SizeMode == "Padding" and not _padding(air, bodies, plane, r):
        return
    try:
        shape = airshapes.air_shape(air, plane)
    except ValueError as e:
        text = str(e)
        r.error(text if text.startswith(prefix) else prefix + text, air)
        return
    if air.AirShape == "Custom":
        source = air.Source
        if source.Name in set(cells):  # the mesher would find it overlapping the copies
            r.error(
                f"{source.Label} is the Custom shape of Air Region {objects.display_name(air)};"
                " take it out of the Symmetric Group.",
                air,
                [(source, "")],
            )
            return
        if not _custom_fits(shape, plane):
            need = "a solid" if plane == "3D" else f"a face in the Study's {plane} plane"
            r.error(prefix + f"the Custom body {source.Label} must be {need}.", air, [(source, "")])
            return
    holder = airshapes.filled_air(air, plane) if filled else shape  # with groups: the outer boundary, holes filled
    hint = ""
    if filled and air.AirShape == "Custom":
        hint = " A Custom air must enclose the copies; a hole through it is not filled."
    for body in bodies:
        body_shape = geometry.global_shape(body)
        measure = body_shape.Volume if plane == "3D" else body_shape.Area
        if airshapes.outside(body_shape, holder, plane) > 1e-6 * measure:
            r.error(
                f"{body.Label} is not fully inside Air Region {objects.display_name(air)}.{hint}", air, [(body, "")]
            )


def _custom_fits(shape, plane):
    """True if a Custom air shape suits the Study: solids in 3D; in 2D faces in the Study's plane and no solid."""
    if plane == "3D":
        return bool(shape.Solids)
    return bool(shape.Faces) and not shape.Solids and all(geometry.plane_of(f) == plane for f in shape.Faces)


def _slides(study, bodies, moving, r):
    """Sliding: an Air Region and Sliding Interfaces that cut it, interfaces that agree on the side of each piece of
    the air, no body across a sliding surface and a body on the moving side. moving: names of the moving bodies."""
    interfaces = objects.sliding_interfaces(study)
    if study.Movement != "Sliding motion":
        for i in interfaces:
            r.warning(f"Sliding Interface {i.Label} is not used: the Study has no movement.", i)
        return
    airs = objects.air_regions(study)
    if not airs or not interfaces:
        r.error("Sliding motion needs an Air Region and at least one Sliding Interface.")
        return
    plane = airshapes.study_plane(study)
    if plane == "ZX":
        r.error("Sliding motion is not supported in a ZX (axisymmetric) Study.")
        return
    try:
        air_shape = airshapes.air_shape(airs[0], plane)
    except ValueError:
        return  # _air reports it
    surfaces = _surfaces(interfaces, airs[0], air_shape, plane, r)
    if surfaces is None:
        return
    cells = airshapes.cells(air_shape, surfaces)  # once: the bodies are sorted into them below
    _, disagreements = sides.piece_sides(cells, interfaces, surfaces, plane)
    for text, iface in disagreements:
        r.error(text, iface)
    unplaced = False  # a body not in one cell
    hint = ""
    if any(i.Kind != "Linear" for i in interfaces):
        hint = " Rotation is about the global Z axis; put the machine axis on Z."
    for body in bodies:
        shape = geometry.global_shape(body)
        measure = shape.Volume if plane == "3D" else shape.Area
        if airshapes.outside(shape, air_shape, plane) > 1e-6 * measure:
            unplaced = True
            continue  # _air reports a body outside the air
        if airshapes.cell_of(shape, cells) is None:
            unplaced = True
            r.error(f"{body.Label} crosses a Sliding Interface." + hint, body, [(body, "")])
    if unplaced or disagreements:
        return  # the sides cannot be judged until those are fixed
    if not moving:
        r.error("No body is on the moving side of the Sliding Interfaces.")


def _surfaces(interfaces, air, air_shape, plane, r):
    """The slide surface of every interface, or None after reporting an interface that cannot be used."""
    surfaces, ok = [], True
    if len({"rotation" if i.Kind != "Linear" else "translation " + i.MotionAxis for i in interfaces}) > 1:
        r.error(
            "Sliding Interfaces "
            + ", ".join(i.Label for i in interfaces)
            + " move in different ways: a Study has one motion, a rotation about Z (Rotational, Axial gap)"
            " or a translation along one axis (Linear).",
            interfaces[-1],
        )
        ok = False
    for i in interfaces:
        name = f"Sliding Interface {i.Label}"
        if i.Kind == "Linear" and air.AirShape != "Box":
            r.error(f"{name}: a Linear interface needs a Box Air Region.", i)
            ok = False
            continue
        try:
            surface = airshapes.slide_surface(i, air_shape, plane)
        except ValueError as e:
            r.error(str(e), i)
            ok = False
            continue
        if not surface.Edges:
            r.error(f"{name} does not cut the Air Region.", i)
            ok = False
            continue
        full = airshapes.full_turn(i, air_shape, plane)
        if full and i.Divisions % 2:
            r.error(f"{name}: Divisions must be even for a full 360° interface (it is meshed in two halves).", i)
            ok = False
        pieces = len(surface.Faces if plane == "3D" else surface.Edges)
        if pieces != (2 if full else 1) or not _marked(i, surface, plane):
            r.error(f"{name} does not span the Air Region: its surface is cut into pieces by the air boundary.", i)
            ok = False
            continue
        surfaces.append(surface)
    return surfaces if ok else None


def _marked(iface, surface, plane):
    """True if the slide point (2D) or slide edge (3D) exists and lies on the slide surface."""
    try:
        marker = airshapes.slide_marker(iface, surface, plane)
    except ValueError:
        return False
    return plane == "3D" or surface.distToShape(marker)[0] < airshapes.TOL


def _transfinite(study, bodies, r):
    """R1 to R3: a face (a whole body in 3D) in one Transfinite Body, an edge in one Transfinite Edges, every edge of
    a structured face counted, no loose compound pieces, corners on a structured face."""
    included = {b.Name for b in bodies}
    owner = {}  # (body name, face) -> Transfinite Body
    entries = []  # (t, b, whole body, the faces of b that t owns)
    for t in objects.transfinite_bodies(study):
        picks = objects.face_picks(t) if study.Dimension == "2D" else [(b, []) for b, _ in objects.subs_by_body(t)]
        for b, faces in picks:
            if b.Name not in included:
                continue
            owned = []
            clashes = {}  # first Transfinite Body -> the faces of b it shares with t
            for face in objects.structured_faces(b, faces):
                if not _has(b, face):  # _links reports it
                    continue
                first = owner.setdefault((b.Name, face), t)
                if first is t:
                    owned.append(face)
                else:
                    clashes.setdefault(first, []).append(face)
            for first, shared in clashes.items():
                first_whole = any(e[0] is first and e[1].Name == b.Name and e[2] for e in entries)
                if not faces and first_whole:
                    r.error(f"Body {b.Label} is in Transfinite Body {first.Label} and {t.Label}.", t, [(b, "")])
                else:
                    names = ", ".join(f"{b.Label}.{f}" for f in shared)
                    verb = "is" if len(shared) == 1 else "are"
                    r.error(
                        f"{names} {verb} in Transfinite Body {first.Label} and {t.Label}.", t, [(b, f) for f in shared]
                    )
            if owned:
                entries.append((t, b, not faces, owned))
    seen = {}
    for e in objects.transfinite_edges(study):
        for b, subs in objects.subs_by_body(e):
            if b.Name not in included:
                continue
            for s in subs:
                if (b.Name, s) in seen and seen[(b.Name, s)] is not e:
                    r.error(
                        f"{b.Label}.{s} is in Transfinite Edges {seen[(b.Name, s)].Label} and {e.Label}.", e, [(b, s)]
                    )
                seen.setdefault((b.Name, s), e)
    pieces, shared = ("faces", "edges") if study.Dimension == "2D" else ("solids", "faces")
    for b in bodies:
        mine = [e for e in entries if e[1].Name == b.Name]
        if not mine:
            continue
        if loose_pieces(b.Shape):
            t = mine[0][0]
            r.error(
                f"Transfinite Body {t.Label}: the {pieces} of {b.Label} touch without sharing {shared}."
                " Make it with Part Slice or Boolean Fragments instead of a compound.",
                t,
                [(b, "")],
            )
            continue
        for t, _, whole, faces in mine:
            if whole:
                groups = [("", _edge_numbers(b))]
            else:
                groups = [(f" {f}", _edge_numbers(b, f)) for f in faces]
            for where, numbers in groups:
                missing = [f"Edge{i}" for i in numbers if (b.Name, f"Edge{i}") not in seen]
                if missing:
                    r.error(
                        f"Transfinite Body {t.Label}: {b.Label}{where} has edges without Transfinite Edges: "
                        + ", ".join(missing),
                        t,
                        [(b, s) for s in missing],
                    )
    for t, b, whole, faces in entries:
        if whole:
            continue
        for cb, subs in t.Corners:
            if cb.Name != b.Name:
                continue
            for sub in subs:
                if _has(b, sub) and not any(_on_face(b, f, sub) for f in faces):
                    text = f"Transfinite Body {t.Label}: corner {b.Label}.{sub} is on none of its structured faces."
                    r.error(text, t, [(b, sub)])


def _edge_numbers(body, face=None):
    """Numbers N of the EdgeN of body that bound the given face (all of body without one). A zero-length edge, the
    pole of a sphere, is left out: it cannot be picked, and the mesher does not need it."""
    edges = None if face is None else body.Shape.getElement(face).Edges
    return [
        i
        for i, e in enumerate(body.Shape.Edges, 1)
        if e.Length > 1e-9 and (edges is None or any(e.isSame(f) for f in edges))
    ]


def _on_face(body, face, vertex):
    v = body.Shape.getElement(vertex)
    return any(v.isSame(f) for f in body.Shape.getElement(face).Vertexes)


def _names(study, bodies, included, r):
    grouped = objects.is_grouped(study)
    if grouped:  # the parts are the volumes, then the free objects
        names = [objects.volume_name(m) for m in objects.part_assignments(study)]
        names += [objects.region_name(study, b) for b in bodies]
    else:
        names = [objects.region_name(study, b) for b in bodies]
        names += [objects.key_name(study, k) for k in objects.air_keys(study)]  # Air, or Air_fixed and Air_moving
    if study.Movement == "Sliding motion":
        names += [objects.key_name(study, i.Name) for i in objects.sliding_interfaces(study)]
    if study.Dimension == "3D":
        names += [
            objects.item_name(e, b)
            for e in objects.excitations(study)
            for b, _ in objects.subs_by_body(e)
            if b.Name in included
        ]
    dups = sorted({n for n in names if names.count(n) > 1})
    if dups:
        r.error(
            "These group names are the same"
            + (" in the mesh" if grouped else "")
            + " after removing special characters: "
            + ", ".join(dups)
            + ". Rename the items or bodies."
        )


def _materials(study, r):
    """The mesh does not need materials, but the input file needs one for every body."""
    bodies = objects.bodies_without_material(study)
    if bodies:
        r.warning(
            "No material (the input file needs one for every body): "
            + ", ".join(objects.display_name(b) for b in bodies),
            None,
            [(b, "") for b in bodies],
        )


def _listed(names, limit=8):
    return ", ".join(names[:limit]) + (f" and {len(names) - limit} more" if len(names) > limit else "")


def _overlaps(item, cells, rules, r, three=False):
    """The copies of the cell objects of group item may only touch (split-cell PRD R3). A cell object past a mirror's
    plane, or a rotation with too many copies, makes them overlap, and the mesher would fail with only a point.
    Copies i and j overlap the way the cell overlaps its copy by T_i^-1 T_j, so the cell is tested against each such
    relative transform once (symmetry.relative_transforms; for rules that close, those are the copies' own
    transforms), only those that move a point of the cells' box into it, and in its own place two cell objects may only
    touch too. Reports the first overlap found. The boxes are exact (_box): a tessellated shape's BoundBox can be
    smaller than the shape."""
    shapes = [(cell, geometry.global_shape(cell)) for cell in cells]
    shapes = [(cell, shape, _box(shape)) for cell, shape in shapes]
    if not shapes:
        return
    boxes = [b for _, _, b in shapes]
    box = (*(min(b[k] for b in boxes) for k in range(3)), *(max(b[k] for b in boxes) for k in range(3, 6)))
    for m in symmetry.relative_transforms(rules, box):
        same = all(abs(a - b) < symmetry.TOL for a, b in zip(m, symmetry.ID))
        for k, (other, shape, other_box) in enumerate(shapes):
            moved, copy = (other_box if same else symmetry.moved_box(m, other_box)), None
            for cell, mine, mine_box in shapes[:k] if same else shapes:
                if not symmetry.boxes_meet(mine_box, moved):
                    continue
                if copy is None:
                    copy = shape if same else shape.transformed(App.Matrix(*m))
                common = mine.common(copy)
                if three:
                    if common.Volume <= 1e-6 * min(mine.Volume, copy.Volume):
                        continue  # they only touch
                elif common.Area <= 1e-6 * min(mine.Area, copy.Area):
                    continue  # they only touch
                if three:
                    c, size = max(common.Solids, key=lambda s: s.Volume).CenterOfMass, f"{common.Volume:.3g} mm³"
                else:
                    c, size = max(common.Faces, key=lambda f: f.Area).CenterOfMass, f"{common.Area:.3g} mm²"
                ts = symmetry.transforms(rules)
                i, j = (0, 0) if same else symmetry.first_pair(ts, m)
                at = symmetry.apply(ts[i], (c.x, c.y, c.z)) if i else (c.x, c.y, c.z)  # where the copies lie
                x, y, z = (round(v, 9) + 0.0 for v in at)
                where = f"({x:.6g}, {y:.6g}, {z:.6g})" if three else f"({x:.6g}, {y:.6g})"
                who = f"cell body {objects.display_name(cell)}"
                if same:
                    what = objects.display_name(other)
                    advice = (
                        "Cell objects may only touch: make them with Part Slice or Boolean Fragments, or cut one out"
                        " of the other."
                    )
                else:
                    if i:  # two copies overlap, though neither is the drawn cell
                        who = f"copy {i + 1} of {who}"
                        what = f"copy {j + 1} of {objects.display_name(other)} (the drawn cell is copy 1)"
                    else:
                        how = "a mirrored copy" if symmetry.det(m) < 0 else _moved_by(m)
                        what = f"{how} of {objects.display_name(other)}"
                    advice = (
                        "The copies of a cell object may only touch: keep every cell object clear of its own copies,"
                        " and check the rules (a mirror's plane, a rotation's step and count, a translation's vector)."
                    )
                r.error(
                    f"Symmetric Group {item.Label}: {who} overlaps {what} near {where}, by {size}. {advice}",
                    item,
                    list({b.Name: (b, "") for b in (cell, other)}.values()),
                )
                return


def _box(shape):
    """(xmin, ymin, zmin, xmax, ymax, zmax) of shape from its geometry, not from its triangles."""
    b = shape.optimalBoundingBox(False, False)
    return (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)


def _interfaces(study, sliding, r):
    """Sliding Interfaces of a Study with Symmetric Groups: one, Rotational; _group_sliding checks the rest."""
    interfaces = objects.sliding_interfaces(study)
    if not sliding:
        for i in interfaces:
            r.warning(f"Sliding Interface {i.Label} is not used: the Study has no movement.", i)
        return
    if not interfaces:
        r.error("Sliding motion needs at least one Sliding Interface.")
    for i in interfaces[1:]:
        r.error(
            "A Study with a Symmetric Group has only one Sliding Interface: more than one is not handled yet, a limit"
            f" of the tool, not of the drawing. Delete {i.Label}.",
            i,
        )
    for i in interfaces:
        if i.Kind != "Rotational":
            r.error(
                f"Sliding Interface {i.Label}: a Study with a Symmetric Group slides Rotational only. {i.Kind} sliding"
                " with Symmetric Groups is not handled yet, a limit of the tool, not of the drawing.",
                i,
            )


# ---- Symmetric Groups (spec section 6)


def _moved_by(m):
    """How a copy that is no mirror lies: moved by a vector, or turned by an angle."""
    if all(abs(m[i] - symmetry.ID[i]) < symmetry.TOL for i in (0, 1, 2, 4, 5, 6, 8, 9, 10)):
        return f"a copy moved by ({m[3]:.6g}, {m[7]:.6g}, {m[11]:.6g})"
    angle = math.degrees(math.acos(max(-1.0, min(1.0, (m[0] + m[5] + m[10] - 1) / 2))))
    return f"a copy turned by {angle:.4g}°"


def _group_plane(study, cells, free, r):
    """ "" in 3D; in 2D the plane ("XY" or "ZX") of the cell objects and the free objects, which must share one."""
    if study.Dimension == "3D":
        return ""
    planes = {}  # plane -> the first body in it
    for body in [*cells, *free]:
        for face in geometry.global_shape(body).Faces:
            found = geometry.plane_of(face)
            if found is None:
                text = "2D faces must lie in the XY plane (z = 0) or the ZX plane (y = 0)."
                r.error(f"{objects.display_name(body)}: {text}", body, [(body, "")])
                break
            planes.setdefault(found, body)
    if len(planes) > 1:
        names = " and ".join(f"{objects.display_name(b)} ({p})" for p, b in planes.items())
        r.error(f"2D geometry must share one plane: {names} are in different planes.")
    return airshapes.plane_of_bodies([*cells, *free])


def _group_rules(item, plane, r):
    """The rules of a group, or None after saying what is wrong with them."""
    prefix = f"Symmetric Group {item.Label}: "
    try:
        rules = objects.rules_of(item)
        found = symmetry.rule_problems(rules, plane)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError):
        r.error(prefix + "the rules cannot be read. Open the group and set its rules again.", item)
        return None
    for text in found:
        r.error(prefix + text, item)
    if found:
        return None
    for text in symmetry.rule_warnings(rules):
        r.warning(prefix + text, item)
    return rules


def _whole_and_blocks(rows):
    """True when the rows of one cell object hold a row for the whole object and another row: they would draw and
    mesh its solids twice."""
    return len(rows) > 1 and any(objects.is_whole(row) for row in rows)


def _group_rows(study, item, rules, r):
    """Every cell object of a group has a solid (face in 2D) and its rows, and no table is of the wrong length or has an
    empty name. True when the cell objects can be drawn."""
    three = study.Dimension == "3D"
    kind = "solid" if three else "face"
    prefix = f"Symmetric Group {item.Label}: "
    ok = True
    rows = objects.rows_of(item)
    gone = list(dict.fromkeys(row["cell"] for row in rows if item.Document.getObject(row["cell"]) is None))
    for name in gone:
        r.error(prefix + f"cell object {name} was deleted. Open the group and pick its cell objects again.", item)
        ok = False
    for cell in item.Cells:
        shape = geometry.global_shape(cell)
        label = objects.display_name(cell)
        if not (shape.Solids if three else shape.Faces):
            cut = "a cutting face or solid" if three else "the cutting sketch"
            r.error(
                prefix + f"cell object {label} has no {kind}; a cell object must be a {kind}. To cut a cell into"
                f" blocks, put its {kind} and {cut} in a Boolean Fragments and use that in the group.",
                item,
                [(cell, "")],
            )
            ok = False
        elif not any(row["cell"] == cell.Name for row in rows):
            r.error(prefix + f"cell object {label} has no part rows. Open the group.", item)
            ok = False
        elif _whole_and_blocks([row for row in rows if row["cell"] == cell.Name]):
            r.error(
                prefix + f"cell object {label} has a row for the whole object beside other rows for it. Open the"
                " group and join its blocks.",
                item,
            )
            ok = False
        elif any(
            row["cell"] == cell.Name and not objects.is_whole(row) and row["solid"] >= len(objects._pieces(shape))
            for row in rows
        ):
            r.error(prefix + f"cell object {label} has fewer {kind}s than the group has rows for.", item)
            ok = False
    if rules is not None:
        n = symmetry.copy_count(rules)
        for row in rows:
            if row.get("mode") != "table":
                continue
            label, table = objects.row_label(item, row), row["table"]
            if len(table) != n:
                r.error(prefix + f"the table of {label} has {len(table)} names, the group makes {n} copies.", item)
            elif not all(str(name).strip() for name in table):
                first = next(i for i, name in enumerate(table, 1) if not str(name).strip())
                r.error(
                    prefix + f"the table of {label} has an empty name (copy {first}). An empty name would leave that"
                    " copy out, and removing a copy is not handled yet, a limit of the tool, not of the drawing: give"
                    " every copy a name.",
                    item,
                )
    return ok


def group_problems(item):
    """What Validate says about one group's rules and rows, for its panel: [Problem], errors first."""
    study = objects.owner_study(item)
    r = _Report()
    plane = "" if study.Dimension == "3D" else airshapes.plane_of_bodies(item.Cells)
    _group_rows(study, item, _group_rules(item, plane, r), r)
    return sorted(r.problems, key=lambda p: p.severity != ERROR)


def _free_cells(groups, r):
    """A cell object is in one group only."""
    owners = {}
    for item in groups:
        for cell in item.Cells:
            owners.setdefault(cell.Name, (cell, []))[1].append(item)
    for cell, items in owners.values():
        if len(items) > 1:
            r.error(
                f"Cell object {objects.display_name(cell)} is in two groups: {', '.join(i.Label for i in items)}."
                " A body can be in one group only.",
                items[1],
                [(cell, "")],
            )


def _elements(group):
    """[(solid or face, its bounding box a little enlarged)] of a group's drawing, and that tolerance."""
    shape = group.Shape
    tol = 1e-6 * max(1.0, shape.BoundBox.DiagonalLength)
    out = []
    for piece in shape.Solids or shape.Faces:
        box = piece.BoundBox
        box.enlarge(tol)
        out.append((piece, box))
    return out, tol


def _touch_groups(a, b, three, r):
    """Copies of two groups on one side may neither overlap nor touch over an area (a length, in 2D). A pair OCC cannot
    compute is reported as a warning, not taken as clear."""
    if a.Shape.isNull() or b.Shape.isNull() or not a.Shape.BoundBox.intersect(b.Shape.BoundBox):
        return

    mine, tol = _elements(a)
    others, _ = _elements(b)
    unit = "mm³" if three else "mm²"
    failed = None  # where the first pair OCC failed on lies
    for sa, box_a in mine:
        for sb, box_b in others:
            if not box_a.intersect(box_b):
                continue
            try:
                hit = _overlap(sa, sb, three, tol)
                if hit is None:
                    continue
                amount, c = hit
                if amount:
                    text = f"overlap by {amount:.3g} {unit} near ({c.x:.6g}, {c.y:.6g}, {c.z:.6g})"
                elif _contact(sa, sb, three, tol):
                    text = "touch"
                else:
                    continue
            except Part.OCCError:
                failed = failed or sa.CenterOfMass
                continue
            advice = "Put them in one group, or draw a normally meshed body between them."
            if text == "touch":
                advice = (
                    "Two groups that touch directly are not handled yet, a limit of the tool, not of the drawing: put"
                    " them in one group, or draw a normally meshed body between them."
                )
            r.error(
                f"Copies of Symmetric Group {a.Label} and Symmetric Group {b.Label} {text}, and both are on the same"
                f" side. {advice}",
                b,
                [(a, ""), (b, "")],
            )
            return
    if failed is not None:
        r.warning(
            f"Could not check contact between Symmetric Group {a.Label} and Symmetric Group {b.Label} near"
            f" ({failed.x:.6g}, {failed.y:.6g}, {failed.z:.6g}); check the drawing. Copies of two groups on one side"
            " may not touch.",
            b,
            [(a, ""), (b, "")],
        )


def _overlap(sa, sb, three, tol):
    """None when two solids (faces, in 2D) are further apart than tol; else (the volume, area in 2D, they share, the
    centre of mass of its largest piece), with (0, None) when they share no more than 1e-6 of the smaller one.
    May raise Part.OCCError."""

    def measure(shape):
        return shape.Volume if three else shape.Area

    if sa.distToShape(sb)[0] > tol:  # apart: neither overlap nor contact, the costly booleans need not run
        return None
    common = sa.common(sb)
    if measure(common) <= 1e-6 * min(measure(sa), measure(sb)):
        return 0, None
    return measure(common), max(common.Solids if three else common.Faces, key=measure).CenterOfMass


def _free_on_copies(groups, free, three, r):
    """A free object may touch the copies of any group, on either side, but not overlap them. A pair OCC cannot compute
    is reported as a warning, not taken as clear."""
    if not free:
        return
    unit = "mm³" if three else "mm²"
    drawn = [(g, _elements(g)[0]) for g in groups if not g.Shape.isNull()]
    for body in free:
        shape = geometry.global_shape(body)
        if shape.isNull():
            continue
        tol = 1e-6 * max(1.0, shape.BoundBox.DiagonalLength)
        box = shape.BoundBox
        box.enlarge(tol)
        name = objects.display_name(body)
        for group, copies in drawn:
            if not box.intersect(group.Shape.BoundBox):
                continue
            failed = None  # where the first pair OCC failed on lies
            for piece, piece_box in copies:
                if not box.intersect(piece_box):
                    continue
                try:
                    hit = _overlap(shape, piece, three, tol)
                except Part.OCCError:
                    failed = failed or piece.CenterOfMass
                    continue
                if hit is None or not hit[0]:
                    continue
                amount, c = hit
                r.error(
                    f"Free object {name} overlaps the copies of Symmetric Group {group.Label} by {amount:.3g} {unit}"
                    f" near ({c.x:.6g}, {c.y:.6g}, {c.z:.6g}). Free objects may only touch the copies: make it the"
                    " Custom shape of the Air Region, or cut the copies out of it.",
                    body,
                    [(body, ""), (group, "")],
                )
                failed = None
                break
            if failed is not None:
                r.warning(
                    f"Could not check overlap between free object {name} and the copies of Symmetric Group"
                    f" {group.Label} near ({failed.x:.6g}, {failed.y:.6g}, {failed.z:.6g}); check the drawing. Free"
                    " objects may only touch the copies.",
                    body,
                    [(body, ""), (group, "")],
                )


def _contact(sa, sb, three, tol):
    """True if two shapes that do not overlap share a face (an edge, in 2D) of positive size. May raise Part.OCCError."""
    first, second = (sa.Faces, sb.Faces) if three else (sa.Edges, sb.Edges)
    for ea in first:
        box = ea.BoundBox
        box.enlarge(tol)
        for eb in second:
            if not box.intersect(eb.BoundBox):
                continue
            common = ea.common(eb)
            if (sum(f.Area for f in common.Faces) if three else sum(e.Length for e in common.Edges)) > tol:
                return True
    return False


def _radial_range(box):
    """The least and the greatest distance from the Z axis that a bounding box reaches."""
    dx = 0 if box.XMin <= 0 <= box.XMax else min(abs(box.XMin), abs(box.XMax))
    dy = 0 if box.YMin <= 0 <= box.YMax else min(abs(box.YMin), abs(box.YMax))
    far = math.hypot(max(abs(box.XMin), abs(box.XMax)), max(abs(box.YMin), abs(box.YMax)))
    return math.hypot(dx, dy), far


def _tools(radius, box, three):
    """(the cylinder face or circle, the solid or disc inside it) of the interface, as long as the box in z."""
    if three:
        base = App.Vector(0, 0, box.ZMin - 1)
        return Part.makeCylinder(radius, box.ZLength + 2, base).Faces[0], Part.makeCylinder(
            radius, box.ZLength + 2, base
        )
    return Part.makeCircle(radius), Part.Face(Part.Wire(Part.makeCircle(radius)))


def _meets(piece, tools, radius, three):
    """How a solid (face in 2D) lies to the interface: None when clear of it, "touches" when it has a face (an edge) on
    it or ends on it, "crosses" when it has material on both sides."""
    near, far = _radial_range(piece.BoundBox)
    tol = 1e-6 * max(1.0, radius)
    if far < radius - tol or near > radius + tol:
        return None
    surface, inner = tools
    try:
        if piece.distToShape(surface)[0] >= tol:
            return None
        size = piece.Volume if three else piece.Area
        inside, outside = piece.common(inner), piece.cut(inner)
    except Part.OCCError:
        return "touches"  # near it, and the rules are checked
    if all((s.Volume if three else s.Area) > 1e-6 * size for s in (inside, outside)):
        return "crosses"
    return "touches"


def _on_interface(shape, radius, three):
    """True if a body crosses the cylinder (circle) of this radius about Z, or has a face on it."""
    return _meets(shape, _tools(radius, shape.BoundBox, three), radius, three) is not None


def _reach(group, radius, three):
    """How the drawing of a group lies to the interface: None, "touches" or "crosses" (any one solid that does)."""
    return _shape_reach(group.Shape, radius, three)


def _shape_reach(shape, radius, three):
    """How a shape lies to the interface: None, "touches" or "crosses" (any one solid, face in 2D, that does)."""
    if shape.isNull() or not (shape.Solids or shape.Faces):
        return None
    tools = _tools(radius, shape.BoundBox, three)
    found = None
    for piece in shape.Solids if three else shape.Faces:
        how = _meets(piece, tools, radius, three)
        if how == "crosses":
            return how
        found = found or how
    return found


def _drawn_cross(cell, radius, three):
    """True if a cell object, where it is drawn, crosses the interface."""
    return _shape_reach(geometry.global_shape(cell), radius, three) == "crosses"


def _about_z(rule):
    """True for a rule that keeps a sliding surface about Z whole (symmetry.z_motion)."""
    return symmetry.z_motion(symmetry.rule_matrix(rule)) is not None


def _group_sliding(study, groups, ruled, free, plane, side, r):
    """Sliding with groups (spec 7.5): a group that reaches the interface may only turn about Z through the origin or
    mirror in a plane that contains Z or in z = const; its turns divide the Divisions; no free object touches it.
    side: group Name -> sides.group_side."""
    three = study.Dimension == "3D"
    sliding = study.Movement == "Sliding motion"
    _interfaces(study, sliding, r)
    if not sliding:
        return
    if plane == "ZX":
        r.error("Sliding motion is not supported in a ZX (axisymmetric) Study.")
        return
    crossed = set()  # the groups refused below as crossing an interface
    for iface in objects.sliding_interfaces(study):
        if iface.Kind != "Rotational":
            continue  # _interfaces says so
        radius = iface.Radius.Value
        reached = set()  # the sides a group reaches the interface on
        for item in groups:
            how = _reach(item, radius, three)
            if how is None:
                continue
            reached.add(side[item.Name])  # None for a group across it, reported below
            rules = ruled.get(item.Name)
            off_z = [(n, rule) for n, rule in enumerate(rules or [], 1) if not _about_z(rule)]
            if how == "crosses" and off_z and not any(_drawn_cross(c, radius, three) for c in item.Cells):
                how = "touches"  # only copies made by a rule refused below cross it: splitting the cells would not help
            if how == "crosses":
                crossed.add(item.Name)
                r.error(
                    f"Sliding Interface {iface.Label}: Symmetric Group {item.Label} crosses it. A group may only end"
                    " on the sliding surface: split the cell objects at it.",
                    iface,
                    [(item, "")],
                )
            if rules is None:
                continue
            for n, rule in off_z:
                r.error(
                    f"Sliding Interface {iface.Label}: Symmetric Group {item.Label} reaches it, but Rule {n}"
                    f" ({rule['kind']}) is not a rotation about Z through the origin, a mirror in a plane"
                    " containing Z or a mirror of z = const. Only these keep the sliding surface whole; this is"
                    " a limit of the tool.",
                    iface,
                )
            turns = symmetry.turns_about_z(rules)
            if turns > 1 and iface.Divisions % turns:
                r.error(
                    f"Sliding Interface {iface.Label}: the divisions ({iface.Divisions}) must be a multiple of the"
                    f" {turns} turns of {item.Label}'s cell objects.",
                    iface,
                )
        for name in ("fixed", "moving") if None not in reached else ():  # a group across it has no side
            if name not in reached:
                r.error(
                    f"Sliding Interface {iface.Label}: no Symmetric Group on the {name} side reaches it. Cell objects"
                    " of groups must cover the sliding surface on both sides (a limit of the tool: free objects may"
                    " not touch it).",
                    iface,
                )
        for body in free:
            if _on_interface(geometry.global_shape(body), radius, three):
                r.error(
                    f"Free object {objects.display_name(body)} crosses or touches Sliding Interface {iface.Label}."
                    " The sliding surface must be covered by cell objects of groups on both sides: draw the air next"
                    " to it as a cell object, and keep free objects clear of it.",
                    iface,
                    [(body, "")],
                )
        for air in objects.air_regions(study):
            try:
                shape = airshapes.air_shape(air, "3D" if three else plane)
            except ValueError:
                continue  # _air reports it
            if _on_interface(shape, radius, three):
                r.error(
                    f"Air Region {objects.display_name(air)} crosses or touches Sliding Interface {iface.Label}. With"
                    " Symmetric Groups the air must keep clear of the sliding surface, a limit of the tool: use a"
                    " Sector whose inner radius is past the copied air band, or a Custom shape.",
                    iface,
                    [(air, "")],
                )
    interfaces = objects.sliding_interfaces(study)
    for item in groups:  # the side group_side gives: none for copies on both sides, touching it or not
        if interfaces and side[item.Name] is None and item.Name not in crossed and item.Shape.Faces:
            r.error(
                f"Symmetric Group {objects.display_name(item)} has copies on both sides of Sliding Interface"
                f" {interfaces[0].Label}: a group is all on one side. Move the interface or split the group.",
                item,
                [(item, "")],
            )
    _air_off_moving(groups, objects.air_regions(study), "3D" if three else plane, side, r)


def _air_off_moving(groups, airs, plane, side, r):
    """The Air Region is meshed with the fixed side (spec decision 3): it may neither touch nor overlap the copies of a
    group on the moving side, the two meshes would share no nodes there. side: group Name -> sides.group_side."""
    moving = [g for g in groups if side[g.Name] == "moving" and not g.Shape.isNull()]
    for air in airs:
        try:
            shape = airshapes.air_shape(air, plane)
        except ValueError:
            continue  # _air reports it
        for group in moving:
            copies, tol = _elements(group)
            near = shape.BoundBox  # a new box on each read
            near.enlarge(tol)
            if not near.intersect(group.Shape.BoundBox):
                continue
            if any(near.intersect(b) and shape.distToShape(piece)[0] <= tol for piece, b in copies):
                r.error(
                    f"Air Region {objects.display_name(air)} touches the copies of Symmetric Group {group.Label},"
                    " which is on the moving side. With Symmetric Groups the Air Region is all on the fixed side, a"
                    " limit of the tool: draw the air next to the moving copies as a cell object of a moving group.",
                    air,
                    [(air, ""), (group, "")],
                )


def _part_materials(study, readable, side, r):
    """Every part has a Material; a part name is on one side of a Sliding Interface only. readable: the groups whose
    rules and rows could be read; side: group Name -> sides.group_side (a group with none is skipped here,
    _group_sliding reports it)."""
    parts = objects.study_parts(study, readable)
    have = {m.PartKey: m for m in objects.part_assignments(study)}
    sliding = study.Movement == "Sliding motion"
    on = {key: {side[item.Name] for item, _, _ in copies} - {None} for key, copies in parts.items()}

    def named(key):
        return key + (" (moving)" if sliding and "moving" in on.get(key, ()) else "")

    spelled = {}  # the name as the mesh has it -> {part name: the first group that has it}
    for name, copies in parts.items():
        spelled.setdefault(objects.clean(name), {}).setdefault(name, copies[0][0])
    for clashing in spelled.values():
        if len(clashing) > 1:
            r.error(
                "These part names are the same in the mesh, after removing special characters:"
                f" {', '.join(sorted(clashing))}. Rename them in the group's table.",
                next(iter(clashing.values())),
            )
    missing = [key for key in parts if key not in have or have[key].LibraryMaterial is None]
    if missing:
        r.error(
            f"Parts with no Material: {_listed([named(k) for k in missing])}. Open the group and choose their Material.",
            parts[missing[0]][0][0],
        )
    if len(readable) == len(objects.symmetric_groups(study)):
        for key, m in have.items():
            if key not in parts:
                r.warning(f"Material {m.Label} is for part {named(key)}, which no group makes any more. Delete it.", m)
    if sliding:
        both = sorted(k for k in parts if on[k] == {"fixed", "moving"})
        if both:
            interfaces = objects.sliding_interfaces(study)
            r.error(
                f"Part names on both sides of the Sliding Interface: {_listed(both)}. The moving side needs IDs of"
                " its own: give its parts other names.",
                interfaces[0] if interfaces else None,
            )


def _free_transfinite(study, free, r):
    """A free object cannot be structured (spec 4.4): the mesher cannot yet put a structured mesh around copies."""
    names = {b.Name for b in free}
    for t in objects.transfinite_bodies(study):
        on = [b for b, _ in objects.subs_by_body(t) if b.Name in names]
        if on:
            r.error(
                f"Transfinite Body {t.Label} refers to free object {_listed([objects.display_name(b) for b in on])}:"
                " a free object cannot be structured yet (a limit of the tool, not a fault in the model). Make it a"
                " cell object of a group, or take it out of the item.",
                t,
                [(b, "") for b in on],
            )


def _groups(study, free, r):
    """A Study with Symmetric Groups (spec section 6). free: the Study's bodies, which are in no group, checked as
    ordinary bodies by validate."""
    groups = objects.symmetric_groups(study)
    three = study.Dimension == "3D"
    cell_bodies = objects.cell_bodies(study)
    _air(study, free + groups, r, {b.Name for b in cell_bodies}, filled=True)
    plane = _group_plane(study, cell_bodies, free, r)
    _free_cells(groups, r)
    ruled, drawn = {}, []  # group Name -> its rules; the groups whose rules and rows can be read
    for item in groups:
        rules = _group_rules(item, plane, r)
        if rules is not None:
            ruled[item.Name] = rules
        if _group_rows(study, item, rules, r) and rules is not None:
            drawn.append(item)
            _overlaps(item, item.Cells, rules, r, three)
    side = {g.Name: sides.group_side(study, g) for g in groups}
    for i, a in enumerate(drawn):
        for b in drawn[i + 1 :]:
            if side[a.Name] is not None and side[a.Name] == side[b.Name]:
                _touch_groups(a, b, three, r)
    _free_on_copies(drawn, free, three, r)
    names = {g.Name for g in groups}
    settings = objects.mesh_sizes(study) + objects.transfinite_bodies(study) + objects.transfinite_edges(study)
    for item in settings + objects.recombine_items(study):
        on = [b for b, _ in objects.subs_by_body(item) if b.Name in names]
        if on:
            r.error(
                f"{_kind(item)} {item.Label} refers to {_listed([objects.display_name(b) for b in on])}: copies are not"
                " meshed. Put it on the cell objects instead.",
                item,
                [(b, "") for b in on],
            )
    cells = {b.Name for b in objects.cell_bodies(study)}
    for e in objects.excitations(study):
        for b in [b for b, _ in objects.subs_by_body(e) if b.Name in cells]:
            r.error(
                f"Excitation {e.Label} refers to {objects.display_name(b)}: copies are not where it is drawn."
                " Pick the faces on the drawing.",
                e,
                [(b, "")],
            )
    for m in objects.materials(study):
        if m.Body is not None and m.Body.Name in names:
            r.error(
                f"Material {m.Label}: Symmetric Group {objects.display_name(m.Body)} gets its Materials through its"
                " parts, not as a whole body. Delete this assignment.",
                m,
                [(m.Body, "")],
            )
        elif m.Body is not None and m.Body.Name in cells:
            r.warning(
                f"Material {m.Label} is not used: the Materials of a Symmetric Group come from its parts, not from its"
                " cell objects.",
                m,
                [(m.Body, "")],
            )
    _group_sliding(study, groups, ruled, free, plane, side, r)
    _free_transfinite(study, free, r)
    _part_materials(study, drawn, side, r)
