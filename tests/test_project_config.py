import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def _config():
    with PYPROJECT.open("rb") as f:
        return tomllib.load(f)


def test_pyemsi_dependencies_have_no_addon_or_freecad():
    dependencies = _config()["project"]["dependencies"]
    assert not [d for d in dependencies if d.startswith(("ems-material-manager", "freecad"))]


def test_freecad_is_only_in_the_addon_environment():
    pixi = _config()["tool"]["pixi"]
    assert "freecad" not in pixi["dependencies"]
    feature = pixi["feature"]["freecad"]
    assert feature["dependencies"]["freecad"] == "==1.1.0"
    assert "ems-material-manager" in feature["pypi-dependencies"]
    assert "freecad" in pixi["environments"]["addon"]


def test_addon_tasks_live_in_the_addon_feature():
    pixi = _config()["tool"]["pixi"]
    for name in ("freecad", "install-addon", "test-addon"):
        assert name in pixi["feature"]["freecad"]["tasks"]
        assert name not in pixi["tasks"]


def test_freecad_pythonpath_is_only_set_in_the_addon_environment():
    # PYTHONPATH points at Library\bin, where only FreeCAD.pyd and FreeCADGui.pyd live.
    pixi = _config()["tool"]["pixi"]
    assert "PYTHONPATH" not in pixi["activation"]["env"]
    assert pixi["feature"]["freecad"]["activation"]["env"]["PYTHONPATH"] == r"%CONDA_PREFIX%\Library\bin"


def test_pyyaml_is_declared():
    # tests/test_installer_config.py imports yaml.
    assert "pyyaml" in _config()["tool"]["pixi"]["dependencies"]


@pytest.mark.skipif(importlib.util.find_spec("FreeCAD") is not None, reason="FreeCAD present: the add-on suite runs")
def test_addon_suite_is_not_collected_without_freecad():
    # A bare `pytest tests` in the default environment must not fail on the add-on tests' FreeCAD imports.
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/freecad_addon", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 5, result.stdout + result.stderr  # 5: no tests collected
