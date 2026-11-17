"""Study validation: every problem at once, for the Validate command, the Study panel and Run Mesh.
Errors stop the mesh; warnings do not. No GUI code here."""

import math
from dataclasses import dataclass, field

import FreeCAD as App
import Part

from . import airshapes, geometry, objects, sides, symmetry, sweeps

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
        geometry.body_shape(body).getElement(sub)
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
    known = {"bodies": bodies}  # what geometry.not_meshed needs, worked out once
    _links(study, with_air, r, known)
    _settings(study, with_air, r, bodies + objects.cell_bodies(study))
    if grouped:
        _groups(study, bodies, r)
    else:
        _air(study, bodies, r)
        _slides(study, bodies, r)
    meshed_bodies = bodies + objects.cell_bodies(study)  # with groups, the cells come besides the free objects
    _coarse(study, meshed_bodies, r)
    _transfinite(study, meshed_bodies, r)
    _names(study, bodies, included, r)
    _materials(study, r, known)
    _links_not_bodies(study, bodies + objects.cell_bodies(study), r)
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
        objects.RefineNear: "Refine Near",
        objects.AirGrading: "Air Grading",
        objects.SkinLayer: "Skin Layer",
        objects.SweptBody: "Swept Body",
        objects.TransfiniteBody: "Transfinite Body",
        objects.TransfiniteEdges: "Transfinite Edges",
        objects.Recombine: "Recombine",
    }[type(item.Proxy)]


def _links(study, included, r, known=None):
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
        for b, subs in by_body:  # kept on purpose, e.g. to mesh only part of a model; they just do not reach this mesh
            why = geometry.not_meshed(study, b, known) if b.Name not in included else None
            text = geometry.not_meshed_text(2, b, *why, k=kind, i=item.Label) if why is not None else None
            if text:
                r.warning(text, item, [(b, s) for s in subs])
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


def _settings(study, included, r, bodies=()):
    """bodies: what the mesh holds besides the Air Region, for the Skin Layer's layer edges."""
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
    parts = {}  # body Name -> _mesh_part, worked out once and only with Symmetric Groups
    for n in objects.refine_items(study):
        if any(b.Name in included for b, _ in n.References):
            if n.FineSize.Value <= 0:
                r.error(f"Refine Near {n.Label}: the fine size must be greater than 0.", n)
            elif n.CoarseSize.Value < n.FineSize.Value:
                r.error(f"Refine Near {n.Label}: the coarse size must not be smaller than the fine size.", n)
            if n.GrowthDistance.Value <= 0:
                r.error(f"Refine Near {n.Label}: the growth distance must be greater than 0.", n)
        unmeshed = [b for b in n.LimitTo if b.Name not in included]
        if unmeshed and len(unmeshed) == len(n.LimitTo):  # jobwriter.refine_entries leaves the item out
            r.warning(
                f"Refine Near {n.Label}: no body in Limit to is meshed by the Study; the refinement is skipped.", n
            )
            continue
        for b in unmeshed:
            r.warning(
                f"Refine Near {n.Label}: {objects.display_name(b)} in Limit to is not meshed by the Study; it has"
                " no effect there.",
                n,
            )
        if not objects.is_grouped(study):
            continue
        meshed_limit = [b for b in n.LimitTo if b.Name in included]
        picked = [b for b, _ in n.References if b.Name in included]
        for b in meshed_limit + picked:
            parts.setdefault(b.Name, _mesh_part(study, b))
        pick_parts = set().union(*(parts[b.Name] for b in picked))
        lost = set()  # the picked bodies whose job leaves the item out: apart from every body in Limit to
        if meshed_limit and pick_parts:
            apart = [b for b in meshed_limit if not parts[b.Name] & pick_parts]
            if len(apart) == len(meshed_limit):  # jobwriter.refine_entries leaves the item out of every job
                r.warning(
                    f"Refine Near {n.Label}: no body in Limit to is meshed with its picks; the refinement is skipped.",
                    n,
                )
                continue
            for b in apart:
                r.warning(
                    f"Refine Near {n.Label}: {objects.display_name(b)} in Limit to is meshed apart from its picks (a"
                    " Symmetric Group's cell objects are meshed on their own); it has no effect there.",
                    n,
                )
            limit_parts = set().union(*(parts[b.Name] for b in meshed_limit))
            for b in dict.fromkeys(picked):
                if parts[b.Name] and not parts[b.Name] & limit_parts:
                    lost.add(b.Name)
                    r.warning(
                        f"Refine Near {n.Label}: {objects.display_name(b)} is meshed apart from every body in Limit"
                        " to; it has no effect there.",
                        n,
                    )
        free = [
            (b, subs)
            for b, subs in objects.subs_by_body(n)
            if b.Name in included and b.Name not in lost and any(p.startswith("free") for p in parts[b.Name])
        ]
        _free_picks_on_copies(study, n, free, r)
    _skin_layers(study, included, bodies, r)
    _swept_bodies(study, included, bodies, r)
    _air_gradings(study, included, r)


def _skin_layers(study, included, bodies, r):
    """Skin Layer items: whole conductors, positive settings, and warnings where the layer does not do what it says.
    The air is refused in _links."""
    structured = {b.Name for t in objects.transfinite_bodies(study) for b, _ in objects.subs_by_body(t)}
    recombined = {b.Name for t in objects.recombine_items(study) for b, _ in objects.subs_by_body(t)}
    three = study.Dimension == "3D"
    swept = {b.Name for w in objects.swept_bodies(study) for b, _ in objects.subs_by_body(w)}
    owners = {}  # body Name -> the first Skin Layer that has it
    for s in objects.skin_layers(study):
        if not any(b.Name in included for b, _ in s.References):
            continue
        picked = [(b, subs) for b, subs in objects.subs_by_body(s) if b.Name in included and not objects.is_air(b)]
        depth = s.SkinDepth.Value
        bad = False
        for ok, what in (
            (depth > 0, "the skin depth"),
            (s.ElementsPerDepth > 0, "elements per depth"),
            (s.LayerDepth > 0, "the layer depth"),
        ):
            if not ok:
                bad = True
                r.error(f"Skin Layer {s.Label}: {what} must be greater than 0.", s)
        if three and s.QuadLayers and not (picked and all(b.Name in swept for b, _ in picked)):  # a section has quads
            r.warning(f"Skin Layer {s.Label}: quad layers are made in 2D Studies only; ignored.", s)
        layer = s.LayerDepth * depth
        for b, subs in picked:
            name = objects.display_name(b)
            parts = [sub for sub in subs if sub]
            for sub in parts:
                r.error(f"Skin Layer {s.Label}: pick whole conductors, not {b.Label}.{sub}.", s, [(b, sub)])
            if parts:
                continue
            first = owners.setdefault(b.Name, s)
            if first is not s:
                r.warning(
                    f"Skin Layer {s.Label}: {name} already has Skin Layer {first.Label}; the smallest size wins, and"
                    " only the first makes quad layers.",
                    s,
                    [(b, "")],
                )
            if b.Name in structured:
                r.warning(
                    f"Skin Layer {s.Label}: {name} is structured, and that wins; the Skin Layer does nothing there.",
                    s,
                    [(b, "")],
                )
                continue
            quads = s.QuadLayers and not three
            if quads and b.Name in recombined:
                r.warning(
                    f"Skin Layer {s.Label}: {name} is recombined; it gets the graded layer but no quad layers.",
                    s,
                    [(b, "")],
                )
            if bad:
                continue
            shape = geometry.global_shape(b)
            t = thickness(shape) if three else thickness_2d(shape)
            if 0 < t < 2 * layer:
                r.warning(
                    f"Skin Layer {s.Label}: the layer ({layer:g} mm) is deeper than half of {name} (about {t:.2g} mm"
                    f" thick); the whole body is skin, so a Mesh Size of {depth / s.ElementsPerDepth:g} mm on it does"
                    " the same.",
                    s,
                    [(b, "")],
                )
            if not quads or b.Name in recombined:
                continue
            if objects.is_grouped(study) and _is_free(study, b):
                r.warning(
                    f"Skin Layer {s.Label}: quad layers are not made on free objects of a Study with Symmetric Groups;"
                    f" {name} gets graded triangles.",
                    s,
                    [(b, "")],
                )
            elif _sharp(study, b, shape, bodies, layer):
                r.warning(
                    f"Skin Layer {s.Label}: {name} has sharp corners on its surface; quad layers need a smooth surface,"
                    " so it gets graded triangles.",
                    s,
                    [(b, "")],
                )


def _swept_bodies(study, included, bodies, r):
    """Swept Body items: whole bodies that are sweeps, in a 3D Study without Symmetric Groups, each in one item, not
    structured, and touching only the air and unstructured bodies by whole faces. The air is refused in _links."""
    items = [w for w in objects.swept_bodies(study) if any(b.Name in included for b, _ in w.References)]
    if not items:
        return
    three, grouped = study.Dimension == "3D", objects.is_grouped(study)
    structured = {}  # body Name -> the first Transfinite Body that has it
    for t in objects.transfinite_bodies(study):
        for b, _ in objects.subs_by_body(t):
            structured.setdefault(b.Name, t)
    recombined = {b.Name for t in objects.recombine_items(study) for b, _ in objects.subs_by_body(t)}
    owners = {}  # body Name -> the first Swept Body that has it
    found = []  # (item, body, shape): the sweeps, for the checks of their contacts
    for w in items:
        if not three:
            r.error(f"Swept Body {w.Label}: a 2D Study is already a cross-section; Swept Body is for 3D Studies.", w)
        if grouped:
            r.error(f"Swept Body {w.Label}: Studies with Symmetric Groups are not swept yet.", w)
        picked = [(b, subs) for b, subs in objects.subs_by_body(w) if b.Name in included and not objects.is_air(b)]
        for b, subs in picked:
            parts = [sub for sub in subs if sub]
            for sub in parts:
                r.error(f"Swept Body {w.Label}: pick whole bodies, not {b.Label}.{sub}.", w, [(b, sub)])
            if parts or not three or grouped:
                continue
            name = objects.display_name(b)
            first = owners.setdefault(b.Name, w)
            if first is not w:
                r.error(f"Swept Body {w.Label}: {name} is already in Swept Body {first.Label}.", w, [(b, "")])
                continue
            if b.Name in structured:
                r.error(
                    f"Swept Body {w.Label}: {name} also has Transfinite Body {structured[b.Name].Label}; a body is"
                    " swept or structured, not both.",
                    w,
                    [(b, "")],
                )
                continue
            shape = geometry.global_shape(b)
            starts = [sub for sb, sub_list in w.StartFace if sb.Name == b.Name for sub in sub_list]
            result = sweeps.recognise_body(shape, starts)
            if isinstance(result, str):
                r.error(f"Swept Body {w.Label}: {name} is not a sweep: {result}.", w, [(b, "")])
                continue
            found.append((w, b, shape))
    swept = {b.Name for _, b, _ in found}
    _swept_win(study, included, swept, r)
    others = [(o, geometry.global_shape(o)) for o in bodies if o.Name in included and not objects.is_air(o)]
    order = {b.Name: i for i, (_, b, _) in enumerate(found)}
    for i, (w, b, shape) in enumerate(found):
        name = objects.display_name(b)
        tol = 1e-6 * max(1.0, shape.BoundBox.DiagonalLength)
        box = shape.BoundBox
        box.enlarge(tol)
        solids = shape.Solids
        for k, solid in enumerate(solids):  # the solids of one reference touching each other
            if any(_shared_area(f, other) > tol * tol for f in solid.Faces for other in solids[k + 1 :]):
                r.error(_touch_text(w, name, name, "swept"), w, [(b, "")])
                break
        for o, o_shape in others:
            if o.Name == b.Name or not box.intersect(o_shape.BoundBox):
                continue
            if o.Name in swept and order[o.Name] < i:
                continue  # the earlier of two swept bodies reports the contact
            areas = [_shared_area(f, o_shape) for f in shape.Faces]
            what = "swept" if o.Name in swept else "structured" if o.Name in structured else None
            what = what or ("recombined" if o.Name in recombined else None)
            if what and any(a > 1e-6 * f.Area for a, f in zip(areas, shape.Faces)):
                r.error(_touch_text(w, name, objects.display_name(o), what), w, [(b, ""), (o, "")])
            for n, (f, a) in enumerate(zip(shape.Faces, areas), 1):
                if 1e-6 * f.Area < a < (1 - 1e-6) * f.Area:
                    r.error(
                        f"Swept Body {w.Label}: {objects.display_name(o)} touches only part of {b.Label}.Face{n} of"
                        f" {name}; a swept body's faces must be touched whole or not at all.",
                        w,
                        [(b, f"Face{n}"), (o, "")],
                    )
    _swept_clear_of_sliding(study, found, r)


def _touch_text(w, name, other, what):
    return (
        f"Swept Body {w.Label}: {name} touches {other}, which is {what}; a swept body may touch only the air and"
        " unstructured bodies."
    )


def _shared_area(face, shape):
    """The area face shares with shape, 0 where OCC cannot tell."""
    try:
        return face.common(shape).Area
    except Part.OCCError:
        return 0.0


def _swept_win(study, included, swept, r):
    """A Mesh Size or Refine Near that picks a swept body does nothing inside it: the sweep sets its own sizes."""
    for item, kind in [(m, "Mesh Size") for m in objects.mesh_sizes(study)] + [
        (n, "Refine Near") for n in objects.refine_items(study)
    ]:
        for b, subs in objects.subs_by_body(item):
            # a whole-body Mesh Size is the size a sweep falls back to, so only its sub-element picks are lost
            if kind == "Mesh Size" and "" in subs and not any(subs):
                continue
            if b.Name in swept and b.Name in included:
                r.warning(
                    f"{kind} {item.Label}: {objects.display_name(b)} is swept, and that wins; the {kind} does nothing"
                    " inside it.",
                    item,
                    [(b, "")],
                )


def _swept_clear_of_sliding(study, found, r):
    """A swept body may not touch a Sliding Interface's surface."""
    interfaces, airs = objects.sliding_interfaces(study), objects.air_regions(study)
    if not found or study.Movement != "Sliding motion" or not interfaces or not airs:
        return
    plane = airshapes.study_plane(study)
    try:
        air_shape = airshapes.air_shape(airs[0], plane)
    except ValueError:
        return  # _air reports it
    surfaces = _surfaces(interfaces, airs[0], air_shape, plane, _Report())
    for iface, surface in zip(interfaces, surfaces or []):
        for w, b, shape in found:
            if surface.distToShape(shape)[0] < 1e-6:
                r.error(
                    f"Swept Body {w.Label}: {objects.display_name(b)} touches the sliding interface {iface.Label};"
                    " swept bodies must keep clear of it.",
                    w,
                    [(b, "")],
                )


def _sharp(study, body, shape, bodies, layer):
    """True when a 2D body's layer edges are not smooth: two meet with the direction turning by more than 15°, or one
    is curved tighter than the layer's depth. A layer edge is an edge of the body's boundary shared with another meshed
    body, or inside the Air Region's face (not on its outline). For a cell object the edges it shares with the other
    cell objects of its groups and its edges toward the free side (free_faces), as its cell job sees them: an edge on
    a seam or against a copy is a cut."""
    tol = 1e-6 * max(1.0, shape.BoundBox.DiagonalLength)
    outline = None
    airs = objects.air_regions(study)
    mine = [g for g in objects.symmetric_groups(study) if body in g.Cells]
    cells = {c.Name for g in mine for c in g.Cells}
    free = [shape.getElement(n) for g in mine for n in free_faces(study, g, body)]
    if cells:
        bodies = [o for o in bodies if o.Name in cells]
    elif airs:
        try:
            outline = Part.Compound(airshapes.air_shape(airs[0], airshapes.study_plane(study)).Edges)
        except ValueError:  # _air reports it
            pass
    box = shape.BoundBox
    box.enlarge(tol)
    others = [geometry.global_shape(o) for o in bodies if o.Name != body.Name]
    others = [o for o in others if box.intersect(o.BoundBox)]
    face_edges = [e for f in shape.Faces for e in f.Edges]
    edges = [e for e in shape.Edges if e.Length > tol and sum(e.isSame(f) for f in face_edges) == 1]  # the boundary
    ends = []  # (point, direction leaving the point along the edge)
    for e in edges:
        samples = [e.valueAt(e.FirstParameter + k * (e.LastParameter - e.FirstParameter) / 4) for k in (1, 2, 3)]
        shared = any(_on(samples, o, tol) for o in others) or any(e.isSame(f) for f in free)
        if not shared and (outline is None or _on(samples, outline, tol)):
            continue
        u0, u1 = e.FirstParameter, e.LastParameter
        if any(e.curvatureAt(u0 + k * (u1 - u0) / 8) * layer > 1 for k in range(9)):
            return True
        ends.append((e.valueAt(u0), e.tangentAt(u0).normalize()))
        ends.append((e.valueAt(u1), -e.tangentAt(u1).normalize()))
    limit = math.cos(math.radians(15))
    for i, (p, a) in enumerate(ends):
        for q, b in ends[i + 1 :]:
            if p.distanceToPoint(q) < tol and -a.dot(b) < limit:  # the turn from arriving along -a to leaving along b
                return True
    return False


def _on(points, shape, tol):
    """True if every point lies on shape."""
    return all(shape.distToShape(Part.Vertex(p))[0] < tol for p in points)


def _beyond(element, body, step, tol):
    """A few points just outside body (a face in 2D, a solid in 3D) beyond an edge (a face in 3D) of its boundary, step
    from it along its normal, away from its ends and sides; [] where that cannot be told."""
    if element.ShapeType == "Edge":
        plane = body.Faces[0].normalAt(0, 0)
        u0, u1 = element.FirstParameter, element.LastParameter
        at = [
            (element.valueAt(u), element.tangentAt(u).cross(plane)) for u in (u0 + k * (u1 - u0) / 4 for k in (1, 2, 3))
        ]
    else:
        u0, u1, v0, v1 = element.ParameterRange
        grid = [(u0 + i * (u1 - u0) / 4, v0 + j * (v1 - v0) / 4) for i in (1, 2, 3) for j in (1, 2, 3)]
        at = [(element.valueAt(u, v), element.normalAt(u, v)) for u, v in grid if element.isPartOfDomain(u, v)]
    out = []
    for p, n in at:
        if n.Length < 1e-12:
            return []
        n.normalize()
        sides = [q for q in (p + n * step, p - n * step) if not _inside(q, [body], tol)]
        if len(sides) != 1:
            return []
        out += sides
    return out


def _inside(q, shapes, tol):
    """True if the point q lies in one of shapes: on a face in 2D, inside a solid in 3D."""
    for s in shapes:
        if s.Solids:
            if any(solid.isInside(q, tol, True) for solid in s.Solids):
                return True
        elif s.distToShape(Part.Vertex(q))[0] < tol:
            return True
    return False


def free_faces(study, group, body):
    """The faces (edges in 2D) of the boundary of a cell object of group that face the free side: the Air Region
    around the copies, free objects and the copies of other groups. Names of geometry.global_shape(body), in order.
    The cell job holds nothing beyond them, so the real surface of the body there is these faces. A face counts when
    the points just beyond it lie inside the Air Region, a free object or a copy of another group, and not in another
    cell object of group or a copy of one of its cell objects (the body's own place excluded): those are seams and
    contacts, which the cell job meshes. Beyond a cut of the domain (a side of the Air Region, a symmetry line of a
    half model) lies nothing."""
    shape = geometry.global_shape(body)
    size = max(1.0, shape.BoundBox.DiagonalLength)
    tol, step = 1e-6 * size, 1e-4 * size
    box = shape.BoundBox
    box.enlarge(2 * step)

    def near(shapes):
        return [s for s in shapes if box.intersect(s.BoundBox)]

    mine = (box.XMin, box.YMin, box.ZMin, box.XMax, box.YMax, box.ZMax)
    own = []  # the cells of group in every copy, the body where it is drawn left out
    for cell in group.Cells:
        cell_shape = geometry.global_shape(cell)
        if cell_shape.isNull():  # _groups reports it
            continue
        cell_box = _box(cell_shape)
        for t in objects.group_transforms(group):
            here = max(abs(a - c) for a, c in zip(t, symmetry.ID)) < symmetry.TOL
            if not (here and cell.Name == body.Name) and symmetry.boxes_meet(symmetry.moved_box(t, cell_box), mine):
                own.append(cell_shape if here else cell_shape.transformed(App.Matrix(*t)))
    cells = {c.Name for c in objects.cell_bodies(study)}
    free = [b for b in geometry.study_geometry(study)[0] if b.Name not in cells and not objects.is_air(b)]
    beside = near(geometry.global_shape(b) for b in free)
    others = [g for g in objects.symmetric_groups(study) if g.Name != group.Name and not g.Shape.isNull()]
    beside += near(p for g in others for p, _ in _elements(g)[0])
    for air in objects.air_regions(study)[:1]:  # validation allows one
        try:
            beside += near([airshapes.air_shape(air, airshapes.study_plane(study))])
        except ValueError:  # _air reports it
            pass
    three = study.Dimension == "3D"
    if three:
        walls, elements = [f for s in shape.Solids for f in s.Faces], shape.Faces
    else:
        walls, elements = [e for f in shape.Faces for e in f.Edges], shape.Edges
    found = []
    for n, element in enumerate(elements, 1):
        if sum(element.isSame(w) for w in walls) != 1:  # inside the body, between two of its pieces
            continue
        points = _beyond(element, shape, step, tol)
        if points and all(not _inside(q, own, tol) and _inside(q, beside, tol) for q in points):
            found.append(f"{'Face' if three else 'Edge'}{n}")
    return found


def _air_gradings(study, included, r):
    """Air Grading items: each reference is an air (the Air Region, or a free object in a Study with Symmetric
    Groups), picked whole, and an air has one item, the first in the tree."""
    owners = {}  # air Name -> the first Air Grading that references it
    for g in objects.air_gradings(study):
        meshed = [(b, next((s for s in subs if s), "")) for b, subs in objects.subs_by_body(g) if b.Name in included]
        if not meshed:
            continue
        if g.GrowthDistance.Value <= 0:
            r.error(f"Air Grading {g.Label}: the growth distance must be greater than 0.", g)
        for b, sub in meshed:
            name = objects.display_name(b)
            if not objects.is_air(b) and not (objects.is_grouped(study) and _is_free(study, b)):
                r.error(
                    f"Air Grading {g.Label}: {name} is not an air. Pick the Air Region (or, in a Study with Symmetric"
                    " Groups, a free object that is air).",
                    g,
                    [(b, "")],
                )
            elif sub:
                r.error(f"Air Grading {g.Label}: pick the whole air, not {b.Label}.{sub}.", g, [(b, sub)])
            elif owners.setdefault(b.Name, g) is not g:
                r.error(
                    f"Air Grading {g.Label}: {name} already has Air Grading {owners[b.Name].Label}; one per air.",
                    g,
                    [(b, "")],
                )


def _is_free(study, body):
    """True for a body that no Symmetric Group holds as a cell object and that is not a group's drawing."""
    return any(p.startswith("free") for p in _mesh_part(study, body))


def _free_picks_on_copies(study, n, free, r):
    """Refine Near n in a Study with Symmetric Groups: the free model meshes without the copies, so the picks of free
    bodies and of the Air Region (free: [(body, subs)]) do not refine where they meet the copies. A whole body is
    refined only where it meets other free objects; a picked face or edge that lies on the copies is dropped from the
    free model there."""
    copies = None
    for body, subs in free:
        name = objects.display_name(body)
        if "" in subs:
            r.warning(
                f"Refine Near {n.Label}: in a Study with Symmetric Groups, {name} is refined only where it meets other"
                " free objects, not where it meets the copies of a Symmetric Group.",
                n,
            )
            continue
        shape = None
        for sub in subs:
            if not sub.startswith(("Face", "Edge")):
                continue
            if copies is None:  # worked out once, and only when a face or an edge is picked
                copies = [p for g in objects.symmetric_groups(study) if not g.Shape.isNull() for p in _elements(g)[0]]
            if shape is None:
                plane = airshapes.study_plane(study)
                try:
                    shape = airshapes.air_shape(body, plane) if objects.is_air(body) else geometry.global_shape(body)
                except ValueError:
                    continue  # _air reports it
            try:
                element = shape.getElement(sub)
            except Exception:  # a stale name: _links reports it
                continue
            if _lies_on(element, copies):
                r.warning(
                    f"Refine Near {n.Label}: {sub} of {name} lies on the copies of a Symmetric Group, which are meshed"
                    " apart; it is not refined there.",
                    n,
                    [(body, sub)],
                )


def _lies_on(element, copies):
    """True if a face or an edge shares an area (a length, for an edge) with the solids or faces copies, as
    _elements gives them. A pair OCC cannot compute counts as not lying on."""
    box = element.BoundBox
    tol = 1e-6 * max(1.0, box.DiagonalLength)
    box.enlarge(tol)
    for piece, piece_box in copies:
        if not box.intersect(piece_box):
            continue
        try:
            if element.distToShape(piece)[0] > tol:
                continue
            common = element.common(piece)
        except Part.OCCError:
            continue
        size = sum(f.Area for f in common.Faces) if element.ShapeType == "Face" else sum(e.Length for e in common.Edges)
        if size > tol:
            return True
    return False


def _mesh_part(study, body):
    """The meshes body is in with Symmetric Groups, as a set: its group for a cell object (one per group that holds
    it), "free fixed" or "free moving" for a free body by its side (the Air Region is on the fixed side), nothing for
    a group's drawing, which no job meshes."""
    if objects.is_air(body):
        return {"free fixed"}
    found = {f"group {g.Name}" for g in objects.symmetric_groups(study) if body in g.Cells}
    if found:
        return found
    if body in objects.symmetric_groups(study):
        return set()
    return {"free moving" if body.Name in sides.moving(study) else "free fixed"}


def thickness(shape):
    """About how thick a solid is, 4 V / A: the diameter of a long round wire."""
    return 4 * shape.Volume / shape.Area if shape.Area > 0 else 0.0


def thickness_2d(face):
    """About how thick a face is, 4 A / perimeter: the diameter of a round wire."""
    perimeter = sum(e.Length for e in face.Edges)
    return 4 * face.Area / perimeter if perimeter > 0 else 0.0


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


def _slides(study, bodies, r):
    """Sliding: an Air Region and Sliding Interfaces that cut it, interfaces that agree on the side of each piece of
    the air, no body across a sliding surface and a body on the moving side (as sides.moving finds it, from the same
    pieces of air)."""
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
    piece_side, disagreements = sides.piece_sides(cells, interfaces, surfaces, plane)
    for text, iface in disagreements:
        r.error(text, iface)
    unplaced, moving = False, False  # a body not in one cell; a body in a moving cell
    hint = ""
    if any(i.Kind != "Linear" for i in interfaces):
        hint = " Rotation is about the global Z axis; put the machine axis on Z."
    for body in bodies:
        shape = geometry.global_shape(body)
        measure = shape.Volume if plane == "3D" else shape.Area
        if airshapes.outside(shape, air_shape, plane) > 1e-6 * measure:
            unplaced = True
            continue  # _air reports a body outside the air
        k = airshapes.cell_of(shape, cells)
        if k is None:
            unplaced = True
            r.error(f"{body.Label} crosses a Sliding Interface." + hint, body, [(body, "")])
        elif piece_side[k] == "moving":
            moving = True
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
        if loose_pieces(geometry.body_shape(b)):
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
    edges = None if face is None else geometry.body_shape(body).getElement(face).Edges
    return [
        i
        for i, e in enumerate(geometry.body_shape(body).Edges, 1)
        if e.Length > 1e-9 and (edges is None or any(e.isSame(f) for f in edges))
    ]


def _on_face(body, face, vertex):
    v = geometry.body_shape(body).getElement(vertex)
    return any(v.isSame(f) for f in geometry.body_shape(body).getElement(face).Vertexes)


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


def _materials(study, r, known=None):
    """The mesh does not need materials, but the input file needs one for every body."""
    bodies = objects.bodies_without_material(study)
    if bodies:
        r.warning(
            "No material (the input file needs one for every body): "
            + ", ".join(objects.display_name(b) for b in bodies),
            None,
            [(b, "") for b in bodies],
        )
    for m in objects.materials(study):  # an assignment left on a body the Study does not mesh
        b = m.Body
        why = geometry.not_meshed(study, b, known) if b is not None and not getattr(m, "PartKey", "") else None
        text = geometry.not_meshed_text(1, b, *why, m=objects.display_name(m)) if why is not None else None
        if text:
            r.warning(text, m, [(b, "")])


def _links_not_bodies(study, meshed, r):
    """A Link the Study cannot mesh (an array, a link to a Part or Group, to a sketch) and no body is made from."""
    used = {name for b in meshed for name in geometry.inputs(b)} | geometry.link_tools(study.Document)
    for link in study.Document.Objects:
        if link.TypeId == "App::Link" and link.Name not in used and not geometry.is_excluded(study, link):
            if geometry.link_target(link) is None:
                r.warning(
                    f"{link.Label} is not meshed: a Link is meshed only when it links one body.", link, [(link, "")]
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
    on_interface = set()  # the free objects refused below as crossing or touching an interface
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
                on_interface.add(body.Name)
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
    for body in free if interfaces else ():  # sides.moving would take one on both sides for fixed
        if body.Name in on_interface:
            continue
        if sides.side_of(geometry.global_shape(body), interfaces[0], "3D" if three else plane) is None:
            r.error(
                f"Free object {objects.display_name(body)} has pieces on both sides of Sliding Interface"
                f" {interfaces[0].Label}: a free object is all on one side. Move the interface or split the object.",
                body,
                [(body, "")],
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
