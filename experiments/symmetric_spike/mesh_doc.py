"""SPIKE (throwaway): what Run Mesh would do with a "Symmetric Mesh" item, on the document from build_doc.py.

For every SymMesh_* object:
    1. mesh only its Cell bodies (with mesh settings on the cell: sizes, a transfinite + recombined magnet)
    2. copy the mesh by its Steps (mirror / rotate, applied in order to everything made so far)
    3. every copied piece takes the Material of the drawn body it lands on: a few element centres of the piece,
       moved by the copy's transform, must all be inside one body. Any number of bodies may share a Material.
    4. check that the copies cover every drawn body exactly (area), so a non-symmetric drawing is refused
Each SymMesh item is written to its own file, like the add-on's fixed / moving sides: stator.msh, rotor.msh.

    pixi run -e addon python experiments/symmetric_spike/mesh_doc.py [--gui]
"""

import math
import os
import sys
import tempfile

import FreeCAD as App
import Part
import gmsh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gmsh_symmetry"))
import motor_cell as mc  # noqa: E402 - the copy and check helpers of the earlier experiments

# stand-in for the add-on's mesh items, all on cell bodies: size per body, transfinite + recombined bodies
SIZES = {"StatorAirCell": 0.6, "RotorAirCell": 0.6, "MagnetCell": 0.8}
STRUCTURED = ["MagnetCell"]
# stand-in for a Sliding Interface: the circle between rotor and stator air, divided evenly over the full turn.
# Must be a multiple of 48 here: stator cell 15 deg (1/24 of the turn), rotor cell 22.5 deg (1/16).
R_SLIDE, SLIDE_DIVISIONS = 35, 144


def transforms(steps):
    """The copy transforms of a list of steps; each step works on all copies made so far."""
    out = [mc.rotation(0)]
    for step in steps:
        kind, *v = step.split()
        x, y, deg = float(v[0]), float(v[1]), float(v[2])
        to, back = [1, 0, 0, x, 0, 1, 0, y, 0, 0, 1, 0, 0, 0, 0, 1], [1, 0, 0, -x, 0, 1, 0, -y, 0, 0, 1, 0, 0, 0, 0, 1]
        if kind == "mirror":
            out += [mc.compose(to, mc.mirror_line(deg), back, m) for m in out]
        else:  # rotate x y deg count
            out = [mc.compose(to, mc.rotation(deg * k), back, m) for k in range(int(v[3])) for m in out]
    return out


def mesh_cell(cell):
    """Mesh the cell bodies. Returns {entity: cell body name}."""
    gmsh.model.add("cell")
    inputs, names = [], []
    for obj in cell:
        path = os.path.join(tempfile.gettempdir(), f"spike_{obj.Name}.brep")
        obj.Shape.exportBrep(path)
        dts = gmsh.model.occ.importShapes(path)
        inputs += dts
        names += [obj.Name] * len(dts)
    _, children = gmsh.model.occ.fragment(inputs[:1], inputs[1:])
    gmsh.model.occ.synchronize()
    owner = {t: n for n, kids in zip(names, children) for _, t in kids}
    for n in set(owner.values()):
        ents = [t for t, o in owner.items() if o == n]
        gmsh.model.addPhysicalGroup(2, ents, name=n)
        pts = gmsh.model.getBoundary([(2, t) for t in ents], combined=False, oriented=False, recursive=True)
        if n in SIZES:
            gmsh.model.mesh.setSize(pts, SIZES[n])
        if n in STRUCTURED:
            for f in ents:
                for _, c in gmsh.model.getBoundary([(2, f)], combined=False, oriented=False):
                    p, q = [gmsh.model.getValue(0, t, []) for _, t in gmsh.model.getBoundary([(1, abs(c))])]
                    turn = abs(math.degrees(math.atan2(p[1], p[0]) - math.atan2(q[1], q[0])))
                    # opposite sides need equal counts: arcs by their angle, radial lines by length
                    count = 2 + round(turn / 1.5) if turn > 1e-6 else 2 + round(math.dist(p, q) / SIZES[n])
                    gmsh.model.mesh.setTransfiniteCurve(abs(c), count)
                gmsh.model.mesh.setTransfiniteSurface(f)
                gmsh.model.mesh.setRecombine(2, f)
    for _, c in gmsh.model.getEntities(1):  # the cell's piece of the sliding circle: its share of the divisions
        p, q = [gmsh.model.getValue(0, t, []) for _, t in gmsh.model.getBoundary([(1, c)])]
        if abs(math.hypot(*p[:2]) - R_SLIDE) < 1e-6 and abs(math.hypot(*q[:2]) - R_SLIDE) < 1e-6:
            share = SLIDE_DIVISIONS * abs(math.degrees(math.atan2(p[1], p[0]) - math.atan2(q[1], q[0]))) / 360
            if abs(share - round(share)) > 1e-6:
                raise SystemExit(f"sliding: {SLIDE_DIVISIONS} divisions give the cell's arc {share:g} elements")
            gmsh.model.mesh.setTransfiniteCurve(c, round(share) + 1)
    gmsh.option.setNumber("Mesh.MeshSizeMax", 2.5)
    gmsh.model.mesh.generate(2)
    return owner


def samples(e, n=3):
    """Centres of a few elements of entity e: points surely inside it."""
    _, tags, nodes = gmsh.model.mesh.getElements(2, e)
    per = len(nodes[0]) // len(tags[0])
    pick = [0, len(tags[0]) // 2, len(tags[0]) - 1][:n]
    out = []
    for k in pick:
        xyz = [gmsh.model.mesh.getNode(int(t))[0] for t in nodes[0][k * per : (k + 1) * per]]
        out.append([sum(p[i] for p in xyz) / per for i in range(3)])
    return out


def main():
    doc = App.openDocument(os.path.join(HERE, "motor2d.FCStd"))
    bodies = [o for o in doc.Objects if hasattr(o, "Material")]
    mat_ids = {m: k for k, m in enumerate(sorted({b.Material for b in bodies}), 1)}
    covered = dict.fromkeys(bodies, 0.0)
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    files = []
    for sym in [o for o in doc.Objects if o.Name.startswith("SymMesh_")]:
        copies = transforms(sym.Steps)
        mesh_cell(sym.Cell)
        cell_ents = [t for _, t in gmsh.model.getEntities(2)]
        pts = {e: samples(e) for e in cell_ents}
        area = {e: gmsh.model.occ.getMass(2, e) for e in cell_ents}
        mc.report(f"{sym.Name}: the cell", radii=())

        def land(dim, e, c):
            hits = set()
            for p in pts[e]:
                q = App.Vector(*mc.apply(copies[c], p))
                near = [b for b in bodies if b.Shape.BoundBox.isInside(q)]
                hits |= {b for b in near if b.Shape.distToShape(Part.Vertex(q))[0] < 1e-6}
            if len(hits) != 1:
                where = [round(v, 2) for v in mc.apply(copies[c], pts[e][0])]
                raise SystemExit(f"{sym.Name}: copy {c} of a cell piece lands in {len(hits)} bodies near {where}")
            body = hits.pop()
            covered[body] += area[e]
            return mat_ids[body.Material], body.Material

        mc.copy_mesh(copies, sym.Name, land)
        path = os.path.join(HERE, sym.Name.replace("SymMesh_", "").lower() + ".msh")
        gmsh.write(path)
        files.append(path)
        mc.report(f"{sym.Name}: {len(copies)} copies", radii=(mc.R_SHAFT, mc.R_OUT, 35))

    sides = []  # the node angles on the sliding circle, per file
    for path in files:
        gmsh.open(path)
        tags, xyz, _ = gmsh.model.mesh.getNodes()
        on = [
            xyz[3 * k : 3 * k + 3]
            for k in range(len(tags))
            if abs(math.hypot(*xyz[3 * k : 3 * k + 2]) - R_SLIDE) < 1e-6
        ]
        sides.append(sorted(round(math.degrees(math.atan2(p[1], p[0])), 6) % 360 for p in on))
    print(
        f"\nsliding circle: {' / '.join(str(len(s)) for s in sides)} nodes, same angles on both sides: {sides[0] == sides[1]}"
    )
    bad = [b.Label for b in bodies if abs(covered[b] - b.Shape.Area) > 1e-6 * b.Shape.Area]
    print(f"\n{len(bodies)} bodies, {len(mat_ids)} materials; bodies not covered exactly by copies: {bad or 'none'}")
    if "--gui" in sys.argv:
        gmsh.open(files[0])
        for f in files[1:]:
            gmsh.merge(f)
        gmsh.fltk.run()
    gmsh.finalize()


main()
