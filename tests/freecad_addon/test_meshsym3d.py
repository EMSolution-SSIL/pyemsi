"""Symmetric mesh tests in 3D: mesher.py meshes the cell solids, copies them and labels each copy by the piece solid it
lands on. Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_meshsym3d.py"""

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
from .meshreport import groups


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

    def cell(self, mat_id, name, sector, size=2.5):
        """A cell body: one solid sector (inner, outer, a0, a1, z0, z1)."""
        write_sector_solids(self.geo(f"vol_{mat_id}.brep"), sector)
        return {"mat_id": mat_id, "name": name, "file": f"geometry/vol_{mat_id}.brep", "size": size}

    def piece(self, mat_id, name, *sectors):
        self.count += 1
        rel = f"geometry/piece_{self.count}.brep"
        write_sector_solids(os.path.join(self.dir, rel), *sectors)
        return {"mat_id": mat_id, "name": name, "file": rel}

    def run_job(self, volumes, sides, extra=None, check=False, patch=""):
        """Run mesher.py on the job (--check when check); patch: Python run on meshsym first, e.g. to break it."""
        job = {
            "model_name": "Model",
            "mesh_file": self.files()[0],
            "volumes": volumes,
            "surfaces": [],
            "sizes": [],
            "symmetric": {"sides": sides},
        }
        job.update(extra or {})
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        cmd = [sys.executable, MESHER, path] + (["--check"] if check else [])
        if patch:
            code = (
                f"import runpy, sys; sys.path.insert(0, {os.path.dirname(MESHER)!r}); import meshsym; {patch}; "
                f"sys.argv = {cmd[1:]!r}; runpy.run_path({MESHER!r}, run_name='__main__')"
            )
            cmd = [sys.executable, "-c", code]
        return subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")

    def ring_job(self, outer_ids=(2,) * 8, outer_cuts=None, extra=None, **kw):
        """Cell: solids r 10..20 (id 1) and 20..30 (id 2), 0..45°, z 0..10; 4 rotations × {identity, mirror at 45°}.
        Pieces: 8 inner sectors (MAT_ID 1) and 8 outer ones with outer_ids, cut at the angles outer_cuts."""
        volumes = [self.cell(1, "InnerCell", (10, 20, 0, 45, 0, 10)), self.cell(2, "OuterCell", (20, 30, 0, 45, 0, 10))]
        pieces = [self.piece(1, "Inner", (10, 20, 45 * k, 45 * (k + 1), 0, 10)) for k in range(8)]
        cuts = list(outer_cuts or range(0, 361, 45))
        for k, id_ in enumerate(outer_ids):
            pieces.append(self.piece(id_, f"Outer{id_}", (20, 30, cuts[k], cuts[k + 1], 0, 10)))
        side = {"side": "fixed", "cells": [1, 2], "transforms": chain(45, 90, 4), "pieces": pieces}
        return self.run_job(volumes, [side], extra=extra, **kw)

    def test_copies_cover_the_ring_without_gaps(self):
        r = self.ring_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        kinds, inverted, loose = mesh_check_3d(self.files()[0], (10, 30), (0, 10))
        self.assertEqual((inverted, loose), (0, 0))
        self.assertEqual(sorted(groups(self.files()[0])), [1, 2])
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        self.assertIn("Inner", r.stdout)

    def test_each_copy_takes_its_piece_mat_id(self):  # outer pieces alternate MAT_ID 2 and 3
        r = self.ring_job(outer_ids=(2, 3) * 4)
        self.assertEqual(r.returncode, 0, r.stderr)
        found = groups(self.files()[0])
        self.assertEqual(set(found), {1, 2, 3})
        self.assertEqual(found[2][1], found[3][1])

    def test_asymmetric_drawing_is_refused(self):  # one outer piece cut at 44° instead of 45°
        r = self.ring_job(outer_cuts=[0, 44, 90, 135, 180, 225, 270, 315, 360])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not symmetric", r.stderr)
        self.assertIn("mm³", r.stderr)

    def rotation_job(self, **kw):
        """Cell A r 10..20, 0..45° with a fine size, cell B 45..90° coarse, z 0..10; 4 rotations of 90°, no mirror:
        the 0° face of A meets the 90° face of B of the next copy."""
        volumes = [self.cell(1, "A", (10, 20, 0, 45, 0, 10), size=1.5), self.cell(2, "B", (10, 20, 45, 90, 0, 10))]
        pieces = [self.piece(1, "PA", (10, 20, 90 * k, 90 * k + 45, 0, 10)) for k in range(4)]
        pieces += [self.piece(2, "PB", (10, 20, 90 * k + 45, 90 * k + 90, 0, 10)) for k in range(4)]
        side = {"side": "fixed", "cells": [1, 2], "transforms": [rotation(90 * k) for k in range(4)], "pieces": pieces}
        return self.run_job(volumes, [side], **kw)

    def test_pure_rotation_seams_conform(self):
        r = self.rotation_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        _, inverted, loose = mesh_check_3d(self.files()[0], (10, 20), (0, 10))
        self.assertEqual((inverted, loose), (0, 0))

    def test_seams_that_do_not_match_are_refused(self):
        r = self.rotation_job(patch="meshsym._periodic = lambda *a, **k: None")
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
        r = self.ring_job(outer_cuts=[0, 44, 90, 135, 180, 225, 270, 315, 360], check=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not symmetric", r.stderr)
        r = self.ring_job(check=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("CHECK OK", r.stdout)
        self.assertFalse(os.path.exists(self.files()[0]))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "mesh.unv")))


if __name__ == "__main__":
    unittest.main()
