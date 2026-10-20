"""Study validation: every problem at once, for the Validate command, the Study panel and Run Mesh.
Errors stop the mesh; warnings do not. No GUI code here."""

from dataclasses import dataclass, field

from . import geometry, objects

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
    bodies, _, setup_errors = geometry.setup(study)
    for text in setup_errors:
        r.error(text)
    bodies = list({b.Name: b for b in bodies}.values())  # main geometry order
    included = {b.Name for b in bodies}
    _skipped_picks(study, r)
    _links(study, included, r)
    _settings(study, included, r)
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
        outside = [(b, subs) for b, subs in by_body if b.Name not in included]
        if outside:  # kept on purpose, e.g. to mesh only part of a model; they just do not reach this mesh
            r.warning(
                f"{kind} {item.Label} is not used for {', '.join(b.Label for b, _ in outside)}:"
                " not in the main geometry.",
                item,
                [(b, s) for b, subs in outside for s in subs],
            )
        for b, subs in by_body:
            if b.Name not in included:
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
            "No material (the input file needs one for every body): " + ", ".join(b.Label for b in bodies),
            None,
            [(b, "") for b in bodies],
        )
