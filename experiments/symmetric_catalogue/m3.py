"""3D motors M3-01 to M3-12. The sliding motors slide at R 28.5 behind a Rotational Sliding Interface: the structured,
recombined layers 28..28.5 (rotor) and 28.5..29 (stator) form the sliding cylinder, with unstructured air between them
and the teeth (29..30) or the magnets (25..28), spec 7.5, as in success_list.m3_02. M3-02, M3-07, M3-10 and M3-12 are
the success list's. M3-01-structured is M3-01 with its coil sides structured too. CASES lists (id, builder,
expected[, check]) in catalogue order."""

from common import (
    App,
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
    objects,
    rotate,
    sector,
    sizes,
    sl,
    symcases,
    table,
    winding,
    Structured,
)
from emsolution import symmetry

L = 14.0  # the stack


def stator48(doc, study, lib, z1, layer=True, rules=()):
    """The 48-slot, 8-pole two-layer stator of M3-02 over z 0..z1 (coil span 5), copied by rules and then Rotate Z
    7.5° x 48. layer: the structured layer 28.5..29 and the gap air 29..30 as cell objects (cells[4] and cells[5])."""
    turn = rotate(7.5, 48)
    inner = [("StatorLayer", sector(28.5, 29, 0, 7.5)), ("StatorGap", sector(29, 30, 0, 7.5))] if layer else []
    cells = sl.stator_slot_3d(doc, 7.5, z1, inner)
    mats = [lib[k] for k in ("Steel", "Air", "Copper", "Copper", "Air", "Air")][: len(cells)]
    rows = {2: winding(turn, 48, 4, 5, "top"), 3: winding(turn, 48, 4, 5, "bottom")}
    make_group(study, "Stator", cells, [*rules, turn], mats, rows)
    return cells


def motion(*matrices, count):
    """A rule of the engine that the panel cannot enter yet (spec 2, "Later"): one rigid motion, matrices composed
    (the last applied first), and its count."""
    return {"kind": "motion", "matrix": symmetry.compose(*matrices), "count": count}


# --- M3-01: the 48-slot, 8-pole motor over the whole stack -----------------------------------------------------------


def m3_01(name="M3_01"):
    doc, study = new_study(name, "3D", "Sliding motion", 2.0)
    lib = symcases.libraries(study)
    stator = stator48(doc, study, lib, L)
    magnet = sector(25, 27.5, 0, 17.5)
    cells = [
        symcases.feature(doc, "RotorIron", extruded(sector(8, 25, 0, 22.5), 0, L)),
        symcases.feature(doc, "Magnet", extruded(magnet, 0, L)),
        symcases.feature(doc, "RotorAir", extruded(cut(sector(25, 28, 0, 22.5), magnet), 0, L)),
        symcases.feature(doc, "RotorLayer", extruded(sector(28, 28.5, 0, 22.5), 0, L)),
    ]
    mats = [lib["Steel"], lib["Steel"], lib["Air"], lib["Air"]]
    make_group(study, "Rotor", cells, [MIRROR_Y, rotate(45, 8)], mats, {1: {"mode": "across", "across": [0]}}, "Moving")
    objects.make_sliding_interface(study, "Rotational", Radius=28.5, Divisions=144, CrossDivisions=8)
    symcases.transfinite_layer(study, stator[4], 3, 8)  # 144 / 48
    symcases.transfinite_layer(study, cells[3], 9, 8)  # 144 * 22.5 / 360
    sizes(study, [(stator[5], 0.8), (cells[2], 1.2)])
    return study


def m3_01_structured():
    """M3-01 with both coil sides structured and recombined as well as the sliding layers: 3 elements on each arc, 4
    across a coil side, 8 along the stack (as the layers). The coils are hexahedra; the slot air round them stays
    tetrahedra, with pyramids where it meets them."""
    study = m3_01("M3_01_structured")
    stator = objects.symmetric_groups(study)[0].Cells
    for side in stator[2:4]:
        symcases.transfinite_layer(study, side, 3, 8, 4)
    return study


# --- M3-03: a rotor in three slices, each turned 6° from the one below (step skew) ------------------------------------

SLICE, SKEW = L / 3, 6.0


def slice_faces():
    """The rotor's pole -22.5..22.5: iron, magnet (-18..18), air to 28 and the structured layer 28..28.5."""
    magnet = sector(25, 27.5, -18, 18)
    return [
        ("RotorIron", sector(8, 25, -22.5, 22.5)),
        ("Magnet", magnet),
        ("RotorAir", cut(sector(25, 28, -22.5, 22.5), magnet)),
        ("RotorLayer", sector(28, 28.5, -22.5, 22.5)),
    ]


def skewed(name, cells_for):
    """The M3-01 stator over a rotor of step-skewed slices; cells_for(doc) gives the rotor's cell objects (their
    layers last of every slice), its rules and rows. 240 divisions, so that the 6° skew lands on the grid (1.5°)."""
    doc, study = new_study(name, "3D", "Sliding motion", 2.0)
    lib = symcases.libraries(study)
    stator = stator48(doc, study, lib, L)
    cells, rules, rows = cells_for(doc)
    by = {"RotorIron": "Steel", "Magnet": "Steel", "RotorAir": "Air", "GapAir": "Air", "RotorLayer": "Air"}
    mats = [lib[by[c.Label.rstrip("0123456789")]] for c in cells]
    make_group(study, "Rotor", cells, rules, mats, rows, "Moving")
    objects.make_sliding_interface(study, "Rotational", Radius=28.5, Divisions=240, CrossDivisions=6)
    symcases.transfinite_layer(study, stator[4], 5, 6)  # 240 / 48
    for c in cells:
        if c.Label.startswith("RotorLayer"):  # 240 / 8; 6 over the stack
            symcases.transfinite_layer(study, c, 30, round(6 * c.Shape.BoundBox.ZLength / L))
    sizes(study, [(stator[5], 0.8)] + [(c, 1.2) for c in cells if c.Label.startswith(("RotorAir", "GapAir"))])
    return study


def m3_03():
    """The catalogue's rules: one slice, Rotate Z 45° x 8, then a screw step (turn 6° and move up a slice, x 3). The
    panel has no entry for a screw step yet; the engine takes it as a motion rule, which a script can set."""

    def cells_for(doc):
        cells = [symcases.feature(doc, n, extruded(f, 0, SLICE)) for n, f in slice_faces()]
        screw = motion(
            symmetry.translation([0, 0, SLICE]), symmetry.rotation_about([0, 0, 0], [0, 0, 1], SKEW), count=3
        )
        return cells, [rotate(45, 8), screw], {1: {"mode": "across", "across": [1]}}  # a pole's magnet slices: one part

    return skewed("M3_03", cells_for)


def m3_03_static():
    """The rotor of M3-03 alone, as the catalogue draws it: one slice of iron (R 8..25) and magnet (R 25..27.5,
    -18..18°), Rotate Z 45° x 8, then the screw step (turn 6° and move up a slice, x 3) as a motion rule; a pole's
    three magnet slices are one part (across rule 2). Static, in a drawn air cylinder, no stator and no sliding: this
    row checks that the engine takes a screw step (spec 2: only its panel entry is Later)."""
    doc, study = new_study("M3_03s", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    cells = [
        symcases.feature(doc, "RotorIron", extruded(sector(8, 25, -22.5, 22.5), 0, SLICE)),
        symcases.feature(doc, "Magnet", extruded(sector(25, 27.5, -18, 18), 0, SLICE)),
    ]
    screw = motion(symmetry.translation([0, 0, SLICE]), symmetry.rotation_about([0, 0, 0], [0, 0, 1], SKEW), count=3)
    rows = {1: {"mode": "across", "across": [1]}}
    make_group(study, "Rotor", cells, [rotate(45, 8), screw], [lib["Steel"], lib["Steel"]], rows)
    air = symcases.add_air_region(study, lib["Air"], shape=Part.makeCylinder(34, L + 8, V(0, 0, -4)))
    sizes(study, [(air, 3.0)])
    return study


def m3_03_cells():
    """What a user does with the panel instead: the three slices drawn as cell objects, each turned 6° and raised a
    slice from the one below, with Rotate Z 45° x 8 only. A pole's three magnet slices are one part (one name in
    three tables), and so are the iron, air and layer slices."""

    def cells_for(doc):
        cells = []
        for s in range(3):
            turn = App.Placement(V(), App.Rotation(V(0, 0, 1), SKEW * s)).toMatrix()
            for n, f in slice_faces():
                shape = extruded(f, s * SLICE, (s + 1) * SLICE).transformed(turn)
                cells.append(symcases.feature(doc, f"{n}{s + 1}", shape))
        rows = {}
        for i, c in enumerate(cells):
            base = c.Label.rstrip("0123456789")
            rows[i] = table(f"Magnet{k + 1}" for k in range(8)) if base == "Magnet" else table([base] * 8)
        return cells, [rotate(45, 8)], rows

    return skewed("M3_03c", cells_for)


def m3_03_band():
    """M3-03-cells after the refusal, drawn so that no structured face is touched in part: the slices hold the iron,
    the magnet and the air between magnets (R 25..27.5, 18..27°); the air band 27.5..28 and the structured layer
    28..28.5 are not skewed and run the whole stack (-22.5..22.5°)."""

    def cells_for(doc):
        cells = []
        for s in range(3):
            turn = App.Placement(V(), App.Rotation(V(0, 0, 1), SKEW * s)).toMatrix()
            for n, f in [*slice_faces()[:2], ("GapAir", sector(25, 27.5, 18, 27))]:
                shape = extruded(f, s * SLICE, (s + 1) * SLICE).transformed(turn)
                cells.append(symcases.feature(doc, f"{n}{s + 1}", shape))
        cells.append(symcases.feature(doc, "RotorAir", extruded(sector(27.5, 28, -22.5, 22.5), 0, L)))
        cells.append(symcases.feature(doc, "RotorLayer", extruded(sector(28, 28.5, -22.5, 22.5), 0, L)))
        rows = {}
        for i, c in enumerate(cells):
            base = c.Label.rstrip("0123456789")
            rows[i] = table(f"Magnet{k + 1}" for k in range(8)) if base == "Magnet" else table([base] * 8)
        return cells, [rotate(45, 8)], rows

    return skewed("M3_03b", cells_for)


# --- M3-04: axial flux, one stator between two rotors -----------------------------------------------------------------


def axial(name, moving):
    """Stator: half a tooth (R 16..34, 0..8°, z 0..4) and a coil side (8.6..14.6°, z 0..3.4), Mirror y = 0, Mirror
    z = 0, Rotate Z 30° x 12; the tooth one part per rotation, the coil side across the z mirror. Rotors: back iron
    (z 7.2..9) and a magnet (0..18°, z 5..7.2), Mirror y = 0, Rotate Z 45° x 8, Mirror z = 0 (the other rotor); the back
    iron one part per rotor, the magnet across the y mirror. moving: the rotors slide behind an Axial gap interface at
    z = 4.5, with the air of the gap a copied disc on each side (4..4.5 and 4.5..5); else the air is one drawn
    cylinder over everything.

    The moving Study is not a valid sliding drawing: its gap discs are unstructured, and the mirrored rotor would need
    two interfaces (z = 4.5 and z = -4.5) where it has one. It is there only to show that Validate refuses Axial
    sliding, which comes first."""
    doc, study = new_study(name, "3D", "Sliding motion" if moving else "No movement", 1.5)
    lib = symcases.libraries(study)
    cells = [
        symcases.feature(doc, "Tooth", extruded(sector(16, 34, 0, 8), 0, 4)),
        symcases.feature(doc, "CoilSide", extruded(sector(17, 33, 8.6, 14.6), 0, 3.4)),
    ]
    mats = [lib["Steel"], lib["Copper"]]
    if moving:
        cells.append(symcases.feature(doc, "StatorGapAir", extruded(sl.pie(40, 0, 15), 4, 4.5)))
        mats.append(lib["Air"])
    rows = {0: {"mode": "across", "across": [0, 1]}, 1: {"mode": "across", "across": [1]}}
    make_group(study, "Stator", cells, [MIRROR_Y, MIRROR_Z, rotate(30, 12)], mats, rows)
    cells = [
        symcases.feature(doc, "BackIron", extruded(sector(16, 34, 0, 22.5), 7.2, 9)),
        symcases.feature(doc, "Magnet", extruded(sector(17, 33, 0, 18), 5, 7.2)),
    ]
    mats = [lib["Steel"], lib["Steel"]]
    if moving:
        cells.append(symcases.feature(doc, "RotorGapAir", extruded(sl.pie(40, 0, 22.5), 4.5, 5)))
        mats.append(lib["Air"])
    rows = {0: {"mode": "across", "across": [0, 1]}, 1: {"mode": "across", "across": [0]}}
    side = "Moving" if moving else "Fixed"
    make_group(study, "Rotors", cells, [MIRROR_Y, rotate(45, 8), MIRROR_Z], mats, rows, side)
    if moving:
        symcases.add_free(study, "StatorAir", Part.makeCylinder(40, 8, V(0, 0, -4)), lib["Air"])
        for z in (5, -12):
            symcases.add_free(study, "RotorAir", Part.makeCylinder(40, 7, V(0, 0, z)), lib["Air"], side="Moving")
        objects.make_sliding_interface(study, "Axial gap", Position=4.5, Divisions=144, CrossDivisions=8)
    else:
        air = symcases.add_air_region(study, lib["Air"], shape=Part.makeCylinder(40, 24, V(0, 0, -12)))
        sizes(study, [(air, 3.0)])
    return study


def m3_04():
    return axial("M3_04", True)


def m3_04_static():
    return axial("M3_04s", False)


# --- M3-05: claw-pole rotor ---------------------------------------------------------------------------------------------


def m3_05():
    """One N claw and its disc sector (a disc -30..30°, R 8..19, z 0..3, and a claw lofted from 27° wide at z 3 to 9°
    at z 15, R 16..19), Rotate Z 60° x 6, then the catalogue's mirror in z = 9.5 and turn 30° as one step, x 2: the S
    half. The panel has no entry for that step yet; the engine takes it as a motion rule. Parts: N and S by a table.
    Static, in a drawn air cylinder."""
    doc, study = new_study("M3_05", "3D", "No movement", 1.5)
    lib = symcases.libraries(study)

    def wire(a, z):
        return Part.Wire(sector(16, 19, -a, a).translated(V(0, 0, z)).Edges)

    claw = Part.makeLoft([wire(13.5, 3), wire(4.5, 15)], True, True)
    body = extruded(sector(8, 19, -30, 30), 0, 3).fuse(claw).removeSplitter()
    assert len(body.Solids) == 1
    cell = symcases.feature(doc, "ClawAndDisc", body.Solids[0])
    flip = symmetry.rule_matrix(mirror((0, 0, 1), (0, 0, 9.5)))
    step = motion(symmetry.rotation_about([0, 0, 0], [0, 0, 1], 30), flip, count=2)
    make_group(study, "Rotor", [cell], [rotate(60, 6), step], [lib["Steel"]], {0: table(["N"] * 6 + ["S"] * 6)})
    air = symcases.add_air_region(study, lib["Air"], shape=Part.makeCylinder(24, 26, V(0, 0, -3.5)))
    sizes(study, [(air, 2.5)])
    return study


# --- M3-06: cage rotor, the bars and end rings one part --------------------------------------------------------------


def m3_06():
    """24 slots, 18 bars, half the stack (z 0..7, end rings to 10) mirrored at z = 0. Rotor: Rotate Z 20° x 18, then
    Mirror z = 0, as the catalogue orders them; the bar and the end-ring sector have one name, Cage, in their tables:
    one part across two objects. The stator's gap air and layer reach z 10 like the rotor's, and the stator's end
    space (R 30..50, z 7..10) is air of the cell."""
    doc, study = new_study("M3_06", "3D", "Sliding motion", 2.0)
    lib = symcases.libraries(study)
    half, top = 7.0, 10.0
    turn = rotate(15, 24)
    stator = sl.stator_slot_3d(doc, 15, half, [])
    for n, f, z0 in (
        ("StatorLayer", sector(28.5, 29, 0, 15), 0),
        ("StatorGap", sector(29, 30, 0, 15), 0),
        ("StatorEnd", sector(30, 50, 0, 15), half),
    ):
        stator.append(symcases.feature(doc, n, extruded(f, z0, top)))
    mats = [lib[k] for k in ("Steel", "Air", "Copper", "Copper", "Air", "Air", "Air")]
    rows = {2: winding(turn, 24, 2, 5, "top"), 3: winding(turn, 24, 2, 5, "bottom")}
    make_group(study, "Stator", stator, [MIRROR_Z, turn], mats, rows)
    bar = sl.disc(P(22, 0), 1.8)
    rotor = [
        symcases.feature(doc, "RotorIron", extruded(cut(sector(8, 25, -10, 10), bar), 0, half)),
        symcases.feature(doc, "Bar", extruded(bar, 0, half)),
        symcases.feature(doc, "EndRing", extruded(sector(19, 25, -10, 10), half, top)),
        symcases.feature(doc, "RotorEndAir", extruded(sector(8, 19, -10, 10), half, top)),
        symcases.feature(doc, "RotorAir", extruded(sector(25, 28, -10, 10), 0, top)),
        symcases.feature(doc, "RotorLayer", extruded(sector(28, 28.5, -10, 10), 0, top)),
    ]
    mats = [lib[k] for k in ("Steel", "Copper", "Copper", "Air", "Air", "Air")]
    cage = table(["Cage"] * 36)
    make_group(study, "Rotor", rotor, [rotate(20, 18), MIRROR_Z], mats, {1: cage, 2: cage}, "Moving")
    objects.make_sliding_interface(study, "Rotational", Radius=28.5, Divisions=144, CrossDivisions=10)
    symcases.transfinite_layer(study, stator[4], 6, 5)  # 144 / 24, 10 / 2 halves
    symcases.transfinite_layer(study, rotor[5], 8, 5)  # 144 / 18
    sizes(study, [(stator[5], 0.8), (rotor[4], 1.2)])
    return study


# --- M3-08: the stator in a frame with four feet ------------------------------------------------------------------------


def m3_08():
    """The M3-01 stator (Rotate Z 7.5° x 48) inside a frame: a quarter shell R 50..53 (-45..45°, z -3..17) and a foot
    below it, Rotate Z 90° x 4. The frame lies on the stator's outside: two groups with different repeats touch. Static,
    in a drawn air cylinder."""
    doc, study = new_study("M3_08", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    stator48(doc, study, lib, L, layer=False)
    foot = Part.Face(
        Part.Wire(
            [
                Part.Arc(P(53, -8), P(53, 0), P(53, 8)).toShape(),
                Part.LineSegment(P(53, 8), V(60, 6, 0)).toShape(),
                Part.LineSegment(V(60, 6, 0), V(60, -6, 0)).toShape(),
                Part.LineSegment(V(60, -6, 0), P(53, -8)).toShape(),
            ]
        )
    )
    cells = [
        symcases.feature(doc, "FrameShell", extruded(sector(50, 53, -45, 45), -3, L + 3)),
        symcases.feature(doc, "Foot", extruded(foot, -3, L + 3)),
    ]
    make_group(study, "Frame", cells, [rotate(90, 4)], [lib["Steel"], lib["Steel"]])
    air = symcases.add_air_region(study, lib["Air"], shape=Part.makeCylinder(66, L + 12, V(0, 0, -6)))
    sizes(study, [(air, 8.0)])
    return study


# --- M3-09: the stator in a normally meshed air box ---------------------------------------------------------------------


def m3_09():
    """The M3-01 stator (Rotate Z 7.5° x 48) in a drawn box of air, -62..62 x -62..62 x -14..28, meshed normally around
    the copies (the Air Region, Custom on the box). Static."""
    doc, study = new_study("M3_09", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    stator48(doc, study, lib, L, layer=False)
    air = symcases.add_air_region(study, lib["Air"], shape=Part.makeBox(124, 124, 42, V(-62, -62, -14)))
    sizes(study, [(air, 8.0)])
    return study


CASES = [
    ("M3-01", m3_01, "meshes"),
    (
        "M3-01-structured",
        m3_01_structured,
        "meshes",
        Structured(dict.fromkeys(("Top", "Bottom", "StatorLayer", "RotorLayer"), "hexahedra")),
    ),
    ("M3-02", sl.m3_02, "meshes"),
    ("M3-03", m3_03, ("refused", "Rule 2 (motion) is not a rotation about Z")),
    ("M3-03-static", m3_03_static, "meshes"),
    ("M3-03-cells", m3_03_cells, ("refused", "would have to be split where a copy touches part of its face")),
    ("M3-03-band", m3_03_band, "meshes"),
    (
        "M3-04",
        m3_04,
        (
            "refused",
            "slides Rotational only. Axial gap sliding with Symmetric Groups is not handled yet, a limit of the tool",
        ),
    ),
    ("M3-04-static", m3_04_static, "meshes"),
    ("M3-05", m3_05, "meshes"),
    ("M3-06", m3_06, "meshes"),
    ("M3-07", sl.m3_07, "meshes"),
    (
        "M3-08",
        m3_08,
        (
            "refused",
            "touch directly are not handled yet, a limit of the tool, not of the drawing: put them in one group, or"
            " draw a normally meshed body between them",
        ),
    ),
    ("M3-09", m3_09, "meshes"),
    ("M3-10", sl.m3_10, "meshes"),
    ("M3-12", sl.m3_12, "meshes"),
]
