"""Group jobs in 3D on the cases of the older symmetric mesher: seams, excitations on copies, the sliding cylinder.
The helpers here (write_sector_solids, write_face, surface_group, slide_nodes, mesh_check_3d) serve the other symmetric
tests too. Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_meshsym3d.py"""

import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter

import gmsh

from .test_mesher import MESHER, write_arc, write_line
from .test_mesher2d import add_sector
from .test_meshsym import chain, rotation
from .meshreport import groups, _marker


def write_sector_solids(path, *sectors):
    """One BREP holding a solid per (inner, outer, a0, a1, z0, z1): the add_sector face extruded from z0 to z1."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        for inner, outer, a0, a1, z0, z1 in sectors:
            face = add_sector(inner, outer, a0, a1)
            occ.translate(face, 0, 0, z0)
            occ.extrude(face, 0, 0, z1 - z0)
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_face(path, sector=None, corners=None, z=0, wall=None):
    """One BREP holding one face: the add_sector face of sector (inner, outer, a0, a1) at height z, the planar
    polygon of corners [(x, y, z)], or the cylinder face of wall (radius, a0, a1, z0, z1)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        if wall:
            r, a0, a1, z0, z1 = wall
            arc = occ.addCircle(0, 0, z0, r, angle1=math.radians(a0), angle2=math.radians(a1))
            occ.extrude([(1, arc)], 0, 0, z1 - z0)
        elif sector:
            occ.translate(add_sector(*sector), 0, 0, z)
        else:
            pts = [occ.addPoint(*p) for p in corners]
            lines = [occ.addLine(pts[k], pts[(k + 1) % len(pts)]) for k in range(len(pts))]
            occ.addPlaneSurface([occ.addCurveLoop(lines)])
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def surface_group(path, id_):
    """(name, element count, area) of the 2D physical group id_ of a mesh file; None when there is none."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        if (2, id_) not in gmsh.model.getPhysicalGroups(2):
            return None
        tags, coords, _ = gmsh.model.mesh.getNodes()
        xyz = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
        count, area = 0, 0.0
        for e in gmsh.model.getEntitiesForPhysicalGroup(2, id_):
            for typ, etags, enodes in zip(*gmsh.model.mesh.getElements(2, e)):
                per = len(enodes) // len(etags)
                corners = gmsh.model.mesh.getElementProperties(typ)[5]  # primary nodes: 3 or 4
                count += len(etags)
                for k in range(len(etags)):
                    a, *rest = (xyz[int(n)] for n in enodes[k * per : k * per + corners])
                    for b, c in zip(rest, rest[1:]):  # fan of triangles from the first corner
                        u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
                        w = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
                        area += math.hypot(*w) / 2
        return gmsh.model.getPhysicalName(2, id_), count, area
    finally:
        gmsh.finalize()


def slide_nodes(msh, r):
    """The rounded coordinates of the nodes of a mesh file on the cylinder of radius r about Z."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh)
        c = gmsh.model.mesh.getNodes()[1]
    finally:
        gmsh.finalize()
    pts = [c[k : k + 3] for k in range(0, len(c), 3)]
    return {tuple(round(x, 6) + 0.0 for x in p) for p in pts if abs(math.hypot(p[0], p[1]) - r) < 1e-6 * r}


CORNERS = {"Tetrahedron 4": (0, 1, 2, 3), "Hexahedron 8": (0, 1, 3, 4), "Prism 6": (0, 1, 2, 3)}
CORNERS["Pyramid 5"] = (0, 1, 3, 4)


def _volume(a, b, c, d):
    u, v, w = ([q[i] - a[i] for i in range(3)] for q in (b, c, d))
    return u[0] * (v[1] * w[2] - v[2] * w[1]) - u[1] * (v[0] * w[2] - v[2] * w[0]) + u[2] * (v[0] * w[1] - v[1] * w[0])


def mesh_check_3d(path, radii, heights):
    """(element type names, inverted elements, element faces used by one element that are not on a cylinder of radii
    about Z or a plane z in heights). Inverted: the corner tetrahedron of CORNERS has a signed volume <= 0."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        tags, coords, _ = gmsh.model.mesh.getNodes()
        xyz = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
        faces, inverted, kinds = Counter(), 0, set()
        for typ in gmsh.model.mesh.getElementTypes(3):
            name = gmsh.model.mesh.getElementProperties(typ)[0]
            kinds.add(name)
            etags, enodes = gmsh.model.mesh.getElementsByType(typ)
            per = len(enodes) // len(etags)
            for k in range(len(etags)):
                inverted += _volume(*(xyz[int(enodes[k * per + c])] for c in CORNERS[name])) <= 0
            for n in (3, 4):
                fn = gmsh.model.mesh.getElementFaceNodes(typ, n, -1, True)
                faces.update(tuple(sorted(int(v) for v in fn[k : k + n])) for k in range(0, len(fn), n))
    finally:
        gmsh.finalize()

    def outside(face):
        pts = [xyz[n] for n in face]
        on_cylinder = any(all(abs(math.hypot(p[0], p[1]) - r) < 1e-6 for p in pts) for r in radii)
        return on_cylinder or any(all(abs(p[2] - z) < 1e-6 for p in pts) for z in heights)

    loose = [f for f, k in faces.items() if k == 1 and not outside(f)]
    return kinds, inverted, len(loose)


class MeshSym3DTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.mkdir(os.path.join(self.dir, "geometry"))
        self.count = 0

    def tearDown(self):
        self.tmp.cleanup()

    def geo(self, name):
        return os.path.join(self.dir, "geometry", name)

    def files(self):
        return os.path.join(self.dir, "pre_geom.msh"), os.path.join(self.dir, "rotor_mesh.msh")

    def group(self, name, cells, transforms, parts, rows, side="fixed", extra=None, excitations=None):
        """A 3D group job: cells [(name, solids, size)] with local ids 1..n, a BREP each holding the sector solids
        (inner, outer, a0, a1, z0, z1); parts [(mat_id, name)]; rows: per cell the index into parts of each copy's
        part."""
        volumes = []
        for k, (cell, solids, size) in enumerate(cells, 1):
            self.count += 1
            rel = f"geometry/cell_{self.count}.brep"
            write_sector_solids(os.path.join(self.dir, rel), *solids)
            volumes.append({"mat_id": k, "name": cell, "file": rel, "size": size})
        group = {
            "name": name,
            "side": side,
            "job": {"volumes": volumes, "surfaces": [], "sizes": [], **(extra or {})},
            "cells": list(range(1, len(cells) + 1)),
            "transforms": transforms,
            "parts": [{"mat_id": i, "name": n} for i, n in parts],
            "rows": [{"cell": k, "file": None, "parts": picks} for k, picks in enumerate(rows, 1)],
        }
        if excitations:
            group["excitations"] = excitations
        return group

    def run_job(self, groups, check=False, patch="", slide=None):
        """Run mesher.py on the job (--check when check); patch: Python run on meshgroups first, e.g. to break it."""
        job = {"model_name": "Model", "mesh_file": self.files()[0], "options": {}, "symmetric": {"groups": groups}}
        if slide:
            job["symmetric"]["slide"] = slide
            job["rotor_file"] = self.files()[1]
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        cmd = [sys.executable, MESHER, path] + (["--check"] if check else [])
        if patch:
            code = (
                f"import runpy, sys; sys.path.insert(0, {os.path.dirname(MESHER)!r}); import meshgroups; {patch}; "
                f"sys.argv = {cmd[1:]!r}; runpy.run_path({MESHER!r}, run_name='__main__')"
            )
            cmd = [sys.executable, "-c", code]
        return subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")

    def ring_job(self, outer=(1,) * 8, extra=None, excitations=None, **kw):
        """Cells: solids r 10..20 (Inner, MAT_ID 1) and 20..30 (MAT_ID 2 or 3), 0..45°, z 0..10; 4 rotations ×
        {identity, mirror at 45°}; outer: the part of each copy of the outer cell, 1 for Outer2 and 2 for Outer3."""
        cells = [("InnerCell", [(10, 20, 0, 45, 0, 10)], 2.5), ("OuterCell", [(20, 30, 0, 45, 0, 10)], 2.5)]
        parts = [(1, "Inner"), (2, "Outer2"), (3, "Outer3")]
        rows = [[0] * 8, list(outer)]
        group = self.group("Ring", cells, chain(45, 90, 4), parts, rows, extra=extra, excitations=excitations)
        return self.run_job([group], **kw)

    def test_copies_cover_the_ring_without_gaps(self):
        r = self.ring_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        kinds, inverted, loose = mesh_check_3d(self.files()[0], (10, 30), (0, 10))
        self.assertEqual((inverted, loose), (0, 0))
        self.assertEqual(sorted(groups(self.files()[0])), [1, 2])
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        self.assertIn("Inner", r.stdout)

    def test_each_copy_takes_its_part_mat_id(self):  # outer copies alternate MAT_ID 2 and 3
        r = self.ring_job(outer=(1, 2) * 4)
        self.assertEqual(r.returncode, 0, r.stderr)
        found = groups(self.files()[0])
        self.assertEqual(set(found), {1, 2, 3})
        self.assertEqual(found[2][1], found[3][1])

    def rotation_job(self, **kw):
        """Cell A r 10..20, 0..45° with a fine size, cell B 45..90° coarse, z 0..10; 4 rotations of 90°, no mirror:
        the 0° face of A meets the 90° face of B of the next copy."""
        cells = [("A", [(10, 20, 0, 45, 0, 10)], 1.5), ("B", [(10, 20, 45, 90, 0, 10)], 2.5)]
        transforms = [rotation(90 * k) for k in range(4)]
        group = self.group("Ring", cells, transforms, [(1, "PA"), (2, "PB")], [[0] * 4, [1] * 4])
        return self.run_job([group], **kw)

    def test_pure_rotation_seams_conform(self):
        r = self.rotation_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        _, inverted, loose = mesh_check_3d(self.files()[0], (10, 20), (0, 10))
        self.assertEqual((inverted, loose), (0, 0))

    def test_seams_that_do_not_match_are_refused(self):
        r = self.rotation_job(patch="meshgroups.meshsym._periodic = lambda *a, **k: None")
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertIn("do not match", r.stderr)
        self.assertFalse(os.path.exists(self.files()[0]))

    def test_structured_cell_stays_hexes(self):  # Transfinite Body + Recombine on cell id 2 (whole body)
        c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
        files = []
        for z in (0, 10):
            for k, (p, q) in enumerate((((20, 0, z), (30, 0, z)), ((20 * c, 20 * s, z), (30 * c, 30 * s, z))), 1):
                write_line(self.geo(f"tedge_r{k}_{z}.brep"), p, q)
                files.append(f"geometry/tedge_r{k}_{z}.brep")
            for r in (20, 30):
                write_arc(self.geo(f"tedge_a{r}_{z}.brep"), (r, 0, z), (r * c, r * s, z), (0, 0, z))
                files.append(f"geometry/tedge_a{r}_{z}.brep")
        for x, y in ((20, 0), (30, 0), (20 * c, 20 * s), (30 * c, 30 * s)):
            name = f"tedge_z{len(files)}.brep"
            write_line(self.geo(name), (x, y, 0), (x, y, 10))
            files.append(f"geometry/{name}")
        edge = {"name": "Edges", "nodes": 5, "distribution": "Uniform", "coef": 1.0, "files": files}
        tf = {"bodies": [{"name": "OuterCell", "mat_id": 2, "corner_files": []}], "edges": [edge]}
        r = self.ring_job(extra={"transfinite": tf, "recombine": [2]})
        self.assertEqual(r.returncode, 0, r.stderr)
        kinds, inverted, loose = mesh_check_3d(self.files()[0], (10, 30), (0, 10))
        self.assertIn("Hexahedron 8", kinds)
        self.assertEqual((inverted, loose), (0, 0))
        self.assertEqual(groups(self.files()[0])[2][1], 8 * 4**3)

    def test_check_runs_the_symmetric_checks_and_writes_nothing(self):
        r = self.rotation_job(check=True, patch="meshgroups.meshsym._periodic = lambda *a, **k: None")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("do not match", r.stderr)
        r = self.ring_job(check=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("CHECK OK", r.stdout)
        self.assertFalse(os.path.exists(self.files()[0]))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "mesh.unv")))

    def excitation(self, **face):
        """The excitation Exc (SMAT_ID 101) on the one face write_face(**face) draws."""
        write_face(self.geo("exc.brep"), **face)
        return [{"smat_id": 101, "name": "Exc", "files": ["geometry/exc.brep"]}]

    def test_excitation_on_an_outer_top_face_gets_its_smat_id(self):
        r = self.ring_job(excitations=self.excitation(sector=(20, 30, 0, 45), z=10))
        self.assertEqual(r.returncode, 0, r.stderr)
        name, count, area = surface_group(self.files()[0], 101)
        self.assertEqual(name, "Exc")
        self.assertGreater(count, 0)
        exact = math.pi * (30**2 - 20**2) / 8
        self.assertAlmostEqual(area / exact, 1, delta=1e-2)  # flat triangles along the arcs: a little less

    def test_excitation_face_shared_by_two_copies_counts_once(self):  # the radial face at 45°, between two copies
        c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
        corners = [(10 * c, 10 * s, 0), (20 * c, 20 * s, 0), (20 * c, 20 * s, 10), (10 * c, 10 * s, 10)]
        r = self.ring_job(excitations=self.excitation(corners=corners))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertAlmostEqual(surface_group(self.files()[0], 101)[2], 100, delta=1e-6)

    def test_excitation_face_not_split_by_the_cell_is_refused(self):  # ends at 30°, inside a copy
        r = self.ring_job(excitations=self.excitation(sector=(20, 30, 0, 30), z=10))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("excitation Exc", r.stderr)
        self.assertIn("cover", r.stderr)

    def test_excitation_on_a_curved_face_lands(self):  # the outer cylinder face r = 30, 0..45°, z 0..10
        r = self.ring_job(excitations=self.excitation(wall=(30, 0, 45, 0, 10)))
        self.assertEqual(r.returncode, 0, r.stderr)
        name, count, area = surface_group(self.files()[0], 101)
        self.assertEqual(name, "Exc")
        self.assertGreater(count, 0)
        self.assertAlmostEqual(area / (30 * math.pi / 4 * 10), 1, delta=1e-2)  # flat triangles: a little less

    def test_excitation_lines_are_reported(self):
        r = self.ring_job(excitations=self.excitation(sector=(20, 30, 0, 45), z=10))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("SMAT_ID    101  Exc", r.stdout)

    def slide_job(self, divisions=16, moving_z=10, fixed_cut=None):
        """Fixed cell r 20..30, moving cell r 10..20, both 0..45°, z 0..10 (the moving one to moving_z, the fixed one
        cut at z fixed_cut into two solids); chain(45, 90, 4) on both sides; sliding cylinder r 20, 4 cross divisions."""
        cut = (
            [(20, 30, 0, 45, 0, 10)]
            if fixed_cut is None
            else [(20, 30, 0, 45, 0, fixed_cut), (20, 30, 0, 45, fixed_cut, 10)]
        )
        fixed = self.group("Stator", [("StatorCell", cut, 2.5)], chain(45, 90, 4), [(5, "Stator")], [[0] * 8])
        rotor = [("RotorCell", [(10, 20, 0, 45, 0, moving_z)], 2.5)]
        moving = self.group("Rotor", rotor, chain(45, 90, 4), [(6, "Rotor")], [[0] * 8], side="moving")
        slide = {"name": "Slide", "kind": "rotational", "radius": 20.0, "divisions": divisions, "cross_divisions": 4}
        slide.update(slide_mat_id=7, full=True)
        return self.run_job([fixed, moving], slide=slide)

    def test_sliding_sides_have_the_same_nodes_on_the_cylinder(self):
        r = self.slide_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, rotor = self.files()
        self.assertEqual(slide_nodes(fixed, 20), slide_nodes(rotor, 20))
        self.assertEqual(len(slide_nodes(fixed, 20)), 16 * (4 + 1))
        self.assertEqual(sorted(groups(fixed)), [5])
        self.assertEqual(sorted(groups(rotor)), [6])
        self.assertEqual(mesh_check_3d(fixed, (20, 30), (0, 10))[1:], (0, 0))
        self.assertEqual(mesh_check_3d(rotor, (10, 20), (0, 10))[1:], (0, 0))
        self.assertIn("SLIDE_NDIV 16", r.stdout)

    def test_marker_line_is_on_the_moving_side_only(self):
        r = self.slide_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, rotor = self.files()
        count, nodes = _marker(rotor, 1, 7)
        self.assertEqual(count, 4)
        for p in nodes:
            self.assertAlmostEqual(p[0], 20, places=6)
            self.assertAlmostEqual(p[1], 0, places=6)
        self.assertEqual(sorted(round(p[2], 6) for p in nodes), [0, 2.5, 5, 7.5, 10])
        self.assertIsNone(_marker(fixed, 1))

    def test_divisions_off_the_grid_are_refused(self):  # divisions 12: a 45° cell arc gets 1.5
        r = self.slide_job(divisions=12)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("whole number", r.stderr)

    def test_side_short_of_the_cylinder_height_is_refused(self):  # moving cell z 0..8, fixed z 0..10
        r = self.slide_job(moving_z=8)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("moving side", r.stderr)
        self.assertIn("cylinder", r.stderr)

    def test_z_cut_off_the_cross_grid_is_refused(self):  # fixed cell split at z = 3 (2 solids), cross_divisions 4
        r = self.slide_job(fixed_cut=3)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("cross_divisions", r.stderr)


if __name__ == "__main__":
    unittest.main()
