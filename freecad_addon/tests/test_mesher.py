"""Mesher tests. Run from the repo root with FreeCAD's python.exe:
    python.exe -m unittest tests.test_mesher -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

import gmsh

MESHER = os.path.join(os.path.dirname(__file__), "..", "emsolution", "mesher.py")


def write_box(path, x, y, z, dx, dy, dz):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addBox(x, y, z, dx, dy, dz)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_rect(path, x, y, z, dx, dy):
    """Rectangle in the plane z = const."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addRectangle(x, y, z, dx, dy)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_line(path, p, q):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addLine(gmsh.model.occ.addPoint(*p), gmsh.model.occ.addPoint(*q))
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_point(path, p):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addPoint(*p)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


class MesherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.mkdir(os.path.join(self.dir, "geometry"))

    def tearDown(self):
        self.tmp.cleanup()

    def geo(self, name):
        return os.path.join(self.dir, "geometry", name)

    def run_job(self, volumes, surfaces=(), version=4.1, sizes=(), options=None):
        job = {"model_name": "Model", "msh_version": version,
               "volumes": list(volumes), "surfaces": list(surfaces), "sizes": list(sizes)}
        if options is not None:
            job["options"] = options
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        return subprocess.run([sys.executable, MESHER, path],
                              capture_output=True, encoding="utf-8", errors="replace")

    def open_msh(self):
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(os.path.join(self.dir, "Model.msh"))
        self.addCleanup(gmsh.finalize)

    def vol(self, id_, name, file, size=0.5):
        return {"id": id_, "name": name, "file": "geometry/" + file, "size": size}

    def test_two_touching_boxes_get_ids_names_and_shared_nodes(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep"),
                          self.vol(2, "Air_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "Model.unv")))
        self.open_msh()
        groups = {t: gmsh.model.getPhysicalName(3, t) for _, t in gmsh.model.getPhysicalGroups(3)}
        self.assertEqual(groups, {1: "Copper_Box", 2: "Air_Box001"})
        nodes1 = set(gmsh.model.mesh.getNodesForPhysicalGroup(3, 1)[0])
        nodes2 = set(gmsh.model.mesh.getNodesForPhysicalGroup(3, 2)[0])
        self.assertTrue(nodes1 & nodes2, "no shared nodes on the common face")

    def test_excitation_face_becomes_surface_group(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("surf_1001_1.brep"), 0, 0, 1, 1, 1)  # top face
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")],
                         [{"id": 1001, "name": "Terminal_In_Box", "volume_id": 1,
                           "files": ["geometry/surf_1001_1.brep"]}])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(gmsh.model.getPhysicalName(2, 1001), "Terminal_In_Box")
        _, coords = gmsh.model.mesh.getNodesForPhysicalGroup(2, 1001)
        self.assertTrue(len(coords) > 0)
        for z in coords[2::3]:
            self.assertAlmostEqual(z, 1.0, places=6)

    def test_smaller_size_gives_denser_mesh(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Fine_Box", "vol_1.brep", size=0.1),
                          self.vol(2, "Coarse_Box", "vol_2.brep", size=0.5)])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()

        def tets(group):
            ents = gmsh.model.getEntitiesForPhysicalGroup(3, group)
            return sum(len(gmsh.model.mesh.getElements(3, e)[1][0]) for e in ents)
        self.assertGreater(tets(1), 5 * tets(2))

    def mesh_box_with_size(self, file=None, size=0.05):
        """Mesh a unit box at size 0.5, plus one size item from geometry/<file> if given.
        Returns the node coordinates as (x, y, z) tuples."""
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        sizes = [{"name": "Fine", "size": size, "files": ["geometry/" + file]}] if file else []
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], sizes=sizes)
        self.assertEqual(r.returncode, 0, r.stderr)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(os.path.join(self.dir, "Model.msh"))
            c = gmsh.model.mesh.getNodes()[1]
        finally:
            gmsh.finalize()
        return [tuple(c[i:i + 3]) for i in range(0, len(c), 3)]

    def test_face_size_refines_only_that_face(self):
        write_rect(self.geo("size_1_1.brep"), 0, 0, 1, 1, 1)  # top face
        nodes = self.mesh_box_with_size("size_1_1.brep")
        top = sum(abs(z - 1) < 1e-9 for x, y, z in nodes)
        bottom = sum(abs(z) < 1e-9 for x, y, z in nodes)
        self.assertGreater(top, 20 * bottom)

    def test_edge_size_refines_that_edge(self):
        write_line(self.geo("size_1_1.brep"), (0, 0, 0), (1, 0, 0))  # box edge along x
        nodes = self.mesh_box_with_size("size_1_1.brep")
        on_edge = sum(abs(y) < 1e-9 and abs(z) < 1e-9 for x, y, z in nodes)
        opposite = sum(abs(y - 1) < 1e-9 and abs(z - 1) < 1e-9 for x, y, z in nodes)
        self.assertGreaterEqual(on_edge, 20)
        self.assertLess(opposite, 5)

    def test_vertex_size_refines_around_that_corner(self):
        def near_corner(nodes):
            return sum(0 < x * x + y * y + z * z < 0.3 ** 2 for x, y, z in nodes)
        before = near_corner(self.mesh_box_with_size())
        write_point(self.geo("size_1_1.brep"), (0, 0, 0))
        self.assertGreater(near_corner(self.mesh_box_with_size("size_1_1.brep")), before)

    def test_size_face_off_the_bodies_fails(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("size_1_1.brep"), 0, 0, 1.5, 1, 1)  # floats above the box
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")],
                         sizes=[{"name": "Fine", "size": 0.1, "files": ["geometry/size_1_1.brep"]}])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("Fine", last)

    def box_tets(self, options=None):
        """Mesh a unit box at size 0.5. Returns {element type: count} of the 3D elements."""
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], options=options)
        self.assertEqual(r.returncode, 0, r.stderr)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(os.path.join(self.dir, "Model.msh"))
            types, tags, _ = gmsh.model.mesh.getElements(3)
        finally:
            gmsh.finalize()
        return {int(t): len(x) for t, x in zip(types, tags)}

    def test_options_are_applied(self):
        plain = self.box_tets()
        finer = self.box_tets({"Mesh.Algorithm3D": 10, "Mesh.MeshSizeFactor": 0.5,
                               "Mesh.OptimizeNetgen": 1})
        self.assertEqual(list(finer), [4], "only first-order tetrahedra")
        self.assertGreater(finer[4], 3 * plain[4])  # 100 -> about 400 tetrahedra

    def test_max_size_option_caps_the_body_size(self):
        plain = self.box_tets()
        capped = self.box_tets({"Mesh.MeshSizeMax": 0.2})
        self.assertGreater(capped[4], 4 * plain[4])

    def test_unknown_option_fails_cleanly(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], options={"Mesh.NoSuchOption": 1})
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("NoSuchOption", last)

    def test_msh_version_22(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], version=2.2)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.dir, "Model.msh"), encoding="ascii") as fh:
            self.assertEqual(fh.read().split()[:2], ["$MeshFormat", "2.2"])

    def test_overlapping_boxes_fail(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 0.5, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "A_Box", "vol_1.brep"),
                          self.vol(2, "B_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("overlap", last)

    def test_offset_face_fails_merge_check(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("surf_1001_1.brep"), 0, 0, 1.5, 1, 1)  # floats above the box
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")],
                         [{"id": 1001, "name": "Terminal_In_Box", "volume_id": 1,
                           "files": ["geometry/surf_1001_1.brep"]}])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("Terminal_In_Box", last)

    def test_missing_geometry_file_fails_cleanly(self):
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stderr.strip().splitlines()[-1].startswith("ERROR:"))

    def test_single_box_without_faces(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(gmsh.model.getPhysicalName(3, 1), "Copper_Box")

    def test_excitation_on_face_shared_by_two_bodies(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        gmsh.initialize()  # the x = 1 interface, as a face of box 1
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
            gmsh.model.occ.synchronize()
            face = next(t for _, t in gmsh.model.getBoundary([(3, 1)], oriented=False)
                        if abs(gmsh.model.occ.getCenterOfMass(2, t)[0] - 1) < 1e-9)
            gmsh.model.occ.remove([(3, 1)])
            gmsh.model.occ.synchronize()
            gmsh.model.occ.remove([(2, t) for _, t in gmsh.model.getEntities(2) if t != face],
                                  recursive=True)
            gmsh.model.occ.synchronize()
            gmsh.write(self.geo("surf_1001_1.brep"))
        finally:
            gmsh.finalize()
        r = self.run_job([self.vol(1, "Coil_A", "vol_1.brep"), self.vol(2, "Lead_B", "vol_2.brep")],
                         [{"id": 1001, "name": "Terminal_A", "volume_id": 1,
                           "files": ["geometry/surf_1001_1.brep"]}])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        _, coords = gmsh.model.mesh.getNodesForPhysicalGroup(2, 1001)
        self.assertTrue(len(coords) > 0)
        for x in coords[0::3]:
            self.assertAlmostEqual(x, 1.0, places=6)

    def test_folder_with_spaces_and_persian_letters(self):
        self.dir = os.path.join(self.tmp.name, "my model \u0645\u062f\u0644")
        os.makedirs(os.path.join(self.dir, "geometry"))
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "Model.msh")))


if __name__ == "__main__":
    unittest.main()
