"""Approach B in 2D: mesh only the 0..45 deg cell, then build the whole motor by copying that mesh.

    8 copies = 4 rotations (0, 90, 180, 270) x {as is, mirrored about the 45 deg line}

Why no periodic constraint is needed here: the cell's 45 deg edge is on the mirror line, so the mirrored copy has
exactly the same nodes there. Its 0 deg edge meets the copy rotated by 270 and mirrored, and that transform maps the
0 deg line onto itself point by point, so again the nodes coincide. The cuts are self-matching by construction.

    pixi run python experiments/gmsh_symmetry/b_mesh_copy_2d.py [--gui]
"""

import os
import sys

import gmsh

import motor_cell as mc

HERE = os.path.dirname(os.path.abspath(__file__))

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.model.add("cell")
regions = mc.build_cell(span=45)
for base in sorted(set(regions.values())):
    gmsh.model.addPhysicalGroup(2, [t for (_, t), b in regions.items() if b == base], name=base)
gmsh.model.addPhysicalGroup(1, mc.outer_boundary(2), name="outer")
gmsh.option.setNumber("Mesh.MeshSizeMax", 2.5)
mc.refine_air_gap(0.6)
gmsh.model.mesh.generate(2)
gmsh.write(os.path.join(HERE, "b_cell_2d.msh"))
mc.report("cell 0..45 deg (the only part that is meshed)")

copies = [mc.compose(mc.rotation(90 * k), mirror) for k in range(4) for mirror in (mc.rotation(0), mc.mirror_line(45))]
mc.copy_mesh(copies, "full")
gmsh.write(os.path.join(HERE, "b_full_2d.msh"))
mc.report("full motor from 8 copies")

if "--gui" in sys.argv:
    gmsh.fltk.run()
gmsh.finalize()
