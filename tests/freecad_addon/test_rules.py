"""The rule engine: ordered mirror, rotation and translation rules become rigid transforms and part names."""

import itertools
import math
import random
import time

import pytest

import FreeCAD as App
import Draft

from emsolution import symmetry
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
    inverse,
    part_names,
    relative_transforms,
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


def test_a_full_turn_the_other_way_does_not_warn():
    assert rule_warnings([ROT(-10, 36)]) == []
    assert "350" in " ".join(rule_warnings([ROT(-10, 35)]))


def test_relative_transforms_of_closed_rules_are_the_copies():
    rules = [MIRROR_X0, ROT(90, 4)]
    assert relative_transforms(rules) == transforms(rules)
    assert relative_transforms([]) == [ID]


def test_relative_transforms_of_open_rules_hold_every_pair():
    """Mirror in a line off the rotation centre, then a quarter turn twice: copies 1 and 3 are related by neither
    copy's transform, but by T1^-1 T3."""
    rules = [{"kind": "mirror", "point": [1, 0.75, 0], "normal": [2, 1.5, 0]}, ROT(90, 2)]
    ts = transforms(rules)
    found = relative_transforms(rules)
    assert found[0] == pytest.approx(ID)
    assert compose(inverse(ts[3]), ts[3]) == pytest.approx(ID)
    for i in range(len(ts)):
        for j in range(i + 1, len(ts)):
            r = compose(inverse(ts[i]), ts[j])
            assert any(max(abs(a - b) for a, b in zip(r, t)) < 1e-9 for t in found), (i, j)
    assert len(found) > len(ts)


OFF_AXIS = {"kind": "mirror", "point": [1, 0.75, 0], "normal": [2, 1.5, 0]}  # its plane misses the rotation axis
MIRROR_Y0 = {"kind": "mirror", "point": [0, 0, 0], "normal": [0, 1, 0]}


def UP(n, step=10):
    return {"kind": "translate", "vector": [0, 0, step], "count": n}


def _sector_box(step, height=10):
    """The box of a sector from the axis to R 50, of half a rotation step (it is mirrored first), z 0..height."""
    return (0, 0, 0, 50, 50 * math.sin(math.radians(step / 2)), height)


def _close(a, b):
    return max(abs(x - y) for x, y in zip(a, b)) < 1e-7


def _moves_into(r, box):
    """True if r moves one of a 5 x 5 x 5 grid of points of the box into the box."""
    grid = [[box[k] + f * (box[k + 3] - box[k]) for f in (0, 0.25, 0.5, 0.75, 1)] for k in range(3)]
    for p in itertools.product(*grid):
        q = apply(r, p)
        if all(box[k] - 1e-7 <= q[k] <= box[k + 3] + 1e-7 for k in range(3)):
            return True
    return False


def _check(rules, box):
    """relative_transforms(rules, box) against every pair i < j: each listed m is a T_i^-1 T_j and first_pair gives the
    first pair that does, and every T_i^-1 T_j that moves a point of the box into it is listed. Returns the list."""
    ts = transforms(rules)
    pairs = [(i, j, compose(inverse(ts[i]), ts[j])) for i in range(len(ts)) for j in range(i + 1, len(ts))]
    found = relative_transforms(rules, box)
    assert _close(found[0], ID)
    for m in found[1:]:
        assert symmetry.first_pair(ts, m) == next((i, j) for i, j, r in pairs if _close(r, m))
    for i, j, r in pairs:
        if _moves_into(r, box):
            assert any(_close(r, m) for m in found), (i, j)
    return found


CHECKED = {
    "closed": ([MIRROR_X0, ROT(90, 4)], (0, 1, 0, 2, 2, 0)),
    "closed-then-turns-and-steps": ([OFF_AXIS, ROT(45, 8), UP(3)], (30, 0, 0, 50, 15, 10)),
    "sector-to-the-axis": ([MIRROR_Y0, ROT(30, 12), UP(4)], _sector_box(30)),
    "steps-then-a-mirror": ([{"kind": "translate", "vector": [3, 1, 0], "count": 6}, OFF_AXIS], (0, 0, 0, 4, 2, 0)),
    "turns-about-x-then-steps": (
        [ROT(90, 4, axis=(1, 0, 0), point=(0, 5, 0)), {"kind": "translate", "vector": [7, 0, 0], "count": 5}],
        (0, 0, 0, 8, 3, 2),
    ),
}


@pytest.mark.parametrize("name", CHECKED)
def test_relative_transforms_hold_every_relative_that_can_overlap(name):
    rules, box = CHECKED[name]
    found = _check(rules, box)
    assert len(found) > 1


def test_relative_transforms_drop_relatives_that_cannot_overlap():
    rules, box = CHECKED["closed-then-turns-and-steps"]
    assert 1 < len(relative_transforms(rules, box)) < len(relative_transforms(rules))


def test_relative_transforms_by_sweeping_pairs_hold_the_same(monkeypatch):
    """With more steps than STRUCTURE_LIMIT, the pairs of copies are swept instead; the list still holds them all."""
    monkeypatch.setattr(symmetry, "STRUCTURE_LIMIT", 0)
    for name in ("closed-then-turns-and-steps", "sector-to-the-axis", "turns-about-x-then-steps"):
        _check(*CHECKED[name])


def test_relative_transforms_of_random_rules_hold_every_relative_that_can_overlap():
    """Random mirrors, turns and steps, any planes and axes, and turns and mirrors about Z that close."""
    rng = random.Random(7)

    def unit():
        v = [rng.gauss(0, 1) for _ in range(3)]
        return [c / math.sqrt(sum(x * x for x in v)) for c in v]

    def rule():
        kind = rng.choice(["mirror", "rotate", "translate", "zrot", "zmirror"])
        p = [rng.uniform(-20, 20) for _ in range(3)]
        if kind == "mirror":
            return {"kind": "mirror", "point": p, "normal": unit()}
        if kind == "zmirror":
            a = rng.uniform(0, math.pi)
            return {"kind": "mirror", "point": [0, 0, 0], "normal": [math.cos(a), math.sin(a), 0]}
        if kind == "zrot":
            n = rng.randint(2, 6)
            return ROT(360 / n, n)
        if kind == "rotate":
            return {"kind": "rotate", "point": p, "axis": unit(), "step": rng.choice([30, 45, 90, 37]), "count": 3}
        return {"kind": "translate", "vector": [rng.uniform(-15, 15) for _ in range(3)], "count": rng.randint(2, 3)}

    done = 0
    while done < 40:
        rules = [rule() for _ in range(rng.randint(1, 3))]
        if copy_count(rules) > 40 or rule_problems(rules, ""):
            continue
        low = [rng.uniform(-30, 30) for _ in range(3)]
        box = (*low, *(a + rng.choice([0.0, rng.uniform(0.1, 40)]) for a in low))
        _check(rules, box)
        ts, everything = transforms(rules), relative_transforms(rules)  # without a box: every relative
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                assert any(_close(compose(inverse(ts[i]), ts[j]), m) for m in everything), (rules, i, j)
        done += 1


def test_relative_transforms_of_closed_rules_are_the_copies_whose_boxes_meet_the_cell():
    rules = [MIRROR_X0, ROT(90, 4)]
    ts = transforms(rules)
    near = relative_transforms(rules, (0, 1, 0, 2, 2, 0))  # a rectangle on the mirror plane, clear of the axis
    assert len(near) == 3 and all(m in ts for m in near)  # itself, its mirror image and one turned mirror image
    assert near[0] == ID and symmetry.first_pair(ts, near[1])[0] == 0


@pytest.mark.parametrize(
    "rules,box",
    [
        ([MIRROR_X0, ROT(7.5, 48), UP(10)], (30, 0, 0, 50, 3.3, 10)),
        ([{"kind": "translate", "vector": [1, 0, 0], "count": 2000}], (0, 0, 0, 1, 1, 0)),
        ([OFF_AXIS, ROT(7.2, 50), UP(50)], (30, 0, 0, 50, 3.1, 10)),
        ([{"kind": "translate", "vector": [1, 0, 0], "count": 5000}], (0, 0, 0, 1, 1, 0)),
        ([MIRROR_Y0, ROT(3.75, 96), UP(10)], _sector_box(3.75)),
        ([MIRROR_Y0, ROT(1.44, 250), UP(10)], _sector_box(1.44)),
        ([MIRROR_Y0, ROT(2.88, 125), UP(20)], _sector_box(2.88)),
        ([{"kind": "translate", "vector": [0.01, -0.01, 0], "count": 5000}], (0, 0, 0, 100, 100, 0)),
        ([ROT(1, 360), UP(10, 1)], (0, -0.1, 0, 100, 0.1, 1)),
    ],
    ids=["960", "2000", "5000-turned", "5000", "sector-1920", "sector-5000", "sector-5000-20", "bars-5000", "spokes"],
)
def test_relative_transforms_of_many_open_copies_are_quick(rules, box):
    """Validate runs this on the GUI thread, and Mesh again. Forming every pair took 14 s at 960 copies and minutes at
    MAX_DRAWN; sweeping the pairs whose boxes meet still took 9 s for 5000 sectors that reach the axis (all of a layer
    meet there) and 21 s for 5000 long bars side by side. The bound is generous; each takes well under a second."""
    start = time.perf_counter()
    found = relative_transforms(rules, box)
    assert time.perf_counter() - start < 3
    assert found[0] == ID and len(found) > 1


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
