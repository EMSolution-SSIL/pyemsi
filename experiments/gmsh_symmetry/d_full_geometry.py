"""The add-on's situation: the user draws the WHOLE motor, one body per FreeCAD object, each with its Material
(MAT_ID). Nothing about poles or slots is known to the mesher. We only declare the symmetry, mesh one cell, and every
copy takes the MAT_ID of the body it lands on in the full geometry.

    1. Import every body (here: built in code), with its MAT_ID. Magnets have 2 materials (N, S), coils 3 (U, V, W).
    2. Fragment the bodies together with the cut lines (2D) or cut planes (3D) of the symmetry, so the model splits
       into sectors.
    3. Match: for every copy transform T and every cell entity e, find the full-model entity f that T(e) lands on
       (same centre of mass, same size). If any entity is left over, the geometry is not symmetric: stop.
    4a. 2D: setPeriodic(2, [f], [e], T) and mesh the full model as usual; gmsh copies the cell's mesh.
        The physical groups are the bodies' MAT_IDs, exactly as the add-on does now.
    4b. 3D: delete everything but the cell, mesh it, copy the mesh. Each copy of e gets the MAT_ID of f.

    pixi run python experiments/gmsh_symmetry/d_full_geometry.py [--dim 2|3] [--gui]
"""

import math
import os
import sys

import gmsh

import motor_cell as mc

HERE = os.path.dirname(os.path.abspath(__file__))
DIM = int(sys.argv[sys.argv.index("--dim") + 1]) if "--dim" in sys.argv else 2
HALF = 20  # 3D: stack z = -20..20
occ = gmsh.model.occ


def ring(r1, r2):
    """Full annulus (2D) or tube (3D, z -HALF..HALF)."""
    if DIM == 2:
        return [(2, occ.cut([(2, occ.addDisk(0, 0, 0, r2, r2))], [(2, occ.addDisk(0, 0, 0, r1, r1))])[0][0][1])]
    return occ.cut(
        [(3, occ.addCylinder(0, 0, -HALF, 0, 0, 2 * HALF, r2))], [(3, occ.addCylinder(0, 0, -HALF, 0, 0, 2 * HALF, r1))]
    )[0]


def piece(r1, r2, a1, a2):
    """Annular sector a1..a2 deg (a2 - a1 < 90), extruded over the stack in 3D."""
    if DIM == 2:
        return mc._sector(r1, r2, a1, a2, None)
    vol = mc._sector(r1, r2, a1, a2, 2 * HALF)
    occ.translate(vol, 0, 0, -HALF)
    return vol


# --- 1. the user's drawing: bodies with materials ---------------------------------------------------------------
MATERIALS = {
    1: "rotor_iron",
    2: "stator_iron",
    3: "air",
    11: "magnet_N",
    12: "magnet_S",
    21: "coil_U",
    22: "coil_V",
    23: "coil_W",
}
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
gmsh.model.add("full")
bodies = [(1, ring(mc.R_SHAFT, mc.R_ROTOR)), (3, ring(mc.R_ROTOR, mc.R_GAP)), (2, ring(mc.R_GAP, mc.R_OUT))]
bodies += [
    (11 + i % 2, piece(mc.R_ROTOR, mc.R_MAGNET, 22.5 + 45 * i - 18, 22.5 + 45 * i + 18)) for i in range(mc.POLES)
]
bodies += [(21 + j % 3, piece(mc.R_SLOT_IN, mc.R_SLOT_OUT, 15 + 30 * j - 5, 15 + 30 * j + 5)) for j in range(mc.SLOTS)]
if "--break" in sys.argv:  # a user mistake: one coil drawn 1 deg off
    occ.rotate(bodies[-1][1], 0, 0, 0, 0, 0, 1, math.radians(1))

# --- 2. the symmetry: 4 x 90 deg, mirror at 45 deg (and z = 0 in 3D) --> cut every 45 deg ------------------------
tools = []
for k in range(8):
    c, s = math.cos(math.radians(45 * k)), math.sin(math.radians(45 * k))
    if DIM == 2:
        p1, p2 = occ.addPoint(mc.R_SHAFT * c, mc.R_SHAFT * s, 0), occ.addPoint(mc.R_OUT * c, mc.R_OUT * s, 0)
        tools.append((1, occ.addLine(p1, p2)))
    else:
        rect = occ.addRectangle(mc.R_SHAFT, -HALF, 0, mc.R_OUT - mc.R_SHAFT, 2 * HALF)
        occ.rotate([(2, rect)], 0, 0, 0, 1, 0, 0, math.pi / 2)  # into the xz plane
        occ.rotate([(2, rect)], 0, 0, 0, 0, 0, 1, math.radians(45 * k))
        tools.append((2, rect))
if DIM == 3:
    tools.append(
        (
            2,
            occ.cut(
                [(2, occ.addDisk(0, 0, 0, mc.R_OUT, mc.R_OUT))], [(2, occ.addDisk(0, 0, 0, mc.R_SHAFT, mc.R_SHAFT))]
            )[0][0][1],
        )
    )
inputs = [dt for _, dts in bodies for dt in dts]
_, children = occ.fragment(inputs, tools)
occ.synchronize()
mat = {}  # final entity -> MAT_ID; later bodies (magnets, coils) win over the ring they sit in
k = 0
for mat_id, dts in bodies:
    for _ in dts:
        mat.update({t: mat_id for d, t in children[k] if d == DIM})
        k += 1

planar = [mc.compose(mc.rotation(90 * k), m) for k in range(4) for m in (mc.rotation(0), mc.mirror_line(45))]
copies = planar if DIM == 2 else [mc.compose(z, p) for p in planar for z in (mc.rotation(0), mc.MIRROR_Z)]

# --- 3. match every copy of every cell entity to an entity of the full model -----------------------------------
props = {t: (occ.getCenterOfMass(DIM, t), occ.getMass(DIM, t)) for t in mat}


def in_cell(t):
    x, y, z = props[t][0]
    return 0 < math.degrees(math.atan2(y, x)) < 45 and (DIM == 2 or z > 0)


cell = [t for t in mat if in_cell(t)]
tol = 1e-6 * mc.R_OUT
match, left = {}, set(mat)
for c, m in enumerate(copies):
    for e in cell:
        target, size = mc.apply(m, props[e][0]), props[e][1]
        f = next(
            (t for t in left if math.dist(props[t][0], target) < tol and abs(props[t][1] - size) < 1e-6 * size), None
        )
        if f is None:
            raise SystemExit(
                f"not symmetric: copy {c} of entity {e} lands on nothing at {[round(v, 3) for v in target]}"
            )
        match[c, e] = f
        left.discard(f)
if left:
    raise SystemExit(f"not symmetric: {len(left)} entities are not a copy of the cell")
print(f"symmetry OK: {len(cell)} cell entities x {len(copies)} copies = {len(mat)} entities of the full model")
# what the user's numbering does to the cell: e.g. the cell's magnet is N in some copies, S in others
for e in cell:
    seen = sorted({MATERIALS[mat[match[c, e]]] for c in range(len(copies))})
    if len(seen) > 1:
        print(f"   cell entity {e} ({MATERIALS[mat[e]]}) becomes {', '.join(seen)} in the copies")

gmsh.option.setNumber("Mesh.MeshSizeMax", 2.5 if DIM == 2 else 4)
mc.refine_air_gap(0.6 if DIM == 2 else 1.5)
if DIM == 2:
    # --- 4a. full model, mesh copied by gmsh -------------------------------------------------------------------
    for (c, e), f in match.items():
        if c:
            gmsh.model.mesh.setPeriodic(2, [f], [e], copies[c])
    for mat_id, name in MATERIALS.items():
        gmsh.model.addPhysicalGroup(2, [t for t in mat if mat[t] == mat_id], mat_id, name=name)
    gmsh.model.mesh.generate(2)
else:
    # --- 4b. keep only the cell, mesh it, copy the mesh with the MAT_IDs of the matched entities ---------------
    gmsh.model.removeEntities([(3, t) for t in mat if t not in cell])
    for d in (2, 1, 0):  # drop what no longer bounds anything
        orphans = [(d, t) for _, t in gmsh.model.getEntities(d) if len(gmsh.model.getAdjacencies(d, t)[0]) == 0]
        gmsh.model.removeEntities(orphans)
    for mat_id in sorted({mat[e] for e in cell}):
        gmsh.model.addPhysicalGroup(3, [e for e in cell if mat[e] == mat_id], mat_id, name=MATERIALS[mat_id])
    gmsh.model.mesh.generate(3)
    mc.report("the cell, the only part meshed", zmax=HALF)
    mc.copy_mesh(copies, "copied", lambda dim, e, c: (mat[match[c, e]], MATERIALS[mat[match[c, e]]]))
gmsh.write(os.path.join(HERE, f"d_full_{DIM}d.msh"))
mc.report(f"full motor, {DIM}D, numbered by the user's materials", zmax=HALF if DIM == 3 else None)

if "--gui" in sys.argv:
    gmsh.fltk.run()
gmsh.finalize()
