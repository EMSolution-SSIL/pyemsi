"""Mesh copying with the add-on's other mesh kinds: transfinite + recombined bodies next to free ones.

The cell (0..45 deg; 3D: z 0..20) is meshed the way the add-on would with these settings:
    magnets and coils   transfinite and recombined: quadrangles in 2D, hexahedra in 3D
    everything else     free: triangles in 2D, tetrahedra in 3D. In 3D the quad faces of the hexes next to
                        tetrahedra get pyramids, as in the add-on's _recombine_3d.
Then the mesh is copied (rotations, the 45 deg mirror and in 3D the z mirror). The check counts each element type,
the inverted elements (the mirrored hexes, prisms and pyramids must be reversed too) and the non-conforming faces.

    pixi run python experiments/gmsh_symmetry/e_transfinite.py [--dim 2|3] [--gui]
"""

import math
import os
import sys

import gmsh

import motor_cell as mc

HERE = os.path.dirname(os.path.abspath(__file__))
DIM = int(sys.argv[sys.argv.index("--dim") + 1]) if "--dim" in sys.argv else 2
HALF = 20

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.model.add("cell")
regions = mc.build_cell(span=45, height=HALF if DIM == 3 else None)
for base in sorted(set(regions.values())):
    gmsh.model.addPhysicalGroup(DIM, [t for (_, t), b in regions.items() if b == base], name=base)

structured = [t for (_, t), b in regions.items() if b in ("magnet", "coil")]


def boundary(dim, tag):
    return [t for _, t in gmsh.model.getBoundary([(dim, tag)], combined=False, oriented=False)]


faces = [f for v in structured for f in boundary(3, v)] if DIM == 3 else structured
for c in {c for f in faces for c in boundary(2, f)}:
    p, q = [gmsh.model.getValue(0, t, []) for t in boundary(1, c)]
    if abs(p[2] - q[2]) > 1e-6:  # along the stack
        n = 6
    elif abs(math.atan2(p[1], p[0]) - math.atan2(q[1], q[0])) < 1e-9:  # radial
        n = 2 + round(math.dist(p, q) / 1.5)
    else:  # arc
        n = 2 + round(abs(math.degrees(math.atan2(p[1], p[0]) - math.atan2(q[1], q[0]))) / 2.5)
    gmsh.model.mesh.setTransfiniteCurve(c, n)
for f in dict.fromkeys(faces):
    gmsh.model.mesh.setTransfiniteSurface(f)
    gmsh.model.mesh.setRecombine(2, f)
for v in structured if DIM == 3 else []:
    gmsh.model.mesh.setTransfiniteVolume(v)

gmsh.option.setNumber("Mesh.MeshSizeMax", 2.5 if DIM == 2 else 4)
mc.refine_air_gap(0.6 if DIM == 2 else 1.5)
gmsh.model.mesh.generate(DIM)
mc.report("cell", zmax=HALF if DIM == 3 else None)

planar = [mc.compose(mc.rotation(90 * k), m) for k in range(4) for m in (mc.rotation(0), mc.mirror_line(45))]
copies = planar if DIM == 2 else [mc.compose(z, p) for p in planar for z in (mc.rotation(0), mc.MIRROR_Z)]
mc.copy_mesh(copies, "full")
gmsh.write(os.path.join(HERE, f"e_full_{DIM}d.msh"))
mc.report(f"full motor from {len(copies)} copies", zmax=HALF if DIM == 3 else None)

if "--gui" in sys.argv:
    gmsh.fltk.run()
gmsh.finalize()
