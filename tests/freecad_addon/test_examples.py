"""Every example model builds, validates and meshes (or is refused as it should be).
Run from the repo root: pixi run pytest tests/freecad_addon/test_examples.py"""

import json
import os
import re

import pytest

from .cases import CASES, Case, rect_2d, run_case

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
