"""2D mesher tests. Run from the repo root: pixi run pytest tests/freecad_addon/test_mesher2d.py"""

import json
import math
import os
import stat
import subprocess
import sys
import tempfile
import unittest

import gmsh

from .test_mesher import write_line, write_point

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

    def run_job(self, bodies, sizes=(), version=4.1, options=None, mesh_file=None):
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


if __name__ == "__main__":
    unittest.main()
