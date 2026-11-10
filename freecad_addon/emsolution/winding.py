"""Winding table generator: part names for a three-phase winding. Pure Python, no FreeCAD."""

import math

SECTORS = ["A+", "C-", "B+", "A-", "C+", "B-"]


def _sector(k, slots, pole_pairs):
    return ((k * pole_pairs * 360 + 30 * slots) % (360 * slots)) // (60 * slots)


def _coil(c):
    return f"Coil{c + 1:02d}"


def two_layer(slots, pole_pairs, span, per_coil=False):
    """Part names (top, bottom), each by slot. The bottom of slot k is coil k - span, on its return side."""
    top, bottom = [], []
    for k in range(slots):
        c = (k - span) % slots
        if per_coil:
            top.append(_coil(k))
            bottom.append(_coil(c))
        else:
            top.append(SECTORS[_sector(k, slots, pole_pairs)])
            bottom.append(SECTORS[(_sector(c, slots, pole_pairs) + 3) % 6])
    return top, bottom


def whole_coils(slots, pole_pairs, per_coil=False):
    """One name per coil, for an object that is a whole coil."""
    if per_coil:
        return [_coil(k) for k in range(slots)]
    return [SECTORS[_sector(k, slots, pole_pairs)] for k in range(slots)]


def slot_of(centres, point, axis, slots):
    """Slot of each copy: its centre's angle about the axis through point, from the first copy, over the pitch."""
    n = math.sqrt(sum(a * a for a in axis))
    w = [a / n for a in axis]
    ref = None
    out = []
    for c in centres:
        v = [c[i] - point[i] for i in range(3)]
        d = sum(v[i] * w[i] for i in range(3))
        v = [v[i] - d * w[i] for i in range(3)]
        if ref is None:
            ref = v
        cross = [ref[1] * v[2] - ref[2] * v[1], ref[2] * v[0] - ref[0] * v[2], ref[0] * v[1] - ref[1] * v[0]]
        delta = math.degrees(math.atan2(sum(cross[i] * w[i] for i in range(3)), sum(ref[i] * v[i] for i in range(3))))
        out.append(round(delta / (360 / slots)) % slots)
    return out


def by_copy(names_by_slot, slots_of_copies):
    """The name of each copy, from the name of its slot."""
    return [names_by_slot[s] for s in slots_of_copies]
