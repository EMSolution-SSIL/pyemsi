"""Symmetric Mesh: read the copy transforms from the objects the user drew the full geometry with.

The user draws a cell and builds the whole 2D geometry from it with Part Mirror, Draft Polar Array and Part
Compound / Boolean Fragments. read_chain walks that chain from its top object down to the cell bodies and returns
where every copy of the cell lies. Transforms are 4x4 affine, row major (16 floats), in global positions. No GUI code."""

import itertools
import math

ID = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
TOL = 1e-9
MAX_DRAWN = 5000


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


# ---- rules: ordered mirror, rotation and translation steps


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def _norm(v):
    return math.sqrt(sum(c * c for c in v))


def translation(v):
    """Move by the vector v."""
    return [1, 0, 0, v[0], 0, 1, 0, v[1], 0, 0, 1, v[2], 0, 0, 0, 1]


def rotation_about(point, axis, deg):
    """Turn by deg about the axis (any direction) through point."""
    x, y, z = _unit(axis)
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    t = 1 - c
    r = [t * x * x + c, t * x * y - s * z, t * x * z + s * y, t * x * y + s * z, t * y * y + c, t * y * z - s * x]
    r += [t * x * z - s * y, t * y * z + s * x, t * z * z + c]
    p = point
    off = [p[i] - (r[3 * i] * p[0] + r[3 * i + 1] * p[1] + r[3 * i + 2] * p[2]) for i in range(3)]
    return [*r[0:3], off[0], *r[3:6], off[1], *r[6:9], off[2], 0, 0, 0, 1]


def _mirror(point, normal):
    n = _unit(normal)
    d = 2 * sum(a * b for a, b in zip(n, point))
    m = [(1.0 if i == j else 0.0) - 2 * n[i] * n[j] for i in range(3) for j in range(3)]
    return [*m[0:3], d * n[0], *m[3:6], d * n[1], *m[6:9], d * n[2], 0, 0, 0, 1]


def rule_matrix(rule):
    """The rigid motion G of one rule."""
    kind = rule["kind"]
    if kind == "mirror":
        return _mirror(rule["point"], rule["normal"])
    if kind == "rotate":
        return rotation_about(rule["point"], rule["axis"], rule["step"])
    if kind == "translate":
        return translation(rule["vector"])
    return [float(v) for v in rule["matrix"]]


def rule_count(rule):
    """Copies a rule makes, the original included."""
    return 2 if rule["kind"] == "mirror" else int(rule["count"])


def copy_count(rules):
    n = 1
    for r in rules:
        n *= rule_count(r)
    return n


def copies(rules):
    """Index of every copy in each rule: the first rule is the fastest, the all-zero copy (the drawn cell) is first."""
    counts = [rule_count(r) for r in rules]
    return [tuple(reversed(i)) for i in itertools.product(*[range(n) for n in reversed(counts)])]


def transforms(rules):
    """The transform of every copy, in the order of copies(): Rm^im after ... after R1^i1."""
    powers = []
    for r in rules:
        g, ps = rule_matrix(r), [ID]
        for _ in range(rule_count(r) - 1):
            ps.append(compose(g, ps[-1]))
        powers.append(ps)
    return [compose(*[powers[k][i] for k, i in reversed(list(enumerate(idx)))]) for idx in copies(rules)]


def _rule_problem(n, rule, plane):
    """What is wrong with one rule (numbered n from 1), or None."""
    kind = rule["kind"]
    who = f"Rule {n}"
    if kind != "mirror" and not (isinstance(rule.get("count"), int) and rule["count"] >= 2):
        return f"{who}: the count must be 2 or more."
    if kind == "mirror" and _norm(rule["normal"]) < TOL:
        return f"{who}: the mirror normal is zero."
    if kind == "rotate" and _norm(rule["axis"]) < TOL:
        return f"{who}: the rotation axis is zero."
    if kind == "translate" and _norm(rule["vector"]) < TOL:
        return f"{who}: the translation vector is zero."
    if plane == "XY":
        if kind == "mirror" and abs(rule["normal"][2]) > TOL * _norm(rule["normal"]):
            return f"{who}: the mirror normal must lie in the XY plane."
        if kind == "rotate" and _norm(rule["axis"][:2]) > TOL * _norm(rule["axis"]):
            return f"{who}: in 2D the rotation axis must be parallel to Z."
        if kind == "translate" and abs(rule["vector"][2]) > TOL:
            return f"{who}: the translation must lie in the XY plane."
        if kind == "motion" and any(abs(rule["matrix"][i]) > TOL for i in (2, 6, 8, 9, 11)):
            return f"{who}: the motion must stay in the XY plane."
    if plane == "ZX":
        if kind == "mirror" and _norm(rule["normal"][:2]) > TOL * _norm(rule["normal"]):
            return f"{who}: in an axisymmetric Study the mirror normal must be along Z."
        if kind in ("rotate", "motion"):
            return f"{who}: a rotation is not possible in an axisymmetric Study."
        if kind == "translate" and _norm(rule["vector"][:2]) > TOL:
            return f"{who}: in an axisymmetric Study the translation must be along Z."
    return None


def rule_problems(rules, plane):
    """Reasons the rules cannot be used. plane is '' (3D), 'XY' or 'ZX'."""
    out = []
    counts_ok = all(r["kind"] == "mirror" or (isinstance(r.get("count"), int) and r["count"] >= 2) for r in rules)
    too_many = counts_ok and copy_count(rules) > MAX_DRAWN
    if too_many:
        out.append(f"The rules make {copy_count(rules)} copies, more than the {MAX_DRAWN} allowed.")
    out += [p for p in (_rule_problem(n, r, plane) for n, r in enumerate(rules, 1)) if p]
    if not out:
        keys = [_key(t) for t in transforms(rules)]
        if len(set(keys)) < len(keys):
            out.append("Some copies are identical: a rule repeats another or comes back to the start too early.")
    return out


def rule_warnings(rules):
    out = []
    for n, r in enumerate(rules, 1):
        if r["kind"] == "rotate" and abs(r["step"] * r["count"] - 360) > 1e-6:
            out.append(f"Rule {n}: the rotation covers {r['step'] * r['count']:g} degrees, not 360.")
    return out


# ---- parts


def part_names(row, rules, label):
    """The part name of every copy of one cell object."""
    mode = row.get("mode", "one")
    idx = copies(rules)
    if mode == "each":
        return [f"{label}_{i + 1}" for i in range(len(idx))]
    if mode == "table":
        return list(row["table"])
    if mode == "across":
        across = set(row.get("across", []))
        rest = [tuple(v for k, v in enumerate(i) if k not in across) for i in idx]
        number = {}
        for r in rest:
            number.setdefault(r, len(number) + 1)
        return [f"{label}_{number[r]}" for r in rest]
    return [label] * len(idx)


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


def _in_table(obj):
    return obj.TypeId in ("Part::Compound", "Part::Mirroring") or _is_array(obj) or _is_fragments(obj)


def _is_leaf(obj):
    """A drawn body: it has a shape and nothing it is made from is a Mirror, Array, Compound or Fragments."""
    return hasattr(obj, "Shape") and not any(_in_table(o) for o in obj.OutListRecursive)


def _cuts_a_cell(obj):
    """A Boolean Fragments with something below it but no Mirror or Polar Array: it cuts cell faces into blocks, so it
    is one cell body with several faces, as a Fragments body is in a Study without a Symmetric Mesh."""
    copies = any(o.TypeId == "Part::Mirroring" or _is_array(o) for o in obj.OutListRecursive)
    return _is_fragments(obj) and bool(obj.Objects) and not copies


def _merge(parts):
    out = {}
    for part in parts:
        for name, (body, ts) in part.items():
            out.setdefault(name, (body, []))[1].extend(ts)
    return out


def _below(obj, prop):
    """What obj's prop links to; SymmetryError when it links to nothing."""
    value = getattr(obj, prop)
    if value is None or (isinstance(value, (list, tuple)) and not value):
        raise SymmetryError(f"{_name(obj)} has no {prop}: it builds nothing")
    return value


def _walk(obj):
    """{body name: (body, transforms)}: where each cell body below obj has been copied to, in obj's shape."""
    if obj.TypeId == "Part::Compound":
        found = _merge(_walk(o) for o in _below(obj, "Links"))
    elif obj.TypeId == "Part::Mirroring":
        n = obj.Normal
        length = math.sqrt(n.x**2 + n.y**2 + n.z**2)
        if length == 0 or abs(n.z) > TOL * length:
            raise SymmetryError(f"{_name(obj)}: the mirror plane must contain the Z axis")
        m = mirror_plane((obj.Base.x, obj.Base.y), (n.x / length, n.y / length))
        found = {k: (b, [compose(m, t) for t in ts]) for k, (b, ts) in _walk(_below(obj, "Source")).items()}
    elif _is_array(obj):
        found = _array(obj)
    elif _cuts_a_cell(obj):
        return {obj.Name: (obj, [ID])}  # a cell body, like a leaf
    elif _is_fragments(obj):
        found = _merge(_walk(o) for o in _below(obj, "Objects"))
    elif _is_leaf(obj):
        return {obj.Name: (obj, [ID])}  # its shape already carries its own Placement
    else:
        raise SymmetryError(f"{_name(obj)} is not supported in a Symmetric Mesh chain")
    p = _placement(obj)
    return {k: (b, [compose(p, t) for t in ts]) for k, (b, ts) in found.items()}


def _array_step(obj):
    """(copies, turn between copies in degrees) of a polar array about +Z or -Z."""
    n, angle = int(obj.NumberPolar), float(obj.Angle)
    if n < 1 or (n == 1 and angle != 360):
        raise SymmetryError(f"{_name(obj)}: a polar array needs at least 2 copies (it has {n})")
    step = angle / n if angle == 360 else angle / (n - 1)  # Draft's rule: only exactly 360 is a full turn
    return n, step if obj.Axis.z > 0 else -step


def _array(obj):
    if obj.ArrayType != "polar":
        raise SymmetryError(f"{_name(obj)}: only polar arrays are supported")
    axis = obj.Axis
    if abs(axis.x) > TOL or abs(axis.y) > TOL or abs(axis.z) < TOL:
        raise SymmetryError(f"{_name(obj)}: the array axis must be Z")
    if abs(obj.IntervalAxis.x) > TOL or abs(obj.IntervalAxis.y) > TOL or abs(obj.IntervalAxis.z) > TOL:
        raise SymmetryError(f"{_name(obj)}: the array interval along the axis must be zero")
    n, step = _array_step(obj)
    sub = _walk(_below(obj, "Base"))
    c = obj.Center
    return {
        k: (b, [compose(rotation(i * step, c.x, c.y), t) for i in range(n) for t in ts]) for k, (b, ts) in sub.items()
    }


def read_chain(top):
    """(cell bodies in first-seen order, transforms) of the chain whose top object is top.

    The transforms are those of the first cell body, identity first; every cell body must have the same set."""
    found = _walk(top)
    if not found:
        raise SymmetryError(f"{_name(top)} holds no cell body")
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
    ident = _key(ID)
    transforms = [first[ident]] if ident in first else []
    transforms += [t for k, t in first.items() if k != ident]
    # the chain sits in its containers (App::Part): move the transforms into the global frame of global_shape
    outer = top.getGlobalPlacement().multiply(top.Placement.inverse())
    if not outer.isIdentity():
        c, back = list(outer.toMatrix().A), list(outer.inverse().toMatrix().A)
        transforms = [ID if _key(t) == ident else compose(c, t, back) for t in transforms]
    return [b for b, _ in found.values()], transforms


def _num(v):
    return f"{round(v, 6) + 0.0:g}"


def _chain_steps(obj):
    """The Mirror and Array objects below obj, outermost first."""
    if obj.TypeId == "Part::Mirroring":
        return [obj] + _chain_steps(_below(obj, "Source"))
    if _is_array(obj):
        return [obj] + _chain_steps(_below(obj, "Base"))
    kids = _below(obj, "Links") if obj.TypeId == "Part::Compound" else obj.Objects if _is_fragments(obj) else []
    return [s for k in kids for s in _chain_steps(k)]


def steps(top):
    """One line per Mirror and Polar Array below top, in the order they are applied (the cell first), e.g.
    "mirror (0, 0) 15°" or "rotate (0, 0) 30° × 12". Raises SymmetryError like read_chain."""
    out = []
    for obj in reversed(list(dict.fromkeys(_chain_steps(top)))):
        if obj.TypeId == "Part::Mirroring":
            n, b = obj.Normal, obj.Base
            length = math.hypot(n.x, n.y)
            if length == 0:
                raise SymmetryError(f"{_name(obj)}: the mirror plane must contain the Z axis")
            nx, ny = n.x / length, n.y / length
            d = nx * b.x + ny * b.y  # the foot of the perpendicular from the origin, on the mirror line
            angle = math.degrees(math.atan2(-nx, ny)) % 180
            out.append(f"mirror ({_num(d * nx)}, {_num(d * ny)}) {_num(angle)}°")
        else:
            n, step = _array_step(obj)
            out.append(f"rotate ({_num(obj.Center.x)}, {_num(obj.Center.y)}) {_num(step)}° × {n}")
    return out
