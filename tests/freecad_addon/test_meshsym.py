"""Group jobs in 2D on the cases of the older symmetric mesher: seams between copies, sliding sides, structured cells.
The helpers here (rotation, mirror_line, chain, mesh_check) serve the other symmetric tests too.
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_meshsym.py"""

import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter

import gmsh

from .test_mesher import write_line
from .test_mesher2d import MESHER2D, write_arc, write_sectors
from .meshreport import _point, groups


def rotation(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def mirror_line(deg):
    """Mirror about the line through the origin at angle deg."""
    c, s = math.cos(math.radians(2 * deg)), math.sin(math.radians(2 * deg))
    return [c, s, 0, 0, s, -c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def compose(a, b):
    """b first, then a."""
    return [sum(a[4 * i + k] * b[4 * k + j] for k in range(4)) for i in range(4) for j in range(4)]


def chain(mirror, step, count):
    """identity and the mirror about the line at angle mirror, then each rotated by step × 0..count - 1."""
    first = [rotation(0), mirror_line(mirror)]
    return [compose(rotation(step * k), m) for k in range(count) for m in first]


def mesh_check(path, radii):
    """(element type names, inverted elements, edges used by one element that are not on a circle of radii).
    Inverted: corners clockwise in XY (minSJ cannot tell: on discrete entities it is 1 either way)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        tags, coords, _ = gmsh.model.mesh.getNodes()
        xyz = {int(t): coords[3 * k : 3 * k + 3] for k, t in enumerate(tags)}
        edges, inverted, kinds = Counter(), 0, set()
        for typ in gmsh.model.mesh.getElementTypes(2):
            etags, _ = gmsh.model.mesh.getElementsByType(typ)
            kinds.add(gmsh.model.mesh.getElementProperties(typ)[0])
            corners = gmsh.model.mesh.getElementProperties(typ)[5]
            enodes = gmsh.model.mesh.getElementsByType(typ)[1]
            per = len(enodes) // len(etags)
            for k in range(len(etags)):  # clockwise corners (signed shoelace area <= 0): an inverted element
                pts = [xyz[int(n)] for n in enodes[k * per : k * per + corners]]
                twice = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
                inverted += twice <= 0
            en = gmsh.model.mesh.getElementEdgeNodes(typ)
            edges.update(tuple(sorted(int(n) for n in en[k : k + 2])) for k in range(0, len(en), 2))
    finally:
        gmsh.finalize()

    def outside(n):
        return any(abs(math.hypot(*xyz[n][:2]) - r) < 1e-6 for r in radii)

    loose = [e for e, k in edges.items() if k == 1 and not all(outside(n) for n in e)]
    return kinds, inverted, len(loose)


class MeshSymTest(unittest.TestCase):
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
        return os.path.join(self.dir, "pre_geom2D.msh"), os.path.join(self.dir, "rotor_mesh2D.msh")

    def group(self, name, cells, transforms, parts, rows, side="fixed", extra=None):
        """A group job: cells [(name, sector, size)] with local ids 1..n, a BREP each (sector: inner, outer, a0, a1);
        parts [(mat_id, name)]; rows: per cell the index into parts of each copy's part."""
        bodies = []
        for k, (cell, sector, size) in enumerate(cells, 1):
            self.count += 1
            rel = f"geometry/cell_{self.count}.brep"
            write_sectors(os.path.join(self.dir, rel), sector)
            bodies.append({"mat_id": k, "name": cell, "file": rel, "size": size})
        job = {"bodies": bodies, "sizes": [], **(extra or {})}
        return {
            "name": name,
            "side": side,
            "job": job,
            "cells": list(range(1, len(cells) + 1)),
            "transforms": transforms,
            "parts": [{"mat_id": i, "name": n} for i, n in parts],
            "rows": [{"cell": k, "file": None, "parts": picks} for k, picks in enumerate(rows, 1)],
        }

    def run_job(self, groups, slide=None, check=False, patch=""):
        """Run the mesher on the job (--check when check); patch: Python run on meshgroups first, e.g. to break it."""
        job = {
            "dimension": "2D",
            "model_name": "Model",
            "mesh_file": self.files()[0],
            "options": {},
            "symmetric": {"groups": groups},
        }
        if slide:
            job["symmetric"]["slide"] = slide
            job["rotor_file"] = self.files()[1]
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        cmd = [sys.executable, MESHER2D, path] + (["--check"] if check else [])
        if patch:
            code = (
                f"import runpy, sys; sys.path.insert(0, {os.path.dirname(MESHER2D)!r}); import meshgroups; {patch}; "
                f"sys.argv = {cmd[1:]!r}; runpy.run_path({MESHER2D!r}, run_name='__main__')"
            )
            cmd = [sys.executable, "-c", code]
        return subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")

    def ring_job(self, outer=(1,) * 8, **kw):
        """Cells r 10..20 (Inner, MAT_ID 1) and 20..30 (MAT_ID 2 or 3), 0..45°; 4 rotations × {identity, mirror at
        45°}; outer: the part of each copy of the outer cell, 1 for Outer2 and 2 for Outer3."""
        cells = [("InnerCell", (10, 20, 0, 45), 2.0), ("OuterCell", (20, 30, 0, 45), 2.0)]
        parts = [(1, "Inner"), (2, "Outer2"), (3, "Outer3")]
        group = self.group("Ring", cells, chain(45, 90, 4), parts, [[0] * 8, list(outer)])
        return self.run_job([group], **kw)

    def test_copies_cover_the_ring_without_gaps(self):
        r = self.ring_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(groups(self.files()[0])), [1, 2])
        _, inverted, loose = mesh_check(self.files()[0], (10, 30))
        self.assertEqual(inverted, 0)
        self.assertEqual(loose, 0)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        self.assertIn("Inner", r.stdout)

    def test_each_copy_takes_its_part_mat_id(self):
        r = self.ring_job(outer=(1, 2) * 4)
        self.assertEqual(r.returncode, 0, r.stderr)
        found = groups(self.files()[0])
        self.assertEqual(sorted(found), [1, 2, 3])
        self.assertEqual(found[2][1], found[3][1])
        self.assertEqual(found[3][0], "Outer3")

    def slide_job(self, divisions=144, rotor=(10, 35, 0, 22.5)):
        """Fixed cell r 35..60, 0..15° (mirror 15°, rotate 30° × 12); moving cell rotor, r 10..35, 0..22.5° by default
        (16 copies); sliding circle r 35."""
        fixed = self.group(
            "Stator", [("StatorCell", (35, 60, 0, 15), 2.0)], chain(15, 30, 12), [(5, "Stator")], [[0] * 24]
        )
        moving = self.group(
            "Rotor", [("RotorCell", rotor, 2.0)], chain(22.5, 45, 8), [(6, "Rotor")], [[0] * 16], side="moving"
        )
        slide = {"name": "Slide", "kind": "rotational", "radius": 35.0, "divisions": divisions, "slide_mat_id": 7}
        slide["full"] = True
        return self.run_job([fixed, moving], slide)

    def test_sliding_sides_match(self):
        r = self.slide_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, rotor = self.files()
        angles = []
        for path in (fixed, rotor):
            gmsh.initialize()
            try:
                gmsh.option.setNumber("General.Terminal", 0)
                gmsh.open(path)
                c = gmsh.model.mesh.getNodes()[1]
            finally:
                gmsh.finalize()
            pts = [c[k : k + 3] for k in range(0, len(c), 3)]
            on = [p for p in pts if abs(math.hypot(p[0], p[1]) - 35) < 1e-6]
            angles.append(sorted(round(math.degrees(math.atan2(p[1], p[0])), 6) % 360 for p in on))
        self.assertEqual(len(angles[0]), 144)
        self.assertEqual(angles[0], angles[1])
        self.assertEqual([mesh_check(f, ())[1] for f in (fixed, rotor)], [0, 0])
        self.assertEqual(sorted(groups(fixed)), [5])
        self.assertEqual(sorted(groups(rotor)), [6])
        marker = _point(rotor, 7)
        self.assertAlmostEqual(marker[0], 35, places=6)
        self.assertAlmostEqual(marker[1], 0, places=6)
        self.assertIn("SLIDE_NDIV 144", r.stdout)

    def test_divisions_off_the_grid_are_refused(self):
        r = self.slide_job(100)
        self.assertEqual(r.returncode, 1)
        self.assertIn("sliding interface", r.stderr)

    def test_structured_cell_stays_quads(self):
        c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
        write_line(self.geo("tedge_1.brep"), (10, 0, 0), (20, 0, 0))
        write_line(self.geo("tedge_2.brep"), (10 * c, 10 * s, 0), (20 * c, 20 * s, 0))
        write_arc(self.geo("tedge_3.brep"), 10, 0, 45)
        write_arc(self.geo("tedge_4.brep"), 20, 0, 45)
        edges = [f"geometry/tedge_{k}.brep" for k in range(1, 5)]
        edge = {"name": "Edges", "nodes": 7, "distribution": "Uniform", "coef": 1.0, "files": edges}
        tf = {"bodies": [{"name": "Core", "mat_id": 1, "corner_files": []}], "edges": [edge]}
        extra = {"transfinite": tf, "recombine": [1]}
        group = self.group(
            "Core", [("Core", (10, 20, 0, 45), 2.0)], chain(45, 90, 4), [(4, "Iron")], [[0] * 8], extra=extra
        )
        r = self.run_job([group])
        self.assertEqual(r.returncode, 0, r.stderr)
        kinds, inverted, loose = mesh_check(self.files()[0], (10, 20))
        self.assertEqual(kinds, {"Quadrilateral 4"})
        self.assertEqual(inverted, 0)
        self.assertEqual(loose, 0)
        self.assertEqual(groups(self.files()[0]), {4: ("Iron", 8 * 36)})

    def rotation_job(self, **kw):
        """Cell A r 10..30, 0..22.5° with a fine size, cell B 22.5..45° coarse; 8 rotations of 45°, no mirror: the
        0° seam of A meets the 45° seam of B of the next copy."""
        cells = [("A", (10, 30, 0, 22.5), 0.5), ("B", (10, 30, 22.5, 45), 2.0)]
        group = self.group(
            "Ring", cells, [rotation(45 * k) for k in range(8)], [(1, "PA"), (2, "PB")], [[0] * 8, [1] * 8]
        )
        return self.run_job([group], **kw)

    def test_pure_rotation_seams_conform(self):
        r = self.rotation_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        _, inverted, loose = mesh_check(self.files()[0], (10, 30))
        self.assertEqual((inverted, loose), (0, 0))

    def test_seams_that_do_not_match_are_refused(self):
        r = self.rotation_job(patch="meshgroups.meshsym._periodic = lambda *a, **k: None")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("do not match", r.stderr)
        self.assertFalse(os.path.exists(self.files()[0]))

    def test_side_short_of_the_sliding_circle_is_refused(self):
        r = self.slide_job(rotor=(10, 34.5, 0, 22.5))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("moving side", r.stderr)

    def test_side_covering_part_of_the_sliding_circle_is_refused(self):
        """The rotor cell reaches the circle from 0 to 10° only: its copies leave gaps in the circle."""
        fixed = self.group("Stator", [("StatorCell", (35, 60, 0, 15), 2.0)], chain(15, 30, 12), [(5, "S")], [[0] * 24])
        write_sectors(self.geo("rotor.brep"), (10, 35, 0, 10), (10, 34, 10, 22.5))
        moving = self.group(
            "Rotor", [("RotorCell", (10, 35, 0, 22.5), 2.0)], chain(22.5, 45, 8), [(6, "R")], [[0] * 16]
        )
        moving["side"] = "moving"
        moving["job"]["bodies"][0]["file"] = "geometry/rotor.brep"
        slide = {"name": "Slide", "kind": "rotational", "radius": 35.0, "divisions": 144, "slide_mat_id": 7}
        r = self.run_job([fixed, moving], dict(slide, full=True))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("moving side", r.stderr)
        self.assertIn("on the circle", r.stderr)

    def test_check_runs_the_symmetric_checks_and_writes_nothing(self):
        r = self.rotation_job(check=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("CHECK OK", r.stdout)
        self.assertFalse(os.path.exists(self.files()[0]))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        r = self.rotation_job(check=True, patch="meshgroups.meshsym._periodic = lambda *a, **k: None")
        self.assertEqual(r.returncode, 1)
        self.assertIn("do not match", r.stderr)


if __name__ == "__main__":
    unittest.main()
