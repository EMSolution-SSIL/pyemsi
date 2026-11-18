"""Prism layers for a 3D skin: grow layers of prisms inward from a body's surface mesh, and fill the core inside them
with tetrahedra. Each surface node moves inward along the angle-weighted mean of its triangles' outward normals; on a
planar cut face (a face on the model boundary or a seam) the layer ends in the face's plane, and the face gets the
prisms' side quads and a triangulated cap inside the inner rim. The caps and the core are meshed in gmsh sub-models.
Runs in the mesher process; never import FreeCAD here."""

from collections import namedtuple
from dataclasses import dataclass, field

import gmsh
import numpy as np

from meshfrozen import _options

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
    heights()). seams: (slave face, master face, 4x4 row-major matrix) triples; the slave's cap is the master's cap
    moved by the matrix, its nodes matched to the slave's rim by nearest point. Raises LayerFailed("fold") when a prism
    is inside out, LayerFailed("core") when the core cannot be filled. Returns a Layered."""
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
