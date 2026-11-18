"""Prism layers for a 3D skin: grow layers of prisms inward from a body's surface mesh, and fill the core inside them
with tetrahedra. Each surface node moves inward along the angle-weighted mean of its triangles' outward normals; on a
planar cut face (a face on the model boundary or a seam) the layer ends in the face's plane, and the face gets the
prisms' side quads and a triangulated cap inside the inner rim. The caps and the core are meshed in gmsh sub-models.
Runs in the mesher process; never import FreeCAD here."""

import math
import os
import sys
from collections import namedtuple
from dataclasses import dataclass, field

import gmsh
import numpy as np

from meshfrozen import _options
from meshcommon import _note

RATIO = 1.2  # the growth of the layers away from the surface

# A cut face's rim: plane_normal, the unit (3,) normal of its plane; edges, (k, 2) node indexes into X of the rim's
# segments (one or more closed loops, the outer one and the holes'); normal, {node index: unit (3,) vector} the
# outward normal at each rim node, in the face's plane
Rim = namedtuple("Rim", "plane_normal edges normal")

# The options every sub-model sets: gmsh options are global, so they are put back after it
CAP_OPTIONS = {
    "Mesh.MeshOnlyVisible": 0,
    "Mesh.MeshOnlyEmpty": 0,
    "Mesh.MeshSizeMin": 0,
    "Mesh.MeshSizeExtendFromBoundary": 1,
    "Mesh.MeshSizeFromPoints": 1,
    "Mesh.MeshSizeFromCurvature": 0,
    "Mesh.Algorithm": 6,
    "Mesh.RecombineAll": 0,
    "Mesh.ElementOrder": 1,
    "Mesh.SubdivisionAlgorithm": 0,
}
CORE_OPTIONS = {
    "Mesh.MeshOnlyVisible": 0,
    "Mesh.MeshOnlyEmpty": 0,
    "Mesh.MeshSizeMin": 0,
    "Mesh.MeshSizeExtendFromBoundary": 0,
    "Mesh.MeshSizeFromPoints": 0,
    "Mesh.MeshSizeFromCurvature": 0,
    "Mesh.Algorithm3D": 1,
    "Mesh.Recombine3DAll": 0,
    "Mesh.ElementOrder": 1,
    "Mesh.SubdivisionAlgorithm": 0,
}


class LayerFailed(Exception):
    """The layers could not be built: kind "fold" (a prism is inside out) or "core" (gmsh could not fill the core;
    detail is its message)."""

    def __init__(self, kind, detail=""):
        super().__init__(f"{kind}: {detail}")
        self.kind = kind
        self.detail = detail


@dataclass
class Layered:
    """The layers and the core of one body. coords (N, 3): the new nodes; where (N,): (3, 0) for a node in the volume
    or (2, face tag) for one on a cut face; prisms (p, 6) and tets (t, 4): node indexes counting X then coords;
    faces: {cut face tag: (quads (a, 4), triangles (b, 3))} indexed the same way."""

    coords: np.ndarray
    where: list
    prisms: np.ndarray
    tets: np.ndarray
    faces: dict = field(default_factory=dict)


def heights(depth, per_depth, layer):
    """The cumulative heights of the layers: steps depth / per_depth growing by RATIO, as many (at least one) as make
    the sum nearest layer * depth, scaled so the last one is exactly layer * depth."""
    total, step, out = layer * depth, depth / per_depth, []
    while not out or out[-1] < total:
        out.append((out[-1] if out else 0.0) + step)
        step *= RATIO
    if len(out) > 1 and total - out[-2] <= out[-1] - total:
        out.pop()
    return [h * total / out[-1] for h in out]


def _unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def normals(X, tris, fixed):
    """The unit normal of each node of X: the mean of its triangles' outward unit normals weighted by the triangles'
    angles at the node. A node in fixed takes its given vector."""
    P = X[tris]
    n = _unit(np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]))
    N = np.zeros_like(X, dtype=float)
    for i in range(3):
        u, v = _unit(P[:, (i + 1) % 3] - P[:, i]), _unit(P[:, (i + 2) % 3] - P[:, i])
        angle = np.arccos(np.clip(np.einsum("ij,ij->i", u, v), -1, 1))
        np.add.at(N, tris[:, i], angle[:, None] * n)
    for node, vector in fixed.items():
        N[node] = vector
    return _unit(N)


def folded(layers, tris):
    """The number of prisms between successive layers (lists of (n, 3) coordinates, the first the surface) that are
    inside out: a corner volume <= 0 at any of the three corners of the bottom or the top triangle."""
    bad = np.zeros((len(layers) - 1, len(tris)), dtype=bool)
    for k in range(len(layers) - 1):
        lo, hi = layers[k], layers[k + 1]
        for i, j, m in ((0, 2, 1), (2, 1, 0), (1, 0, 2)):  # the bottom (a, c, b) of an outward (a, b, c), as the prism
            a, b, c = tris[:, i], tris[:, j], tris[:, m]
            up = hi[a] - lo[a]
            bottom = np.einsum("ij,ij->i", np.cross(lo[b] - lo[a], lo[c] - lo[a]), up)
            top = np.einsum("ij,ij->i", np.cross(hi[b] - hi[a], hi[c] - hi[a]), up)
            bad[k] |= ~(bottom > 0) | ~(top > 0)  # a NaN volume counts too
    return int(bad.sum())


class _SubModel:
    """A gmsh model of its own for one step: the options set and the caller's model current again afterwards, the
    sub-model removed."""

    def __init__(self, name, options):
        self.name, self.options = name, options

    def __enter__(self):
        self.caller = gmsh.model.getCurrent()
        self.set = _options(self.options)
        self.set.__enter__()
        gmsh.model.add(self.name)
        return self

    def __exit__(self, *exc):
        try:
            if gmsh.model.getCurrent() == self.name:
                gmsh.model.remove()
            gmsh.model.setCurrent(self.caller)
        finally:
            self.set.__exit__(*exc)
        return False


def cap(loop, holes, size):
    """Triangulate the plane face inside the closed loop of points (k, 3) and outside the holes (each (h, 3)), with the
    loops' segments as its edges: a geo plane surface whose lines get 2 nodes each, in its own model. Each point's
    size is the mean length of its two segments, and size is the largest. Returns the interior nodes' coordinates
    (q, 3) and the triangles (t, 3), whose indexes count the loop first, then the holes in order, then the interior
    nodes."""
    rings = [np.asarray(loop, dtype=float)] + [np.asarray(h, dtype=float) for h in holes]
    with _SubModel("meshlayers_cap", {**CAP_OPTIONS, "Mesh.MeshSizeMax": size}):
        try:
            geo = gmsh.model.geo
            points, curve_loops = [], []
            for ring in rings:
                seg = np.linalg.norm(np.roll(ring, -1, axis=0) - ring, axis=1)
                lc = np.minimum((seg + np.roll(seg, 1)) / 2, size)
                tags = [geo.addPoint(*p.tolist(), meshSize=float(s)) for p, s in zip(ring, lc)]
                lines = [geo.addLine(tags[i], tags[(i + 1) % len(tags)]) for i in range(len(tags))]
                curve_loops.append(geo.addCurveLoop(lines))
                points += tags
            surface = geo.addPlaneSurface(curve_loops)
            geo.synchronize()
            for _, line in gmsh.model.getEntities(1):
                gmsh.model.mesh.setTransfiniteCurve(line, 2)
            gmsh.model.mesh.generate(2)
            index = {int(gmsh.model.mesh.getNodes(0, p)[0][0]): i for i, p in enumerate(points)}
            inner, xyz, _ = gmsh.model.mesh.getNodes(2, surface)
            index.update({int(t): len(points) + j for j, t in enumerate(inner)})
            _, nodes = gmsh.model.mesh.getElementsByType(2, surface)
            triangles = np.array([index[int(t)] for t in nodes], dtype=np.int64).reshape(-1, 3)
            coords = np.array(xyz, dtype=float).reshape(-1, 3)
        except Exception as exc:
            raise LayerFailed("core", f"the cap: {exc}") from exc
    # gmsh meshes a loop that crosses itself without an error: the triangles must cover the face once, all one way
    normal = np.cross(rings[0], np.roll(rings[0], -1, axis=0)).sum(axis=0)  # twice the loop's area along its normal
    if len(triangles) and normal.any():
        unit = _unit(normal)
        P = np.vstack(rings + [coords])
        signed = np.cross(P[triangles[:, 1]] - P[triangles[:, 0]], P[triangles[:, 2]] - P[triangles[:, 0]]) @ unit / 2
        signed = signed * (1 if signed.sum() >= 0 else -1)  # either way round, as long as all are
        area = np.linalg.norm(normal) / 2 - sum(_area(h, unit) for h in rings[1:])
        if (signed > 0).all() and area > 0 and abs(signed.sum() - area) <= 1e-6 * area:
            return coords, triangles
    raise LayerFailed("core", "the cap's rim crosses itself")


def core(inner, tris, caps, size_in, size_out):
    """Fill the closed surface made of the inner surface (nodes inner (n, 3), triangles tris) and the caps with
    tetrahedra, in a sub-model. caps: (coords, triangles) per cap, coords its interior nodes and triangles indexing
    inner first, then each cap's interior nodes in order. The size is size_in at the inner surface, growing to size_out
    at 2 * size_out from it. Returns the new interior nodes' coordinates (q, 3) and the tets (t, 4), indexing inner,
    then the caps' interior nodes, then the new nodes. A gmsh error raises LayerFailed("core")."""
    with _SubModel("meshlayers_core", {**CORE_OPTIONS, "Mesh.MeshSizeMax": size_out}):
        known = len(inner) + sum(len(c) for c, _ in caps)
        try:
            surfaces = [gmsh.model.addDiscreteEntity(2)]
            gmsh.model.mesh.addNodes(2, surfaces[0], list(range(1, len(inner) + 1)), inner.ravel().tolist())
            gmsh.model.mesh.addElementsByType(surfaces[0], 2, [], (np.asarray(tris) + 1).ravel().tolist())
            first = len(inner) + 1
            for coords, triangles in caps:
                s = gmsh.model.addDiscreteEntity(2)
                gmsh.model.mesh.addNodes(2, s, list(range(first, first + len(coords))), coords.ravel().tolist())
                gmsh.model.mesh.addElementsByType(s, 2, [], (np.asarray(triangles) + 1).ravel().tolist())
                surfaces.append(s)
                first += len(coords)
            volume = gmsh.model.geo.addVolume([gmsh.model.geo.addSurfaceLoop(surfaces)])
            gmsh.model.geo.synchronize()
            fields = gmsh.model.mesh.field
            distance = fields.add("Distance")
            fields.setNumbers(distance, "SurfacesList", [surfaces[0]])
            threshold = fields.add("Threshold")
            for name, value in (
                ("InField", distance),
                ("SizeMin", size_in),
                ("SizeMax", size_out),
                ("DistMin", 0),
                ("DistMax", 2 * size_out),
            ):
                fields.setNumber(threshold, name, value)
            fields.setAsBackgroundMesh(threshold)
            gmsh.model.mesh.generate(3)
        except Exception as exc:
            raise LayerFailed("core", str(exc)) from exc
        tags, xyz, _ = gmsh.model.mesh.getNodes(3, volume)
        _, nodes = gmsh.model.mesh.getElementsByType(4, volume)
        index = np.full(int(max(known, tags.max() if len(tags) else 0)) + 1, -1, dtype=np.int64)
        index[1 : known + 1] = np.arange(known)
        index[tags.astype(np.int64)] = known + np.arange(len(tags))
        nodes = np.asarray(nodes, dtype=np.int64)
        if len(nodes) == 0 or nodes.max() >= len(index) or (index[nodes] < 0).any():
            raise LayerFailed("core", "the core's tetrahedra changed its boundary" if len(nodes) else "no tetrahedra")
        return np.array(xyz, dtype=float).reshape(-1, 3), index[nodes].reshape(-1, 4)


def _loops(edges):
    """The closed loops of node indexes that the segments edges (k, 2) make."""
    around = {}
    for a, b in np.asarray(edges).tolist():
        around.setdefault(a, []).append(b)
        around.setdefault(b, []).append(a)
    seen, loops = set(), []
    for start in around:
        if start in seen:
            continue
        loop, prev = [start], None
        seen.add(start)
        while True:
            nxt = next((m for m in around[loop[-1]] if m != prev and (m not in seen or m == start)), None)
            if nxt is None or nxt == start:
                break
            prev = loop[-1]
            loop.append(nxt)
            seen.add(nxt)
        loops.append(loop)
    return loops


def _area(points, normal):
    """The area of the closed polygon points (k, 3) seen along normal."""
    return abs(np.cross(points, np.roll(points, -1, axis=0)).sum(axis=0) @ normal) / 2


def _transform(matrix, points):
    M = np.asarray(matrix, dtype=float).reshape(4, 4)
    return points @ M[:3, :3].T + M[:3, 3]


def build(X, tris, rims, heights, size_in, size_out, seams=()):
    """Grow prism layers inward from the surface X (n, 3), tris (m, 3) oriented outward (every node of X a node of
    tris), and fill the core with tetrahedra. rims: {cut face tag: Rim}; heights: the cumulative layer heights (from
    heights()). size_in None: the median edge of the inner surface. seams: (slave face, master face, 4x4 row-major
    matrix) triples; the slave's cap is the master's cap moved by the matrix, its nodes matched to the slave's rim by
    nearest point. Raises LayerFailed("fold") when a prism is inside out, LayerFailed("core") when the core cannot be
    filled. Returns a Layered."""
    X, tris, n, L = np.asarray(X, dtype=float), np.asarray(tris, dtype=np.int64), len(X), len(heights)
    fixed, face_of = {}, {}
    for face, rim in rims.items():
        plane = _unit(np.asarray(rim.plane_normal, dtype=float))
        for node, vector in rim.normal.items():
            v = fixed.get(node, np.asarray(vector, dtype=float))
            fixed[node] = v - (v @ plane) * plane
            face_of.setdefault(node, face)
    N = normals(X, tris, fixed)
    layers = [X] + [X - h * N for h in heights]
    bad = folded(layers, tris)
    if bad:
        raise LayerFailed("fold", f"{bad} prisms are inside out")
    # node k * n + i is node i of layer k; layer 0 is X itself
    prisms = np.vstack(
        [np.column_stack([k * n + tris[:, [0, 2, 1]], (k + 1) * n + tris[:, [0, 2, 1]]]) for k in range(L)]
    )
    coords = list(layers[1:])
    where = [face_of.get(i) for i in range(n)]
    where = [(3, 0) if f is None else (2, f) for f in where] * L
    inner = layers[L]
    if size_in is None:
        size_in = float(np.median(np.linalg.norm(inner[tris[:, [1, 2, 0]]] - inner[tris], axis=2)))
    size = np.ptp(X, axis=0).max()
    # the caps in the core's numbering: inner first, then each cap's interior nodes; a seam's master before its slave
    moved = {slave: (master, matrix) for slave, master, matrix in seams}
    caps, starts, first = {}, {}, n
    for face in [f for f in rims if f not in moved] + [f for f in rims if f in moved]:
        rim = rims[face]
        plane = _unit(np.asarray(rim.plane_normal, dtype=float))
        rim_nodes = np.unique(rim.edges)
        if face in moved:
            master, matrix = moved[face]
            m_coords, m_tris = caps[master]
            m_rim = np.unique(m_tris[m_tris < n])
            gap = np.linalg.norm(_transform(matrix, inner[m_rim])[:, None, :] - inner[None, rim_nodes, :], axis=2)
            nearest = gap.argmin(axis=1)
            if (
                len(m_rim) != len(rim_nodes)
                or len(set(nearest.tolist())) != len(nearest)
                or (gap[np.arange(len(m_rim)), nearest] > 1e-6 * size).any()
            ):
                raise LayerFailed("core", f"the rim of face {face} does not match the cap of face {master} moved")
            c_tris = m_tris.copy()
            on = c_tris < n
            c_tris[on] = rim_nodes[nearest[np.searchsorted(m_rim, c_tris[on])]]
            c_tris[~on] += first - starts[master]
            c_coords = _transform(matrix, m_coords)
        else:
            loops = sorted(_loops(rim.edges), key=lambda lp: -_area(inner[lp], plane))
            ring = np.concatenate(loops)
            c_coords, local = cap(inner[loops[0]], [inner[lp] for lp in loops[1:]], size_out)
            c_tris = np.where(local < len(ring), ring[np.minimum(local, len(ring) - 1)], local - len(ring) + first)
        # outward, away from the body: the side the triangles at the rim lie on is inside
        P = np.vstack([inner, *(c for c, _ in caps.values()), c_coords])
        normal = np.cross(P[c_tris[:, 1]] - P[c_tris[:, 0]], P[c_tris[:, 2]] - P[c_tris[:, 0]])
        near = tris[np.isin(tris, rim_nodes).any(axis=1)]
        inside = np.sign(((X[near].mean(axis=1) - X[rim_nodes].mean(axis=0)) @ plane).sum()) or 1.0
        flip = (normal @ plane) * inside > 0
        c_tris[flip] = c_tris[flip][:, ::-1]
        caps[face], starts[face] = (c_coords, c_tris), first
        first += len(c_coords)
    c_new, tets = core(inner, tris, list(caps.values()), size_in, size_out)
    # the core's numbering is ours less the first L layers: inner node i is L * n + i, the cap and core nodes follow
    faces = {}
    for face, (c_coords, c_tris) in caps.items():
        e = np.asarray(rims[face].edges, dtype=np.int64)
        quads = np.vstack([np.column_stack([k * n + e, (k + 1) * n + e[:, ::-1]]) for k in range(L)])
        faces[face] = (quads, c_tris + L * n)
        coords.append(c_coords)
        where += [(2, face)] * len(c_coords)
    coords.append(c_new)
    where += [(3, 0)] * len(c_new)
    return Layered(np.vstack(coords), where, prisms, tets + L * n, faces)


SMOOTH = math.cos(math.radians(15))  # two real faces meet with their normals turning by at most 15 degrees
SQUARE = 0.5  # a real face meets a cut within 30 degrees of square: |real normal . cut normal| at most this
SAMPLES = 7  # the points along a curve where the normals are compared


def _signs(vol):
    """{face: +1 or -1}: the faces of vol and the sign that turns their CAD normal outward, found by stepping off a
    point inside the face along its normal (the sign of getBoundary's oriented faces is not that on OCC planes)."""
    box = np.reshape(gmsh.model.getBoundingBox(3, vol), (2, 3))
    eps = 1e-4 * float(np.linalg.norm(box[1] - box[0]))
    out = {}
    for _, t in gmsh.model.getBoundary([(3, vol)], combined=False, oriented=False):
        f, out[abs(t)] = abs(t), 1
        lo, hi = gmsh.model.getParametrizationBounds(2, f)
        grid = [
            (u, v)
            for k in (7, 15)
            for u in np.linspace(lo[0], hi[0], k)[1:-1]
            for v in np.linspace(lo[1], hi[1], k)[1:-1]
        ]
        for uv in grid:
            if gmsh.model.isInside(2, f, list(uv), parametric=True):
                p = np.array(gmsh.model.getValue(2, f, list(uv)))
                n = _unit(np.array(gmsh.model.getNormal(f, list(uv))))
                ahead, behind = (gmsh.model.isInside(3, vol, (p + s * eps * n).tolist()) for s in (1, -1))
                if ahead and not behind:
                    out[f] = -1
                break
    return out


def _curves(face):
    return list(dict.fromkeys(abs(t) for _, t in gmsh.model.getBoundary([(2, face)], combined=False, oriented=False)))


def _normals_at(face, sign, xyz):
    """The outward unit normals (k, 3) of face (sign from _signs) at the points xyz (k, 3) on it."""
    uv = gmsh.model.getParametrization(2, face, np.asarray(xyz, dtype=float).ravel().tolist())
    return sign * _unit(np.reshape(gmsh.model.getNormal(face, uv), (-1, 3)))


def _along(curve):
    """SAMPLES points (k, 3) along curve, its ends included."""
    lo, hi = (b[0] for b in gmsh.model.getParametrizationBounds(1, curve))
    return np.reshape(gmsh.model.getValue(1, curve, np.linspace(lo, hi, SAMPLES).tolist()), (-1, 3))


def _planar(face):
    """True when face is a plane: its normal the same over a grid of its parameters."""
    lo, hi = gmsh.model.getParametrizationBounds(2, face)
    uv = [x for u in np.linspace(lo[0], hi[0], 5) for v in np.linspace(lo[1], hi[1], 5) for x in (u, v)]
    n = _unit(np.reshape(gmsh.model.getNormal(face, uv), (-1, 3)))
    return bool((n @ n[0] >= 1 - 1e-9).all())


def _layer_faces(vol, cut_against, images, extra):
    """(real faces, cut faces, signs from _signs) of vol. A face is real when it is in extra (a cell's faces toward the
    free side) or a volume that is no image lies beyond it, unless all such volumes are in cut_against (conductors with
    a skin of their own: terminals); every other face is a cut (on the model boundary, a seam with a copy, against a
    terminal)."""
    signs = _signs(vol)
    real = []
    for f in signs:
        beyond = [v for v in gmsh.model.getAdjacencies(2, f)[0] if v != vol and v not in images]
        if f in extra or (beyond and not all(v in cut_against for v in beyond)):
            real.append(f)
    return real, [f for f in signs if f not in real], signs


def _check(real, cuts, signs):
    """(why, rim_face): why is None when the body is smooth and its cuts flat and square (spec 6), else "sharp" or
    "cut"; rim_face: {curve of a cut face: the real face beside it}."""
    rim_face, faces_of = {}, {}
    for f in real + cuts:
        for c in _curves(f):
            faces_of.setdefault(c, []).append(f)
    for c, faces in faces_of.items():
        mine = [f for f in dict.fromkeys(faces) if f in real]
        if len(mine) == 2:  # between two real faces: smooth along the curve
            xyz = _along(c)
            a, b = (_normals_at(f, signs[f], xyz) for f in mine)
            if (np.einsum("ij,ij->i", a, b) < SMOOTH).any():
                return "sharp", rim_face
    corners = {}
    for cut in cuts:
        if not _planar(cut):
            return "cut", rim_face
        for c in _curves(cut):
            beside = [f for f in faces_of[c] if f in real]
            if not beside:  # every curve of a cut face is shared with a real face
                return "cut", rim_face
            xyz = _along(c)
            square = np.einsum("ij,ij->i", _normals_at(beside[0], signs[beside[0]], xyz), _normals_at(cut, 1, xyz))
            if (np.abs(square) > SQUARE).any():
                return "cut", rim_face
            rim_face[c] = beside[0]
        for _, p in gmsh.model.getBoundary([(2, cut)], combined=False, oriented=False, recursive=True):
            if corners.setdefault(p, cut) != cut:  # a rim node on two cut faces
                return "cut", rim_face
    return None, rim_face


def _surface(real, signs):
    """The mesh gmsh made on the real faces: node tags (n,) sorted, X (n, 3) and the triangles (m, 3) indexing them,
    oriented outward with the faces' CAD normals."""
    blocks, xyz = [], {}
    for f in real:
        types, _, nodes = gmsh.model.mesh.getElements(2, f)
        if [int(t) for t in types] != [2]:
            raise LayerFailed("core", f"the mesh of face {f} is not all triangles")
        T = np.asarray(nodes[0], dtype=np.int64).reshape(-1, 3)
        tags, coords, _ = gmsh.model.mesh.getNodes(2, f, includeBoundary=True)
        xyz.update(zip(tags.astype(np.int64).tolist(), np.reshape(coords, (-1, 3))))
        P = np.array([[xyz[int(t)] for t in row] for row in T])
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        flip = np.einsum("ij,ij->i", n, _normals_at(f, signs[f], P.mean(axis=1))) < 0
        T[flip] = T[flip][:, ::-1]
        blocks.append(T)
    T = np.vstack(blocks)
    tags = np.unique(T)
    return tags, np.array([xyz[int(t)] for t in tags]), np.searchsorted(tags, T)


def _rims(cuts, rim_face, signs, tags, X):
    """{cut face: Rim} from the mesh of its curves; a rim node's normal is that of the real face beside its curve
    (rim_face), projected into the cut's plane by build."""
    rims = {}
    for cut in cuts:
        lo, hi = gmsh.model.getParametrizationBounds(2, cut)
        plane = _unit(np.array(gmsh.model.getNormal(cut, [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2])))
        edges, normal = [], {}
        for c in _curves(cut):
            _, nodes = gmsh.model.mesh.getElementsByType(1, c)
            e = np.asarray(nodes, dtype=np.int64).reshape(-1, 2)
            i = np.minimum(np.searchsorted(tags, e), len(tags) - 1)
            if (tags[i] != e).any():
                raise LayerFailed("core", f"the rim of face {cut} is not on the real surface")
            edges.append(i)
            at = np.unique(i)
            f = rim_face[c]
            normal.update(zip(at.tolist(), _normals_at(f, signs[f], X[at])))
        rims[cut] = Rim(plane, np.vstack(edges), normal)
    return rims


def _oriented(face, conn, P):
    """The rows conn (node indexes into P) turned as face is, the way gmsh meshes a face (as meshsweep._join)."""
    conn = np.array(conn, dtype=np.int64)
    if not len(conn):
        return conn
    p = P[conn]
    uv = gmsh.model.getParametrization(2, face, p.mean(axis=1).ravel().tolist())
    n = np.reshape(gmsh.model.getNormal(face, uv), (-1, 3))
    turned = np.einsum("ij,ij->i", np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), n) < 0
    conn[turned] = conn[turned][:, ::-1]
    return conn


def _write(vol, tags, X, layered):
    """Put layered (built on the surface nodes tags, X) into the model: tags from the largest ones on (Mesh.Renumber
    is off: gmsh numbers on from the max), the nodes on the cut faces with their parameters."""
    start = int(gmsh.model.mesh.getMaxNodeTag()) + 1
    node = np.concatenate([tags, start + np.arange(len(layered.coords))])
    groups = {}
    for i, w in enumerate(layered.where):
        groups.setdefault(w, []).append(i)
    for (d, t), idx in groups.items():
        xyz = layered.coords[idx].ravel().tolist()
        par = list(gmsh.model.getParametrization(2, t, xyz)) if d == 2 else []
        gmsh.model.mesh.addNodes(d, t if d == 2 else vol, node[len(X) + np.asarray(idx)].tolist(), xyz, par)
    element = int(gmsh.model.mesh.getMaxElementTag()) + 1
    P = np.vstack([X, layered.coords])
    blocks = [(f, 3, _oriented(f, q, P)) for f, (q, _) in layered.faces.items()]
    blocks += [(f, 2, _oriented(f, t, P)) for f, (_, t) in layered.faces.items()]
    for t, etype, conn in blocks + [(vol, 6, layered.prisms), (vol, 4, layered.tets)]:
        if len(conn):
            n = len(conn)
            gmsh.model.mesh.addElementsByType(t, etype, list(range(element, element + n)), node[conn].ravel().tolist())
            element += n


INWARD_SAMPLES = 25  # the inner-layer nodes _inward tests


def _inward(vol, layered, n, L):
    """Raise LayerFailed("fold") unless the layers grew into vol: most of a sample of the inner layer's nodes off the
    cut faces (layered from build on n surface nodes, L layers) lie inside it. A wrong sign from _signs (no grid
    point of a face found inside it) turns the surface inside out: the layers grow outward, unfolded, into the air."""
    inner = (L - 1) * n + np.flatnonzero([w == (3, 0) for w in layered.where[(L - 1) * n : L * n]])
    if not len(inner):
        return
    pick = inner[np.linspace(0, len(inner) - 1, min(INWARD_SAMPLES, len(inner))).astype(int)]
    inside = gmsh.model.isInside(3, vol, layered.coords[pick].ravel().tolist())
    if 2 * inside <= len(pick):
        raise LayerFailed("fold", f"{len(pick) - inside} of {len(pick)} inner nodes are outside the body")


def _layer_add(job, entry, m, vol, faces, rim_face, hidden, size_out):
    """add(d) for meshcommon._swept_stages: at d == 3, the prism layers and the core of vol on the mesh gmsh made on
    its real faces (faces: _layer_faces), a seam's cap (job["layer_seams"], a cell's) moved from its master's. On
    LayerFailed nothing is written, hidden is shown again so gmsh meshes the body, each seam's slave as a copy of its
    master (their rims are copies already, meshgroups._pair_rims), and a note says why."""
    real, cuts, signs = faces

    def add(d):
        if d != 3 or gmsh.model.getVisibility(3, vol):  # shown: generate did not hide it, so gmsh meshes it
            return
        seams = [s for s in job["layer_seams"] if s[0] in cuts]
        try:
            tags, X, tris = _surface(real, signs)
            rims = _rims(cuts, rim_face, signs, tags, X)
            hs = heights(entry["depth"], entry["per_depth"], entry["layer"])
            layered = build(X, tris, rims, hs, None, size_out, seams)
            _inward(vol, layered, len(X), len(hs))
        except LayerFailed as failed:
            for slave, master, matrix in seams:
                gmsh.model.mesh.setPeriodic(2, [slave], [master], matrix)
            gmsh.model.setVisibility(hidden, 1)
            if failed.kind == "fold":
                why = "the prism layers would fold (the layer is too deep for its curves)"
            else:
                why = f"gmsh could not fill the core inside the prism layers ({failed.detail})"
            _note(f"Skin Layer {entry['name']}: MAT_ID {m}: {why}; graded tetrahedra instead")
            return
        _write(vol, tags, X, layered)
        gmsh.model.mesh.setTransfiniteVolume(vol)  # Delaunay leaves it alone, as a swept volume (_mesh_swept)
        if os.environ.get("EMS_LAYER_DEBUG"):  # the tests compare what was built with what was written
            print(f"LAYERS {vol} prisms {len(layered.prisms)} tets {len(layered.tets)}", file=sys.stderr)
        if m not in job["layered"]:
            job["layered"].append(m)

    return add


def _periodic_faces():
    """The faces that gmsh copies the mesh of (setPeriodic, meshcommon.apply_periodic) or copies it to."""
    out = set()
    for _, f in gmsh.model.getEntities(2):
        master = int(gmsh.model.mesh.getPeriodic(2, [f])[0])
        if master != f:
            out |= {f, master}
    return out


def apply_layers(job, body_vols, sizes, skin_faces=None):
    """3D prism layers in the skins with "quads" (job["skin"] entries), at the end of mesher.build: the first such skin
    in job order makes them per MAT_ID (not swept, structured or recombined), each volume of it on its own. A volume
    that is not smooth, whose cuts are not flat and square (spec 6) or that a periodic boundary cuts keeps the graded
    tetrahedra, with a note.
    body_vols: {MAT_ID: final tags}; sizes: {MAT_ID: size}; skin_faces: {(index of the skin entry, MAT_ID): {dim:
    [final tags]}}, a cell's faces toward the free side. job gets "layer_tags" (the volumes), "layer_hidden" (each
    volume and its cut faces, which meshcommon.generate hides), "layer_seams" (seam pairs of cells, filled by
    meshgroups), "layered" (the MAT_IDs that got layers, filled while meshing) and one add(d) per volume in
    "swept_add". Returns the volumes."""
    job["layer_tags"], job["layer_hidden"], job["layer_seams"], job["layered"] = [], [], [], []
    adds = []
    entries = job.get("skin", [])
    swept = {e["mat_id"] for e in job.get("swept", [])}
    tf = {b["mat_id"] for b in (job.get("transfinite") or {}).get("bodies", [])}
    recombined = set(job.get("recombine", [])) | tf
    layering = {m for e in entries if e.get("quads") for m in e["mat_ids"]}
    skins = {m for e in entries for m in e["mat_ids"]} | {e["mat_id"] for e in job.get("swept", []) if e.get("skin")}
    # a face against another conductor with a skin of its own (a terminal) is a cut, as no skin is there; one against
    # a body that may get layers too is real (both sides meet its triangles); one against a swept body is real too,
    # and Validate refuses a swept body touching a body that gets prism layers (validation._swept_bodies)
    cut_against = {t for m in skins - layering - swept for t in body_vols.get(m, [])}
    images = {t for v in job.get("volumes", []) if v.get("image") for t in body_vols.get(v["mat_id"], [])}
    periodic = _periodic_faces() if any(e.get("quads") for e in entries) else set()
    done = set()
    for k, e in enumerate(entries):
        if not e.get("quads"):
            continue
        for m in e["mat_ids"]:
            if m in done or m in swept:
                continue
            done.add(m)
            if m in recombined:
                _note(f"Skin Layer {e['name']}: MAT_ID {m} is structured or recombined; no prism layers")
                continue
            extra = set((skin_faces or {}).get((k, m), {}).get(2, []))
            noted = set()
            for vol in body_vols.get(m, []):
                faces = _layer_faces(vol, cut_against, images, extra)
                if not faces[0]:  # no real surface: apply_refinements said so
                    continue
                why, rim_face = _check(*faces)
                if not why and periodic.intersection(faces[1]):  # each cut capped on its own: no periodic copy
                    why = "periodic"
                if why:
                    if why not in noted:
                        noted.add(why)
                        what = {
                            "sharp": "has a sharp edge on its surface",
                            "cut": "is cut by a curved face or at a slant",
                            "periodic": "is cut by a periodic boundary",
                        }[why]
                        _note(f"Skin Layer {e['name']}: MAT_ID {m} {what}; graded tetrahedra instead of prism layers")
                    continue
                hidden = [(3, vol)] + [(2, c) for c in faces[1]]
                job["layer_tags"].append(vol)
                job["layer_hidden"] += hidden
                adds.append(_layer_add(job, e, m, vol, faces, rim_face, hidden, sizes[m]))
    job["swept_add"] = list(job.get("swept_add", [])) + adds
    return job["layer_tags"]
