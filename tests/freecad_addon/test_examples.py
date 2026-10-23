"""Every example model builds, validates and meshes (or is refused as it should be).
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_examples.py"""

import json
import os
import re
from types import SimpleNamespace

import FreeCAD as App
import pytest

from emsolution import objects

from .cases import (
    CASES,
    Case,
    bodies_overlap,
    box_3d,
    padded_box_3d,
    padded_rect_zx,
    padded_sector_ring_2d,
    rect_2d,
    run_case,
)

ROW = re.compile(r"^MAT_ID\s+(\d+)\s+(\S+)\s+(\d+)$", re.MULTILINE)


@pytest.mark.parametrize("case", CASES, ids=[c.name for c in CASES])
def test_case(case, tmp_path):
    text = run_case(case, str(tmp_path))
    assert os.path.isfile(tmp_path / case.name / "report.txt")
    if case.expect_error:
        assert case.expect_error in text
        return
    (job_path,) = [os.path.join(d, "job.json") for d, _, files in os.walk(tmp_path / case.name) if "job.json" in files]
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    air = job["air"]
    airs = [side["name"] for side in air["sides"].values()] if "sides" in air else [air["name"]]
    expected = {item["name"] for item in job.get("bodies") or job["volumes"]} | set(airs)
    rows = {name: int(count) for _, name, count in ROW.findall(text)}
    assert set(rows) == expected and len(expected) >= 3
    assert all(count > 0 for count in rows.values())
    assert "Warning" not in text
    assert text.count("slide nodes match: yes") == len(job.get("slides", []))
    assert "slide nodes match: no" not in text
    if "periodic" in job:
        assert text.count("periodic: yes") == 2 and "periodic: no" not in text  # in both files


def test_error_case_without_an_error_fails(tmp_path):
    # the checklist mentions the expected word too: only a real error may satisfy an E-case
    case = Case("X_fine", rect_2d, ["the bodies overlap"], "overlap")
    with pytest.raises(RuntimeError, match="expected an error"):
        run_case(case, str(tmp_path))


def built_air(build):
    """What the Air Region of the Study that build makes in a new document gives, as a namespace."""
    doc = App.newDocument("size_check")
    try:
        (air,) = objects.air_regions(build(doc))
        box = air.Shape.BoundBox
        limits = (box.XMin, box.XMax, box.YMin, box.YMax, box.ZMin, box.ZMax)
        values = {
            name: getattr(air, name).Value for name in ("Length", "Width", "Height", "InnerRadius", "OuterRadius")
        }
        return SimpleNamespace(mode=air.SizeMode, center=tuple(air.Center), limits=limits, **values)
    finally:
        App.closeDocument(doc.Name)


# The sizes the one-shot "fit to bodies" (50 % of the bodies' size on each side) gave these cases before Padding.
@pytest.mark.parametrize(
    "build, center, length, width, height",
    [
        (rect_2d, (30, 25, 0), 120, 100, None),  # 01
        (box_3d, (30, 25, 15), 120, 100, 60),  # 09
        (bodies_overlap, (15, 10, 0), 60, 40, None),  # E6, also made by fit_air
    ],
    ids=["01_rect_2d", "09_box_3d", "E6_bodies_overlap"],
)
def test_padded_air_keeps_the_fitted_sizes(build, center, length, width, height):
    air = built_air(build)
    assert air.mode == "Padding"
    assert air.center == pytest.approx(center)
    assert air.Length == pytest.approx(length) and air.Width == pytest.approx(width)
    if height is not None:
        assert air.Height == pytest.approx(height)


def test_padded_case_limits():
    assert built_air(padded_box_3d).limits == pytest.approx((-12, 72, 0, 60, -15, 45))
    ring = built_air(padded_sector_ring_2d)
    assert (ring.InnerRadius, ring.OuterRadius) == pytest.approx((25, 57.6))
    x0, x1, _, _, z0, z1 = built_air(padded_rect_zx).limits
    assert (x0, x1, z0, z1) == pytest.approx((0, 32.5, -10, 60))
