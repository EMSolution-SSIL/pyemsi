"""Approach A in 2D: build the whole motor's geometry from copies of the cell, and let gmsh copy the mesh.

Every surface of every copy is made periodic with the cell surface it came from (setPeriodic with the copy's
transform). gmsh then meshes only the cell surfaces and copies their mesh onto the others, mirrored ones included
(it fixes the element orientation itself). The physical groups are assigned on the geometry, with the same rule as
approach B.

Note: this only works in 2D. In 3D gmsh copies the mesh of periodic *surfaces*, but meshes every volume on its own,
even with setPeriodic(3, ...): the volumes are conforming but not copies (see the README).

    pixi run python experiments/gmsh_symmetry/a_periodic_2d.py [--gui]
"""

import os
import sys

import gmsh

import motor_cell as mc

HERE = os.path.dirname(os.path.abspath(__file__))

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.model.add("periodic")
cell = mc.build_cell(span=45)  # fragmented cell: its surfaces only touch along lines
copies = [mc.compose(mc.rotation(90 * k), mirror) for k in range(4) for mirror in (mc.rotation(0), mc.mirror_line(45))]

occ = gmsh.model.occ
sources = list(cell)
pieces = list(sources)  # every surface of every copy, in order: copy c, cell surface j
for m in copies[1:]:
    dup = occ.copy(sources)
    occ.affineTransform(dup, m[:12])
    pieces += dup
_, children = occ.fragment(pieces, [])  # glue the copies together along the cut lines
occ.synchronize()
assert all(len(k) == 1 for k in children), "a copy overlapped another one"

for c, m in enumerate(copies[1:], 1):
    for j in range(len(sources)):
        master, slave = children[j][0][1], children[c * len(sources) + j][0][1]
        gmsh.model.mesh.setPeriodic(2, [slave], [master], m)

groups = {}
for c, m in enumerate(copies):
    for j, src in enumerate(sources):
        surf = children[c * len(sources) + j][0][1]
        pid, name = mc.physical(cell[src], *occ.getCenterOfMass(2, surf)[:2])
        groups.setdefault(pid, [name, []])[1].append(surf)
for pid, (name, surfs) in sorted(groups.items()):
    gmsh.model.addPhysicalGroup(2, surfs, pid, name=name)
gmsh.model.addPhysicalGroup(1, mc.outer_boundary(2), mc.SHARED["outer"], name="outer")

gmsh.option.setNumber("Mesh.MeshSizeMax", 2.5)
mc.refine_air_gap(0.6)
gmsh.model.mesh.generate(2)
gmsh.write(os.path.join(HERE, "a_full_2d.msh"))
mc.report("full motor, geometry copied, mesh copied by gmsh (periodic surfaces)")

if "--gui" in sys.argv:
    gmsh.fltk.run()
gmsh.finalize()
