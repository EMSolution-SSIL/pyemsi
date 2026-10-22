"""2D mesher tests. Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_mesher2d.py"""

import json
import math
import os
import stat
import subprocess
import sys
import tempfile
import unittest

import gmsh

from emsolution import meshcommon

from .test_mesher import write_line, write_point
from .meshreport import report

MESHER2D = os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution", "mesher2d.py")


def write_rects(path, rects, plane="XY"):
    """One BREP holding rectangles (x, y, dx, dy) in the XY plane, or turned into the ZX plane (y = 0)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        tags = [gmsh.model.occ.addRectangle(x, y, 0, dx, dy) for x, y, dx, dy in rects]
        if plane == "ZX":
            gmsh.model.occ.rotate([(2, t) for t in tags], 0, 0, 0, 1, 0, 0, math.pi / 2)  # (x, y, 0) -> (x, 0, y)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_box(path):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_polygons(path, loops):
    """One BREP holding one plane face in z = 0 bounded by the point loops (first = outer, rest = holes)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        curve_loops = []
        for pts in loops:
            tags = [gmsh.model.occ.addPoint(x, y, 0) for x, y in pts]
            lines = [gmsh.model.occ.addLine(tags[k], tags[(k + 1) % len(tags)]) for k in range(len(tags))]
            curve_loops.append(gmsh.model.occ.addCurveLoop(lines))
        gmsh.model.occ.addPlaneSurface(curve_loops)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def add_sector(inner, outer, a0=0.0, a1=360.0):
    """OCC face(s) of the ring (a disc when inner is 0) between the radii from angle a0 to a1 (degrees; under 180
    apart unless a full turn). Gmsh must be initialized."""
    occ = gmsh.model.occ
    face = [(2, occ.addDisk(0, 0, 0, outer, outer))]
    if inner:
        face = occ.cut(face, [(2, occ.addDisk(0, 0, 0, inner, inner))])[0]
    if a1 - a0 < 360:
        far = 4 * outer
        rays = [math.radians(a) for a in (a0, (a0 + a1) / 2, a1)]
        pts = [occ.addPoint(0, 0, 0)] + [occ.addPoint(far * math.cos(a), far * math.sin(a), 0) for a in rays]
        wedge = occ.addPlaneSurface([occ.addCurveLoop([occ.addLine(pts[k], pts[(k + 1) % 4]) for k in range(4)])])
        face = occ.intersect(face, [(2, wedge)])[0]
    return face


def write_sectors(path, *sectors):
    """One BREP holding the faces add_sector(*s) for each s."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        for s in sectors:
            add_sector(*s)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_arc(path, r, a0, a1):
    """A circle arc about the origin in z = 0 from angle a0 to a1 (degrees)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addCircle(0, 0, 0, r, angle1=math.radians(a0), angle2=math.radians(a1))
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def read_nodes(path):
    """{node tag: (x, y, z)} of a mesh file."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        tags, coords = gmsh.model.mesh.getNodes()[:2]
    finally:
        gmsh.finalize()
    return {int(t): tuple(coords[3 * k : 3 * k + 3]) for k, t in enumerate(tags)}


def square_lines(x=0.0, y=0.0, w=1.0, h=1.0):
    """Bottom, right, top, left edges of a rectangle in z = 0 as point pairs."""
    c = [(x, y, 0), (x + w, y, 0), (x + w, y + h, 0), (x, y + h, 0)]
    return [(c[k], c[(k + 1) % 4]) for k in range(4)]


class Mesher2DTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.mkdir(os.path.join(self.dir, "geometry"))

    def tearDown(self):
        self.tmp.cleanup()

    def geo(self, name):
        return os.path.join(self.dir, "geometry", name)

    def body(self, id_, name, file, size=0.5):
        return {"mat_id": id_, "name": name, "file": "geometry/" + file, "size": size}

    def run_job(
        self,
        bodies,
        sizes=(),
        version=4.1,
        options=None,
        mesh_file=None,
        transfinite=None,
        recombine=None,
        air=None,
        extra=None,
    ):
        job = {
            "dimension": "2D",
            "model_name": "Model",
            "msh_version": version,
            "mesh_file": mesh_file or os.path.join(self.dir, "pre_geom2D.msh"),
            "bodies": list(bodies),
            "sizes": list(sizes),
        }
        if options is not None:
            job["options"] = options
        if transfinite is not None:
            job["transfinite"] = transfinite
        if recombine is not None:
            job["recombine"] = list(recombine)
        if air is not None:
            job["air"] = air
        job.update(extra or {})  # e.g. the slide keys
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        return subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")

    def open_msh(self):
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(os.path.join(self.dir, "pre_geom2D.msh"))
        self.addCleanup(gmsh.finalize)

    def triangles(self, group):
        ents = gmsh.model.getEntitiesForPhysicalGroup(2, group)
        return sum(len(gmsh.model.mesh.getElements(2, e)[1][0]) for e in ents)

    def last_error(self, r):
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR:"), last)
        return last

    def edge_item(self, name, lines, n, distribution="Uniform", coef=1.0):
        """Write each (p, q) line as geometry/<name>_<k>.brep; returns the job's Transfinite Edges entry."""
        files = []
        for k, (p, q) in enumerate(lines, 1):
            write_line(self.geo(f"{name}_{k}.brep"), p, q)
            files.append(f"geometry/{name}_{k}.brep")
        return {"name": name, "nodes": n + 1, "distribution": distribution, "coef": coef, "files": files}

    def corner_files(self, name, points):
        files = []
        for k, p in enumerate(points, 1):
            write_point(self.geo(f"{name}_{k}.brep"), p)
            files.append(f"geometry/{name}_{k}.brep")
        return files

    def element_counts(self, group, dim=2):
        """{element name: count} in a physical group of the open mesh."""
        out = {}
        for e in gmsh.model.getEntitiesForPhysicalGroup(dim, group):
            types, tags = gmsh.model.mesh.getElements(dim, e)[:2]
            for t, ts in zip(types, tags):
                name = gmsh.model.mesh.getElementProperties(t)[0]
                out[name] = out.get(name, 0) + len(ts)
        return out

    def test_two_touching_squares_get_ids_names_triangles_and_shared_nodes(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep"), self.body(2, "Air_Sq001", "vol_2.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        self.open_msh()
        groups = {t: gmsh.model.getPhysicalName(2, t) for _, t in gmsh.model.getPhysicalGroups(2)}
        self.assertEqual(groups, {1: "Copper_Sq", 2: "Air_Sq001"})
        self.assertEqual(list(gmsh.model.mesh.getElementTypes(2)), [2], "only 3-node triangles")
        nodes1 = set(gmsh.model.mesh.getNodesForPhysicalGroup(2, 1)[0])
        nodes2 = set(gmsh.model.mesh.getNodesForPhysicalGroup(2, 2)[0])
        self.assertTrue(nodes1 & nodes2, "no shared nodes on the common edge")

    def test_body_of_several_faces_is_one_group(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1), (1, 0, 1, 1)])  # one body, two touching faces
        r = self.run_job([self.body(1, "Two_Part", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(gmsh.model.getPhysicalName(2, 1), "Two_Part")
        self.assertEqual(len(gmsh.model.getEntitiesForPhysicalGroup(2, 1)), 2)

    def test_smaller_size_gives_denser_mesh(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        r = self.run_job(
            [self.body(1, "Fine_Sq", "vol_1.brep", size=0.05), self.body(2, "Coarse_Sq", "vol_2.brep", size=0.5)]
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertGreater(self.triangles(1), 10 * self.triangles(2))

    def mesh_square_with_size(self, make=None, size=0.05):
        """Mesh a unit square at size 0.5, plus one size item from geometry/size_1_1.brep when make(path) writes it.
        Returns the node coordinates as (x, y, z) tuples."""
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        sizes = []
        if make:
            make(self.geo("size_1_1.brep"))
            sizes = [{"name": "Fine", "size": size, "files": ["geometry/size_1_1.brep"]}]
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], sizes=sizes)
        self.assertEqual(r.returncode, 0, r.stderr)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(os.path.join(self.dir, "pre_geom2D.msh"))
            c = gmsh.model.mesh.getNodes()[1]
        finally:
            gmsh.finalize()
        return [tuple(c[i : i + 3]) for i in range(0, len(c), 3)]

    def test_face_size_refines_that_face(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        write_rects(self.geo("size_1_1.brep"), [(1, 0, 1, 1)])  # the second square, as a size item
        r = self.run_job(
            [self.body(1, "A_Sq", "vol_1.brep"), self.body(2, "B_Sq001", "vol_2.brep")],
            sizes=[{"name": "Fine", "size": 0.05, "files": ["geometry/size_1_1.brep"]}],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertGreater(self.triangles(2), 10 * self.triangles(1))

    def test_edge_size_refines_that_edge(self):
        nodes = self.mesh_square_with_size(lambda p: write_line(p, (0, 0, 0), (1, 0, 0)))  # the bottom edge
        bottom = sum(abs(y) < 1e-9 for x, y, z in nodes)
        top = sum(abs(y - 1) < 1e-9 for x, y, z in nodes)
        self.assertGreaterEqual(bottom, 20)
        self.assertLess(top, 5)

    def test_vertex_size_refines_around_that_corner(self):
        def near_corner(nodes):
            return sum(0 < x * x + y * y < 0.3**2 for x, y, z in nodes)

        before = near_corner(self.mesh_square_with_size())
        after = near_corner(self.mesh_square_with_size(lambda p: write_point(p, (0, 0, 0))))
        self.assertGreater(after, before)

    def test_zx_plane_keeps_y_zero(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)], plane="ZX")
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        coords = gmsh.model.mesh.getNodes()[1]
        self.assertTrue(len(coords) > 0)
        for y in coords[1::3]:
            self.assertAlmostEqual(y, 0.0, places=9)
        self.assertGreater(max(coords[2::3]), 0.9)  # the square really stands along z

    def test_options_are_applied(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        plain = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")])
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.open_msh()
        before = self.triangles(1)
        finer = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], options={"Mesh.MeshSizeFactor": 0.5})
        self.assertEqual(finer.returncode, 0, finer.stderr)
        gmsh.clear()
        gmsh.open(os.path.join(self.dir, "pre_geom2D.msh"))
        self.assertGreater(self.triangles(1), 2 * before)

    def test_unknown_option_fails_cleanly(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], options={"Mesh.NoSuchOption": 1})
        self.assertIn("NoSuchOption", self.last_error(r))

    def test_msh_version_22(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], version=2.2)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.dir, "pre_geom2D.msh"), encoding="ascii") as fh:
            self.assertEqual(fh.read().split()[:2], ["$MeshFormat", "2.2"])

    def test_mesh_goes_to_mesh_file_and_unv_beside_the_job(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        target = os.path.join(self.dir, "run dir", "pre_geom2D.msh")
        os.mkdir(os.path.dirname(target))
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], mesh_file=target)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(target))
        self.assertTrue(os.path.isfile(os.path.join(self.dir, "mesh.unv")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "pre_geom2D.msh")))
        self.assertIn("MAT_ID", r.stdout)
        self.assertIn(f"Wrote {target}", r.stdout)

    def write_old_mesh(self):
        path = os.path.join(self.dir, "pre_geom2D.msh")
        with open(path, "w", encoding="ascii") as fh:
            fh.write("old")
        return path

    def read_text(self, path):
        with open(path, encoding="ascii") as fh:
            return fh.read()

    def test_existing_mesh_is_replaced(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        target = self.write_old_mesh()
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.read_text(target).startswith("$MeshFormat"))

    def test_failed_run_keeps_the_existing_mesh(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(0.5, 0, 1, 1)])  # overlaps vol_1
        target = self.write_old_mesh()
        r = self.run_job([self.body(1, "A_Sq", "vol_1.brep"), self.body(2, "B_Sq001", "vol_2.brep")])
        self.last_error(r)
        self.assertEqual(self.read_text(target), "old")

    def test_read_only_mesh_fails_cleanly_and_stays(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        target = self.write_old_mesh()
        os.chmod(target, stat.S_IREAD)
        try:
            r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")])
        finally:
            os.chmod(target, stat.S_IREAD | stat.S_IWRITE)  # let the temporary folder be deleted
        self.assertEqual(
            self.last_error(r), f"ERROR: Could not replace {target}: it is read-only or open in another program."
        )
        self.assertEqual(self.read_text(target), "old")

    def test_overlapping_squares_fail(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(0.5, 0, 1, 1)])
        r = self.run_job([self.body(1, "A_Sq", "vol_1.brep"), self.body(2, "B_Sq001", "vol_2.brep")])
        self.assertIn("overlap", self.last_error(r))

    def test_size_item_off_the_bodies_fails(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("size_1_1.brep"), [(5, 5, 1, 1)])  # a square far from the body
        r = self.run_job(
            [self.body(1, "Copper_Sq", "vol_1.brep")],
            sizes=[{"name": "Fine", "size": 0.1, "files": ["geometry/size_1_1.brep"]}],
        )
        self.assertIn("Fine", self.last_error(r))

    def test_a_solid_body_fails(self):
        write_box(self.geo("vol_1.brep"))
        r = self.run_job([self.body(1, "Copper_Box", "vol_1.brep")])
        self.assertIn("vol_1.brep", self.last_error(r))

    def test_no_bodies_fails(self):
        self.assertIn("no bodies", self.last_error(self.run_job([])))

    def test_missing_geometry_file_fails_cleanly(self):
        self.last_error(self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")]))

    def structured(self, *names_ids, corners=None):
        return [{"name": n, "mat_id": i, "corner_files": (corners or {}).get(n, [])} for n, i in names_ids]

    def test_structured_square_with_recombine_has_only_quads(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines(), 4)]}
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], recombine=[1], transfinite=tf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Quadrilateral 4": 16})

    def test_structured_square_without_recombine_has_structured_triangles(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines(), 4)]}
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite=tf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Triangle 3": 32})

    def test_bump_below_one_refines_the_edge_ends(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        edges = self.edge_item("tedge_1", square_lines(), 10, "Bump", 0.2)
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite={"bodies": [], "edges": [edges]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        c = gmsh.model.mesh.getNodes()[1]
        xs = sorted(c[i] for i in range(0, len(c), 3) if abs(c[i + 1]) < 1e-9)  # nodes on the bottom edge
        gaps = [b - a for a, b in zip(xs, xs[1:])]
        self.assertEqual(len(gaps), 10)
        self.assertLess(gaps[0] * 2, gaps[5])

    def test_structured_square_next_to_an_unstructured_one_shares_nodes(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines(), 4)]}
        r = self.run_job(
            [self.body(1, "Core", "vol_1.brep"), self.body(2, "Air", "vol_2.brep", size=0.1)], transfinite=tf
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Triangle 3": 32})
        nodes1 = set(gmsh.model.mesh.getNodesForPhysicalGroup(2, 1)[0])
        nodes2 = set(gmsh.model.mesh.getNodesForPhysicalGroup(2, 2)[0])
        self.assertEqual(len(nodes1 & nodes2), 5, "the shared edge has 4 elements, so 5 shared nodes")

    def test_five_point_face_with_chosen_corners(self):
        write_polygons(self.geo("vol_1.brep"), [[(0, 0), (0.5, 0), (1, 0), (1, 1), (0, 1)]])
        bottom = self.edge_item("tedge_1", [((0, 0, 0), (0.5, 0, 0)), ((0.5, 0, 0), (1, 0, 0))], 2)
        sides = self.edge_item("tedge_2", square_lines()[1:], 4)  # right, top, left
        corners = {"Core": self.corner_files("corner_1", [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])}
        tf = {"bodies": self.structured(("Core", 1), corners=corners), "edges": [bottom, sides]}
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], recombine=[1], transfinite=tf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Quadrilateral 4": 16})

    def test_five_point_face_finds_corners_where_the_boundary_turns(self):
        write_polygons(self.geo("vol_1.brep"), [[(0, 0), (0.5, 0), (1, 0), (1, 1), (0, 1)]])
        bottom = self.edge_item("tedge_1", [((0, 0, 0), (0.5, 0, 0)), ((0.5, 0, 0), (1, 0, 0))], 2)
        sides = self.edge_item("tedge_2", square_lines()[1:], 4)
        tf = {"bodies": self.structured(("Core", 1)), "edges": [bottom, sides]}
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], recombine=[1], transfinite=tf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: structured body Core", r.stderr)
        self.assertIn("5 boundary points; using the 4 where the boundary turns", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Quadrilateral 4": 16})

    def test_pentagon_without_corners_is_an_error(self):
        pts = [(0, 0), (1, 0), (1, 1), (0.5, 1.5), (0, 1)]
        write_polygons(self.geo("vol_1.brep"), [pts])
        lines = [((*pts[k], 0), (*pts[(k + 1) % 5], 0)) for k in range(5)]
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", lines, 2)]}
        last = self.last_error(self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite=tf))
        self.assertIn("structured body Core", last)
        self.assertIn("5 boundary points and 5 corners", last)

    def test_opposite_sides_with_different_counts_are_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        b, r_, t, l_ = square_lines()
        tf = {
            "bodies": self.structured(("Core", 1)),
            "edges": [self.edge_item("tedge_1", [b, t, l_], 4), self.edge_item("tedge_2", [r_], 6)],
        }
        last = self.last_error(self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite=tf))
        self.assertIn("opposite sides", last)

    def test_structured_face_edge_without_item_is_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines()[:3], 4)]}
        last = self.last_error(self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite=tf))
        self.assertIn("without Transfinite Edges", last)

    def test_edge_that_did_not_merge_is_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        far = self.edge_item("tedge_1", [((5, 5, 0), (6, 5, 0))], 4)
        last = self.last_error(
            self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite={"bodies": [], "edges": [far]})
        )
        self.assertIn("Transfinite Edges tedge_1", last)
        self.assertIn("did not merge", last)

    def test_shared_edge_with_two_settings_is_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        tf = {
            "bodies": self.structured(("A", 1), ("B", 2)),
            "edges": [self.edge_item("tedge_1", square_lines(), 4), self.edge_item("tedge_2", square_lines(1), 6)],
        }
        last = self.last_error(
            self.run_job([self.body(1, "A", "vol_1.brep"), self.body(2, "B", "vol_2.brep")], transfinite=tf)
        )
        self.assertIn("different settings", last)

    def test_edge_split_by_a_touching_body_shares_its_elements(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 0.5)])  # its corner (1, 0.5) splits Core's right edge
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines(), 4)]}
        r = self.run_job(
            [self.body(1, "Core", "vol_1.brep"), self.body(2, "Air", "vol_2.brep")],
            recombine=[1],
            transfinite=tf,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: Transfinite Edges tedge_1: tedge_1_2.brep was split into 2 pieces", r.stderr)
        self.assertIn("elements 2 + 2", r.stderr)
        self.assertIn("where the boundary turns", r.stderr)  # the split adds a 5th point to Core's face
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Quadrilateral 4": 16}, "the total stays 4 per side")

    def on_top(self, core_top, top_n, tops=((1, 1),)):
        """Core 4 x 1 with 2 elements up and core_top along x; each (x, w) in tops is a w x 1 body on Core's
        top edge with top_n elements on every edge. All structured and recombined."""
        write_rects(self.geo("vol_1.brep"), [(0, 0, 4, 1)])
        b, r_, t, l_ = square_lines(0, 0, 4, 1)
        edges = [self.edge_item("tedge_1", [b, t], core_top), self.edge_item("tedge_2", [r_, l_], 2)]
        bodies = [self.body(1, "Core", "vol_1.brep")]
        for k, (x, w) in enumerate(tops, 2):
            write_rects(self.geo(f"vol_{k}.brep"), [(x, 1, w, 1)])
            edges.append(self.edge_item(f"tedge_{k + 1}", square_lines(x, 1, w, 1), top_n))
            bodies.append(self.body(k, f"Top{k}", f"vol_{k}.brep"))
        ids = [(b_["name"], b_["mat_id"]) for b_ in bodies]
        tf = {"bodies": self.structured(*ids), "edges": edges}
        return self.run_job(bodies, recombine=[i for _, i in ids], transfinite=tf)

    def test_split_edge_keeps_the_piece_another_item_sets_and_shares_the_rest(self):
        r = self.on_top(8, 2)  # Core's top: 1 | 1 set to 2 by Top | 2 -> the other 6 shared by length: 2 + 4
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("split into 3 pieces", r.stderr)
        self.assertIn("(set by tedge_3)", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Quadrilateral 4": 16}, "8 along x stays 8")
        self.assertEqual(self.element_counts(2), {"Quadrilateral 4": 4})
        c = gmsh.model.mesh.getNodes()[1]
        top = [c[i] for i in range(0, len(c), 3) if abs(c[i + 1] - 1) < 1e-9]
        self.assertEqual(len([x for x in top if 0 < x < 1]), 1, "first piece: 2 elements")
        self.assertEqual(len([x for x in top if 2 < x < 4]), 3, "last piece: 4 elements")

    def test_split_edge_with_too_few_elements_left_is_an_error(self):
        last = self.last_error(self.on_top(3, 2))  # 3 - 2 leaves 1 for 2 pieces
        self.assertIn("Transfinite Edges tedge_1", last)
        self.assertIn("2 of them set by tedge_3", last)
        self.assertIn("1 left for 2 pieces", last)

    def test_split_edge_set_fully_by_others_must_add_up(self):
        last = self.last_error(self.on_top(5, 2, tops=((0, 2), (2, 2))))  # 2 + 2 set, but 5 asked
        self.assertIn("Transfinite Edges tedge_1", last)
        self.assertIn("all its pieces are set by other Transfinite Edges (4 elements:", last)

    def test_split_edge_set_fully_by_others_that_add_up_meshes(self):
        r = self.on_top(4, 2, tops=((0, 2), (2, 2)))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_split_bump_edge_is_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 0.5)])
        edges = self.edge_item("tedge_1", square_lines(), 4, "Bump", 0.5)
        tf = {"bodies": self.structured(("Core", 1)), "edges": [edges]}
        last = self.last_error(
            self.run_job([self.body(1, "Core", "vol_1.brep"), self.body(2, "Air", "vol_2.brep")], transfinite=tf)
        )
        self.assertIn("split into 2 pieces", last)
        self.assertIn("Bump", last)

    def test_structured_face_with_a_hole_is_an_error(self):
        outer, inner = [(0, 0), (3, 0), (3, 3), (0, 3)], [(1, 1), (2, 1), (2, 2), (1, 2)]
        write_polygons(self.geo("vol_1.brep"), [outer, inner])
        lines = square_lines(0, 0, 3, 3) + square_lines(1, 1, 1, 1)
        corners = {"Frame": self.corner_files("corner_1", [(x, y, 0) for x, y in outer])}
        tf = {"bodies": self.structured(("Frame", 1), corners=corners), "edges": [self.edge_item("tedge_1", lines, 3)]}
        last = self.last_error(self.run_job([self.body(1, "Frame", "vol_1.brep")], transfinite=tf))
        self.assertIn("not one loop", last)

    def test_face_with_a_hole_and_no_corners_says_not_one_loop(self):
        outer, inner = [(0, 0), (3, 0), (3, 3), (0, 3)], [(1, 1), (2, 1), (2, 2), (1, 2)]
        write_polygons(self.geo("vol_1.brep"), [outer, inner])
        lines = square_lines(0, 0, 3, 3) + square_lines(1, 1, 1, 1)
        tf = {"bodies": self.structured(("Frame", 1)), "edges": [self.edge_item("tedge_1", lines, 3)]}
        last = self.last_error(self.run_job([self.body(1, "Frame", "vol_1.brep")], transfinite=tf))
        self.assertIn("structured body Frame", last)
        self.assertIn("not one loop", last)

    def triangle_job(self, bottom, slope, left, recombine=0):
        """Triangle (0, 0), (2, 0), (0, 1): structured, with these element counts on its three edges."""
        pts = [(0, 0), (2, 0), (0, 1)]
        write_polygons(self.geo("vol_1.brep"), [pts])
        p = [(x, y, 0) for x, y in pts]
        edges = [
            self.edge_item("tedge_1", [(p[0], p[1])], bottom),
            self.edge_item("tedge_2", [(p[1], p[2])], slope),
            self.edge_item("tedge_3", [(p[2], p[0])], left),
        ]
        tf = {"bodies": self.structured(("Tri", 1)), "edges": edges}
        return self.run_job([self.body(1, "Tri", "vol_1.brep")], recombine=[1] if recombine else None, transfinite=tf)

    def test_triangle_with_two_equal_sides_is_structured(self):
        for counts in ((4, 6, 4), (6, 4, 4), (4, 4, 6)):  # the equal sides meet at each of the three points
            with self.subTest(counts=counts):
                r = self.triangle_job(*counts, recombine=1)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertNotIn("cannot be meshed", r.stdout + r.stderr)
                gmsh.initialize()
                try:
                    gmsh.option.setNumber("General.Terminal", 0)
                    gmsh.open(os.path.join(self.dir, "pre_geom2D.msh"))
                    self.assertEqual(self.element_counts(1), {"Triangle 3": 6, "Quadrilateral 4": 18})
                finally:
                    gmsh.finalize()

    def test_triangle_without_two_equal_sides_is_an_error(self):
        last = self.last_error(self.triangle_job(2, 4, 6))
        self.assertIn("structured body Tri", last)
        self.assertIn("2/4/6", last)

    def test_recombine_gives_quads_only_in_the_chosen_body(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        r = self.run_job(
            [self.body(1, "A", "vol_1.brep", 0.2), self.body(2, "B", "vol_2.brep", 0.2)],
            options={"Mesh.RecombinationAlgorithm": 3},
            recombine=[1],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Recombined      A", r.stdout)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Quadrilateral 4"})
        self.assertEqual(set(self.element_counts(2)), {"Triangle 3"})

    def test_full_quad_algorithm_reaches_gmsh(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        counts = {}
        for alg in (1, 3):
            r = self.run_job(
                [self.body(1, "A", "vol_1.brep", 0.2)], options={"Mesh.RecombinationAlgorithm": alg}, recombine=[1]
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            gmsh.initialize()
            try:
                gmsh.option.setNumber("General.Terminal", 0)
                gmsh.open(os.path.join(self.dir, "pre_geom2D.msh"))
                counts[alg] = self.element_counts(1)
            finally:
                gmsh.finalize()
        self.assertEqual(set(counts[3]), {"Quadrilateral 4"})
        self.assertGreater(counts[3]["Quadrilateral 4"], sum(counts[1].values()), "full-quad splits into more quads")

    def full_quad_core_and_air(self, n, recombine):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines(), n)]}
        return self.run_job(
            [self.body(1, "Core", "vol_1.brep"), self.body(2, "Air", "vol_2.brep", 0.3)],
            options={"Mesh.RecombinationAlgorithm": 3},
            transfinite=tf,
            recombine=recombine,
        )

    def test_full_quad_with_an_odd_transfinite_count_next_to_a_recombined_body_is_an_error(self):
        for recombine in ([1, 2], [2]):
            with self.subTest(recombine=recombine):
                last = self.last_error(self.full_quad_core_and_air(3, recombine))
                self.assertTrue(last.startswith("ERROR: recombine: full-quad"), last)
                self.assertIn("Air", last)
                self.assertIn("tedge_1", last)

    def test_full_quad_with_an_even_transfinite_count_meshes(self):
        r = self.full_quad_core_and_air(4, [1, 2])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(2)), {"Quadrilateral 4"})

    def test_job_without_recombine_key_has_only_triangles(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        r = self.run_job([self.body(1, "A", "vol_1.brep", 0.2)], options={"Mesh.RecombinationAlgorithm": 1})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Triangle 3"})

    def air_area_and_nodes(self, group):
        """Total triangle area of a physical group, and its triangle corner points."""
        area, pts = 0.0, []
        for e in gmsh.model.getEntitiesForPhysicalGroup(2, group):
            _, tags, nodes = gmsh.model.mesh.getElements(2, e)
            coords = {n: gmsh.model.mesh.getNode(n)[0] for n in nodes[0]}
            for k in range(0, len(nodes[0]), 3):
                (x1, y1, _), (x2, y2, _), (x3, y3, _) = (coords[n] for n in nodes[0][k : k + 3])
                area += abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2
                pts += [(x1, y1), (x2, y2), (x3, y3)]
        return area, pts

    def test_air_fills_around_body_and_body_wins(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("air.brep"), [(-1, -1, 3, 3)])
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.5}
        r = self.run_job([self.body(1, "Body", "vol_1.brep")], air=air)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("MAT_ID       2  Air", r.stdout)
        self.open_msh()
        groups = {t: gmsh.model.getPhysicalName(2, t) for _, t in gmsh.model.getPhysicalGroups(2)}
        self.assertEqual(groups, {1: "Body", 2: "Air"})
        self.assertGreater(self.triangles(1), 0)
        self.assertGreater(self.triangles(2), 0)
        area, pts = self.air_area_and_nodes(2)
        self.assertAlmostEqual(area, 9 - 1, delta=1e-6)
        eps = 1e-9
        self.assertFalse([p for p in pts if eps < p[0] < 1 - eps and eps < p[1] < 1 - eps])

    def test_air_covered_by_bodies_fails_cleanly(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("air.brep"), [(0, 0, 1, 1)])
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.5}
        r = self.run_job([self.body(1, "Body", "vol_1.brep")], air=air)
        self.assertEqual(self.last_error(r), "ERROR: the air region is fully covered by bodies")

    def test_face_size_inside_the_air_merges(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("air.brep"), [(-1, -1, 3, 3)])
        write_rects(self.geo("size_1.brep"), [(1, 0, 1, 1)])  # a face inside the air only
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.5}
        sizes = [{"name": "Fine", "size": 0.2, "files": ["geometry/size_1.brep"]}]
        r = self.run_job([self.body(1, "Body", "vol_1.brep")], sizes=sizes, air=air)
        self.assertEqual(r.returncode, 0, r.stderr)

    # ---- sliding motion: the fixed side goes to pre_geom2D.msh, the moving side to rotor_mesh2D.msh

    def files(self):
        return os.path.join(self.dir, "pre_geom2D.msh"), os.path.join(self.dir, "rotor_mesh2D.msh")

    def slide(self, name, id_, files, n, full=False, kind="rotational"):
        """A slide entry; its marker is geometry/marker_<id_>.brep."""
        return {
            "name": name,
            "kind": kind,
            "files": ["geometry/" + f for f in files],
            "marker": f"geometry/marker_{id_}.brep",
            "divisions": n,
            "slide_mat_id": id_,
            "full": full,
        }

    def slide_job(self, bodies, moving, slides, periodic=None, fine=None):
        """Run a slide job: air from geometry/air.brep (fixed ID 10, moving 11), moving cell geometry/cell_1.brep.
        fine: (p, q), a line on the second periodic boundary meshed at size 1; the period must undo it."""
        sides = {"fixed": {"mat_id": 10, "name": "Air_fixed"}, "moving": {"mat_id": 11, "name": "Air_moving"}}
        air = {"sides": sides, "file": "geometry/air.brep", "size": 5.0}
        extra = {
            "rotor_file": self.files()[1],
            "moving": moving,
            "moving_cells": ["geometry/cell_1.brep"],
            "slides": slides,
        }
        if periodic:
            extra["periodic"] = periodic
        sizes = []
        if fine:
            write_line(self.geo("size_1.brep"), *fine)
            sizes = [{"name": "Fine", "size": 1.0, "files": ["geometry/size_1.brep"]}]
        return self.run_job(bodies, sizes=sizes, air=air, extra=extra)

    def motor_job(self, tooth=None, rotor=40):
        """Full turn: stator ring 45..80 fixed (tooth: plus a tooth 42.5..45 between these two angles), rotor disc r 40
        (rotor) moving, air disc r 100, slide circle r 42.5 in two halves with 72 divisions, slide point at (42.5, 0)."""
        write_sectors(self.geo("vol_1.brep"), (45, 80), *([(42.5, 45, *tooth)] if tooth else []))
        write_sectors(self.geo("vol_2.brep"), (0, rotor))
        write_sectors(self.geo("air.brep"), (0, 100))
        write_sectors(self.geo("cell_1.brep"), (0, 42.5))
        write_arc(self.geo("slide_20_1.brep"), 42.5, 0, 180)
        write_arc(self.geo("slide_20_2.brep"), 42.5, 180, 360)
        write_point(self.geo("marker_20.brep"), (42.5, 0, 0))
        bodies = [self.body(1, "Stator", "vol_1.brep", 5), self.body(2, "Rotor", "vol_2.brep", 5)]
        return self.slide_job(bodies, [2], [self.slide("Slide", 20, ["slide_20_1.brep", "slide_20_2.brep"], 72, True)])

    def sector_job(self, stator=(82, 149, 0, 45)):
        """The 45° machine: shaft r < 30 and rotor 30..78 moving, stator fixed, air sector r 200, slide arc
        r 80.575 with 90 divisions, rotation period 45°."""
        write_sectors(self.geo("vol_1.brep"), stator)
        write_sectors(self.geo("vol_2.brep"), (0, 30, 0, 45))
        write_sectors(self.geo("vol_3.brep"), (30, 78, 0, 45))
        write_sectors(self.geo("air.brep"), (0, 200, 0, 45))
        write_sectors(self.geo("cell_1.brep"), (0, 80.575, 0, 45))
        write_arc(self.geo("slide_20_1.brep"), 80.575, 0, 45)
        write_point(self.geo("marker_20.brep"), (80.575, 0, 0))
        bodies = [self.body(k, n, f"vol_{k}.brep", 5) for k, n in ((1, "Stator"), (2, "Shaft"), (3, "Rotor"))]
        c = math.cos(math.pi / 4)
        fine = ((149 * c, 149 * c, 0), (200 * c, 200 * c, 0))  # the air edge at 45°
        period = {"kind": "rotation", "angle": 45.0, "start": 0.0}
        return self.slide_job(bodies, [2, 3], [self.slide("Slide", 20, ["slide_20_1.brep"], 90)], period, fine=fine)

    def on_circle(self, path, r):
        return sorted(
            tuple(round(x, 9) for x in p) for p in read_nodes(path).values() if abs(math.hypot(*p) - r) < 1e-6
        )

    def angles(self, points):
        return sorted(round(math.degrees(math.atan2(y, x)), 6) % 360 for x, y, _ in points)

    def test_full_circle_slide_has_n_nodes_on_both_sides(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (self.on_circle(f, 42.5) for f in self.files())
        self.assertEqual(len(fixed), 72)
        self.assertEqual(fixed, moving)
        for got, want in zip(self.angles(fixed), range(0, 360, 5)):
            self.assertAlmostEqual(got, want, places=6)

    def test_rotor_file_has_slide_point_at_start_angle(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, rotor = self.files()
        gmsh.initialize()
        self.addCleanup(gmsh.finalize)
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(rotor)
        self.assertEqual(gmsh.model.getPhysicalGroups(0), [(0, 20)])
        self.assertEqual(gmsh.model.getPhysicalName(0, 20), "Slide")
        (point,) = gmsh.model.getEntitiesForPhysicalGroup(0, 20)
        types, _, nodes = gmsh.model.mesh.getElements(0, point)
        self.assertEqual((list(types), len(nodes[0])), ([15], 1))
        x, y, z = gmsh.model.mesh.getNode(nodes[0][0])[0]
        self.assertEqual((round(x, 9), round(y, 9) + 0.0, z), (42.5, 0, 0))
        gmsh.open(fixed)
        self.assertEqual(gmsh.model.getPhysicalGroups(0), [])

    def test_each_file_numbers_nodes_from_one(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        for path in self.files():
            tags = read_nodes(path)
            self.assertEqual((min(tags), max(tags)), (1, len(tags)), path)

    def test_air_split_by_side(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("MAT_ID      10  Air_fixed", r.stdout)
        self.assertIn("MAT_ID      11  Air_moving", r.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "mesh.msh")))
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        found = []
        for path in self.files():
            gmsh.initialize()
            try:
                gmsh.option.setNumber("General.Terminal", 0)
                gmsh.open(path)
                found.append({t: gmsh.model.getPhysicalName(2, t) for _, t in gmsh.model.getPhysicalGroups(2)})
                self.assertTrue(all(self.triangles(t) for t in found[-1]))
            finally:
                gmsh.finalize()
        self.assertEqual(found, [{1: "Stator", 10: "Air_fixed"}, {2: "Rotor", 11: "Air_moving"}])

    def test_air_side_without_elements_is_not_listed(self):
        r = self.motor_job(rotor=42.5)  # the rotor fills the moving cell: no moving air
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("MAT_ID      10  Air_fixed", r.stdout)
        self.assertNotIn("Air_moving", r.stdout)
        fixed, moving = (self.on_circle(f, 42.5) for f in self.files())
        self.assertEqual(len(fixed), 72)
        self.assertEqual(fixed, moving)
        text = report(self.dir, os.path.join(self.dir, "job.json"))  # must not raise "has no elements"
        self.assertIn("no Air_moving", text)

    def test_sector_slide_and_periodic_edges_match(self):
        r = self.sector_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (self.on_circle(f, 80.575) for f in self.files())
        self.assertEqual(len(fixed), 91)
        self.assertEqual(fixed, moving)
        for got, want in zip(self.angles(fixed), [k / 2 for k in range(91)]):
            self.assertAlmostEqual(got, want, places=6)
        for path in self.files():
            pts = read_nodes(path).values()
            start = sorted(round(x, 6) for x, y, _ in pts if abs(y) < 1e-9)
            end = sorted(round(math.hypot(x, y), 6) for x, y, _ in pts if abs(x - y) < 1e-7)
            self.assertGreater(len(start), 10)
            self.assertEqual(start, end, path)

    def test_body_vertex_on_slide_circle_keeps_n_nodes(self):
        r = self.motor_job(tooth=(10, 20))  # on the 5° grid
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (self.on_circle(f, 42.5) for f in self.files())
        self.assertEqual(len(fixed), 72)
        self.assertEqual(fixed, moving)
        for got, want in zip(self.angles(fixed), range(0, 360, 5)):
            self.assertAlmostEqual(got, want, places=6)

    def test_body_vertex_between_two_divisions_fails_cleanly(self):
        last = self.last_error(self.motor_job(tooth=(12, 20)))
        self.assertIn("sliding interface Slide: slide_20_1.brep: the point at (41.571", last)
        self.assertIn("at 12° lies between two divisions along the motion", last)
        self.assertIn("seam of a round body face", last)
        self.assertIn("(every 5°)", last)

    def test_nonperiodic_geometry_fails_cleanly(self):
        r = self.sector_job(stator=(82, 149, 0, 30))  # cut by 0° but not by 45°
        self.assertTrue(self.last_error(r).startswith("ERROR: periodic boundaries do not match"), r.stderr)

    def test_linear_two_slides_and_translation_period(self):
        """Case 16: a mover between two stators, two slide lines, the period is the 80 mm air box length."""
        write_rects(self.geo("vol_1.brep"), [(0, 0, 80, 20)])
        write_rects(self.geo("vol_2.brep"), [(0, 40, 80, 20)])
        write_rects(self.geo("vol_3.brep"), [(0, 24, 80, 12)])
        write_rects(self.geo("air.brep"), [(0, 0, 80, 60)])
        write_rects(self.geo("cell_1.brep"), [(0, 22, 80, 16)])
        slides = []
        for id_, y in ((20, 22), (21, 38)):
            write_line(self.geo(f"slide_{id_}_1.brep"), (0, y, 0), (80, y, 0))
            write_point(self.geo(f"marker_{id_}.brep"), (0, y, 0))
            slides.append(self.slide(f"Slide_{y}", id_, [f"slide_{id_}_1.brep"], 32, kind="linear"))
        bodies = [self.body(k, n, f"vol_{k}.brep", 5) for k, n in ((1, "Bottom"), (2, "Top"), (3, "Mover"))]
        period = {"kind": "translation", "vector": [80.0, 0.0, 0.0], "start": 0.0}
        r = self.slide_job(bodies, [3], slides, period, fine=((80, 0, 0), (80, 20, 0)))
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = []
        for path in self.files():
            pts = [tuple(round(x, 9) for x in p) for p in read_nodes(path).values()]
            lines.append([sorted(p for p in pts if abs(p[1] - y) < 1e-9) for y in (22, 38)])
            self.assertEqual([len(line) for line in lines[-1]], [33, 33], path)
            left = sorted(round(y, 6) for x, y, _ in pts if abs(x) < 1e-9)
            right = sorted(round(y, 6) for x, y, _ in pts if abs(x - 80) < 1e-9)
            self.assertGreater(len(left), 4)
            self.assertEqual(left, right, path)
        self.assertEqual(lines[0], lines[1])
        self.assertIn("DXYZ 0.08 0 0", r.stdout)

    def test_slide_report_lines(self):
        r = self.sector_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        for text in ("SLIDE_NDIV 90", "SLIDE_MAT_ID 20", "ANGLE 45", '"CYCLIC": 2', "UNIT = 1"):
            self.assertIn(text, r.stdout)
        self.assertLess(r.stdout.index("MAT_ID      10  Air_fixed"), r.stdout.index("SLIDE_NDIV 90"))

    def test_slide_report_half_turn_separates_the_boundaries(self):
        """ANGLE = 180 needs SEPARATE_ANGLE (handbook 14): the middle of the meshed half turn."""
        job = {"slides": [{"name": "Gap", "divisions": 90, "slide_mat_id": 20}]}
        job["periodic"] = {"kind": "rotation", "angle": 180.0, "start": 300.0}
        text = "\n".join(meshcommon.slide_report(job))
        self.assertIn("SEPARATE_ANGLE 30", text)
        self.assertIn('"SEPARATE_ANGLE": 30.0', text)
        job["periodic"]["angle"] = 90.0
        self.assertNotIn("SEPARATE_ANGLE", "\n".join(meshcommon.slide_report(job)))


if __name__ == "__main__":
    unittest.main()
