"""The rows of the refinement catalogue (spec 9): Stage 1 (RN-01..RN-10), Refine Near in ordinary Studies, and Stage 2
(RN-S1..RN-S6), Refine Near in Studies with Symmetric Groups. Each row is
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

from emsolution import geometry, objects  # noqa: E402
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


def rn08():
    """Rotor disc r 25 with 4 surface magnets r 25..27 (60 degrees each), stator ring r 30..50, a Sector Air Region
    r 60 and a Rotational Sliding Interface at r 28.5 with 120 divisions."""
    magnets = [(f"Magnet{k + 1}", cases.ring_face(25, 27, 90 * k - 30, 90 * k + 30)) for k in range(4)]
    shapes = [("Stator", cases.ring_face(30, 50, 0, 360)), ("Rotor", cases.ring_face(0, 25, 0, 360)), *magnets]
    doc, study, bodies = study_of("RN-08", "2D", shapes, movement="Sliding motion")
    air = objects.make_air_region(study, "Sector", OuterRadius=60)
    objects.make_sliding_interface(study, "Rotational", Radius=SLIDE_R, Divisions=120)
    done(study, bodies, air)
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


def part_elements(msh, name):
    """The elements of the 2D physical group name in a mesh file."""
    import gmsh

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        return sum(
            len(t)
            for d, tag in gmsh.model.getPhysicalGroups(2)
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
