"""Example models for the Air Region (and later the sliding motion): built from Part primitives, meshed by the
real mesher in a subprocess, described by a report. Shared by test_examples.py and build_examples.py. Lengths in mm."""

import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable

import FreeCAD as App
import Part

from emsolution import airshapes, jobwriter, objects, validation

from . import meshreport
from .materialdata import STEEL, record

ADDON = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution"))
MESHERS = {"2D": os.path.join(ADDON, "mesher2d.py"), "3D": os.path.join(ADDON, "mesher.py")}


@dataclass
class Case:
    name: str
    build: Callable[[App.Document], object]  # builds the Study (bodies, material, air) in a new document
    checklist: list = field(default_factory=list)
    expect_error: str = ""  # E-cases: part of the error text Validate (or the mesher) must give


# ---- shapes

C_CORE = [(0, 0), (60, 0), (60, 10), (20, 10), (20, 40), (60, 40), (60, 50), (0, 50)]  # opens to +x
C_COIL = [(20, 10), (40, 10), (40, 40), (20, 40)]  # fills the window next to the left leg
CORE = [(0, 0), (20, 0), (20, 20), (0, 20)]  # in the first quadrant, touching both axes
COIL = [(22, 0), (32, 0), (32, 20), (22, 20)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def face(points, plane="XY"):
    """A face from (u, v) points: (x, y) in z = 0 ("XY") or (x, z) in y = 0 ("ZX")."""
    vectors = [App.Vector(u, 0, v) if plane == "ZX" else App.Vector(u, v, 0) for u, v in points]
    return Part.Face(Part.makePolygon(vectors + vectors[:1]))


def solid(points, height):
    """The XY polygon pulled up from z = 0 to height."""
    return face(points).extrude(App.Vector(0, 0, height))


def ring_sector(inner, outer, start, end, z0=0.0, height=1.0):
    """Solid ring sector about the Z axis from angle start to end (degrees), from z0 up by height."""
    sweep = end - start
    shape = Part.makeCylinder(outer, height, App.Vector(0, 0, z0), App.Vector(0, 0, 1), sweep)
    if inner > 0:
        shape = shape.cut(Part.makeCylinder(inner, height + 2, App.Vector(0, 0, z0 - 1), App.Vector(0, 0, 1), sweep))
    shape.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), start)
    return shape


def ring_face(inner, outer, start, end):
    """The same in the XY plane, as a face in z = 0."""
    flat = [
        f for f in ring_sector(inner, outer, start, end).Faces if abs(f.BoundBox.ZMin) + abs(f.BoundBox.ZMax) < 1e-9
    ]
    return flat[0]


# ---- Study helpers


def new_study(doc, dimension, shapes):
    """A Manual Study of dimension with one body per (name, shape). Returns (study, bodies)."""
    study = objects.make_study(doc, dimension, doc.Name)
    study.MainMode = "Manual"
    bodies = []
    for name, shape in shapes:
        body = doc.addObject("Part::Feature", name)
        body.Shape = shape
        bodies.append(body)
    study.MainObjects = bodies
    doc.recompute()
    return study, bodies


def fit_air(study, bodies, padding=50):
    """A Box Air Region in Padding mode: padding % of the bodies' size on every side the Study's plane offers."""
    sides = airshapes.padding_sides("Box", airshapes.study_plane(study))
    props = {f"Pad{key}Percent": padding for key, _ in sides}
    return objects.make_air_region(study, "Box", SizeMode="Padding", **props)


def finish(study, bodies, air):
    """One library material for every body and the air, so validation has nothing to warn about."""
    lib = objects.make_library_material(study, json.dumps(record("user:steel", "Steel", "Steel", STEEL)))
    objects.assign(study, [*bodies, air], lib, 0)
    study.Document.recompute()
    return study


def air_study(doc, dimension, shapes, shape="Box", **props):
    """A Study with the given bodies and an Air Region: a Box fitted to them, or another shape with these properties."""
    study, bodies = new_study(doc, dimension, shapes)
    if shape == "Box" and not props:
        air = fit_air(study, bodies)
    else:
        air = objects.make_air_region(study, shape, **props)
    return finish(study, bodies, air)


# ---- 2D XY


def rect_2d(doc):
    return air_study(doc, "2D", [("Core", face(C_CORE)), ("Coil", face(C_COIL))])


def simple_2d(doc, **air):
    return air_study(doc, "2D", [("Core", face(CORE)), ("Coil", face(COIL))], "Sector", **air)


def full_circle_2d(doc):
    return simple_2d(doc, OuterRadius=60)


def half_circle_2d(doc):
    return simple_2d(doc, OuterRadius=60, StartAngle=-90, EndAngle=90)


def quarter_circle_2d(doc):
    return simple_2d(doc, OuterRadius=60, StartAngle=0, EndAngle=90)


def crescent_2d(doc):
    shapes = [("Yoke", ring_face(30, 40, 20, 160)), ("Coil", ring_face(40, 48, 20, 160))]
    return air_study(doc, "2D", shapes, "Sector", InnerRadius=20, OuterRadius=60, StartAngle=0, EndAngle=180)


def padded_sector_ring_2d(doc):
    """The crescent of case 05 with a hollow inside that follows the bodies: 5 mm inside the yoke, 20 % outside."""
    shapes = [("Yoke", ring_face(30, 40, 20, 160)), ("Coil", ring_face(40, 48, 20, 160))]
    props = {"EndAngle": 180, "InnerFromBodies": True, "PadOuterPercent": 20, "PadInner": 5}
    return air_study(doc, "2D", shapes, "Sector", SizeMode="Padding", **props)


def custom_2d(doc):
    study, bodies = new_study(doc, "2D", [("Core", face(CORE)), ("Coil", face(COIL))])
    hexagon = [(16 + 50 * math.cos(math.radians(a)), 10 + 50 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    source = doc.addObject("Part::Feature", "Outline")  # not part of the Study: only gives the air its shape
    source.Shape = face(hexagon)
    air = objects.make_air_region(study, "Custom", Source=source)
    return finish(study, bodies, air)


# ---- 2D ZX (axisymmetric: x is the radius, z the axis)


def zx_bodies():
    return [("Plunger", face(rect(0, 5, 10, 45), "ZX")), ("Coil", face(rect(15, 0, 25, 50), "ZX"))]


def half_disc_zx(doc):
    return air_study(doc, "2D", zx_bodies(), "Sector", OuterRadius=80, Center=App.Vector(0, 0, 25))


def rect_zx(doc):
    return air_study(doc, "2D", zx_bodies(), "Box", Center=App.Vector(50, 0, 25), Length=100, Width=100)


def padded_rect_zx(doc):
    """The left edge stays on the axis; 30 % past the coil in x, 10 mm above and below in z."""
    props = {"PadXPlusPercent": 30, "PadZPlus": 10, "PadZMinus": 10}
    return air_study(doc, "2D", zx_bodies(), "Box", SizeMode="Padding", **props)


# ---- 3D


def c_bodies():
    return [("Core", solid(C_CORE, 30)), ("Coil", solid(C_COIL, 30))]


def box_3d(doc):
    return air_study(doc, "3D", c_bodies())


def padded_box_3d(doc):
    """Unequal padding: 20 % in x, 10 mm on +y only, 50 % in z."""
    props = {"PadXPlusPercent": 20, "PadXMinusPercent": 20, "PadYPlus": 10}
    props.update(PadZPlusPercent=50, PadZMinusPercent=50)
    return air_study(doc, "3D", c_bodies(), "Box", SizeMode="Padding", **props)


def cylinder_3d(doc):
    return air_study(doc, "3D", c_bodies(), "Sector", OuterRadius=90, ZMin=-25, Height=80)


def quarter_cylinder_3d(doc):
    return air_study(doc, "3D", c_bodies(), "Sector", OuterRadius=90, StartAngle=0, EndAngle=90, ZMin=-25, Height=80)


def hollow_sector_3d(doc):
    shapes = [("Yoke", ring_sector(30, 40, 20, 160, 0, 20)), ("Coil", ring_sector(40, 48, 20, 160, 0, 20))]
    props = {"InnerRadius": 20, "OuterRadius": 60, "StartAngle": 0, "EndAngle": 180, "ZMin": -20, "Height": 60}
    return air_study(doc, "3D", shapes, "Sector", **props)


# ---- sliding motion (2D XY)


def slide_study(doc, fixed, moving, shape, air_props, interfaces, dimension="2D", size=None):
    """A sliding-motion Study: fixed and moving (name, face or solid) bodies, an Air Region of shape with air_props
    and the Sliding Interfaces [(kind, properties)]. size: the default mesh size, if not the Study's."""
    study, bodies = new_study(doc, dimension, fixed + moving)
    if size:
        study.MeshSizesGroup.DefaultMeshSize = size
    study.MainObjects = bodies[: len(fixed)]
    study.MovingMode = "Manual"
    study.MovingObjects = bodies[len(fixed) :]
    study.Movement = "Sliding motion"
    air = objects.make_air_region(study, shape, **air_props)
    for kind, props in interfaces:
        objects.make_sliding_interface(study, kind, **props)
    return finish(study, bodies, air)


def full_motor_2d(doc, rotor=40):
    fixed, moving = [("Stator", ring_face(45, 80, 0, 360))], [("Rotor", ring_face(0, rotor, 0, 360))]
    interface = ("Rotational", {"Radius": 42.5, "Divisions": 72})
    return slide_study(doc, fixed, moving, "Sector", {"OuterRadius": 100}, [interface])


def sector_motor_2d(doc):
    """The 45° machine of the user's working sample (in mm): slide circle r 80.575, 90 divisions."""
    fixed = [("Stator", ring_face(82, 149, 0, 45))]
    moving = [("Shaft", ring_face(0, 30, 0, 45)), ("Rotor", ring_face(30, 78, 0, 45))]
    air = {"OuterRadius": 200, "EndAngle": 45}
    return slide_study(doc, fixed, moving, "Sector", air, [("Rotational", {"Radius": 80.575, "Divisions": 90})])


def linear_props(y, name="Sliding Interface"):
    return {"NormalAxis": "Y", "Position": y, "MotionAxis": "X", "Divisions": 32, "GroupName": name}


def linear_2d(doc):
    fixed, moving = [("Stator", face(rect(0, 0, 80, 20)))], [("Mover", face(rect(0, 24, 80, 40)))]
    air = {"Center": App.Vector(40, 25, 0), "Length": 80, "Width": 50}
    return slide_study(doc, fixed, moving, "Box", air, [("Linear", linear_props(22))])


def linear_two_2d(doc):
    fixed = [("Bottom", face(rect(0, 0, 80, 20))), ("Top", face(rect(0, 40, 80, 60)))]
    moving = [("Mover", face(rect(0, 24, 80, 36)))]
    air = {"Center": App.Vector(40, 30, 0), "Length": 80, "Width": 60}
    gaps = [("Linear", linear_props(22, "Lower gap")), ("Linear", linear_props(38, "Upper gap"))]
    return slide_study(doc, fixed, moving, "Box", air, gaps)


# ---- sliding motion (3D)


def motor_3d(doc, end=360, divisions=72):
    """Stator ring 45..80 and rotor r 40, both z 0..50, in a Sector air r 100 from z -25 to 75; slide cylinder
    r 42.5, 10 divisions up."""
    fixed, moving = [("Stator", ring_sector(45, 80, 0, end, 0, 50))], [("Rotor", ring_sector(0, 40, 0, end, 0, 50))]
    interface = ("Rotational", {"Radius": 42.5, "Divisions": divisions, "CrossDivisions": 10})
    air = {"OuterRadius": 100, "EndAngle": end, "ZMin": -25, "Height": 100}
    return slide_study(doc, fixed, moving, "Sector", air, [interface], "3D", 10)


def full_motor_3d(doc):
    return motor_3d(doc)


def sector_motor_3d(doc):
    return motor_3d(doc, 90, 18)


def axial_gap_3d(doc):
    """Rotor disc z 0..10 moving, stator disc z 12..22 fixed, slide disc z 11 over the whole air."""
    fixed, moving = [("Stator", ring_sector(0, 50, 0, 360, 12, 10))], [("Rotor", ring_sector(0, 50, 0, 360, 0, 10))]
    interface = ("Axial gap", {"Position": 11, "Divisions": 36, "CrossDivisions": 8})
    air = {"OuterRadius": 80, "ZMin": -10, "Height": 42}
    return slide_study(doc, fixed, moving, "Sector", air, [interface], "3D", 10)


def linear_3d(doc):
    """Stator box below z 20 fixed, mover z 24..40 moving along x, slide plane z 22."""
    mover = solid(rect(0, 0, 80, 40), 16)
    mover.translate(App.Vector(0, 0, 24))
    fixed, moving = [("Stator", solid(rect(0, 0, 80, 40), 20))], [("Mover", mover)]
    props = {"NormalAxis": "Z", "Position": 22, "MotionAxis": "X", "Divisions": 32, "CrossDivisions": 8}
    air = {"Center": App.Vector(40, 20, 20), "Length": 80, "Width": 40, "Height": 50}
    return slide_study(doc, fixed, moving, "Box", air, [("Linear", props)], "3D", 10)


# ---- error cases


def body_outside_air(doc):
    shapes = [("Core", face(CORE)), ("Coil", face(COIL))]
    return air_study(doc, "2D", shapes, "Box", Center=App.Vector(10, 10, 0), Length=30, Width=30)


def bodies_overlap(doc):
    study, bodies = new_study(doc, "2D", [("Left", face(rect(0, 0, 20, 20))), ("Right", face(rect(10, 0, 30, 20)))])
    return finish(study, bodies, fit_air(study, bodies))


def body_crosses_slide(doc):
    return full_motor_2d(doc, rotor=44)  # the rotor reaches across the slide circle at 42.5


def sliding_zx(doc):
    fixed, moving = zx_bodies()[1:], zx_bodies()[:1]  # the plunger moves
    air = {"OuterRadius": 80, "Center": App.Vector(0, 0, 25)}
    return slide_study(doc, fixed, moving, "Sector", air, [("Rotational", {"Radius": 12})])


def axis_not_z(doc):
    """The motor of case 17 turned onto the X axis: the slide cylinder about Z cuts through both bodies."""
    axis, base = App.Vector(1, 0, 0), App.Vector(-25, 0, 0)
    stator = Part.makeCylinder(80, 50, base, axis).cut(Part.makeCylinder(45, 50, base, axis))
    fixed, moving = [("Stator", stator)], [("Rotor", Part.makeCylinder(40, 50, base, axis))]
    air = {"OuterRadius": 120, "ZMin": -100, "Height": 200}
    return slide_study(doc, fixed, moving, "Sector", air, [("Rotational", {"Radius": 42.5})], "3D", 20)


def moving_on_fixed_side(doc):
    fixed = [("Shaft", ring_face(0, 40, 0, 360)), ("Stator", ring_face(45, 60, 0, 360))]
    moving = [("Rotor", ring_face(65, 80, 0, 360))]  # outside the slide circle, next to the stator
    interface = ("Rotational", {"Radius": 42.5, "Divisions": 72})
    return slide_study(doc, fixed, moving, "Sector", {"OuterRadius": 100}, [interface])


AIR_PRIORITY = "air priority: the bodies keep their own elements where they lie inside the hexagon"
NO_AIR_IN_BODIES = "no element inside a body carries the air's MAT_ID"

CASES = [
    Case("01_rect_2d", rect_2d, ["air all around the C core and the coil", "no overlap", NO_AIR_IN_BODIES]),
    Case("02_circle_2d", full_circle_2d, ["round outer boundary", NO_AIR_IN_BODIES]),
    Case("03_half_circle_2d", half_circle_2d, ["straight symmetry edge on the y axis (x = 0)", NO_AIR_IN_BODIES]),
    Case("04_quarter_circle_2d", quarter_circle_2d, ["two straight symmetry edges, on the x and y axes"]),
    Case("05_crescent_2d", crescent_2d, ["hollow inside: no air nor elements for r < 20", NO_AIR_IN_BODIES]),
    Case(
        "06_custom_2d",
        custom_2d,
        ["outer boundary is the hexagon, which is not meshed as a body", AIR_PRIORITY, NO_AIR_IN_BODIES],
    ),
    Case("07_half_disc_zx", half_disc_zx, ["air has x >= 0 only, its straight edge lies on the Z axis"]),
    Case("08_rect_zx", rect_zx, ["air rectangle starts on the Z axis (x = 0)"]),
    Case("09_box_3d", box_3d, ["air box around the core and the coil: the old problem is solved"]),
    Case("10_cylinder_3d", cylinder_3d, ["round outer boundary, flat top and bottom"]),
    Case("11_quarter_cylinder_3d", quarter_cylinder_3d, ["two symmetry faces, on the xz and yz planes"]),
    Case("12_hollow_sector_3d", hollow_sector_3d, ["hollow inside: no air nor elements for r < 20"]),
    Case(
        "13_full_motor_2d",
        full_motor_2d,
        [
            "72 slide nodes every 5° on the circle r = 42.5, the same in both files",
            "pre_geom2D.msh: the stator and the fixed air",
            "rotor_mesh2D.msh: the rotor, the moving air and the slide point at (42.5, 0)",
        ],
    ),
    Case(
        "14_sector_motor_2d",
        sector_motor_2d,
        [
            "91 slide nodes every 0.5° on the arc r = 80.575 in both files; the arc ends on the 0° and 45° edges",
            "in each file the 0° and 45° edges have nodes at the same radii",
            "the slide point is at (80.575, 0) in rotor_mesh2D.msh only",
        ],
    ),
    Case(
        "15_linear_2d",
        linear_2d,
        ["33 slide nodes on the line y = 22 in both files", "DXYZ = 0.08 m: the 80 mm air box length along x"],
    ),
    Case(
        "16_linear_two_2d",
        linear_two_2d,
        [
            "33 slide nodes on each of the lines y = 22 and y = 38, the same in both files",
            "the mover and the air between the lines are in rotor_mesh2D.msh, with a slide point on each line at x = 0",
            "the nodes at x = 0 and x = 80 match in each file",
        ],
    ),
    Case(
        "17_full_motor_3d",
        full_motor_3d,
        [
            "72 x 11 slide nodes on the cylinder r = 42.5 (every 5°, every 10 mm in z), the same in both files",
            "pre_geom.msh: the stator and the fixed air; rotor_mesh.msh: the rotor and the moving air",
            "the slide edge: 10 line elements in rotor_mesh.msh along (42.5, 0, z), z -25..75",
        ],
    ),
    Case(
        "18_sector_motor_3d",
        sector_motor_3d,
        [
            "19 x 11 slide nodes on the quarter cylinder r = 42.5 in both files; it ends on the 0° and 90° faces",
            "in each file the 0° and 90° faces have nodes at the same (r, z)",
        ],
    ),
    Case(
        "19_axial_gap_3d",
        axial_gap_3d,
        [
            "the slide disc z = 11 has 36 x 8 + 1 nodes in both files: 8 rings of 36 and the centre",
            "the slide edge is radial: 8 line elements in rotor_mesh.msh from (0, 0, 11) to (80, 0, 11)",
        ],
    ),
    Case(
        "20_linear_3d",
        linear_3d,
        [
            "33 x 9 slide nodes on the plane z = 22 in both files",
            "the faces x = 0 and x = 80 have matching nodes in each file; DXYZ = 0.08 m",
        ],
    ),
    Case(
        "21_padded_box_3d",
        padded_box_3d,
        ["air x -12..72 (20 %), y 0..60 (10 mm on +y only), z -15..45 (50 %): centre (30, 30, 15), 84 x 60 x 60"],
    ),
    Case(
        "22_padded_sector_ring_2d",
        padded_sector_ring_2d,
        ["outer radius 57.6 (48 + 20 %), inner radius 25 (30 - 5 mm): no air nor elements for r < 25"],
    ),
    Case(
        "23_padded_rect_zx",
        padded_rect_zx,
        ["air x 0..32.5 (the left edge on the Z axis, 30 % past the coil), z -10..60 (10 mm each side)"],
    ),
    Case(
        "E1_body_outside_air",
        body_outside_air,
        ["Validate refuses: the coil sticks out of the air"],
        "not fully inside",
    ),
    Case(
        "E2_body_crosses_slide",
        body_crosses_slide,
        ["Validate refuses: the rotor reaches across the slide circle"],
        "crosses a Sliding Interface",
    ),
    Case(
        "E3_axis_not_z",
        axis_not_z,
        ["Validate refuses: the machine axis is X, the slide cylinder is about Z"],
        "Rotation is about the global Z axis",
    ),
    Case("E4_sliding_zx", sliding_zx, ["Validate refuses: no sliding motion in a ZX Study"], "not supported in a ZX"),
    Case(
        "E5_moving_on_fixed_side",
        moving_on_fixed_side,
        ["Validate refuses: the moving rotor is on the stator's side of the slide circle"],
        "on the same side of the Sliding Interfaces",
    ),
    Case("E6_bodies_overlap", bodies_overlap, ["Run Mesh refuses: the two bodies overlap"], "overlap"),
]


# ---- running


def run_case(case, out_dir):
    """Build the case in a new document saved in out_dir/<name>/, validate, mesh and write report.txt there.
    Returns the report text; for an E-case the error text instead. Anything unexpected raises, among it an
    E-case that validates and meshes without an error."""
    case_dir = os.path.join(out_dir, case.name)
    os.makedirs(case_dir, exist_ok=True)
    doc = App.newDocument(case.name)
    try:
        doc.saveAs(os.path.join(case_dir, case.name + ".FCStd"))
        study = case.build(doc)
        text = _validate_and_mesh(case, study, case_dir)
        doc.save()  # again, now with the IDs the job wrote
    finally:
        App.closeDocument(doc.Name)
    for name in os.listdir(case_dir):
        if name.endswith(".FCBak"):  # the backup that saving twice leaves
            os.remove(os.path.join(case_dir, name))
    with open(os.path.join(case_dir, "report.txt"), "w", encoding="utf-8") as fh:
        fh.write(text + (meshreport.checklist_text(case.checklist) if case.expect_error else ""))
    return text


def _validate_and_mesh(case, study, case_dir):
    problems = validation.validate(study)
    found = validation.errors(problems)
    if found:
        text = "\n".join(p.text for p in found) + "\n"
        if case.expect_error:
            return text
        raise RuntimeError(text)
    job = jobwriter.write_job(study)
    run = subprocess.run([sys.executable, MESHERS[study.Dimension], job], capture_output=True, encoding="utf-8")
    if run.returncode != 0:
        text = run.stderr.strip().splitlines()[-1] + "\n"
        if case.expect_error:
            return text
        raise RuntimeError(text)
    if case.expect_error:
        raise RuntimeError(f"expected an error with '{case.expect_error}', got none: the model validated and meshed")
    text = meshreport.report(case_dir, job, case.checklist)
    warnings = [p.text for p in problems if p.severity == validation.WARNING]
    return text + "".join(f"Warning: {w}\n" for w in warnings)
