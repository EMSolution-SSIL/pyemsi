"""Traps T-01 to T-07: drawings the tool has to catch. T-01 and T-02 mesh, with different drawings; T-03 meshes with a
warning; the others are refused, by Validate (T-04, T-05, T-07) or by the mesher (T-06). CASES lists (id, builder,
expected, check) in catalogue order; a check(study) gives (ok, text) on the built Study, and the row matches only
when it is ok."""

import math

from common import (
    App,
    MIRROR_X,
    MIRROR_Y,
    RI,
    RO,
    RR,
    RS,
    RY,
    cut,
    extruded,
    make_group,
    mirror,
    new_study,
    objects,
    outline,
    polygon,
    rotate,
    sector,
    symcases,
    V,
)
from emsolution import validation

MOVE = {"kind": "translate", "vector": [24, 0, 0], "count": 2}


# --- T-01 and T-02: the order of the rules ----------------------------------------------------------------------------


def order(name, rules):
    """A block (x 2..9, y -2..3), each copy its own part, in a drawn air rectangle that covers either order."""
    doc, study = new_study(name, "2D", "No movement", 0.8)
    lib = symcases.libraries(study)
    block = symcases.feature(doc, "Block", polygon([V(x, y, 0) for x, y in ((2, -2), (9, -2), (9, 3), (2, 3))]))
    make_group(study, "Part", [block], rules, [lib["Copper"]], {0: {"mode": "each"}})
    symcases.add_free(
        study, "Air", polygon([V(x, y, 0) for x, y in ((-40, -10), (40, -10), (40, 10), (-40, 10))]), lib["Air"]
    )
    return study


def t_01():
    """Mirror x = 0, then Translate (24, 0) x 2: blocks at x -9..-2, 2..9, 15..22, 26..33."""
    return order("T_01", [MIRROR_X, MOVE])


def t_02():
    """Translate (24, 0) x 2, then Mirror x = 0: blocks at x -33..-26, -9..-2, 2..9, 26..33."""
    return order("T_02", [MOVE, MIRROR_X])


def drawing(study):
    """(x range, sorted x of the block centres) of the group's drawing."""
    (item,) = objects.symmetric_groups(study)
    box = item.Shape.BoundBox
    return (round(box.XMin, 6), round(box.XMax, 6)), sorted(round(f.CenterOfMass.x, 6) for f in item.Shape.Faces)


def other_order(build):
    """A check: this Study's drawing differs from the one the other order (build) gives."""

    def check(study):
        mine = drawing(study)
        other = build()
        try:
            theirs = drawing(other)
        finally:
            App.closeDocument(other.Document.Name)

        def text(d):
            return f"x {d[0][0]:g}..{d[0][1]:g}, blocks at {', '.join(f'{x:g}' for x in d[1])}"

        same = "the same as" if mine == theirs else "differs from"
        return mine != theirs, f"drawing {text(mine)} {same} the other order's ({text(theirs)})"

    return check


# --- T-03: a rotation that does not close -----------------------------------------------------------------------------


def stator_half(doc, lib):
    """Half a slot pitch of a 12-slot stator (0..15°, the tooth on 0°): gap band, slot air, iron, coil side."""
    th = 15 * 0.42
    coil = sector(RI + (RY - RI) * 0.16, RY - (RY - RI) * 0.06, th + (15 - th) * 0.12, 15 * 0.96)
    cells = [
        symcases.feature(doc, "Gap", sector(RS, RI, 0, 15)),
        symcases.feature(doc, "SlotAir", cut(sector(RI, RY, th, 15), coil)),
        symcases.feature(doc, "Iron", outline((RI, 0), (RI, th), (RY, th), (RY, 15), (RO, 15), (RO, 0))),
        symcases.feature(doc, "CoilSide", coil),
    ]
    return cells, [lib["Air"], lib["Air"], lib["Steel"], lib["Copper"]]


def t_03():
    """Mirror y = 0, then Rotate Z 30° x 11: 330°, one slot pitch missing. Allowed with a warning (spec 4.1): the tool
    cannot tell a slip from a sector."""
    doc, study = new_study("T_03", "2D", "No movement", 1.0)
    lib = symcases.libraries(study)
    cells, mats = stator_half(doc, lib)
    make_group(study, "Stator", cells, [MIRROR_Y, rotate(30, 11)], mats, {3: {"mode": "each"}})
    return study


def warned(phrase):
    """A check: Validate gives a warning with phrase."""

    def check(study):
        objects.sync_parts(study)
        study.Document.recompute()
        found = [p.text for p in validation.validate(study) if p.severity != validation.ERROR]
        hit = [t for t in found if phrase in t]
        return bool(hit), "warning: " + (" | ".join(hit) if hit else f"none with '{phrase}' (warnings: {found})")

    return check


# --- T-04 and T-05: copies that overlap -------------------------------------------------------------------------------


def t_04():
    """The iron of T-03's half pitch and a coil (R 32..41, 5..18°) that reaches past the mirror line at 15°, cut out of
    the iron so that the two cell objects only touch. Mirror at the line of 15°, Rotate Z 30° x 12: the coil and its
    mirror image overlap (12..18°). Trimming at the plane is Later (spec 2)."""
    doc, study = new_study("T_04", "2D", "No movement", 1.0)
    lib = symcases.libraries(study)
    th = 15 * 0.42
    coil = sector(RI + 2, RY - 1, 5, 18)
    iron = cut(outline((RI, 0), (RI, th), (RY, th), (RY, 15), (RO, 15), (RO, 0)), coil)
    cells = [symcases.feature(doc, "Iron", iron), symcases.feature(doc, "CoilPastTheLine", coil)]
    a = math.radians(15)
    make_group(
        study,
        "Stator",
        cells,
        [mirror((-math.sin(a), math.cos(a), 0)), rotate(30, 12)],
        [lib["Steel"], lib["Copper"]],
        {1: {"mode": "each"}},
    )
    return study


def t_05():
    """A 30° yoke sector (R 30..48) rotated in 20° steps x 18: each copy overlaps the next."""
    doc, study = new_study("T_05", "2D", "No movement", 1.0)
    lib = symcases.libraries(study)
    yoke = symcases.feature(doc, "Yoke", sector(30, 48, 0, 30))
    make_group(study, "Stator", [yoke], [rotate(20, 18)], [lib["Steel"]])
    return study


# --- T-06: seams that do not match ------------------------------------------------------------------------------------


def t_06():
    """A yoke sector (R 30..45, 0..30°) whose edge on the 0° line is split at R 40 and whose edge on the 30° line is
    not, Rotate Z 30° x 12: a seam split on one side only. The seams are not paired (their lengths differ), so each is
    meshed on its own and the mesher refuses when the nodes do not meet (spec 7.2, step 6). Mesh size 1.5: at 1.0 both
    sides get a node at every whole radius, the copies join by chance and the mesh is right (checked: no boundary
    edge off R 30 and R 45, no doubled node)."""
    doc, study = new_study("T_06", "2D", "No movement", 1.5)
    lib = symcases.libraries(study)
    yoke = symcases.feature(doc, "Yoke", outline((30, 0), (30, 30), (45, 30), (45, 0), (40, 0)))
    assert len(yoke.Shape.Edges) == 5
    make_group(study, "Stator", [yoke], [rotate(30, 12)], [lib["Steel"]])
    return study


# --- T-07: sliding on a motor whose axis is X -------------------------------------------------------------------------


def t_07():
    """A motor with its shaft along X, as a user would try to slide it: the stator (gap band R 28.75..30, a slot pitch
    of iron 0..30° with its slot air, 14 long) Rotate X 30° x 12, and the moving rotor (iron R 8..25, air band to
    28.75, 0..45°) Rotate X 45° x 8, a Rotational Sliding Interface at R 28.75. Symmetry takes any axis; sliding is
    about Z only (spec 7.5), so the Sliding Interface refuses, naming the rule. The catalogue draws only the stator's
    iron; the rotor and the air bands are what a sliding Study needs besides."""
    doc, study = new_study("T_07", "3D", "Sliding motion", 3.0)
    lib = symcases.libraries(study)
    to_x = App.Placement(V(), App.Rotation(V(0, 1, 0), 90)).toMatrix()  # Z goes to X
    th = 30 * 0.2

    def body(name, face):
        return symcases.feature(doc, name, extruded(face, 0, 14).transformed(to_x))

    slot = sector(RI, RY, th, 30 - th)
    stator = [
        body("Gap", sector(RS, RI, 0, 30)),
        body("Iron", cut(sector(RI, RO, 0, 30), slot)),
        body("SlotAir", slot),
    ]
    make_group(study, "Stator", stator, [rotate(30, 12, (1, 0, 0))], [lib["Air"], lib["Steel"], lib["Air"]])
    rotor = [body("RotorIron", sector(8, RR, 0, 45)), body("RotorAir", sector(RR, RS, 0, 45))]
    make_group(study, "Rotor", rotor, [rotate(45, 8, (1, 0, 0))], [lib["Steel"], lib["Air"]], side="Moving")
    objects.make_sliding_interface(study, "Rotational", Radius=RS, Divisions=120, CrossDivisions=6)
    return study


CASES = [
    ("T-01", t_01, "meshes", other_order(t_02)),
    ("T-02", t_02, "meshes", other_order(t_01)),
    ("T-03", t_03, "meshes", warned("not 360")),
    ("T-04", t_04, ("refused", "overlaps a mirrored copy")),
    ("T-05", t_05, ("refused", "overlaps a copy turned by")),
    ("T-06", t_06, ("refused", "do not match")),
    ("T-07", t_07, ("refused", "Rule 1 (rotate) is not a rotation about Z")),
]
