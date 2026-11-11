"""The success list of the Symmetric Mesh by rules (spec section 8, item 2): each case is built in FreeCAD as a Study of
Symmetric Groups and free objects, validated, meshed by the add-on and read back. A row is OK when the Study validates,
the mesher runs and the mesh has 0 inverted elements, no facet in 3 or more elements and every frozen face kept.
Poor elements (min SICN below 0.1) are reported, not failed.

Run: pixi run -e addon python experiments/symmetric_rules/success_list.py [case ...]
Output: C:\\Users\\hamed\\Desktop\\delme\\rules_success\\<case>\\ (<case>.FCStd and the mesh files beside it)

The shapes follow the example catalogue loosely (the examples illustrate, nothing here is special to them). In 3D
sliding the air that forms the sliding surface is a structured, recombined layer of its own on each side, with
unstructured air between it and the teeth or magnets (spec 7.5)."""

import math
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "freecad_addon"))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiments", "symmetric_examples"))

import FreeCAD as App  # noqa: E402 - after the add-on path
import Part  # noqa: E402

import gmsh  # noqa: E402
import numpy as np  # noqa: E402

from emsolution import jobwriter, objects, validation  # noqa: E402
from tests.freecad_addon import meshreport, symcases  # noqa: E402
from tests.freecad_addon.symcases import extruded, sector  # noqa: E402
from tests.freecad_addon.test_rules_end_to_end import general_study  # noqa: E402

OUT = r"C:\Users\hamed\Desktop\delme\rules_success"
DATA = os.path.join(HERE, "data")
V = App.Vector


def P(r, a, z=0.0):
    return V(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), z)


def mirror(normal, point=(0, 0, 0)):
    return {"kind": "mirror", "point": list(point), "normal": list(normal)}


def rotate(step, count, axis=(0, 0, 1)):
    return {"kind": "rotate", "point": [0, 0, 0], "axis": list(axis), "step": step, "count": count}


MIRROR_Z, MIRROR_Y, MIRROR_X = mirror((0, 0, 1)), mirror((0, 1, 0)), mirror((1, 0, 0))


def polygon(points):
    return Part.Face(Part.makePolygon([*points, points[0]]))


def pie(r, a1, a2):
    """The circular sector from the centre, radius r, angles a1..a2."""
    am = (a1 + a2) / 2
    edges = [
        Part.LineSegment(V(0, 0, 0), P(r, a1)).toShape(),
        Part.Arc(P(r, a1), P(r, am), P(r, a2)).toShape(),
        Part.LineSegment(P(r, a2), V(0, 0, 0)).toShape(),
    ]
    return Part.Face(Part.Wire(edges))


def disc(centre, r):
    return Part.Face(Part.Wire(Part.makeCircle(r, centre)))


def cut(shape, *tools):
    """shape less tools, as one solid (one face in 2D)."""
    out = shape.cut(Part.makeCompound(list(tools)) if len(tools) > 1 else tools[0])
    pieces = out.Solids or out.Faces
    assert len(pieces) == 1, f"the cut left {len(pieces)} pieces"
    return pieces[0]


def new_study(name, dimension, movement="No movement", size=2.0):
    doc = App.newDocument(name)
    study = objects.make_study(doc, dimension, "Study", movement)
    study.MeshSizesGroup.DefaultMeshSize = size
    return doc, study


def sizes(study, by_cell):
    for cell, size in by_cell:
        objects.make_mesh_size(study, size, [(cell, "")])


def winding(rule, slots, pole_pairs, span=1, layer="top"):
    """Row change: a table of the three-phase winding generator (objects.winding_table)."""

    def change(item, r):
        table = objects.winding_table(item, r, rule, slots, pole_pairs, span, layer=layer)
        return {"mode": "table", "table": table}

    return change


# --- the sliding motor of experiments/symmetric_examples, redone with rules --------------------------------------


def motor_sliding():
    import build_examples

    doc, study, _ = build_examples.motor()
    return study


# --- M2-15: 36 slots, 4 poles, two layers, coil span 8 ------------------------------------------------------------


def stator_slot_2d(doc, pitch, rs, ri, ry, ro):
    """One slot pitch 0..pitch: gap band rs..ri, iron, slot air, top and bottom layer (coil sides)."""
    th = pitch * 0.2
    slot = sector(ri, ry, th, pitch - th)
    r1, r2 = ri + (ry - ri) * 0.16, ry - (ry - ri) * 0.06
    mid = (r1 + r2) / 2
    top = sector(r1, mid - 0.2, th * 1.2, pitch - th * 1.2)
    bottom = sector(mid + 0.2, r2, th * 1.2, pitch - th * 1.2)
    return [
        symcases.feature(doc, "Gap", sector(rs, ri, 0, pitch)),
        symcases.feature(doc, "Iron", cut(sector(ri, ro, 0, pitch), slot)),
        symcases.feature(doc, "SlotAir", cut(slot, top, bottom)),
        symcases.feature(doc, "Top", top),
        symcases.feature(doc, "Bottom", bottom),
    ]


def m2_15():
    doc, study = new_study("M2_15", "2D", "Sliding motion", 1.0)
    lib = symcases.libraries(study)
    turn = rotate(10, 36)
    cells = stator_slot_2d(doc, 10, 28.75, 30, 42, 50)
    mats = {"Gap": lib["Air"], "Iron": lib["Steel"], "SlotAir": lib["Air"], "Top": lib["Copper"]}
    mats["Bottom"] = lib["Copper"]
    rows = {"Top": winding(turn, 36, 2, 8, "top"), "Bottom": winding(turn, 36, 2, 8, "bottom")}
    symcases.group(study, "Stator", cells, [turn], rows, lib=mats)
    # rotor: half a pole 0..45 with one leg of a V magnet in the iron, mirrored at y = 0, then four poles
    c, u = P(18.5, 19), V(math.cos(math.radians(58)), math.sin(math.radians(58)), 0)
    w = V(-u.y, u.x, 0)
    leg = polygon([c + u * sa * 4.5 + w * sb * 1.2 for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    rotor = [
        symcases.feature(doc, "RotorAir", sector(25, 28.75, 0, 45)),
        symcases.feature(doc, "RotorIron", cut(sector(8, 25, 0, 45), leg)),
        symcases.feature(doc, "Magnet", leg),
    ]
    mats = {"RotorAir": lib["Air"], "RotorIron": lib["Steel"], "Magnet": lib["Steel"]}
    rows = {"Magnet": {"mode": "across", "across": [0]}}
    symcases.group(study, "Rotor", rotor, [MIRROR_Y, rotate(90, 4)], rows, side="Moving", lib=mats)
    objects.make_sliding_interface(study, "Rotational", Radius=28.75, Divisions=144)
    return study


# --- 3D motors: M3-02 (half stack, z mirror, sliding) and M3-07 (shaft along X, locked) ---------------------------


def stator_slot_3d(doc, pitch, z1, inner, ri=30, ry=42, ro=50, prefix=""):
    """stator_slot_2d's iron, slot air and layers over z 0..z1, and inner (the gap band and structured layer faces)."""
    faces = stator_slot_2d(doc, pitch, 29, ri, ry, ro)
    doc.removeObject(faces[0].Name)
    out = []
    for f in faces[1:]:
        f.Shape = extruded(f.Shape, 0, z1)
        f.Label = prefix + f.Label
        out.append(f)
    for name, face in inner:
        out.append(symcases.feature(doc, prefix + name, extruded(face, 0, z1)))
    return out


def m3_02():
    """48 slots, 8 poles, half the stack drawn (z 0..7) and mirrored at z = 0, sliding at R 28.5. The structured
    layers 28..28.5 (rotor) and 28.5..29 (stator) form the sliding cylinder; unstructured air lies between them and
    the teeth (29..30) or the magnets (25..28)."""
    doc, study = new_study("M3_02", "3D", "Sliding motion", 2.0)
    lib = symcases.libraries(study)
    half, turn = 7.0, rotate(7.5, 48)
    stator = stator_slot_3d(
        doc, 7.5, half, [("StatorLayer", sector(28.5, 29, 0, 7.5)), ("StatorGap", sector(29, 30, 0, 7.5))]
    )
    names = [c.Name for c in stator]
    mats = dict(zip(names, (lib[k] for k in ("Steel", "Air", "Copper", "Copper", "Air", "Air"))))
    rows = {names[2]: winding(turn, 48, 4, 5, "top"), names[3]: winding(turn, 48, 4, 5, "bottom")}
    symcases.group(study, "Stator", stator, [MIRROR_Z, turn], rows, lib=mats)
    magnet = sector(25, 27.5, 0, 17.5)
    rotor = [
        symcases.feature(doc, "RotorIron", extruded(sector(8, 25, 0, 22.5), 0, half)),
        symcases.feature(doc, "Magnet", extruded(magnet, 0, half)),
        symcases.feature(doc, "RotorAir", extruded(cut(sector(25, 28, 0, 22.5), magnet), 0, half)),
        symcases.feature(doc, "RotorLayer", extruded(sector(28, 28.5, 0, 22.5), 0, half)),
    ]
    mats = dict(zip([c.Name for c in rotor], (lib[k] for k in ("Steel", "Steel", "Air", "Air"))))
    rows = {"Magnet": {"mode": "across", "across": [0, 1]}}
    symcases.group(study, "Rotor", rotor, [MIRROR_Y, MIRROR_Z, rotate(45, 8)], rows, side="Moving", lib=mats)
    objects.make_sliding_interface(study, "Rotational", Radius=28.5, Divisions=144, CrossDivisions=8)
    symcases.transfinite_layer(study, doc.getObject(names[4]), 3, 4)  # 144 / 48 turns, 8 / 2 halves
    symcases.transfinite_layer(study, doc.getObject("RotorLayer"), 9, 4)  # 144 * 22.5 / 360
    sizes(study, [(doc.getObject(names[5]), 0.8), (doc.getObject("RotorAir"), 1.2)])
    return study


def m3_07():
    """M3-02's machine over the whole stack (z 0..14) turned so that its shaft lies along X: the stator rotated about
    X 7.5° x 48, the rotor mirrored at y = 0 and rotated about X 45° x 8, and the air gap (28..30) a drawn ring, in no
    group, flush against both."""
    doc, study = new_study("M3_07", "3D", "No movement", 2.0)
    lib = symcases.libraries(study)
    length, turn, x = 14.0, rotate(7.5, 48, (1, 0, 0)), (1, 0, 0)
    to_x = App.Placement(V(), App.Rotation(V(0, 1, 0), 90)).toMatrix()  # Z goes to X

    def along_x(objs):
        for o in objs:
            o.Shape = o.Shape.transformed(to_x)
        return objs

    stator = along_x(stator_slot_3d(doc, 7.5, length, []))
    names = [c.Name for c in stator]
    mats = dict(zip(names, (lib[k] for k in ("Steel", "Air", "Copper", "Copper"))))
    rows = {names[2]: winding(turn, 48, 4, 5, "top"), names[3]: winding(turn, 48, 4, 5, "bottom")}
    symcases.group(study, "Stator", stator, [turn], rows, lib=mats)
    magnet = sector(25, 27.5, 0, 17.5)
    rotor = [
        symcases.feature(doc, "RotorIron", extruded(sector(8, 25, 0, 22.5), 0, length)),
        symcases.feature(doc, "Magnet", extruded(magnet, 0, length)),
        symcases.feature(doc, "RotorAir", extruded(cut(sector(25, 28, 0, 22.5), magnet), 0, length)),
    ]
    along_x(rotor)
    mats = dict(zip([c.Name for c in rotor], (lib[k] for k in ("Steel", "Steel", "Air"))))
    rows = {"Magnet": {"mode": "across", "across": [0]}}
    symcases.group(study, "Rotor", rotor, [MIRROR_Y, rotate(45, 8, x)], rows, lib=mats)
    ring = Part.makeCylinder(30, length).cut(Part.makeCylinder(28, length)).transformed(to_x)
    symcases.add_free(study, "AirGap", ring, lib["Air"])
    sizes(study, [(study.Document.getObject("AirGap"), 1.0)])
    return study


# --- M3-10: distributed winding, whole curved coils pressed in the slots, drawn air -------------------------------


def m3_10():
    """24 slots, 4 poles, coil span 5: the half coil of data/distributed_half.brep (z >= 0) and a 15° iron wedge
    over the half stack (z 0..14), mirrored at z = 0, then rotated 15° x 24. Each slot is two pockets that fit the coil
    sides exactly (a top side of one coil and the bottom side of the coil five slots back), so the iron touches coil
    copies other than its own. The air is one drawn cylinder over everything."""
    doc, study = new_study("M3_10", "3D", "No movement", 5.0)
    lib = symcases.libraries(study)
    turn = rotate(15, 24)
    a = math.radians(7.5)
    er, et = V(math.cos(a), math.sin(a), 0), V(-math.sin(a), math.cos(a), 0)

    def pocket(s1, s2):  # the section of a coil side: 4 wide across the slot axis at 7.5°, s1..s2 along it
        return polygon([er * s + et * t for s, t in ((s1, -2), (s2, -2), (s2, 2), (s1, 2))])

    iron = symcases.feature(
        doc, "Iron", extruded(cut(sector(31, 50, 0, 15), pocket(32.25, 36.15), pocket(37.05, 40.95)), 0, 14)
    )
    coil = symcases.feature(doc, "HalfCoil", Part.read(os.path.join(DATA, "distributed_half.brep")).Solids[0])
    rows = {"HalfCoil": winding(turn, 24, 2, layer="whole")}
    symcases.group(
        study, "Stator", [iron, coil], [MIRROR_Z, turn], rows, lib={"Iron": lib["Steel"], "HalfCoil": lib["Copper"]}
    )
    sizes(study, [(iron, 2.5), (coil, 1.5)])
    symcases.add_free(study, "FreeAir", Part.makeCylinder(58, 92, V(0, 0, -46)), lib["Air"])
    return study


# --- M3-12: switched reluctance stator with curved tooth coils, a rotor, drawn air --------------------------------


def m3_12():
    """12 stator poles: an iron cell 0..15° over z 0..14 and a quarter coil (y >= 0, z >= 0) around the pole, mirrored
    at y = 0 and z = 0, then rotated 30° x 12; the coil's four quarters are one part. An 8-pole rotor of its own rules.
    Static: one drawn air cylinder holds both groups."""
    doc, study = new_study("M3_12", "3D", "No movement", 5.0)
    lib = symcases.libraries(study)
    b = 3.7  # half the pole width
    ain, aout = math.degrees(math.asin(b / 30)), math.degrees(math.asin(b / 42))
    wire = Part.Wire(
        [
            Part.Arc(P(30, 0), P(30, ain / 2), P(30, ain)).toShape(),
            Part.LineSegment(P(30, ain), P(42, aout)).toShape(),
            Part.Arc(P(42, aout), P(42, (aout + 15) / 2), P(42, 15)).toShape(),
            Part.LineSegment(P(42, 15), P(50, 15)).toShape(),
            Part.Arc(P(50, 15), P(50, 7.5), P(50, 0)).toShape(),
            Part.LineSegment(P(50, 0), P(30, 0)).toShape(),
        ]
    )
    iron = symcases.feature(doc, "StatorIron", extruded(Part.Face(wire), 0, 14))

    def yz(y, z):
        return V(31.5, y, z)

    def corner(cy, cz, r, a1, a2):
        am = (a1 + a2) / 2
        return Part.Arc(
            *(yz(cy + r * math.cos(math.radians(t)), cz + r * math.sin(math.radians(t))) for t in (a1, am, a2))
        )

    xi, xo, zi, zo, ri, ro = b + 0.4, b + 3.4, 16.5, 19.5, 3.5, 6.5
    xc, zc = xi - ri, zi - ri
    loop = Part.Wire(
        [
            Part.LineSegment(yz(xi, 0), yz(xo, 0)).toShape(),
            Part.LineSegment(yz(xo, 0), yz(xc + ro, zc)).toShape(),
            corner(xc, zc, ro, 0, 90).toShape(),
            Part.LineSegment(yz(xc, zo), yz(0, zo)).toShape(),
            Part.LineSegment(yz(0, zo), yz(0, zi)).toShape(),
            Part.LineSegment(yz(0, zi), yz(xc, zi)).toShape(),
            corner(xc, zc, ri, 90, 0).toShape(),
            Part.LineSegment(yz(xi, zc), yz(xi, 0)).toShape(),
        ]
    )
    coil = symcases.feature(doc, "QuarterCoil", Part.Face(loop).extrude(V(9.5, 0, 0)))
    rows = {"QuarterCoil": {"mode": "across", "across": [0, 1]}}
    mats = {"StatorIron": lib["Steel"], "QuarterCoil": lib["Copper"]}
    symcases.group(study, "Stator", [iron, coil], [MIRROR_Y, MIRROR_Z, rotate(30, 12)], rows, lib=mats)
    rotor = Part.Wire(
        [
            Part.Arc(P(8, 0), P(8, 11.25), P(8, 22.5)).toShape(),
            Part.LineSegment(P(8, 22.5), P(19, 22.5)).toShape(),
            Part.Arc(P(19, 22.5), P(19, 16.75), P(19, 11)).toShape(),
            Part.LineSegment(P(19, 11), P(25, 11)).toShape(),
            Part.Arc(P(25, 11), P(25, 5.5), P(25, 0)).toShape(),
            Part.LineSegment(P(25, 0), P(8, 0)).toShape(),
        ]
    )
    rotor = symcases.feature(doc, "RotorIron", extruded(Part.Face(rotor), 0, 14))
    symcases.group(study, "Rotor", [rotor], [MIRROR_Y, MIRROR_Z, rotate(45, 8)], lib={"RotorIron": lib["Steel"]})
    sizes(study, [(iron, 2.5), (coil, 1.5), (rotor, 2.5)])
    symcases.add_free(study, "FreeAir", Part.makeCylinder(58, 60, V(0, 0, -30)), lib["Air"])
    return study


# --- R-07: a rod in an air box, one eighth drawn ------------------------------------------------------------------


def r_07():
    doc, study = new_study("R_07", "3D", "No movement", 1.5)
    lib = symcases.libraries(study)
    rod = extruded(pie(4, 0, 90), 0, 16)
    cells = [
        symcases.feature(doc, "Rod", rod),
        symcases.feature(doc, "RodAir", cut(Part.makeBox(14, 14, 24), rod)),
    ]
    symcases.group(
        study, "Rod", cells, [MIRROR_X, MIRROR_Y, MIRROR_Z], lib={"Rod": lib["Copper"], "RodAir": lib["Air"]}
    )
    sizes(study, [(cells[1], 3.0)])
    return study


# --- L-06 and L-07: a 7 x 7 double-skew wire, skews in opposite directions ----------------------------------------


def litz(name, tables):
    """data/double_skew_opposite.brep: the straight strand on the axis is a group of its own with no rules; the 8
    strands whose centres lie between 15° and 75° are the cells of Rotate Z 60° x 6. tables: one part per bundle
    (L-07), else each strand separate (L-06). Air: one drawn cylinder."""
    doc, study = new_study(name, "3D", "No movement", 1.0)
    lib = symcases.libraries(study)
    solids = Part.read(os.path.join(DATA, "double_skew_opposite.brep")).Solids
    centre = next(s for s in solids if math.hypot(s.CenterOfMass.x, s.CenterOfMass.y) < 1e-6)
    window = [
        s
        for s in solids
        if s is not centre and 15 <= math.degrees(math.atan2(s.CenterOfMass.y, s.CenterOfMass.x)) % 360 < 75
    ]
    window.sort(key=lambda s: math.hypot(s.CenterOfMass.x, s.CenterOfMass.y))  # the ring strand of the centre first
    straight = symcases.feature(doc, "CentreStrand", centre)
    cells = [symcases.feature(doc, f"Strand{k + 1}", s) for k, s in enumerate(window)]
    copper = {c.Name: lib["Copper"] for c in [straight, *cells]}
    if tables:
        one = {"CentreStrand": {"mode": "table", "table": ["CentreBundle"]}}
        rows = {"Strand1": {"mode": "table", "table": ["CentreBundle"] * 6}}
        rows.update({c.Name: {"mode": "table", "table": [f"Bundle{k + 1}" for k in range(6)]} for c in cells[1:]})
    else:
        one, rows = {}, {c.Name: {"mode": "each"} for c in cells}
    symcases.group(study, "Centre", [straight], [], one, lib=copper)
    symcases.group(study, "Strands", cells, [rotate(60, 6)], rows, lib=copper)
    sizes(study, [(c, 0.35) for c in [straight, *cells]])
    symcases.add_free(study, "FreeAir", Part.makeCylinder(7.5, 36, V(0, 0, -3)), lib["Air"])
    return study


def l_06():
    return litz("L_06", tables=False)


def l_07():
    return litz("L_07", tables=True)


# --- D-07: three-core armoured cable (2D) and D-08: Helmholtz pair (2D ZX) -----------------------------------------


def d_07():
    """Three cores in their filler (Rotate Z 120° x 3) and 40 armour wires (Rotate Z 9° x 40) have no common repeat:
    the bedding, a drawn disc over both, joins them."""
    doc, study = new_study("D_07", "2D", "No movement", 0.8)
    lib = symcases.libraries(study)
    core = disc(P(8.5, 60), 5)
    cores = [symcases.feature(doc, "Filler", cut(pie(16, 0, 120), core)), symcases.feature(doc, "Core", core)]
    rows = {"Core": {"mode": "each"}}
    symcases.group(study, "Cores", cores, [rotate(120, 3)], rows, lib={"Filler": lib["Air"], "Core": lib["Copper"]})
    wire = symcases.feature(doc, "Wire", disc(P(21.6, 4.5), 1.5))
    symcases.group(study, "Armour", [wire], [rotate(9, 40)], {"Wire": {"mode": "each"}}, lib={"Wire": lib["Steel"]})
    symcases.add_free(study, "Bedding", disc(V(0, 0, 0), 25), lib["Air"])
    return study


def d_08():
    """Half the pair above z = 0 in an axisymmetric (ZX) Study, mirrored at z = 0: each coil its own part."""
    doc, study = new_study("D_08", "2D", "No movement", 1.0)
    lib = symcases.libraries(study)

    def rect(x1, z1, x2, z2):  # in the ZX plane, turned like Part.makePlane(..., V(0, -1, 0))
        return polygon([V(x1, 0, z1), V(x2, 0, z1), V(x2, 0, z2), V(x1, 0, z2)])

    coil = rect(14, 6.2, 18, 9.8)
    cells = [symcases.feature(doc, "Air", cut(rect(0, 0, 26, 22), coil)), symcases.feature(doc, "Coil", coil)]
    rows = {"Coil": {"mode": "each"}}
    symcases.group(study, "Half", cells, [MIRROR_Z], rows, lib={"Air": lib["Air"], "Coil": lib["Copper"]})
    return study


# --- the table -----------------------------------------------------------------------------------------------------


CASES = [
    ("motor_sliding", motor_sliding),
    ("M2-15", m2_15),
    ("M3-02", m3_02),
    ("M3-07", m3_07),
    ("M3-10", m3_10),
    ("M3-12", m3_12),
    ("R-07", r_07),
    ("L-06", l_06),
    ("L-07", l_07),
    ("D-07", d_07),
    ("D-08", d_08),
    ("general", lambda: general_study(App.newDocument("General"))),
]


def cylinder_faces(path, r):
    """(quadrangles, triangles): the element faces of a mesh file with all their nodes on the cylinder of radius r
    about Z."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        tags, xyz, _ = gmsh.model.mesh.getNodes()
        at = np.zeros((int(tags.max()) + 1, 3))
        at[tags.astype(np.int64)] = np.reshape(xyz, (-1, 3))
        on = np.abs(np.hypot(at[:, 0], at[:, 1]) - r) < 1e-6 * r
        found = {3: set(), 4: set()}
        for etype in gmsh.model.mesh.getElementTypes(3):
            _, conn = gmsh.model.mesh.getElementsByType(etype)
            conn = np.reshape(conn, (-1, gmsh.model.mesh.getElementProperties(etype)[3])).astype(np.int64)
            for f in meshreport.FACETS[etype]:
                c = conn[:, list(f)]
                found[len(f)].update(map(tuple, np.sort(c[on[c].all(axis=1)], axis=1)))
        return len(found[4]), len(found[3])
    finally:
        gmsh.finalize()


def sliding_faces(study):
    """The faces on the sliding cylinder of a 3D Study, per mesh file: quadrangles and triangles."""
    (iface,) = objects.sliding_interfaces(study)
    out = []
    for path in (jobwriter.mesh_file(study), jobwriter.rotor_file(study)):
        quads, tris = cylinder_faces(path, iface.Radius.Value)
        out.append(f"{os.path.basename(path)}: {quads} quadrangles, {tris} triangles")
    return "sliding cylinder " + ", ".join(out)


def run(name, build, path=None, setup=None):
    """One row: (name, verdict, details). path: where the document is saved and meshed (default:
    OUT/<name>/<name>.FCStd). setup: where a copy of the set-up document is also saved, before meshing."""
    study = None
    start = time.time()
    try:
        study = build()
        symcases.finish(study, path or os.path.join(OUT, name, name.replace("-", "_") + ".FCStd"))
        if setup:
            os.makedirs(os.path.dirname(setup), exist_ok=True)
            study.Document.saveCopy(setup)
        errors = validation.errors(validation.validate(study))
        if errors:
            return name, "refused", "validation: " + " | ".join(p.text for p in errors)
        r = symcases.mesh_and_read(study)
        if not r.ok:
            return name, "refused", "mesher: " + r.refused
        good = r.inverted == 0 and r.faces_in_three == 0 and r.frozen_kept
        types = ", ".join(f"{k} {v}" for k, v in sorted(r.types.items()))
        poor = sum(p for _, p, _ in r.poor)
        worst = max(r.poor, key=lambda p: p[1] / p[2], default=None)
        detail = (
            f"{types} | inverted {r.inverted}, facets in 3+ {r.faces_in_three}, frozen facets kept {r.kept}, lost"
            f" {r.lost} | poor {poor}" + (f" (most in {worst[0]}: {worst[1]} of {worst[2]})" if poor else "")
        )
        if study.Dimension == "3D" and study.Movement == "Sliding motion":
            detail += " | " + sliding_faces(study)
        if poor:
            detail += " | poor by part: " + ", ".join(f"{n} {p} of {t}" for n, p, t in r.poor)
        return name, "OK" if good else "FAILED", f"{detail} | {time.time() - start:.0f} s"
    except Exception as err:  # a case that cannot be built or written is a row, not the end of the list
        traceback.print_exc()
        return name, "refused", f"{type(err).__name__}: {err}"
    finally:
        if study is not None:
            App.closeDocument(study.Document.Name)


if __name__ == "__main__":
    wanted = sys.argv[1:]
    rows = []
    for name, build in CASES:
        if wanted and name not in wanted:
            continue
        rows.append(run(name, build))
        print(" | ".join(rows[-1]), flush=True)
    print("\nSuccess list")
    for name, verdict, detail in rows:
        print(f"{name:14s} {verdict:8s} {detail}")
