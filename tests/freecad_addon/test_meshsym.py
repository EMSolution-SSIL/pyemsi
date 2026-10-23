"""Symmetric mesh tests: the mesher meshes the cell, copies it and labels each copy by the piece it lands on.
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

    def cell(self, mat_id, name, sector, size=2.0):
        """A cell body: one annular sector (inner, outer, a0, a1)."""
        write_sectors(self.geo(f"vol_{mat_id}.brep"), sector)
        return {"mat_id": mat_id, "name": name, "file": f"geometry/vol_{mat_id}.brep", "size": size}

    def piece(self, mat_id, name, *sectors):
        self.count += 1
        rel = f"geometry/piece_{self.count}.brep"
        write_sectors(os.path.join(self.dir, rel), *sectors)
        return {"mat_id": mat_id, "name": name, "file": rel}

    def run_job(self, bodies, sides, slide=None, extra=None, check=False, patch=""):
        """Run the mesher on the job (--check when check); patch: Python run on meshsym first, e.g. to break it."""
        job = {
            "dimension": "2D",
            "model_name": "Model",
            "msh_version": 4.1,
            "mesh_file": self.files()[0],
            "bodies": bodies,
            "sizes": [],
            "symmetric": {"sides": sides},
        }
        if slide:
            job["symmetric"]["slide"] = slide
            job["rotor_file"] = self.files()[1]
        job.update(extra or {})
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        cmd = [sys.executable, MESHER2D, path] + (["--check"] if check else [])
        if patch:
            code = (
                f"import runpy, sys; sys.path.insert(0, {os.path.dirname(MESHER2D)!r}); import meshsym; {patch}; "
                f"sys.argv = {cmd[1:]!r}; runpy.run_path({MESHER2D!r}, run_name='__main__')"
            )
            cmd = [sys.executable, "-c", code]
        return subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")

    def ring_job(self, outer_ids=(2,) * 8, outer_cuts=None, **kw):
        """Cell: sectors r 10..20 (id 1) and 20..30 (id 2), 0..45°; 4 rotations × {identity, mirror at 45°}.
        Pieces: 8 inner sectors (MAT_ID 1) and 8 outer ones with outer_ids, cut at the angles outer_cuts."""
        bodies = [self.cell(1, "InnerCell", (10, 20, 0, 45)), self.cell(2, "OuterCell", (20, 30, 0, 45))]
        pieces = [self.piece(1, "Inner", (10, 20, 45 * k, 45 * (k + 1))) for k in range(8)]
        cuts = list(outer_cuts or range(0, 361, 45))
        for k, id_ in enumerate(outer_ids):
            pieces.append(self.piece(id_, f"Outer{id_}", (20, 30, cuts[k], cuts[k + 1])))
        side = {"side": "fixed", "cells": [1, 2], "transforms": chain(45, 90, 4), "pieces": pieces}
        return self.run_job(bodies, [side], **kw)

    def test_copies_cover_the_ring_without_gaps(self):
        r = self.ring_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(groups(self.files()[0])), [1, 2])
        _, inverted, loose = mesh_check(self.files()[0], (10, 30))
        self.assertEqual(inverted, 0)
        self.assertEqual(loose, 0)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        self.assertIn("Inner", r.stdout)

    def test_each_copy_takes_its_piece_mat_id(self):
        r = self.ring_job(outer_ids=(2, 3) * 4)
        self.assertEqual(r.returncode, 0, r.stderr)
        found = groups(self.files()[0])
        self.assertEqual(sorted(found), [1, 2, 3])
        self.assertEqual(found[2][1], found[3][1])
        self.assertEqual(found[3][0], "Outer3")

    def test_asymmetric_drawing_is_refused(self):
        r = self.ring_job(outer_cuts=[0, 44, 90, 135, 180, 225, 270, 315, 360])
        self.assertEqual(r.returncode, 1)
        self.assertIn("not symmetric", r.stderr)

    def slide_job(self, divisions):
        """Fixed cell r 35..60, 0..15° (mirror 15°, rotate 30° × 12); moving cell r 10..35, 0..22.5° (16 copies);
        sliding circle r 35."""
        bodies = [self.cell(1, "StatorCell", (35, 60, 0, 15)), self.cell(2, "RotorCell", (10, 35, 0, 22.5))]
        fixed = {
            "side": "fixed",
            "cells": [1],
            "transforms": chain(15, 30, 12),
            "pieces": [self.piece(5, "Stator", (35, 60))],
        }
        moving = {
            "side": "moving",
            "cells": [2],
            "transforms": chain(22.5, 45, 8),
            "pieces": [self.piece(6, "Rotor", (10, 35))],
        }
        slide = {"name": "Slide", "kind": "rotational", "radius": 35.0, "divisions": divisions, "slide_mat_id": 7}
        slide["full"] = True
        return self.run_job(bodies, [fixed, moving], slide)

    def test_sliding_sides_match(self):
        r = self.slide_job(144)
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
        bodies = [self.cell(1, "Core", (10, 20, 0, 45))]
        c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
        write_line(self.geo("tedge_1.brep"), (10, 0, 0), (20, 0, 0))
        write_line(self.geo("tedge_2.brep"), (10 * c, 10 * s, 0), (20 * c, 20 * s, 0))
        write_arc(self.geo("tedge_3.brep"), 10, 0, 45)
        write_arc(self.geo("tedge_4.brep"), 20, 0, 45)
        edges = [f"geometry/tedge_{k}.brep" for k in range(1, 5)]
        edge = {"name": "Edges", "nodes": 7, "distribution": "Uniform", "coef": 1.0, "files": edges}
        tf = {"bodies": [{"name": "Core", "mat_id": 1, "corner_files": []}], "edges": [edge]}
        pieces = [self.piece(4, "Iron", (10, 20, 45 * k, 45 * (k + 1))) for k in range(8)]
        side = {"side": "fixed", "cells": [1], "transforms": chain(45, 90, 4), "pieces": pieces}
        r = self.run_job(bodies, [side], extra={"transfinite": tf, "recombine": [1]})
        self.assertEqual(r.returncode, 0, r.stderr)
        kinds, inverted, loose = mesh_check(self.files()[0], (10, 20))
        self.assertEqual(kinds, {"Quadrilateral 4"})
        self.assertEqual(inverted, 0)
        self.assertEqual(loose, 0)
        self.assertEqual(groups(self.files()[0]), {4: ("Iron", 8 * 36)})

    def rotation_job(self, **kw):
        """Cell A r 10..30, 0..22.5° with a fine size, cell B 22.5..45° coarse; 8 rotations of 45°, no mirror: the
        0° seam of A meets the 45° seam of B of the next copy."""
        bodies = [self.cell(1, "A", (10, 30, 0, 22.5), size=0.5), self.cell(2, "B", (10, 30, 22.5, 45))]
        pieces = [self.piece(1, "PA", (10, 30, 45 * k, 45 * k + 22.5)) for k in range(8)]
        pieces += [self.piece(2, "PB", (10, 30, 45 * k + 22.5, 45 * k + 45)) for k in range(8)]
        side = {"side": "fixed", "cells": [1, 2], "transforms": [rotation(45 * k) for k in range(8)], "pieces": pieces}
        return self.run_job(bodies, [side], **kw)

    def test_pure_rotation_seams_conform(self):
        r = self.rotation_job()
        self.assertEqual(r.returncode, 0, r.stderr)
        _, inverted, loose = mesh_check(self.files()[0], (10, 30))
        self.assertEqual((inverted, loose), (0, 0))

    def test_seams_that_do_not_match_are_refused(self):
        r = self.rotation_job(patch="meshsym._periodic = lambda sides: None")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("do not match", r.stderr)
        self.assertFalse(os.path.exists(self.files()[0]))

    def test_side_short_of_the_sliding_circle_is_refused(self):
        bodies = [self.cell(1, "StatorCell", (35, 60, 0, 15)), self.cell(2, "RotorCell", (10, 34.5, 0, 22.5))]
        fixed = {
            "side": "fixed",
            "cells": [1],
            "transforms": chain(15, 30, 12),
            "pieces": [self.piece(5, "S", (35, 60))],
        }
        moving = {"side": "moving", "cells": [2], "transforms": chain(22.5, 45, 8)}
        moving["pieces"] = [self.piece(6, "R", (10, 34.5))]
        slide = {"name": "Slide", "kind": "rotational", "radius": 35.0, "divisions": 144, "slide_mat_id": 7}
        r = self.run_job(bodies, [fixed, moving], slide)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("moving side", r.stderr)

    def test_side_covering_part_of_the_sliding_circle_is_refused(self):
        """The rotor cell reaches the circle from 0 to 10° only: its copies leave gaps in the circle."""
        write_sectors(self.geo("vol_2.brep"), (10, 35, 0, 10), (10, 34, 10, 22.5))
        rotor = {"mat_id": 2, "name": "RotorCell", "file": "geometry/vol_2.brep", "size": 2.0}
        bodies = [self.cell(1, "StatorCell", (35, 60, 0, 15)), rotor]
        fixed = {
            "side": "fixed",
            "cells": [1],
            "transforms": chain(15, 30, 12),
            "pieces": [self.piece(5, "S", (35, 60))],
        }
        parts = []
        for k in range(8):
            a = 45 * k
            parts += [(10, 35, a, a + 10), (10, 34, a + 10, a + 35), (10, 35, a + 35, a + 45)]
        moving = {
            "side": "moving",
            "cells": [2],
            "transforms": chain(22.5, 45, 8),
            "pieces": [self.piece(6, "R", *parts)],
        }
        slide = {"name": "Slide", "kind": "rotational", "radius": 35.0, "divisions": 144, "slide_mat_id": 7}
        r = self.run_job(bodies, [fixed, moving], slide)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("moving side", r.stderr)
        self.assertIn("on the circle", r.stderr)

    def test_check_runs_the_symmetric_checks_and_writes_nothing(self):
        r = self.rotation_job(check=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("CHECK OK", r.stdout)
        self.assertFalse(os.path.exists(self.files()[0]))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        r = self.ring_job(outer_cuts=[0, 44, 90, 135, 180, 225, 270, 315, 360], check=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("not symmetric", r.stderr)


if __name__ == "__main__":
    unittest.main()
