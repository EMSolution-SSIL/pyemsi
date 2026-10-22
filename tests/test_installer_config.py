"""Checks that both installers take their version from pyemsi.__version__ and that CI offers the installer choice."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FREECAD_INSTALLER = ROOT / "installer" / "freecad"
# Repackaged third-party wheels pin their own upstream version.
THIRD_PARTY_RECIPES = {"ems-file-format-converter", "ems-material-manager"}


def _package_version() -> str:
    text = (ROOT / "pyemsi" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    assert match is not None
    return match.group(1)


def test_version_script_matches_package():
    result = subprocess.run([sys.executable, str(ROOT / "installer" / "version.py")], capture_output=True, check=True)
    assert result.stdout.strip().decode() == _package_version()


def test_version_script_output_has_no_carriage_return():
    # The value goes into PYEMSI_VERSION through $(...); a trailing CR from Windows text-mode print would break it.
    result = subprocess.run([sys.executable, str(ROOT / "installer" / "version.py")], capture_output=True, check=True)
    assert result.stdout in (_package_version().encode(), _package_version().encode() + b"\n")


def _installer_files() -> list[Path]:
    recipes = [
        recipe
        for recipe in (FREECAD_INSTALLER / "recipes").glob("*/recipe.yaml")
        if recipe.parent.name not in THIRD_PARTY_RECIPES
    ]
    return [FREECAD_INSTALLER / "construct.yaml", ROOT / "installer" / "pyemsi.nsi", *recipes]


def test_no_literal_versions_in_installer_files():
    literal = re.compile(
        r"""^\s*(?:version:\s*["']?\d+\.\d+|!define\s+APP_VERSION\s+["']?\d+\.\d+)""", re.MULTILINE | re.IGNORECASE
    )
    files = _installer_files()
    assert FREECAD_INSTALLER / "construct.yaml" in files and ROOT / "installer" / "pyemsi.nsi" in files
    offenders = [str(path.relative_to(ROOT)) for path in files if literal.search(path.read_text(encoding="utf-8"))]
    assert offenders == []


def test_versioned_installer_files_read_pyemsi_version():
    for name in ("pyemsi", "emsolution-freecad"):
        text = (FREECAD_INSTALLER / "recipes" / name / "recipe.yaml").read_text(encoding="utf-8")
        assert 'env.get("PYEMSI_VERSION")' in text, name
    assert 'environ["PYEMSI_VERSION"]' in (FREECAD_INSTALLER / "construct.yaml").read_text(encoding="utf-8")


def test_nsis_script_requires_app_version():
    text = (ROOT / "installer" / "pyemsi.nsi").read_text(encoding="utf-8")
    assert re.search(r"^!ifndef APP_VERSION\s*\n\s*!error", text, re.MULTILINE)


def test_addon_recipe_depends_on_ems_material_manager():
    recipe = yaml.safe_load((FREECAD_INSTALLER / "recipes" / "emsolution-freecad" / "recipe.yaml").read_text("utf-8"))
    assert "ems-material-manager" in recipe["requirements"]["run"]
    assert (FREECAD_INSTALLER / "recipes" / "ems-material-manager" / "recipe.yaml").is_file()


def test_pyemsi_recipe_does_not_depend_on_ems_material_manager():
    text = (FREECAD_INSTALLER / "recipes" / "pyemsi" / "recipe.yaml").read_text(encoding="utf-8")
    assert "ems-material-manager" not in text


def test_packaging_workflow_offers_installer_choice():
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "windows-packaging.yml").read_text("utf-8"))
    # PyYAML parses the bare key `on` as the boolean True.
    triggers = workflow.get("on", workflow.get(True))
    choice = triggers["workflow_dispatch"]["inputs"]["installers"]
    assert choice["type"] == "choice"
    assert choice["options"] == ["pyemsi", "freecad", "both"]
    assert choice["default"] == "pyemsi"
    freecad_job = next(job for name, job in workflow["jobs"].items() if "freecad" in name)
    assert "freecad" in freecad_job["if"]
    assert "both" in freecad_job["if"]
    assert "pyemsi" in workflow["jobs"]["build_windows_portable"]["if"]
