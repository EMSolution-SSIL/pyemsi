"""Checks that both installers take their version from pyemsi.__version__ and that CI offers the installer choice."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml
from packaging.requirements import Requirement

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


PACKAGE_XML_NS = {"p": "https://wiki.freecad.org/Package_Metadata"}


def _package_xml_version(path: Path) -> str:
    return ET.parse(path).getroot().find("p:version", PACKAGE_XML_NS).text


def test_addon_package_xml_version_matches_pyemsi():
    # Developer installs (`pixi run -e addon install-addon`) read the repo file as is.
    assert _package_xml_version(ROOT / "freecad_addon" / "package.xml") == _package_version()


def test_addon_recipe_stamps_package_xml_version(tmp_path):
    script = yaml.safe_load((FREECAD_INSTALLER / "recipes" / "emsolution-freecad" / "recipe.yaml").read_text("utf-8"))
    script = script["build"]["script"]
    stamps = [i for i, line in enumerate(script) if "package.xml" in line and "${{ version }}" in line]
    assert len(stamps) == 1
    copy = next(i for i, line in enumerate(script) if line.startswith("copy package.xml"))
    assert stamps[0] > copy
    # Run the stamp line the way rattler-build does (cmd), with the recipe's version rendered and %MOD% set.
    source = ROOT / "freecad_addon" / "package.xml"
    shutil.copy(source, tmp_path / "package.xml")
    line = script[stamps[0]].replace("${{ version }}", "9.8.7")
    subprocess.run(line, shell=True, env={**os.environ, "MOD": str(tmp_path)}, check=True)
    stamped = (tmp_path / "package.xml").read_bytes()
    assert not stamped.startswith(b"\xef\xbb\xbf")
    assert _package_xml_version(tmp_path / "package.xml") == "9.8.7"
    expected = re.sub(rb"<version>[^<]*</version>", b"<version>9.8.7</version>", source.read_bytes())
    assert stamped == expected


def _pixi_tasks() -> dict:
    with (FREECAD_INSTALLER / "pixi.toml").open("rb") as f:
        return tomllib.load(f)["tasks"]


def test_packages_task_removes_our_built_packages(tmp_path):
    # The build string doesn't depend on the source, so --skip-existing=local would reuse a stale pyemsi or add-on
    # package of the same version. Third-party recipes keep being skipped.
    task = _pixi_tasks()["packages"]
    assert "--skip-existing=local" in task
    cleanup = re.search(r'powershell -NoProfile -Command "([^"]*)"', task)
    assert cleanup is not None
    assert task.index(cleanup.group(0)) < task.index("rattler-build build")
    output = tmp_path / "output"
    removed = [
        output / "bld" / "rattler-build_pyemsi" / "work" / "x.txt",
        output / "win-64" / "pyemsi-0.6.0-h0123abc_0.conda",
        output / "noarch" / "emsolution-freecad-0.6.0-h0123abc_0.conda",
    ]
    kept = [
        output / "noarch" / "ems-material-manager-0.1.0-h0123abc_0.conda",
        output / "noarch" / "ems-file-format-converter-0.5.1-h0123abc_0.conda",
        output / "noarch" / "repodata.json",
    ]
    for path in removed + kept:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
    subprocess.run(["powershell", "-NoProfile", "-Command", cleanup.group(1)], cwd=tmp_path, check=True)
    assert [p for p in removed if p.exists()] == []
    assert [p for p in kept if not p.exists()] == []
    assert not (output / "bld").exists()


def _lock_package(name: str) -> dict:
    lock = yaml.load((ROOT / "pixi.lock").read_text("utf-8"), Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    return next(package for package in lock["packages"] if package.get("name") == name)


def test_ems_material_manager_recipe_matches_pixi_lock():
    recipe = yaml.safe_load((FREECAD_INSTALLER / "recipes" / "ems-material-manager" / "recipe.yaml").read_text("utf-8"))
    locked = _lock_package("ems-material-manager")
    assert recipe["context"]["version"] == locked["version"]
    assert recipe["source"]["sha256"] == locked["sha256"]
    assert locked["pypi"].endswith(recipe["context"]["wheel"].replace("${{ version }}", locked["version"]))


# PyPI name -> conda-forge name where they differ.
CONDA_NAMES = {"matplotlib": "matplotlib-base", "gmsh": "python-gmsh"}


def test_pyemsi_recipe_runs_every_pyemsi_dependency():
    with (ROOT / "pyproject.toml").open("rb") as f:
        dependencies = [Requirement(d) for d in tomllib.load(f)["project"]["dependencies"]]
    recipe = yaml.safe_load((FREECAD_INSTALLER / "recipes" / "pyemsi" / "recipe.yaml").read_text("utf-8"))
    run = {spec.split()[0].lower() for spec in recipe["requirements"]["run"]}
    missing = [d.name for d in dependencies if CONDA_NAMES.get(d.name.lower(), d.name.lower()) not in run]
    assert missing == []


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


def _freecad_job_steps() -> list[dict]:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "windows-packaging.yml").read_text("utf-8"))
    return workflow["jobs"]["build_windows_freecad_installer"]["steps"]


def test_freecad_ci_job_builds_from_a_short_path():
    # rattler-build's work dirs hit Windows' 260-char MAX_PATH from the runner's checkout path (see
    # installer/freecad/pixi.toml): the job builds from a git worktree at <drive>:\pe, like the local build. Not subst
    # or a junction: pixi resolves those to the real, long path.
    steps = _freecad_job_steps()
    worktree = next(i for i, step in enumerate(steps) if "git worktree add" in step.get("run", ""))
    assert '"\\pe"' in steps[worktree]["run"]
    assert "SHORT_ROOT=" in steps[worktree]["run"] and "GITHUB_ENV" in steps[worktree]["run"]
    assert "subst" not in "".join(step.get("run", "") for step in steps)
    pixi = next(i for i, step in enumerate(steps) if step.get("uses", "").startswith("prefix-dev/setup-pixi@"))
    assert worktree < pixi
    assert steps[pixi]["with"]["manifest-path"] == "${{ env.SHORT_ROOT }}\\installer\\freecad\\pixi.toml"
    build = next(i for i, step in enumerate(steps) if "pixi run" in step.get("run", ""))
    assert pixi < build
    assert steps[build]["working-directory"] == "${{ env.SHORT_ROOT }}"
    assert steps[build]["run"] == "pixi run --manifest-path installer\\freecad\\pixi.toml installer"
    upload = next(step for step in steps if step.get("uses", "").startswith("actions/upload-artifact@"))
    assert upload["with"]["path"].startswith("${{ env.SHORT_ROOT }}/installer/freecad/dist/")


def test_ci_pins_the_pixi_version_that_wrote_the_locks():
    # pixi.lock and installer/freecad/pixi.lock were written by pixi 0.81.0; `locked: true` needs a pixi that reads them.
    versions = []
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        for job in yaml.safe_load(workflow.read_text("utf-8"))["jobs"].values():
            for step in job["steps"]:
                if step.get("uses", "").startswith("prefix-dev/setup-pixi@"):
                    versions.append(step["with"]["pixi-version"])
    assert len(versions) >= 2
    assert set(versions) == {"v0.81.0"}


def test_freecad_ci_job_leaves_the_version_to_the_tasks():
    # The installer tasks set PYEMSI_VERSION from installer/version.py themselves.
    for step in _freecad_job_steps():
        assert "PYEMSI_VERSION" not in step.get("env", {}), step.get("name")
