"""Shared helpers of the catalogue Studies. The helpers of experiments/symmetric_rules/success_list.py are imported
here and used as they are; this file adds only what several sections need."""

import collections
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "symmetric_rules"))

import success_list as sl  # noqa: E402 - sets up the add-on paths and FreeCAD
from success_list import (  # noqa: E402, F401 - re-exported for the section modules
    App,
    DATA,
    MIRROR_X,
    MIRROR_Y,
    MIRROR_Z,
    P,
    Part,
    V,
    cut,
    disc,
    mirror,
    new_study,
    pie,
    polygon,
    rotate,
    sizes,
    winding,
)
from emsolution import objects  # noqa: E402, F401
from tests.freecad_addon import symcases  # noqa: E402
from tests.freecad_addon.symcases import extruded, sector  # noqa: E402, F401

RS, RI, RY, RO, RR = 28.75, 30.0, 42.0, 50.0, 25.0  # sliding radius, stator bore, slot bottom, yoke, rotor iron
SECTORS = ["A+", "C-", "B+", "A-", "C+", "B-"]


def make_group(study, name, cells, rules, mats, rows=None, side="Fixed"):
    """symcases.group with the rows and materials given by the position of the cell in cells: rows {index: change},
    mats [library material or None]."""
    by_row = {cells[i].Name: change for i, change in (rows or {}).items()}
    lib = {c.Name: m for c, m in zip(cells, mats) if m is not None}
    return symcases.group(study, name, cells, rules, by_row, side=side, lib=lib)


def table(names):
    return {"mode": "table", "table": list(names)}


def sliding(study, counts=None, radius=RS):
    """A Rotational Sliding Interface at radius with 120 or more divisions, a multiple of the cells around the
    circle on each side: counts, or from every group the turns of its rotations, doubled by each mirror."""
    if counts is None:
        counts = []
        for item in objects.symmetric_groups(study):
            n = 1
            for rule in json.loads(item.Rules):
                n *= 2 if rule["kind"] == "mirror" else rule["count"]
            counts.append(n)
    n = 1
    for c in counts:
        n = n * c // math.gcd(n, c)
    objects.make_sliding_interface(study, "Rotational", Radius=radius, Divisions=n * math.ceil(120 / n))


def outline(*points):
    """A face through the polar points (r, deg), in order and closed: an arc where the radius stays and the angle
    changes, a line otherwise."""
    area = sum(r1 * r1 * (a2 - a1) for (r1, a1), (r2, a2) in zip(points, points[1:] + points[:1]) if r1 == r2)
    if area < 0:  # a clockwise outline would make a face turned the other way: draw it counterclockwise
        points = points[::-1]
    edges = []
    for (r1, a1), (r2, a2) in zip(points, points[1:] + points[:1]):
        if abs(r1 - r2) < 1e-9 and abs(a1 - a2) > 1e-9:
            edges.append(Part.Arc(P(r1, a1), P(r1, (a1 + a2) / 2), P(r2, a2)).toShape())
        else:
            edges.append(Part.LineSegment(P(r1, a1), P(r2, a2)).toShape())
    return Part.Face(Part.Wire(edges))


def blanked(change, copies):
    """A row change (such as winding's) whose table has the names of the given copies emptied."""

    def edited(item, r):
        out = change(item, r)
        out["table"] = ["" if k in copies else n for k, n in enumerate(out["table"])]
        return out

    return edited


def distributed(doc, study, lib, slots, pole_pairs, span, name="Stator", gap=True, count=None, blank=None):
    """The two-layer stator of M2-15 (one slot pitch, the gap band at R 28.75 unless gap is False, left to a drawn
    ring) with the winding generator; count turns (default: all the slots). blank {"top": copies, "bottom": copies}
    empties those names of the tables."""
    pitch = 360 / slots
    turn = rotate(pitch, count or slots)
    cells = sl.stator_slot_2d(doc, pitch, RS, RI, RY, RO)
    mats = [lib["Air"], lib["Steel"], lib["Air"], lib["Copper"], lib["Copper"]]
    rows = {3: winding(turn, slots, pole_pairs, span, "top"), 4: winding(turn, slots, pole_pairs, span, "bottom")}
    for index, key in ((3, "top"), (4, "bottom")):
        if blank and key in blank:
            rows[index] = blanked(rows[index], blank[key])
    if not gap:
        doc.removeObject(cells[0].Name)
        cells, mats, rows = cells[1:], mats[1:], {i - 1: c for i, c in rows.items()}
    return make_group(study, name, cells, [turn], mats, rows)


def surface_rotor(doc, study, lib, poles, name="Rotor", side="Moving", band=True, magnet_row=None):
    """A half pole 0..180/poles of iron, a magnet on it (78 % of the half) and an air band to the sliding radius,
    mirrored at y = 0 and rotated; the two halves of a magnet are one part (or magnet_row)."""
    b = 180 / poles
    magnet = sector(RR, 27.5, 0, b * 0.78)
    cells = [symcases.feature(doc, "RotorIron", sector(8, RR, 0, b)), symcases.feature(doc, "Magnet", magnet)]
    mats = [lib["Steel"], lib["Steel"]]
    if band:
        cells.append(symcases.feature(doc, "RotorAir", cut(sector(RR, RS, 0, b), magnet)))
        mats.append(lib["Air"])
    row = magnet_row or {"mode": "across", "across": [0]}
    return make_group(study, name, cells, [MIRROR_Y, rotate(2 * b, poles)], mats, {1: row}, side)


def v_rotor(doc, study, lib, name="Rotor"):
    """The 4-pole V-magnet rotor of M2-15: a half pole 0..45 with one leg of the magnet, mirrored and rotated."""
    c, u = P(18.5, 19), V(math.cos(math.radians(58)), math.sin(math.radians(58)), 0)
    w = V(-u.y, u.x, 0)
    leg = polygon([c + u * sa * 4.5 + w * sb * 1.2 for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    cells = [
        symcases.feature(doc, "RotorAir", sector(RR, RS, 0, 45)),
        symcases.feature(doc, "RotorIron", cut(sector(8, RR, 0, 45), leg)),
        symcases.feature(doc, "Magnet", leg),
    ]
    mats = [lib["Air"], lib["Steel"], lib["Steel"]]
    return make_group(
        study, name, cells, [MIRROR_Y, rotate(90, 4)], mats, {2: {"mode": "across", "across": [0]}}, "Moving"
    )


def coil_sector(k, slots, pole_pairs):
    return ((k * pole_pairs * 360 + 30 * slots) % (360 * slots)) // (60 * slots)


# --- whole strands: skew is part of the drawn strand (spec 2, anti-goals) ----------------------------------------------


def frames(centre, z0, z1, n):
    """[(c, a, b)] at n + 1 even heights z0..z1 of the centre line centre(z): its point c at that height and the
    directions a and b in which the plane of the height cuts the tube round the line (c + a r cos f + b r sin f is r
    from the line). a and b come from a frame carried along the line (each start direction the last one made normal
    to the line, so it does not twist), slid along the line into the plane."""
    out, u = [], V(1, 0, 0)
    for i in range(n + 1):
        z = z0 + (z1 - z0) * i / n
        c, h = centre(z), (z1 - z0) / n / 10
        t = centre(z + h) - centre(z - h)
        t.normalize()
        u = u - t * u.dot(t)
        u.normalize()
        w = t.cross(u)
        out.append((c, u - t * (u.z / t.z), w - t * (w.z / t.z)))  # u and w slid along t into the plane of height z
    return out


def strand(centre, r, z0, z1, n=40, points=24):
    """A whole round strand of radius r about the centre line centre(z) (a Vector at height z) from z0 to z1: a ruled
    loft through n + 1 sections at even heights. Each section is where the plane of its height cuts the tube of radius
    r round the line (the circle normal to the line, slid along it into that plane: an ellipse, interpolated through
    points points), so the ends are flat at z0 and z1 and lie on the end planes of a wire's air, with no boolean on
    the loft (those fail on these surfaces). The sections start on a frame carried along the line (frames), so the
    loft's seam does not twist."""
    wires = []
    for c, a, b in frames(centre, z0, z1, n):
        angles = [2 * math.pi * k / points for k in range(points)]
        ring = [c + a * (r * math.cos(f)) + b * (r * math.sin(f)) for f in angles]
        curve = Part.BSplineCurve()
        curve.interpolate(ring, PeriodicFlag=True)
        wires.append(Part.Wire(curve.toShape()))
    out = Part.makeLoft(wires, True, True)
    assert len(out.Solids) == 1 and out.Solids[0].isValid(), "the strand is not one valid solid"
    return out.Solids[0]


def twist_line(rb, rho, a0, phi, psi, length):
    """The centre line of a strand of a twisted bundle, z 0..length: it sits rho from the bundle's axis at
    a0 + psi * z / length degrees (the strand's skew in the bundle), and the bundle's axis rb from the wire's axis,
    turned phi * z / length degrees about Z (the bundle's skew round the wire)."""

    def centre(z):
        f, g = math.radians(phi * z / length), math.radians(psi * z / length + a0)
        x, y = rb + rho * math.cos(g), rho * math.sin(g)
        return V(x * math.cos(f) - y * math.sin(f), x * math.sin(f) + y * math.cos(f), z)

    return centre


def twisted(rb, rho, a0, phi, psi, length, r, n=40):
    """The catalogue's whole strand of a twisted bundle (twist_line), z 0..length."""
    if rb == 0 and rho == 0:
        return Part.makeCylinder(r, length)
    return strand(twist_line(rb, rho, a0, phi, psi, length), r, 0, length, n)


# --- structured strands: an O-grid cross-section of 5 blocks ------------------------------------------------------------

ARC_POINTS = 6  # points along a quarter circle of an O-grid, less one


def _interpolated(points):
    """The B-spline through points at even parameters: two curves through the same points are the same curve."""
    curve = Part.BSplineCurve()
    curve.interpolate(points, Parameters=[i / (len(points) - 1) for i in range(len(points))])
    return curve


def _surface(grid):
    """The B-spline surface through grid[j][i] (section j, point i along it), interpolated at even parameters along
    the sections, then across them: its edges are the curves _interpolated gives through the grid's first and last
    rows and columns, so two surfaces built on one edge row of points meet exactly."""
    rows = [_interpolated(row) for row in grid]
    across = [_interpolated([row.getPole(i + 1) for row in rows]) for i in range(rows[0].NbPoles)]
    surface = Part.BSplineSurface()
    surface.buildFromPolesMultsKnots(
        [[c.getPole(j + 1) for j in range(c.NbPoles)] for c in across],
        rows[0].getMultiplicities(),
        across[0].getMultiplicities(),
        rows[0].getKnots(),
        across[0].getKnots(),
        False,
        False,
        rows[0].Degree,
        across[0].Degree,
    )
    return surface


def _ogrid_points(c, a, b, r, q):
    """One O-grid section about c (directions a and b, as frames gives them): ((sides, radials, arcs), corners), each
    of the 12 lines as its points: the square's 4 sides and the 4 radial lines from its corners (q from c, at 45° +
    k 90°) to the circle (r) as their two ends, the 4 quarter circles between those points as ARC_POINTS + 1 points;
    corners: the square's 4. Straight sides keep the surfaces through them simple, and the booleans on them fast."""

    def at(rad, f):
        return c + a * (rad * math.cos(f)) + b * (rad * math.sin(f))

    angles = [math.pi / 4 + k * math.pi / 2 for k in range(4)]
    square, circle = [at(q, f) for f in angles], [at(r, f) for f in angles]

    sides = [[square[k], square[(k + 1) % 4]] for k in range(4)]
    radials = [[square[k], circle[k]] for k in range(4)]
    arcs = [[at(r, f + math.pi / 2 * i / ARC_POINTS) for i in range(ARC_POINTS + 1)] for f in angles]
    return (sides, radials, arcs), square


def _ogrid_faces(lines):
    """The 5 faces of one O-grid section: (the square, [the 4 blocks with a curved side])."""
    sides, radials, arcs = [[_interpolated(p).toShape() for p in kind] for kind in lines]
    blocks = [Part.Face(Part.Wire([sides[k], radials[(k + 1) % 4], arcs[k], radials[k]])) for k in range(4)]
    return Part.Face(Part.Wire(sides)), blocks


def _ogrid_kinds(shape, corners, solid):
    """The kind of each edge of an O-grid, in order: "square" (a side of the square), "radial", "arc", or (solid)
    "length", along the strand. corners: the square's corners (at both ends of a strand)."""

    def corner(p):
        return any(p.distanceToPoint(c) < 1e-7 for c in corners)

    kinds = []
    for e in shape.Edges:
        p, s = e.Vertexes[0].Point, e.Vertexes[-1].Point
        kinds.append(
            "length" if solid and abs(p.z - s.z) > 1e-9 else ("arc", "radial", "square")[corner(p) + corner(s)]
        )
    return kinds


def ogrid(centre, r, z0, z1, n=24, q=0.55):
    """A whole round strand of radius r about the centre line centre(z) from z0 to z1, its sections as strand's (in
    the planes of their heights, on frames, flat ends at z0 and z1), cut into the 5 blocks of an O-grid: a square
    inside the circle (corners q r from the line) and 4 blocks with one curved side, the square's corners joined to
    the circle. Each side of a block is one surface through the n + 1 sections (_surface; a side two blocks share is
    one surface), each block a solid, the 5 fused so that the sides they share are one face. Not a ruled loft: that
    gives a block a face per section and side, and a structured block needs 5 or 6 faces. Returns (shape, kinds): the
    compound of the 5 solids and the kind of each of its edges (_ogrid_kinds)."""
    sections = [_ogrid_points(c, a, b, r, q * r) for c, a, b in frames(centre, z0, z1, n)]
    square, radial, arc = [
        [Part.Face(_surface([s[0][kind][k] for s in sections])) for k in range(4)] for kind in range(3)
    ]
    (c0, ends0), (c1, ends1) = _ogrid_faces(sections[0][0]), _ogrid_faces(sections[-1][0])
    blocks = [[c0, c1, *square]]
    blocks += [[ends0[k], ends1[k], square[k], radial[(k + 1) % 4], arc[k], radial[k]] for k in range(4)]
    solids = []
    for faces in blocks:
        sewn = Part.Compound(faces).copy()
        sewn.sewShape()
        assert len(sewn.Shells) == 1 and sewn.Shells[0].isClosed(), "an O-grid block is not a closed shell"
        solid = Part.Solid(sewn.Shells[0])
        if solid.Volume < 0:
            solid.reverse()
        assert solid.isValid(), "an O-grid block is not a valid solid"
        solids.append(solid)
    out = solids[0].generalFuse(solids[1:])[0]
    assert len(out.Solids) == 5 and len(out.Faces) == 22 and out.isValid(), "the O-grid blocks did not fuse"
    return out, _ogrid_kinds(out, sections[0][1] + sections[-1][1], True)


def ogrid_disc(centre, r, q=0.55):
    """The O-grid of a disc of radius r about the point centre in the XY plane (2D), as ogrid's section: 5 faces fused
    so that the edges they share are one. Returns (shape, kinds) as ogrid."""
    lines, corners = _ogrid_points(centre, V(1, 0, 0), V(0, 1, 0), r, q * r)
    middle, blocks = _ogrid_faces(lines)
    out = middle.generalFuse(blocks)[0]
    assert len(out.Faces) == 5 and len(out.Edges) == 12, "the O-grid blocks did not fuse"
    return out, _ogrid_kinds(out, corners, False)


def structure(study, body, kinds, counts, label=None):
    """Make body structured and recombined: a Transfinite Body and a Recombine on it, and Transfinite Edges on all its
    edges, counts[kind] elements on the edges of that kind (kinds: one per edge of body.Shape, in order)."""
    by = {}
    for i, kind in enumerate(kinds, 1):
        by.setdefault(counts[kind], []).append((body, f"Edge{i}"))
    for n, edges in sorted(by.items()):
        objects.make_transfinite_edges(study, n, edges).Label = f"{label or body.Label} {n}"
    objects.make_transfinite_body(study, [body])
    objects.make_recombine(study, [body])


# --- the check of a structured row ----------------------------------------------------------------------------------


def types_by_part(folder):
    """[(part name, {element type name: count})] of the mesh files in folder (the fixed and the moving mesh), one per
    physical group of their highest dimension (one per part: two parts may have one name, A+ and A- are both A_)."""
    import gmsh

    from tests.freecad_addon.meshreport import TYPE_NAMES

    out = []
    for name in ("pre_geom.msh", "pre_geom2D.msh", "rotor_mesh.msh", "rotor_mesh2D.msh"):
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            continue
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(path)
            top = max(d for d, _ in gmsh.model.getPhysicalGroups())
            for d, tag in gmsh.model.getPhysicalGroups(top):
                types = collections.Counter()
                for entity in gmsh.model.getEntitiesForPhysicalGroup(d, tag):
                    for etype, tags, _ in zip(*gmsh.model.mesh.getElements(d, entity)):
                        types[TYPE_NAMES.get(int(etype), f"type {etype}")] += len(tags)
                out.append((gmsh.model.getPhysicalName(d, tag), types))
        finally:
            gmsh.finalize()
    return out


class Structured:
    """The check of a structured row. Before meshing (called on the built Study): each cut cell object named in whole
    (by Label) has several faces or solids and is one row of its group, so its blocks are one part (or one per copy,
    as its mode says), not a part per block. After meshing (after, on the folder of the mesh files): every part of
    the cell objects in kinds ({Label: "quadrangles" or "hexahedra"}) holds that element type only. Both give (ok,
    text); after's text lists the element types of every cell object's parts and of every free object."""

    def __init__(self, kinds, whole=()):
        self.kinds, self.whole, self.cell_of = dict(kinds), tuple(whole), {}

    def __call__(self, study):
        self.cell_of, rows = {}, {}
        for item in objects.symmetric_groups(study):
            for row in objects.rows_of(item):
                cell = study.Document.getObject(row["cell"])
                rows.setdefault(cell.Label, []).append(row)
                for part in objects.row_parts(item, row):  # named in the mesh as its Material is
                    self.cell_of.setdefault(objects.clean(part), set()).add(cell.Label)
        problems, said = [], []
        for label in self.whole:
            (cell,) = study.Document.getObjectsByLabel(label)
            blocks = len(cell.Shape.Solids if study.Dimension == "3D" else cell.Shape.Faces)
            mine = rows.get(label, [])
            if blocks < 2 or len(mine) != 1 or not objects.is_whole(mine[0]):
                problems.append(f"{label}: {blocks} blocks, {len(mine)} rows")
            else:
                said.append(f"{label}: {blocks} blocks, one row")
        missing = [label for label in self.kinds if label not in rows]
        problems += [f"{label}: no row" for label in missing]
        return not problems, "; ".join(problems or said or ["no cut cell object named"])

    def after(self, folder):
        found = types_by_part(folder)
        by_cell = {}  # the cell Labels of a part (or a free object's name) -> [parts, Counter]
        problems = []
        meshed = set()
        for part, types in sorted(found, key=lambda x: x[0]):
            cells = sorted(self.cell_of.get(part, {part}))
            meshed.update(cells)
            entry = by_cell.setdefault(" + ".join(cells), [0, collections.Counter()])
            entry[0] += 1
            entry[1].update(types)
            wants = {self.kinds.get(c) for c in cells}  # a part of structured cells only: that type only
            if len(wants) == 1 and None not in wants and set(types) != wants:
                found_types = ", ".join(f"{k} {v}" for k, v in sorted(types.items()))
                problems.append(f"{part} is {found_types}, not {wants.pop()} only")
        problems += [f"{label}: no part in the mesh" for label in self.kinds if label not in meshed]
        listing = "; ".join(
            f"{cell} ({n} part{'s' * (n > 1)}): " + ", ".join(f"{k} {v}" for k, v in sorted(t.items()))
            for cell, (n, t) in by_cell.items()
        )
        return not problems, ("; ".join(problems) + " | " if problems else "") + "by part: " + listing


def wire_air(study, lib, radius, length, size=None, z0=0.0):
    """The drawn air of a wire: a cylinder of radius about Z from z0 over length, the Custom shape of the Study's Air
    Region (it gives way to the strands). Strands that run the whole length end on its end planes."""
    air = symcases.add_air_region(study, lib["Air"], shape=Part.makeCylinder(radius, length, V(0, 0, z0)))
    if size:
        sizes(study, [(air, size)])
    return air
