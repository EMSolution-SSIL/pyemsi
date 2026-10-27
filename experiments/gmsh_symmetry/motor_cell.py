"""Shared pieces of the symmetry experiments: a toy 12-slot / 8-pole motor, the rule that numbers the physical groups of
every copy, mesh copying through the gmsh API, and checks on the result.

The motor (radii in mm, angles in degrees, all measured from the x axis):

    shaft hole        r < 10
    rotor iron        10 < r < 30
    magnets           30 < r < 34, 8 poles centred at 22.5 + 45 i, each 36 deg wide
    air               30 < r < 36 (around the magnets, and the air gap)
    stator iron       36 < r < 60
    coils (slots)     37 < r < 50, 12 slots centred at 15 + 30 j, each 10 deg wide

gcd(12 slots, 8 poles) = 4, so the machine repeats every 90 deg. Inside that, the geometry is also mirror symmetric
about the 45 deg line. The smallest piece to mesh (the "cell") is therefore 0..45 deg: 1 magnet and 1.5 slots.
"""

import math
from collections import Counter

import gmsh

R_SHAFT, R_ROTOR, R_MAGNET, R_GAP, R_SLOT_IN, R_SLOT_OUT, R_OUT = 10, 30, 34, 36, 37, 50, 60
POLES, SLOTS = 8, 12

# --- geometry ---------------------------------------------------------------------------------------------------


def _sector(r1, r2, a1, a2, height):
    """Annular sector r1..r2, a1..a2 deg, as an OCC surface (or a volume 0..height when height is given)."""
    occ = gmsh.model.occ
    ring = occ.addDisk(0, 0, 0, r2, r2)
    if r1 > 0:
        ring = occ.cut([(2, ring)], [(2, occ.addDisk(0, 0, 0, r1, r1))])[0][0][1]
    big = 2 * r2
    pts = [occ.addPoint(0, 0, 0)]
    for a in (a1, (a1 + a2) / 2, a2):
        pts.append(occ.addPoint(big * math.cos(math.radians(a)), big * math.sin(math.radians(a)), 0))
    lines = [occ.addLine(pts[k], pts[(k + 1) % 4]) for k in range(4)]
    wedge = occ.addPlaneSurface([occ.addCurveLoop(lines)])
    surf = occ.intersect([(2, ring)], [(2, wedge)])[0]
    return occ.extrude(surf, 0, 0, height)[1:2] if height else surf


def build_cell(span=45, height=None):
    """Fragmented geometry of 0..span deg of the motor: 2D surfaces, or volumes extruded 0..height.
    Returns {dim tag: base name}, where base name is rotor_iron, stator_iron, air, magnet or coil."""
    parts, names = [], []
    for r1, r2, base in ((R_SHAFT, R_ROTOR, "rotor_iron"), (R_ROTOR, R_GAP, "air"), (R_GAP, R_OUT, "stator_iron")):
        parts += _sector(r1, r2, 0, span, height)
        names.append(base)
    inserts = (
        (_centres(POLES, 22.5), 36, R_ROTOR, R_MAGNET, "magnet"),
        (_centres(SLOTS, 15), 10, R_SLOT_IN, R_SLOT_OUT, "coil"),
    )
    for centres, width, r1, r2, base in inserts:
        for c in centres:
            a1, a2 = max(c - width / 2, 0), min(c + width / 2, span)
            if a2 > a1:
                parts += _sector(r1, r2, a1, a2, height)
                names.append(base)
    _, children = gmsh.model.occ.fragment(parts, [])
    gmsh.model.occ.synchronize()
    regions = {}
    for base, kids in zip(names, children):  # inserts come last, so they win over the ring they sit in
        regions.update({dt: base for dt in kids})
    return regions


def _centres(count, first):
    return [first + 360 * k / count for k in range(count)]


def outer_boundary(dim):
    """Entities of dimension dim - 1 lying on the stator outside (r = R_OUT): every corner point is on it."""
    out = []
    for _, t in gmsh.model.getEntities(dim - 1):
        corners = gmsh.model.getBoundary([(dim - 1, t)], combined=False, oriented=False, recursive=True)
        if all(abs(math.hypot(*gmsh.model.getValue(0, p, [])[:2]) - R_OUT) < 1e-6 for _, p in corners):
            out.append(t)
    return out


def refine_air_gap(size):
    """Smaller elements at the points of the air gap region."""
    for _, p in gmsh.model.getEntities(0):
        x, y, _ = gmsh.model.getValue(0, p, [])
        if R_ROTOR - 1e-6 < math.hypot(x, y) < R_GAP + 1e-6:
            gmsh.model.mesh.setSize([(0, p)], size)


# --- the numbering rule ----------------------------------------------------------------------------------------

SHARED = {"rotor_iron": 1, "stator_iron": 2, "air": 3, "outer": 10}


def physical(base, x, y):
    """(id, name) of the physical group for region `base` of one copy, whose centre has moved to (x, y).

    Regions that are the same everywhere (iron, air, outer boundary) keep one id in every copy. Regions whose role
    changes from copy to copy (a magnet's polarity, a slot's phase) get their id from *where the copy landed*,
    not from which copy it is: the pole or slot number follows from the angle. This works the same for rotated and
    for mirrored copies, and for halves of a slot cut by a symmetry line (both halves land on the same slot)."""
    if base in SHARED:
        return SHARED[base], base
    a = math.degrees(math.atan2(y, x)) % 360
    if base == "magnet":
        pole = int(a // (360 / POLES))
        return 101 + pole, f"magnet_p{pole}_{'NS'[pole % 2]}"
    if base == "coil":
        slot = round((a - 15) / (360 / SLOTS)) % SLOTS
        return 201 + slot, f"coil_s{slot:02d}_{'UVW'[slot % 3]}"  # illustrative phases; a real winding table goes here
    raise ValueError(base)


# --- transforms (4x4 affine, row major, as gmsh wants them) -----------------------------------------------------


def rotation(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def mirror_line(deg):
    """Mirror about the line through the origin at angle deg (a plane containing the z axis, in 3D)."""
    c, s = math.cos(math.radians(2 * deg)), math.sin(math.radians(2 * deg))
    return [c, s, 0, 0, s, -c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


MIRROR_Z = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1]


def compose(*ms):
    """compose(A, B) applies B first, then A."""
    out = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    for m in ms:
        out = [sum(out[4 * i + k] * m[4 * k + j] for k in range(4)) for i in range(4) for j in range(4)]
    return out


def apply(m, p):
    return [sum(m[4 * i + k] * v for k, v in enumerate((*p, 1))) for i in range(3)]


def det(m):
    a = m
    return (
        a[0] * (a[5] * a[10] - a[6] * a[9]) - a[1] * (a[4] * a[10] - a[6] * a[8]) + a[2] * (a[4] * a[9] - a[5] * a[8])
    )


# --- approach B: copy a finished mesh ---------------------------------------------------------------------------


def copy_mesh(transforms, name, label=None):
    """Make a new model `name` holding one transformed copy of the current (meshed) model per transform.

    Every physical group of the current model must be named by its base name. Each copy of a group becomes a
    discrete entity, joined to the physical group that `physical()` gives for where it landed. Mirrored copies
    (det < 0) get their elements reversed, and the nodes that copies share on the cut lines are merged.

    label(dim, cell entity, copy index) -> (id, name), when given, replaces `physical()`."""
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
    groups = []  # one per entity of a physical group: (dim, base name, {element type: node tags}, nodes used, centre)
    for dim, ptag in sorted(gmsh.model.getPhysicalGroups(), reverse=True):  # volumes own their nodes first
        for e in gmsh.model.getEntitiesForPhysicalGroup(dim, ptag):  # per entity: the 2 coils of the cell land apart
            conn = {}
            for typ, nodes in zip(*gmsh.model.mesh.getElements(dim, e)[::2]):
                conn.setdefault(int(typ), []).extend(int(n) for n in nodes)
            used = sorted({n for nodes in conn.values() for n in nodes})
            centre = [sum(xyz[n][i] for n in used) / len(used) for i in range(3)]
            groups.append((dim, e, gmsh.model.getPhysicalName(dim, ptag), conn, used, centre))
    shift = int(max(tags))

    gmsh.model.add(name)
    members, mirrored, entity = {}, [], 0
    for c, m in enumerate(transforms):
        owned = set()
        for dim, e, base, conn, used, centre in groups:
            entity += 1
            gmsh.model.addDiscreteEntity(dim, entity)
            mine = [n for n in used if n not in owned]
            owned.update(mine)
            moved = [v for n in mine for v in apply(m, xyz[n])]
            gmsh.model.mesh.addNodes(dim, entity, [n + c * shift for n in mine], moved)
            for typ, nodes in conn.items():
                gmsh.model.mesh.addElementsByType(entity, typ, [], [n + c * shift for n in nodes])
            pid, pname = label(dim, e, c) if label else physical(base, *apply(m, centre)[:2])
            members.setdefault((dim, pid), [pname, []])[1].append(entity)
            if det(m) < 0:
                mirrored.append((dim, entity))
    for (dim, pid), (pname, ents) in sorted(members.items()):
        gmsh.model.addPhysicalGroup(dim, ents, pid, name=pname)
    if mirrored:
        gmsh.model.mesh.reverse(mirrored)
    gmsh.model.mesh.removeDuplicateNodes()
    gmsh.model.mesh.renumberNodes()
    gmsh.model.mesh.renumberElements()


# --- checks -----------------------------------------------------------------------------------------------------


def report(title, zmax=None, radii=(R_SHAFT, R_OUT)):
    """Print node / element counts per physical group, inverted elements, and non-conforming facets: a facet
    (edge in 2D, face in 3D) used by only one element that is not on the true outside of the model means two
    neighbouring copies did not share their nodes there."""
    dim = gmsh.model.getDimension()
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
    print(f"\n== {title}: {len(tags)} nodes")
    for d, ptag in gmsh.model.getPhysicalGroups():
        n = sum(
            len(e)
            for ent in gmsh.model.getEntitiesForPhysicalGroup(d, ptag)
            for e in gmsh.model.mesh.getElements(d, ent)[1]
        )
        print(f"   dim {d}  id {ptag:4d}  {gmsh.model.getPhysicalName(d, ptag):18s} {n:7d} elements")
    facets, inverted, kinds = Counter(), 0, []
    for typ in gmsh.model.mesh.getElementTypes(dim):
        etags, _ = gmsh.model.mesh.getElementsByType(typ)
        kinds.append(f"{len(etags)} {gmsh.model.mesh.getElementProperties(typ)[0]}")
        inverted += sum(q < 0 for q in gmsh.model.mesh.getElementQualities(etags, "minSJ"))
        if dim == 2:
            parts = [(gmsh.model.mesh.getElementEdgeNodes(typ), 2)]
        else:  # triangle and quadrangle faces; a type without one of them gives nothing
            parts = []
            for per in (3, 4):
                try:
                    parts.append((gmsh.model.mesh.getElementFaceNodes(typ, per), per))
                except Exception:
                    pass
        for fn, per in parts:
            facets.update(tuple(sorted(int(n) for n in fn[k : k + per])) for k in range(0, len(fn), per))
    print(f"   element types: {', '.join(kinds)}")

    def outside(n):
        x, y, z = xyz[n]
        r = math.hypot(x, y)
        return any(abs(r - R) < 1e-6 for R in radii) or (zmax is not None and abs(abs(z) - zmax) < 1e-6)

    loose = [f for f, k in facets.items() if k == 1 and not all(outside(n) for n in f)]
    print(f"   inverted elements: {inverted}   non-conforming facets inside the model: {len(loose)}")
