"""Other electromagnetic devices D-01 to D-13, and D-01-structured (the user's own D-01 with structured blocks). D-07
(three-core cable) and D-08 (Helmholtz pair) are the success list's. 3D devices are in an Air Region on a drawn shape
unless the catalogue draws the air in the cell. CASES lists (id, builder, expected[, check]) in catalogue order."""

from common import (
    MIRROR_X,
    MIRROR_Y,
    MIRROR_Z,
    Part,
    Structured,
    V,
    cut,
    extruded,
    make_group,
    new_study,
    objects,
    outline,
    polygon,
    rotate,
    sector,
    sizes,
    sl,
    symcases,
    table,
)

EACH = {"mode": "each"}
ACROSS_1 = {"mode": "across", "across": [0]}


def rect(x1, y1, x2, y2):
    return polygon([V(x1, y1, 0), V(x2, y1, 0), V(x2, y2, 0), V(x1, y2, 0)])


def zx(x1, z1, x2, z2):
    """A rectangle in the ZX plane (y = 0), turned like Part.makePlane(..., V(0, -1, 0)), as success_list.d_08."""
    return polygon([V(x1, 0, z1), V(x2, 0, z1), V(x2, 0, z2), V(x1, 0, z2)])


def box(x1, x2, y1, y2, z1, z2):
    return Part.makeBox(x2 - x1, y2 - y1, z2 - z1, V(x1, y1, z1))


def revolved(section, a1, a2):
    """The solid swept by the polygon section [(r, z)] about Z from a1 to a2 degrees."""
    face = polygon([V(r, 0, z) for r, z in section])
    face.rotate(V(0, 0, 0), V(0, 0, 1), a1)
    solid = face.revolve(V(0, 0, 0), V(0, 0, 1), a2 - a1)
    assert solid.isValid() and abs(solid.Volume) > 0, "the revolved section is not a valid solid"
    return solid


def free_air(study, lib, shape, size):
    """The drawn air shape as the Custom shape of the Study's Air Region, with a Mesh Size of size."""
    sizes(study, [(symcases.add_air_region(study, lib["Air"], shape=shape), size)])


# --- D-01 and D-02: transformers, a quarter drawn, Mirror y = 0 then Mirror x = 0 -------------------------------------


def d_01():
    """Single-phase EI transformer. A quarter: the core (centre limb x 0..5, window 5..15 x 0..12, outer limb 15..20,
    yoke to y 17), the coil side in the window (6..14 x 0..10.5) and the air to 30 x 28. The window air is enclosed by
    the core and the mirror line, so it is a cell object of its own. The coil is across rule 1 (one side of the coil),
    separate across rule 2 (left and right carry opposite current)."""
    doc, study = new_study("D_01", "2D", "No movement", 0.8)
    lib = symcases.libraries(study)
    core = polygon([V(x, y, 0) for x, y in ((0, 0), (5, 0), (5, 12), (15, 12), (15, 0), (20, 0), (20, 17), (0, 17))])
    coil = rect(6, 0, 14, 10.5)
    cells = [
        symcases.feature(doc, "Air", cut(rect(0, 0, 30, 28), rect(0, 0, 20, 17))),
        symcases.feature(doc, "WindowAir", cut(rect(5, 0, 15, 12), coil)),
        symcases.feature(doc, "Core", core),
        symcases.feature(doc, "Coil", coil),
    ]
    mats = [lib["Air"], lib["Air"], lib["Steel"], lib["Copper"]]
    make_group(study, "Core and coil", cells, [MIRROR_Y, MIRROR_X], mats, {3: ACROSS_1})
    return study


def edges_on(body, segments):
    """[(body, "EdgeN")] of the edges of body from one end to the other of a segment ((x1, y1), (x2, y2))."""
    want = [{(float(x), float(y)) for x, y in s} for s in segments]
    out = []
    for i, e in enumerate(body.Shape.Edges, 1):
        ends = {(round(v.X, 9) + 0.0, round(v.Y, 9) + 0.0) for v in e.Vertexes}
        if ends in want:
            out.append((body, f"Edge{i}"))
    assert len(out) == len(segments), f"{body.Label}: {len(out)} of {len(segments)} edges found"
    return out


def d_01_structured():
    """The user's own D-01 (their file delme\\new_symmetric tesrs\\D-01), drawn the way they drew it: a quarter, the
    core (x 0..42, y 0..32, the window 13..32 x 0..22 cut out) cut into 3 faces of 4 corners by two lines from the
    window's top corners to the outer corners (a Boolean Fragments: symcases.transformer_doc), the coil (15..30 x
    0..20) and the window's air round it; no air outside the core. Mirror y = 0, then Mirror x = 0. Their mesh items:
    Transfinite Body and Recombine on the core and the coil, Transfinite Edges of 10 (the coil's sides, the core's ends
    across the limbs and yoke) and 15 (along the limbs and yoke, and the window's sides) on the core, the coil and the
    air; the air is not structured (8 corners). The core is one row, so one part (their file, from before a cell
    object had one row, had a part per face); the coil across rule 1, so the left and right sides; mesh size 5."""
    doc, study = new_study("D_01_structured", "2D", "No movement", 5.0)
    lib = symcases.libraries(study)
    drawn = symcases.transformer_doc(doc)
    core, coil, air = drawn["core"], drawn["coil"], drawn["air"]
    make_group(
        study,
        "Symmetric Group",
        [core, air, coil],
        symcases.TRANSFORMER_RULES,
        [lib[k] for k in ("Steel", "Air", "Copper")],
        {2: ACROSS_1},
    )
    coil_sides = [((15, 0), (30, 0)), ((30, 0), (30, 20)), ((30, 20), (15, 20)), ((15, 20), (15, 0))]
    window = [((13, 0), (13, 22)), ((13, 22), (32, 22)), ((32, 22), (32, 0))]
    ends = [((0, 0), (13, 0)), ((0, 32), (13, 22)), ((32, 22), (42, 32)), ((32, 0), (42, 0))]
    along = [((0, 0), (0, 32)), ((0, 32), (42, 32)), ((42, 32), (42, 0))] + window
    objects.make_transfinite_edges(study, 10, edges_on(coil, coil_sides) + edges_on(air, coil_sides[1:]))
    objects.make_transfinite_edges(study, 10, edges_on(core, ends))
    objects.make_transfinite_edges(study, 15, edges_on(core, along) + edges_on(air, window))
    objects.make_transfinite_body(study, [coil])
    objects.make_recombine(study, [coil])
    objects.make_transfinite_body(study, [core])
    objects.make_recombine(study, [core])
    return study


def d_02():
    """Three-phase core-type transformer. A quarter: the core (centre limb x 0..4, window 4..14 x 0..12, outer limb
    14..22, yoke to y 17), phase B's coil side on the centre limb (4.6..8.4), the inner (9.6..13.4) and outer
    (22.6..26.4) sides of the coil on the outer limb, and air to 34 x 26. Parts by a table, one per phase: B from one
    cell object and its mirror copies, A (copies not mirrored in x) and C (mirrored) from the two outer-limb objects."""
    doc, study = new_study("D_02", "2D", "No movement", 0.8)
    lib = symcases.libraries(study)
    core = polygon([V(x, y, 0) for x, y in ((0, 0), (4, 0), (4, 12), (14, 12), (14, 0), (22, 0), (22, 17), (0, 17))])
    phase_b, inner, outer = rect(4.6, 0, 8.4, 10.5), rect(9.6, 0, 13.4, 10.5), rect(22.6, 0, 26.4, 10.5)
    cells = [
        symcases.feature(doc, "Air", cut(rect(0, 0, 34, 26), rect(0, 0, 22, 17), outer)),
        symcases.feature(doc, "WindowAir", cut(rect(4, 0, 14, 12), phase_b, inner)),
        symcases.feature(doc, "Core", core),
        symcases.feature(doc, "CoilB", phase_b),
        symcases.feature(doc, "CoilACInner", inner),
        symcases.feature(doc, "CoilACOuter", outer),
    ]
    mats = [lib["Air"], lib["Air"], lib["Steel"], lib["Copper"], lib["Copper"], lib["Copper"]]
    a_or_c = table(["A", "A", "C", "C"])  # copy = mirror y + 2 * mirror x
    rows = {3: table(["B"] * 4), 4: a_or_c, 5: a_or_c}
    make_group(study, "Core and coils", cells, [MIRROR_Y, MIRROR_X], mats, rows)
    return study


# --- D-03: E-core inductor, one eighth --------------------------------------------------------------------------------


def d_03():
    """One eighth (x, y, z >= 0): the E core (centre limb x 0..4, window 4..12 x 0..10, outer limb 12..16, back to
    y 14, half its depth z 0..6), an eighth of the coil round the centre limb (an L section in XZ: x 4.5..11.5 in the
    window, x 0..11.5 over the core at z 6.5..9.5, along y 0..9.5) and the air to 24 x 22 x 16 round them. The
    catalogue draws the coil as two boxes with a gap at z 6..6.5; here they are joined into one L, so that the eight
    copies fuse into one closed coil. Mirror x = 0, Mirror y = 0, Mirror z = 0; each object one part."""
    doc, study = new_study("D_03", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    e = polygon([V(x, y, 0) for x, y in ((0, 0), (4, 0), (4, 10), (12, 10), (12, 0), (16, 0), (16, 14), (0, 14))])
    core = extruded(e, 0, 6)
    section = [(4.5, 0), (11.5, 0), (11.5, 9.5), (0, 9.5), (0, 6.5), (4.5, 6.5)]
    coil = polygon([V(x, 0, z) for x, z in section]).extrude(V(0, 9.5, 0))
    cells = [
        symcases.feature(doc, "Air", cut(box(0, 24, 0, 22, 0, 16), core, coil)),
        symcases.feature(doc, "Core", core),
        symcases.feature(doc, "Coil", coil),
    ]
    make_group(study, "Inductor", cells, [MIRROR_X, MIRROR_Y, MIRROR_Z], [lib["Air"], lib["Steel"], lib["Copper"]])
    sizes(study, [(cells[1], 1.5), (cells[2], 1.5)])
    return study


# --- D-04: toroidal inductor with discrete turns ------------------------------------------------------------------------


def d_04():
    """A core sector (R 21..29, z 0..4, -7.5..7.5°) and the upper half of one turn round it (legs R 19.6..20.6 and
    29.4..30.4 from z 0 to 5, the top R 19.6..30.4 at z 5..6, -2.2..2.2°). Mirror z = 0, then Rotate Z 15° x 24. The
    core fuses into one ring (one part); each turn is its two halves (across rule 1): 24 turns. Drawn air cylinder."""
    doc, study = new_study("D_04", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    turn = revolved([(19.6, 0), (20.6, 0), (20.6, 5), (29.4, 5), (29.4, 0), (30.4, 0), (30.4, 6), (19.6, 6)], -2.2, 2.2)
    cells = [
        symcases.feature(doc, "CoreSector", extruded(sector(21, 29, -7.5, 7.5), 0, 4)),
        symcases.feature(doc, "HalfTurn", turn),
    ]
    make_group(study, "Toroid", cells, [MIRROR_Z, rotate(15, 24)], [lib["Steel"], lib["Copper"]], {1: ACROSS_1})
    sizes(study, [(cells[0], 1.5), (cells[1], 0.8)])
    free_air(study, lib, Part.makeCylinder(38, 20, V(0, 0, -10)), 4.0)
    return study


# --- D-05: wireless charging pads facing each other -------------------------------------------------------------------


def d_05():
    """A ferrite bar (x 8..22, y -1.6..1.6, z 3..4) and a coil sector over it (R 10..20, z 4.2..5.6, -22.5..22.5°),
    Rotate Z 45° x 8, then Mirror z = 0: the other pad. Bars each copy separate (16 parts); the coil across rule 1, so
    two parts, the top coil and the bottom coil. Drawn air cylinder."""
    doc, study = new_study("D_05", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    cells = [
        symcases.feature(doc, "FerriteBar", box(8, 22, -1.6, 1.6, 3, 4)),
        symcases.feature(doc, "CoilSector", extruded(sector(10, 20, -22.5, 22.5), 4.2, 5.6)),
    ]
    make_group(study, "Pads", cells, [rotate(45, 8), MIRROR_Z], [lib["Steel"], lib["Copper"]], {0: EACH, 1: ACROSS_1})
    sizes(study, [(cells[0], 0.8), (cells[1], 0.8)])
    free_air(study, lib, Part.makeCylinder(32, 24, V(0, 0, -12)), 4.0)
    return study


# --- D-06: eight-pole magnetic bearing --------------------------------------------------------------------------------


def d_06():
    """Stator: a pole (R 20..32, 8..37°) on its yoke (R 32..38, 0..45°), the coil round it (two faces in one object,
    R 21.5..30.5 at 2..7.2° and 37.8..43°) and the slot air (R 20..32, two faces). Rotor: iron R 8..18. Both Mirror
    y = 0, Rotate Z 90° x 4, as the catalogue gives them. The coil is one part per pole pair, a quadrant (a table: the
    two faces and their mirror copies). The catalogue's rotor air band (R 18..20) would touch the stator's copies, and
    copies of two groups on one side may not touch (Validate), so it is drawn as a ring between them, a free object
    flush against both (spec 4.4). Static."""
    doc, study = new_study("D_06", "2D", "No movement", 1.0)
    lib = symcases.libraries(study)
    pole = outline((20, 8), (20, 37), (32, 37), (32, 45), (38, 45), (38, 0), (32, 0), (32, 8))
    sides = [sector(21.5, 30.5, 2, 7.2), sector(21.5, 30.5, 37.8, 43)]
    slots = [cut(sector(20, 32, 0, 8), sides[0]), cut(sector(20, 32, 37, 45), sides[1])]
    cells = [
        symcases.feature(doc, "SlotAir", Part.makeCompound(slots)),
        symcases.feature(doc, "Iron", pole),
        symcases.feature(doc, "CoilAroundPole", Part.makeCompound(sides)),
    ]
    mats = [lib["Air"], lib["Steel"], lib["Copper"]]
    pairs = table(f"PolePair{c // 2 + 1}" for c in range(8))  # copy = mirror + 2 * rotation
    make_group(study, "Stator", cells, [MIRROR_Y, rotate(90, 4)], mats, {2: pairs})
    rotor = symcases.feature(doc, "RotorIron", sector(8, 18, 0, 45))
    make_group(study, "Rotor", [rotor], [MIRROR_Y, rotate(90, 4)], [lib["Steel"]])
    gap = Part.Face(Part.Wire(Part.makeCircle(20))).cut(Part.Face(Part.Wire(Part.makeCircle(18))))
    symcases.add_free(study, "AirGap", gap.Faces[0], lib["Air"])
    return study


# --- D-09: induction-heating coil on a billet (ZX) --------------------------------------------------------------------


def d_09():
    """Axisymmetric (ZX) Study, one turn pitch above z = 0: the billet (r 0..5, z 0..3), half a coil turn (r 8..11,
    z 0..1.4) and the air to r 16. Mirror z = 0, then Translate (0, 0, 6) x 6. Billet and air one part each (they fuse
    along the length), each turn its own part (across rule 1)."""
    doc, study = new_study("D_09", "2D", "No movement", 0.5)
    lib = symcases.libraries(study)
    billet, coil = zx(0, 0, 5, 3), zx(8, 0, 11, 1.4)
    cells = [
        symcases.feature(doc, "Air", cut(zx(0, 0, 16, 3), billet, coil)),
        symcases.feature(doc, "Billet", billet),
        symcases.feature(doc, "HalfTurn", coil),
    ]
    move = {"kind": "translate", "vector": [0, 0, 6], "count": 6}
    mats = [lib["Air"], lib["Steel"], lib["Copper"]]
    make_group(study, "One turn pitch", cells, [MIRROR_Z, move], mats, {2: ACROSS_1})
    return study


# --- D-10: pancake coil over a cracked plate --------------------------------------------------------------------------


def d_10():
    """Half the model, y >= 0: the plate (x -20..20, y 0..18, z -3..0) with the crack cut out of it (x -1..1, y 0..8,
    through the plate), the crack's air, and half the pancake coil (R 5..8, z 2..5, 0..180°). One mirror only, y = 0:
    the crack breaks the other direction. The crack and the coil are across the mirror. Drawn air box."""
    doc, study = new_study("D_10", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    crack = box(-1, 1, 0, 8, -3, 0)
    cells = [
        symcases.feature(doc, "Plate", cut(box(-20, 20, 0, 18, -3, 0), crack)),
        symcases.feature(doc, "Crack", crack),
        symcases.feature(doc, "CoilHalf", revolved([(5, 2), (8, 2), (8, 5), (5, 5)], 0, 180)),
    ]
    mats = [lib["Copper"], lib["Air"], lib["Copper"]]
    make_group(study, "Plate and coil", cells, [MIRROR_Y], mats, {1: ACROSS_1, 2: ACROSS_1})
    sizes(study, [(cells[1], 0.8), (cells[2], 1.0)])
    free_air(study, lib, box(-30, 30, -28, 28, -12, 15), 5.0)
    return study


# --- D-11: shield plate with a grid of holes --------------------------------------------------------------------------


def d_11():
    """A plate cell 10 x 10 x 1 with a hole R 2.6 at its centre, Translate (10, 0, 0) x 5, then Translate (0, 10, 0)
    x 4: a 5 x 4 grid, one part. The air is a drawn box over the plate; it fills the holes."""
    doc, study = new_study("D_11", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    hole = Part.makeCylinder(2.6, 1, V(5, 5, 0))
    cell = symcases.feature(doc, "PlateCell", cut(box(0, 10, 0, 10, 0, 1), hole))
    rules = [
        {"kind": "translate", "vector": [10, 0, 0], "count": 5},
        {"kind": "translate", "vector": [0, 10, 0], "count": 4},
    ]
    make_group(study, "Plate", [cell], rules, [lib["Copper"]])
    sizes(study, [(cell, 0.8)])
    free_air(study, lib, box(-10, 60, -10, 50, -10, 11), 5.0)
    return study


# --- D-12: 18 toroidal coils with ring coils round them ---------------------------------------------------------------

TF = [(38, 0), (46, 0), (46, 10), (42, 22), (28, 28), (14, 22), (10, 10), (10, 0), (18, 0), (18, 8), (21, 16)]
TF += [(28, 20), (35, 16), (38, 8)]


def d_12():
    """Toroidal coils: the top half of a D-shaped coil (the catalogue's outline in the XZ plane, 3.6 thick in y, its
    legs ending on z = 0), Rotate Z 20° x 18, then Mirror z = 0; each coil its two halves (across rule 2): 18 coils.
    The outline is moved 4 out in x (legs at x 14..22 and 42..50): with the catalogue's inner leg at x 10..18, the
    corners of neighbouring coils overlap. Ring coils: a whole ring (R 50..54, z 24..28) as the cell of its own group,
    Mirror z = 0, each ring its own part. The groups do not touch. Drawn air cylinder."""
    doc, study = new_study("D_12", "3D", "No movement", 3.0)
    lib = symcases.libraries(study)
    coil = polygon([V(x + 4, -1.8, z) for x, z in TF]).extrude(V(0, 3.6, 0))
    tf = symcases.feature(doc, "ToroidalCoilHalf", coil)
    make_group(
        study,
        "Toroidal coils",
        [tf],
        [rotate(20, 18), MIRROR_Z],
        [lib["Copper"]],
        {0: {"mode": "across", "across": [1]}},
    )
    ring = symcases.feature(doc, "Ring", revolved([(50, 24), (54, 24), (54, 28), (50, 28)], 0, 360))
    make_group(study, "Ring coils", [ring], [MIRROR_Z], [lib["Copper"]], {0: EACH})
    sizes(study, [(tf, 1.5), (ring, 1.5)])
    free_air(study, lib, Part.makeCylinder(66, 80, V(0, 0, -40)), 7.0)
    return study


# --- D-13: railgun rails and armature ---------------------------------------------------------------------------------


def d_13():
    """A rail (x 3..7, y 0..6, z 0..30) and half the armature against it (x 0..3, z 12..16), Mirror x = 0: the rails
    each their own part (opposite current), the armature halves one part. Drawn air box."""
    doc, study = new_study("D_13", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    cells = [
        symcases.feature(doc, "Rail", box(3, 7, 0, 6, 0, 30)),
        symcases.feature(doc, "ArmatureHalf", box(0, 3, 0, 6, 12, 16)),
    ]
    make_group(study, "Launcher", cells, [MIRROR_X], [lib["Copper"], lib["Copper"]], {0: EACH})
    free_air(study, lib, box(-15, 15, -8, 14, -6, 36), 4.0)
    return study


CASES = [
    ("D-01", d_01, "meshes"),
    (
        "D-01-structured",
        d_01_structured,
        "meshes",
        Structured({"CoreCell": "quadrangles", "CoilCell": "quadrangles"}, ["CoreCell"]),
    ),
    ("D-02", d_02, "meshes"),
    ("D-03", d_03, "meshes"),
    ("D-04", d_04, "meshes"),
    ("D-05", d_05, "meshes"),
    ("D-06", d_06, "meshes"),
    ("D-07", sl.d_07, "meshes"),
    ("D-08", sl.d_08, "meshes"),
    ("D-09", d_09, "meshes"),
    ("D-10", d_10, "meshes"),
    ("D-11", d_11, "meshes"),
    ("D-12", d_12, "meshes"),
    ("D-13", d_13, "meshes"),
]
