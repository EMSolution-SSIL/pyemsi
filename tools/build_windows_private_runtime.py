from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tomllib
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

DEFAULT_PYTHON_VERSION = "3.11.9"
DEFAULT_DIST_NAME = "pyemsi-windows-portable"
DEFAULT_APP_MODULE = "pyemsi.gui"
WINDOWS_RUNTIME_TOOL_PATH = ("tool", "pyemsi", "windows-private-runtime")
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"


@dataclass(frozen=True)
class BuildLayout:
    repo_root: Path
    build_dir: Path
    cache_dir: Path
    dist_dir: Path
    runtime_dir: Path
    app_dir: Path
    launcher_bat: Path
    script_launcher_bat: Path


@dataclass(frozen=True)
class BuildConfig:
    app_name: str
    python_version: str
    python_tag: str
    app_module: str
    dependencies: tuple[str, ...]
    layout: BuildLayout

    @property
    def embed_zip_name(self) -> str:
        return f"python-{self.python_version}-embed-amd64.zip"

    @property
    def embed_url(self) -> str:
        return f"https://www.python.org/ftp/python/{self.python_version}/{self.embed_zip_name}"

    @property
    def pth_file(self) -> Path:
        return self.layout.runtime_dir / f"python{self.python_tag}._pth"


def build_layout(repo_root: Path, *, dist_name: str = DEFAULT_DIST_NAME) -> BuildLayout:
    build_dir = repo_root / "build" / "windows-private-runtime"
    cache_dir = build_dir / "cache"
    dist_dir = repo_root / "dist" / dist_name
    runtime_dir = dist_dir / "runtime"
    app_dir = dist_dir / "app"
    return BuildLayout(
        repo_root=repo_root,
        build_dir=build_dir,
        cache_dir=cache_dir,
        dist_dir=dist_dir,
        runtime_dir=runtime_dir,
        app_dir=app_dir,
        launcher_bat=dist_dir / "run_pyemsi.bat",
        script_launcher_bat=dist_dir / "run_script.bat",
    )


def load_pyproject(pyproject_path: Path) -> dict[str, Any]:
    with pyproject_path.open("rb") as handle:
        return tomllib.load(handle)


def _get_nested_mapping(data: Mapping[str, Any], path: tuple[str, ...]) -> Mapping[str, Any]:
    current: Mapping[str, Any] | Any = data
    for key in path:
        if not isinstance(current, Mapping):
            return {}
        current = current.get(key, {})
    return current if isinstance(current, Mapping) else {}


def read_app_name(pyproject_data: Mapping[str, Any]) -> str:
    project_name = pyproject_data.get("project", {}).get("name")
    if isinstance(project_name, str) and project_name.strip():
        return project_name.strip()

    return "pyemsi"


def read_app_module(pyproject_data: Mapping[str, Any], *, default: str = DEFAULT_APP_MODULE) -> str:
    runtime_config = _get_nested_mapping(pyproject_data, WINDOWS_RUNTIME_TOOL_PATH)
    app_module = runtime_config.get("app_module")
    if isinstance(app_module, str) and app_module.strip():
        return app_module.strip()
    return default


def read_runtime_dependencies(pyproject_data: Mapping[str, Any]) -> tuple[str, ...]:
    runtime_config = _get_nested_mapping(pyproject_data, WINDOWS_RUNTIME_TOOL_PATH)
    extra_dependencies = runtime_config.get("extra_dependencies", [])
    project_dependencies = pyproject_data.get("project", {}).get("dependencies", [])

    ordered: list[str] = []
    seen: set[str] = set()
    for item in [*project_dependencies, *extra_dependencies]:
        if not isinstance(item, str):
            continue
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return tuple(ordered)


def load_build_config(
    repo_root: Path,
    *,
    pyproject_path: Path | None = None,
    python_version: str = DEFAULT_PYTHON_VERSION,
    dist_name: str = DEFAULT_DIST_NAME,
    app_module: str | None = None,
) -> BuildConfig:
    project_path = pyproject_path or repo_root / "pyproject.toml"
    pyproject_data = load_pyproject(project_path)
    python_tag = "".join(python_version.split(".")[:2])
    resolved_app_module = app_module or read_app_module(pyproject_data)
    return BuildConfig(
        app_name=read_app_name(pyproject_data),
        python_version=python_version,
        python_tag=python_tag,
        app_module=resolved_app_module,
        dependencies=read_runtime_dependencies(pyproject_data),
        layout=build_layout(repo_root, dist_name=dist_name),
    )


def render_pth_text(original_text: str, *, app_relative_path: str = r"..\app") -> str:
    lines = original_text.splitlines()
    output: list[str] = []
    has_import_site = False
    has_app_path = False

    for line in lines:
        stripped = line.strip()
        if stripped in {"#import site", "# import site", "import site"}:
            output.append("import site")
            has_import_site = True
            continue
        if stripped == app_relative_path:
            has_app_path = True
        output.append(line)

    if not has_import_site:
        output.append("import site")
    if not has_app_path:
        output.append(app_relative_path)

    return "\n".join(output) + "\n"


def render_launcher_bat(*, app_module: str, runtime_dir_name: str = "runtime", app_dir_name: str = "app") -> str:
    lines = [
        "@echo off",
        "setlocal",
        "set BASE_DIR=%~dp0",
        f"set PYTHONHOME=%BASE_DIR%{runtime_dir_name}",
        f"set PYTHONPATH=%BASE_DIR%{app_dir_name}",
        f"set PATH=%BASE_DIR%{runtime_dir_name};%BASE_DIR%{runtime_dir_name}\\Scripts;%PATH%",
        f'"%BASE_DIR%{runtime_dir_name}\\python.exe" -m {app_module} %*',
        "",
    ]
    return "\r\n".join(lines)


def render_script_launcher_bat(*, runtime_dir_name: str = "runtime", app_dir_name: str = "app") -> str:
    lines = [
        "@echo off",
        "setlocal",
        "set BASE_DIR=%~dp0",
        'if "%~1"=="" (',
        "  echo Usage: run_script.bat path\\to\\script.py [args...]",
        "  exit /b 1",
        ")",
        "set SCRIPT=%~1",
        "shift",
        f"set PYTHONHOME=%BASE_DIR%{runtime_dir_name}",
        f"set PYTHONPATH=%BASE_DIR%{app_dir_name}",
        f"set PATH=%BASE_DIR%{runtime_dir_name};%BASE_DIR%{runtime_dir_name}\\Scripts;%PATH%",
        f'"%BASE_DIR%{runtime_dir_name}\\python.exe" "%SCRIPT%" %*',
        "",
    ]
    return "\r\n".join(lines)


def ensure_runtime_source_artifacts(repo_root: Path) -> None:
    extension_matches = list((repo_root / "pyemsi" / "core").glob("femap_parser*.pyd"))
    if not extension_matches:
        raise FileNotFoundError(
            "Missing compiled femap_parser extension under pyemsi/core. "
            "Run `python setup.py build_ext --inplace` before packaging."
        )

    resources_module = repo_root / "pyemsi" / "resources" / "resources.py"
    if not resources_module.is_file():
        raise FileNotFoundError(
            "Missing compiled Qt resource module pyemsi/resources/resources.py. Regenerate it before packaging."
        )

    launcher_module = repo_root / "pyemsi" / "gui" / "__main__.py"
    if not launcher_module.is_file():
        raise FileNotFoundError("Missing pyemsi/gui/__main__.py launcher module.")


def reset_output_directories(layout: BuildLayout) -> None:
    layout.dist_dir.mkdir(parents=True, exist_ok=True)
    for path in (layout.runtime_dir, layout.app_dir):
        if path.exists():
            shutil.rmtree(path)
    for path in (layout.launcher_bat, layout.script_launcher_bat):
        if path.exists():
            path.unlink()
    layout.cache_dir.mkdir(parents=True, exist_ok=True)
    layout.runtime_dir.mkdir(parents=True, exist_ok=True)
    layout.app_dir.mkdir(parents=True, exist_ok=True)


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, destination)


def extract_embed_runtime(zip_path: Path, destination: Path) -> None:
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(destination)


def patch_pth_file(pth_path: Path) -> None:
    original_text = pth_path.read_text(encoding="ascii")
    pth_path.write_text(render_pth_text(original_text), encoding="ascii")


def copy_application_source(repo_root: Path, app_dir: Path) -> None:
    for package_name in ("pyemsi",):
        source = repo_root / package_name
        destination = app_dir / package_name
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))


def run_checked(command: Iterable[str], *, cwd: Path | None = None) -> None:
    subprocess.run(list(command), cwd=cwd, check=True)


def install_runtime_dependencies(config: BuildConfig) -> None:
    get_pip_path = config.layout.cache_dir / "get-pip.py"
    if not get_pip_path.exists():
        download_file(GET_PIP_URL, get_pip_path)

    python_exe = config.layout.runtime_dir / "python.exe"
    run_checked([str(python_exe), str(get_pip_path), "--no-warn-script-location"])
    run_checked([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    if config.dependencies:
        run_checked([str(python_exe), "-m", "pip", "install", *config.dependencies])


def write_launchers(config: BuildConfig) -> None:
    config.layout.launcher_bat.write_text(render_launcher_bat(app_module=config.app_module), encoding="ascii")
    config.layout.script_launcher_bat.write_text(render_script_launcher_bat(), encoding="ascii")


def smoke_test(config: BuildConfig) -> None:
    python_exe = config.layout.runtime_dir / "python.exe"
    run_checked(
        [
            str(python_exe),
            "-c",
            (
                "import os, shutil, sys, pyemsi, PySide6, scienceplots;"
                "scripts_dir=os.path.join(os.path.dirname(sys.executable), 'Scripts');"
                "os.environ['PATH']=os.pathsep.join([os.path.dirname(sys.executable), scripts_dir, os.environ.get('PATH', '')]);"
                "assert shutil.which('basedpyright-langserver');"
                "assert shutil.which('pylsp');"
                "print(sys.executable);"
                "print(pyemsi.__version__);"
                "print(scienceplots.__file__)"
            ),
        ],
        cwd=config.layout.dist_dir,
    )


def build_private_runtime(
    config: BuildConfig,
    *,
    install_dependencies_flag: bool = True,
    run_smoke_test: bool = True,
) -> BuildConfig:
    ensure_runtime_source_artifacts(config.layout.repo_root)
    reset_output_directories(config.layout)

    embed_zip_path = config.layout.cache_dir / config.embed_zip_name
    if not embed_zip_path.exists():
        download_file(config.embed_url, embed_zip_path)

    extract_embed_runtime(embed_zip_path, config.layout.runtime_dir)
    if not config.pth_file.is_file():
        raise FileNotFoundError(f"Embedded runtime ._pth file not found: {config.pth_file}")
    patch_pth_file(config.pth_file)
    copy_application_source(config.layout.repo_root, config.layout.app_dir)

    if install_dependencies_flag:
        install_runtime_dependencies(config)

    write_launchers(config)

    if run_smoke_test:
        smoke_test(config)

    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Windows portable pyemsi runtime.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--python-version", default=DEFAULT_PYTHON_VERSION)
    parser.add_argument("--dist-name", default=DEFAULT_DIST_NAME)
    parser.add_argument("--app-module")
    parser.add_argument("--skip-dependency-install", action="store_true")
    parser.add_argument("--skip-smoke-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    if sys.platform != "win32":
        print("This build script currently supports Windows only.", file=sys.stderr)
        return 1

    args = parse_args()
    repo_root = args.repo_root.resolve()
    config = load_build_config(
        repo_root,
        python_version=args.python_version,
        dist_name=args.dist_name,
        app_module=args.app_module,
    )
    build_private_runtime(
        config,
        install_dependencies_flag=not args.skip_dependency_install,
        run_smoke_test=not args.skip_smoke_test,
    )
    print(f"Build completed: {config.layout.dist_dir}")
    print(f"Launcher: {config.layout.launcher_bat}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
