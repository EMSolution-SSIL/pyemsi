"""Approach B in 3D: mesh one cell of the extruded motor (tetrahedra), copy it to the whole machine.

The stack is 40 mm long (z = -20..20). Three ways to choose the cell:

    --mode mirror           cell 0..45 deg, z 0..20. 16 copies = 4 rotations x 45 deg mirror x z mirror.
                            Every cut is a mirror plane (or maps onto itself), so the cut faces match by construction.
    --mode rotate           cell 0..90 deg, z 0..20. 8 copies = 4 rotations x z mirror. The 0 and 90 deg faces of the
                            cell are linked with setPeriodic (rotation by 90 deg), so their triangles match.
    --mode rotate-free      as rotate, but without setPeriodic: the two cut faces are meshed independently and the
                            copies do not share nodes there. The check reports the holes.

    pixi run python experiments/gmsh_symmetry/c_mesh_copy_3d.py [--mode mirror|rotate|rotate-free] [--gui]
"""

import math
import os
import sys

import gmsh

import motor_cell as mc

HERE = os.path.dirname(os.path.abspath(__file__))
HALF = 20
mode = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "mirror"
span = 45 if mode == "mirror" else 90


def cut_faces(deg):
    """Faces of the cell lying on the plane through the z axis at angle deg."""
    n = (-math.sin(math.radians(deg)), math.cos(math.radians(deg)))
    out = []
    for _, f in gmsh.model.getEntities(2):
        corners = gmsh.model.getBoundary([(2, f)], combined=False, oriented=False, recursive=True)
        pts = [gmsh.model.getValue(0, p, []) for _, p in corners]
        if all(abs(n[0] * x + n[1] * y) < 1e-6 for x, y, _ in pts):
            out.append(f)
    return out


gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.model.add("cell")
regions = mc.build_cell(span=span, height=HALF)
for base in sorted(set(regions.values())):
    gmsh.model.addPhysicalGroup(3, [t for (_, t), b in regions.items() if b == base], name=base)
gmsh.model.addPhysicalGroup(2, mc.outer_boundary(3), name="outer")

if mode == "rotate":
    occ = gmsh.model.occ
    slaves = {f: occ.getCenterOfMass(2, f) for f in cut_faces(90)}
    for f in cut_faces(0):
        moved = mc.apply(mc.rotation(90), occ.getCenterOfMass(2, f))
        partner = min(slaves, key=lambda s: math.dist(slaves[s], moved))
        gmsh.model.mesh.setPeriodic(2, [partner], [f], mc.rotation(90))

gmsh.option.setNumber("Mesh.MeshSizeMax", 4)
mc.refine_air_gap(1.5)
gmsh.model.mesh.generate(3)
gmsh.write(os.path.join(HERE, f"c_cell_3d_{mode}.msh"))
mc.report(f"cell 0..{span} deg, z 0..{HALF}", zmax=HALF)

if mode == "mirror":
    planar = [mc.compose(mc.rotation(90 * k), m) for k in range(4) for m in (mc.rotation(0), mc.mirror_line(45))]
else:
    planar = [mc.rotation(90 * k) for k in range(4)]
copies = [mc.compose(z, p) for p in planar for z in (mc.rotation(0), mc.MIRROR_Z)]
mc.copy_mesh(copies, "full")
gmsh.write(os.path.join(HERE, f"c_full_3d_{mode}.msh"))
mc.report(f"full motor from {len(copies)} copies", zmax=HALF)

if "--gui" in sys.argv:
    gmsh.fltk.run()
gmsh.finalize()
