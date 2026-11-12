"""2D motors M2-01 to M2-18. Each Study is an XY Study of Symmetric Groups; the rotor is moving behind a Rotational
Sliding Interface at R 28.75 wherever the catalogue's rotor moves (the stator's gap band and the rotor's air band are
the copied cells that cover it, spec 7.5). M2-01-structured is M2-01 with structured blocks beside the others;
motor_sliding-air is the success list's motor_sliding in a ring Air Region. CASES lists (id, builder, expected[,
check]) in catalogue order."""

import math

from common import (
    MIRROR_Y,
    P,
    RI,
    RO,
    RR,
    RS,
    RY,
    V,
    cut,
    disc,
    distributed,
    make_group,
    mirror,
    new_study,
    objects,
    outline,
    polygon,
    rotate,
    sector,
    sl,
    sliding,
    surface_rotor,
    symcases,
    table,
    v_rotor,
    winding,
    SECTORS,
    coil_sector,
    Part,
    Structured,
    structure,
)


def motor(name, slots, pole_pairs, span, poles, size=1.0):
    """A distributed two-layer stator over a surface-magnet rotor, sliding."""
    doc, study = new_study(name, "2D", "Sliding motion", size)
    lib = symcases.libraries(study)
    distributed(doc, study, lib, slots, pole_pairs, span)
    surface_rotor(doc, study, lib, poles)
    sliding(study)
    return study


def m2_01():
    return motor("M2_01", 48, 4, 5, 8)


def arcs_and_lines(body):
    """The kind of each edge of an annular sector face: "arc" or "line"."""
    return ["arc" if isinstance(e.Curve, Part.Circle) else "line" for e in body.Shape.Edges]


def m2_01_structured():
    """M2-01 with the stator's gap band (R 28.75..30) and both coil sides as structured, recombined blocks: 3 elements
    on each arc (the 144 divisions of the sliding interface over the 48 slot pitches), 2 across the band, 5 across a
    coil side. The iron, the slot air and the rotor stay unstructured. The band's outer arc is split where the teeth
    and the slot opening meet it; its 3 elements are shared out over the pieces."""
    study = motor("M2_01_structured", 48, 4, 5, 8)
    (iface,) = objects.sliding_interfaces(study)
    gap, _, _, top, bottom = objects.symmetric_groups(study)[0].Cells
    structure(study, gap, arcs_and_lines(gap), {"arc": iface.Divisions // 48, "line": 2})
    for side in (top, bottom):
        structure(study, side, arcs_and_lines(side), {"arc": 3, "line": 5})
    return study


# --- M2-02: single layer, the coil of a slot named by its phase belt ------------------------------------------------


def m2_02():
    doc, study = new_study("M2_02", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    pitch, th = 10, 2
    r1, r2 = RI + (RY - RI) * 0.16, RY - (RY - RI) * 0.06
    slot = sector(RI, RY, th, pitch - th)
    coil = sector(r1, r2, th * 1.2, pitch - th * 1.2)
    cells = [
        symcases.feature(doc, "Gap", sector(RS, RI, 0, pitch)),
        symcases.feature(doc, "Iron", cut(sector(RI, RO, 0, pitch), slot)),
        symcases.feature(doc, "SlotAir", cut(slot, coil)),
        symcases.feature(doc, "Coil", coil),
    ]
    mats = [lib["Air"], lib["Steel"], lib["Air"], lib["Copper"]]
    belts = table(SECTORS[(k // 3) % 6] for k in range(36))  # slots 1-3, 4-6, ...
    make_group(study, "Stator", cells, [rotate(pitch, 36)], mats, {3: belts})
    v_rotor(doc, study, lib)
    sliding(study)
    return study


# --- M2-03: spoke magnets cut by the mirror line --------------------------------------------------------------------


def m2_03():
    doc, study = new_study("M2_03", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    distributed(doc, study, lib, 30, 5, 3)
    spoke = polygon([V(11, 0, 0), V(24, 0, 0), V(24, 1.6, 0), V(11, 1.6, 0)])
    cells = [
        symcases.feature(doc, "RotorAir", sector(RR, RS, 0, 18)),
        symcases.feature(doc, "RotorIron", cut(sector(8, RR, 0, 18), spoke)),
        symcases.feature(doc, "HalfSpoke", spoke),
    ]
    mats = [lib["Air"], lib["Steel"], lib["Steel"]]
    polarity = table("MagN" if (c // 2) % 2 == 0 else "MagS" for c in range(20))  # copy = mirror + 2 * rotation
    make_group(study, "Rotor", cells, [MIRROR_Y, rotate(36, 10)], mats, {2: polarity}, "Moving")
    sliding(study)
    return study


# --- M2-04: notched rotor, rotation only -----------------------------------------------------------------------------


def m2_04():
    doc, study = new_study("M2_04", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    distributed(doc, study, lib, 36, 4, 4)
    iron = outline((8, 0), (8, 45), (RR, 45), (RR, 34), (RR - 1.8, 34), (RR - 1.8, 26), (RR, 26), (RR, 0))
    c, a = P(19, 13), math.radians(13)
    u, w = V(math.cos(a), math.sin(a), 0), V(-math.sin(a), math.cos(a), 0)
    magnet = polygon([c + u * 4 * sa + w * 1.1 * sb for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    cells = [
        symcases.feature(doc, "RotorAir", cut(sector(RR - 1.8, RS, 0, 45), iron)),
        symcases.feature(doc, "RotorIron", cut(iron, magnet)),
        symcases.feature(doc, "Magnet", magnet),
    ]
    mats = [lib["Air"], lib["Steel"], lib["Steel"]]
    make_group(study, "Rotor", cells, [rotate(45, 8)], mats, {2: {"mode": "each"}}, "Moving")
    sliding(study)
    return study


# --- M2-05: induction motor, 24 slots and 18 bars ---------------------------------------------------------------------


def m2_05():
    doc, study = new_study("M2_05", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    distributed(doc, study, lib, 24, 2, 5)
    bar = disc(P(22.5, 0), 1.8)
    cells = [
        symcases.feature(doc, "RotorAir", sector(RR, RS, -10, 10)),
        symcases.feature(doc, "RotorIron", cut(sector(8, RR, -10, 10), bar)),
        symcases.feature(doc, "Bar", bar),
    ]
    mats = [lib["Air"], lib["Steel"], lib["Copper"]]
    make_group(study, "Rotor", cells, [rotate(20, 18)], mats, {2: {"mode": "each"}}, "Moving")
    sliding(study)
    return study


# --- M2-06: switched reluctance 12/8, concentrated coils --------------------------------------------------------------


def m2_06():
    doc, study = new_study("M2_06", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    iron = outline((RI, 0), (RI, 7), (RY, 7), (RY, 15), (RO, 15), (RO, 0))
    coil = sector(RI + 2, RY - 1, 8, 14.3)
    cells = [
        symcases.feature(doc, "Air", cut(sector(RS, RY, 0, 15), iron, coil)),
        symcases.feature(doc, "Iron", iron),
        symcases.feature(doc, "CoilSide", coil),
    ]
    mats = [lib["Air"], lib["Steel"], lib["Copper"]]
    # six parts: phase (the rotation, k mod 3) x direction (the mirror copy); copy = mirror + 2 * rotation
    sides = table(f"Ph{(c // 2) % 3 + 1}{'+' if c % 2 == 0 else '-'}" for c in range(24))
    make_group(study, "Stator", cells, [MIRROR_Y, rotate(30, 12)], mats, {2: sides})
    rotor = outline((8, 0), (8, 22.5), (19, 22.5), (19, 11), (RR, 11), (RR, 0))
    cells = [
        symcases.feature(doc, "RotorAir", cut(sector(19, RS, 0, 22.5), rotor)),
        symcases.feature(doc, "RotorIron", rotor),
    ]
    make_group(study, "Rotor", cells, [MIRROR_Y, rotate(45, 8)], [lib["Air"], lib["Steel"]], side="Moving")
    sliding(study)
    return study


# --- M2-07: Halbach rotor over a slotless winding ---------------------------------------------------------------------


def m2_07():
    doc, study = new_study("M2_07", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    block = sector(31, 37, 0.5, 9.5)
    cells = [
        symcases.feature(doc, "Yoke", sector(38, 45, 0, 10)),
        symcases.feature(doc, "WindingBlock", block),
        symcases.feature(doc, "StatorAir", cut(sector(RS, 38, 0, 10), block)),
    ]
    mats = [lib["Steel"], lib["Copper"], lib["Air"]]
    make_group(study, "Stator", cells, [rotate(10, 36)], mats, {1: {"mode": "each"}})
    magnet = sector(22, 27, 0.4, 14.6)
    cells = [
        symcases.feature(doc, "Hub", sector(8, 22, 0, 15)),
        symcases.feature(doc, "MagnetBlock", magnet),
        symcases.feature(doc, "RotorAir", cut(sector(22, RS, 0, 15), magnet)),
    ]
    mats = [lib["Steel"], lib["Steel"], lib["Air"]]
    make_group(study, "Rotor", cells, [rotate(15, 24)], mats, {1: {"mode": "each"}}, "Moving")
    sliding(study)
    return study


# --- M2-08: 9 slots, 8 poles, concentrated coils side by side ---------------------------------------------------------


def m2_08():
    doc, study = new_study("M2_08", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    iron = outline((RI, 0), (RI, 8.4), (RY, 8.4), (RY, 20), (RO, 20), (RO, 0))
    coil = sector(RI + 1.92, RY - 0.72, 9.79, 19.2)
    cells = [
        symcases.feature(doc, "Air", cut(sector(RS, RY, 0, 20), iron, coil)),
        symcases.feature(doc, "Iron", iron),
        symcases.feature(doc, "CoilSide", coil),
    ]
    mats = [lib["Air"], lib["Steel"], lib["Copper"]]
    # the winding table of tooth k (the rotation), the other direction on the mirror copy
    sides = table(SECTORS[(coil_sector(c // 2, 9, 4) + 3 * (c % 2)) % 6] for c in range(18))
    make_group(study, "Stator", cells, [MIRROR_Y, rotate(40, 9)], mats, {2: sides})
    surface_rotor(doc, study, lib, 8)
    sliding(study)
    return study


# --- M2-09: one coil removed (left for later: removing one copy) ------------------------------------------------------


def m2_09():
    """Coil 4 has its top side in slot 4 and its bottom side in slot 9 (span 5). A user takes it out of the winding
    tables by emptying the name of those two copies."""
    doc, study = new_study("M2_09", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    distributed(doc, study, lib, 48, 4, 5, blank={"top": {4}, "bottom": {9}})
    surface_rotor(doc, study, lib, 8)
    sliding(study)
    return study


def m2_10():
    """One magnet demagnetised: its copy has a part (and so a Material) of its own, the mesh is unchanged."""
    doc, study = new_study("M2_10", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    distributed(doc, study, lib, 48, 4, 5)
    names = table("MagBad" if c // 2 == 3 else "MagGood" for c in range(16))
    surface_rotor(doc, study, lib, 8, magnet_row=names)
    sliding(study)
    return study


# --- M2-11: eccentric rotor, its own rotation centre -----------------------------------------------------------------

ECC = V(2.2, 1.0, 0)


def m2_11():
    """The rotor turns about (2.2, 1.0), the uneven gap is the Air Region, Custom on a disc R 50 (the
    stator outside) that gives way to the copies of both groups. Static, as the two groups meet no sliding surface."""
    doc, study = new_study("M2_11", "2D", "No movement", 1.5)
    lib = symcases.libraries(study)
    distributed(doc, study, lib, 48, 4, 5, gap=False)
    magnet = sector(RR, 27.5, 0, 17.5).translated(ECC)
    cells = [
        symcases.feature(doc, "RotorIron", sector(8, RR, 0, 22.5).translated(ECC)),
        symcases.feature(doc, "Magnet", magnet),
    ]
    about = {"point": list(ECC), "axis": [0, 0, 1]}
    rules = [mirror((0, 1, 0), (2.2, 1.0, 0)), {"kind": "rotate", "step": 45, "count": 8, **about}]
    make_group(study, "Rotor", cells, rules, [lib["Steel"], lib["Steel"]], {1: {"mode": "across", "across": [0]}})
    symcases.add_air_region(study, lib["Air"], shape=disc(V(0, 0, 0), RO))
    return study


# --- M2-12: a quarter of the machine, 12 of 48 slots and 2 of 8 poles -------------------------------------------------


def quarter(name, moving, air=False):
    """The stator turns 7.5 deg x 12 and the rotor, a half pole mirrored at the line of 22.5 deg, 45 deg x 2: 90 deg.
    moving: the sliding gap (stator band and rotor air band, a sliding interface); else an Air Region on a
    sector R 8..50, 0..90 deg that gives way to the copies: the gap. air (moving): an Air Region on a disc R 55 too."""
    doc, study = new_study(name, "2D", "Sliding motion" if moving else "No movement", 1.0)
    lib = symcases.libraries(study)
    distributed(doc, study, lib, 48, 4, 5, gap=moving, count=12)
    a = math.radians(22.5)
    magnet = sector(RR, 27.5, 5, 22.5)  # the half pole drawn from the other end: its magnet reaches the mirror line
    cells = [symcases.feature(doc, "RotorIron", sector(8, RR, 0, 22.5)), symcases.feature(doc, "Magnet", magnet)]
    mats = [lib["Steel"], lib["Steel"]]
    if moving:
        cells.append(symcases.feature(doc, "RotorAir", cut(sector(RR, RS, 0, 22.5), magnet)))
        mats.append(lib["Air"])
    rules = [mirror((-math.sin(a), math.cos(a), 0)), rotate(45, 2)]
    make_group(
        study, "Rotor", cells, rules, mats, {1: {"mode": "across", "across": [0]}}, "Moving" if moving else "Fixed"
    )
    if moving:
        sliding(study, [48, 16])
        if air:
            symcases.add_air_region(study, lib["Air"], shape=disc(V(0, 0, 0), RO + 5))
    else:
        symcases.add_air_region(study, lib["Air"], shape=sector(8, RO, 0, 90))
    return study


def m2_12():
    return quarter("M2_12", False)


def m2_12_sliding():
    return quarter("M2_12s", True)


def m2_12_sliding_air():
    """M2-12-sliding's Study with an Air Region on a disc R 55 over everything: it crosses the sliding circle, and
    with Symmetric Groups the air must keep clear of it."""
    return quarter("M2_12sa", True, air=True)


def motor_sliding_air():
    """The success list's motor_sliding (stator to R 60, rotor moving behind the interface at R 35) with a Sector Air
    Region R 60..90 outside the stator: the air lies on the fixed side, clear of the sliding surface."""
    study = sl.motor_sliding()
    symcases.add_air_region(study, symcases.libraries(study)["Air"], AirShape="Sector", InnerRadius=60, OuterRadius=90)
    return study


# --- M2-13: coaxial magnetic gear, three rings, two sliding surfaces --------------------------------------------------


def m2_13():
    doc, study = new_study("M2_13", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    magnet = sector(18, 21, 0.5, 44.5)
    cells = [
        symcases.feature(doc, "InnerHub", sector(8, 18, 0, 45)),
        symcases.feature(doc, "InnerMagnet", magnet),
        symcases.feature(doc, "InnerAir", cut(sector(18, 22.5, 0, 45), magnet)),
    ]
    mats = [lib["Steel"], lib["Steel"], lib["Air"]]
    polarity = table("MagN" if k % 2 == 0 else "MagS" for k in range(8))
    make_group(study, "Inner rotor", cells, [rotate(45, 8)], mats, {1: polarity}, "Moving")
    pitch = 360 / 21
    piece = sector(24, 30, 0.5, 9)
    cells = [
        symcases.feature(doc, "PoleAir", cut(sector(22.5, 33, 0, pitch), piece)),
        symcases.feature(doc, "PolePiece", piece),
    ]
    make_group(study, "Pole pieces", cells, [rotate(pitch, 21)], [lib["Air"], lib["Steel"]], {1: {"mode": "each"}})
    pitch = 360 / 34
    magnet = sector(36.4, 38, 0.3, pitch - 0.3)
    cells = [
        symcases.feature(doc, "OuterAir", cut(sector(33, 38, 0, pitch), magnet)),
        symcases.feature(doc, "OuterMagnet", magnet),
        symcases.feature(doc, "OuterYoke", sector(38, 42, 0, pitch)),
    ]
    mats = [lib["Air"], lib["Steel"], lib["Steel"]]
    polarity = table("MagN" if k % 2 == 0 else "MagS" for k in range(34))
    make_group(study, "Outer rotor", cells, [rotate(pitch, 34)], mats, {1: polarity}, "Moving")
    objects.make_sliding_interface(study, "Rotational", Radius=22.5, Divisions=168, Label="Inner sliding")
    objects.make_sliding_interface(study, "Rotational", Radius=33, Divisions=714, Label="Outer sliding")
    return study


# --- M2-14: linear motor with free end teeth --------------------------------------------------------------------------


def m2_14():
    """The primary (a half tooth mirrored at x = 0, 12 mm x 5) and the secondary (a magnet and the air beside it,
    10 mm x 7, polarity alternating) are groups; the two end teeth and the back iron are drawn bodies. The gap is a
    pair of copied air bands with a Linear interface between them."""
    doc, study = new_study("M2_14", "2D", "Sliding motion", 0.8)
    lib = symcases.libraries(study)

    def rect(x1, y1, x2, y2):
        return polygon([V(x1, y1, 0), V(x2, y1, 0), V(x2, y2, 0), V(x1, y2, 0)])

    tooth = polygon([V(*p, 0) for p in ((0, 0), (6, 0), (6, 4), (2.2, 4), (2.2, 12), (0, 12))])
    coil = rect(2.8, 4.6, 5.6, 11)
    cells = [
        symcases.feature(doc, "Iron", tooth),
        symcases.feature(doc, "SlotAir", cut(rect(2.2, 4, 6, 12), coil)),
        symcases.feature(doc, "Coil", coil),
        symcases.feature(doc, "PrimaryGap", rect(0, -1.5, 6, 0)),
    ]
    mats = [lib["Steel"], lib["Air"], lib["Copper"], lib["Air"]]
    mirror_x = mirror((1, 0, 0))
    move = {"kind": "translate", "vector": [12, 0, 0], "count": 5}
    make_group(study, "Primary", cells, [mirror_x, move], mats, {2: {"mode": "each"}})
    for name, x1, x2 in (("EndToothLeft", -14, -6), ("EndToothRight", 54, 62)):
        symcases.add_free(study, name, rect(x1, 0, x2, 12), lib["Steel"])
    magnet = rect(-13, -6.5, -5, -3)
    cells = [
        symcases.feature(doc, "Magnet", magnet),
        symcases.feature(doc, "MagnetGap", rect(-5, -6.5, -3, -3)),
        symcases.feature(doc, "SecondaryGap", rect(-13, -3, -3, -1.5)),
    ]
    polarity = table("MagN" if k % 2 == 0 else "MagS" for k in range(7))
    move = {"kind": "translate", "vector": [10, 0, 0], "count": 7}
    make_group(study, "Secondary", cells, [move], [lib["Steel"], lib["Air"], lib["Air"]], {0: polarity}, "Moving")
    symcases.add_free(study, "BackIron", rect(-14, -10, 62, -6.5), lib["Steel"], side="Moving")
    objects.make_sliding_interface(study, "Linear", Position=-1.5, NormalAxis="Y", MotionAxis="X", Divisions=60)
    return study


# --- M2-15 to M2-18: distributed and fractional windings ---------------------------------------------------------------


def m2_16():
    return motor("M2_16", 27, 3, 4, 6)


def m2_17():
    return motor("M2_17", 30, 2, 7, 4)


def m2_18():
    """M2-15's motor on a smaller cell: half a slot pitch drawn from the slot centre, mirrored at y = 0 and rotated.
    The two halves of a layer carry one name (the generator reads the slot from the first copy)."""
    doc, study = new_study("M2_18", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    pitch = 10
    half, th = pitch / 2, pitch * 0.2
    r1, r2 = RI + (RY - RI) * 0.16, RY - (RY - RI) * 0.06
    mid = (r1 + r2) / 2
    slot = sector(RI, RY, 0, half - th)
    top, bottom = sector(r1, mid - 0.2, 0, half - th * 1.2), sector(mid + 0.2, r2, 0, half - th * 1.2)
    cells = [
        symcases.feature(doc, "Gap", sector(RS, RI, 0, half)),
        symcases.feature(doc, "Iron", cut(sector(RI, RO, 0, half), slot)),
        symcases.feature(doc, "SlotAir", cut(slot, top, bottom)),
        symcases.feature(doc, "HalfTop", top),
        symcases.feature(doc, "HalfBottom", bottom),
    ]
    turn = rotate(pitch, 36)
    mats = [lib["Air"], lib["Steel"], lib["Air"], lib["Copper"], lib["Copper"]]
    rows = {3: winding(turn, 36, 2, 8, "top"), 4: winding(turn, 36, 2, 8, "bottom")}
    make_group(study, "Stator", cells, [MIRROR_Y, turn], mats, rows)
    v_rotor(doc, study, lib)
    sliding(study)
    return study


CASES = [
    ("M2-01", m2_01, "meshes"),
    (
        "M2-01-structured",
        m2_01_structured,
        "meshes",
        Structured(dict.fromkeys(("Gap", "Top", "Bottom"), "quadrangles")),
    ),
    ("M2-02", m2_02, "meshes"),
    ("M2-03", m2_03, "meshes"),
    ("M2-04", m2_04, "meshes"),
    ("M2-05", m2_05, "meshes"),
    ("M2-06", m2_06, "meshes"),
    ("M2-07", m2_07, "meshes"),
    ("M2-08", m2_08, "meshes"),
    (
        "M2-09",
        m2_09,
        (
            "refused",
            "An empty name would leave that copy out, and removing a copy is not handled yet, a limit of the tool",
        ),
    ),
    ("M2-10", m2_10, "meshes"),
    ("M2-11", m2_11, "meshes"),
    ("M2-12", m2_12, "meshes"),
    ("M2-12-sliding", m2_12_sliding, ("refused", "must cover the circle")),
    ("M2-12-sliding-air", m2_12_sliding_air, ("refused", "keep clear of the sliding surface")),
    ("motor_sliding-air", motor_sliding_air, "meshes"),
    ("M2-13", m2_13, ("refused", "only one Sliding Interface: more than one is not handled yet, a limit of the tool")),
    (
        "M2-14",
        m2_14,
        (
            "refused",
            "slides Rotational only. Linear sliding with Symmetric Groups is not handled yet, a limit of the tool",
        ),
    ),
    ("M2-15", sl.m2_15, "meshes"),
    ("M2-16", m2_16, "meshes"),
    ("M2-17", m2_17, "meshes"),
    ("M2-18", m2_18, "meshes"),
]
