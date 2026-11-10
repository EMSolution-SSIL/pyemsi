"""Shared helpers of the catalogue Studies. The helpers of experiments/symmetric_rules/success_list.py are imported
here and used as they are; this file adds only what several sections need."""

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


def strand(centre, r, z0, z1, n=40, points=24):
    """A whole round strand of radius r about the centre line centre(z) (a Vector at height z) from z0 to z1: a ruled
    loft through n + 1 sections at even heights. Each section is where the plane of its height cuts the tube of radius
    r round the line (the circle normal to the line, slid along it into that plane: an ellipse, interpolated through
    points points), so the ends are flat at z0 and z1 and lie on the end planes of a wire's air, with no boolean on
    the loft (those fail on these surfaces). The sections start on a frame carried along the line (each start direction
    the last one made normal to the line), so the loft's seam does not twist."""
    wires, u = [], V(1, 0, 0)
    for i in range(n + 1):
        z = z0 + (z1 - z0) * i / n
        c, h = centre(z), (z1 - z0) / n / 10
        t = centre(z + h) - centre(z - h)
        t.normalize()
        u = u - t * u.dot(t)
        u.normalize()
        w = t.cross(u)
        a, b = u - t * (u.z / t.z), w - t * (w.z / t.z)  # u and w slid along t into the plane of height z
        angles = [2 * math.pi * k / points for k in range(points)]
        ring = [c + a * (r * math.cos(f)) + b * (r * math.sin(f)) for f in angles]
        curve = Part.BSplineCurve()
        curve.interpolate(ring, PeriodicFlag=True)
        wires.append(Part.Wire(curve.toShape()))
    out = Part.makeLoft(wires, True, True)
    assert len(out.Solids) == 1 and out.Solids[0].isValid(), "the strand is not one valid solid"
    return out.Solids[0]


def twisted(rb, rho, a0, phi, psi, length, r, n=40):
    """The catalogue's whole strand of a twisted bundle, z 0..length: its centre sits rho from the bundle's axis at
    a0 + psi * z / length degrees (the strand's skew in the bundle), and the bundle's axis rb from the wire's axis,
    turned phi * z / length degrees about Z (the bundle's skew round the wire)."""
    if rb == 0 and rho == 0:
        return Part.makeCylinder(r, length)

    def centre(z):
        f, g = math.radians(phi * z / length), math.radians(psi * z / length + a0)
        x, y = rb + rho * math.cos(g), rho * math.sin(g)
        return V(x * math.cos(f) - y * math.sin(f), x * math.sin(f) + y * math.cos(f), z)

    return strand(centre, r, 0, length, n)


def wire_air(study, lib, radius, length, size=None, z0=0.0):
    """The drawn air of a wire: a cylinder of radius about Z from z0 over length, in the Main geometry (free air, spec
    4.4). Strands that run the whole length end on its end planes."""
    air = symcases.add_free(study, "FreeAir", Part.makeCylinder(radius, length, V(0, 0, z0)), lib["Air"])
    if size:
        sizes(study, [(air, size)])
    return air
