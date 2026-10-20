"""Every example model builds, validates and meshes (or is refused as it should be).
Run from the repo root: pixi run pytest tests/freecad_addon/test_examples.py"""

import json
import os
import re

import pytest

from .cases import CASES, run_case

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
    expected = {item["name"] for item in job.get("bodies") or job["volumes"]} | {job["air"]["name"]}
    rows = {name: int(count) for _, name, count in ROW.findall(text)}
    assert set(rows) == expected and len(expected) >= 3
    assert all(count > 0 for count in rows.values())
    assert "Warning" not in text
