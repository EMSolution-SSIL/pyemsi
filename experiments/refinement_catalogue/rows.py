"""The rows of the refinement catalogue (spec 9): Stage 1 (RN-01..RN-10), Refine Near in ordinary Studies, and Stage 2
(RN-S1..RN-S6), Refine Near in Studies with Symmetric Groups, Stage 3 (AG-01..AG-S2), Air Grading, and Stage 4
(SL-01..SL-10), Skin Layer, and Swept Body Stage 1 (SW-01..SW-12). Each row is
(id, title, build, expected, picture): build() makes the Study in a new document and returns it; expected is "meshes"
or a phrase of the refusal; picture holds the hints of render.render ({"clip": axis, "at": value} cuts a 3D mesh at
axis = value, {"zoom": (x0, y0, x1, y1)} shows that box of the drawing's plane). A row may also carry after(folder)
(see AFTER), a check of its meshes. Sizes in mm, default mesh size 4."""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "freecad_addon"))
sys.path.insert(0, ROOT)

import FreeCAD as App  # noqa: E402 - after the add-on path
import Part  # noqa: E402

from emsolution import airshapes, geometry, objects  # noqa: E402
from emsolution import jobwriter, validation  # noqa: E402
from tests.freecad_addon import cases  # noqa: E402
from tests.freecad_addon import symcases  # noqa: E402

V = App.Vector
SIZE = 4.0
SLIDE_R = 28.5  # RN-08's sliding circle, between the magnets (r 27) and the stator bore (r 30)


def study_of(name, dimension, shapes, size=SIZE, movement="No movement"):
    """A new document with a Study of the bodies [(name, shape)]. Returns (doc, study, bodies)."""
    doc = App.newDocument(name.replace("-", "_"))
    study, bodies = cases.new_study(doc, dimension, shapes)
    study.MeshSizesGroup.DefaultMeshSize = size
    study.Movement = movement
    return doc, study, bodies


def done(study, bodies, air):
    """One material on every body and the air (cases.finish), then a recompute so sub-element names are current."""
    cases.finish(study, bodies, air)
    study.Document.recompute()
    return study


def subs(body, kind, keep):
    """The names ("Edge3", ...) of body's sub-elements of kind ("Vertex", "Edge", "Face") for which keep(element)."""
    found = {"Vertex": body.Shape.Vertexes, "Edge": body.Shape.Edges, "Face": body.Shape.Faces}[kind]
    names = [f"{kind}{i}" for i, e in enumerate(found, 1) if keep(e)]
    assert names, f"no {kind} of {body.Label} matches"
    return names


def near(a, b, tol=1e-6):
    return abs(a - b) < tol


def centre(e):
    return e.BoundBox.Center


# --- 2D: the magnet of RN-01, RN-06, RN-07 and RN-09 ---------------------------------------------------------------


def magnet_2d(name):
    """A 40 x 10 magnet at the origin in a Padding Box Air Region (100 % on every side: 120 x 30)."""
    doc, study, (magnet,) = study_of(name, "2D", [("Magnet", cases.face(cases.rect(-20, -5, 20, 5)))])
    air = cases.fit_air(study, [magnet], 100)
    return done(study, [magnet], air), magnet, air


def corners(study, magnet, **sizes):
    refs = [(magnet, n) for n in subs(magnet, "Vertex", lambda v: True)]
    return objects.make_refine_near(study, refs, **sizes)


def rn01():
    study, magnet, _ = magnet_2d("RN-01")
    corners(study, magnet, fine=0.3, coarse=4, growth=8)
    return study


def rn06():
    study, magnet, _ = magnet_2d("RN-06")
    corners(study, magnet, fine=0.3, coarse=4, growth=8)
    top = subs(magnet, "Edge", lambda e: near(centre(e).y, 5) and near(e.Length, 40))
    bottom = subs(magnet, "Edge", lambda e: near(centre(e).y, -5) and near(e.Length, 40))
    objects.make_refine_near(study, [(magnet, top[0])], fine=0.6, coarse=4, growth=8)
    objects.make_mesh_size(study, 1, [(magnet, bottom[0])])
    return study


def rn07():
    study, magnet, air = magnet_2d("RN-07")
    xmax = air.Shape.BoundBox.XMax
    right = subs(air, "Edge", lambda e: near(e.BoundBox.XMin, xmax) and near(e.BoundBox.XMax, xmax))
    objects.make_refine_near(study, [(air, right[0])], fine=1, coarse=4, growth=20)
    return study


def rn09a():
    study, magnet, _ = magnet_2d("RN-09a")
    corners(study, magnet, fine=0.3, coarse=0.2, growth=8)
    return study


def rn09b():
    study, magnet, _ = magnet_2d("RN-09b")
    corners(study, magnet, fine=0.3, coarse=4, growth=0)
    return study


def rn09c():
    """RN-01 with a pole piece 10 x 10 beside the magnet; the Refine Near picks the pole's corners, then the pole is
    deleted (deleting the magnet would leave nothing to mesh, a refusal of its own)."""
    shapes = [("Magnet", cases.face(cases.rect(-20, -5, 20, 5))), ("Pole", cases.face(cases.rect(25, -5, 35, 5)))]
    doc, study, (magnet, pole) = study_of("RN-09c", "2D", shapes)
    done(study, [magnet, pole], cases.fit_air(study, [magnet, pole], 100))
    corners(study, pole, fine=0.3, coarse=4, growth=8)
    objects.unassign(study, [pole])
    doc.removeObject(pole.Name)
    doc.recompute()
    return study


# --- 2D: the stator of RN-03 and the sliding motor of RN-08 ---------------------------------------------------------


def rn03():
    """A yoke r 40..50 with 6 teeth (16 degrees wide) down to r 31, in a full-disc Sector Air Region r 60."""
    teeth = [cases.ring_face(31, 41, a - 8, a + 8) for a in range(0, 360, 60)]
    stator = cases.ring_face(40, 50, 0, 360).fuse(teeth).removeSplitter()
    assert len(stator.Faces) == 1
    doc, study, (body,) = study_of("RN-03", "2D", [("Stator", stator.Faces[0])])
    air = objects.make_air_region(study, "Sector", OuterRadius=60)
    done(study, [body], air)

    def tip(e):
        ends = (e.FirstParameter, (e.FirstParameter + e.LastParameter) / 2, e.LastParameter)
        return all(near(math.hypot(p.x, p.y), 31, 1e-4) for p in map(e.valueAt, ends))

    tips = subs(body, "Edge", lambda e: tip(e) and e.Length < 10)
    assert len(tips) == 6, tips
    objects.make_refine_near(study, [(body, n) for n in tips], fine=0.4, coarse=3, growth=6)
    return study


def sliding_motor(name, outer=60):
    """Rotor disc r 25 with 4 surface magnets r 25..27 (60 degrees each), stator ring r 30..50, a Sector Air Region
    r outer and a Rotational Sliding Interface at r 28.5 with 120 divisions. Returns (study, bodies, air)."""
    magnets = [(f"Magnet{k + 1}", cases.ring_face(25, 27, 90 * k - 30, 90 * k + 30)) for k in range(4)]
    shapes = [("Stator", cases.ring_face(30, 50, 0, 360)), ("Rotor", cases.ring_face(0, 25, 0, 360)), *magnets]
    doc, study, bodies = study_of(name, "2D", shapes, movement="Sliding motion")
    air = objects.make_air_region(study, "Sector", OuterRadius=outer)
    objects.make_sliding_interface(study, "Rotational", Radius=SLIDE_R, Divisions=120)
    return done(study, bodies, air), bodies, air


def rn08():
    """sliding_motor with its 4 magnets refined."""
    study, bodies, _ = sliding_motor("RN-08")
    objects.make_refine_near(study, [(b, "") for b in bodies[2:]], fine=0.4, coarse=2, growth=3)
    return study


def slide_nodes(msh, radius=SLIDE_R):
    """The nodes of a mesh file on a sliding circle of radius (RN-08's by default)."""
    import gmsh
    import numpy as np

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        xyz = np.reshape(gmsh.model.mesh.getNodes()[1], (-1, 3))
    finally:
        gmsh.finalize()
    return int(np.sum(np.abs(np.hypot(xyz[:, 0], xyz[:, 1]) - radius) < 1e-6))


def rn08_after(folder):
    """(passed, text): the nodes on the sliding circle are the same in new and today, in both mesh files."""
    counts = {}
    for which in ("new", "today"):
        for f in ("pre_geom2D.msh", "rotor_mesh2D.msh"):
            path = os.path.join(folder, which, f)
            counts[which, f] = slide_nodes(path) if os.path.exists(path) else -1
    same = all(counts["new", f] == counts["today", f] > 0 for f in ("pre_geom2D.msh", "rotor_mesh2D.msh"))
    text = ", ".join(
        f"{f}: new {counts['new', f]}, today {counts['today', f]}" for f in ("pre_geom2D.msh", "rotor_mesh2D.msh")
    )
    return same, "nodes on the sliding circle " + text


# --- 3D ---------------------------------------------------------------------------------------------------------------


def block(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def rn02():
    """A 40 x 20 x 10 magnet in a Padding Box Air Region (50 %); the long edge at y = -10, z = 5."""
    doc, study, (magnet,) = study_of("RN-02", "3D", [("Magnet", block(-20, -10, -5, 20, 10, 5))])
    done(study, [magnet], cases.fit_air(study, [magnet], 50))
    edge = subs(magnet, "Edge", lambda e: near(e.Length, 40) and near(centre(e).y, -10) and near(centre(e).z, 5))
    objects.make_refine_near(study, [(magnet, edge[0])], fine=0.5, coarse=4, growth=10)
    return study


def rn04():
    """Iron x -20..0 and copper x 0..20 (both y -10..10, z -5..5) in air; their shared face x = 0, limited to copper."""
    shapes = [("Iron", block(-20, -10, -5, 0, 10, 5)), ("Copper", block(0, -10, -5, 20, 10, 5))]
    doc, study, bodies = study_of("RN-04", "3D", shapes)
    done(study, bodies, cases.fit_air(study, bodies, 50))
    copper = bodies[1]
    face = subs(copper, "Face", lambda f: near(f.BoundBox.XMin, 0) and near(f.BoundBox.XMax, 0))
    objects.make_refine_near(study, [(copper, face[0])], fine=0.5, coarse=4, growth=8, limit_to=[copper])
    return study


def rn05():
    """A 30 x 20 x 10 copper block in air; the whole block (its faces with the air)."""
    doc, study, (copper,) = study_of("RN-05", "3D", [("Copper", block(-15, -10, -5, 15, 10, 5))])
    done(study, [copper], cases.fit_air(study, [copper], 50))
    objects.make_refine_near(study, [(copper, "")], fine=0.5, coarse=4, growth=6)
    return study


PLATE_FINE = 2.0


def rn10():
    """A 200 x 200 x 10 plate in a Manual Box Air Region 220 x 220 x 30 (10 mm of air round it), default size 10; its
    top face z = 5. A large face: the Distance must sample it densely enough that the face gets the fine size."""
    doc, study, (plate,) = study_of("RN-10", "3D", [("Plate", block(-100, -100, -5, 100, 100, 5))], size=10)
    air = objects.make_air_region(study, "Box", SizeMode="Manual", Center=V(0, 0, 0), Length=220, Width=220, Height=30)
    done(study, [plate], air)
    top = subs(plate, "Face", lambda f: near(f.BoundBox.ZMin, 5) and near(f.BoundBox.ZMax, 5))
    objects.make_refine_near(study, [(plate, top[0])], fine=PLATE_FINE, coarse=10, growth=10)
    return study


def face_edges(msh, z=5.0, half=100.0):
    """(longest, mean) length of the mesh edges in the plane z inside |x|, |y| <= half: the edges of RN-10's top face
    triangles. Read from the tetrahedra, as the file holds only the volumes' elements."""
    import gmsh
    import numpy as np

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        tags, coords, _ = gmsh.model.mesh.getNodes()
        types, _, nodes = gmsh.model.mesh.getElements(3)
    finally:
        gmsh.finalize()
    where = np.zeros(int(tags.max()) + 1, dtype=int)
    where[tags.astype(int)] = np.arange(len(tags))
    xyz = np.reshape(coords, (-1, 3))
    tets = np.reshape(nodes[list(types).index(4)], (-1, 4)).astype(int)
    pairs = np.concatenate([tets[:, [a, b]] for a in range(4) for b in range(a + 1, 4)])
    pairs = np.unique(np.sort(pairs, axis=1), axis=0)
    p, q = xyz[where[pairs[:, 0]]], xyz[where[pairs[:, 1]]]
    on = (np.abs(p[:, 2] - z) < 1e-6) & (np.abs(q[:, 2] - z) < 1e-6)
    on &= np.all(np.abs(p[:, :2]) <= half + 1e-6, axis=1) & np.all(np.abs(q[:, :2]) <= half + 1e-6, axis=1)
    lengths = np.linalg.norm(p[on] - q[on], axis=1)
    return (float(lengths.max()), float(lengths.mean())) if len(lengths) else (0.0, 0.0)


def rn10_after(folder):
    """(passed, text): the plate's top face is refined (its longest edge in new under half of today's); the text says
    whether the longest is within 1.5 x the fine size, which the Distance's Sampling (at most 100 per side of a
    surface) does not reach on a face this large."""
    worst, mean = face_edges(os.path.join(folder, "new", "pre_geom.msh"))
    today = face_edges(os.path.join(folder, "today", "pre_geom.msh"))
    within = "within" if worst <= 1.5 * PLATE_FINE else "NOT within"
    text = f"top face edges: new longest {worst:.2f} mean {mean:.2f}, today longest {today[0]:.2f} mean {today[1]:.2f}"
    return 0 < worst < today[0] / 2, text + f" mm; new longest {within} 1.5 x fine {PLATE_FINE:g}"


# --- Stage 2: Refine Near in Studies with Symmetric Groups (symcases' spike motor) ------------------------------------
# The stator cells span 0..15 deg (iron r 36..60 with a closed slot r 37..50 at 10..15, the coil, an air band r 35..36),
# mirrored at 15 deg and turned 12 times; the rotor cells 0..22.5 deg (iron r 10..30, the magnet r 30..34 at 4.5..22.5,
# the air r 30..35), mirrored at 22.5 deg and turned 8 times; a Rotational Sliding Interface at r 35, 144 divisions.

MOTOR_R = 35.0  # the motor's sliding circle
TIP_R = 36.0  # the stator's bore: the tooth tips


def polar(p):
    """(radius, angle in degrees 0..360) of a point."""
    return math.hypot(p.x, p.y), math.degrees(math.atan2(p.y, p.x)) % 360


def motor(name):
    """symcases.motor_study (default size 5) in a new document."""
    return symcases.motor_study(App.newDocument(name.replace("-", "_")))


def cell(study, name):
    return next(b for b in objects.cell_bodies(study) if b.Name == name)


def on_arc(e, r):
    """True when e is an arc of radius r about Z."""
    return isinstance(e.Curve, Part.Circle) and near(e.Curve.Radius, r) and near(e.Curve.Center.Length, 0)


def rns1():
    study = motor("RN-S1")
    corners(study, cell(study, "MagnetCell"), fine=0.3, coarse=2, growth=4)
    return study


RNS2_COPY = (90, 105)  # the copy of the stator cell the tooth tip is picked on (degrees)


def rns2():
    """The tooth tip of the copy at 90..105 deg, picked on the stator's drawing and mapped to the cells by to_cells
    as the command does: the arc r 36, 0..15 deg, that the iron cell and the air band share."""
    study = motor("RN-S2")
    stator = objects.symmetric_groups(study)[0]
    drawing = geometry.global_shape(stator)

    def tip(e):
        return on_arc(e, TIP_R) and RNS2_COPY[0] < polar(centre(e))[1] < RNS2_COPY[1]

    picks = [f"Edge{i}" for i, e in enumerate(drawing.Edges, 1) if tip(e)]
    assert picks, "no tooth tip on the copy"
    refs = objects.to_cells(study, [(stator, picks[0])])
    assert all(b.Name in {c.Name for c in stator.Cells} for b, _ in refs), refs
    objects.make_refine_near(study, refs, fine=0.3, coarse=2, growth=4)
    return study


def job_of(folder):
    """(job, its folder) of the Study saved in folder: the one job.json under its .pyemsi."""
    found = [os.path.join(d, "job.json") for d, _, f in os.walk(os.path.join(folder, ".pyemsi")) if "job.json" in f]
    assert len(found) == 1, found
    with open(found[0], encoding="utf-8") as fh:
        return json.load(fh), os.path.dirname(found[0])


def rns2_after(folder):
    """(passed, text): the job has one refine entry, in the stator's cell job, and its edges lie on the cell's tooth
    tip (r 36, 0..15 deg), not on the copy picked; the rotor's and the free jobs have none."""
    job, where = job_of(os.path.join(folder, "new"))
    sym = job["symmetric"]
    stator, rotor = (g["job"].get("refine") or [] for g in sym["groups"])
    free = [e for f in sym.get("free", []) for e in f["job"].get("refine") or []]
    places = []
    for entry in stator:
        for f in entry["files"]:
            for e in Part.read(os.path.join(where, f)).Edges:
                places.append((on_arc(e, TIP_R), round(polar(centre(e))[1], 2)))
    passed = len(stator) == 1 and not rotor and not free and places and all(ok and 0 < a < 15 for ok, a in places)
    angles = ", ".join(f"{a:g}" for _, a in places)
    text = (
        f"refine entries: stator cells {len(stator)}, rotor cells {len(rotor)}, free {len(free)}; the stator's entry"
        f" has {len(places)} edge(s), on r {TIP_R:g}: {all(ok for ok, _ in places)}, centred at {angles} deg (picked"
        f" on the copy at {RNS2_COPY[0]}..{RNS2_COPY[1]} deg)"
    )
    return bool(passed), text


SEAM = (10.0, 40.0, 30.0)  # RN-S3's cell: r 10..40, 0..30 deg, turned 12 times


def rns3():
    """A sector cell r 10..40, 0..30 deg, turned 12 times (its 0 and 30 deg sides are periodic seams), default size 4;
    the seam at 0 deg."""
    r1, r2, pitch = SEAM
    doc = App.newDocument("RN_S3")
    study = objects.make_study(doc, "2D")
    study.MeshSizesGroup.DefaultMeshSize = SIZE
    lib = symcases.libraries(study)
    body = symcases.feature(doc, "SectorCell", symcases.sector(r1, r2, 0, pitch))
    symcases.group(study, "Ring", [body], [symcases.rotate_rule(pitch, 12)], lib={body.Name: lib["Steel"]})
    seam = subs(body, "Edge", lambda e: not isinstance(e.Curve, Part.Circle) and near(centre(e).y, 0))
    objects.make_refine_near(study, [(body, seam[0])], fine=0.3, coarse=2, growth=3)
    return study


def mesh_nodes(msh):
    """The (n, 3) node coordinates of a mesh file."""
    import gmsh
    import numpy as np

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        return np.reshape(gmsh.model.mesh.getNodes()[1], (-1, 3))
    finally:
        gmsh.finalize()


def seam_nodes(xyz, deg):
    """The nodes of RN-S3's cell on its side at deg degrees (r 10..40)."""
    import numpy as np

    r1, r2, _ = SEAM
    u = np.array([math.cos(math.radians(deg)), math.sin(math.radians(deg))])
    along, off = xyz[:, :2] @ u, np.abs(xyz[:, :2] @ np.array([-u[1], u[0]]))
    return int(np.sum((off < 1e-6) & (along > r1 - 1e-6) & (along < r2 + 1e-6)))


def rns3_after(folder):
    """(passed, text): both seams of the cell (0 and 30 deg) have the same nodes, more than today."""
    counts = {}
    for which in ("new", "today"):
        xyz = mesh_nodes(os.path.join(folder, which, "pre_geom2D.msh"))
        counts[which] = (seam_nodes(xyz, 0), seam_nodes(xyz, SEAM[2]))
    new, today = counts["new"], counts["today"]
    passed = new[0] == new[1] > today[0] == today[1]
    return passed, f"nodes on the seams at 0 / {SEAM[2]:g} deg: new {new[0]} / {new[1]}, today {today[0]} / {today[1]}"


def rns4():
    """The 3D motor (10 mm high, default size 1.5); the magnet's outer face r 34 on the rotor cell."""
    study = symcases.motor_study_3d(App.newDocument("RN_S4"))
    magnet = cell(study, "MagnetCell")
    face = subs(magnet, "Face", lambda f: isinstance(f.Surface, Part.Cylinder) and near(f.Surface.Radius, 34))
    objects.make_refine_near(study, [(magnet, face[0])], fine=0.5, coarse=3, growth=5)
    return study


def rns5():
    """The 2D motor in a Sector Air Region r 60..90 (default size 5) with a free sensor block 6 x 6 in the air at
    x 72..78; the sensor whole, coarse the air's size."""
    study = motor("RN-S5")
    lib = symcases.libraries(study)
    symcases.add_air_region(study, lib["Air"], AirShape="Sector", InnerRadius=60, OuterRadius=90)
    sensor = symcases.add_free(study, "Sensor", cases.face(cases.rect(72, -3, 78, 3)), lib["Steel"])
    size = study.MeshSizesGroup.DefaultMeshSize.Value
    objects.make_refine_near(study, [(sensor, "")], fine=0.3, coarse=size, growth=10)
    return study


def rns6():
    """The 2D sliding motor with its stator air band (r 35..36, the gap's stator half) structured and recombined: 6
    elements on each arc (144 divisions over 24 cells), 2 across. Refined: the iron cell's corners on the bore (r 36)
    and the tooth's sides, the slot wall at 10 deg and the slot's arc r 37, next to the band but not its arcs, which
    are transfinite curves whose divisions win."""
    study = motor("RN-S6")
    band = cell(study, "StatorAirCell")
    by = {}
    for i, e in enumerate(band.Shape.Edges, 1):
        by.setdefault(6 if isinstance(e.Curve, Part.Circle) else 2, []).append((band, f"Edge{i}"))
    for n, edges in sorted(by.items()):
        objects.make_transfinite_edges(study, n, edges).Label = f"{band.Label} {n}"
    objects.make_transfinite_body(study, [band])
    objects.make_recombine(study, [band])
    iron = cell(study, "StatorIronCell")
    bore = subs(iron, "Vertex", lambda v: near(polar(v.Point)[0], TIP_R))
    sides = subs(iron, "Edge", lambda e: on_arc(e, TIP_R + 1) or (not isinstance(e.Curve, Part.Circle) and side(e)))
    refs = [(iron, n) for n in bore + sides]
    objects.make_refine_near(study, refs, fine=0.3, coarse=2, growth=RNS6_GROWTH)
    return study


RNS6_GROWTH = 3
IRON_FACTOR = 3  # the stator iron of new has at least this many times today's elements


def side(e):
    """True for the slot's wall at 10 deg, r 37..50: the side of the tooth."""
    return all(near(polar(v.Point)[1], 10, 1e-6) for v in e.Vertexes)


def part_elements(msh, name, dim=2):
    """The elements of the physical group name of dimension dim in a mesh file."""
    import gmsh

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        return sum(
            len(t)
            for d, tag in gmsh.model.getPhysicalGroups(dim)
            if gmsh.model.getPhysicalName(d, tag) == name
            for ent in gmsh.model.getEntitiesForPhysicalGroup(d, tag)
            for t in gmsh.model.mesh.getElements(d, ent)[1]
        )
    finally:
        gmsh.finalize()


def rns6_after(folder):
    """(passed, text): the nodes on the sliding circle r 35 are the same in new and today, in both mesh files, the
    structured band keeps its elements, and the stator iron has IRON_FACTOR times today's elements or more."""
    files = ("pre_geom2D.msh", "rotor_mesh2D.msh")
    counts = {}
    for which in ("new", "today"):
        for f in files:
            path = os.path.join(folder, which, f)
            counts[which, f] = slide_nodes(path, MOTOR_R) if os.path.exists(path) else -1
        fixed = os.path.join(folder, which, files[0])
        counts[which, "iron"] = part_elements(fixed, "StatorIron")
        counts[which, "band"] = part_elements(fixed, "StatorAir")
    same = all(counts["new", f] == counts["today", f] > 0 for f in files)
    band = counts["new", "band"] == counts["today", "band"] > 0
    iron = counts["new", "iron"] >= IRON_FACTOR * counts["today", "iron"] > 0
    text = ", ".join(f"{f}: new {counts['new', f]}, today {counts['today', f]}" for f in files)
    text = f"nodes on the sliding circle r {MOTOR_R:g} {text}; structured band (StatorAir) elements: new"
    text += (
        f" {counts['new', 'band']}, today {counts['today', 'band']}; StatorIron elements: new {counts['new', 'iron']},"
    )
    text += f" today {counts['today', 'iron']} (needs x {IRON_FACTOR:g})"
    return same and band and iron, text


MAGNET = {"zoom": (-30, -15, 30, 15)}
CASES = [
    ("RN-01", "2D magnet 40 x 10, its 4 corners (0.3 to 4 over 8)", rn01, "meshes", MAGNET),
    (
        "RN-02",
        "3D magnet 40 x 20 x 10, one long edge (0.5 to 4 over 10), cut at x = 0",
        rn02,
        "meshes",
        {"clip": "x", "at": 0.0, "zoom": (-20, -10, 5, 10)},
    ),
    ("RN-03", "2D stator with 6 teeth, the tooth tips (0.4 to 3 over 6)", rn03, "meshes", {"zoom": (0, -8, 52, 40)}),
    (
        "RN-04",
        "3D iron and copper blocks, their shared face limited to the copper (0.5 to 4 over 8), cut at y = 0",
        rn04,
        "meshes",
        {"clip": "y", "at": 0.0, "zoom": (-16, -10, 16, 10)},
    ),
    (
        "RN-05",
        "3D copper block, the whole block (0.5 to 4 over 6), cut at y = 0",
        rn05,
        "meshes",
        {"clip": "y", "at": 0.0, "zoom": (-20, -12, 20, 12)},
    ),
    (
        "RN-06",
        "2D magnet: corners 0.3, top edge 0.6, Mesh Size 1 on the bottom edge (smallest wins)",
        rn06,
        "meshes",
        MAGNET,
    ),
    ("RN-07", "2D magnet: the right outer edge of the Air Region (1 to 4 over 20)", rn07, "meshes", {}),
    (
        "RN-08",
        "2D sliding motor: the 4 magnets whole (0.4 to 2 over 3), the sliding circle keeps 120 divisions",
        rn08,
        "meshes",
        {"zoom": (15, -14, 50, 14)},
    ),
    (
        "RN-09a",
        "RN-01 with coarse 0.2 < fine 0.3: refused",
        rn09a,
        "the coarse size must not be smaller than the fine size",
        {},
    ),
    ("RN-09b", "RN-01 with growth 0: refused", rn09b, "the growth distance must be greater than 0", {}),
    (
        "RN-09c",
        "RN-01 plus a pole piece whose corners are picked, the pole deleted: refused",
        rn09c,
        "refers to nothing (were its bodies deleted?)",
        {},
    ),
    (
        "RN-10",
        "3D plate 200 x 200 x 10, its top face (2 to 10 over 10, default 10): the whole face gets 2, cut at y = 0",
        rn10,
        "meshes",
        {"clip": "y", "at": 0.0, "zoom": (-110, -15, -60, 15)},
    ),
]
STATOR_TIP = {"zoom": (26, -4, 46, 16)}
CASES += [
    (
        "RN-S1",
        "2D motor: the rotor cell magnet's 4 corners (0.3 to 2 over 4)",
        rns1,
        "meshes",
        {"zoom": (12, -4, 44, 36)},
    ),
    (
        "RN-S2",
        "2D motor: a tooth tip picked on the stator copy at 90..105 deg, moved to the cell (0.3 to 2 over 4)",
        rns2,
        "meshes",
        STATOR_TIP,
    ),
    (
        "RN-S3",
        "2D sector cell r 10..40 turned 12 times: its seam at 0 deg (0.3 to 2 over 3) refines the partner seam too",
        rns3,
        "meshes",
        {"zoom": (0, -12, 44, 30)},
    ),
    (
        "RN-S4",
        "3D motor: the magnet's outer face on the rotor cell (0.5 to 3 over 5), cut at z = 5",
        rns4,
        "meshes",
        {"clip": "z", "at": 5.0, "zoom": (29, 1, 37, 11)},
    ),
    (
        "RN-S5",
        "2D motor in a Sector Air Region r 60..90: a free sensor block whole (0.3 to the air's 5 over 10)",
        rns5,
        "meshes",
        {"zoom": (56, -16, 94, 16)},
    ),
    (
        "RN-S6",
        "2D sliding motor with a structured stator air band: the teeth's bore corners and slot sides beside it (0.3"
        " to 2 over 3) grade the iron; the band and the sliding circle (144) keep their divisions",
        rns6,
        "meshes",
        STATOR_TIP,
    ),
]
AFTER = {"RN-08": rn08_after, "RN-10": rn10_after, "RN-S2": rns2_after, "RN-S3": rns3_after, "RN-S6": rns6_after}


# --- Stage 3: Air Grading --------------------------------------------------------------------------------------------
# Each row has a large air and a small body size; the air's size is a whole-body Mesh Size on the Air Region.


def ag_magnet(name, far=0.0):
    """The 40 x 10 magnet of RN-01 at size 2 (the default) in a Padding Box Air Region of 200 x 200 (80 / 95 mm on
    the sides) with a Mesh Size 20 on it; an Air Grading over 60 to far. Returns (study, magnet, air)."""
    doc, study, (magnet,) = study_of(name, "2D", [("Magnet", cases.face(cases.rect(-20, -5, 20, 5)))], size=2)
    pads = {"PadXPlus": 80, "PadXMinus": 80, "PadYPlus": 95, "PadYMinus": 95}
    air = objects.make_air_region(study, "Box", SizeMode="Padding", **pads)
    done(study, [magnet], air)
    box = air.Shape.BoundBox
    assert near(box.XLength, 200) and near(box.YLength, 200), box
    objects.make_mesh_size(study, 20, [(air, "")])
    objects.make_air_grading(study, growth=60, far=far)
    return study, magnet, air


def ag01():
    return ag_magnet("AG-01")[0]


def ag02():
    """The 40 x 20 x 10 magnet of RN-02 at size 3 (the default) in a Manual Box Air Region 300 x 300 x 300 with a Mesh
    Size 30 on it; an Air Grading over 80 to the air's size."""
    doc, study, (magnet,) = study_of("AG-02", "3D", [("Magnet", block(-20, -10, -5, 20, 10, 5))], size=3)
    air = objects.make_air_region(study, "Box", SizeMode="Manual", Center=V(0, 0, 0), Length=300, Width=300, Height=300)
    done(study, [magnet], air)
    objects.make_mesh_size(study, 30, [(air, "")])
    objects.make_air_grading(study, growth=80, far=0)
    return study


def ag03():
    return ag_magnet("AG-03", far=60)[0]


def ag04():
    """sliding_motor (default size 4) in a Sector Air Region r 150 with a Mesh Size 10 on it; an Air Grading over 30."""
    study, _, air = sliding_motor("AG-04", outer=150)
    objects.make_mesh_size(study, 10, [(air, "")])
    objects.make_air_grading(study, growth=30, far=0)
    return study


def ag05a():
    study, _, _ = ag_magnet("AG-05a")
    objects.make_air_grading(study, growth=30)
    return study


def ag05b():
    study, magnet, _ = ag_magnet("AG-05b")
    for item in objects.air_gradings(study):
        study.Document.removeObject(item.Name)
    objects.make_air_grading(study, [(magnet, "")], growth=60)
    return study


def ags1():
    """The 2D motor (default size 5) in a Sector Air Region r 60..150 round the copies with a Mesh Size 10 on it; an
    Air Grading over 30 to the air's size."""
    study = motor("AG-S1")
    lib = symcases.libraries(study)
    air = symcases.add_air_region(study, lib["Air"], AirShape="Sector", InnerRadius=60, OuterRadius=150)
    objects.make_mesh_size(study, 10, [(air, "")])
    objects.make_air_grading(study, growth=30, far=0)
    return study


def ags2():
    """The 3D motor of RN-S4 (10 mm high, default size 1.5) in a Sector Air Region r 60..120, z 0..10 round the
    copies (a Box would cross the sliding surface and the moving copies, which Validate refuses) with a Mesh Size 8 on
    it; an Air Grading over 25 to the air's size."""
    study = symcases.motor_study_3d(App.newDocument("AG_S2"))
    ring = {"InnerRadius": 60, "OuterRadius": 120, "ZMin": 0, "Height": 10}
    air = symcases.add_air_region(study, symcases.libraries(study)["Air"], AirShape="Sector", **ring)
    objects.make_mesh_size(study, 8, [(air, "")])
    objects.make_air_grading(study, growth=25, far=0)
    return study


def air_band(msh, keep, name="Air"):
    """(elements, mean edge length) of the 2D physical group name's elements whose centroid (x, y) passes keep."""
    import gmsh
    import numpy as np

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        tags, coords, _ = gmsh.model.mesh.getNodes()
        where = np.zeros(int(tags.max()) + 1, dtype=int)
        where[tags.astype(int)] = np.arange(len(tags))
        xyz = np.reshape(coords, (-1, 3))[:, :2]
        lengths, count = [], 0
        for d, tag in gmsh.model.getPhysicalGroups(2):
            if gmsh.model.getPhysicalName(d, tag) != name:
                continue
            for ent in gmsh.model.getEntitiesForPhysicalGroup(d, tag):
                for etype, _, nodes in zip(*gmsh.model.mesh.getElements(2, ent)):
                    corners = gmsh.model.mesh.getElementProperties(etype)[5]
                    each = gmsh.model.mesh.getElementProperties(etype)[3]
                    pts = xyz[where[np.reshape(nodes, (-1, each))[:, :corners].astype(int)]]
                    mid = pts.mean(axis=1)
                    pts = pts[[keep(x, y) for x, y in mid]]
                    count += len(pts)
                    lengths += [np.linalg.norm(pts - np.roll(pts, 1, axis=1), axis=2).ravel()]
    finally:
        gmsh.finalize()
    lengths = np.concatenate(lengths) if lengths else np.zeros(0)
    return count, float(lengths.mean()) if len(lengths) else 0.0


def air_counts(folder, msh="pre_geom2D.msh"):
    """{"new": elements, "today": elements} of the Air in the mesh file msh of new and today."""
    return {w: part_elements(os.path.join(folder, w, msh), "Air") for w in ("new", "today")}


def ag01_after(folder):
    """(passed, text): the Air's elements in new and today, printed."""
    n = air_counts(folder)
    return n["new"] > 0 and n["today"] > 0, f"Air elements: new {n['new']}, today {n['today']}"


def ag03_after(folder):
    """(passed, text): the far size 60 gives the Air fewer elements than today."""
    n = air_counts(folder)
    return 0 < n["new"] < n["today"], f"Air elements: new {n['new']}, today {n['today']} (needs new < today)"


AGS1_BAND = (60, 90)  # the air within the growth distance of the stator (r 60)


def ags1_after(folder):
    """(passed, text): the Air's elements and the mean edge of the air in the band r 60..90 beside the copies, in new
    and today, printed."""
    lo, hi = AGS1_BAND
    out = {}
    for w in ("new", "today"):
        msh = os.path.join(folder, w, "pre_geom2D.msh")
        out[w] = (part_elements(msh, "Air"), air_band(msh, lambda x, y: lo <= math.hypot(x, y) <= hi))
    text = "; ".join(
        f"{w}: Air elements {n}, band r {lo}..{hi} {b} elements, mean edge {e:.2f}" for w, (n, (b, e)) in out.items()
    )
    return all(n > 0 and b > 0 for n, (b, _) in out.values()), text


ONE_PER_AIR = "already has Air Grading AirGrading; one per air."
NOT_AN_AIR = "is not an air. Pick the Air Region"
AIR_BOX = {"zoom": (-100, -100, 100, 100)}
CASES += [
    (
        "AG-01",
        "2D magnet (size 2) in a 200 x 200 air (size 20): Air Grading over 60 to the air's size",
        ag01,
        "meshes",
        AIR_BOX,
    ),
    (
        "AG-02",
        "3D magnet 40 x 20 x 10 (size 3) in a 300 mm air box (size 30): Air Grading over 80 to the air's size, cut at"
        " z = 0",
        ag02,
        "meshes",
        {"clip": "z", "at": 0.0, "zoom": (-100, -100, 100, 100)},
    ),
    ("AG-03", "AG-01 with far size 60: fewer air elements than today", ag03, "meshes", AIR_BOX),
    (
        "AG-04",
        "2D sliding motor (size 4) in an air r 150 (size 10): Air Grading over 30; the sliding circle keeps 120"
        " divisions",
        ag04,
        "meshes",
        {"zoom": (0, -75, 150, 75)},
    ),
    ("AG-05a", "AG-01 with a second Air Grading on the air: refused", ag05a, ONE_PER_AIR, {}),
    ("AG-05b", "AG-01 with the Air Grading on the magnet: refused", ag05b, NOT_AN_AIR, {}),
    (
        "AG-S1",
        "2D motor (size 5) in an air r 60..150 round the copies (size 10): Air Grading over 30 to the air's size",
        ags1,
        "meshes",
        {"zoom": (0, -80, 155, 80)},
    ),
    (
        "AG-S2",
        "3D motor (size 1.5) in an air r 60..120, z 0..10 round the copies (size 8): Air Grading over 25, cut at z = 5",
        ags2,
        "meshes",
        {"clip": "z", "at": 5.0, "zoom": (40, -50, 120, 50)},
    ),
]
AFTER.update({"AG-01": ag01_after, "AG-03": ag03_after, "AG-04": rn08_after, "AG-S1": ags1_after})


# --- Stage 4: Skin Layer ---------------------------------------------------------------------------------------------
# A calculator row sets Frequency, Conductivity and a relative permeability of 1 on the item, and its SkinDepth from
# objects.skin_depth, as the panel's calculator does.


def skin(study, body, depth=None, f=None, sigma=None, quads=False):
    """A Skin Layer on the whole body: depth in mm, or the calculator's depth at f Hz and sigma S/m (mu_r 1)."""
    item = objects.make_skin_layer(study, [(body, "")])
    if f is not None:
        item.Frequency, item.Conductivity, item.RelativePermeability = f, sigma, 1.0
        depth = objects.skin_depth(f, sigma, 1.0)
    item.SkinDepth = depth
    item.QuadLayers = quads
    study.Document.recompute()
    return item


def sl_block(name, f):
    """An aluminium block 40 x 40 x 20 at size 8 (the default) in a Padding Box Air Region (50 %); a Skin Layer at f
    Hz, sigma 3.5e7 (2/δ, 3δ)."""
    doc, study, (body,) = study_of(name, "3D", [("Block", block(-20, -20, -10, 20, 20, 10))], size=8)
    done(study, [body], cases.fit_air(study, [body], 50))
    skin(study, body, f=f, sigma=3.5e7)
    return study


def sl01():
    return sl_block("SL-01", 1000)


def sl02():
    return sl_block("SL-02", 5000)


def disc(r, x=0.0, y=0.0):
    return Part.Face(Part.Wire(Part.makeCircle(r, V(x, y, 0))))


def sl_wire(name, r, size, quads=False, **depth):
    """A 2D round wire of radius r at size (the default) in a Padding Box Air Region (50 %) with a Skin Layer."""
    doc, study, (wire,) = study_of(name, "2D", [("Wire", disc(r))], size=size)
    done(study, [wire], cases.fit_air(study, [wire], 50))
    skin(study, wire, quads=quads, **depth)
    return study


def sl03():
    return sl_wire("SL-03", 30, 10, f=1000, sigma=5.8e7)


def sl04():
    return sl_wire("SL-04", 30, 10, quads=True, f=1000, sigma=5.8e7)


def sl05():
    """A 2D bar 40 x 10 at size 6 in a Padding Box Air Region (50 %), δ 2 with quad layers: its corners are sharp."""
    doc, study, (bar,) = study_of("SL-05", "2D", [("Bar", cases.face(cases.rect(-20, -5, 20, 5)))], size=6)
    done(study, [bar], cases.fit_air(study, [bar], 50))
    skin(study, bar, depth=2, quads=True)
    return study


def sl07():
    return sl_wire("SL-07", 3, SIZE, depth=2)


def rounded_rect(w, h, r):
    """A face w x h centred at the origin with its corners rounded to radius r."""
    a, b = w / 2 - r, h / 2 - r
    edges = [
        Part.LineSegment(V(-a, -h / 2, 0), V(a, -h / 2, 0)).toShape(),
        Part.LineSegment(V(w / 2, -b, 0), V(w / 2, b, 0)).toShape(),
        Part.LineSegment(V(a, h / 2, 0), V(-a, h / 2, 0)).toShape(),
        Part.LineSegment(V(-w / 2, b, 0), V(-w / 2, -b, 0)).toShape(),
    ]
    for (x, y), start in (((a, -b), 270), ((a, b), 0), ((-a, b), 90), ((-a, -b), 180)):
        edges.append(Part.makeCircle(r, V(x, y, 0), V(0, 0, 1), start, start + 90))
    return Part.Face(Part.Wire(Part.__sortEdges__(edges)))


def sl10():
    """A 2D bar 30 x 14 with corners rounded to r 6 (twice the layer depth) at size 3 in a Padding Box Air Region
    (50 %), δ 1 with quad layers: smooth, so it gets them."""
    doc, study, (bar,) = study_of("SL-10", "2D", [("Bar", rounded_rect(30, 14, 6))], size=3)
    done(study, [bar], cases.fit_air(study, [bar], 50))
    skin(study, bar, depth=1, quads=True)
    return study


BAR = (22.0, 11.25, 3.0)  # SL-06's round bar in the rotor iron cell: centred at r 22, 11.25 deg, radius 3
BAR_DEPTH = 0.5


def sl06():
    """The 2D motor of RN-S1 (default size 5) with a copper round bar in its rotor iron cell, a cell of its own in
    the rotor's Symmetric Group (16 copies); a Skin Layer δ 0.5 on the bar cell."""
    study = motor("SL-06")
    doc = study.Document
    r, a, radius = BAR
    bar_face = disc(radius, r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
    iron = cell(study, "RotorIronCell")
    iron.Shape = iron.Shape.cut(bar_face).Faces[0]
    bar = symcases.feature(doc, "Bar", bar_face)
    bar.Visibility = False
    rotor = objects.symmetric_groups(study)[1]
    rotor.Cells = list(rotor.Cells) + [bar]
    objects.sync_rows(rotor)
    row = [x["cell"] for x in objects.rows_of(rotor)].index(bar.Name)
    objects.set_row_material(study, rotor, row, symcases.libraries(study)["Copper"])
    doc.recompute()
    objects.sync_parts(study)
    doc.recompute()
    skin(study, bar, depth=BAR_DEPTH)
    return study


OUTER_BAR = (55.0, 60.0, 2.0, 13.0)  # SL-09's bar in the stator iron cell: r 55..60, 2..13 deg, its arc r 60 outside
OUTER_DEPTH = 0.5


def sl09():
    """SL-06's set-up on the stator: the 2D motor of RN-S1 (default size 5) with a copper bar r 55..60 over 2..13 deg
    at the outer surface of its stator iron cell, a cell of its own in the stator's Symmetric Group (24 copies), in a
    Sector Air Region r 60..90 round the copies; a Skin Layer δ 0.5 on the bar cell. The bar's arc r 60 faces the air,
    which the cell job does not hold."""
    study = motor("SL-09")
    doc = study.Document
    bar_face = symcases.sector(*OUTER_BAR)
    iron = cell(study, "StatorIronCell")
    iron.Shape = iron.Shape.cut(bar_face).Faces[0]
    bar = symcases.feature(doc, "Bar", bar_face)
    bar.Visibility = False
    stator = objects.symmetric_groups(study)[0]
    stator.Cells = list(stator.Cells) + [bar]
    objects.sync_rows(stator)
    lib = symcases.libraries(study)
    row = [x["cell"] for x in objects.rows_of(stator)].index(bar.Name)
    objects.set_row_material(study, stator, row, lib["Copper"])
    doc.recompute()
    objects.sync_parts(study)
    symcases.add_air_region(study, lib["Air"], AirShape="Sector", InnerRadius=60, OuterRadius=90)
    skin(study, bar, depth=OUTER_DEPTH)
    return study


SENSOR_DEPTH = 0.6


def sl08():
    """The 3D motor of RN-S4 (default size 1.5) in a Sector Air Region r 60..90, z 0..10 round the copies, with RN-S5's
    free sensor block 6 x 6 (x 72..78) in the air as a copper conductor, z 2..8; a Skin Layer δ 0.6 on it."""
    study = symcases.motor_study_3d(App.newDocument("SL_08"))
    lib = symcases.libraries(study)
    ring = {"InnerRadius": 60, "OuterRadius": 90, "ZMin": 0, "Height": 10}
    symcases.add_air_region(study, lib["Air"], AirShape="Sector", **ring)
    sensor = symcases.add_free(study, "Sensor", block(72, -3, 2, 78, 3, 8), lib["Copper"])
    skin(study, sensor, depth=SENSOR_DEPTH)
    return study


def part_types(msh, name):
    """{gmsh element type: elements} of the 2D physical group name in a mesh file (3 is a quadrangle)."""
    import gmsh

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        out = {}
        for d, tag in gmsh.model.getPhysicalGroups(2):
            if gmsh.model.getPhysicalName(d, tag) != name:
                continue
            for ent in gmsh.model.getEntitiesForPhysicalGroup(d, tag):
                for etype, elements, _ in zip(*gmsh.model.mesh.getElements(2, ent)):
                    out[int(etype)] = out.get(int(etype), 0) + len(elements)
        return out
    finally:
        gmsh.finalize()


def sl01_after(folder):
    """(passed, text): the block's elements in new and today, printed; new has more."""
    n = {w: part_elements(os.path.join(folder, w, "pre_geom.msh"), "Block", 3) for w in ("new", "today")}
    return n["new"] > n["today"] > 0, f"Block elements: new {n['new']}, today {n['today']}"


def sl04_after(folder):
    """(passed, text): the wire of new has quadrangles."""
    t = {w: part_types(os.path.join(folder, w, "pre_geom2D.msh"), "Wire") for w in ("new", "today")}
    quads = t["new"].get(3, 0)
    text = f"quads in the Wire: new {quads} of {sum(t['new'].values())}, today {t['today'].get(3, 0)}"
    return quads > 0, text


def new_warnings(folder, name):
    """The Validate warnings of the Study saved in folder/new/name.FCStd."""
    doc = App.openDocument(os.path.join(folder, "new", name + ".FCStd"))
    try:
        return [p.text for p in validation.validate(objects.find_study(doc)) if p.severity == validation.WARNING]
    finally:
        App.closeDocument(doc.Name)


def mesher_notes(folder):
    """The NOTE lines mesher2d prints for the job of the 2D Study saved in folder/new (the mesher is run again)."""
    import subprocess

    _, where = job_of(os.path.join(folder, "new"))
    script = os.path.join(os.path.dirname(jobwriter.__file__), "mesher2d.py")
    r = subprocess.run([sys.executable, script, os.path.join(where, "job.json")], capture_output=True, text=True)
    return [x[len("NOTE: ") :] for x in r.stderr.splitlines() if x.startswith("NOTE: ")]


SHARP_WARNING = "Bar has sharp corners on its surface; quad layers need a smooth surface, so it gets graded triangles."
SHARP_NOTE = "has a sharp corner on its surface; graded triangles instead of quad layers"
DEEPER = "is deeper than half of"


def sl05_after(folder):
    """(passed, text): no quadrangles in the bar, and the sharp-corner note and Validate warning printed."""
    quads = part_types(os.path.join(folder, "new", "pre_geom2D.msh"), "Bar").get(3, 0)
    notes = [x for x in mesher_notes(folder) if SHARP_NOTE in x]
    warnings = [x for x in new_warnings(folder, "SL-05") if SHARP_WARNING in x]
    text = (
        f"quads in the Bar: {quads}; mesher: {' | '.join(notes) or 'no note'}; Validate: {' | '.join(warnings) or '-'}"
    )
    return quads == 0 and bool(notes) and bool(warnings), text


def sl10_after(folder):
    """(passed, text): quadrangles in the bar, and no sharp-corner note or Validate warning."""
    quads = part_types(os.path.join(folder, "new", "pre_geom2D.msh"), "Bar").get(3, 0)
    notes = [x for x in mesher_notes(folder) if SHARP_NOTE in x]
    warnings = [x for x in new_warnings(folder, "SL-10") if SHARP_WARNING in x]
    text = f"quads in the Bar: {quads}; sharp-corner note: {len(notes)}; Validate warning: {len(warnings)}"
    return quads > 0 and not notes and not warnings, text


def sl07_after(folder):
    """(passed, text): the "layer is deeper than half" warning printed."""
    warnings = [x for x in new_warnings(folder, "SL-07") if DEEPER in x]
    return bool(warnings), "Validate: " + (" | ".join(warnings) or "no warning")


def in_copy(k):
    """True for a point (x, y) in the rotor's k-th 22.5 deg sector."""
    return lambda x, y: 22.5 * k < math.degrees(math.atan2(y, x)) % 360 < 22.5 * (k + 1)


def stator_copy(k, band):
    """True for a point (x, y) in the stator's k-th 15 deg sector within band of the bar's arc r 60."""
    return lambda x, y: 15 * k < math.degrees(math.atan2(y, x)) % 360 < 15 * (k + 1) and math.hypot(x, y) > 60 - band


def sl09_after(folder):
    """(passed, text): in each of the 24 copies of the bar (one per 15 deg of the stator) the elements within δ of
    its arc r 60 are as many and as fine (mean edge below δ); today that band is as coarse as the bar."""
    out = {}
    for w in ("new", "today"):
        msh = os.path.join(folder, w, "pre_geom2D.msh")
        out[w] = [air_band(msh, stator_copy(k, OUTER_DEPTH), "Bar") for k in range(24)]
    new, today = out["new"], out["today"]
    counts = {n for n, _ in new}
    passed = len(counts) == 1 and min(counts) > 0 and max(e for _, e in new) < OUTER_DEPTH
    edges = sorted({round(e, 3) for _, e in new})
    text = (
        f"Bar elements within δ of r 60 per copy: new {sorted(counts)} (mean edge {edges}), today"
        f" {sorted({n for n, _ in today})} (mean edge {sorted({round(e, 3) for _, e in today})}), 24 copies"
    )
    return passed, text


def sl06_after(folder):
    """(passed, text): each of the 16 copies of the bar (one per 22.5 deg of the rotor) has the same elements, more
    than today."""
    out = {}
    for w in ("new", "today"):
        msh = os.path.join(folder, w, "rotor_mesh2D.msh")
        out[w] = [air_band(msh, in_copy(k), "Bar")[0] for k in range(16)]
    new, today = out["new"], out["today"]
    passed = len(set(new)) == 1 and len(set(today)) == 1 and new[0] > today[0] > 0
    return passed, f"Bar elements per copy: new {sorted(set(new))}, today {sorted(set(today))} (16 copies)"


WIRE = {"zoom": (-35, -35, 35, 35)}
BLOCK_CUT = {"clip": "y", "at": 0.0, "zoom": (-22, -12, 22, 12)}
CASES += [
    (
        "SL-01",
        "3D aluminium block 40 x 40 x 20 (size 8): Skin Layer from the calculator, 1 kHz, σ 3.5e7 (δ 2.69), 2/δ, 3δ,"
        " cut at y = 0",
        sl01,
        "meshes",
        BLOCK_CUT,
    ),
    ("SL-02", "SL-01 at 5 kHz (δ 1.20), cut at y = 0", sl02, "meshes", BLOCK_CUT),
    ("SL-03", "2D round copper wire r 30 (size 10): calculator 1 kHz, σ 5.8e7 (δ 2.09), graded", sl03, "meshes", WIRE),
    ("SL-04", "SL-03 with quad layers (3δ, about 6.3 mm)", sl04, "meshes", WIRE),
    (
        "SL-05",
        "2D bar 40 x 10 (size 6), δ 2 with quad layers: sharp corners, graded triangles instead",
        sl05,
        "meshes",
        {"zoom": (-24, -8, 24, 8)},
    ),
    (
        "SL-06",
        "2D motor of RN-S1 with a copper round bar r 3 in the rotor iron cell: Skin Layer δ 0.5 on the bar cell, graded"
        " in every copy",
        sl06,
        "meshes",
        {"zoom": (8, -4, 34, 18)},
    ),
    (
        "SL-07",
        "2D wire r 3, δ 2, layer 3δ: the layer is deeper than half the wire",
        sl07,
        "meshes",
        {"zoom": (-8, -8, 8, 8)},
    ),
    (
        "SL-08",
        "3D motor in an air r 60..90 with RN-S5's free sensor block as a conductor (z 2..8): Skin Layer δ 0.6, cut at"
        " z = 5",
        sl08,
        "meshes",
        {"clip": "z", "at": 5.0, "zoom": (69, -4.5, 81, 4.5)},
    ),
    (
        "SL-09",
        "2D motor of RN-S1 with a copper bar r 55..60 at the outer surface of the stator iron cell, in a Sector Air"
        " Region r 60..90: Skin Layer δ 0.5 on the bar cell, graded along its arc toward the air in every copy",
        sl09,
        "meshes",
        {"zoom": (50, -1, 64, 16)},
    ),
    (
        "SL-10",
        "2D bar 30 x 14 with corners rounded to r 6 (size 3), δ 1 with quad layers: smooth, so the layers follow the"
        " corners",
        sl10,
        "meshes",
        {"zoom": (-18, -10, 18, 10)},
    ),
]
AFTER.update({"SL-01": sl01_after, "SL-04": sl04_after, "SL-05": sl05_after, "SL-06": sl06_after, "SL-07": sl07_after})
AFTER["SL-09"] = sl09_after
AFTER["SL-10"] = sl10_after


# --- Swept Body, Stage 1 ----------------------------------------------------------------------------------------------
# A busbar 10 x 4 x 100 (z 0..100) of the Study's size 4 in a Padding Box Air Region, swept along z. The after-checks
# print the element types of each part, today's and new, and the air's worst elements (min SICN, and how many are
# below 0.1): gmsh puts pyramids on the long thin skin quads, so those are poor.

POOR = 0.1


def pad_air(study, bodies, mm):
    """A Box Air Region in Padding mode, mm on every side (a thin air shell round a long thin body does not mesh)."""
    air = cases.fit_air(study, bodies, 0)
    sides = airshapes.padding_sides("Box", "3D")
    for key, _ in sides:
        setattr(air, f"Pad{key}", mm)
    return air


def bar_study(name, items, size=SIZE, pad=30, shape=None, air_size=None, label="Busbar"):
    """A busbar (or shape) in a Padding Box Air Region; items(study, body) adds the items."""
    shape = shape or block(-5, -2, 0, 5, 2, 100)
    doc, study, (body,) = study_of(name, "3D", [(label, shape)], size=size)
    air = pad_air(study, [body], pad)
    done(study, [body], air)
    if air_size:
        objects.make_mesh_size(study, air_size, [(air, "")])
    items(study, body)
    return study


def sw01_items(study, body):
    skin(study, body, f=1000, sigma=5.8e7)
    objects.make_swept_body(study, [(body, "")], path_size=4.0)


def sw01():
    return bar_study("SW-01", sw01_items)


def sw02():
    def items(study, body):
        skin(study, body, f=10000, sigma=5.8e7)
        objects.make_swept_body(study, [(body, "")])

    return bar_study("SW-02", items, size=2, pad=20, shape=Part.makeCylinder(3, 100), air_size=8, label="Wire")


def sw03():
    def items(study, body):
        skin(study, body, f=1000, sigma=3.5e7)
        objects.make_swept_body(study, [(body, "")])

    return bar_study("SW-03", items, size=10, pad=20, shape=block(-50, -50, 0, 50, 50, 2), label="Plate")


def sw04():
    return bar_study("SW-04", lambda study, body: objects.make_swept_body(study, [(body, "")], path_size=4.0))


def sw12():
    """SW-01's busbar with its end face (z = 0) on a 40 x 40 x 10 terminal block (z -10..0); both have a Skin Layer."""
    shapes = [("Busbar", block(-5, -2, 0, 5, 2, 100)), ("Terminal", block(-20, -20, -10, 20, 20, 0))]
    doc, study, (bar, term) = study_of("SW-12", "3D", shapes)
    done(study, [bar, term], pad_air(study, [bar, term], 12))
    sw01_items(study, bar)
    skin(study, term, f=1000, sigma=5.8e7)
    return study


def refusal(name, shapes, items):
    """A Study of the bodies [(name, shape)] in a Padding Box Air Region (12 mm); items(study, bodies, air) adds the
    items that are refused."""
    doc, study, bodies = study_of(name, "3D", shapes)
    air = pad_air(study, bodies, 12)
    done(study, bodies, air)
    items(study, bodies, air)
    return study


def bar_shape():
    return ("Busbar", block(-5, -2, 0, 5, 2, 100))


def sw05a():
    return refusal(
        "SW-05a", [("Ball", Part.makeSphere(5))], lambda s, bodies, air: objects.make_swept_body(s, [(bodies[0], "")])
    )


def sw05b():
    return refusal("SW-05b", [bar_shape()], lambda s, bodies, air: objects.make_swept_body(s, [(air, "")]))


def sw05c():
    def items(study, bodies, air):
        objects.make_swept_body(study, [(bodies[0], "")])
        objects.make_transfinite_body(study, bodies)

    return refusal("SW-05c", [bar_shape()], items)


def sw05d():
    def items(study, bodies, air):
        for body in bodies:
            objects.make_swept_body(study, [(body, "")])

    return refusal("SW-05d", [bar_shape(), ("Next", block(5, -2, 0, 15, 2, 100))], items)


def sw05e():
    def items(study, bodies, air):
        objects.make_swept_body(study, [(bodies[0], "")])

    return refusal("SW-05e", [bar_shape(), ("Block", block(5, -2, 0, 15, 0, 50))], items)


def types3(msh, name):
    """{element type name: elements} of the 3D physical group name in a mesh file."""
    import gmsh

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        out = {}
        for d, tag in gmsh.model.getPhysicalGroups(3):
            if gmsh.model.getPhysicalName(d, tag) != name:
                continue
            for ent in gmsh.model.getEntitiesForPhysicalGroup(d, tag):
                for etype, elements, _ in zip(*gmsh.model.mesh.getElements(3, ent)):
                    key = gmsh.model.mesh.getElementProperties(etype)[0]
                    out[key] = out.get(key, 0) + len(elements)
        return out
    finally:
        gmsh.finalize()


def air_quality(msh):
    """(minimum SICN, elements below POOR) of the 3D physical group Air of a mesh file."""
    import gmsh

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        worst, poor = 1.0, 0
        for d, tag in gmsh.model.getPhysicalGroups(3):
            if gmsh.model.getPhysicalName(d, tag) != "Air":
                continue
            for ent in gmsh.model.getEntitiesForPhysicalGroup(d, tag):
                for etype, elements, _ in zip(*gmsh.model.mesh.getElements(3, ent)):
                    q = gmsh.model.mesh.getElementQualities(elements, "minSICN")
                    worst, poor = min(worst, float(min(q))), poor + int((q < POOR).sum())
        return worst, poor
    finally:
        gmsh.finalize()


FACES_3D = {  # gmsh element type: (nodes, its faces), as tests/freecad_addon/test_mesher.py
    4: (4, ((0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3))),
    5: (8, ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))),
    6: (6, ((0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5))),
    7: (5, ((0, 3, 2, 1), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4))),
}


def free_faces_inside(msh):
    """The faces of the 3D elements used once that are not on the model's bounding box: none in a conformal mesh."""
    import gmsh

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        tags, coords = gmsh.model.mesh.getNodes()[:2]
        at = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
        box = gmsh.model.getBoundingBox(-1, -1)
        count = {}
        for _, e in gmsh.model.getEntities(3):
            for typ, nodes in zip(*gmsh.model.mesh.getElements(3, e)[::2]):
                n, faces = FACES_3D[int(typ)]
                for k in range(0, len(nodes), n):
                    cell = nodes[k : k + n]
                    for f in faces:
                        key = tuple(sorted(int(cell[i]) for i in f))
                        count[key] = count.get(key, 0) + 1
        lo, hi = box[:3], box[3:]

        def on_box(f):
            return any(all(abs(at[n][i] - b[i]) < 1e-6 for n in f) for i in range(3) for b in (lo, hi))

        return [f for f, c in count.items() if c == 1 and not on_box(f)]
    finally:
        gmsh.finalize()


def z_steps(msh, name):
    """The steps between the z of the nodes of the 3D physical group name, from the lowest z up."""
    import gmsh

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        z = set()
        for d, tag in gmsh.model.getPhysicalGroups(3):
            if gmsh.model.getPhysicalName(d, tag) == name:
                z |= {round(float(x), 6) for x in gmsh.model.mesh.getNodesForPhysicalGroup(d, tag)[1][2::3]}
        z = sorted(z)
        return [b - a for a, b in zip(z, z[1:])]
    finally:
        gmsh.finalize()


def sw_report(folder, name):
    """(text, new types of the part, new msh): the part's element types, today's and new, and the air's worst elements."""
    msh = {w: os.path.join(folder, w, "pre_geom.msh") for w in ("new", "today")}
    types = {w: types3(msh[w], name) for w in msh}
    air = {w: air_quality(msh[w]) for w in msh}
    text = (
        f"{name} elements: new {sum(types['new'].values())} {types['new']}, today {sum(types['today'].values())}"
        f" {types['today']}; Air minimum SICN: new {air['new'][0]:.3f} ({air['new'][1]} elements below {POOR}),"
        f" today {air['today'][0]:.3f} ({air['today'][1]} below {POOR})"
    )
    return text, types["new"], msh["new"]


def sw01_after(folder):
    """(passed, text): the busbar is hexahedra only; the counts today and new and the air's quality printed."""
    text, types, msh = sw_report(folder, "Busbar")
    return set(types) == {"Hexahedron 8"}, text + f"; free faces inside: {len(free_faces_inside(msh))}"


def sw02_after(folder):
    """(passed, text): hexahedra (the quads of the section) and prisms."""
    text, types, msh = sw_report(folder, "Wire")
    return types.get("Hexahedron 8", 0) > 0 and types.get("Prism 6", 0) > 0, text


def sw03_after(folder):
    """(passed, text): the "deeper than half" warning printed."""
    warnings = [x for x in new_warnings(folder, "SW-03") if DEEPER in x]
    text, _, _ = sw_report(folder, "Plate")
    return bool(warnings), "Validate: " + (" | ".join(warnings) or "no warning") + "; " + text


def sw04_after(folder):
    """(passed, text): hexahedra only, every step along the path the same."""
    text, types, msh = sw_report(folder, "Busbar")
    steps = z_steps(msh, "Busbar")
    ok = set(types) == {"Hexahedron 8"} and max(steps) - min(steps) < 1e-6
    return ok, text + f"; steps along z {min(steps):.2f}..{max(steps):.2f}"


def sw12_after(folder):
    """(passed, text): no free faces inside, and the busbar's steps along z at the terminal end (z 0) are not graded
    while the free end (z 100) is."""
    text, types, msh = sw_report(folder, "Busbar")
    free = free_faces_inside(msh)
    steps = z_steps(msh, "Busbar")
    ok = not free and steps[0] > 0.8 * SIZE and steps[-1] < 0.8 * SIZE
    text += (
        f"; free faces inside: {len(free)}; first step at the terminal {steps[0]:.2f}, at the free end {steps[-1]:.2f}"
    )
    return ok, text


SW_CUT = {
    "clip": "y",
    "at": 0.0,
    "zoom": (-12, -6, 12, 106),
    "across": {"clip": "z", "at": 50.0, "zoom": (-12, -8, 12, 8)},
}
CASES += [
    (
        "SW-01",
        "3D copper busbar 10 x 4 x 100 (size 4) in a Padding Box Air Region: Skin Layer 1 kHz (δ 2.09), Swept Body"
        " (path size 4), cut at y = 0",
        sw01,
        "meshes",
        SW_CUT,
    ),
    (
        "SW-02",
        "3D round wire r 3 x 100 (size 2): Skin Layer 10 kHz (δ 0.66), Swept Body, cut at y = 0",
        sw02,
        "meshes",
        {
            "clip": "y",
            "at": 0.0,
            "zoom": (-8, -4, 8, 104),
            "across": {"clip": "z", "at": 50.0, "zoom": (-10, -8, 10, 8)},
        },
    ),
    (
        "SW-03",
        "3D aluminium plate 100 x 100 x 2 (size 10): Skin Layer 1 kHz (δ 2.69, fills the plate), Swept Body",
        sw03,
        "meshes",
        {"clip": "y", "at": 0.0, "zoom": (-30, -3, 30, 5)},
    ),
    ("SW-04", "SW-01's busbar with a Swept Body only: uniform hexahedra, cut at y = 0", sw04, "meshes", SW_CUT),
    ("SW-05a", "A swept sphere: refused", sw05a, "is not a sweep", {}),
    ("SW-05b", "The Air Region swept: refused", sw05b, "cannot be a Swept Body", {}),
    ("SW-05c", "A swept bar with a Transfinite Body: refused", sw05c, "a body is swept or structured, not both", {}),
    ("SW-05d", "Two swept bars touching: refused", sw05d, "which is swept", {}),
    ("SW-05e", "A block on half of a swept bar's side: refused", sw05e, "touches only part of", {}),
    (
        "SW-12",
        "SW-01's busbar with its end on a 40 x 40 x 10 terminal block (own Skin Layer): conformal, no grading at the"
        " terminal end, cut at y = 0",
        sw12,
        "meshes",
        {
            "clip": "y",
            "at": 0.0,
            "zoom": (-25, -14, 25, 106),
            "across": {"clip": "z", "at": 50.0, "zoom": (-12, -8, 12, 8)},
        },
    ),
]
AFTER.update({"SW-01": sw01_after, "SW-02": sw02_after, "SW-03": sw03_after, "SW-04": sw04_after, "SW-12": sw12_after})
