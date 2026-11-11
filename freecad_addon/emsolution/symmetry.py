"""Symmetric Groups: the copies that ordered mirror, rotation and translation rules make, and the parts they belong to.

A drawing built with Part Mirror, Draft Polar Array and Part Compound / Boolean Fragments can fill a group:
rules_from_chain walks that chain from its top object down to the cell bodies and reads it as ordered rules. Mirror
planes and array axes may lie any way.
Transforms are 4x4 affine, row major (16 floats), in global positions. No GUI code."""

import collections
import itertools
import math

import numpy as np

ID = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
TOL = 1e-9
MAX_DRAWN = 5000
STRUCTURE_LIMIT = 2_000_000  # steps y1^-1 D y2 above which relative_transforms sweeps the pairs of copies instead
BLOCK = 100_000  # transforms formed at once by numpy


class SymmetryError(Exception):
    pass


# ---- transforms


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


def inverse(m):
    """The inverse of the affine transform m."""
    a, d = m, det(m)
    r = [
        [a[5] * a[10] - a[6] * a[9], a[2] * a[9] - a[1] * a[10], a[1] * a[6] - a[2] * a[5]],
        [a[6] * a[8] - a[4] * a[10], a[0] * a[10] - a[2] * a[8], a[2] * a[4] - a[0] * a[6]],
        [a[4] * a[9] - a[5] * a[8], a[1] * a[8] - a[0] * a[9], a[0] * a[5] - a[1] * a[4]],
    ]
    r = [[v / d for v in row] for row in r]
    off = [-sum(r[i][k] * a[4 * k + 3] for k in range(3)) for i in range(3)]
    return [*r[0], off[0], *r[1], off[1], *r[2], off[2], 0, 0, 0, 1]


def relative_transforms(rules, box=None):
    """The identity, then relative transforms m = T_i^-1 T_j (i != j) of the copies T the rules make: copy j lies as
    copy i would if the cell were moved by m. Each is listed once (by rounded key), and never beside its inverse: cells
    A and C overlap as A and m C exactly when C and m^-1 A do, and the overlap check tries both orders of the cells.
    Without box, one of m and m^-1 for every pair. With box (xmin, ymin, zmin, xmax, ymax, zmax), the bounding box of
    the drawn cells, at least that for every m that moves a point of the box into the box: two copies overlap only
    where the cells overlap their copies by T_i^-1 T_j, which then does so. first_pair names the copies of an m.
    The rules are split in three, P, M and S, each copy being s y p (p of P, y of M, s of S). P must close (each of
    its rules maps P's copies onto themselves, so they form a group G; it may be empty). Then T_i^-1 T_j =
    (p1^-1 y1^-1 D y2 p1)(p1^-1 p2) with D = s1^-1 s2, and the differences D are few when S closes too (D is one of
    S's copies), holds translations only (D moves by a sum of whole steps) or is one rule L (D = L^d). The split with
    the fewest steps y1^-1 D y2 is taken: the steps are pruned by the box of all of G's copies, conjugated by G and
    multiplied by G, so the pairs of copies are never visited. When every split has more steps than STRUCTURE_LIMIT,
    the pairs whose copies' boxes meet are found by a sweep instead."""
    split = _best_split(rules)
    if split is None:
        mats = _mats(transforms(rules))
        return _halved(_from_pairs(mats, *(np.triu_indices(len(mats), 1) if box is None else _meeting(mats, box))))
    return _halved(_structured(*split, box))


def _mats(ts):
    return np.array(ts, dtype=float).reshape(-1, 4, 4)


def _closes(rules, ts=None):
    """True if each rule's motion maps the copies the rules make onto themselves."""
    if any(r["kind"] == "translate" for r in rules):
        return False  # a translation moves the farthest copy along it farther: no finite set of copies is kept
    ts = transforms(rules) if ts is None else ts
    return all(_same_copies((compose(rule_matrix(r), t) for t in ts), ts) for r in rules)


def _signed(count):
    """0, 1, -1, 2, -2, ... up to count - 1: the whole steps between two of count copies, no step first."""
    return [0, *(x for d in range(1, count) for x in (d, -d))]


def _difference_count(rules, closes):
    """How many differences s1^-1 s2 of the copies of rules _differences lists, or None when they are not few.
    closes: whether the rules close."""
    if not rules or closes:
        return copy_count(rules)
    if all(r["kind"] == "translate" for r in rules) or len(rules) == 1:
        return math.prod(2 * rule_count(r) - 1 for r in rules)
    return None


def _differences(rules, closes):
    """Every s1^-1 s2 of two copies of rules (n x 4 x 4), no move first: their copies when they close, the sums of
    whole steps of translations, or L^d (-count < d < count) of one rule L."""
    if not rules or closes:
        return _mats(transforms(rules))
    if all(r["kind"] == "translate" for r in rules):
        steps = np.array(list(itertools.product(*[_signed(rule_count(r)) for r in rules])), dtype=float)
        out = np.tile(np.eye(4), (len(steps), 1, 1))
        out[:, :3, 3] = steps @ np.array([r["vector"] for r in rules], dtype=float)
        return out
    (rule,) = rules
    g, back, ups, downs = rule_matrix(rule), inverse(rule_matrix(rule)), [ID], [ID]
    for _ in range(rule_count(rule) - 1):
        ups.append(compose(g, ups[-1]))
        downs.append(compose(back, downs[-1]))
    return _mats([ID, *(m for pair in zip(ups[1:], downs[1:]) for m in pair)])


def _best_split(rules):
    """(G, M, D) as numpy arrays for the split P | M | S of the rules with the fewest steps y1^-1 D y2 (G: P's copies, M:
    the copies of the rules between, D: S's differences), or None when even that has more than STRUCTURE_LIMIT."""
    n = len(rules)
    known = {}

    def closes(a, b):
        if (a, b) not in known:
            known[a, b] = _closes(rules[a:b])
        return known[a, b]

    best = None
    for b in range(n + 1):
        count = _difference_count(rules[b:], b < n and closes(b, n))
        for a in [] if count is None else [a for a in range(b + 1) if closes(0, a)]:
            steps = copy_count(rules[a:b]) ** 2 * count
            if best is None or steps + copy_count(rules[:a]) < best[0]:
                best = (steps + copy_count(rules[:a]), steps, a, b)
    if best is None or best[1] > STRUCTURE_LIMIT:
        return None
    _, _, a, b = best
    return _mats(transforms(rules[:a])), _mats(transforms(rules[a:b])), _differences(rules[b:], b < n and closes(b, n))


def _keys(mats):
    """A key per transform of mats (n x 4 x 4), equal for transforms that round alike."""
    return [row.tobytes() for row in np.round(mats.reshape(-1, 16), 9) + 0.0]


def _distinct(mats):
    """mats (n x 4 x 4) each once by rounded value, in the order they first come."""
    if not len(mats):
        return mats
    _, first = np.unique(np.round(mats.reshape(-1, 16), 9) + 0.0, axis=0, return_index=True)
    return mats[np.sort(first)]


def _new(mats, seen):
    """The transforms of mats not in seen (keys), each once, in order; their keys are added to seen."""
    mats = _distinct(mats)
    keep = [k not in seen for k in _keys(mats)]
    seen.update(k for k, new in zip(_keys(mats), keep) if new)
    return mats[np.array(keep, dtype=bool)] if len(mats) else mats


def _halved(ts):
    """ts (a list, the identity first) without any transform whose inverse comes before it."""
    if len(ts) < 2:
        return ts
    mats = _mats(ts)
    kept, out = set(), []
    for m, key, back in zip(ts, _keys(mats), _keys(np.linalg.inv(mats))):
        if back not in kept:
            kept.add(key)
            out.append(m)
    return out


def _from_pairs(mats, firsts, seconds):
    """The identity, then mats[i]^-1 mats[j] of the pairs (firsts, seconds), each once, in the order of the pairs."""
    out, seen, backs = [ID], set(_keys(_mats([ID]))), np.linalg.inv(mats)
    for start in range(0, len(firsts), BLOCK):  # a bounded block of products at a time
        rel = np.matmul(backs[firsts[start : start + BLOCK]], mats[seconds[start : start + BLOCK]])
        out += _new(rel, seen).reshape(-1, 16).tolist()
    return out


def _structured(group, mid, differences, box):
    """The relative transforms of copies s y g (g of group, y of mid, s1^-1 s2 among differences), from the steps
    y1^-1 D y2, a bounded block of numpy products at a time."""
    block = None
    if box is not None:
        lows, highs = _boxes(group, box)
        block = (*lows.min(axis=0), *highs.max(axis=0))  # holds every copy of the cells that group makes
    backs, inverse_group = np.linalg.inv(mid), np.linalg.inv(group)
    out, seen, steps_seen, conj_seen = [ID], set(_keys(_mats([ID]))), set(), set()
    width = max(1, BLOCK // len(mid))  # differences per block: width x len(mid) steps
    per = max(1, BLOCK // len(group))  # steps (and conjugates) per block: per x len(group) products
    for back in backs:
        for start in range(0, len(differences), width):
            s = np.matmul(np.matmul(back, differences[start : start + width])[:, None], mid[None]).reshape(-1, 4, 4)
            s = _new(s[_onto(s, block)], steps_seen)  # the copies of the block by y1 s1 and by s2 y2 must meet
            for c0 in range(0, len(s), per):
                conj = np.matmul(np.matmul(inverse_group[None], s[c0 : c0 + per, None]), group[None])
                conj = _new(conj.reshape(-1, 4, 4), conj_seen)
                for c1 in range(0, len(conj), per):
                    ms = np.matmul(conj[c1 : c1 + per, None], group[None]).reshape(-1, 4, 4)
                    out += _new(ms[_onto(ms, box)], seen).reshape(-1, 16).tolist()
    return out


def first_pair(ts, m, tol=1e-6):
    """The first copies (i, j), i != j, with T_i^-1 T_j = m (T_j = T_i m), or (0, 0). A grid lookup keeps this linear."""
    index = {}
    for j, t in enumerate(ts):
        index.setdefault(next(_grid_keys(t, 0)), []).append(j)
    moved = np.matmul(_mats(ts), np.array(m, dtype=float).reshape(4, 4)).reshape(-1, 16).tolist()
    for i, t in enumerate(moved):
        for key in _grid_keys(t, tol):
            for j in index.get(key, ()):
                if j != i and max(abs(a - b) for a, b in zip(t, ts[j])) < tol:
                    return i, j
    return 0, 0


def _onto(mats, box):
    """For each transform of mats (n x 4 x 4), False only if it moves no point of the box into the box (their boxes
    are apart); all True without a box."""
    if box is None:
        return np.ones(len(mats), dtype=bool)
    lows, highs = _boxes(mats, box)
    return np.all((lows <= np.array(box[3:])) & (np.array(box[:3]) <= highs), axis=1)


def moved_box(m, box):
    """The bounding box (xmin, ymin, zmin, xmax, ymax, zmax) of the box moved by m, a little enlarged."""
    lows, highs = _boxes(_mats([m]), box)
    return (*lows[0].tolist(), *highs[0].tolist())


def boxes_meet(a, b):
    """True if two boxes (xmin, ymin, zmin, xmax, ymax, zmax) share a point."""
    return all(a[k] <= b[k + 3] and b[k] <= a[k + 3] for k in range(3))


def _boxes(mats, box):
    """(lows, highs), n x 3: the bounding box of box moved by each transform of mats (n x 4 x 4), a little enlarged."""
    corners = np.array([[x, y, z, 1.0] for x in box[0::3] for y in box[1::3] for z in box[2::3]])
    moved = np.einsum("nij,kj->nki", mats[:, :3, :], corners)
    tol = 1e-6 * max(1.0, math.dist(box[:3], box[3:]))
    return moved.min(axis=1) - tol, moved.max(axis=1) + tol


def _meeting(mats, box):
    """(i, j) arrays of the pairs i < j of copies whose boxes meet, in the order of i then j, by a sort and sweep along
    the axis the boxes spread most on."""
    lows, highs = _boxes(mats, box)
    axis = int(np.argmax(np.ptp(lows, axis=0)))
    order = np.argsort(lows[:, axis], kind="stable")
    lo, hi = lows[order], highs[order]
    ends = np.searchsorted(lo[:, axis], hi[:, axis], side="right")
    found = []
    for a in range(len(order)):
        b = np.arange(a + 1, ends[a])
        b = b[np.all((lo[b] <= hi[a]) & (lo[a] <= hi[b]), axis=1)]
        if len(b):
            found.append(np.stack([np.full(len(b), order[a]), order[b]]))
    if not found:
        return np.empty(0, dtype=int), np.empty(0, dtype=int)
    pairs = np.concatenate(found, axis=1)
    i, j = pairs.min(axis=0), pairs.max(axis=0)
    k = np.lexsort((j, i))
    return i[k], j[k]


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


def z_motion(m):
    """ "turn" for a rotation about Z through the origin, "mirror" for a mirror in a plane that contains Z or a mirror
    of z = const, None for any other motion."""
    t = TOL
    if any(abs(m[i]) > t for i in (2, 6, 8, 9)):
        return None
    if abs(m[10] - 1) < t:  # Z stays: a turn or a mirror about Z, both through the origin
        if any(abs(m[i]) > t for i in (3, 7, 11)):
            return None
        return "turn" if det(m) > 0 else "mirror"
    if abs(m[10] + 1) < t:  # z flips: only a mirror of z = const leaves x and y alone
        same = abs(m[0] - 1) < t and abs(m[5] - 1) < t and abs(m[1]) < t and abs(m[4]) < t
        return "mirror" if same and abs(m[3]) < t and abs(m[7]) < t else None
    return None


def turns_about_z(rules):
    """The copies a group makes around Z: the product of the counts of its rotations about Z through the origin."""
    turns = 1
    for rule in rules:
        if z_motion(rule_matrix(rule)) == "turn":
            turns *= rule_count(rule)
    return turns


def copy_count(rules):
    n = 1
    for r in rules:
        n *= rule_count(r)
    return n


def copies(rules):
    """Index of every copy in each rule: the first rule is the fastest, the all-zero copy (the drawn cell) is first."""
    counts = [rule_count(r) for r in rules]
    return [tuple(reversed(i)) for i in itertools.product(*[range(n) for n in reversed(counts)])]


def _each_transform(rules):
    """transforms(rules), one at a time: a caller may stop at the first that does not fit."""
    powers = []
    for r in rules:
        g, ps = rule_matrix(r), [ID]
        for _ in range(rule_count(r) - 1):
            ps.append(compose(g, ps[-1]))
        powers.append(ps)
    for idx in copies(rules):
        yield compose(*[powers[k][i] for k, i in reversed(list(enumerate(idx)))])


def transforms(rules):
    """The transform of every copy, in the order of copies(): Rm^im after ... after R1^i1."""
    return list(_each_transform(rules))


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
        if r["kind"] == "rotate" and abs(abs(r["step"] * r["count"]) - 360) > 1e-6:
            out.append(f"Rule {n}: the rotation covers {abs(r['step'] * r['count']):g} degrees, not 360.")
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
    is one cell body with several faces, as a Fragments body is in a Study without a Symmetric Group."""
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


def _vec(v):
    return [v.x, v.y, v.z]


def _mirror_of(obj):
    """The motion of a Part Mirror; its plane may lie any way."""
    n = obj.Normal
    if n.Length == 0:
        raise SymmetryError(f"{_name(obj)}: the mirror normal is zero")
    return _mirror(_vec(obj.Base), _vec(n))


def _walk(obj):
    """{body name: (body, transforms)}: where each cell body below obj has been copied to, in obj's shape."""
    if obj.TypeId == "Part::Compound":
        found = _merge(_walk(o) for o in _below(obj, "Links"))
    elif obj.TypeId == "Part::Mirroring":
        m = _mirror_of(obj)
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
        raise SymmetryError(f"{_name(obj)} is not supported in a Symmetric Group chain")
    p = _placement(obj)
    return {k: (b, [compose(p, t) for t in ts]) for k, (b, ts) in found.items()}


def _array_step(obj):
    """(copies, turn between copies in degrees) of a polar array, about its own axis (right-handed, as Draft turns)."""
    n, angle = int(obj.NumberPolar), float(obj.Angle)
    if n < 1 or (n == 1 and angle != 360):
        raise SymmetryError(f"{_name(obj)}: a polar array needs at least 2 copies (it has {n})")
    step = angle / n if angle == 360 else angle / (n - 1)  # Draft's rule: only exactly 360 is a full turn
    return n, step


def _array(obj):
    if obj.ArrayType != "polar":
        raise SymmetryError(f"{_name(obj)}: only polar arrays are supported")
    if obj.Axis.Length < TOL:
        raise SymmetryError(f"{_name(obj)}: the array axis is zero")
    if abs(obj.IntervalAxis.x) > TOL or abs(obj.IntervalAxis.y) > TOL or abs(obj.IntervalAxis.z) > TOL:
        raise SymmetryError(f"{_name(obj)}: the array interval along the axis must be zero")
    n, step = _array_step(obj)
    sub = _walk(_below(obj, "Base"))
    c, axis = _vec(obj.Center), _vec(obj.Axis)
    turns = [rotation_about(c, axis, i * step) for i in range(n)]
    return {k: (b, [compose(turn, t) for turn in turns for t in ts]) for k, (b, ts) in sub.items()}


def _unique(ts):
    """{key: transform} of ts, each copy once."""
    out = {}
    for t in ts:
        out.setdefault(_key(t), t)
    return out


def _outer(top):
    """The placement of the containers (App::Part) that the chain's top sits in."""
    return top.getGlobalPlacement().multiply(top.Placement.inverse())


# ---- reading rules from a chain


Proposal = collections.namedtuple("Proposal", "cells rules")
MAX_ORDERS = 6  # steps of one body whose orders are all tried


def _step_objects(obj):
    """{body name: [Mirror and Polar Array objects on its ways up to obj]}, the ones nearest the body first. Call after
    _walk, which refuses what a chain cannot hold."""
    if obj.TypeId == "Part::Mirroring" or _is_array(obj):
        below = _step_objects(_below(obj, "Source" if obj.TypeId == "Part::Mirroring" else "Base"))
        return {k: [*steps, obj] for k, steps in below.items()}
    if obj.TypeId == "Part::Compound" or (_is_fragments(obj) and not _cuts_a_cell(obj)):
        out = {}
        for kid in _below(obj, "Links" if obj.TypeId == "Part::Compound" else "Objects"):
            for k, steps in _step_objects(kid).items():
                have = out.setdefault(k, [])
                have += [s for s in steps if s.Name not in {h.Name for h in have}]
        return out
    return {obj.Name: []}


def _clean(v):
    return [round(c, 9) + 0.0 for c in v]


def _step_rule(obj, outer):
    """The rule of a Mirror or Polar Array object, in global positions (outer: the containers' placement)."""
    if obj.TypeId == "Part::Mirroring":
        normal = _unit(_vec(outer.Rotation.multVec(obj.Normal)))
        return {"kind": "mirror", "point": _clean(_vec(outer.multVec(obj.Base))), "normal": _clean(normal)}
    n, step = _array_step(obj)
    axis = _unit(_vec(outer.Rotation.multVec(obj.Axis)))
    point = _clean(_vec(outer.multVec(obj.Center)))
    return {"kind": "rotate", "point": point, "axis": _clean(axis), "step": round(step, 9) + 0.0, "count": n}


GRID = 1e-4  # cell size of the transform lookup; a match must be closer than the tolerance, far below it
GRID_SHIFT = 0.3183  # keeps 0, 1 and 0.5 off the cell borders


def _grid_keys(t, tol):
    """The lookup cells a transform within tol of t can lie in: its own, and across a border it is within tol of."""
    options = []
    for v in t:
        s = v / GRID + GRID_SHIFT
        cell = math.floor(s)
        near = [cell - 1] if s - cell < tol / GRID else [cell + 1] if s - cell > 1 - tol / GRID else []
        options.append([cell, *near])
    return itertools.product(*options)


def _same_copies(a, b, tol=1e-6):
    """True if the transforms a (any iterable, read until the first that b lacks) are those of the list b, each once.
    A grid lookup keeps this linear in the number of copies."""
    index = {}
    for i, t in enumerate(b):
        index.setdefault(next(_grid_keys(t, 0)), []).append(i)
    used, n = set(), 0
    for t in a:
        hit = next(
            (
                i
                for key in _grid_keys(t, tol)
                for i in index.get(key, ())
                if i not in used and max(abs(x - y) for x, y in zip(t, b[i])) < tol
            ),
            None,
        )
        if hit is None:
            return False
        used.add(hit)
        n += 1
    return n == len(b)


def _fitting_rules(steps, outer, chain):
    """The rules of steps, in the first order whose copies are chain's; None if no order is. The number of copies is
    the same in every order, so a wrong number is refused at once, and a wrong order at its first stray copy."""
    rules = [_step_rule(s, outer) for s in steps]
    if copy_count(rules) != len(chain):
        return None
    orders = itertools.permutations(range(len(rules))) if len(rules) <= MAX_ORDERS else [range(len(rules))]
    for order in orders:
        ordered = [rules[i] for i in order]
        if _same_copies(_each_transform(ordered), chain):
            return ordered
    return None


def rules_from_chain(top):
    """[Proposal(cells, rules)] for the chain whose top object is top, in global positions: one per set of copies its
    cell bodies have, so branches with other copies are other proposals. Mirror planes and array axes may lie any way.
    SymmetryError explains a set of copies that no ordered list of the chain's steps gives exactly."""
    found = _walk(top)
    if not found:
        raise SymmetryError(f"{_name(top)} holds no cell body")
    steps = _step_objects(top)
    outer = _outer(top)
    c, back = list(outer.toMatrix().A), list(outer.inverse().toMatrix().A)
    sets = {}  # copy keys -> [body names]
    for name, (_, ts) in found.items():
        sets.setdefault(frozenset(_unique(ts)), []).append(name)
    out = []
    for key, names in sets.items():
        cells = [found[n][0] for n in names]
        if len(key) > MAX_DRAWN:
            labels = ", ".join(b.Label for b in cells)
            raise SymmetryError(f"{labels}: the chain makes {len(key)} copies, more than the {MAX_DRAWN} allowed.")
        chain = [compose(c, t, back) for t in _unique(found[names[0]][1]).values()]
        rules = _fitting_rules(steps[names[0]], outer, chain)
        if rules is None:
            labels = ", ".join(b.Label for b in cells)
            if not any(max(abs(x - y) for x, y in zip(t, ID)) < 1e-6 for t in chain):
                raise SymmetryError(
                    f"{labels}: none of the {len(chain)} copies the chain makes is the body where it is drawn, as a"
                    " Placement in the chain moves them all. Rules start from the drawn cell: reset that Placement, or"
                    " enter the rules by hand."
                )
            used = ", ".join(s.Label for s in steps[names[0]]) or "none"
            made = copy_count([_step_rule(s, outer) for s in steps[names[0]]])
            raise SymmetryError(
                f"{labels}: the chain makes {len(chain)} copies, and no ordered list of rules made of its steps"
                f" ({used}) gives exactly these: they make {made}. A Mirror or Polar Array that copies only part of"
                " what the steps before it made cannot be read as a rule. Enter the rules by hand."
            )
        out.append(Proposal(cells, rules))
    return out
