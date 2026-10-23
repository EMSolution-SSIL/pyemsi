"""Symmetric Mesh: read the copy transforms from the objects the user drew the full geometry with.

The user draws a cell and builds the whole 2D geometry from it with Part Mirror, Draft Polar Array and Part
Compound / Boolean Fragments. read_chain walks that chain from its top object down to the cell bodies and returns
where every copy of the cell lies. Transforms are 4x4 affine, row major (16 floats), in global positions. No GUI code."""

import math

ID = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
TOL = 1e-9


class SymmetryError(Exception):
    pass


# ---- transforms


def rotation(deg, cx=0.0, cy=0.0):
    """Turn by deg about the z axis through (cx, cy)."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [c, -s, 0, cx - c * cx + s * cy, s, c, 0, cy - s * cx - c * cy, 0, 0, 1, 0, 0, 0, 0, 1]


def mirror_plane(base, normal):
    """Mirror about the plane through base with the (unit) normal; the normal has no z component."""
    nx, ny = normal[0], normal[1]
    d = 2 * (nx * base[0] + ny * base[1])
    return [1 - 2 * nx * nx, -2 * nx * ny, 0, d * nx, -2 * nx * ny, 1 - 2 * ny * ny, 0, d * ny, 0, 0, 1, 0, 0, 0, 0, 1]


def compose(*ms):
    """compose(A, B) applies B first, then A."""
    out = ID
    for m in ms:
        out = [sum(out[4 * i + k] * m[4 * k + j] for k in range(4)) for i in range(4) for j in range(4)]
    return out


def apply(m, p):
    """The point p (x, y, z) moved by m."""
    return [sum(m[4 * i + k] * v for k, v in enumerate((*p, 1))) for i in range(3)]


def det(m):
    """Determinant of the 3x3 linear part: negative for a mirror."""
    a = m
    return (
        a[0] * (a[5] * a[10] - a[6] * a[9]) - a[1] * (a[4] * a[10] - a[6] * a[8]) + a[2] * (a[4] * a[9] - a[5] * a[8])
    )


def _placement(obj):
    return list(obj.Placement.toMatrix().A)


def _key(m):
    return tuple(round(v, 9) + 0.0 for v in m)


# ---- the chain


def _name(obj):
    return f"{obj.Label} ({obj.TypeId})"


def _is_array(obj):
    return obj.TypeId == "Part::FeaturePython" and getattr(obj, "ArrayType", None) is not None


def _is_fragments(obj):
    return obj.TypeId == "Part::FeaturePython" and hasattr(obj, "Objects") and not hasattr(obj, "ArrayType")


def _is_leaf(obj):
    """A drawn body: it has a shape and is not made from other objects."""
    return hasattr(obj, "Shape") and not any(
        obj.getTypeIdOfProperty(p).startswith("App::PropertyLink") for p in obj.PropertiesList
    )


def _merge(parts):
    out = {}
    for part in parts:
        for name, (body, ts) in part.items():
            out.setdefault(name, (body, []))[1].extend(ts)
    return out


def _walk(obj):
    """{body name: (body, transforms)}: where each cell body below obj has been copied to, in obj's shape."""
    if obj.TypeId == "Part::Compound":
        found = _merge(_walk(o) for o in obj.Links)
    elif obj.TypeId == "Part::Mirroring":
        n = obj.Normal
        length = math.sqrt(n.x**2 + n.y**2 + n.z**2)
        if length == 0 or abs(n.z) > TOL * length:
            raise SymmetryError(f"{_name(obj)}: the mirror plane must contain the Z axis (2D, XY plane only)")
        m = mirror_plane((obj.Base.x, obj.Base.y), (n.x / length, n.y / length))
        found = {k: (b, [compose(m, t) for t in ts]) for k, (b, ts) in _walk(obj.Source).items()}
    elif _is_array(obj):
        found = _array(obj)
    elif _is_fragments(obj):
        found = _merge(_walk(o) for o in obj.Objects)
    elif obj.TypeId == "Part::Feature" or _is_leaf(obj):
        return {obj.Name: (obj, [compose(_placement_free(obj))])}
    else:
        raise SymmetryError(f"{_name(obj)} is not supported in a Symmetric Mesh chain")
    p = _placement(obj)
    return {k: (b, [compose(p, t) for t in ts]) for k, (b, ts) in found.items()}


def _placement_free(obj):
    return ID


def _array(obj):
    if obj.ArrayType != "polar":
        raise SymmetryError(f"{_name(obj)}: only polar arrays are supported")
    axis = obj.Axis
    if abs(axis.x) > TOL or abs(axis.y) > TOL or abs(axis.z) < TOL:
        raise SymmetryError(f"{_name(obj)}: the array axis must be Z")
    if abs(obj.IntervalAxis.x) > TOL or abs(obj.IntervalAxis.y) > TOL or abs(obj.IntervalAxis.z) > TOL:
        raise SymmetryError(f"{_name(obj)}: the array interval along the axis must be zero")
    n, angle = int(obj.NumberPolar), float(obj.Angle)
    step = angle / n if abs(angle) == 360 else angle / (n - 1)
    step = step if axis.z > 0 else -step
    sub = _walk(obj.Base)
    c = obj.Center
    return {
        k: (b, [compose(rotation(i * step, c.x, c.y), t) for i in range(n) for t in ts]) for k, (b, ts) in sub.items()
    }


def read_chain(top):
    """(cell bodies in first-seen order, transforms) of the chain whose top object is top.

    The transforms are those of the first cell body, identity first; every cell body must have the same set."""
    found = _walk(top)
    sets = {}
    for name, (body, ts) in found.items():
        unique = {}
        for t in ts:
            unique.setdefault(_key(t), t)
        sets[name] = unique
    first = next(iter(sets.values()))
    for name, unique in sets.items():
        if unique.keys() != first.keys():
            raise SymmetryError(
                f"{found[name][0].Label} is not copied the same way as the other cell bodies: "
                "every body of the cell must go through the same Mirror and Polar Array"
            )
    return [b for b, _ in found.values()], list(first.values())
