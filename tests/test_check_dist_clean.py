"""The leak checker refuses pyemsi outputs (wheel, sdist, directory) that carry FreeCAD, the add-on or ems_material."""

from __future__ import annotations

import importlib.util
import io
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

CHECKER = Path(__file__).resolve().parents[1] / "tools" / "check_dist_clean.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_dist_clean", CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


checker = _load_checker()

CLEAN_FILES = {
    "pyemsi/__init__.py": "import numpy\n__version__ = '1.0'\n",
    "pyemsi/gui/main.py": "from pyemsi import core\n# FreeCAD is only mentioned in a comment\n",
    "pyemsi-1.0.dist-info/METADATA": "Name: pyemsi\nRequires-Dist: numpy>=1.21\nRequires-Dist: pyvista\n",
}


def _wheel(path: Path, files: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, text in files.items():
            archive.writestr(name, text)
    return path


def _sdist(path: Path, files: dict[str, str]) -> Path:
    with tarfile.open(path, "w:gz") as archive:
        for name, text in files.items():
            data = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return path


def _tree(root: Path, files: dict[str, str]) -> Path:
    for name, text in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    return root


def _run(capsys, *paths: Path) -> tuple[int, list[str]]:
    code = checker.main([str(p) for p in paths])
    return code, capsys.readouterr().out.splitlines()


def test_clean_wheel_passes(tmp_path, capsys):
    code, lines = _run(capsys, _wheel(tmp_path / "pyemsi-1.0-py3-none-any.whl", CLEAN_FILES))

    assert (code, lines) == (0, [])


def test_wheel_with_addon_package_is_refused(tmp_path, capsys):
    wheel = _wheel(tmp_path / "pyemsi-1.0-py3-none-any.whl", {**CLEAN_FILES, "freecad_addon/x.py": "x = 1\n"})

    code, lines = _run(capsys, wheel)

    assert code == 1
    assert lines == [f"{wheel}: freecad_addon/x.py: freecad_addon"]


def test_sdist_with_freecad_import_is_refused(tmp_path, capsys):
    sdist = _sdist(tmp_path / "pyemsi-1.0.tar.gz", {**CLEAN_FILES, "pyemsi-1.0/pyemsi/viewer.py": "import FreeCAD\n"})

    code, lines = _run(capsys, sdist)

    assert code == 1
    assert lines == [f"{sdist}: pyemsi-1.0/pyemsi/viewer.py: FreeCAD"]


@pytest.mark.parametrize(
    "source, name",
    [
        ("import FreeCADGui\n", "FreeCADGui"),
        ("def f():\n    import FreeCAD as App\n", "FreeCAD"),
        ("from FreeCAD import Vector\n", "FreeCAD"),
        ("import os, ems_material\n", "ems_material"),
        ("from ems_material.widget import W\n", "ems_material"),
    ],
)
def test_import_forms_are_detected(tmp_path, capsys, source, name):
    wheel = _wheel(tmp_path / "a.whl", {"pkg/m.py": source})

    code, lines = _run(capsys, wheel)

    assert (code, lines) == (1, [f"{wheel}: pkg/m.py: {name}"])


def test_directory_with_ems_material_package_is_refused(tmp_path, capsys):
    root = _tree(tmp_path / "pyemsi", {"Lib/site-packages/ems_material/__init__.py": "", "python.exe": "MZ"})

    code, lines = _run(capsys, root)

    assert code == 1
    assert lines == [f"{root}: Lib/site-packages/ems_material/__init__.py: ems_material"]


def test_directory_with_freecad_import_in_site_packages_is_refused(tmp_path, capsys):
    root = _tree(tmp_path / "pyemsi", {"Lib/site-packages/dep/plugin.py": "import numpy\nimport FreeCAD\n"})

    code, lines = _run(capsys, root)

    assert (code, lines) == (1, [f"{root}: Lib/site-packages/dep/plugin.py: FreeCAD"])


def test_clean_directory_passes_and_binary_files_are_not_read(tmp_path, capsys):
    root = _tree(tmp_path / "pyemsi", {"Lib/site-packages/dep/__init__.py": "import numpy\n"})
    (root / "data.bin").write_bytes(b"import FreeCAD\n")

    assert _run(capsys, root) == (0, [])


@pytest.mark.parametrize("requirement", ["ems-material-manager>=0.1", "ems_material_manager", "FreeCAD (>=1.0)"])
def test_metadata_requiring_the_addon_dependency_is_refused(tmp_path, capsys, requirement):
    files = {**CLEAN_FILES, "pyemsi-1.0.dist-info/METADATA": f"Name: pyemsi\nRequires-Dist: {requirement}\n"}
    wheel = _wheel(tmp_path / "pyemsi-1.0-py3-none-any.whl", files)

    code, lines = _run(capsys, wheel)

    assert code == 1
    assert len(lines) == 1
    assert lines[0].startswith(f"{wheel}: pyemsi-1.0.dist-info/METADATA: ")


def test_sdist_pkg_info_requirement_is_refused(tmp_path, capsys):
    sdist = _sdist(tmp_path / "pyemsi-1.0.tar.gz", {"pyemsi-1.0/PKG-INFO": "Requires-Dist: ems-material-manager\n"})

    assert _run(capsys, sdist)[0] == 1


def test_every_path_is_checked_and_hits_are_listed(tmp_path, capsys):
    clean = _wheel(tmp_path / "clean.whl", CLEAN_FILES)
    dirty = _wheel(tmp_path / "dirty.whl", {"ems_material/__init__.py": ""})

    code, lines = _run(capsys, clean, dirty)

    assert (code, lines) == (1, [f"{dirty}: ems_material/__init__.py: ems_material"])


def test_glob_patterns_are_expanded_and_an_empty_match_is_an_error(tmp_path, capsys):
    _wheel(tmp_path / "a.whl", CLEAN_FILES)

    assert checker.main([str(tmp_path / "*.whl")]) == 0
    assert checker.main([str(tmp_path / "*.nothing")]) == 2
    assert "no such file" in capsys.readouterr().err.lower()


def test_command_line_exit_code(tmp_path):
    import subprocess

    wheel = _wheel(tmp_path / "bad.whl", {"freecad_addon/x.py": ""})

    result = subprocess.run([sys.executable, str(CHECKER), str(wheel)], capture_output=True, text=True)

    assert result.returncode == 1
    assert "freecad_addon/x.py: freecad_addon" in result.stdout
