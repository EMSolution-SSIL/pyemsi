"""The winding table generator: part names for a three-phase winding, by slot or by copy."""

import math
import re
from collections import Counter

from emsolution.winding import by_copy, slot_of, two_layer, whole_coils


def _centres():
    out = []
    for slot in range(3):
        for off in (-2.5, 2.5):
            a = math.radians(slot * 30 + off)
            out.append((10 * math.cos(a), 10 * math.sin(a), 0.0))
    return out


def test_36_slots_4_poles_span_8():  # M2-15
    top, bottom = two_layer(36, 2, 8)
    assert top[:8] == ["A+", "A+", "C-", "C-", "C-", "B+", "B+", "B+"]
    assert bottom[:3] == ["A+", "C-", "C-"]


def test_27_slots_6_poles_fractional():  # M2-16: q = 1.5
    top, _ = two_layer(27, 3, 4)
    assert top[:9] == ["A+", "C-", "C-", "B+", "A-", "A-", "C+", "B-", "B-"]
    assert Counter(n[0] for n in top) == {"A": 9, "B": 9, "C": 9}


def test_bottom_layer_is_the_top_moved_by_the_span_and_reversed():
    top, bottom = two_layer(30, 2, 7)
    flip = {"+": "-", "-": "+"}
    assert all(bottom[k] == top[k - 7][0] + flip[top[k - 7][1]] for k in range(30))


def test_span_one_gives_concentrated():  # M2-08
    top, bottom = two_layer(9, 4, 1)
    assert all(bottom[k][0] == top[k - 1][0] for k in range(9))


def test_per_coil_names():
    top, bottom = two_layer(36, 2, 8, per_coil=True)
    assert top[0] == "Coil01" and bottom[0] == "Coil29"


def test_whole_coils_one_row():
    assert whole_coils(36, 2)[:3] == ["A+", "A+", "C-"]
    assert whole_coils(6, 1, per_coil=True) == [f"Coil{k:02d}" for k in range(1, 7)]


def test_slot_of_a_mirrored_half_cell():  # centres at +-2.5 degrees about each slot axis, 30 degree pitch
    assert slot_of(_centres(), (0, 0, 0), (0, 0, 1), 12) == [0, 0, 1, 1, 2, 2]


def test_slot_of_uses_the_axis_sense_and_any_length():
    assert slot_of(_centres(), (0, 0, 0), (0, 0, -2), 12) == [0, 0, 11, 11, 10, 10]


def test_by_copy_indexes():
    assert by_copy(["x", "y", "z"], [2, 0, 0]) == ["z", "x", "x"]


def test_names_stay_different_in_the_mesh():  # objects.clean maps + to _, keeps -
    assert len({re.sub(r"[^A-Za-z0-9_-]", "_", n) for n in two_layer(36, 2, 8)[0]}) == 6
