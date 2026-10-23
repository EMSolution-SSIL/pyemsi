import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_python_json(snippet: str) -> dict:
    result = subprocess.run(
        [sys.executable, "-c", snippet],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_import_pyemsi_keeps_heavy_modules_lazy():
    heavy_modules = [
        "pyemsi.io._emsolution_output",
        "pyemsi.plotter.plotter",
        "pyemsi.plotter.qt_window",
        "pyemsi.tools.FemapConverter",
    ]
    snippet = f"""
import json
import sys

import pyemsi

heavy = {heavy_modules!r}
before = {{name: name in sys.modules for name in heavy}}
from pyemsi import EMSolutionOutput, Plotter
after_partial = {{name: name in sys.modules for name in heavy}}

femap_error = None
try:
    getattr(pyemsi, "FemapConverter")
except Exception as exc:
    femap_error = type(exc).__name__
after_femap = "pyemsi.tools.FemapConverter" in sys.modules

print(json.dumps({{
    "before": before,
    "after_partial": after_partial,
    "femap_error": femap_error,
    "after_femap": after_femap,
}}))
"""

    payload = _run_python_json(snippet)

    assert payload["before"] == {name: False for name in heavy_modules}
    assert payload["after_partial"] == {
        "pyemsi.io._emsolution_output": True,
        "pyemsi.plotter.plotter": True,
        "pyemsi.plotter.qt_window": True,
        "pyemsi.tools.FemapConverter": False,
    }
    assert payload["femap_error"] in {None, "ModuleNotFoundError"}


def test_import_pyemsi_gui_keeps_optional_stacks_lazy():
    watched_modules = [
        "qtconsole",
        "IPython",
        "ipykernel",
        "pyemsi.plotter",
        "pyemsi.io",
    ]
    snippet = f"""
import json
import sys

import pyemsi.gui

watched = {watched_modules!r}
status = {{name: name in sys.modules for name in watched}}
print(json.dumps(status))
"""

    payload = _run_python_json(snippet)

    assert payload == {name: False for name in watched_modules}


def test_subpackage_lazy_exports_stay_importable():
    from pyemsi import EMSolutionOutput, Plotter
    from pyemsi.io import EMSolutionOutput as IOOutput
    from pyemsi.plotter import Plotter as PlotterFromSubpackage

    assert EMSolutionOutput.__name__ == "EMSolutionOutput"
    assert Plotter.__name__ == "Plotter"
    assert IOOutput is EMSolutionOutput
    assert PlotterFromSubpackage is Plotter


def test_lazy_export_stub_files_expose_expected_names():
    cases = [
        ("pyemsi", REPO_ROOT / "pyemsi" / "__init__.pyi", {"EMSolutionOutput", "Plotter", "FemapConverter"}),
        ("pyemsi.io", REPO_ROOT / "pyemsi" / "io" / "__init__.pyi", {"EMSolutionOutput", "PlotAxisOption"}),
        ("pyemsi.plotter", REPO_ROOT / "pyemsi" / "plotter" / "__init__.pyi", {"Plotter"}),
    ]

    for module_name, stub_path, expected_names in cases:
        module = __import__(module_name, fromlist=["__all__"])
        stub_text = stub_path.read_text(encoding="utf-8")

        for name in expected_names:
            assert name in module.__all__
            assert name in stub_text


def test_basedpyright_resolves_lazy_exports(tmp_path):
    executable = shutil.which("basedpyright")
    if executable is None:
        pytest.skip("basedpyright executable is not available")

    source = tmp_path / "check_lazy_exports.py"
    source.write_text(
        "\n".join(
            [
                "from pyemsi import EMSolutionOutput, FemapConverter, Plotter",
                "from pyemsi.io import EMSolutionOutput as IOOutput",
                "from pyemsi.plotter import Plotter as PlotterFromSubpackage",
                "_ = EMSolutionOutput",
                "_ = FemapConverter",
                "_ = Plotter",
                "_ = IOOutput",
                "_ = PlotterFromSubpackage",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [executable, str(source)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
