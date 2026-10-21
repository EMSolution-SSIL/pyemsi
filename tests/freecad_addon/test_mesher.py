"""Mesher tests. Run from the repo root: pixi run pytest tests/freecad_addon/test_mesher.py"""

import json
import math
import os
import stat
import subprocess
import sys
import tempfile
import unittest

import gmsh

MESHER = os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution", "mesher.py")


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


def write_rings(path, *rings):
    """One BREP holding a solid ring sector about Z per (inner, outer, z0, height[, a0, a1]): a cylinder when inner
    is 0, from angle a0 to a1 (degrees, default the full turn)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        for inner, outer, z0, h, *angles in rings:
            a0, a1 = angles or (0.0, 360.0)
            sweep = math.radians(a1 - a0)
            vol = [(3, occ.addCylinder(0, 0, z0, 0, 0, h, outer, angle=sweep))]
            if inner:
                vol = occ.cut(vol, [(3, occ.addCylinder(0, 0, z0 - 1, 0, 0, h + 2, inner, angle=sweep))])[0]
            occ.rotate(vol, 0, 0, 0, 0, 0, 1, math.radians(a0))
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_revolved(path, p, q, a0, a1):
    """The face swept by the line p-q turning about Z from angle a0 to a1 (degrees): a cylinder piece for a vertical
    line, a disc or ring piece for a radial one. Built like FreeCAD's half faces, so a disc piece has a corner on Z."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        line = occ.addLine(occ.addPoint(*p), occ.addPoint(*q))
        out = occ.revolve([(1, line)], 0, 0, 0, 0, 0, 1, math.radians(a1 - a0))
        occ.rotate([dt for dt in out if dt[0] == 2], 0, 0, 0, 0, 0, 1, math.radians(a0))
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def read_nodes(path):
    """[(x, y, z)] of the nodes of a mesh file, rounded to 1e-9."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        c = gmsh.model.mesh.getNodes()[1]
    finally:
        gmsh.finalize()
    return [tuple(round(x, 9) + 0.0 for x in c[i : i + 3]) for i in range(0, len(c), 3)]


def box_lines(x=0.0):
    """The 12 edges of the unit box at x as point pairs."""
    pts = [(x + i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    return [(p, q) for a, p in enumerate(pts) for q in pts[a + 1 :] if sum(abs(u - v) for u, v in zip(p, q)) == 1]


class MesherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.mkdir(os.path.join(self.dir, "geometry"))

    def tearDown(self):
        self.tmp.cleanup()

    def geo(self, name):
        return os.path.join(self.dir, "geometry", name)

    def run_job(
        self,
        volumes,
        surfaces=(),
        version=4.1,
        sizes=(),
        options=None,
        mesh_file=None,
        transfinite=None,
        recombine=None,
        air=None,
        extra=None,
    ):
        job = {
            "model_name": "Model",
            "msh_version": version,
            "mesh_file": mesh_file or os.path.join(self.dir, "pre_geom.msh"),
            "volumes": list(volumes),
            "surfaces": list(surfaces),
            "sizes": list(sizes),
        }
        if options is not None:
            job["options"] = options
        if transfinite is not None:
            job["transfinite"] = transfinite
        if recombine is not None:
            job["recombine"] = recombine
        if air is not None:
            job["air"] = air
        job.update(extra or {})  # e.g. the slide keys
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        return subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")

    def edge_item(self, name, lines, n):
        files = []
        for k, (p, q) in enumerate(lines, 1):
            write_line(self.geo(f"{name}_{k}.brep"), p, q)
            files.append(f"geometry/{name}_{k}.brep")
        return {"name": name, "nodes": n + 1, "distribution": "Uniform", "coef": 1.0, "files": files}

    def element_counts(self, group, dim=3):
        out = {}
        for e in gmsh.model.getEntitiesForPhysicalGroup(dim, group):
            types, tags = gmsh.model.mesh.getElements(dim, e)[:2]
            for t, ts in zip(types, tags):
                name = gmsh.model.mesh.getElementProperties(t)[0]
                out[name] = out.get(name, 0) + len(ts)
        return out

    def structured_box(self, n=3):
        return {
            "bodies": [{"name": "Core", "mat_id": 1, "corner_files": []}],
            "edges": [self.edge_item("tedge_1", box_lines(), n)],
        }

    def structured_boxes(self, *names_ids_x):
        return {
            "bodies": [{"name": n, "mat_id": m, "corner_files": []} for n, m, _ in names_ids_x],
            "edges": [self.edge_item(f"tedge_{i}", box_lines(x), 3) for i, (_, _, x) in enumerate(names_ids_x, 1)],
        }

    def open_msh(self):
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(os.path.join(self.dir, "pre_geom.msh"))
        self.addCleanup(gmsh.finalize)

    def vol(self, id_, name, file, size=0.5):
        return {"mat_id": id_, "name": name, "file": "geometry/" + file, "size": size}

    def test_two_touching_boxes_get_ids_names_and_shared_nodes(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep"), self.vol(2, "Air_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        self.open_msh()
        groups = {t: gmsh.model.getPhysicalName(3, t) for _, t in gmsh.model.getPhysicalGroups(3)}
        self.assertEqual(groups, {1: "Copper_Box", 2: "Air_Box001"})
        nodes1 = set(gmsh.model.mesh.getNodesForPhysicalGroup(3, 1)[0])
        nodes2 = set(gmsh.model.mesh.getNodesForPhysicalGroup(3, 2)[0])
        self.assertTrue(nodes1 & nodes2, "no shared nodes on the common face")

    def test_excitation_face_becomes_surface_group(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("surf_1001_1.brep"), 0, 0, 1, 1, 1)  # top face
        r = self.run_job(
            [self.vol(1, "Copper_Box", "vol_1.brep")],
            [{"smat_id": 1001, "name": "Terminal_In_Box", "mat_id": 1, "files": ["geometry/surf_1001_1.brep"]}],
        )
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
        r = self.run_job(
            [self.vol(1, "Fine_Box", "vol_1.brep", size=0.1), self.vol(2, "Coarse_Box", "vol_2.brep", size=0.5)]
        )
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
            gmsh.open(os.path.join(self.dir, "pre_geom.msh"))
            c = gmsh.model.mesh.getNodes()[1]
        finally:
            gmsh.finalize()
        return [tuple(c[i : i + 3]) for i in range(0, len(c), 3)]

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
            return sum(0 < x * x + y * y + z * z < 0.3**2 for x, y, z in nodes)

        before = near_corner(self.mesh_box_with_size())
        write_point(self.geo("size_1_1.brep"), (0, 0, 0))
        self.assertGreater(near_corner(self.mesh_box_with_size("size_1_1.brep")), before)

    def test_size_face_off_the_bodies_fails(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("size_1_1.brep"), 0, 0, 1.5, 1, 1)  # floats above the box
        r = self.run_job(
            [self.vol(1, "Copper_Box", "vol_1.brep")],
            sizes=[{"name": "Fine", "size": 0.1, "files": ["geometry/size_1_1.brep"]}],
        )
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
            gmsh.open(os.path.join(self.dir, "pre_geom.msh"))
            types, tags, _ = gmsh.model.mesh.getElements(3)
        finally:
            gmsh.finalize()
        return {int(t): len(x) for t, x in zip(types, tags)}

    def test_options_are_applied(self):
        plain = self.box_tets()
        finer = self.box_tets({"Mesh.Algorithm3D": 10, "Mesh.MeshSizeFactor": 0.5, "Mesh.OptimizeNetgen": 1})
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
        with open(os.path.join(self.dir, "pre_geom.msh"), encoding="ascii") as fh:
            self.assertEqual(fh.read().split()[:2], ["$MeshFormat", "2.2"])

    def test_mesh_goes_to_mesh_file_and_unv_beside_the_job(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = os.path.join(self.dir, "run dir", "pre_geom.msh")
        os.mkdir(os.path.dirname(target))
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], mesh_file=target)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(target))
        self.assertTrue(os.path.isfile(os.path.join(self.dir, "mesh.unv")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "pre_geom.msh")))
        self.assertIn(f"Wrote {target}", r.stdout)

    def write_old_mesh(self):
        path = os.path.join(self.dir, "pre_geom.msh")
        with open(path, "w", encoding="ascii") as fh:
            fh.write("old")
        return path

    def read_text(self, path):
        with open(path, encoding="ascii") as fh:
            return fh.read()

    def test_existing_mesh_is_replaced(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = self.write_old_mesh()
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.read_text(target).startswith("$MeshFormat"))

    def test_failed_run_keeps_the_existing_mesh(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 0.5, 0, 0, 1, 1, 1)  # overlaps vol_1
        target = self.write_old_mesh()
        r = self.run_job([self.vol(1, "A_Box", "vol_1.brep"), self.vol(2, "B_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.read_text(target), "old")

    def test_read_only_mesh_fails_cleanly_and_stays(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = self.write_old_mesh()
        os.chmod(target, stat.S_IREAD)
        try:
            r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        finally:
            os.chmod(target, stat.S_IREAD | stat.S_IWRITE)  # let the temporary folder be deleted
        self.assertCannotReplace(r, target)

    def test_mesh_open_in_another_program_fails_cleanly_and_stays(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = self.write_old_mesh()
        with open(target, encoding="ascii"):  # a viewer holding pre_geom.msh open
            r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertCannotReplace(r, target)

    def assertCannotReplace(self, r, target):
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertEqual(last, f"ERROR: Could not replace {target}: it is read-only or open in another program.")
        self.assertEqual(self.read_text(target), "old")

    def test_overlapping_boxes_fail(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 0.5, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "A_Box", "vol_1.brep"), self.vol(2, "B_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("overlap", last)

    def test_offset_face_fails_merge_check(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("surf_1001_1.brep"), 0, 0, 1.5, 1, 1)  # floats above the box
        r = self.run_job(
            [self.vol(1, "Copper_Box", "vol_1.brep")],
            [{"smat_id": 1001, "name": "Terminal_In_Box", "mat_id": 1, "files": ["geometry/surf_1001_1.brep"]}],
        )
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
            face = next(
                t
                for _, t in gmsh.model.getBoundary([(3, 1)], oriented=False)
                if abs(gmsh.model.occ.getCenterOfMass(2, t)[0] - 1) < 1e-9
            )
            gmsh.model.occ.remove([(3, 1)])
            gmsh.model.occ.synchronize()
            gmsh.model.occ.remove([(2, t) for _, t in gmsh.model.getEntities(2) if t != face], recursive=True)
            gmsh.model.occ.synchronize()
            gmsh.write(self.geo("surf_1001_1.brep"))
        finally:
            gmsh.finalize()
        r = self.run_job(
            [self.vol(1, "Coil_A", "vol_1.brep"), self.vol(2, "Lead_B", "vol_2.brep")],
            [{"smat_id": 1001, "name": "Terminal_A", "mat_id": 1, "files": ["geometry/surf_1001_1.brep"]}],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        _, coords = gmsh.model.mesh.getNodesForPhysicalGroup(2, 1001)
        self.assertTrue(len(coords) > 0)
        for x in coords[0::3]:
            self.assertAlmostEqual(x, 1.0, places=6)

    def test_structured_box_with_recombine_has_only_hexahedra(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], transfinite=self.structured_box(), recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})

    def test_structured_box_without_recombine_has_six_tetrahedra_per_cell(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], transfinite=self.structured_box())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Tetrahedron 4": 162})

    def test_structured_box_next_to_unstructured_box_gets_pyramids(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep", size=0.3)],
            options={"Mesh.Algorithm3D": 1},
            transfinite=self.structured_box(),
            recombine=[1],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertIn("Pyramid 5", self.element_counts(2))

    def three_boxes(self):
        for i, x in enumerate((0, 1, 2), 1):
            write_box(self.geo(f"vol_{i}.brep"), x, 0, 0, 1, 1, 1)
        return [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep"), self.vol(3, "Coil", "vol_3.brep")]

    def test_faces_between_two_tet_bodies_stay_triangles_with_a_note(self):
        r = self.run_job(
            self.three_boxes(),
            options={"Mesh.Algorithm3D": 1},
            transfinite=self.structured_box(),
            recombine=[1, 2, 3],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: recombine: faces between Air and Coil stay triangles", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertIn("Pyramid 5", self.element_counts(2))
        self.assertIn("Pyramid 5", self.element_counts(3))  # Coil's outside faces are quads

    def test_only_the_structured_body_chosen_next_to_two_tet_bodies(self):
        r = self.run_job(self.three_boxes(), transfinite=self.structured_box(), recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("NOTE: recombine", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertEqual(set(self.element_counts(3)), {"Tetrahedron 4"})

    def test_unstructured_box_alone_gets_pyramids(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Air", "vol_1.brep", 0.3)], recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertIn("Pyramid 5", self.element_counts(1))

    def test_body_inside_a_tet_body_stays_tetrahedra_with_a_note(self):
        # Coil is the middle cube of a 3x3x3 block; six Air slabs touch each of its faces (bodies cannot overlap)
        slabs = [(0, 0, 0, 3, 3, 1), (0, 0, 2, 3, 3, 1), (0, 0, 1, 1, 3, 1), (2, 0, 1, 1, 3, 1)]
        slabs += [(1, 0, 1, 1, 1, 1), (1, 2, 1, 1, 1, 1)]
        vols = []
        for i, box in enumerate(slabs, 1):
            write_box(self.geo(f"vol_{i}.brep"), *box)
            vols.append(self.vol(i, f"Air{i}", f"vol_{i}.brep"))
        write_box(self.geo("vol_7.brep"), 1, 1, 1, 1, 1, 1)
        vols.append(self.vol(7, "Coil", "vol_7.brep", 0.3))
        r = self.run_job(vols, recombine=[7])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: recombine: Coil has no face that can be recombined", r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(7)), {"Tetrahedron 4"})

    def test_structured_body_not_chosen_next_to_a_chosen_structured_body_is_an_error(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        tf = self.structured_boxes(("Core", 1, 0), ("Yoke", 2, 1))
        vols = [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Yoke", "vol_2.brep")]
        r = self.run_job(vols, transfinite=tf, recombine=[1])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR: recombine: Yoke is structured"), last)
        self.assertIn("Core", last)

    def test_quads_next_to_tets_need_delaunay(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep")],
            options={"Mesh.Algorithm3D": 10},
            transfinite=self.structured_box(),
            recombine=[1],
        )
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("Delaunay", last)
        self.assertIn("Core", last)
        self.assertIn("Air", last)

    def full_quad_core_and_air(self, n):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        return self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep", size=0.3)],
            options={"Mesh.RecombinationAlgorithm": 3},
            transfinite=self.structured_box(n),
            recombine=[1, 2],
        )

    def test_full_quad_with_an_odd_transfinite_count_next_to_a_recombined_body_is_an_error(self):
        r = self.full_quad_core_and_air(3)
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR: recombine: full-quad"), last)
        self.assertIn("Air", last)
        self.assertIn("tedge_1", last)

    def test_full_quad_with_an_even_transfinite_count_meshes(self):
        r = self.full_quad_core_and_air(4)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 64})

    def test_structured_and_two_unstructured_bodies_all_chosen(self):
        r = self.run_job(
            self.three_boxes(),
            options={"Mesh.Algorithm3D": 1},
            transfinite=self.structured_box(),
            recombine=[1, 2],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: recombine: faces between Air and Coil stay triangles", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertEqual(set(self.element_counts(3)), {"Tetrahedron 4"})

    def test_structured_box_alone_meshes_with_hxt(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep")],
            options={"Mesh.Algorithm3D": 10},
            transfinite=self.structured_box(),
            recombine=[1],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})

    def test_structured_box_edge_without_item_is_an_error(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        tf = self.structured_box()
        tf["edges"] = [self.edge_item("tedge_1", box_lines()[:11], 3)]
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], transfinite=tf)
        self.assertEqual(r.returncode, 1)
        self.assertIn("without Transfinite Edges", r.stderr.strip().splitlines()[-1])

    def test_structured_volume_with_seven_faces_is_an_error(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0.25, 0.25, 1, 0.5, 0.5)  # touches the middle of Core's x = 1 face
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep")], transfinite=self.structured_box()
        )
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR:"), last)
        self.assertIn("7 faces, needs 5 or 6", last)

    def test_folder_with_spaces_and_persian_letters(self):
        self.dir = os.path.join(self.tmp.name, "my model \u0645\u062f\u0644")
        os.makedirs(os.path.join(self.dir, "geometry"))
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "pre_geom.msh")))

    def test_air_fills_around_box(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("air.brep"), -1, -1, -1, 3, 3, 3)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.8}
        r = self.run_job([self.vol(1, "Body", "vol_1.brep", size=0.8)], air=air)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("MAT_ID       2  Air", r.stdout)
        self.open_msh()
        groups = {t: gmsh.model.getPhysicalName(3, t) for _, t in gmsh.model.getPhysicalGroups(3)}
        self.assertEqual(groups, {1: "Body", 2: "Air"})
        volume = 0.0
        for e in gmsh.model.getEntitiesForPhysicalGroup(3, 2):
            volume += sum(gmsh.model.mesh.getElementQualities(gmsh.model.mesh.getElements(3, e)[1][0], "volume"))
        self.assertAlmostEqual(volume, 27 - 1, delta=1e-6)

    def test_air_covered_by_bodies_fails_cleanly(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("air.brep"), 0, 0, 0, 1, 1, 1)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.8}
        r = self.run_job([self.vol(1, "Body", "vol_1.brep")], air=air)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stderr.strip().splitlines()[-1], "ERROR: the air region is fully covered by bodies")

    def test_recombined_body_inside_air_meshes(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("air.brep"), -1, -1, -1, 3, 3, 3)
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.8}
        r = self.run_job([self.vol(1, "Body", "vol_1.brep", size=0.8)], recombine=[1], air=air)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("faces between Air and Body stay triangles", r.stderr)

    def test_face_size_on_the_air_merges(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("air.brep"), -1, -1, -1, 3, 3, 3)
        write_rect(self.geo("size_1.brep"), -1, -1, -1, 3, 3)  # the air's bottom face
        air = {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 0.8}
        sizes = [{"name": "Fine", "size": 0.4, "files": ["geometry/size_1.brep"]}]
        r = self.run_job([self.vol(1, "Body", "vol_1.brep", size=0.8)], sizes=sizes, air=air)
        self.assertEqual(r.returncode, 0, r.stderr)

    # ---- sliding motion: the fixed side goes to pre_geom.msh, the moving side to rotor_mesh.msh

    def files(self):
        return os.path.join(self.dir, "pre_geom.msh"), os.path.join(self.dir, "rotor_mesh.msh")

    def slide(self, kind, files, n, cross, full=False, id_=20):
        """A slide entry named Slide; its marker is geometry/marker_<id_>.brep."""
        return {
            "name": "Slide",
            "kind": kind,
            "files": ["geometry/" + f for f in files],
            "marker": f"geometry/marker_{id_}.brep",
            "divisions": n,
            "cross_divisions": cross,
            "slide_mat_id": id_,
            "full": full,
        }

    def slide_job(self, volumes, moving, slides, periodic=None, surfaces=()):
        """Run a slide job: air from geometry/air.brep (fixed ID 10, moving 11), moving cell geometry/cell_1.brep."""
        sides = {"fixed": {"mat_id": 10, "name": "Air_fixed"}, "moving": {"mat_id": 11, "name": "Air_moving"}}
        air = {"sides": sides, "file": "geometry/air.brep", "size": 15.0}
        extra = {
            "rotor_file": self.files()[1],
            "moving": moving,
            "moving_cells": ["geometry/cell_1.brep"],
            "slides": slides,
        }
        if periodic:
            extra["periodic"] = periodic
        return self.run_job(volumes, surfaces, air=air, extra=extra)

    def motor_job(self, tooth=None, surfaces=(), rotor=40, start=0):
        """Case 17: stator ring 45..80 fixed, rotor (radius rotor) moving, both z 0..50, air cylinder r 100 from z -25
        to 75, slide cylinder r 42.5 in two halves from angle start, 72 divisions round and 10 up, slide edge at start.
        tooth: (z0, height, a0, a1) of a stator tooth 42.5..45 that touches the slide cylinder."""
        write_rings(self.geo("vol_1.brep"), (45, 80, 0, 50), *([(42.5, 45, *tooth)] if tooth else []))
        write_rings(self.geo("vol_2.brep"), (0, rotor, 0, 50))
        write_rings(self.geo("air.brep"), (0, 100, -25, 100))
        write_rings(self.geo("cell_1.brep"), (0, 42.5, -25, 100))
        for k, a in enumerate((start, start + 180), 1):
            write_revolved(self.geo(f"slide_20_{k}.brep"), (42.5, 0, -25), (42.5, 0, 75), a, a + 180)
        x, y = 42.5 * math.cos(math.radians(start)), 42.5 * math.sin(math.radians(start))
        write_line(self.geo("marker_20.brep"), (x, y, -25), (x, y, 75))
        vols = [self.vol(1, "Stator", "vol_1.brep", 10), self.vol(2, "Rotor", "vol_2.brep", 10)]
        slide = self.slide("rotational", ["slide_20_1.brep", "slide_20_2.brep"], 72, 10, True)
        return self.slide_job(vols, [2], [slide], surfaces=surfaces)

    def test_radial_slide_cylinder_matches(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (
            sorted(p for p in read_nodes(f) if abs(math.hypot(p[0], p[1]) - 42.5) < 1e-6) for f in self.files()
        )
        self.assertEqual(len(fixed), 72 * 11)
        self.assertEqual(fixed, moving)
        self.assertEqual(sorted({p[2] for p in fixed}), list(range(-25, 76, 10)))
        angles = sorted({round(math.degrees(math.atan2(p[1], p[0])), 6) % 360 for p in fixed})
        self.assertEqual(len(angles), 72)
        for got, want in zip(angles, range(0, 360, 5)):
            self.assertAlmostEqual(got, want, places=6)
        self.assertIn("MAT_ID      10  Air_fixed", r.stdout)
        self.assertIn("MAT_ID      11  Air_moving", r.stdout)
        self.assertIn("SLIDE_NDIV 72", r.stdout)
        self.assertIn(f"Wrote {self.files()[1]}", r.stdout)
        for path in self.files():  # each file numbers its nodes from 1
            tags = self.node_tags(path)
            self.assertEqual(tags, list(range(1, len(tags) + 1)), path)

    def node_tags(self, path):
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(path)
            return sorted(int(t) for t in gmsh.model.mesh.getNodes()[0])
        finally:
            gmsh.finalize()

    def cylinder_nodes(self, r=42.5):
        """The nodes on the slide cylinder in each file."""
        return [sorted(p for p in read_nodes(f) if abs(math.hypot(p[0], p[1]) - r) < 1e-6) for f in self.files()]

    def test_rotor_on_the_slide_cylinder_matches(self):
        """The rotor's outer face is part of the slide cylinder: its end circles cut each half into three bands."""
        r = self.motor_job(rotor=42.5)
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = self.cylinder_nodes()
        self.assertEqual(len(fixed), 72 * 11)
        self.assertEqual(fixed, moving)
        self.assertEqual(len({p[2] for p in fixed}), 11)
        self.assertEqual(len({round(math.degrees(math.atan2(p[1], p[0])), 6) % 360 for p in fixed}), 72)

    def test_excitation_surface_goes_to_the_file_of_its_body(self):
        write_revolved(self.geo("surf_1001_1.brep"), (45, 0, 50), (80, 0, 50), 0, 360)  # the stator's top face
        surface = {"smat_id": 1001, "name": "Terminal", "mat_id": 1, "files": ["geometry/surf_1001_1.brep"]}
        r = self.motor_job(surfaces=[surface])
        self.assertEqual(r.returncode, 0, r.stderr)
        found = []
        for path in self.files():
            gmsh.initialize()
            try:
                gmsh.option.setNumber("General.Terminal", 0)
                gmsh.open(path)
                found.append(gmsh.model.getPhysicalGroups(2))
                if found[-1]:
                    z = gmsh.model.mesh.getNodesForPhysicalGroup(2, 1001)[1][2::3]
                    self.assertTrue(len(z) and all(abs(v - 50) < 1e-9 for v in z))
            finally:
                gmsh.finalize()
        self.assertEqual(found, [[(2, 1001)], []])

    def test_tooth_on_the_slide_cylinder_keeps_the_grid(self):
        """A tooth face from 10° to 20° over the whole height splits a half along the motion, on the 5° grid."""
        r = self.motor_job(tooth=(-25, 100, 10, 20))
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = self.cylinder_nodes()
        self.assertEqual(len(fixed), 72 * 11)
        self.assertEqual(fixed, moving)
        angles = sorted({round(math.degrees(math.atan2(p[1], p[0])), 6) % 360 for p in fixed})
        for got, want in zip(angles, range(0, 360, 5)):
            self.assertAlmostEqual(got, want, places=6)

    def test_tooth_on_part_of_the_slide_cylinder_fails_cleanly(self):
        """A tooth face from 10° to 20° and z 0..50 is a hole in the half cylinder face: it cannot be structured."""
        r = self.motor_job(tooth=(0, 50, 10, 20))
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(
            last.startswith("ERROR: sliding interface Slide: slide_20_1.brep: a body lies on only part"), last
        )
        self.assertIn("must reach from edge to edge", last)

    def test_tooth_between_two_divisions_fails_cleanly(self):
        last = self.last_error(self.motor_job(tooth=(-25, 100, 12, 20)))
        self.assertIn("sliding interface Slide: slide_20_1.brep: the point at (41.571", last)
        self.assertIn("at 12° lies between two divisions along the motion", last)
        self.assertIn("(every 5°)", last)

    def test_rotor_seam_between_two_divisions_fails_cleanly(self):
        """The slide starts at 3°: the seam of the rotor's cylinder face at 0° cuts the slide cylinder off the grid."""
        last = self.last_error(self.motor_job(rotor=42.5, start=3))
        self.assertIn("at 0° lies between two divisions along the motion", last)
        self.assertIn("it may be a body edge or the seam of a round body face", last)
        self.assertIn("(every 5°), or change Divisions or the start angle", last)

    def test_rotor_on_the_slide_cylinder_with_its_seam_on_the_grid_matches(self):
        r = self.motor_job(rotor=42.5, start=-30)  # the seam at 0° lies on the 5° grid from -30°
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = self.cylinder_nodes()
        self.assertEqual(len(fixed), 72 * 11)
        self.assertEqual(fixed, moving)

    def last_error(self, r):
        self.assertEqual(r.returncode, 1, r.stderr)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR:"), last)
        return last

    def line_group(self, path, group):
        """(element count, node coordinates) of the dim-1 physical group in a mesh file; None if it has none."""
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(path)
            if (1, group) not in gmsh.model.getPhysicalGroups(1):
                return None
            count = 0
            for e in gmsh.model.getEntitiesForPhysicalGroup(1, group):
                count += sum(len(t) for t in gmsh.model.mesh.getElements(1, e)[1])
            c = gmsh.model.mesh.getNodesForPhysicalGroup(1, group)[1]
            return count, [tuple(round(x, 9) + 0.0 for x in c[i : i + 3]) for i in range(0, len(c), 3)]
        finally:
            gmsh.finalize()

    def test_rotor_file_has_slide_edge_at_start_angle(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, rotor = self.files()
        count, nodes = self.line_group(rotor, 20)
        self.assertEqual(count, 10)
        self.assertEqual(sorted(nodes), [(42.5, 0, z) for z in range(-25, 76, 10)])
        self.assertIsNone(self.line_group(fixed, 20))

    def slide_triangles(self, path, r):
        """The faces of the tetrahedra in path that lie on the cylinder of radius r, each as a frozenset of
        (5° step, z) of its nodes."""
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(path)
            tags, coords = gmsh.model.mesh.getNodes()[:2]
            where = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
            _, nodes = gmsh.model.mesh.getElementsByType(4)
        finally:
            gmsh.finalize()
        on = {t: (round(math.degrees(math.atan2(y, x)) / 5) % 72, round(z, 6)) for t, (x, y, z) in where.items()}
        on = {t: key for t, key in on.items() if abs(math.hypot(*where[t][:2]) - r) < 1e-6}
        found = set()
        for k in range(0, len(nodes), 4):
            tet = [int(n) for n in nodes[k : k + 4]]
            for skip in range(4):
                tri = [n for i, n in enumerate(tet) if i != skip]
                if all(n in on for n in tri):
                    found.add(frozenset(on[n] for n in tri))
        return found

    def test_slide_triangles_same_after_one_division(self):
        r = self.motor_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        tris = self.slide_triangles(self.files()[1], 42.5)
        self.assertEqual(len(tris), 72 * 10 * 2)
        turned = {frozenset(((k + 1) % 72, z) for k, z in tri) for tri in tris}
        self.assertEqual(turned, tris)

    def axial_job(self, rotor_z=0):
        """Case 19: rotor disc r 50 from z rotor_z, 10 high, moving; stator disc z 12..22 fixed; slide disc z 11 over
        the whole air r 80, 36 divisions round and 8 out."""
        write_rings(self.geo("vol_1.brep"), (0, 50, 12, 10))
        write_rings(self.geo("vol_2.brep"), (0, 50, rotor_z, 10))
        write_rings(self.geo("air.brep"), (0, 80, -10, 42))
        write_rings(self.geo("cell_1.brep"), (0, 80, -10, 21))
        for k, a in enumerate((0, 180), 1):
            write_revolved(self.geo(f"slide_20_{k}.brep"), (0, 0, 11), (80, 0, 11), a, a + 180)
        write_line(self.geo("marker_20.brep"), (0, 0, 11), (80, 0, 11))
        vols = [self.vol(1, "Stator", "vol_1.brep", 10), self.vol(2, "Rotor", "vol_2.brep", 10)]
        slide = self.slide("axial", ["slide_20_1.brep", "slide_20_2.brep"], 36, 8, True)
        return self.slide_job(vols, [2], [slide])

    def test_axial_gap_disc_reaching_axis(self):
        r = self.axial_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (sorted(p for p in read_nodes(f) if abs(p[2] - 11) < 1e-9) for f in self.files())
        self.assertEqual(len(fixed), 36 * 8 + 1)
        self.assertEqual(fixed, moving)
        count, nodes = self.line_group(self.files()[1], 20)
        self.assertEqual(count, 8)
        self.assertEqual(sorted(nodes), [(x, 0, 11) for x in range(0, 81, 10)])

    def test_rotor_disc_on_the_axial_gap_plane_matches(self):
        """The rotor's top face lies on the slide disc: each half is a half disc r < 50 and a half ring around it."""
        r = self.axial_job(rotor_z=1)
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (sorted(p for p in read_nodes(f) if abs(p[2] - 11) < 1e-9) for f in self.files())
        self.assertEqual(len(fixed), 36 * 8 + 1)
        self.assertEqual(fixed, moving)

    def linear_job(self, mover=(0, 0, 24, 80, 40, 16)):
        """Case 20: stator box below z 20 fixed, mover box (x, y, z, dx, dy, dz) moving, slide plane z 22 moving along
        x with 32 divisions and 8 across, the period is the 80 mm air box length."""
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 80, 40, 20)
        write_box(self.geo("vol_2.brep"), *mover)
        write_box(self.geo("air.brep"), 0, 0, -5, 80, 40, 50)
        write_box(self.geo("cell_1.brep"), 0, 0, 22, 80, 40, 23)
        write_rect(self.geo("slide_20_1.brep"), 0, 0, 22, 80, 40)
        write_line(self.geo("marker_20.brep"), (0, 0, 22), (0, 40, 22))
        vols = [self.vol(1, "Stator", "vol_1.brep", 10), self.vol(2, "Mover", "vol_2.brep", 10)]
        period = {"kind": "translation", "vector": [80.0, 0.0, 0.0], "start": 0.0}
        return self.slide_job(vols, [2], [self.slide("linear", ["slide_20_1.brep"], 32, 8)], period)

    def test_mover_on_the_linear_plane_matches(self):
        """The mover's bottom face (y 10..30) lies on the slide plane: it cuts it into three bands across the motion."""
        r = self.linear_job(mover=(0, 10, 22, 80, 20, 18))
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, moving = (sorted(p for p in read_nodes(f) if abs(p[2] - 22) < 1e-9) for f in self.files())
        self.assertEqual(len(fixed), 33 * 9)
        self.assertEqual(fixed, moving)
        self.assertEqual(sorted({p[1] for p in fixed}), list(range(0, 41, 5)))

    def test_linear_3d_plane_and_period(self):
        r = self.linear_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        planes = []
        for path in self.files():
            pts = read_nodes(path)
            planes.append(sorted(p for p in pts if abs(p[2] - 22) < 1e-9))
            self.assertEqual(len(planes[-1]), 33 * 9, path)
            left = sorted(p[1:] for p in pts if abs(p[0]) < 1e-9)
            right = sorted(p[1:] for p in pts if abs(p[0] - 80) < 1e-9)
            self.assertGreater(len(left), 9)
            self.assertEqual(left, right, path)
        self.assertEqual(planes[0], planes[1])
        self.assertEqual(self.line_group(self.files()[1], 20)[0], 8)
        self.assertIn("DXYZ 0.08 0 0", r.stdout)


if __name__ == "__main__":
    unittest.main()
