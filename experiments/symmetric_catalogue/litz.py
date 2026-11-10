"""Litz wires L-01 to L-13: whole strands, no slices. A twisted strand is one whole object copied by rotation about the
wire axis; its skews are part of the drawn strand (common.twisted, a ruled loft through circles normal to its centre
line). Each wire is in a drawn air cylinder; the strands run its whole length and end on its end planes (spec 4.4).
A straight centre strand is a group of its own with no rules (spec 4.1). L-06 and L-07 are the success list's, built
from data/double_skew_opposite.brep. L-12 is the one 2D case. CASES lists (id, builder, expected) in catalogue
order."""

import math

from common import (
    P,
    Part,
    RI,
    RO,
    RS,
    RY,
    V,
    cut,
    disc,
    make_group,
    new_study,
    rotate,
    sector,
    sizes,
    sl,
    sliding,
    strand,
    surface_rotor,
    symcases,
    twisted,
    winding,
    wire_air,
)

EACH = {"mode": "each"}
LENGTH, SR = 30.0, 0.5  # the catalogue's wire length and strand radius


def wire_study(name, size=1.0):
    doc, study = new_study(name, "3D", "No movement", size)
    return doc, study, symcases.libraries(study)


def strands(doc, name, solids):
    return [symcases.feature(doc, f"{name}{k + 1}" if len(solids) > 1 else name, s) for k, s in enumerate(solids)]


def layer(study, lib, name, cells, rules, rows=None, size=0.4):
    """A group of whole strands (Copper), each copy its own part unless rows say otherwise; size on every strand."""
    make_group(study, name, cells, rules, [lib["Copper"]] * len(cells), rows or {i: EACH for i in range(len(cells))})
    sizes(study, [(c, size) for c in cells])


def centre(doc, study, lib, length=LENGTH, rows=None):
    """The straight strand on the axis: a group with no rules."""
    layer(study, lib, "Centre", strands(doc, "CentreStrand", [twisted(0, 0, 0, 0, 0, length, SR)]), [], rows or {})


# --- L-01: the user's litz1 model ----------------------------------------------------------------------------------------


def l_01():
    """Helix radius 1.2, pitch 10, height 12, strand radius 0.45 (read from the user's file), Rotate Z 60° x 6, each
    strand its own part."""
    doc, study, lib = wire_study("L_01")
    pitch, height = 10.0, 12.0
    helix = strand(
        lambda z: V(1.2 * math.cos(2 * math.pi * z / pitch), 1.2 * math.sin(2 * math.pi * z / pitch), z),
        0.45,
        0,
        height,
        48,
    )
    layer(study, lib, "Strands", strands(doc, "HelicalStrand", [helix]), [rotate(60, 6)], size=0.3)
    wire_air(study, lib, 3.5, height)
    return study


# --- L-02 to L-05: concentric layers ---------------------------------------------------------------------------------------


def layered(name, layers, air):
    """A centre strand and layers [(radius, twist over the length, strands in the layer)], each layer a group of its
    own with one whole strand, Rotate Z 360/n x n."""
    doc, study, lib = wire_study(name)
    centre(doc, study, lib)
    for k, (rho, phi, n) in enumerate(layers, 1):
        cells = strands(doc, f"Layer{k}Strand", [twisted(0, rho, 0, phi, 0, LENGTH, SR)])
        layer(study, lib, f"Layer {k}", cells, [rotate(360 / n, n)])
    wire_air(study, lib, air, LENGTH)
    return study


def l_02():
    """Seven strands: the centre straight, six twisted half a turn over the length."""
    return layered("L_02", [(1.1, 180, 6)], 3.5)


def l_03():
    """19 strands in two layers, same lay direction: layer 2 has its own rule (Rotate Z 30° x 12)."""
    return layered("L_03", [(1.1, 180, 6), (2.2, 180, 12)], 4.5)


def l_04():
    """37 strands, layers twisted in alternating directions, so the strands of neighbouring layers cross."""
    return layered("L_04", [(1.1, 180, 6), (2.2, -180, 12), (3.3, 180, 18)], 5.5)


def l_05():
    """Odd lay, 1 + 5 + 11: 5 and 11 have no common repeat, and need none."""
    return layered("L_05", [(1.1, 180, 5), (2.3, 180, 11)], 4.5)


# --- L-13 and L-08: double skew --------------------------------------------------------------------------------------------


def bundle_strands(rb, phi, psi):
    """The seven whole strands of a bundle rb from the axis: its centre strand and six round it 1.2 from the bundle's
    axis; the bundle turns phi over the length round the wire, the strands psi round the bundle's axis."""
    return [twisted(rb, rho, a0, phi, psi, LENGTH, SR) for rho, a0 in [(0, 0)] + [(1.2, 60 * k) for k in range(6)]]


def l_13():
    """L-06's 7 x 7 wire with both skews the same way (strands 240° round their bundle, bundles 90° round the wire). The
    straight centre strand is a group with no rules; the ring strand of the centre bundle and the 7 strands of one
    outer bundle (3.6 from the axis) are the cells of Rotate Z 60° x 6, each strand its own part."""
    doc, study, lib = wire_study("L_13")
    centre(doc, study, lib)
    ring = twisted(0, 1.2, 0, 90, 240, LENGTH, SR)
    cells = strands(doc, "RingStrand", [ring]) + strands(doc, "BundleStrand", bundle_strands(3.6, 90, 240))
    layer(study, lib, "Strands", cells, [rotate(60, 6)])
    wire_air(study, lib, 7.5, LENGTH)
    return study


def l_08():
    """Five twisted bundles of seven (3.0 from the axis, the skews as L-06's), no centre bundle: the 7 strands of one
    bundle are the cells of Rotate Z 72° x 5, each strand its own part."""
    doc, study, lib = wire_study("L_08")
    layer(study, lib, "Bundles", strands(doc, "BundleStrand", bundle_strands(3.0, 90, -240)), [rotate(72, 5)])
    wire_air(study, lib, 6.5, LENGTH)
    return study


# --- L-09: rectangular transposed bundle (Roebel) -------------------------------------------------------------------------


def rounded_rectangle(s, a=4.0, b=1.6, c=1.0):
    """The point at arc length s (any, taken round) on a rectangle 2a x 2b with corners of radius c, centred at the
    origin, counterclockwise from (a, -b + c)."""
    ax, by = a - c, b - c
    q = math.pi * c / 2
    pieces = [
        (2 * by, lambda t: (a, -by + 2 * by * t)),
        (q, lambda t: (ax + c * math.cos(t * math.pi / 2), by + c * math.sin(t * math.pi / 2))),
        (2 * ax, lambda t: (ax - 2 * ax * t, b)),
        (q, lambda t: (-ax - c * math.sin(t * math.pi / 2), by + c * math.cos(t * math.pi / 2))),
        (2 * by, lambda t: (-a, by - 2 * by * t)),
        (q, lambda t: (-ax - c * math.cos(t * math.pi / 2), -by - c * math.sin(t * math.pi / 2))),
        (2 * ax, lambda t: (-ax + 2 * ax * t, -b)),
        (q, lambda t: (ax + c * math.sin(t * math.pi / 2), -by - c * math.cos(t * math.pi / 2))),
    ]
    s %= sum(p[0] for p in pieces)
    for length, at in pieces:
        if s <= length:
            return at(s / length)
        s -= length
    return pieces[-1][1](1.0)


def l_09():
    """Ten strands (R 0.7) that each walk once round a rounded rectangle (8 x 3.2, corners R 1) over the length, a
    tenth of the way apart, so every strand takes every place. A rectangle has only the 180° turn: the cell is five
    whole strands, Rotate Z 180° x 2, each strand its own part."""
    doc, study, lib = wire_study("L_09")
    total = 2 * (2 * 3.0 + 2 * 0.6) + 2 * math.pi * 1.0

    def walk(k):
        return lambda z: V(*rounded_rectangle(total * (k / 10 + z / LENGTH)), z)

    cells = strands(doc, "Strand", [strand(walk(k), 0.7, 0, LENGTH, 40) for k in range(5)])
    layer(study, lib, "Bundle", cells, [rotate(180, 2)], size=0.5)
    wire_air(study, lib, 6.5, LENGTH)
    return study


# --- L-10: strands joined at terminal plates ------------------------------------------------------------------------------


def l_10():
    """L-02's wire between two terminal plates (R 2.2, 3 thick) at its ends: the strands end on the plates. Plates and
    air are free objects; the air (R 5, z -6..36) is drawn with the plates cut out of it, since free objects may only
    touch. The plates are Copper where the catalogue colours them iron: they are the terminals that join the strands
    and carry the current (the excitation goes on them), a conductor, not a core."""
    doc, study, lib = wire_study("L_10")
    centre(doc, study, lib)
    layer(study, lib, "Wire", strands(doc, "RingStrand", [twisted(0, 1.1, 0, 180, 0, LENGTH, SR)]), [rotate(60, 6)])
    plates = [Part.makeCylinder(2.2, 3, V(0, 0, -3)), Part.makeCylinder(2.2, 3, V(0, 0, LENGTH))]
    for k, plate in enumerate(plates):
        symcases.add_free(study, f"Plate{k + 1}", plate, lib["Copper"])
    air = Part.makeCylinder(5, LENGTH + 12, V(0, 0, -6)).cut(Part.makeCompound(plates))
    sizes(study, [(symcases.add_free(study, "FreeAir", air.Solids[0], lib["Air"]), 1.0)])
    return study


# --- L-11: twisted segmented (Milliken) conductor ---------------------------------------------------------------------------


def l_11():
    """Six sectors (R 1.2..5.4, 1.5..58.5°), each twisted 60° over the length: one whole segment (a ruled loft through
    its turned sections), Rotate Z 60° x 6, each segment its own part."""
    doc, study, lib = wire_study("L_11")
    n = 20
    sections = [
        sector(1.2, 5.4, 1.5 + 60 * s / n, 58.5 + 60 * s / n).OuterWire.translated(V(0, 0, LENGTH * s / n))
        for s in range(n + 1)
    ]
    segment = Part.makeLoft(sections, True, True)
    cells = strands(doc, "Segment", [segment])
    layer(study, lib, "Conductor", cells, [rotate(60, 6)], size=0.6)
    wire_air(study, lib, 7, LENGTH)
    return study


# --- L-12: Litz strands in the slots of a distributed winding (2D) ---------------------------------------------------------


def l_12():
    """24 slots, 2 pole pairs, coil span 5, a cross-section: one slot pitch (15°) with its gap band, iron, slot air and
    eight strands (R 0.85), four of the top layer and four of the bottom, Rotate Z 15° x 24. The winding generator names
    the strands of a layer: 6 parts. The rotor (4 surface magnets) slides at R 28.75."""
    doc, study = new_study("L_12", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    pitch, th = 15.0, 3.0
    slot = sector(RI, RY, th, pitch - th)
    wires = [
        disc(P(r, pitch / 2 + side * math.degrees(1.0 / r)), 0.85) for r in (33.1, 35.2, 38.0, 40.1) for side in (-1, 1)
    ]
    cells = [
        symcases.feature(doc, "Gap", sector(RS, RI, 0, pitch)),
        symcases.feature(doc, "Iron", cut(sector(RI, RO, 0, pitch), slot)),
        symcases.feature(doc, "SlotAir", cut(slot, *wires)),
        *[symcases.feature(doc, f"Strand{k + 1}", w) for k, w in enumerate(wires)],
    ]
    turn = rotate(pitch, 24)
    rows = {3 + k: winding(turn, 24, 2, 5, "top" if k < 4 else "bottom") for k in range(8)}
    mats = [lib["Air"], lib["Steel"], lib["Air"]] + [lib["Copper"]] * 8
    make_group(study, "Stator", cells, [turn], mats, rows)
    surface_rotor(doc, study, lib, 4)
    sliding(study)
    return study


CASES = [
    ("L-01", l_01, "meshes"),
    ("L-02", l_02, "meshes"),
    ("L-03", l_03, "meshes"),
    ("L-04", l_04, "meshes"),
    ("L-05", l_05, "meshes"),
    ("L-06", sl.l_06, "meshes"),
    ("L-07", sl.l_07, "meshes"),
    ("L-13", l_13, "meshes"),
    ("L-08", l_08, "meshes"),
    ("L-09", l_09, "meshes"),
    ("L-10", l_10, "meshes"),
    ("L-11", l_11, "meshes"),
    ("L-12", l_12, "meshes"),
]
