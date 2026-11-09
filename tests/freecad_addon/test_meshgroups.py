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
from .test_mesher2d import write_rects as write_plane_rects
from .test_meshsym import chain, compose, mesh_check, mirror_line, rotation
from .test_meshsym3d import mesh_check_3d, slide_nodes, surface_group, write_face, write_sector_solids
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


def free_area(path):
    """The total area of the element faces used by one element, of a 3D mesh."""
    xyz, found = read_mesh(path)
    b = meshfrozen.boundary(xyz, [found], 3)
    return float(meshfrozen._area(xyz, b.tri).sum() + meshfrozen._area(xyz, b.quad).sum())


def _facet_keys(xyz, b):
    """The facets of a Boundary, each as its sorted rounded corner coordinates: comparable between meshes."""
    return {
        tuple(sorted(tuple(np.round(p, 6) + 0.0) for p in xyz[f])) for facets in (b.tri, b.quad, b.edge) for f in facets
    }


def frozen_facets(path):
    """The facets on the outside of the whole mesh of a job with no free object."""
    xyz, found = read_mesh(path)
    return _facet_keys(xyz, meshfrozen.boundary(xyz, [found], 3 if any(t > 3 for t in found) else 2))


def boundary_of(path, id_):
    """(the facets used by one element among the elements of physical group id_, its elements)."""
    xyz, elements, dim = _physical_mesh(path, (id_,))
    return _facet_keys(xyz, meshfrozen.boundary(xyz, [elements[id_]], dim)), elements[id_]


def area(path, id_=None):
    """The total area of the elements of physical group id_, or of the whole 2D mesh."""
    if id_ is None:
        xyz, found = read_mesh(path)
    else:
        xyz, elements, _ = _physical_mesh(path, (id_,))
        found = elements[id_]
    return sum(float(meshfrozen._area(xyz, c).sum()) for c in found.values())


def area_or_volume_of_air(path):
    """The volume of the tetrahedra of physical group 20."""
    xyz, elements, _ = _physical_mesh(path, (20,))
    t = xyz[elements[20][4]]
    return float(
        np.abs(np.einsum("ij,ij->i", np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), t[:, 3] - t[:, 0])).sum() / 6
    )


def y_range(path):
    y = read_mesh(path)[0][:, 1]
    return round(float(y.min()), 6), round(float(y.max()), 6)


def write_disc(path, r):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addDisk(0, 0, 0, r, r)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_ring(path, inner, outer, z0, z1):
    """One BREP holding the solid ring between the radii, from z0 to z1."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        whole = occ.addCylinder(0, 0, z0, 0, 0, z1 - z0, outer)
        hole = occ.addCylinder(0, 0, z0, 0, 0, z1 - z0, inner)
        occ.cut([(3, whole)], [(3, hole)])
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_cylinders(path, *cylinders):
    """One BREP holding a solid per (x, y, z, height, radius), axis along Z."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        for x, y, z, height, radius in cylinders:
            gmsh.model.occ.addCylinder(x, y, z, 0, 0, height, radius)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def regions_of(path, id_):
    """How many connected regions the tetrahedra of physical group id_ form."""
    _, elements, _ = _physical_mesh(path, (id_,))
    tets = elements[id_][4]
    faces = np.vstack([np.sort(tets[:, local], axis=1) for local in meshfrozen.TRI_FACES[4]])
    owner = np.tile(np.arange(len(tets)), 4)
    inverse = np.unique(faces, axis=0, return_inverse=True)[1].ravel()
    order = np.argsort(inverse, kind="stable")
    twice = np.flatnonzero(np.diff(inverse[order]) == 0)
    pairs = np.column_stack([owner[order[twice]], owner[order[twice + 1]]])
    return len(np.unique(meshfrozen._components(len(tets), pairs)))


def edges_in_three(path):
    xyz, found = read_mesh(path)
    return meshfrozen.boundary(xyz, [found], 2).over_used


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

    def test_contact_left_unpaired_is_refused_3d(self):  # nothing paired: the plate does not match its copy
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
        off = "lambda *a, **k: None"
        r = self.run_job([group], dim=3, patch=f"meshgroups.pair_images = {off}; meshgroups.meshsym._periodic = {off}")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("do not match near", r.stderr)

    def box_group(self, box, transforms, size=0.27, file="box.brep"):
        """A 3D group of one cell, the box (x, y, z, dx, dy, dz). 0.27 divides no side: opposite faces differ by chance."""
        write_boxes(self.geo(file), box)
        job = {"volumes": [{"mat_id": 1, "name": "Cell", "file": f"geometry/{file}", "size": size}]}
        job.update(surfaces=[], sizes=[])
        rows = [{"cell": 1, "file": None, "parts": [0] * len(transforms)}]
        return {
            "name": "Boxes",
            "side": "fixed",
            "job": job,
            "cells": [1],
            "transforms": transforms,
            "parts": self.IRON,
            "rows": rows,
        }

    def test_seams_of_copies_towards_minus_x(self):  # the direction the transforms run in must not matter
        mesh = self.meshed([self.box_group((0, 0, 0, 1, 1, 1), [translation(-k) for k in range(3)])], dim=3)
        self.assertAlmostEqual(free_area(mesh), 3 * 6 - 2 * 2, delta=1e-6)

    def test_seam_of_copies_that_only_two_of_them_have(self):  # offsets 0, 2, 3: the relative +1 is not in the list
        mesh = self.meshed([self.box_group((0, 0, 0, 1, 1, 1), [translation(k) for k in (0, 2, 3)])], dim=3)
        self.assertAlmostEqual(free_area(mesh), 3 * 6 - 2, delta=1e-6)

    def test_staircase_3d_either_way(self):  # the image's face on the source is a seam of the cell, in both directions
        for sign in (1, -1):
            with self.subTest(sign=sign):
                transforms = [translation(sign * k, sign * k) for k in range(3)]
                mesh = self.meshed([self.box_group((0, 0, 0, 2, 1, 1), transforms)], dim=3)
                self.assertAlmostEqual(free_area(mesh), 3 * 10 - 2 * 2, delta=1e-6)

    def test_seam_whose_transform_is_not_in_the_list(self):  # copies at 0, +2, -2: copies 1 and 2 touch at relative -4
        write_rects(self.geo("a.brep"), (0, 0, 1, 1))
        write_rects(self.geo("b.brep"), (3, 0, 1, 1))
        transforms = [translation(0), translation(2), translation(-2)]
        group = self.two_cells("Row", "bodies", "geometry/a.brep", "geometry/b.brep", transforms, (0.15, 0.4))
        self.assertAlmostEqual(shared_area(self.meshed([group]), 7, 8), 3.0, delta=1e-6)

    def test_structured_cell_that_an_image_splits_is_a_limit_of_the_tool(self):
        write_rects(self.geo("a.brep"), (0, 0, 2, 1))
        write_rects(self.geo("b.brep"), (1, 1, 2, 1))
        group = self.two_cells(
            "Wall", "bodies", "geometry/a.brep", "geometry/b.brep", [translation(2 * k) for k in range(3)], (0.15, 0.4)
        )
        group["job"]["transfinite"] = {"bodies": [{"name": "Iron", "mat_id": 1, "corner_files": []}], "edges": []}
        r = self.run_job([group])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("limit of the tool", r.stderr)
        self.assertIn("Iron", r.stderr)
        self.assertEqual([n for n in os.listdir(self.dir) if n.startswith("images_")], [])

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

    AIR = {"mat_id": 20, "name": "Air", "file": "geometry/air.brep", "size": 6.0}

    def air_3d(self, *boxes, surfaces=(), size=6.0, side="fixed"):
        """A free job of one body, the solid boxes (x, y, z, dx, dy, dz), named Air (MAT_ID 20)."""
        write_boxes(self.geo("air.brep"), *boxes)
        return {"side": side, "job": {"volumes": [dict(self.AIR, size=size)], "surfaces": list(surfaces), "sizes": []}}

    def air_2d(self, size=6.0, side="fixed"):
        return {"side": side, "job": {"bodies": [dict(self.AIR, size=size)], "sizes": []}}

    BOX = (-30, -30, -5, 60, 60, 15)

    def test_box_of_air_around_rotated_copies(self):  # the free box is drawn right over the copied solids
        ring = lambda: self.ring_3d(self.TWELVE, ())  # noqa: E731
        frozen = frozen_facets(self.meshed([ring()], dim=3))
        mesh = self.meshed([ring()], free=[self.air_3d(self.BOX)], dim=3)
        kept, _ = boundary_of(mesh, 20)
        self.assertLessEqual(frozen, kept)
        self.assertEqual(mesh_check_3d(mesh, (), ())[1], 0)
        self.assertEqual(groups(mesh)[20][0], "Air")
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertAlmostEqual(volume(mesh) / (60 * 60 * 15), 1, delta=1e-6)
        self.assertIn("MAT_ID      20  Air", self.result.stdout)

    def test_mirrored_copies_in_free_air(self):  # mirrored copies have their elements reversed
        transforms = [compose(rotation(30 * k), m) for k in range(12) for m in (ID, MIRROR_Z)]
        mesh = self.meshed([self.ring_3d(transforms, ())], free=[self.air_3d((-30, -30, -10, 60, 60, 20))], dim=3)
        self.assertEqual(mesh_check_3d(mesh, (), ())[1], 0)
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertAlmostEqual(volume(mesh) / (60 * 60 * 20), 1, delta=1e-6)

    def hex_group(self, transforms):
        """A structured, recombined unit box, 3 divisions a side: every element a hexahedron."""
        write_boxes(self.geo("hex.brep"), (0, 0, 0, 1, 1, 1))
        pts = [(i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
        lines = [(p, q) for a, p in enumerate(pts) for q in pts[a + 1 :] if sum(abs(u - v) for u, v in zip(p, q)) == 1]
        files = []
        for k, (p, q) in enumerate(lines):
            write_line(self.geo(f"hedge_{k}.brep"), p, q)
            files.append(f"geometry/hedge_{k}.brep")
        edge = {"name": "E", "nodes": 4, "distribution": "Uniform", "coef": 1.0, "files": files}
        job = {
            "volumes": [{"mat_id": 1, "name": "Core", "file": "geometry/hex.brep", "size": 0.5}],
            "surfaces": [],
            "sizes": [],
            "transfinite": {"bodies": [{"name": "Core", "mat_id": 1, "corner_files": []}], "edges": [edge]},
            "recombine": [1],
        }
        return {
            "name": "Hex",
            "side": "fixed",
            "job": job,
            "cells": [1],
            "transforms": transforms,
            "parts": self.IRON,
            "rows": [{"cell": 1, "file": None, "parts": [0] * len(transforms)}],
        }

    def test_hex_copies_get_pyramids(self):  # gmsh sees only the triangles of the pyramids the tool built
        transforms = [translation(3 * k) for k in range(3)]
        frozen = frozen_facets(self.meshed([self.hex_group(transforms)], dim=3))
        mesh = self.meshed([self.hex_group(transforms)], free=[self.air_3d((-3, -3, -3, 13, 7, 7), size=1.5)], dim=3)
        kept, elements = boundary_of(mesh, 20)
        self.assertLessEqual({4, 7}, set(elements))  # tetrahedra and pyramids
        self.assertLessEqual(frozen, kept)
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertEqual(mesh_check_3d(mesh, (), ())[1], 0)

    def far_group(self):
        write_boxes(self.geo("far.brep"), (200, 200, 200, 4, 4, 4))
        job = {"volumes": [{"mat_id": 1, "name": "Far", "file": "geometry/far.brep", "size": 2.0}]}
        job.update(surfaces=[], sizes=[])
        parts = [{"mat_id": 9, "name": "Far"}]
        rows = [{"cell": 1, "file": None, "parts": [0]}]
        return {
            "name": "Far",
            "side": "fixed",
            "job": job,
            "cells": [1],
            "transforms": [ID],
            "parts": parts,
            "rows": rows,
        }

    def test_shell_outside_the_free_body_is_left_out(self):  # a second group far from the air
        without = groups(self.meshed([self.ring_3d(self.TWELVE, ())], free=[self.air_3d(self.BOX)], dim=3))[20][1]
        both = [self.ring_3d(self.TWELVE, ()), self.far_group()]
        found = groups(self.meshed(both, free=[self.air_3d(self.BOX)], dim=3))
        self.assertEqual(found[20][1], without)
        self.assertEqual(found[9][1], groups(self.meshed([self.far_group()], dim=3))[9][1])

    def test_free_object_and_excitation_on_its_face(self):
        write_face(self.geo("outer.brep"), corners=[(-30, -30, 10), (30, -30, 10), (30, 30, 10), (-30, 30, 10)])
        surface = {"smat_id": 50, "name": "Outer", "mat_id": 20, "files": ["geometry/outer.brep"]}
        mesh = self.meshed([self.ring_3d(self.TWELVE, ())], free=[self.air_3d(self.BOX, surfaces=[surface])], dim=3)
        name, count, face = surface_group(mesh, 50)
        self.assertEqual(name, "Outer")
        self.assertGreater(count, 0)
        self.assertAlmostEqual(face, 60 * 60, delta=1e-6)
        self.assertIn("SMAT_ID     50  Outer", self.result.stdout)

    def test_two_free_bodies_touching(self):  # two boxes side by side, a copy inside each
        write_boxes(self.geo("cubes.brep"), (-12, -2, -2, 4, 4, 4))
        job = {"volumes": [{"mat_id": 1, "name": "Cube", "file": "geometry/cubes.brep", "size": 1.5}]}
        job.update(surfaces=[], sizes=[])
        transforms = [ID, translation(20)]
        group = {
            "name": "Cubes",
            "side": "fixed",
            "job": job,
            "cells": [1],
            "transforms": transforms,
            "parts": self.IRON,
            "rows": [{"cell": 1, "file": None, "parts": [0, 0]}],
        }
        write_boxes(self.geo("a.brep"), (-20, -10, -10, 20, 20, 20))
        write_boxes(self.geo("b.brep"), (0, -10, -10, 20, 20, 20))
        bodies = [
            {"mat_id": 20, "name": "AirA", "file": "geometry/a.brep", "size": 6.0},
            {"mat_id": 21, "name": "AirB", "file": "geometry/b.brep", "size": 6.0},
        ]
        free = {"side": "fixed", "job": {"volumes": bodies, "surfaces": [], "sizes": []}}
        mesh = self.meshed([group], free=[free], dim=3)
        self.assertAlmostEqual(shared_area(mesh, 20, 21), 20 * 20, delta=1e-6)
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertEqual({k: v[0] for k, v in groups(mesh).items() if k >= 20}, {20: "AirA", 21: "AirB"})

    def cube(self):
        return self.box_group((-2, -2, -2, 4, 4, 4), [ID], size=2.0)

    SIZED = (-8, -8, -8, 16, 16, 16)

    def test_free_size_is_used(self):  # size 1 against size 4
        fine = groups(self.meshed([self.cube()], free=[self.air_3d(self.SIZED, size=1.0)], dim=3))[20][1]
        coarse = groups(self.meshed([self.cube()], free=[self.air_3d(self.SIZED, size=4.0)], dim=3))[20][1]
        self.assertGreater(fine, 2 * coarse)

    def test_mesh_size_on_a_free_face_is_used(self):  # build's size fields act on the free surface mesh
        plain = groups(self.meshed([self.cube()], free=[self.air_3d(self.SIZED, size=4.0)], dim=3))[20][1]
        free = self.air_3d(self.SIZED, size=4.0)
        write_face(self.geo("top.brep"), corners=[(-8, -8, 8), (8, -8, 8), (8, 8, 8), (-8, 8, 8)])
        free["job"]["sizes"] = [{"name": "Top", "size": 1.0, "files": ["geometry/top.brep"]}]
        self.assertGreater(groups(self.meshed([self.cube()], free=[free], dim=3))[20][1], plain)

    MIRROR_X = [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

    def assert_refused(self, result, text):
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(text, result.stderr)
        self.assertFalse(os.path.exists(self.mesh_file()))

    def test_two_groups_touching_inside_a_free_object_are_refused(self):  # the second is the mirror of the first
        a = self.box_group((-2, -2, -2, 2, 4, 4), [ID], size=1.0, file="a_box.brep")
        b = dict(self.box_group((-2, -2, -2, 2, 4, 4), [self.MIRROR_X], size=1.0, file="b_box.brep"), name="Other")
        self.assert_refused(self.run_job([a, b], free=[self.air_3d(self.SIZED, size=4.0)], dim=3), "in one group")

    def test_two_groups_touching_inside_a_free_object_are_refused_2d(self):
        write_rects(self.geo("a_rect.brep"), (-2, -2, 2, 4))
        a = self.sector_group((10, 20, 0, 30), [ID], self.IRON, size=1.0)
        a["job"]["bodies"][0]["file"] = "geometry/a_rect.brep"
        b = dict(self.sector_group((10, 20, 0, 30), [mirror_line(90)], self.IRON, size=1.0), name="Other")
        b["job"]["bodies"][0]["file"] = "geometry/a_rect.brep"
        write_rects(self.geo("air.brep"), (-8, -8, 16, 16))
        self.assert_refused(self.run_job([a, b], free=[self.air_2d(size=4.0)]), "in one group")

    def test_two_groups_touching_with_different_meshes_are_refused(self):  # no facet of one coincides with the other
        a = self.box_group((-2, -2, -2, 2, 4, 4), [ID], size=1.0, file="a_box.brep")
        b = dict(self.box_group((0, -2, -2, 2, 4, 4), [ID], size=0.7, file="b_box.brep"), name="Other")
        self.assert_refused(self.run_job([a, b], free=[self.air_3d(self.SIZED, size=4.0)], dim=3), "limit of the tool")

    def test_a_group_inside_the_solid_of_another_is_refused(self):  # its inside would be filled with air
        a = self.box_group((-5, -5, -5, 10, 10, 10), [ID], size=3.0, file="a_box.brep")
        b = dict(self.box_group((-1, -1, -1, 2, 2, 2), [ID], size=1.0, file="b_box.brep"), name="Other")
        self.assert_refused(self.run_job([a, b], free=[self.air_3d(self.SIZED, size=4.0)], dim=3), "limit of the tool")

    def test_free_object_inside_a_copy_is_refused(self):
        group = self.box_group((-10, -10, -10, 20, 20, 20), [ID], size=6.0)
        free = self.air_3d((-2, -2, -2, 4, 4, 4), size=2.0)
        self.assert_refused(self.run_job([group], free=[free], dim=3), "does not fit")

    def test_free_object_inside_a_copy_is_refused_2d(self):
        write_rects(self.geo("big.brep"), (-10, -10, 20, 20))
        group = self.sector_group((10, 20, 0, 30), [ID], self.IRON, size=6.0)
        group["job"]["bodies"][0]["file"] = "geometry/big.brep"
        write_rects(self.geo("air.brep"), (-2, -2, 4, 4))
        self.assert_refused(self.run_job([group], free=[self.air_2d(size=2.0)]), "does not fit")

    def test_free_object_in_the_bore_of_the_copies_is_meshed(self):  # inside the ring of copies, but not inside a copy
        mesh = self.meshed([self.ring_3d(self.TWELVE, ())], free=[self.air_3d((-5, -5, 1, 10, 10, 3), size=2.0)], dim=3)
        self.assertEqual(sorted(groups(mesh)), [7, 20])
        self.assertAlmostEqual(area_or_volume_of_air(mesh), 10 * 10 * 3, delta=1e-6)

    def test_copy_around_a_cavity_of_the_free_object_is_refused(self):  # its cavity has no air, the cavity is not free
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            whole = gmsh.model.occ.addBox(-30, -30, -30, 60, 60, 60)
            cavity = gmsh.model.occ.addBox(-2, -2, -2, 4, 4, 4)
            gmsh.model.occ.cut([(3, whole)], [(3, cavity)])
            gmsh.model.occ.synchronize()
            gmsh.write(self.geo("air.brep"))
        finally:
            gmsh.finalize()
        free = {"side": "fixed", "job": {"volumes": [dict(self.AIR, size=8.0)], "surfaces": [], "sizes": []}}
        r = self.run_job([self.box_group((-5, -5, -5, 10, 10, 10), [ID], size=4.0)], free=[free], dim=3)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("limit of the tool", r.stderr)

    def test_structured_free_object_is_a_limit_of_the_tool(self):
        free = self.air_3d(self.BOX)
        free["job"]["transfinite"] = {"bodies": [{"name": "Air", "mat_id": 20, "corner_files": []}], "edges": []}
        r = self.run_job([self.ring_3d(self.TWELVE, ())], free=[free], dim=3)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("limit of the tool", r.stderr)
        self.assertIn("Air", r.stderr)

    def test_copy_through_the_free_surface_is_a_limit_of_the_tool(self):  # never a silent wrong mesh
        r = self.run_job([self.ring_3d(self.TWELVE, ())], free=[self.air_3d((-30, -30, 2, 60, 60, 15))], dim=3)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("limit of the tool", r.stderr)
        self.assertFalse(os.path.exists(self.mesh_file()))

    def strand_group(self, cylinder, transforms, size=0.8):
        """A 3D group of one cell, the cylinder (x, y, z, height, radius)."""
        write_cylinders(self.geo("strand.brep"), cylinder)
        job = {"volumes": [{"mat_id": 1, "name": "Strand", "file": "geometry/strand.brep", "size": size}]}
        job.update(surfaces=[], sizes=[])
        rows = [{"cell": 1, "file": None, "parts": [0] * len(transforms)}]
        group = {"name": "Strands", "side": "fixed", "job": job, "cells": [1], "transforms": transforms}
        return dict(group, parts=self.IRON, rows=rows)

    STRANDS = [translation(8 * k) for k in range(3)]
    STRAND = (0, 0, 0, 10, 1)  # z from 0 to 10
    STRAND_BOX = (-5, -5, 0, 30, 10, 10)

    def strands_in_air(self, **air):
        return [self.strand_group(self.STRAND, self.STRANDS)], [self.air_3d(self.STRAND_BOX, **air)]

    def test_strands_ending_on_the_air_end_planes(self):
        frozen = frozen_facets(self.meshed([self.strand_group(self.STRAND, self.STRANDS)], dim=3))
        strands, free = self.strands_in_air(size=3.0)
        mesh = self.meshed(strands, free=free, dim=3)
        kept, _ = boundary_of(mesh, 20)
        ends = {f for f in frozen if all(abs(p[2]) < 1e-6 for p in f) or all(abs(p[2] - 10) < 1e-6 for p in f)}
        self.assertTrue(ends)
        self.assertLessEqual(frozen - ends, kept)
        self.assertEqual(ends & kept, set())
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertAlmostEqual(volume(mesh) / (30 * 10 * 10), 1, delta=1e-6)

    def test_air_ring_flush_against_the_copies(self):  # the air's inner face is exactly the copies' outer face
        group = self.ring_3d(self.TWELVE, ())
        group["job"]["volumes"][0]["size"] = 2.0
        write_ring(self.geo("air.brep"), 20, 30, 0, 5)
        free = {"side": "fixed", "job": {"volumes": [dict(self.AIR, size=4.0)], "surfaces": [], "sizes": []}}
        mesh = self.meshed([group], free=[free], dim=3)
        self.assertAlmostEqual(shared_area(mesh, 7, 20) / (2 * math.pi * 20 * 5), 1, delta=1e-3)
        self.assertEqual(faces_in_three(mesh), 0)

    def test_stator_running_the_full_height_splits_the_air(self):  # bore and outside, both in the Air group
        group = self.ring_3d(self.TWELVE, ())
        group["job"]["volumes"][0]["size"] = 2.0
        mesh = self.meshed([group], free=[self.air_3d((-30, -30, 0, 60, 60, 5), size=5.0)], dim=3)
        self.assertGreater(groups(mesh)[20][1], 0)
        self.assertEqual(regions_of(mesh, 20), 2)
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertAlmostEqual(volume(mesh) / (60 * 60 * 5), 1, delta=1e-6)

    def test_copy_crossing_a_curved_face_is_refused(self):
        write_cylinders(self.geo("air.brep"), (0, 0, -5, 15, 15))  # the ring's outer part is outside the cylinder
        free = {"side": "fixed", "job": {"volumes": [dict(self.AIR, size=4.0)], "surfaces": [], "sizes": []}}
        r = self.run_job([self.ring_3d(self.TWELVE, ())], free=[free], dim=3)
        self.assert_refused(r, "limit of the tool")
        self.assertIn("curved face", r.stderr)

    def test_copies_covering_part_of_a_curved_face_are_refused(self):  # flush, but on half of the turn
        write_ring(self.geo("air.brep"), 20, 30, 0, 5)
        free = {"side": "fixed", "job": {"volumes": [dict(self.AIR, size=4.0)], "surfaces": [], "sizes": []}}
        r = self.run_job([self.ring_3d(self.TWELVE[:6], ())], free=[free], dim=3)
        self.assert_refused(r, "limit of the tool")
        self.assertIn("curved face", r.stderr)

    def test_copy_passing_through_a_planar_face_is_refused(self):  # it does not end on the plane
        r = self.run_job([self.ring_3d(self.TWELVE, ())], free=[self.air_3d((-30, -30, 1, 60, 60, 3))], dim=3)
        self.assert_refused(r, "limit of the tool")

    def test_strand_flush_against_the_air_from_outside(self):  # its end cap is the air's boundary
        below = (0, 0, -5, 5, 1)
        frozen = frozen_facets(self.meshed([self.strand_group(below, self.STRANDS)], dim=3))
        strands = [self.strand_group(below, self.STRANDS)]
        mesh = self.meshed(strands, free=[self.air_3d(self.STRAND_BOX, size=3.0)], dim=3)
        kept, _ = boundary_of(mesh, 20)
        caps = {f for f in frozen if all(abs(p[2]) < 1e-6 for p in f)}
        self.assertTrue(caps)
        self.assertLessEqual(caps, kept)
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertAlmostEqual(area_or_volume_of_air(mesh) / (30 * 10 * 10), 1, delta=1e-6)

    def test_copy_ending_on_the_face_between_two_free_bodies(self):  # end cap of the body it is in, flush for the other
        group = self.box_group((-5, -2, -2, 5, 4, 4), [ID], size=1.0)
        write_boxes(self.geo("a.brep"), (-20, -10, -10, 20, 20, 20))
        write_boxes(self.geo("b.brep"), (0, -10, -10, 20, 20, 20))
        bodies = [
            {"mat_id": 20, "name": "AirA", "file": "geometry/a.brep", "size": 6.0},
            {"mat_id": 21, "name": "AirB", "file": "geometry/b.brep", "size": 6.0},
        ]
        free = {"side": "fixed", "job": {"volumes": bodies, "surfaces": [], "sizes": []}}
        mesh = self.meshed([group], free=[free], dim=3)
        self.assertAlmostEqual(shared_area(mesh, 20, 21), 20 * 20 - 4 * 4, delta=1e-6)
        self.assertAlmostEqual(shared_area(mesh, 7, 21), 4 * 4, delta=1e-6)
        self.assertEqual(faces_in_three(mesh), 0)

    def test_excitation_on_a_face_with_holes(self):  # the rebuilt face keeps its physical group
        write_face(self.geo("top.brep"), corners=[(-5, -5, 10), (25, -5, 10), (25, 5, 10), (-5, 5, 10)])
        surface = {"smat_id": 50, "name": "Top", "mat_id": 20, "files": ["geometry/top.brep"]}
        strands, free = self.strands_in_air(size=3.0, surfaces=[surface])
        mesh = self.meshed(strands, free=free, dim=3)
        name, count, face = surface_group(mesh, 50)
        self.assertEqual(name, "Top")
        self.assertGreater(count, 0)
        self.assertAlmostEqual(face / (30 * 10 - 3 * math.pi), 1, delta=1e-2)

    def test_mesh_size_on_a_face_with_holes_is_used(self):
        strands, free = self.strands_in_air(size=4.0)
        plain = groups(self.meshed(strands, free=free, dim=3))[20][1]
        strands, free = self.strands_in_air(size=4.0)
        write_face(self.geo("top.brep"), corners=[(-5, -5, 10), (25, -5, 10), (25, 5, 10), (-5, 5, 10)])
        free[0]["job"]["sizes"] = [{"name": "Top", "size": 1.0, "files": ["geometry/top.brep"]}]
        self.assertGreater(groups(self.meshed(strands, free=free, dim=3))[20][1], 1.5 * plain)

    def test_size_of_a_free_object_with_holes_is_used(self):
        strands, free = self.strands_in_air(size=1.5)
        fine = groups(self.meshed(strands, free=free, dim=3))[20][1]
        strands, free = self.strands_in_air(size=4.0)
        self.assertGreater(fine, 2 * groups(self.meshed(strands, free=free, dim=3))[20][1])

    def cap_is_kept_at_a_curved_rim(self, group, air, air_volume, size):
        """The mesh of group and a free cylinder air (x, y, z, height, radius) on its top end, whose lateral face the
        copies reach only along its rim: their end caps at z = 0 stay frozen, the air is a valid mesh of its volume."""
        frozen = frozen_facets(self.meshed([group()], dim=3))
        write_cylinders(self.geo("air.brep"), air)
        free = {"side": "fixed", "job": {"volumes": [dict(self.AIR, size=size)], "surfaces": [], "sizes": []}}
        mesh = self.meshed([group()], free=[free], dim=3)
        kept, _ = boundary_of(mesh, 20)
        caps = {f for f in frozen if all(abs(p[2]) < 1e-6 for p in f)}
        self.assertTrue(caps)
        self.assertLessEqual(caps, kept)
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertEqual(mesh_check_3d(mesh, (), ())[1], 0)
        self.assertAlmostEqual(area_or_volume_of_air(mesh) / air_volume, 1, delta=2e-2)
        return mesh

    def test_air_cylinder_on_a_copy(self):  # a whole end flush: the lateral face is reached only along its rim
        group = lambda: self.strand_group((0, 0, -5, 5, 1), [ID], size=0.2)  # noqa: E731 - rebuilt for each run
        self.cap_is_kept_at_a_curved_rim(group, (0, 0, 0, 5, 1), math.pi * 5, 0.3)

    def test_air_cylinder_on_a_turned_copy(self):  # no node of the copy at the rim's own vertex: that one moves to one
        group = lambda: self.strand_group((0, 0, -5, 5, 1), [rotation(17)], size=0.2)  # noqa: E731 - as above
        self.cap_is_kept_at_a_curved_rim(group, (0, 0, 0, 5, 1), math.pi * 5, 0.3)

    def sector_solid_group(self, sector, transforms, size=1.0):
        write_sector_solids(self.geo("wedge.brep"), sector)
        job = {"volumes": [{"mat_id": 1, "name": "Wedge", "file": "geometry/wedge.brep", "size": size}]}
        job.update(surfaces=[], sizes=[])
        rows = [{"cell": 1, "file": None, "parts": [0] * len(transforms)}]
        group = {"name": "Wedges", "side": "fixed", "job": job, "cells": [1], "transforms": transforms}
        return dict(group, parts=self.IRON, rows=rows)

    def test_copy_ending_on_a_planar_end_reaching_part_of_the_rim(self):  # the rest of the rim is still the air's
        group = lambda: self.sector_solid_group((3, 5, 0, 60, -3, 0), [ID, rotation(120)])  # noqa: E731 - as above
        self.cap_is_kept_at_a_curved_rim(group, (0, 0, 0, 10, 5), math.pi * 25 * 10, 1.5)

    def test_air_filling_the_bore_of_the_copies(self):  # its whole lateral face lies on theirs: dropped, nothing open
        group = self.ring_3d(self.TWELVE, ())
        write_cylinders(self.geo("air.brep"), (0, 0, 0, 5, 10))
        free = {"side": "fixed", "job": {"volumes": [dict(self.AIR, size=2.0)], "surfaces": [], "sizes": []}}
        mesh = self.meshed([group], free=[free], dim=3)
        self.assertAlmostEqual(area_or_volume_of_air(mesh) / (math.pi * 10**2 * 5), 1, delta=2e-2)
        self.assertEqual(faces_in_three(mesh), 0)

    def test_stator_flush_against_the_cylinder_of_the_air(self):  # the air's outer face is the copies' outer face too
        group = self.ring_3d(self.TWELVE, ())
        group["job"]["volumes"][0]["size"] = 2.0
        write_cylinders(self.geo("air.brep"), (0, 0, 0, 5, 20))
        free = {"side": "fixed", "job": {"volumes": [dict(self.AIR, size=4.0)], "surfaces": [], "sizes": []}}
        mesh = self.meshed([group], free=[free], dim=3)
        self.assertEqual(regions_of(mesh, 20), 1)
        self.assertAlmostEqual(area_or_volume_of_air(mesh) / (math.pi * 10**2 * 5), 1, delta=2e-2)
        self.assertEqual(faces_in_three(mesh), 0)

    def test_copy_in_the_corner_of_the_air(self):  # its faces cover part of three of the air's, each touching its rim
        group = self.box_group((0, 0, 0, 2, 2, 2), [ID], size=0.8)
        mesh = self.meshed([group], free=[self.air_3d((0, 0, 0, 10, 10, 10), size=2.5)], dim=3)
        self.assertAlmostEqual(area_or_volume_of_air(mesh), 10**3 - 2**3, delta=1e-6)
        self.assertAlmostEqual(shared_area(mesh, 7, 20), 3 * 2 * 2, delta=1e-6)
        self.assertEqual(faces_in_three(mesh), 0)

    def test_hex_copies_ending_on_a_planar_face(self):  # end caps that are quads are removed, lateral ones get pyramids
        group = self.hex_group([translation(3 * k) for k in range(3)])
        mesh = self.meshed([group], free=[self.air_3d((-3, -3, 0, 13, 7, 7), size=1.5)], dim=3)
        self.assertLessEqual({4, 7}, set(boundary_of(mesh, 20)[1]))
        self.assertEqual(faces_in_three(mesh), 0)
        self.assertEqual(mesh_check_3d(mesh, (), ())[1], 0)

    def test_hex_copies_flush_against_a_planar_face(self):  # the end caps, quads, carry pyramids into the air
        group = self.hex_group([translation(3 * k) for k in range(3)])
        mesh = self.meshed([group], free=[self.air_3d((-3, -3, 1, 13, 7, 7), size=1.5)], dim=3)
        self.assertIn(7, set(boundary_of(mesh, 20)[1]))
        self.assertAlmostEqual(shared_area(mesh, 7, 20), 3, delta=1e-6)  # the bases of the pyramids on the three caps
        self.assertEqual(faces_in_three(mesh), 0)

    def test_excitation_wholly_under_copies_is_refused(self):
        write_face(self.geo("bottom.brep"), corners=[(-5, -5, 0), (25, -5, 0), (25, 5, 0), (-5, 5, 0)])
        surface = {"smat_id": 50, "name": "Under", "mat_id": 20, "files": ["geometry/bottom.brep"]}
        group = self.box_group((-5, -5, -5, 30, 10, 5), [ID], size=2.0)
        free = self.air_3d(self.STRAND_BOX, size=3.0, surfaces=[surface])
        self.assert_refused(self.run_job([group], free=[free], dim=3), "does not fit")

    def rect_group(self, rect, transforms, size=1.0, file="cell_rect.brep"):
        write_rects(self.geo(file), rect)
        group = self.sector_group((10, 20, 0, 30), transforms, self.IRON, size=size)
        group["job"]["bodies"][0]["file"] = f"geometry/{file}"
        return group

    def test_2d_copies_reaching_a_straight_edge_of_the_air(self):
        group = self.rect_group((5, 0, 4, 6), [translation(10 * k) for k in range(3)])
        write_rects(self.geo("air.brep"), (0, 0, 40, 20))
        mesh = self.meshed([group], free=[self.air_2d(size=3.0)])
        self.assertAlmostEqual(area(mesh) / (40 * 20), 1, delta=1e-3)
        self.assertEqual(edges_in_three(mesh), 0)
        self.assertEqual(sorted(groups(mesh)), [7, 20])

    def test_2d_copies_flush_against_a_straight_edge_from_outside(self):
        group = self.rect_group((5, -6, 4, 6), [translation(10 * k) for k in range(3)])
        write_rects(self.geo("air.brep"), (0, 0, 40, 20))
        mesh = self.meshed([group], free=[self.air_2d(size=3.0)])
        self.assertAlmostEqual(area(mesh, 20) / (40 * 20), 1, delta=1e-6)
        self.assertAlmostEqual(shared_area(mesh, 7, 20), 3 * 4, delta=1e-6)
        self.assertEqual(edges_in_three(mesh), 0)

    def test_2d_copy_over_a_whole_edge_of_the_air(self):  # the edge is dropped, the copy's edge bounds the air
        group = self.rect_group((0, -6, 40, 6), [ID])
        write_rects(self.geo("air.brep"), (0, 0, 40, 20))
        mesh = self.meshed([group], free=[self.air_2d(size=3.0)])
        self.assertAlmostEqual(shared_area(mesh, 7, 20), 40, delta=1e-6)
        self.assertEqual(edges_in_three(mesh), 0)

    def test_2d_air_filling_the_bore_of_the_copies(self):  # every edge dropped: the air has no surface of its own
        group = self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON, size=1.0)
        write_disc(self.geo("air.brep"), 10)
        mesh = self.meshed([group], free=[self.air_2d(size=2.0)])
        self.assertAlmostEqual(area(mesh, 20) / (math.pi * 10**2), 1, delta=5e-3)
        self.assertEqual(edges_in_three(mesh), 0)

    def test_2d_copy_covering_part_of_a_curved_edge_is_refused(self):
        group = self.sector_group((50, 60, 0, 20), self.spaced(), self.IRON, size=2.0)
        write_disc(self.geo("air.brep"), self.DISC)
        r = self.run_job([group], free=[self.air_2d(size=4.0)])
        self.assert_refused(r, "limit of the tool")
        self.assertIn("curved face", r.stderr)

    DISC = 50

    def spaced(self):
        return [rotation(30 * k) for k in range(12)]

    def test_2d_disc_with_holes(self):  # 2D copies inside a drawn disc
        write_disc(self.geo("air.brep"), self.DISC)
        mesh = self.meshed([self.sector_group((20, 30, 0, 20), self.spaced(), self.IRON)], free=[self.air_2d(size=2.0)])
        self.assertAlmostEqual(area(mesh) / (math.pi * self.DISC**2), 1, delta=1e-3)
        self.assertEqual(mesh_check(mesh, [self.DISC])[1:], (0, 0))
        self.assertEqual(sorted(groups(mesh)), [7, 20])

    def test_2d_free_air_shares_the_nodes_of_the_copies(self):
        write_disc(self.geo("air.brep"), self.DISC)
        mesh = self.meshed([self.sector_group((20, 30, 0, 20), self.spaced(), self.IRON)], free=[self.air_2d()])
        outline = 12 * (2 * 10 + math.radians(20) * (20 + 30))
        self.assertAlmostEqual(shared_area(mesh, 7, 20) / outline, 1, delta=1e-2)

    def test_2d_ring_of_copies_gives_bore_and_outside(self):  # copies form an annulus: two regions, one Air group
        write_disc(self.geo("air.brep"), 30)
        group = self.sector_group((10, 20, 0, 30), self.TWELVE, self.IRON, size=1.0)
        mesh = self.meshed([group], free=[self.air_2d(size=1.0)])
        self.assertAlmostEqual(area(mesh, 20) / (math.pi * (30**2 - 20**2 + 10**2)), 1, delta=1e-3)
        self.assertEqual(mesh_check(mesh, [30])[1:], (0, 0))
        self.assertEqual(sorted(groups(mesh)), [7, 20])

    def test_zx_copies_in_free_air(self):  # 2D ZX job: Mirror z = 0, a drawn rectangle of air
        write_plane_rects(self.geo("zx.brep"), [(2, 1, 2, 2)], plane="ZX")
        write_plane_rects(self.geo("air.brep"), [(0, -6, 10, 12)], plane="ZX")
        group = self.sector_group((10, 20, 0, 30), [ID, MIRROR_Z], self.IRON, size=0.5)
        group["job"]["bodies"][0]["file"] = "geometry/zx.brep"
        mesh = self.meshed([group], free=[self.air_2d(size=1.5)])
        self.assertEqual(y_range(mesh), (0, 0))
        self.assertAlmostEqual(area(mesh) / 120, 1, delta=1e-3)
        self.assertEqual(sorted(groups(mesh)), [7, 20])
        xyz, found = read_mesh(mesh)
        t = xyz[found[2]]
        normals = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        self.assertEqual(len(np.unique(np.sign(normals[:, 1]))), 1)  # copies and air are turned the same way

    def test_free_air_on_the_moving_side(self):  # a free job takes the boundary of its own side only
        stator = self.sector_group((35, 45, 0, 20), self.spaced(), [{"mat_id": 5, "name": "S"}])
        rotor = self.sector_group((10, 15, 0, 20), self.spaced(), [{"mat_id": 6, "name": "R"}], "Rotor", side="moving")
        write_disc(self.geo("air.brep"), 30)  # holds the rotor's copies; the stator's are outside it
        mesh = self.meshed([stator, rotor], free=[self.air_2d(side="moving")])
        rotor_area = 12 * math.radians(20) / 2 * (15**2 - 10**2)
        self.assertAlmostEqual(area(mesh, 20) / (math.pi * 30**2 - rotor_area), 1, delta=1e-2)

    def test_sliding_with_free_air_outside_the_band(self):  # Task 3's motor, plus copies in a free ring outside it
        groups_3d, slide = self.slide_groups_3d()
        write_sector_solids(self.geo("coil.brep"), (35, 40, 0, 20, -3, 3))
        job = {"volumes": [{"mat_id": 1, "name": "Coil", "file": "geometry/coil.brep", "size": 3.0}]}
        job.update(surfaces=[], sizes=[])
        rows = [{"cell": 1, "file": None, "parts": [0] * 12}]
        parts = [{"mat_id": 8, "name": "Coil"}]
        coil = {"name": "Coil", "side": "fixed", "job": job, "cells": [1], "transforms": self.spaced()}
        groups_3d.append(dict(coil, parts=parts, rows=rows))
        write_ring(self.geo("air.brep"), 32, 44, -5, 5)
        free = {"side": "fixed", "job": {"volumes": [dict(self.AIR, size=4.0)], "surfaces": [], "sizes": []}}
        r = self.run_job(groups_3d, free=[free], slide=slide, dim=3)
        self.assertEqual(r.returncode, 0, r.stderr)
        fixed, rotor = self.mesh_file(), self.rotor_file()
        self.assertEqual(sorted(slide_nodes(fixed, 20)), sorted(slide_nodes(rotor, 20)))
        self.assertIn("Air", {v[0] for v in groups(fixed).values()})
        self.assertEqual(faces_in_three(fixed), 0)


if __name__ == "__main__":
    unittest.main()
