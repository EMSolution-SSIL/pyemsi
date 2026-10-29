"""Build the structured-mesh example files, one folder each, and mesh them headless.
Run from the repo root: pixi run -e addon python experiments/structured_examples/build_examples.py"""

import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "freecad_addon"))

import FreeCAD as App  # noqa: E402 - after the add-on path
import Part  # noqa: E402
from BOPTools import SplitFeatures  # noqa: E402

from emsolution import jobwriter, objects  # noqa: E402

MESHER2D = os.path.join(HERE, "..", "..", "freecad_addon", "emsolution", "mesher2d.py")
V = App.Vector


def polygon(*pts):
    return Part.Face(Part.makePolygon([V(x, y, 0) for x, y in pts + pts[:1]]))


def feature(doc, group, name, shape):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    group.addObject(obj)
    return obj


def fragments(doc, group, name, inputs):
    obj = SplitFeatures.makeBooleanFragments(name)
    obj.Objects = inputs
    obj.Mode = "Standard"
    group.addObject(obj)
    doc.recompute()
    for o in inputs + [s for i in inputs for s in getattr(i, "Sources", [])]:
        o.Visibility = False  # as the GUI's Fragments command does: clicks then land on the Fragments
    return obj


def new_doc(name, dimension="2D"):
    folder = os.path.join(HERE, name)
    os.makedirs(folder, exist_ok=True)
    doc = App.newDocument(name)
    group = doc.addObject("App::DocumentObjectGroup", "Geometry")
    study = objects.make_study(doc, dimension, "Study")
    study.MainMode, study.MainSource = "Container", group
    study.MeshSizesGroup.DefaultMeshSize = 2 if dimension == "2D" else 3
    return doc, group, study, os.path.join(folder, name + ".FCStd")


def edges_where(body, test):
    return [(body, f"Edge{i}") for i, e in enumerate(body.Shape.Edges, 1) if test(e)]


def face_at(body, x, y):
    faces = body.Shape.Faces
    best = min(range(len(faces)), key=lambda i: faces[i].CenterOfMass.distanceToPoint(V(x, y, 0)))
    return f"Face{best + 1}"


def vertex_at(body, x, y):
    return next(
        f"Vertex{i}" for i, v in enumerate(body.Shape.Vertexes, 1) if v.Point.distanceToPoint(V(x, y, 0)) < 1e-6
    )


def mid(e):
    return e.valueAt((e.FirstParameter + e.LastParameter) / 2)


# --- 1: a quarter ring cut into 6 curved blocks ------------------------------------------------------------------


def ring_sectors():
    doc, group, study, path = new_doc("1_ring_sectors")
    parts = []
    for i, (r1, r2) in enumerate([(20, 30), (30, 40)]):
        for j in range(3):
            a1, a2 = 30 * j, 30 * (j + 1)
            c = [V(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0) for r in (r1, r2) for a in (a1, a2)]
            wire = Part.Wire(
                [
                    Part.makeCircle(r1, V(), V(0, 0, 1), a1, a2),
                    Part.LineSegment(c[1], c[3]).toShape(),
                    Part.makeCircle(r2, V(), V(0, 0, 1), a1, a2),
                    Part.LineSegment(c[2], c[0]).toShape(),
                ]
            )
            parts.append(feature(doc, group, f"sector_{i}{j}", Part.Face(wire)))
    ring = fragments(doc, group, "ring_fragments", parts)
    arcs = edges_where(ring, lambda e: isinstance(e.Curve, Part.Circle))
    radials = edges_where(ring, lambda e: isinstance(e.Curve, Part.Line))
    objects.make_transfinite_edges(study, 8, arcs).Label = "arcs 8 el"
    objects.make_transfinite_edges(study, 5, radials, "Bump", 0.3).Label = "radials 5 el bump"
    objects.make_transfinite_body(study, [ring])
    objects.make_recombine(study, [ring])
    return doc, study, path


# --- 2: some faces structured, the rest left free ----------------------------------------------------------------


def mixed():
    doc, group, study, path = new_doc("2_mixed_partial")
    a = feature(doc, group, "block_a", polygon((0, 0), (10, 0), (10, 10), (0, 10)))
    b = feature(doc, group, "block_b", polygon((10, 0), (20, 0), (20, 10), (10, 10)))
    roof = feature(doc, group, "roof", polygon((0, 10), (20, 10), (20, 18), (10, 24), (0, 18)))
    plate = polygon((20, 0), (35, 0), (35, 10), (20, 10))
    hole = Part.Face(Part.Wire(Part.makeCircle(2.5, V(27.5, 5, 0))))
    holed = feature(doc, group, "holed", plate.cut(hole))
    body = fragments(doc, group, "mixed_fragments", [a, b, roof, holed])
    left, right = face_at(body, 5, 5), face_at(body, 15, 5)
    square = {left, right}
    own = [
        r
        for f in square
        for r in edges_where(body, lambda e, f=f: any(e.isSame(g) for g in body.Shape.getElement(f).Edges))
    ]
    objects.make_transfinite_edges(study, 4, list(dict.fromkeys(own))).Label = "squares 4 el"
    objects.make_transfinite_body(study, []).References = [(body, left), (body, right)]
    objects.make_recombine(study, []).References = [(body, left), (body, right), (body, face_at(body, 27.5, 5))]
    return doc, study, path


def mixed_roof(doc, study):
    """The challenge: structure the roof too, with 4 chosen corners and side counts that add up."""
    body = doc.getObject("mixed_fragments")
    roof = face_at(body, 10, 15)
    tops = edges_where(body, lambda e: mid(e).y > 18)
    sides = edges_where(body, lambda e: abs(mid(e).y - 14) < 1e-6)
    objects.make_transfinite_edges(study, 4, tops).Label = "roof slopes 4 el"
    objects.make_transfinite_edges(study, 3, sides).Label = "roof sides 3 el"
    corners = [(body, vertex_at(body, x, y)) for x, y in [(0, 10), (20, 10), (20, 18), (0, 18)]]
    objects.make_transfinite_body(study, [], corners).References = [(body, roof)]


# --- 3: a T-junction: one face, five boundary points --------------------------------------------------------------


def t_junction():
    doc, group, study, path = new_doc("3_t_junction")
    tall = feature(doc, group, "tall", polygon((0, 0), (10, 0), (10, 20), (0, 20)))
    low = feature(doc, group, "low", polygon((10, 0), (20, 0), (20, 10), (10, 10)))
    high = feature(doc, group, "high", polygon((10, 10), (20, 10), (20, 20), (10, 20)))
    body = fragments(doc, group, "t_fragments", [tall, low, high])
    objects.make_transfinite_edges(study, 8, edges_where(body, lambda e: e.Length > 15)).Label = "long 8 el"
    objects.make_transfinite_edges(study, 4, edges_where(body, lambda e: e.Length < 15)).Label = "short 4 el"
    objects.make_transfinite_body(study, [body])
    objects.make_recombine(study, [body])
    return doc, study, path


# --- 4: a coil whose neighbour's sketch traces its edge -----------------------------------------------------------


def coil_traced():
    doc, group, study, path = new_doc("4_coil_traced")
    coil_sketch = doc.addObject("Sketcher::SketchObject", "coil_sketch")
    coil_sketch.addGeometry([Part.LineSegment(V(*p), V(*q)) for p, q in _loop([(10, 0), (15, 0), (15, 10), (10, 10)])])
    coil = doc.addObject("Part::Face", "coil_cell")
    coil.Sources = [coil_sketch]
    doc.recompute()
    air_sketch = doc.addObject("Sketcher::SketchObject", "air_sketch")
    air_sketch.addExternal(coil.Name, _edge_at(coil, 10, 5))  # trace the coil's left edge
    air_sketch.addGeometry([Part.LineSegment(V(*p), V(*q)) for p, q in _loop([(0, 0), (10, 0), (10, 10), (0, 10)])])
    air = doc.addObject("Part::Face", "air_cell")
    air.Sources = [air_sketch]
    top_sketch = doc.addObject("Sketcher::SketchObject", "air_top_sketch")
    top_sketch.addGeometry([Part.LineSegment(V(*p), V(*q)) for p, q in _loop([(0, 10), (10, 10), (10, 20), (0, 20)])])
    top = doc.addObject("Part::Face", "air_top")
    top.Sources = [top_sketch]
    for o in (coil_sketch, coil, air_sketch, air, top_sketch, top):
        group.addObject(o)
    doc.recompute()
    body = fragments(doc, group, "air_fragments", [air, top])
    coil_sketch.Visibility = False
    objects.make_transfinite_edges(study, 4, edges_where(body, lambda e: True) + edges_where(coil, lambda e: True))
    objects.make_transfinite_body(study, [body, coil])
    objects.make_recombine(study, [body, coil])
    return doc, study, path


def _loop(pts):
    return list(zip(pts, pts[1:] + pts[:1]))


def _edge_at(body, x, y):
    return next(f"Edge{i}" for i, e in enumerate(body.Shape.Edges, 1) if mid(e).distanceToPoint(V(x, y, 0)) < 1e-6)


# --- 5: 3D, the ring sectors extruded: 6 curved hexahedral blocks -------------------------------------------------


def ring_3d():
    doc, group, study, path = new_doc("5_3d_ring_sectors", "3D")
    parts = []
    for i, (r1, r2) in enumerate([(20, 30), (30, 40)]):
        for j in range(3):
            a1, a2 = 30 * j, 30 * (j + 1)
            c = [V(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0) for r in (r1, r2) for a in (a1, a2)]
            wire = Part.Wire(
                [
                    Part.makeCircle(r1, V(), V(0, 0, 1), a1, a2),
                    Part.LineSegment(c[1], c[3]).toShape(),
                    Part.makeCircle(r2, V(), V(0, 0, 1), a1, a2),
                    Part.LineSegment(c[2], c[0]).toShape(),
                ]
            )
            parts.append(feature(doc, group, f"sector_{i}{j}", Part.Face(wire).extrude(V(0, 0, 10))))
    ring = fragments(doc, group, "ring_fragments", parts)
    arcs = edges_where(ring, lambda e: isinstance(e.Curve, Part.Circle))
    axial = edges_where(ring, lambda e: isinstance(e.Curve, Part.Line) and abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1)
    radials = [r for r in edges_where(ring, lambda e: isinstance(e.Curve, Part.Line)) if r not in axial]
    objects.make_transfinite_edges(study, 8, arcs).Label = "arcs 8 el"
    objects.make_transfinite_edges(study, 5, radials, "Bump", 0.3).Label = "radials 5 el bump"
    objects.make_transfinite_edges(study, 3, axial).Label = "axial 3 el"
    objects.make_transfinite_body(study, [ring])
    objects.make_recombine(study, [ring])
    return doc, study, path


# --- 6: 3D, a structured core (two boxes and a prism) beside a free body ------------------------------------------


def partial_3d():
    doc, group, study, path = new_doc("6_3d_partial", "3D")
    a = feature(doc, group, "box_a", Part.makeBox(10, 10, 10))
    b = feature(doc, group, "box_b", Part.makeBox(10, 10, 10, V(10, 0, 0)))
    tri = Part.Face(Part.makePolygon([V(0, 0, 10), V(10, 0, 10), V(0, 0, 20), V(0, 0, 10)]))
    prism = feature(doc, group, "prism", tri.extrude(V(0, 10, 0)))  # 5 faces, on top of box_a
    core = fragments(doc, group, "core_fragments", [a, b, prism])
    hole = Part.makeCylinder(2.5, 10, V(25, 5, 0))
    feature(doc, group, "holed_block", Part.makeBox(10, 10, 10, V(20, 0, 0)).cut(hole))  # touches box_b at x = 20
    objects.make_transfinite_edges(study, 4, edges_where(core, lambda e: True)).Label = "core 4 el"
    objects.make_transfinite_body(study, [core])
    objects.make_recombine(study, [core])
    return doc, study, path


# --- 7: 3D, a T-junction: refused in 3D until the tall block is sliced too ----------------------------------------


def t_junction_3d(sliced=False):
    doc, group, study, path = new_doc("7_3d_t_junction", "3D")
    if sliced:
        path = path.replace(".FCStd", "_sliced.FCStd")
        tall = [feature(doc, group, f"tall_{k}", Part.makeBox(10, 10, 10, V(0, 0, 10 * k))) for k in (0, 1)]
    else:
        tall = [feature(doc, group, "tall", Part.makeBox(10, 10, 20))]
    low = feature(doc, group, "low", Part.makeBox(10, 10, 10, V(10, 0, 0)))
    high = feature(doc, group, "high", Part.makeBox(10, 10, 10, V(10, 0, 10)))
    body = fragments(doc, group, "t_fragments", tall + [low, high])
    if not sliced:
        objects.make_transfinite_edges(study, 8, edges_where(body, lambda e: e.Length > 15)).Label = "long 8 el"
    objects.make_transfinite_edges(study, 4, edges_where(body, lambda e: e.Length < 15)).Label = "short 4 el"
    objects.make_transfinite_body(study, [body])
    objects.make_recombine(study, [body])
    return doc, study, path


def sliced_t_3d():
    return t_junction_3d(sliced=True)


# --- run ------------------------------------------------------------------------------------------------------------

MESHER = os.path.join(HERE, "..", "..", "freecad_addon", "emsolution", "mesher.py")
ELEMENTS = {2: "triangles", 3: "quads", 4: "tetrahedra", 5: "hexahedra", 6: "prisms", 7: "pyramids"}


def element_counts(path, dim):
    """{element name: count} of the dim-D blocks of an ASCII msh 4.1 file."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("$Elements\n", 1)[1].split("$EndElements", 1)[0].splitlines()
    counts, k = {}, 1
    while k < len(lines):
        d, _, t, n = map(int, lines[k].split())
        if d == dim:
            counts[ELEMENTS.get(t, t)] = counts.get(ELEMENTS.get(t, t), 0) + n
        k += n + 1
    return counts


def mesh(study, title):
    try:
        job = jobwriter.write_job(study)
    except jobwriter.StudyError as e:
        print(f"[{title}] Study refused:\n  " + str(e).replace("\n", "\n  "))
        return
    two_d = study.Dimension == "2D"
    mesher = MESHER2D if two_d else MESHER
    r = subprocess.run([sys.executable, mesher, job], capture_output=True, encoding="utf-8", errors="replace")
    lines = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip() and not ln.startswith("Info")]
    print(f"[{title}] mesher exit {r.returncode}:\n  " + "\n  ".join(lines[-12:]))
    if r.returncode == 0:
        print("  elements:", element_counts(jobwriter.mesh_file(study), 2 if two_d else 3))


def recount(study, body, test, elements):
    """Move the edges of body that pass test out of their Transfinite Edges item into a new one with elements."""
    moved = edges_where(body, test)
    gone = {(b.Name, sub) for b, sub in moved}
    for item in objects.transfinite_edges(study):
        item.References = [(b, sub) for b, subs in item.References for sub in subs if (b.Name, sub) not in gone]
    objects.make_transfinite_edges(study, elements, moved)


def challenges():
    """The guide's challenges, built and meshed on throwaway copies, to check what the guide promises."""

    def outer_arc_9(doc, study):
        ring = doc.getObject("ring_fragments")
        recount(study, ring, lambda e: isinstance(e.Curve, Part.Circle) and e.Curve.Radius > 39 and mid(e).y < 15, 9)

    def roof_no_corners(doc, study):
        mixed_roof(doc, study)
        objects.transfinite_bodies(study)[-1].Corners = []

    def holed_in_tf(doc, study):
        body = doc.getObject("mixed_fragments")
        holed = face_at(body, 27.5, 5)
        objects.make_transfinite_body(study, []).References = [(body, holed)]
        recount(study, body, lambda e: any(e.isSame(g) for g in body.Shape.getElement(holed).Edges), 4)

    def same_face_twice(doc, study):
        body = doc.getObject("mixed_fragments")
        objects.make_transfinite_body(study, []).References = [(body, face_at(body, 5, 5))]

    def left_7(doc, study):
        objects.transfinite_edges(study)[0].Elements = 7  # "long 8 el": the left edge

    def wide_top(doc, study):
        sketch = doc.getObject("air_top_sketch")
        sketch.deleteAllGeometry()
        sketch.addGeometry([Part.LineSegment(V(*p), V(*q)) for p, q in _loop([(0, 10), (15, 10), (15, 20), (0, 20)])])
        doc.recompute()
        body, coil = doc.getObject("air_fragments"), doc.getObject("coil_cell")
        objects.transfinite_edges(study)[0].References = edges_where(body, lambda e: True) + edges_where(
            coil, lambda e: True
        )

    def pick_a_face_3d(doc, study):
        ring = doc.getObject("ring_fragments")
        objects.transfinite_bodies(study)[0].References = [(ring, "Face1")]

    def outer_arc_9_3d(doc, study):
        ring = doc.getObject("ring_fragments")
        recount(
            study,
            ring,
            lambda e: isinstance(e.Curve, Part.Circle) and e.Curve.Radius > 39 and mid(e).y < 15 and mid(e).z < 1,
            9,
        )

    def holed_structured_3d(doc, study):
        holed = doc.getObject("holed_block")
        objects.make_transfinite_edges(study, 4, edges_where(holed, lambda e: True))
        objects.transfinite_bodies(study)[0].References = list(objects.transfinite_bodies(study)[0].References) + [
            (holed, "")
        ]

    def core_not_recombined_3d(doc, study):
        doc.removeObject(objects.recombine_items(study)[0].Name)

    for build, change, title in [
        (ring_3d, pick_a_face_3d, "5 + a face picked in 3D"),
        (ring_3d, outer_arc_9_3d, "5 + one outer arc 9 el"),
        (partial_3d, holed_structured_3d, "6 + holed block structured"),
        (partial_3d, core_not_recombined_3d, "6 + core structured, no Recombine"),
        (ring_sectors, outer_arc_9, "1 + one outer arc 9 el"),
        (mixed, roof_no_corners, "2 + roof structured, no corners"),
        (mixed, holed_in_tf, "2 + holed face structured"),
        (mixed, same_face_twice, "2 + block_a in two Transfinite Bodies"),
        (t_junction, left_7, "3 + left edge 7 el"),
        (coil_traced, wide_top, "4 + top air over the coil too"),
    ]:
        doc, study, path = build()
        doc.recompute()
        change(doc, study)
        doc.recompute()
        check = path.replace(".FCStd", "_check.FCStd")
        doc.saveAs(check)
        mesh(study, title)
        App.closeDocument(doc.Name)
        os.remove(check)


if __name__ == "__main__":
    for build in (ring_sectors, mixed, t_junction, coil_traced, ring_3d, partial_3d, t_junction_3d, sliced_t_3d):
        doc, study, path = build()
        doc.recompute()
        doc.saveAs(path)
        print("saved", path, "| bodies:", [b.Label for b in objects.assignable(study)])
        mesh(study, doc.Name)
        if build is mixed:  # the challenge, meshed on a copy only
            mixed_roof(doc, study)
            doc.recompute()
            doc.saveAs(path.replace(".FCStd", "_roof_solved.FCStd"))
            mesh(study, doc.Name + " + roof")
        App.closeDocument(doc.Name)
    if "--challenges" in sys.argv:
        challenges()
