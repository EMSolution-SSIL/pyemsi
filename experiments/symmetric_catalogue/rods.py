"""Rods and conductors R-01 to R-11 (R-10, a twisted wire made of slices, left the catalogue). R-07 is the success
list's. CASES lists (id, builder, expected) in catalogue order."""

import math

from common import (
    App,
    MIRROR_X,
    MIRROR_Y,
    MIRROR_Z,
    P,
    Part,
    V,
    cut,
    extruded,
    make_group,
    mirror,
    new_study,
    pie,
    polygon,
    rotate,
    sector,
    sizes,
    sl,
    symcases,
    table,
    twisted,
    wire_air,
)

EACH = {"mode": "each"}


def rect(x1, y1, x2, y2):
    return polygon([V(x1, y1, 0), V(x2, y1, 0), V(x2, y2, 0), V(x1, y2, 0)])


def half_disc(centre_deg, radius, r, side, ccw=True):
    """Half the disc of radius r centred radius from the origin at centre_deg: the half on side +1 (towards larger
    angles) or -1 of the line through the origin at centre_deg, its diameter on that line. Drawn counterclockwise,
    so that the face is turned to +Z. A clockwise face (ccw False, the R-06-clockwise row) is turned to -Z; the mesher
    meshes it counterclockwise all the same (tool defect D3, fixed)."""
    c = P(radius, centre_deg)
    u = V(math.cos(math.radians(centre_deg)), math.sin(math.radians(centre_deg)), 0)
    w = V(-u.y, u.x, 0) * side
    a, b = c + u * r * side, c - u * r * side
    if not ccw:
        a, b = b, a
    return Part.Face(Part.Wire([Part.Arc(a, c + w * r, b).toShape(), Part.LineSegment(b, a).toShape()]))


# --- R-01: round rod in air, 2D -----------------------------------------------------------------------------------------


def r_01():
    """An eighth of the rod and its air (0..45°), mirrored at the line of 45°, then Rotate Z 90° x 4."""
    doc, study = new_study("R_01", "2D", "No movement", 0.8)
    lib = symcases.libraries(study)
    cells = [symcases.feature(doc, "Air", sector(4, 14, 0, 45)), symcases.feature(doc, "Rod", pie(4, 0, 45))]
    a = math.radians(45)
    make_group(
        study,
        "Rod and air",
        cells,
        [mirror((-math.sin(a), math.cos(a), 0)), rotate(90, 4)],
        [lib["Air"], lib["Copper"]],
    )
    return study


# --- R-02: axisymmetric rod inside a coil, 2D ZX ------------------------------------------------------------------------


def r_02():
    """Half the model above z = 0 in a ZX Study: the rod (r 0..3, z 0..14), half the coil (r 6..9, z 0..6) and the air
    (r 0..16, z 0..20) round them, mirrored at z = 0. The coil's halves are one part (across the mirror)."""
    doc, study = new_study("R_02", "2D", "No movement", 0.8)
    lib = symcases.libraries(study)

    def zx(x1, z1, x2, z2):  # in the ZX plane, turned like Part.makePlane(..., V(0, -1, 0))
        return polygon([V(x1, 0, z1), V(x2, 0, z1), V(x2, 0, z2), V(x1, 0, z2)])

    rod, coil = zx(0, 0, 3, 14), zx(6, 0, 9, 6)
    cells = [
        symcases.feature(doc, "Air", cut(zx(0, 0, 16, 20), rod, coil)),
        symcases.feature(doc, "Rod", rod),
        symcases.feature(doc, "Coil", coil),
    ]
    mats = [lib["Air"], lib["Copper"], lib["Copper"]]
    make_group(study, "Half model", cells, [MIRROR_Z], mats, {2: {"mode": "across", "across": [0]}})
    return study


# --- R-03: rectangular busbar, two mirrors -------------------------------------------------------------------------------


def r_03():
    """A quarter of the bar (0..12 x 0..2) in its air (0..20 x 0..12), mirrored at y = 0 and then at x = 0."""
    doc, study = new_study("R_03", "2D", "No movement", 0.8)
    lib = symcases.libraries(study)
    bar = rect(0, 0, 12, 2)
    cells = [symcases.feature(doc, "Air", cut(rect(0, 0, 20, 12), bar)), symcases.feature(doc, "Bar", bar)]
    make_group(study, "Bar and air", cells, [MIRROR_Y, MIRROR_X], [lib["Air"], lib["Copper"]])
    return study


# --- R-04: three-phase busbar row, a translation --------------------------------------------------------------------------


def r_04():
    """A bar (0..3 x -5..5) in its air (-5..9 x -12..12), Translate (14, 0) x 3: each bar its own part (its own phase),
    the air one part."""
    doc, study = new_study("R_04", "2D", "No movement", 0.8)
    lib = symcases.libraries(study)
    bar = rect(0, -5, 3, 5)
    cells = [symcases.feature(doc, "Air", cut(rect(-5, -12, 9, 12), bar)), symcases.feature(doc, "Bar", bar)]
    move = {"kind": "translate", "vector": [14, 0, 0], "count": 3}
    make_group(study, "Conductors", cells, [move], [lib["Air"], lib["Copper"]], {1: EACH})
    return study


# --- R-05 and R-06: stranded conductors, 2D ------------------------------------------------------------------------------

RING1, RING2 = 4.2, 8.4  # the catalogue's 4.05 and 8.05 put a ring-2 strand on a ring-1 strand at one point: 0.2 apart


def bundle(name, size, outer, rows_more):
    """The 0..30° wedge of a stranded conductor, Mirror y = 0 and Rotate Z 60° x 6: the centre strand's wedge (all 12
    one part), half a ring-1 strand (its halves across the mirror) and the air to radius outer; rows_more(doc, lib)
    gives more cells, their materials and their rows (by index in the group)."""
    doc, study = new_study(name, "2D", "No movement", size)
    lib = symcases.libraries(study)
    centre, half = pie(2, 0, 30), half_disc(0, RING1, 2, 1)
    more, mats_more, rows = rows_more(doc, lib)
    air = cut(pie(outer, 0, 30), centre, half, *[c.Shape for c in more])
    cells = [
        symcases.feature(doc, "Air", air),
        symcases.feature(doc, "CentreStrand", centre),
        symcases.feature(doc, "Ring1Half", half),
        *more,
    ]
    mats = [lib["Air"], lib["Copper"], lib["Copper"], *mats_more]
    rows = {2: {"mode": "across", "across": [0]}, **rows}
    make_group(study, "Bundle", cells, [MIRROR_Y, rotate(60, 6)], mats, rows)
    return study


def r_05():
    """Seven strands: the centre one from 12 wedges, six outer ones from two halves each."""
    return bundle("R_05", 0.5, 7.2, lambda doc, lib: ([], [], {}))


def r_06(name="R_06", ccw=True):
    """19 strands. Ring 2 has a strand at 0° (its halves across the mirror, as ring 1) and one at 30°, on the seam of
    the rotation: its drawn half (below the 30° line) and the mirrored half of the next rotation copy meet across the
    seam. The catalogue's "merge what touches" is Later (spec 2); a table does it: copy (mirror m, rotation k) of that
    half is the strand at 30 + 60 k (m = 0) or -30 + 60 k (m = 1). ccw False draws that half clockwise."""

    def more(doc, lib):
        cells = [
            symcases.feature(doc, "Ring2Half0", half_disc(0, RING2, 2, 1)),
            symcases.feature(doc, "Ring2Half30", half_disc(30, RING2, 2, -1, ccw)),
        ]
        seam = table(f"Ring2At{(30 + 60 * (c // 2) if c % 2 == 0 else -30 + 60 * (c // 2)) % 360}" for c in range(12))
        return cells, [lib["Copper"], lib["Copper"]], {3: {"mode": "across", "across": [0]}, 4: seam}

    return bundle(name, 0.5, 11.2, more)


def r_06_clockwise():
    """R-06 with the ring-2 half at 30° drawn clockwise (its face turned to -Z). The design takes it (a face is a face),
    so it meshes, every triangle counterclockwise (tool defect D3, fixed: it gave inverted triangles silently)."""
    return r_06("R_06cw", ccw=False)


# --- R-08: rod tilted 30° from Z --------------------------------------------------------------------------------------


def r_08():
    """An eighth of a rod (R 3, 0..45°, 14 long) on an axis tilted 30° from Z towards X. Rules follow the rod: Mirror in
    the plane y = 0 (it holds the axis), Rotate about the axis (0.5, 0, 0.866) 90° x 4, Mirror in the mid-plane normal
    to the axis. A drawn box of air round it."""
    doc, study = new_study("R_08", "3D", "No movement", 1.0)
    lib = symcases.libraries(study)
    tilt = App.Placement(V(), App.Rotation(V(0, 1, 0), 30)).toMatrix()
    rod = symcases.feature(doc, "Rod", extruded(pie(3, 0, 45), 0, 14).transformed(tilt))
    axis = (math.sin(math.radians(30)), 0, math.cos(math.radians(30)))
    rules = [MIRROR_Y, rotate(90, 4, axis), mirror(axis)]
    make_group(study, "Rod", [rod], rules, [lib["Copper"]])
    air = symcases.add_free(study, "FreeAir", Part.makeBox(30, 20, 40, V(-15, -10, -20)), lib["Air"])
    sizes(study, [(air, 3.0)])
    return study


# --- R-09: rod with periodic ferrite beads ----------------------------------------------------------------------------


def r_09():
    """A rod (R 2, z 0..3) and half a bead (R 3..7, z 0..1.6), Mirror z = 0, then Translate (0, 0, 6) x 5: the rod one
    part end to end, each bead its two halves (across the mirror). The rod runs the length of its drawn air (R 10,
    z -3..27) and ends on its end planes."""
    doc, study = new_study("R_09", "3D", "No movement", 1.0)
    lib = symcases.libraries(study)
    cells = [
        symcases.feature(doc, "Rod", Part.makeCylinder(2, 3)),
        symcases.feature(doc, "BeadHalf", Part.makeCylinder(7, 1.6).cut(Part.makeCylinder(3, 1.6))),
    ]
    move = {"kind": "translate", "vector": [0, 0, 6], "count": 5}
    make_group(
        study, "Rod", cells, [MIRROR_Z, move], [lib["Copper"], lib["Steel"]], {1: {"mode": "across", "across": [0]}}
    )
    wire_air(study, lib, 10, 30, 2.0, z0=-3)
    return study


def r_09_quarter():
    """R-09 drawn as a quarter (0..90°), Mirror x = 0 and Mirror y = 0 before the catalogue's two rules, as R-07: no
    face of the cell on the z = 0 seam is a whole disc or ring with free air round it."""
    doc, study = new_study("R_09q", "3D", "No movement", 1.0)
    lib = symcases.libraries(study)
    cells = [
        symcases.feature(doc, "Rod", extruded(pie(2, 0, 90), 0, 3)),
        symcases.feature(doc, "BeadQuarter", extruded(sector(3, 7, 0, 90), 0, 1.6)),
    ]
    move = {"kind": "translate", "vector": [0, 0, 6], "count": 5}
    rows = {1: {"mode": "across", "across": [0, 1, 2]}}
    make_group(study, "Rod", cells, [MIRROR_X, MIRROR_Y, MIRROR_Z, move], [lib["Copper"], lib["Steel"]], rows)
    wire_air(study, lib, 10, 30, 2.0, z0=-3)
    return study


# --- R-11: twisted pair ------------------------------------------------------------------------------------------------


def r_11():
    """One whole strand (R 1.8, its centre 2.4 from the axis, one turn over 28), Rotate Z 180° x 2: the other strand.
    Each strand its own part, in a drawn air cylinder whose end planes the strands end on."""
    doc, study = new_study("R_11", "3D", "No movement", 1.5)
    lib = symcases.libraries(study)
    wire = symcases.feature(doc, "Strand", twisted(0, 2.4, 0, 360, 0, 28, 1.8, n=48))
    make_group(study, "Pair", [wire], [rotate(180, 2)], [lib["Copper"]], {0: EACH})
    sizes(study, [(wire, 0.8)])
    wire_air(study, lib, 7, 28)
    return study


CASES = [
    ("R-01", r_01, "meshes"),
    ("R-02", r_02, "meshes"),
    ("R-03", r_03, "meshes"),
    ("R-04", r_04, "meshes"),
    ("R-05", r_05, "meshes"),
    ("R-06", r_06, "meshes"),
    ("R-06-clockwise", r_06_clockwise, "meshes"),
    ("R-07", sl.r_07, "meshes"),
    ("R-08", r_08, "meshes"),
    ("R-09", r_09, "meshes"),
    ("R-09-quarter", r_09_quarter, "meshes"),
    ("R-11", r_11, "meshes"),
]
