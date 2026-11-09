"""Group jobs: the mesher meshes each group's cell, copies it by the group's transforms and gives every copy the part its
row names. Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py"""

import json
import math
import os
import subprocess
import sys
import tempfile
import unittest

import gmsh
import numpy as np

from emsolution import meshfrozen
from .test_mesher import MESHER, write_line
from .test_mesher2d import MESHER2D, write_arc, write_sectors
from .test_meshsym import chain, compose, mesh_check, mirror_line, rotation
from .test_meshsym3d import slide_nodes, surface_group, write_face, write_sector_solids
from .meshreport import groups

sys.path.insert(0, os.path.dirname(MESHER))  # meshgroups imports its neighbours by bare name, as in the mesher process
import meshgroups  # noqa: E402 - needs the path above

ID = rotation(0)
MIRROR_Z = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1]


def read_mesh(path):
    """(xyz[n, 3], {element type: connectivity[n, k]}) of the elements of highest dimension of a mesh file, nodes
    0-based into xyz."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        dim = max(d for d, _ in gmsh.model.getEntities())
        tags, coords, _ = gmsh.model.mesh.getNodes()
        where = {int(t): k for k, t in enumerate(tags)}
        xyz = np.asarray(coords).reshape(-1, 3)
        found = {}
        for typ in gmsh.model.mesh.getElementTypes(dim):
            etags, nodes = gmsh.model.mesh.getElementsByType(typ)
            per = len(nodes) // len(etags)
            found[typ] = np.array([where[int(n)] for n in nodes]).reshape(-1, per)
        return xyz, found
    finally:
        gmsh.finalize()


def element_count(path):
    return sum(len(c) for c in read_mesh(path)[1].values())


def node_count(path):
    return len(read_mesh(path)[0])


def element_names(path):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        dim = max(d for d, _ in gmsh.model.getEntities())
        return {gmsh.model.mesh.getElementProperties(t)[0] for t in gmsh.model.mesh.getElementTypes(dim)}
    finally:
        gmsh.finalize()


def z_range(path):
    z = read_mesh(path)[0][:, 2]
    return round(float(z.min()), 6), round(float(z.max()), 6)


def volume(path):
    xyz, found = read_mesh(path)
    t = xyz[found[4]]  # tetrahedra
    return float(
        np.abs(np.einsum("ij,ij->i", np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), t[:, 3] - t[:, 0])).sum() / 6
    )


def faces_in_three(path):
    xyz, found = read_mesh(path)
    return meshfrozen.boundary(xyz, [found], 3).over_used


def translation(x, y=0):
    return [1, 0, 0, x, 0, 1, 0, y, 0, 0, 1, 0, 0, 0, 0, 1]


def write_boxes(path, *boxes):
    """One BREP holding a solid per (x, y, z, dx, dy, dz)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        for box in boxes:
            gmsh.model.occ.addBox(*box)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_rects(path, *rects):
    """One BREP holding a face per (x, y, dx, dy)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        for x, y, dx, dy in rects:
            gmsh.model.occ.addRectangle(x, y, 0, dx, dy)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def _polar(r, degrees):
    return r * math.cos(math.radians(degrees)), r * math.sin(math.radians(degrees))


def _write_loop(path, edges):
    """One BREP holding the plane face bounded by edges: (x, y) pairs joined by lines, or (start, centre, end) arcs."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        points = {}

        def point(p):
            key = (round(p[0], 9), round(p[1], 9))
            if key not in points:
                points[key] = occ.addPoint(p[0], p[1], 0)
            return points[key]

        curves = [
            occ.addLine(point(e[0]), point(e[1]))
            if len(e) == 2
            else occ.addCircleArc(point(e[0]), point(e[1]), point(e[2]))
            for e in edges
        ]
        occ.addPlaneSurface([occ.addCurveLoop(curves)])
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_sector_split_seam(path, inner, outer, angle, split):
    """The sector from 0 to angle between the radii; its side at angle is two lines that meet at radius split."""
    start, end = _polar(inner, 0), _polar(outer, 0)
    middle = _polar(split, angle)
    arc_out = (end, (0, 0), _polar(outer, angle))
    arc_in = (_polar(inner, angle), (0, 0), start)
    _write_loop(path, [(start, end), arc_out, (_polar(outer, angle), middle), (middle, _polar(inner, angle)), arc_in])


def write_sector_curved_seams(path, inner, outer, angle):
    """A sector from 0 to angle whose two sides are the same circle arc, bulging towards increasing angle."""
    bulge = (inner + outer) / 2
    centre = (bulge, -(outer - inner))
    turned = _polar(math.hypot(*centre), math.degrees(math.atan2(centre[1], centre[0])) + angle)
    arc_out = (_polar(outer, 0), (0, 0), _polar(outer, angle))
    arc_in = (_polar(inner, angle), (0, 0), _polar(inner, 0))
    side_0 = (_polar(inner, 0), centre, _polar(outer, 0))
    side_angle = (_polar(outer, angle), turned, _polar(inner, angle))
    _write_loop(path, [side_0, arc_out, side_angle, arc_in])


def _physical_mesh(path, ids):
    """(xyz, {id: elements of dimension dim of that physical group}, dim): the nodes of ids together, so shared."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        dim = max(d for d, _ in gmsh.model.getEntities())
        entities = {i: list(gmsh.model.getEntitiesForPhysicalGroup(dim, i)) for i in ids}
        xyz, elements = meshfrozen.read_model(dim, entities)
    finally:
        gmsh.finalize()
    return xyz, elements, dim


def shared_area(path, a, b):
    """The area (length in 2D) that the elements of physical groups a and b share."""
    xyz, elements, dim = _physical_mesh(path, (a, b))
    both = meshfrozen.boundary(xyz, [elements[a], elements[b]], dim).shared_area
    return both - sum(meshfrozen.boundary(xyz, [elements[k]], dim).shared_area for k in (a, b))


def free_length(path):
    """The total length of the element edges used by one element, of a 2D mesh in one physical group."""
    xyz, found = read_mesh(path)
    edges = meshfrozen.boundary(xyz, [found], 2).edge
    return float(np.linalg.norm(xyz[edges[:, 1]] - xyz[edges[:, 0]], axis=1).sum())


def contact_table_of(group, folder, dim):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        return meshgroups.contact_table(group, group["job"], folder, dim)
    finally:
        gmsh.finalize()


class GroupJobTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.mkdir(os.path.join(self.dir, "geometry"))
        self.count = 0
        self.result = None

    def tearDown(self):
        self.tmp.cleanup()

    def mesh_file(self):
        return os.path.join(self.dir, "pre_geom2D.msh")

    def rotor_file(self):
        return os.path.join(self.dir, "rotor_mesh2D.msh")

    def sector_group(self, sector, transforms, parts, name="Stator", size=2.0, rows=None, extra=None, side="fixed"):
        """A group of one cell: the annular sector (inner, outer, a0, a1); rows default to one row, copy c taking
        parts[c % len(parts)]."""
        self.count += 1
        rel = f"geometry/cell_{self.count}.brep"
        write_sectors(os.path.join(self.dir, rel), sector)
        job = {"bodies": [{"mat_id": 1, "name": "Cell", "file": rel, "size": size}], "sizes": []}
        job.update(extra or {})
        rows = rows or [{"cell": 1, "file": None, "parts": [k % len(parts) for k in range(len(transforms))]}]
        return {
            "name": name,
            "side": side,
            "job": job,
            "cells": [1],
            "transforms": transforms,
            "parts": parts,
            "rows": rows,
        }

    def run_job(self, groups, free=(), slide=None, dim=2, check=False, patch=""):
        """Run the mesher on the job (--check when check); patch: Python run on the mesher modules first."""
        mesher = MESHER2D if dim == 2 else MESHER
        job = {
            "model_name": "Model",
            "mesh_file": self.mesh_file(),
            "options": {},
            "symmetric": {"groups": groups},
        }
        if dim == 2:
            job["dimension"] = "2D"
        if free:
            job["symmetric"]["free"] = list(free)
        if slide:
            job["symmetric"]["slide"] = slide
            job["rotor_file"] = self.rotor_file()
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        cmd = [sys.executable, mesher, path] + (["--check"] if check else [])
        if patch:
            code = (
                f"import runpy, sys; sys.path.insert(0, {os.path.dirname(mesher)!r}); import meshgroups; {patch}; "
                f"sys.argv = {cmd[1:]!r}; runpy.run_path({mesher!r}, run_name='__main__')"
            )
            cmd = [sys.executable, "-c", code]
        self.result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
        return self.result

    def meshed(self, *args, **kw):
        r = self.run_job(*args, **kw)
        self.assertEqual(r.returncode, 0, r.stderr)
        return self.mesh_file()

    def count_of(self, *args, **kw):
        """The elements of the mesh of the job."""
        return element_count(self.meshed(*args, **kw))

    IRON = [{"mat_id": 7, "name": "Iron"}]
    TWELVE = [rotation(30 * k) for k in range(12)]

    def test_one_part_over_twelve_copies(self):
        one = self.count_of([self.sector_group((10, 20, 0, 30), [ID], self.IRON)])
        mesh = self.meshed([self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON)])
        found = groups(mesh)
        self.assertEqual(list(found), [7])
        self.assertEqual(found[7][0], "Iron")
        self.assertEqual(found[7][1], 12 * one)
        self.assertEqual(mesh_check(mesh, [10, 20])[1:], (0, 0))
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))

    TWO = [{"mat_id": 7, "name": "North"}, {"mat_id": 8, "name": "South"}]

    def test_rows_give_parts_by_copy(self):
        mesh = self.meshed([self.sector_group((10, 20, 0, 30), self.TWELVE, self.TWO)])
        self.assertEqual({k: v[0] for k, v in groups(mesh).items()}, {7: "North", 8: "South"})
        self.assertEqual(groups(mesh)[7][1], groups(mesh)[8][1])

    def test_parts_do_not_change_the_mesh(self):
        mesh = self.meshed([self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON)])
        one = element_count(mesh), node_count(mesh)
        mesh = self.meshed([self.sector_group((10, 20, 0, 30), self.TWELVE, self.TWO)])
        self.assertEqual((element_count(mesh), node_count(mesh)), one)

    def test_cell_with_two_rows_splits_by_solid(self):  # one body of two faces, a file per row
        group = self.sector_group((10, 20, 0, 15), self.TWELVE, self.TWO)
        write_sectors(os.path.join(self.dir, "geometry", "cell_two.brep"), (10, 20, 0, 15), (10, 20, 15, 30))
        group["job"]["bodies"][0]["file"] = "geometry/cell_two.brep"
        for k, sector in enumerate(((10, 20, 0, 15), (10, 20, 15, 30))):
            write_sectors(os.path.join(self.dir, "geometry", f"row_{k}.brep"), sector)
        group["rows"] = [
            {"cell": 1, "file": f"geometry/row_{k}.brep", "parts": [k] * len(self.TWELVE)} for k in range(2)
        ]
        found = groups(self.meshed([group]))
        whole = self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON)
        whole["job"]["bodies"][0]["file"] = "geometry/cell_two.brep"
        self.assertEqual(found[7][1] + found[8][1], self.count_of([whole]))
        self.assertGreater(found[7][1], 0)
        self.assertGreater(found[8][1], 0)

    def test_structured_and_free_cells_in_one_group(self):  # a transfinite recombined sector beside a free one
        self.count += 1
        write_sectors(os.path.join(self.dir, "geometry", "both.brep"), (10, 20, 0, 45), (20, 30, 0, 45))
        write_sectors(os.path.join(self.dir, "geometry", "core.brep"), (10, 20, 0, 45))
        write_sectors(os.path.join(self.dir, "geometry", "free.brep"), (20, 30, 0, 45))
        c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
        geo = lambda n: os.path.join(self.dir, "geometry", n)  # noqa: E731
        write_line(geo("tedge_1.brep"), (10, 0, 0), (20, 0, 0))
        write_line(geo("tedge_2.brep"), (10 * c, 10 * s, 0), (20 * c, 20 * s, 0))
        write_arc(geo("tedge_3.brep"), 10, 0, 45)
        write_arc(geo("tedge_4.brep"), 20, 0, 45)
        edges = [f"geometry/tedge_{k}.brep" for k in range(1, 5)]
        edge = {"name": "Edges", "nodes": 7, "distribution": "Uniform", "coef": 1.0, "files": edges}
        job = {
            "bodies": [
                {"mat_id": 1, "name": "Core", "file": "geometry/core.brep", "size": 2.0},
                {"mat_id": 2, "name": "Free", "file": "geometry/free.brep", "size": 2.0},
            ],
            "sizes": [],
            "transfinite": {"bodies": [{"name": "Core", "mat_id": 1, "corner_files": []}], "edges": [edge]},
            "recombine": [1],
        }
        transforms = [compose(rotation(90 * k), m) for k in range(4) for m in (ID, mirror_line(45))]
        rows = [{"cell": k, "file": None, "parts": [0] * len(transforms)} for k in (1, 2)]
        group = {
            "name": "Mixed",
            "side": "fixed",
            "job": job,
            "cells": [1, 2],
            "transforms": transforms,
            "parts": [{"mat_id": 4, "name": "Iron"}],
            "rows": rows,
        }
        mesh = self.meshed([group])
        self.assertEqual(element_names(mesh), {"Quadrilateral 4", "Triangle 3"})
        self.assertEqual(mesh_check(mesh, [10, 30])[1:], (0, 0))
        self.assertEqual(list(groups(mesh)), [4])

    def test_z_mirror_3d(self):
        write_sector_solids(os.path.join(self.dir, "geometry", "cell3d.brep"), (10, 20, 0, 30, 0, 5))
        job = {
            "volumes": [{"mat_id": 1, "name": "Cell", "file": "geometry/cell3d.brep", "size": 3.0}],
            "surfaces": [],
            "sizes": [],
        }
        transforms = [compose(rotation(30 * k), m) for k in range(12) for m in (ID, MIRROR_Z)]
        group = {
            "name": "Ring",
            "side": "fixed",
            "job": job,
            "cells": [1],
            "transforms": transforms,
            "parts": self.IRON,
            "rows": [{"cell": 1, "file": None, "parts": [0] * len(transforms)}],
        }
        mesh = self.meshed([group], dim=3)
        self.assertEqual(z_range(mesh), (-5, 5))
        self.assertAlmostEqual(volume(mesh) / (math.pi * 300 * 10), 1, delta=1e-2)
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertEqual(list(groups(mesh)), [7])

    def ring_3d(self, transforms, tops):
        """A 3D group: the solid sector (10, 20, 0, 30, 0, 5) copied by transforms, with the excitation Exc (SMAT_ID
        101) on the top faces (z = 5) of the sectors starting at the angles tops."""
        write_sector_solids(os.path.join(self.dir, "geometry", "cell3d.brep"), (10, 20, 0, 30, 0, 5))
        files = []
        for k, a in enumerate(tops):
            write_face(os.path.join(self.dir, "geometry", f"exc_{k}.brep"), sector=(10, 20, a, a + 30), z=5)
            files.append(f"geometry/exc_{k}.brep")
        job = {
            "volumes": [{"mat_id": 1, "name": "Cell", "file": "geometry/cell3d.brep", "size": 3.0}],
            "surfaces": [],
            "sizes": [],
        }
        return {
            "name": "Ring",
            "side": "fixed",
            "job": job,
            "cells": [1],
            "transforms": transforms,
            "parts": self.IRON,
            "rows": [{"cell": 1, "file": None, "parts": [0] * len(transforms)}],
            "excitations": [{"smat_id": 101, "name": "Exc", "files": files}],
        }

    def test_excitation_on_end_faces_of_copies(self):
        group = self.ring_3d(self.TWELVE, (0, 60))
        before = groups(self.meshed([self.ring_3d(self.TWELVE, ())], dim=3))
        mesh = self.meshed([group], dim=3)
        name, count, area = surface_group(mesh, 101)
        self.assertEqual(name, "Exc")
        self.assertGreater(count, 0)
        self.assertAlmostEqual(area / (2 * math.pi * 300 / 12), 1, delta=1e-2)
        self.assertEqual(groups(mesh), before)
        self.assertIn("SMAT_ID    101  Exc", self.result.stdout)

    def test_excitation_with_a_mirror(self):  # the mirrored copies are reversed; only the top at z = 5 is the face
        transforms = [compose(rotation(30 * k), m) for k in range(12) for m in (ID, MIRROR_Z)]
        mesh = self.meshed([self.ring_3d(transforms, (0, 60))], dim=3)
        name, count, area = surface_group(mesh, 101)
        self.assertEqual(name, "Exc")
        self.assertAlmostEqual(area / (2 * math.pi * 300 / 12), 1, delta=1e-2)
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertEqual(groups(mesh)[7][1], groups(self.meshed([self.ring_3d(transforms, ())], dim=3))[7][1])

    def test_excitation_on_a_mirrored_copy_is_reversed(self):  # the copy at 30..60 degrees is the mirror of the cell
        transforms = [compose(rotation(60 * k), m) for k in range(6) for m in (ID, mirror_line(30))]
        mesh = self.meshed([self.ring_3d(transforms, (30,))], dim=3)
        self.assertAlmostEqual(surface_group(mesh, 101)[2] / (math.pi * 300 / 12), 1, delta=1e-2)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(mesh)
            tags, coords, _ = gmsh.model.mesh.getNodes()
            xyz = {int(t): np.array(coords[3 * k : 3 * k + 3]) for k, t in enumerate(tags)}
            down = 0
            for e in gmsh.model.getEntitiesForPhysicalGroup(2, 101):
                for etype, _, nodes in zip(*gmsh.model.mesh.getElements(2, e)):
                    n = np.reshape(nodes, (-1, 3 if etype == 2 else 4))
                    for a, b, c, *_ in n:
                        down += np.cross(xyz[int(b)] - xyz[int(a)], xyz[int(c)] - xyz[int(a)])[2] <= 0
        finally:
            gmsh.finalize()
        self.assertEqual(down, 0)  # the face normals point up, out of the solid, as for an unmirrored copy

    def test_groups_do_not_influence_each_other(self):
        a = lambda: self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON, "A", size=2.0)  # noqa: E731
        b = lambda: self.sector_group(  # noqa: E731
            (40, 50, 0, 45), [rotation(45 * k) for k in range(8)], [{"mat_id": 8, "name": "Far"}], "B", size=3.0
        )
        only_a, only_b = self.count_of([a()]), self.count_of([b()])
        found = groups(self.meshed([a(), b()]))
        self.assertEqual(found[7][1], only_a)
        self.assertEqual(found[8][1], only_b)

    def test_group_with_no_rules(self):
        self.assertGreater(groups(self.meshed([self.sector_group((10, 20, 0, 30), [ID], self.IRON)]))[7][1], 0)

    def test_copies_that_overlap_are_refused(self):  # three copies on the same place: every edge has six elements
        r = self.run_job([self.sector_group((10, 20, 0, 30), [ID, ID, ID], self.IRON)])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("more than two elements", r.stderr)
        self.assertFalse(os.path.exists(self.mesh_file()))

    def test_report_names_poor_elements_per_part(self):
        r = self.run_job([self.sector_group((10, 20, 0, 30), self.TWELVE, self.TWO)], patch="meshgroups.POOR = 2.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Poor elements  North", r.stdout)
        self.assertIn("Poor elements  South", r.stdout)
        self.assertIn("MAT_ID       7  North", r.stdout)

    def test_check_writes_nothing(self):
        r = self.run_job([self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON)], check=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("CHECK OK", r.stdout)
        self.assertFalse(os.path.exists(self.mesh_file()))

    def slide_groups(self, stator_outer=60, rotor_outer=35):
        """Stator r 35..60 (12 copies, mirrored at 15°) and rotor r 10..rotor_outer (8 copies); the circle is r 35."""
        stator = self.sector_group((35, stator_outer, 0, 15), chain(15, 30, 12), [{"mat_id": 5, "name": "Stator"}])
        rotor = self.sector_group(
            (10, rotor_outer, 0, 22.5), chain(22.5, 45, 8), [{"mat_id": 6, "name": "Rotor"}], "Rotor", side="moving"
        )
        return stator, rotor

    SLIDE_2D = {
        "name": "Slide",
        "kind": "rotational",
        "radius": 35.0,
        "divisions": 144,
        "slide_mat_id": 7,
        "full": True,
    }

    def test_sliding_2d_two_sides(self):  # today's stator and rotor as two groups, 144 divisions
        r = self.run_job(list(self.slide_groups()), slide=self.SLIDE_2D)
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, rotor = self.mesh_file(), self.rotor_file()
        self.assertEqual(len(slide_nodes(fixed, 35)), 144)
        self.assertEqual(sorted(slide_nodes(fixed, 35)), sorted(slide_nodes(rotor, 35)))
        self.assertEqual([mesh_check(f, ())[1] for f in (fixed, rotor)], [0, 0])
        self.assertEqual(sorted(groups(fixed)), [5])
        self.assertEqual(sorted(groups(rotor)), [6])
        self.assertIn("SLIDE_NDIV 144", r.stdout)
        self.assertIn(f"Wrote {rotor}", r.stdout)

    def test_two_groups_on_a_side_only_one_reaches(self):  # a group that stays clear of the circle
        stator, rotor = self.slide_groups()
        far_parts = [{"mat_id": 9, "name": "Far"}]
        far = self.sector_group((70, 80, 0, 45), [rotation(45 * k) for k in range(8)], far_parts, "Far")
        r = self.run_job([stator, far, rotor], slide=self.SLIDE_2D)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(groups(self.mesh_file())), [5, 9])
        self.assertEqual(sorted(slide_nodes(self.mesh_file(), 35)), sorted(slide_nodes(self.rotor_file(), 35)))

    def test_side_that_does_not_reach_is_refused(self):
        r = self.run_job(list(self.slide_groups(rotor_outer=34.5)), slide=self.SLIDE_2D)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("must reach it", r.stderr)
        self.assertIn("moving side", r.stderr)

    def slide_groups_3d(self, cross=4, rotor_outer=20, top=5, mirror=True):
        """Cells over z 0..5 (sector 30°, radius 20 the circle) mirrored at z = 0 and rotated 12 times; z_range -5..5."""
        out = []
        for k, (name, side, sector, mat) in enumerate(
            (("Stator", "fixed", (20, 30, 0, 30, 0, top), 5), ("Rotor", "moving", (10, rotor_outer, 0, 30, 0, top), 6))
        ):
            rel = f"geometry/slide_{k}.brep"
            write_sector_solids(os.path.join(self.dir, rel), sector)
            job = {"volumes": [{"mat_id": 1, "name": "Cell", "file": rel, "size": 3.0}], "surfaces": [], "sizes": []}
            transforms = [
                compose(rotation(30 * c), m) for c in range(12) for m in ((ID, MIRROR_Z) if mirror else (ID,))
            ]
            out.append(
                {
                    "name": name,
                    "side": side,
                    "job": job,
                    "cells": [1],
                    "transforms": transforms,
                    "parts": [{"mat_id": mat, "name": name}],
                    "rows": [{"cell": 1, "file": None, "parts": [0] * len(transforms)}],
                    "turns": 12,
                }
            )
        slide = {"name": "Slide", "kind": "rotational", "radius": 20.0, "divisions": 144, "cross_divisions": cross}
        return out, dict(slide, slide_mat_id=7, full=True, z_range=[-5, 5])

    def test_sliding_3d_with_z_mirror(self):  # cells over z 0..5, Mirror z = 0, Rotate, z_range [-5, 5], cross 4
        groups_3d, slide = self.slide_groups_3d()
        r = self.run_job(groups_3d, slide=slide, dim=3)
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, rotor = self.mesh_file(), self.rotor_file()
        self.assertEqual(len(slide_nodes(fixed, 20)), 144 * 5)
        self.assertEqual(sorted(slide_nodes(fixed, 20)), sorted(slide_nodes(rotor, 20)))
        self.assertEqual(z_range(fixed), (-5, 5))
        self.assertEqual(sorted(groups(rotor)), [6])

    def test_cross_divisions_off_the_mirror_are_refused(self):  # cross 3 with the mirror at the middle
        groups_3d, slide = self.slide_groups_3d(cross=3)
        r = self.run_job(groups_3d, slide=slide, dim=3)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("off the grid", r.stderr)

    def test_cell_short_of_the_z_range_is_refused(self):  # cells over z 0..3, z_range -5..5, turns 12, no mirror
        groups_3d, slide = self.slide_groups_3d(top=3, mirror=False)
        r = self.run_job(groups_3d, slide=slide, dim=3)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("do not reach over the whole cylinder", r.stderr)

    def test_3d_side_that_does_not_reach_is_refused(self):
        groups_3d, slide = self.slide_groups_3d(rotor_outer=19)
        r = self.run_job(groups_3d, slide=slide, dim=3)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("must reach it", r.stderr)

    def geo(self, name):
        return os.path.join(self.dir, "geometry", name)

    def two_cells(self, name, key, first, second, transforms, sizes):
        """A group of two cells, each with its own part: 1 (MAT_ID 7) in BREP first, 2 (MAT_ID 8) in second, with the
        sizes (size of 1, size of 2). A size that differs keeps the meshes of the two from matching by chance."""
        job = {
            key: [
                {"mat_id": 1, "name": "Iron", "file": first, "size": sizes[0]},
                {"mat_id": 2, "name": "Coil", "file": second, "size": sizes[1]},
            ],
            "sizes": [],
        }
        if key == "volumes":
            job["surfaces"] = []
        rows = [{"cell": c, "file": None, "parts": [c - 1] * len(transforms)} for c in (1, 2)]
        parts = [{"mat_id": 7, "name": "Iron"}, {"mat_id": 8, "name": "Coil"}]
        group = {"name": name, "side": "fixed", "job": job, "cells": [1, 2], "transforms": transforms}
        return dict(group, parts=parts, rows=rows)

    def test_plate_shares_nodes_with_two_copies_of_the_bar(self):
        write_boxes(self.geo("bar.brep"), (0, 0, 0, 1, 1, 1), (1, 0, 1, 1, 1, 1))
        write_boxes(self.geo("plate.brep"), (0, 1, 0, 1, 1, 2))
        group = self.two_cells(
            "Stack",
            "volumes",
            "geometry/bar.brep",
            "geometry/plate.brep",
            [translation(k) for k in range(4)],
            (0.3, 0.5),
        )
        mesh = self.meshed([group], dim=3)
        self.assertAlmostEqual(shared_area(mesh, 7, 8), 2.0 * 4 - 1.0, delta=1e-6)
        self.assertEqual(list(groups(mesh)), [7, 8])  # the images are not in the mesh
        self.assertAlmostEqual(volume(mesh), 16, delta=1e-6)

    def test_seam_of_identical_wedges_needs_no_image(self):  # the sector of test_one_part_over_twelve_copies
        group = self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON)
        contacts = contact_table_of(group, self.dir, 2)
        self.assertTrue(contacts)
        self.assertTrue(all(c.seam for c in contacts))
        self.assertAlmostEqual(sum(c.area * c.count for c in contacts), 12 * 10, delta=1e-6)

    def test_seam_that_does_not_match_is_refused(self):  # T-06: the 30° side of the sector is split at r 15
        group = self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON)
        write_sector_split_seam(os.path.join(self.dir, group["job"]["bodies"][0]["file"]), 10, 20, 30, 15)
        r = self.run_job([group])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("do not match", r.stderr)
        self.assertFalse(os.path.exists(self.mesh_file()))

    def test_bricks_share_nodes_with_two_copies_2d(self):  # the plate test in 2D: B straddles two copies of A
        write_rects(self.geo("a.brep"), (0, 0, 2, 1))
        write_rects(self.geo("b.brep"), (1, 1, 2, 1))
        group = self.two_cells(
            "Wall", "bodies", "geometry/a.brep", "geometry/b.brep", [translation(2 * k) for k in range(3)], (0.15, 0.4)
        )
        mesh = self.meshed([group])
        self.assertAlmostEqual(shared_area(mesh, 7, 8), 5.0, delta=1e-6)  # 3 under its own copy, 2 under the next
        self.assertEqual(mesh_check(mesh, ())[1], 0)

    def test_bricks_around_a_closed_ring(self):  # curved contact, and both T and its inverse are in the table
        write_sectors(self.geo("a.brep"), (10, 20, 0, 30))
        write_sectors(self.geo("b.brep"), (20, 30, 15, 45))
        group = self.two_cells("Ring", "bodies", "geometry/a.brep", "geometry/b.brep", self.TWELVE, (0.8, 2.0))
        mesh = self.meshed([group])
        self.assertAlmostEqual(shared_area(mesh, 7, 8) / (2 * math.pi * 20), 1, delta=1e-2)
        self.assertEqual(mesh_check(mesh, ())[1], 0)

    def test_a_cell_that_touches_its_own_copy_partly(self):  # a staircase of 3: step k sits on half of step k - 1
        write_rects(self.geo("a.brep"), (0, 0, 2, 1))
        group = self.sector_group((10, 20, 0, 30), [translation(k, k) for k in range(3)], self.IRON, size=0.3)
        group["job"]["bodies"][0]["file"] = "geometry/a.brep"
        mesh = self.meshed([group])
        self.assertEqual(list(groups(mesh)), [7])
        self.assertEqual(mesh_check(mesh, ())[1], 0)
        # three bricks of 2 x 1 that share two half-edges: the free outline is 3 * 6 - 2 * 2 = 14
        self.assertAlmostEqual(free_length(mesh), 14, delta=1e-6)

    def test_contact_left_unpaired_is_refused_3d(
        self,
    ):  # pair_images off: the plate meets a copy that it does not match
        write_boxes(self.geo("bar.brep"), (0, 0, 0, 1, 1, 1), (1, 0, 1, 1, 1, 1))
        write_boxes(self.geo("plate.brep"), (0, 1, 0, 1, 1, 2))
        group = self.two_cells(
            "Stack",
            "volumes",
            "geometry/bar.brep",
            "geometry/plate.brep",
            [translation(k) for k in range(4)],
            (0.3, 0.5),
        )
        r = self.run_job([group], dim=3, patch="meshgroups.pair_images = lambda *a, **k: None")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("do not match near", r.stderr)

    def test_contact_the_method_cannot_pair_is_a_limit_of_the_tool(self):  # no face of the image finds its partner
        write_rects(self.geo("a.brep"), (0, 0, 2, 1))
        write_rects(self.geo("b.brep"), (1, 1, 2, 1))
        group = self.two_cells(
            "Wall", "bodies", "geometry/a.brep", "geometry/b.brep", [translation(2 * k) for k in range(3)], (0.15, 0.4)
        )
        r = self.run_job([group], patch="meshgroups.meshsym._apply = lambda m, p: [9e9] * 3")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("limit of the tool", r.stderr)

    def test_curved_seam_is_not_refused(self):  # the mesh's chords are shorter than the arc they follow
        group = self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON)
        write_sector_curved_seams(os.path.join(self.dir, group["job"]["bodies"][0]["file"]), 10, 20, 30)
        mesh = self.meshed([group])
        self.assertEqual(mesh_check(mesh, ())[1], 0)


if __name__ == "__main__":
    unittest.main()
