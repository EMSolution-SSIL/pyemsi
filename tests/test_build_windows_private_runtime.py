"""Tests for the Windows private-runtime builder helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_builder_module():
    module_path = Path(__file__).resolve().parents[1] / "tools" / "build_windows_private_runtime.py"
    spec = importlib.util.spec_from_file_location("build_windows_private_runtime", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


builder = _load_builder_module()


def test_unique_strings_deduplicates_and_preserves_order():
    result = builder._unique_strings(["numpy>=1.21.0", "PySide6>=6.5.0", "PySide6>=6.5.0", "pywinpty"])

    assert result == ("numpy>=1.21.0", "PySide6>=6.5.0", "pywinpty")


def test_unique_strings_skips_non_strings_and_blanks():
    result = builder._unique_strings(["numpy", 42, "", None, "  pyvista  "])

    assert result == ("numpy", "pyvista")


def test_load_build_config_uses_runtime_tool_app_module(tmp_path):
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(
        """
[project]
name = "pyemsi"
dependencies = ["numpy>=1.21.0"]

[tool.pyemsi.windows-private-runtime]
app_module = "pyemsi.gui"
extra_dependencies = ["pywinpty"]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    config = builder.load_build_config(tmp_path, pyproject_path=pyproject_path)

    assert config.app_module == "pyemsi.gui"
    assert config.dependencies == ("numpy>=1.21.0", "pywinpty")


def test_render_pth_text_enables_site_and_app_path_once():
    original = "python311.zip\n.\n# import site\n"

    rendered = builder.render_pth_text(original)

    assert rendered.count("import site") == 1
    assert rendered.count("..\\app") == 1
    assert rendered.endswith("\n")


def test_render_launcher_bat_targets_private_runtime_module():
    launcher = builder.render_launcher_bat(app_module="pyemsi.gui")

    assert "set PYTHONHOME=%BASE_DIR%runtime" in launcher
    assert "set PYTHONPATH=%BASE_DIR%app" in launcher
    assert "set PATH=%BASE_DIR%runtime;%BASE_DIR%runtime\\Scripts;%PATH%" in launcher
    assert '"%BASE_DIR%runtime\\python.exe" -m pyemsi.gui %*' in launcher


def test_render_launcher_bat_script_mode():
    launcher = builder.render_launcher_bat(script_mode=True)

    assert "set SCRIPT=%~1" in launcher
    assert '"%BASE_DIR%runtime\\python.exe" "%SCRIPT%" %*' in launcher
    assert "-m" not in launcher


def test_build_layout_uses_scoped_output_directories(tmp_path):
    layout = builder.build_layout(tmp_path)

    assert layout.build_dir == tmp_path / "build" / "windows-private-runtime"
    assert layout.cache_dir == layout.build_dir / "cache"
    assert layout.dist_dir == tmp_path / "dist" / "pyemsi"
    assert layout.runtime_dir == layout.dist_dir / "runtime"
    assert layout.app_dir == layout.dist_dir / "app"
    assert layout.launcher_exe == layout.dist_dir / "pyemsi.exe"
    assert layout.script_launcher_exe == layout.dist_dir / "run_script.exe"
