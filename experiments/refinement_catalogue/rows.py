"""The Stage 1 rows of the refinement catalogue (spec 9): Refine Near in ordinary Studies. Each row is
(id, title, build, expected, picture): build() makes the Study in a new document and returns it; expected is "meshes"
or a phrase of the refusal; picture holds the hints of render.render ({"clip": axis, "at": value} cuts a 3D mesh at
axis = value, {"zoom": (x0, y0, x1, y1)} shows that box of the drawing's plane). A row may also carry after(folder)
(see AFTER), a check of its meshes. Sizes in mm, default mesh size 4."""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "freecad_addon"))
sys.path.insert(0, ROOT)

import FreeCAD as App  # noqa: E402 - after the add-on path
import Part  # noqa: E402

from emsolution import objects  # noqa: E402
from tests.freecad_addon import cases  # noqa: E402

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


def slide_nodes(msh):
    """The nodes of a mesh file on RN-08's sliding circle."""
    import gmsh
    import numpy as np

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        xyz = np.reshape(gmsh.model.mesh.getNodes()[1], (-1, 3))
    finally:
        gmsh.finalize()
    return int(np.sum(np.abs(np.hypot(xyz[:, 0], xyz[:, 1]) - SLIDE_R) < 1e-6))


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
AFTER = {"RN-08": rn08_after, "RN-10": rn10_after}
