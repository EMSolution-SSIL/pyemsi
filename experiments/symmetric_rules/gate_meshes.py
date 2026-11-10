"""Gate meshes for an EMSolution solve: two group jobs written to JSON and meshed by mesher.py.

(a) a small 3D motor: stator iron, coils and slot air over z 0..50, the air gap band, the rotor and a free air ring
    over z 0..75 (all mirrored at z = 0, then rotated), a Rotational sliding interface (the ring is drawn over the stator);
(b) hexahedral coils pressed on tetrahedral iron, in a free air cylinder (hexahedra, tetrahedra and pyramids).

Run: pixi run -e addon python experiments/symmetric_rules/gate_meshes.py
Output: C:\\Users\\hamed\\Desktop\\delme\\rules_gate\\<mesh>\\ (job.json, geometry/*.brep, pre_geom.msh, rotor_mesh.msh, mesh.unv)
"""

import collections
import json
import math
import os
import shutil
import subprocess
import sys

import gmsh
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MESHER = os.path.join(HERE, "..", "..", "freecad_addon", "emsolution", "mesher.py")
OUT = r"C:\Users\hamed\Desktop\delme\rules_gate"
MIRROR_Z = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1]
TYPES = {4: "tetrahedra", 5: "hexahedra", 6: "prisms", 7: "pyramids"}


def rotation(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def compose(a, b):
    """b first, then a."""
    return [sum(a[4 * i + k] * b[4 * k + j] for k in range(4)) for i in range(4) for j in range(4)]


ID = rotation(0)


def sector(r0, r1, a0, a1, z0, z1):
    """The solid between radii r0 < r1 and angles a0..a1 (degrees), z0..z1; returns its dimtag."""
    occ = gmsh.model.occ
    p = lambda r, a: occ.addPoint(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), z0)  # noqa: E731
    c = occ.addPoint(0, 0, z0)
    p00, p01, p10, p11 = p(r0, a0), p(r0, a1), p(r1, a0), p(r1, a1)
    inner = occ.addCircleArc(p00, c, p01)
    outer = occ.addCircleArc(p10, c, p11)
    loop = occ.addCurveLoop([occ.addLine(p00, p10), outer, -occ.addLine(p01, p11), -inner])
    face = occ.addPlaneSurface([loop])
    return [t for t in occ.extrude([(2, face)], 0, 0, z1 - z0) if t[0] == 3][0]


def box(x, y, z, dx, dy, dz):
    return (3, gmsh.model.occ.addBox(x, y, z, dx, dy, dz))


def brep(path, build):
    """Write the shape build() makes in a fresh Gmsh model to path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        build()
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def cut(whole, *holes):
    gmsh.model.occ.cut([whole], list(holes))


def piece(folder, name, build, mat_id, label, size):
    """Write geometry/<name>.brep and return the job's volume entry."""
    brep(os.path.join(folder, "geometry", name + ".brep"), build)
    return {"mat_id": mat_id, "name": label, "file": f"geometry/{name}.brep", "size": size}


def line_files(folder, prefix, lines):
    """Write one BREP per ((x, y, z), (x, y, z)) line; return their relative paths."""
    files = []
    for k, (p, q) in enumerate(lines):
        rel = f"geometry/{prefix}_{k}.brep"
        brep(
            os.path.join(folder, rel),
            lambda p=p, q=q: gmsh.model.occ.addLine(gmsh.model.occ.addPoint(*p), gmsh.model.occ.addPoint(*q)),
        )
        files.append(rel)
    return files


def box_edges(x, y, z, dx, dy, dz):
    """The 12 edges of a box, as three lists by direction (x, y, z)."""
    corners = [(x + i * dx, y + j * dy, z + k * dz) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    out = ([], [], [])
    for a, p in enumerate(corners):
        for q in corners[a + 1 :]:
            diff = [i for i in range(3) if p[i] != q[i]]
            if len(diff) == 1:
                out[diff[0]].append((p, q))
    return out


def structured_layer(folder, name, r0, r1, top, mat_id, label, arcs=12, ups=15):
    """A one-element-thick structured layer: the sector r0..r1, 0..30 degrees, z 0..top, as its own cell object of 6
    faces. Returns (volume entry, transfinite edges): arcs divisions per cell around Z, 1 across, ups along z."""
    vol = piece(folder, name, lambda: sector(r0, r1, 0, 30, 0, top), mat_id, label, 2.0)
    pt = lambda r, a, z: (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), z)  # noqa: E731
    files = {"Arc": [], "Radial": [], "Up": []}

    def add(kind, build):
        rel = f"geometry/{name}_{kind}_{len(files[kind])}.brep"
        brep(os.path.join(folder, rel), build)
        files[kind].append(rel)

    occ = lambda: gmsh.model.occ  # noqa: E731
    for r in (r0, r1):
        for z in (0, top):
            add("Arc", lambda r=r, z=z: occ().addCircle(0, 0, z, r, angle1=0, angle2=math.pi / 6))
    for a in (0, 30):
        for z in (0, top):
            add("Radial", lambda a=a, z=z: occ().addLine(occ().addPoint(*pt(r0, a, z)), occ().addPoint(*pt(r1, a, z))))
        for r in (r0, r1):
            add("Up", lambda a=a, r=r: occ().addLine(occ().addPoint(*pt(r, a, 0)), occ().addPoint(*pt(r, a, top))))
    nodes = {"Arc": arcs + 1, "Radial": 2, "Up": ups + 1}
    edges = [
        dict(name=f"{label}{k}", nodes=nodes[k], distribution="Uniform", coef=1.0, files=f) for k, f in files.items()
    ]
    return vol, edges


def group(name, side, volumes, transforms, parts, rows, turns=None):
    cells = list(range(1, len(volumes) + 1))
    job = {"volumes": volumes, "surfaces": [], "sizes": []}
    rows = [{"cell": c, "file": None, "parts": r} for c, r in zip(cells, rows)]
    out = {"name": name, "side": side, "job": job, "cells": cells, "transforms": transforms, "parts": parts}
    out["rows"] = rows
    if turns:
        out["turns"] = turns
    return out


def counts(path):
    """{part name: {type name: count}} of the volume elements of a mesh file."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        out = {}
        for dim, tag in gmsh.model.getPhysicalGroups(3):
            name = gmsh.model.getPhysicalName(dim, tag) + f" ({tag})"
            found = collections.Counter()
            for ent in gmsh.model.getEntitiesForPhysicalGroup(dim, tag):
                types, tags, _ = gmsh.model.mesh.getElements(dim, ent)
                for t, e in zip(types, tags):
                    found[TYPES.get(t, f"type{t}")] += len(e)
            out[name] = dict(found)
        return out
    finally:
        gmsh.finalize()


def run(label, folder, job):
    """Write job.json, run mesher.py on it, print the report. Returns the total number of volume elements."""
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=1)
    print(f"\n===== {label} =====")
    r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
    print(*[x for x in r.stdout.splitlines() if x.strip() and not x.startswith("Info")], sep=chr(10))
    if r.returncode:
        print(r.stderr)
        raise SystemExit(f"{label}: mesher.py failed with {r.returncode}")
    total = 0
    for mesh in (job["mesh_file"], job.get("rotor_file")):
        if not mesh:
            continue
        print(f"-- {os.path.basename(mesh)}")
        by_type = collections.Counter()
        for part, found in counts(mesh).items():
            print(f"   {part:28s} " + ", ".join(f"{k} {v}" for k, v in sorted(found.items())))
            by_type.update(found)
        print("   total: " + ", ".join(f"{k} {v}" for k, v in sorted(by_type.items())) + f"  = {sum(by_type.values())}")
        total += sum(by_type.values())
    for line in r.stdout.splitlines():
        if "Poor elements" in line:
            print(line)
    print(f"{label}: {total} volume elements")
    return total


def fresh(name):
    folder = os.path.join(OUT, name)
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    return folder


def motor():
    """(a) 12 slots, 12 poles, sliding cylinder R 40, stack 2 x 50 mm."""
    folder = fresh("a_motor_z_mirror_sliding")
    L, R, T = 50, 40, 75  # stack half-length, sliding radius, half-height of the band, rotor and air
    transforms = [compose(rotation(30 * c), m) for c in range(12) for m in (ID, MIRROR_Z)]
    turn = [c for c in range(12) for _ in (0, 1)]  # the rotation of each transform

    def stator_iron():
        iron = sector(R + 2, 80, 0, 30, 0, L)
        cut(iron, sector(R + 2, 68, 6, 24, 0, L))

    def slot_air():
        slot = sector(R + 2, 68, 6, 24, 0, L)
        cut(slot, sector(R + 6, 66, 8, 22, 0, L))

    stator = [
        piece(folder, "stator_gap", lambda: sector(R + 1, R + 2, 0, 30, 0, T), 1, "Gap", 2.0),
        piece(folder, "stator_iron", stator_iron, 2, "StatorIron", 7.0),
        piece(folder, "stator_slot_air", slot_air, 3, "SlotAir", 5.0),
        piece(folder, "stator_coil", lambda: sector(R + 6, 66, 8, 22, 0, L), 4, "Coil", 5.0),
    ]
    layer, stator_edges = structured_layer(folder, "stator_layer", R, R + 1, T, 5, "StatorLayer")
    stator.append(layer)
    stator_parts = [{"mat_id": 1, "name": "StatorIron"}, {"mat_id": 2, "name": "Air"}]
    stator_parts += [{"mat_id": 11 + c, "name": f"Coil_{c + 1:02d}"} for c in range(12)]
    stator_rows = [[1] * 24, [0] * 24, [1] * 24, [2 + c for c in turn], [1] * 24]

    def rotor_air():
        air = sector(30, R - 1, 0, 30, 0, T)
        cut(air, sector(30, 38, 3, 27, 0, T))

    rotor = [
        piece(folder, "rotor_iron", lambda: sector(10, 30, 0, 30, 0, T), 1, "RotorIron", 10.0),
        piece(folder, "rotor_magnet", lambda: sector(30, 38, 3, 27, 0, T), 2, "Magnet", 6.0),
        piece(folder, "rotor_air", rotor_air, 3, "RotorAir", 5.0),
    ]
    layer, rotor_edges = structured_layer(folder, "rotor_layer", R - 1, R, T, 4, "RotorLayer")
    rotor.append(layer)
    rotor_parts = [{"mat_id": 3, "name": "RotorIron"}, {"mat_id": 7, "name": "RotorAir"}]
    rotor_parts += [{"mat_id": 4, "name": "MagnetN"}, {"mat_id": 5, "name": "MagnetS"}]
    rotor_rows = [[0] * 24, [2 + c % 2 for c in turn], [1] * 24, [1] * 24]
    groups = [
        group("Stator", "fixed", stator, transforms, stator_parts, stator_rows, turns=12),
        group("Rotor", "moving", rotor, transforms, rotor_parts, rotor_rows, turns=12),
    ]
    for g, edges, mat in ((groups[0], stator_edges, 5), (groups[1], rotor_edges, 4)):
        g["job"]["transfinite"] = {
            "bodies": [{"name": g["job"]["volumes"][-1]["name"], "mat_id": mat, "corner_files": []}],
            "edges": edges,
        }
        g["job"]["recombine"] = [mat]
    ring = piece(folder, "air_ring", lambda: sector_ring(R + 2, 110, -T, T), 2, "Air", 20.0)
    slide = {"name": "Slide", "kind": "rotational", "radius": float(R), "divisions": 144, "cross_divisions": 30}
    slide.update(slide_mat_id=6, full=True, z_range=[-T, T])
    free = {"side": "fixed", "job": {"volumes": [ring], "surfaces": [], "sizes": []}}
    job = {
        "model_name": "Model",
        "mesh_file": os.path.join(folder, "pre_geom.msh"),
        "rotor_file": os.path.join(folder, "rotor_mesh.msh"),
        "options": {},
        "symmetric": {"groups": groups, "free": [free], "slide": slide},
    }
    total = run("a_motor_z_mirror_sliding", folder, job)
    vols = check_mesh(job["mesh_file"])
    fixed_ids, moving_ids = (set(ids_of(job[k])) for k in ("mesh_file", "rotor_file"))
    print(
        f"   MAT_IDs fixed {sorted(fixed_ids)}, moving {sorted(moving_ids)}, in common {sorted(fixed_ids & moving_ids)}"
    )
    pi = math.pi
    slot = 12 * 2 * L * (pi * (68**2 - (R + 2) ** 2) * 18 / 360 - pi * (66**2 - (R + 6) ** 2) * 14 / 360)
    band = pi * ((R + 2) ** 2 - R**2) * 2 * T
    ring = pi * (110**2 - (R + 2) ** 2) * 2 * T - pi * (80**2 - (R + 2) ** 2) * 2 * L
    want = ring + band + slot
    print(
        f"   Air volume {vols['Air']:.0f}, wanted (ring - stator cells + band + slot air) {want:.0f}: {vols['Air'] / want:.4f}"
    )
    for path in (job["mesh_file"], job["rotor_file"]):
        quads, tris = cylinder_faces(path, R)
        print(f"   faces on the sliding cylinder, {os.path.basename(path)}: {quads} quads, {tris} triangles")
    return total


def sector_ring(inner, outer, z0, z1):
    whole = gmsh.model.occ.addCylinder(0, 0, z0, 0, 0, z1 - z0, outer)
    hole = gmsh.model.occ.addCylinder(0, 0, z0, 0, 0, z1 - z0, inner)
    gmsh.model.occ.cut([(3, whole)], [(3, hole)])


FACES = {  # volume element type -> (corner indices of its triangle faces, of its quad faces)
    4: ([(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)], []),
    5: ([], [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]),
    6: ([(0, 1, 2), (3, 4, 5)], [(0, 1, 4, 3), (1, 2, 5, 4), (0, 2, 5, 3)]),
    7: ([(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], [(0, 1, 2, 3)]),
}


def cylinder_faces(path, r):
    """(quads, triangles): the element faces with all their nodes on the cylinder of radius r about Z."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        nodes, xyz, _ = gmsh.model.mesh.getNodes()
        at = np.zeros((int(nodes.max()) + 1, 3))
        at[nodes.astype(int)] = np.reshape(xyz, (-1, 3))
        on = np.abs(np.hypot(at[:, 0], at[:, 1]) - r) < 1e-6 * r
        found = {4: set(), 3: set()}
        for typ, (tris, quads) in FACES.items():
            _, conn = gmsh.model.mesh.getElementsByType(typ)
            if not len(conn):
                continue
            conn = np.reshape(conn, (-1, gmsh.model.mesh.getElementProperties(typ)[3])).astype(int)
            for size, faces in ((3, tris), (4, quads)):
                for f in faces:
                    c = conn[:, list(f)]
                    c = c[on[c].all(axis=1)]
                    found[size].update(map(tuple, np.sort(c, axis=1)))
        return len(found[4]), len(found[3])
    finally:
        gmsh.finalize()


def ids_of(path):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        return [t for _, t in gmsh.model.getPhysicalGroups(3)]
    finally:
        gmsh.finalize()


def tet_volume(p):
    """The summed volume of the tetrahedra p[n, 4, 3]."""
    return abs(np.einsum("ij,ij->i", np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), p[:, 3] - p[:, 0])).sum() / 6


def check_mesh(path, expect=None):
    """Print the faces (triangles and quads) held by 3 or more elements; return the volume of each physical group."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        nodes, xyz, _ = gmsh.model.mesh.getNodes()
        at = np.zeros((int(nodes.max()) + 1, 3))
        at[nodes.astype(int)] = np.reshape(xyz, (-1, 3))
        faces, quads, vols = [], [], {}
        for dim, tag in gmsh.model.getPhysicalGroups(3):
            total = 0.0
            for ent in gmsh.model.getEntitiesForPhysicalGroup(dim, tag):
                types, _, conn = gmsh.model.mesh.getElements(dim, ent)
                for t, c in zip(types, conn):
                    if t == 4:
                        c = np.reshape(c, (-1, 4)).astype(int)
                        p = at[c]
                        total += tet_volume(p)
                        for k in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
                            faces.append(np.sort(c[:, k], axis=1))
                    elif t == 5:
                        c = np.reshape(c, (-1, 8)).astype(int)
                        for k in ((0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6), (0, 5, 1, 6)):
                            total += tet_volume(at[c[:, k]])
                        for k in ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
                            quads.append(np.sort(c[:, k], axis=1))
                    elif t == 7:
                        c = np.reshape(c, (-1, 5)).astype(int)
                        for k in ((0, 1, 2, 4), (0, 2, 3, 4)):
                            total += tet_volume(at[c[:, k]])
                        for k in ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)):
                            faces.append(np.sort(c[:, k], axis=1))
                        quads.append(np.sort(c[:, :4], axis=1))
            vols[gmsh.model.getPhysicalName(dim, tag)] = total
        over = sum(int((np.unique(np.vstack(f), axis=0, return_counts=True)[1] > 2).sum()) for f in (faces, quads) if f)
        print(f"   faces in 3 or more elements: {over}")
        return vols
    finally:
        gmsh.finalize()


def hex_coils():
    """(b) 12 hexahedral coils in tetrahedral iron wedges, iron ring r 20..40, stack 20 mm, coils 5 mm taller."""
    folder = fresh("b_hex_coils_on_iron")
    L, H = 20, 25
    cx, cy, cdx, cdy = 26, -3, 8, 6
    transforms = [compose(rotation(30 * c), m) for c in range(12) for m in (ID, MIRROR_Z)]
    turn = [c for c in range(12) for _ in (0, 1)]

    def iron():
        wedge = sector(20, 40, -15, 15, 0, L)
        cut(wedge, box(cx, cy, 0, cdx, cdy, L))

    lower = piece(folder, "coil_lower", lambda: box(cx, cy, 0, cdx, cdy, L), 2, "CoilLower", 2.0)
    upper = piece(folder, "coil_upper", lambda: box(cx, cy, L, cdx, cdy, H - L), 3, "CoilUpper", 2.0)
    volumes = [piece(folder, "iron", iron, 1, "Iron", 4.0), lower, upper]
    nx, ny, nz, nzu = 5, 4, 11, 3
    edges = []
    for name, lines_by, nodes in (("X", 0, nx), ("Y", 1, ny)):
        both = box_edges(cx, cy, 0, cdx, cdy, L)[lines_by] + box_edges(cx, cy, L, cdx, cdy, H - L)[lines_by]
        edges.append({"name": name, "nodes": nodes, "distribution": "Uniform", "coef": 1.0})
        edges[-1]["files"] = line_files(folder, f"edge_{name}", both)
    for name, (z, h), nodes in (("ZLower", (0, L), nz), ("ZUpper", (L, H - L), nzu)):
        lines = box_edges(cx, cy, z, cdx, cdy, h)[2]
        edges.append({"name": name, "nodes": nodes, "distribution": "Uniform", "coef": 1.0})
        edges[-1]["files"] = line_files(folder, f"edge_{name}", lines)
    bodies = [
        {"name": "CoilLower", "mat_id": 2, "corner_files": []},
        {"name": "CoilUpper", "mat_id": 3, "corner_files": []},
    ]
    parts = [{"mat_id": 1, "name": "Iron"}] + [{"mat_id": 11 + c, "name": f"Coil_{c + 1:02d}"} for c in range(12)]
    rows = [[0] * 24, [1 + c for c in turn], [1 + c for c in turn]]
    g = group("Stator", "fixed", volumes, transforms, parts, rows)
    g["job"]["transfinite"] = {"bodies": bodies, "edges": edges}
    g["job"]["recombine"] = [2, 3]
    air = piece(folder, "air", lambda: gmsh.model.occ.addCylinder(0, 0, -45, 0, 0, 90, 70), 30, "Air", 12.0)
    job = {
        "model_name": "Model",
        "mesh_file": os.path.join(folder, "pre_geom.msh"),
        "options": {},
        "symmetric": {
            "groups": [g],
            "free": [{"side": "fixed", "job": {"volumes": [air], "surfaces": [], "sizes": []}}],
        },
    }
    total = run("b_hex_coils_on_iron", folder, job)
    check_mesh(job["mesh_file"])
    return total


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    totals = {"a_motor_z_mirror_sliding": motor(), "b_hex_coils_on_iron": hex_coils()}
    print("\nTotals:", totals)
