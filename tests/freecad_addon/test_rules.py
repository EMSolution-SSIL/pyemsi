"""The rule engine: ordered mirror, rotation and translation rules become rigid transforms and part names."""

import pytest

from emsolution.symmetry import (
    ID,
    MAX_DRAWN,
    apply,
    compose,
    copies,
    copy_count,
    det,
    part_names,
    rotation_about,
    rule_matrix,
    rule_problems,
    rule_warnings,
    transforms,
    translation,
)

MIRROR_X0 = {"kind": "mirror", "point": [0, 0, 0], "normal": [1, 0, 0]}
TWO_24 = {"kind": "translate", "vector": [24, 0, 0], "count": 2}


def ROT(step, n, axis=(0, 0, 1), point=(0, 0, 0)):
    return {"kind": "rotate", "point": list(point), "axis": list(axis), "step": step, "count": n}


def xs(rules, x=5.0):
    return [round(apply(t, [x, 0, 0])[0], 6) for t in transforms(rules)]


def test_mirror_then_translate():  # T-01
    assert xs([MIRROR_X0, TWO_24]) == [5, -5, 29, 19]


def test_translate_then_mirror():  # T-02
    assert xs([TWO_24, MIRROR_X0]) == [5, 29, -5, -29]


def test_numbering_has_the_last_rule_slowest():
    assert copies([MIRROR_X0, ROT(90, 2)]) == [(0, 0), (1, 0), (0, 1), (1, 1)]


def test_identity_first():
    assert transforms([MIRROR_X0, ROT(90, 4)])[0] == ID


def test_no_rules_is_one_copy():
    assert transforms([]) == [ID]


def test_rotation_about_an_oblique_axis_through_a_point():
    t = rule_matrix(ROT(120, 3, axis=(1, 1, 1), point=(1, 0, 0)))
    assert apply(t, [2, 0, 0]) == pytest.approx([1, 1, 0])


def test_mirror_normal_need_not_be_unit():
    m = rule_matrix({"kind": "mirror", "point": [0, 0, 2], "normal": [0, 0, 5]})
    assert apply(m, [1, 1, 3]) == pytest.approx([1, 1, 1]) and det(m) == pytest.approx(-1)


def test_a_screw_step_goes_through_the_engine():
    screw = compose(translation([0, 0, 4]), rotation_about([0, 0, 0], [0, 0, 1], 6))
    assert apply(transforms([{"kind": "motion", "matrix": screw, "count": 3}])[2], [1, 0, 0])[2] == pytest.approx(8)


@pytest.mark.parametrize(
    "rule,plane,text",
    [
        (ROT(30, 2, axis=(1, 0, 0)), "XY", "axis"),
        ({"kind": "mirror", "point": [0, 0, 0], "normal": [0, 0, 1]}, "XY", "normal"),
        (ROT(30, 2, axis=(0, 1, 0)), "ZX", "rotation"),
        ({"kind": "mirror", "point": [0, 0, 0], "normal": [1, 0, 0]}, "ZX", "normal"),
        ({"kind": "translate", "vector": [1, 0, 0], "count": 2}, "ZX", "translation"),
        (ROT(30, 1), "", "count"),
        ({"kind": "mirror", "point": [0, 0, 0], "normal": [0, 0, 0]}, "", "normal"),
    ],
)
def test_rule_problems(rule, plane, text):
    assert text in " ".join(rule_problems([rule], plane))


def test_identical_copies_are_refused():
    assert "identical" in " ".join(rule_problems([MIRROR_X0, MIRROR_X0], ""))
    assert "identical" in " ".join(rule_problems([ROT(90, 5)], ""))


def test_any_3d_axis_is_accepted():
    assert rule_problems([ROT(45, 8, axis=(1, 2, 3))], "") == []


def test_rotation_that_does_not_close_warns():
    assert "360" in " ".join(rule_warnings([ROT(30, 11)])) and rule_warnings([ROT(30, 12)]) == []


def test_part_names():
    rules = [MIRROR_X0, ROT(120, 3)]
    assert part_names({"mode": "one"}, rules, "Iron") == ["Iron"] * 6
    assert len(set(part_names({"mode": "each"}, rules, "S"))) == 6
    assert part_names({"mode": "across", "across": [0]}, rules, "C") == ["C_1", "C_1", "C_2", "C_2", "C_3", "C_3"]
    assert part_names({"mode": "table", "table": list("abcdef")}, rules, "x") == list("abcdef")


def test_huge_count_is_a_problem():
    assert "copies" in " ".join(rule_problems([ROT(0.001, 100000)], ""))
    assert copy_count([ROT(0.001, 100000)]) > MAX_DRAWN
