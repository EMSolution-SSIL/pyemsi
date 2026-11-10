"""The rule engine: ordered mirror, rotation and translation rules become rigid transforms and part names."""

import math
import time

import pytest

import FreeCAD as App
import Draft

from emsolution.symmetry import (
    GRID,
    GRID_SHIFT,
    ID,
    MAX_DRAWN,
    SymmetryError,
    _same_copies,
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
    rules_from_chain,
    transforms,
    translation,
)

from . import symcases

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


# ---- reading rules from a Mirror / Polar Array chain


@pytest.fixture
def motor():
    doc = App.newDocument("RulesFromChain")
    info = symcases.motor_doc(doc)
    info["doc"] = doc
    yield info
    App.closeDocument(doc.Name)


@pytest.fixture
def motor3d():
    doc = App.newDocument("RulesFromChain3D")
    info = symcases.motor_doc_3d(doc)
    info["doc"] = doc
    yield info
    App.closeDocument(doc.Name)


def test_chain_reads_as_rules(motor):
    (p,) = rules_from_chain(motor["stator_top"])
    assert p.cells == motor["stator_cells"]
    assert [r["kind"] for r in p.rules] == ["mirror", "rotate"] and p.rules[1]["count"] == 12
    assert p.rules[1]["step"] == pytest.approx(30)
    assert len(transforms(p.rules)) == 24


def test_chain_branches_with_different_copies_are_two_proposals(motor):
    doc = motor["doc"]
    stray = symcases.feature(doc, "StrayBody", symcases.sector(60, 62, 0, 15))
    pitch = doc.getObject("StatorPitch")
    pitch.Links = list(pitch.Links) + [stray]  # turned by the array, not mirrored
    doc.recompute()
    first, second = rules_from_chain(motor["stator_top"])
    assert first.cells == motor["stator_cells"] and [r["kind"] for r in first.rules] == ["mirror", "rotate"]
    assert second.cells == [stray] and [r["kind"] for r in second.rules] == ["rotate"]
    assert second.rules[0]["count"] == 12


def test_mirror_along_z_reads(motor3d):
    top = motor3d["stator_top"]
    motor3d["doc"].getObject("StatorMirror").Normal = App.Vector(0, 0, 1)
    motor3d["doc"].recompute()
    (p,) = rules_from_chain(top)
    assert p.rules[0]["kind"] == "mirror" and p.rules[0]["normal"] == pytest.approx([0, 0, 1])
    assert apply(transforms(p.rules)[1], [40, 1, 4]) == pytest.approx([40, 1, -4])
    assert len(transforms(p.rules)) == 24


def test_polar_axis_other_than_z_reads(motor3d):
    array = motor3d["doc"].getObjectsByLabel("StatorArray")[0]
    array.Axis = App.Vector(1, 0, 0)
    motor3d["doc"].recompute()
    (p,) = rules_from_chain(motor3d["stator_top"])
    assert p.rules[1]["kind"] == "rotate" and p.rules[1]["axis"] == pytest.approx([1, 0, 0])
    assert apply(transforms(p.rules)[2], [0, 1, 0]) == pytest.approx([0, math.cos(math.pi / 6), math.sin(math.pi / 6)])


def test_chain_in_a_moved_part_reads_rules_in_global_positions(motor):
    doc, top = motor["doc"], motor["stator_top"]
    part = doc.addObject("App::Part", "Holder")
    part.addObjects([top, *top.OutListRecursive])
    part.Placement = App.Placement(App.Vector(5, -3, 0), App.Rotation(App.Vector(0, 0, 1), 10))
    doc.recompute()
    (p,) = rules_from_chain(top)
    assert p.rules[1]["point"] == pytest.approx([5, -3, 0])
    assert len(transforms(p.rules)) == 24


def test_chain_that_is_no_rule_list_is_explained(motor):
    doc = motor["doc"]
    odd = doc.addObject("Part::Mirroring", "OddMirror")  # one more mirror of the cell only, beside the array
    odd.Source = doc.getObject("StatorCell")
    odd.Normal = App.Vector(-math.sin(math.radians(7)), math.cos(math.radians(7)), 0)
    frag = motor["stator_top"]
    frag.Objects = list(frag.Objects) + [odd]
    doc.recompute()
    with pytest.raises(SymmetryError, match=r"StatorIronCell.*25 copies.*ordered list of rules"):
        rules_from_chain(frag)


def test_large_chain_reads_quickly():
    """4000 copies: comparing the copies of each order of steps with the chain's must not be quadratic."""
    doc = App.newDocument("LargeChain")
    try:
        cell = symcases.feature(doc, "Tiny", symcases.sector(60, 61, 0, 0.05))
        array = Draft.make_polar_array(cell, number=4000, angle=360)
        doc.recompute()
        start = time.perf_counter()
        (p,) = rules_from_chain(array)
        assert p.rules[0]["count"] == 4000 and time.perf_counter() - start < 5
        odd = doc.addObject("Part::Mirroring", "OddMirror")  # 4001 copies, which no order of two steps makes
        odd.Source, odd.Normal = cell, App.Vector(0, 1, 0)
        both = doc.addObject("Part::Compound", "Both")
        both.Links = [array, odd]
        doc.recompute()
        start = time.perf_counter()
        with pytest.raises(SymmetryError, match="4001 copies"):
            rules_from_chain(both)
        assert time.perf_counter() - start < 5
        array.NumberPolar = MAX_DRAWN + 1
        doc.recompute()
        with pytest.raises(SymmetryError, match=f"{MAX_DRAWN + 1} copies, more than"):
            rules_from_chain(array)
    finally:
        App.closeDocument(doc.Name)


def test_copies_are_compared_in_linear_time():
    chain = transforms([ROT(360 / 4000, 4000)])
    start = time.perf_counter()
    assert _same_copies(iter(reversed(chain)), chain)
    assert not _same_copies(chain[:-1] + [chain[0]], chain)  # one copy twice, one missing
    assert not _same_copies(chain[:-1], chain)
    assert time.perf_counter() - start < 5


def test_copies_within_the_tolerance_across_a_grid_border_match():
    t = list(ID)
    t[3] = (1 - GRID_SHIFT) * GRID - 1e-8  # x offset just below a cell border, its match just above it
    u = list(t)
    u[3] += 2e-8
    assert _same_copies([u], [t]) and not _same_copies([[*u[:3], u[3] + 1e-5, *u[4:]]], [t])
