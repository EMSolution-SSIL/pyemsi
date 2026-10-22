import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


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
