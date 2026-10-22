"""Study validation: every problem at once, for the Validate command, the Study panel and Run Mesh.
Errors stop the mesh; warnings do not. No GUI code here."""

from dataclasses import dataclass, field

from . import airshapes, geometry, objects

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


class _Report:
    def __init__(self):
        self.problems = []

    def error(self, text, item=None, refs=()):
        self.problems.append(Problem(ERROR, text, item, list(refs)))

    def warning(self, text, item=None, refs=()):
        self.problems.append(Problem(WARNING, text, item, list(refs)))


def validate(study):
    """Every problem of the Study, errors and warnings, in a stable order."""
    r = _Report()
    unavailable = geometry.export_unavailable(study)
    if unavailable:
        r.error(unavailable)
        return r.problems
    refresh_padding(study)
    main, moving, setup_errors = geometry.setup(study)
    for text in setup_errors:
        r.error(text)
    bodies = list({b.Name: b for b in main + moving}.values())  # main geometry order, then moving
    included = {b.Name for b in bodies}
    with_air = meshed(study, bodies)
    _skipped_picks(study, r)
    _links(study, with_air, r)
    _settings(study, with_air, r)
    _air(study, bodies, {b.Name for b in moving}, r)
    _slides(study, main, moving, r)
    _transfinite(study, bodies, r)
    _names(study, bodies, included, r)
    _materials(study, r)
    return r.problems


def _skipped_picks(study, r):
    """A body picked by hand that another picked body is made from is not meshed on its own (geometry.collect)."""
    for name in ("Main", "Moving"):
        if getattr(study, name + "Mode") != "Manual" or (name == "Moving" and study.Movement == "No movement"):
            continue
        picked = list(getattr(study, name + "Objects"))
        resolved, _ = geometry.region(study, name)
        kept = {o.Name for o in resolved}
        for obj in picked:
            if obj.Name in kept or not obj.isDerivedFrom("Part::Feature"):
                continue
            users = [o.Label for o in resolved if obj in o.OutListRecursive]
            if users:
                r.warning(
                    f"{obj.Label} is not meshed on its own: {', '.join(users)} is made from it."
                    " Use a copy of it (or the Body) as the Boolean tool if you want both.",
                    obj,
                    [(obj, "")],
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
    """Items left empty by a deleted body, bodies outside the main geometry, sub-elements a body no longer has."""
    items = objects.excitations(study) if study.Dimension == "3D" else []  # 2D: no excitations yet
    items += list(study.MeshSizesGroup.Group)
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
                " not in the main geometry.",
                item,
                [(b, s) for b, subs in outside for s in subs],
            )
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
        if m.Body is None:
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


def refresh_padding(study):
    """Padding mode Air Regions follow the Study's bodies as they are now: a body added to a container source, edited
    since the last recompute or moved with a container counts. Recomputes the air and what it depends on, no more.
    Validate and Run Mesh call it."""
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
    study = objects.owner_study(air)
    readers = objects.readers_in_sources(air, study) if not bodies and study is not None else []
    for reader in readers:  # the container source is no source: it holds an object made from the air
        r.error(prefix + f"{objects.display_name(reader)} depends on the Air Region; it cannot size it.", air)
    if readers:
        return False
    try:
        airshapes.padded_size(air, bodies, plane)
    except ValueError as e:
        text = str(e)
        r.error(text if text.startswith(prefix) else prefix + text, air)
        return False
    return True


def _air(study, bodies, moving, r):
    """One Air Region, a shape the Study's plane allows, and every body inside it. moving: names of the moving
    bodies."""
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
        if source.Name in {b.Name for b in bodies}:  # the mesher would find it overlapping the bodies inside it
            where = "moving" if source.Name in moving else "main"
            r.error(
                f"{source.Label} is the Custom shape of Air Region {objects.display_name(air)};"
                f" take it out of the {where} geometry.",
                air,
                [(source, "")],
            )
            return
        if not _custom_fits(shape, plane):
            need = "a solid" if plane == "3D" else f"a face in the Study's {plane} plane"
            r.error(prefix + f"the Custom body {source.Label} must be {need}.", air, [(source, "")])
            return
    for body in bodies:
        body_shape = geometry.global_shape(body)
        measure = body_shape.Volume if plane == "3D" else body_shape.Area
        if airshapes.outside(body_shape, shape, plane) > 1e-6 * measure:
            r.error(f"{body.Label} is not fully inside Air Region {objects.display_name(air)}.", air, [(body, "")])


def _custom_fits(shape, plane):
    """True if a Custom air shape suits the Study: solids in 3D; in 2D faces in the Study's plane and no solid."""
    if plane == "3D":
        return bool(shape.Solids)
    return bool(shape.Faces) and not shape.Solids and all(geometry.plane_of(f) == plane for f in shape.Faces)


def _slides(study, main, moving, r):
    """Sliding: an Air Region and Sliding Interfaces that cut it, every body on one side, both sides in use."""
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
    if not moving:
        r.error("No body is in the moving geometry.")
        return
    cells = airshapes.cells(air_shape, surfaces)  # once: the bodies are sorted into them below
    moving_names = {b.Name for b in moving}
    fixed = [b for b in main if b.Name not in moving_names]
    held, unplaced = {}, False  # cell index -> ([moving bodies], [fixed bodies]); a body not in one cell
    hint = ""
    if any(i.Kind != "Linear" for i in interfaces):
        hint = " Rotation is about the global Z axis; put the machine axis on Z."
    for side, group in enumerate((moving, fixed)):
        for body in group:
            shape = geometry.global_shape(body)
            measure = shape.Volume if plane == "3D" else shape.Area
            if airshapes.outside(shape, air_shape, plane) > 1e-6 * measure:
                unplaced = True
                continue  # _air reports a body outside the air
            k = airshapes.cell_of(shape, cells)
            if k is None:
                unplaced = True
                r.error(f"{body.Label} crosses a Sliding Interface." + hint, body, [(body, "")])
            else:
                held.setdefault(k, ([], []))[side].append(body)
    if unplaced:
        return  # the sides cannot be judged until those bodies are fixed
    for k in range(len(cells)):
        moving_here, fixed_here = held.get(k, ([], []))
        if moving_here and fixed_here:
            m, f = moving_here[0], fixed_here[0]
            refs = [(m, ""), (f, "")]
            r.error(
                f"Moving body {m.Label} and fixed body {f.Label} are on the same side of the Sliding Interfaces.",
                m,
                refs,
            )
    empty = {}  # error text -> the first interface it names
    for k, cell in enumerate(cells):
        if any(held.get(k, ([], []))):
            continue
        near = [i for i, s in zip(interfaces, surfaces) if cell.distToShape(s)[0] < airshapes.TOL]
        names = ("Sliding Interfaces " if len(near) > 1 else "Sliding Interface ") + ", ".join(i.Label for i in near)
        text = f"Part of the air next to {names} holds no body; its side is unknown. Move an interface or add the body."
        empty.setdefault(text, near[0] if near else None)
    for text, iface in empty.items():
        r.error(text, iface)


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
    """R1 to R3: a body in one Transfinite Body, an edge in one Transfinite Edges, every edge of a
    structured body counted, and no loose compound pieces."""
    included = {b.Name for b in bodies}
    owner = {}
    for t in objects.transfinite_bodies(study):
        for b, _ in objects.subs_by_body(t):
            if b.Name not in included:
                continue
            if b.Name in owner:
                r.error(f"Body {b.Label} is in Transfinite Body {owner[b.Name].Label} and {t.Label}.", t, [(b, "")])
                continue
            owner[b.Name] = t
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
        t = owner.get(b.Name)
        if t is None:
            continue
        if loose_pieces(b.Shape):
            r.error(
                f"Transfinite Body {t.Label}: the {pieces} of {b.Label} touch without sharing {shared}."
                " Make it with Part Slice or Boolean Fragments instead of a compound.",
                t,
                [(b, "")],
            )
            continue
        missing = [f"Edge{i}" for i in range(1, len(b.Shape.Edges) + 1) if (b.Name, f"Edge{i}") not in seen]
        if missing:
            r.error(
                f"Transfinite Body {t.Label}: {b.Label} has edges without Transfinite Edges: " + ", ".join(missing),
                t,
                [(b, s) for s in missing],
            )


def _names(study, bodies, included, r):
    names = [objects.volume_name(b) for b in bodies]
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
            "These group names are the same after removing special characters: "
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
