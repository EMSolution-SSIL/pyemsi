"""Litz wires L-01 to L-13: whole strands, no slices. A twisted strand is one whole object copied by rotation about the
wire axis; its skews are part of the drawn strand (common.twisted, a ruled loft through circles normal to its centre
line). Each wire is in a drawn air cylinder; the strands run its whole length and end on its end planes (spec 4.4).
A straight centre strand is a group of its own with no rules (spec 4.1). L-06 and L-07 are the success list's, built
from data/double_skew_opposite.brep. L-12 is the one 2D case. The <id>-structured rows draw each strand as the 5
blocks of an O-grid (common.ogrid: a square inside the circle, its corners joined to the circle), one cell object,
structured and recombined, so the strands are hexahedra (quadrangles in 2D) and the drawn air round them stays
unstructured. CASES lists (id, builder, expected[, check]) in catalogue order."""

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
    Structured,
    ogrid,
    ogrid_disc,
    structure,
    twist_line,
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


PITCH, HEIGHT = 10.0, 12.0


def helix(z):
    """The centre line of L-01's strand: helix radius 1.2, pitch 10."""
    return V(1.2 * math.cos(2 * math.pi * z / PITCH), 1.2 * math.sin(2 * math.pi * z / PITCH), z)


def l_01():
    """Helix radius 1.2, pitch 10, height 12, strand radius 0.45 (read from the user's file), Rotate Z 60° x 6, each
    strand its own part."""
    doc, study, lib = wire_study("L_01")
    cells = strands(doc, "HelicalStrand", [strand(helix, 0.45, 0, HEIGHT, 48)])
    layer(study, lib, "Strands", cells, [rotate(60, 6)], size=0.3)
    wire_air(study, lib, 3.5, HEIGHT)
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
    """L-02's wire between two terminal plates (R 2.2, 3 thick) at its ends: the strands end on the plates. The plates
    are free objects inside the Air Region, a cylinder R 5, z -6..36 that gives way to them and to the strands. The
    plates are Copper where the catalogue colours them iron: they are the terminals that join the strands and carry the
    current (the excitation goes on them), a conductor, not a core."""
    doc, study, lib = wire_study("L_10")
    centre(doc, study, lib)
    layer(study, lib, "Wire", strands(doc, "RingStrand", [twisted(0, 1.1, 0, 180, 0, LENGTH, SR)]), [rotate(60, 6)])
    plates = [Part.makeCylinder(2.2, 3, V(0, 0, -3)), Part.makeCylinder(2.2, 3, V(0, 0, LENGTH))]
    for k, plate in enumerate(plates):
        symcases.add_free(study, f"Plate{k + 1}", plate, lib["Copper"])
    wire_air(study, lib, 5, LENGTH + 12, 1.0, z0=-6)
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


def l_12(name="L_12", structured=False):
    """24 slots, 2 pole pairs, coil span 5, a cross-section: one slot pitch (15°) with its gap band, iron, slot air and
    eight strands (R 0.85), four of the top layer and four of the bottom, Rotate Z 15° x 24. The winding generator names
    the strands of a layer: 6 parts. The rotor (4 surface magnets) slides at R 28.75. structured: each strand is the
    O-grid of its disc (common.ogrid_disc, 5 faces in one cell object), structured and recombined: 3 elements on the
    square's sides and the arcs, 1 on the radial lines."""
    doc, study = new_study(name, "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    pitch, th = 15.0, 3.0
    slot = sector(RI, RY, th, pitch - th)
    centres = [P(r, pitch / 2 + side * math.degrees(1.0 / r)) for r in (33.1, 35.2, 38.0, 40.1) for side in (-1, 1)]
    grids = [ogrid_disc(c, 0.85) for c in centres] if structured else []
    wires = [g[0] for g in grids] if structured else [disc(c, 0.85) for c in centres]
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
    for cell, (_, kinds) in zip(cells[3:], grids):
        structure(study, cell, kinds, {"square": 3, "arc": 3, "radial": 1})
    surface_rotor(doc, study, lib, 4)
    sliding(study)
    return study


# --- structured strands: O-grid blocks, hexahedra ---------------------------------------------------------------------

SHORT = 10.0  # L-02, L-03 and L-06 structured: a third of the wire, the same lay (the skews a third of the angles)


def straight(z):
    return V(0, 0, z)


def o_strands(doc, study, name, lines, r, length, across=6, step=0.125, n=24):
    """Whole strands about the centre lines lines, z 0..length, each the 5 blocks of an O-grid (common.ogrid through
    n + 1 sections, 2 for a straight line) in one cell object, structured and recombined: across elements on the
    square's sides and the arcs, 1 on the radial lines, and along the strand as many as make elements step long.
    The air puts a pyramid on each quadrangle of a strand (meshfrozen.quad_pyramids), lower where a neighbouring
    strand is close (gaps of 0.1 in L-01 to L-03, 0.16 in L-06); coarser counts (3 x 0.5) mesh too."""
    cells = []
    for k, line in enumerate(lines):
        shape, kinds = ogrid(line, r, 0, length, 1 if line is straight else n)
        points = [line(length * i / 200) for i in range(201)]
        along = math.ceil(sum(p.distanceToPoint(q) for p, q in zip(points, points[1:])) / step)
        cell = symcases.feature(doc, f"{name}{k + 1}" if len(lines) > 1 else name, shape)
        structure(study, cell, kinds, {"square": across, "arc": across, "radial": 1, "length": along})
        cells.append(cell)
    return cells


def o_layer(study, lib, name, cells, rules, rows=None):
    """layer for structured strands: Copper, each copy its own part unless rows say otherwise, and no Mesh Size."""
    make_group(study, name, cells, rules, [lib["Copper"]] * len(cells), rows or {i: EACH for i in range(len(cells))})


def l_01_structured():
    """L-01 with O-grid strands."""
    doc, study, lib = wire_study("L_01_structured")
    cells = o_strands(doc, study, "HelicalStrand", [helix], 0.45, HEIGHT)
    o_layer(study, lib, "Strands", cells, [rotate(60, 6)])
    wire_air(study, lib, 3.5, HEIGHT)
    return study


def o_layered(name, layers, air):
    """layered with O-grid strands over SHORT of the wire (the twist of each layer over the whole length LENGTH, so
    a third of it here): at the element size the 0.1 gaps need, the whole length takes over 2 minutes for L-02's
    7 strands. The straight centre strand is a group with no rules, one part."""
    doc, study, lib = wire_study(name)
    o_layer(study, lib, "Centre", o_strands(doc, study, "CentreStrand", [straight], SR, SHORT), [], {})
    for k, (rho, phi, n) in enumerate(layers, 1):
        line = twist_line(0, rho, 0, phi * SHORT / LENGTH, 0, SHORT)
        o_layer(
            study, lib, f"Layer {k}", o_strands(doc, study, f"Layer{k}Strand", [line], SR, SHORT), [rotate(360 / n, n)]
        )
    wire_air(study, lib, air, SHORT)
    return study


def l_02_structured():
    return o_layered("L_02_structured", [(1.1, 180, 6)], 3.5)


def l_03_structured():
    return o_layered("L_03_structured", [(1.1, 180, 6), (2.2, 180, 12)], 4.5)


def l_06_structured():
    """L-06's 7 x 7 wire with opposite skews (strands -240° round their bundle, bundles 90° round the wire), drawn as
    L-13 is (the success list's L-06 reads round strands from a BREP, which cannot be cut into blocks): the straight
    centre strand a group with no rules; the ring strand of the centre bundle and the 7 strands of one outer bundle
    (3.6 from the axis) the cells of Rotate Z 60° x 6, each strand its own part. A smaller wire than L-06: all 49
    strands, but SHORT of the length (the skews a third: 30° and -80°), since 49 structured strands over the whole
    length are too slow; the gaps (0.16 at least) allow elements of 5 x 0.2. O-grid strands, ending on the end planes
    of the air (R 7.5)."""
    doc, study, lib = wire_study("L_06_structured")
    f = SHORT / LENGTH
    sizes = {"across": 5, "step": 0.2}
    o_layer(study, lib, "Centre", o_strands(doc, study, "CentreStrand", [straight], SR, SHORT, **sizes), [], {})
    ring = o_strands(doc, study, "RingStrand", [twist_line(0, 1.2, 0, 90 * f, -240 * f, SHORT)], SR, SHORT, **sizes)
    lines = [twist_line(3.6, p, a, 90 * f, -240 * f, SHORT) for p, a in [(0, 0)] + [(1.2, 60 * k) for k in range(6)]]
    bundle = o_strands(doc, study, "BundleStrand", lines, SR, SHORT, **sizes)
    o_layer(study, lib, "Strands", ring + bundle, [rotate(60, 6)])
    wire_air(study, lib, 7.5, SHORT)
    return study


def l_12_structured():
    return l_12("L_12_structured", structured=True)


def hexahedra(*labels):
    """The check of a structured strand row: the strands of labels, each a cell object of 5 blocks, are one row each
    and hexahedra."""
    return Structured({label: "hexahedra" for label in labels}, labels)


BUNDLE = [f"BundleStrand{k}" for k in range(1, 8)]
SLOT_STRANDS = Structured({f"Strand{k}": "quadrangles" for k in range(1, 9)}, [f"Strand{k}" for k in range(1, 9)])

CASES = [
    ("L-01", l_01, "meshes"),
    ("L-01-structured", l_01_structured, "meshes", hexahedra("HelicalStrand")),
    ("L-02", l_02, "meshes"),
    ("L-02-structured", l_02_structured, "meshes", hexahedra("CentreStrand", "Layer1Strand")),
    ("L-03", l_03, "meshes"),
    ("L-03-structured", l_03_structured, "meshes", hexahedra("CentreStrand", "Layer1Strand", "Layer2Strand")),
    ("L-04", l_04, "meshes"),
    ("L-05", l_05, "meshes"),
    ("L-06", sl.l_06, "meshes"),
    ("L-06-structured", l_06_structured, "meshes", hexahedra("CentreStrand", "RingStrand", *BUNDLE)),
    ("L-07", sl.l_07, "meshes"),
    ("L-13", l_13, "meshes"),
    ("L-08", l_08, "meshes"),
    ("L-09", l_09, "meshes"),
    ("L-10", l_10, "meshes"),
    ("L-11", l_11, "meshes"),
    ("L-12", l_12, "meshes"),
    ("L-12-structured", l_12_structured, "meshes", SLOT_STRANDS),
]
