from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import textwrap
import tomllib
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

DEFAULT_PYTHON_VERSION = "3.11.9"
DEFAULT_DIST_NAME = "pyemsi"
DEFAULT_APP_MODULE = "pyemsi.gui"
_RUNTIME_TOOL_KEY = ("tool", "pyemsi", "windows-private-runtime")
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

_REQUIRED_ARTIFACTS = [
    ("pyemsi/core/femap_parser*.pyd", "Run `python setup.py build_ext --inplace` before packaging."),
    ("pyemsi/resources/resources.py", "Regenerate the Qt resource module before packaging."),
    ("pyemsi/gui/__main__.py", "Missing GUI launcher module."),
]

_SMOKE_TEST_SCRIPT = textwrap.dedent("""\
    import os, shutil, sys, pyemsi, PySide6, scienceplots
    scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
    os.environ["PATH"] = os.pathsep.join([
        os.path.dirname(sys.executable), scripts_dir,
        os.environ.get("PATH", ""),
    ])
    assert shutil.which("basedpyright-langserver")
    assert shutil.which("pylsp")
    print(sys.executable)
    print(pyemsi.__version__)
    print(scienceplots.__file__)
""")


LAUNCHER_C_SOURCE = Path(__file__).resolve().parent / "launcher.c"
LAUNCHER_ICO = Path(__file__).resolve().parents[1] / "pyemsi" / "resources" / "icons" / "Icon.ico"


def _render_rc(*, version_str: str, ico_path: Path | None) -> str:
    """Generate a Win32 .rc resource script with VERSIONINFO and icon."""
    parts = (version_str + ".0.0.0").split(".")[:4]
    ver_csv = ",".join(parts[:4])
    lines = [
        "#include <winver.h>",
        "",
    ]
    if ico_path and ico_path.is_file():
        lines.append(f'1 ICON "{ico_path.as_posix()}"')
        lines.append("")
    lines += [
        "VS_VERSION_INFO VERSIONINFO",
        f" FILEVERSION {ver_csv}",
        f" PRODUCTVERSION {ver_csv}",
        " FILEFLAGSMASK VS_FFI_FILEFLAGSMASK",
        " FILEFLAGS 0x0",
        " FILEOS VOS_NT_WINDOWS32",
        " FILETYPE VFT_APP",
        " FILESUBTYPE 0x0",
        "BEGIN",
        '  BLOCK "StringFileInfo"',
        "  BEGIN",
        '    BLOCK "040904B0"',
        "    BEGIN",
        '      VALUE "FileDescription", "pyemsi - EMSolution Visualization"',
        f'      VALUE "FileVersion", "{version_str}"',
        '      VALUE "ProductName", "pyemsi"',
        f'      VALUE "ProductVersion", "{version_str}"',
        '      VALUE "LegalCopyright", "Copyright \\251 SSIL"',
        '      VALUE "OriginalFilename", "pyemsi.exe"',
        "    END",
        "  END",
        '  BLOCK "VarFileInfo"',
        "  BEGIN",
        '    VALUE "Translation", 0x0409, 0x04B0',
        "  END",
        "END",
    ]
    return "\n".join(lines) + "\n"


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
    launcher_exe: Path
    script_launcher_exe: Path


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
        launcher_bat=dist_dir / "pyemsi.bat",
        script_launcher_bat=dist_dir / "run_script.bat",
        launcher_exe=dist_dir / "pyemsi.exe",
        script_launcher_exe=dist_dir / "run_script.exe",
    )


def load_pyproject(pyproject_path: Path) -> dict[str, Any]:
    with pyproject_path.open("rb") as handle:
        return tomllib.load(handle)


def _get_nested(data: Mapping[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, Mapping):
            return {}
        current = current.get(key, {})
    return current


def _unique_strings(items: Iterable[Any]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for item in items:
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
    pyproject_data = load_pyproject(pyproject_path or repo_root / "pyproject.toml")
    runtime_config = _get_nested(pyproject_data, *_RUNTIME_TOOL_KEY)
    runtime_config = runtime_config if isinstance(runtime_config, Mapping) else {}

    project_name = _get_nested(pyproject_data, "project", "name")
    app_name = project_name.strip() if isinstance(project_name, str) and project_name.strip() else "pyemsi"

    if app_module is None:
        configured_module = runtime_config.get("app_module")
        app_module = (
            configured_module.strip()
            if isinstance(configured_module, str) and configured_module.strip()
            else DEFAULT_APP_MODULE
        )

    project_deps = _get_nested(pyproject_data, "project", "dependencies")
    extra_deps = runtime_config.get("extra_dependencies", [])
    all_deps = [
        *(project_deps if isinstance(project_deps, list) else []),
        *(extra_deps if isinstance(extra_deps, list) else []),
    ]

    python_tag = "".join(python_version.split(".")[:2])
    return BuildConfig(
        app_name=app_name,
        python_version=python_version,
        python_tag=python_tag,
        app_module=app_module,
        dependencies=_unique_strings(all_deps),
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


def render_launcher_bat(
    *,
    app_module: str | None = None,
    script_mode: bool = False,
    runtime_dir_name: str = "runtime",
    app_dir_name: str = "app",
) -> str:
    lines = ["@echo off", "setlocal", "set BASE_DIR=%~dp0"]
    if script_mode:
        lines += [
            'if "%~1"=="" (',
            "  echo Usage: run_script.bat path\\to\\script.py [args...]",
            "  exit /b 1",
            ")",
            "set SCRIPT=%~1",
            "shift",
        ]
    lines += [
        f"set PYTHONHOME=%BASE_DIR%{runtime_dir_name}",
        f"set PYTHONPATH=%BASE_DIR%{app_dir_name}",
        f"set PATH=%BASE_DIR%{runtime_dir_name};%BASE_DIR%{runtime_dir_name}\\Scripts;%PATH%",
    ]
    if script_mode:
        lines.append(f'"%BASE_DIR%{runtime_dir_name}\\python.exe" "%SCRIPT%" %*')
    else:
        lines.append(f'"%BASE_DIR%{runtime_dir_name}\\python.exe" -m {app_module} %*')
    lines.append("")
    return "\r\n".join(lines)


def ensure_runtime_source_artifacts(repo_root: Path) -> None:
    for pattern, message in _REQUIRED_ARTIFACTS:
        if "*" in pattern:
            if not list(repo_root.glob(pattern)):
                raise FileNotFoundError(f"Missing {pattern}. {message}")
        elif not (repo_root / pattern).is_file():
            raise FileNotFoundError(f"Missing {pattern}. {message}")


def reset_output_directories(layout: BuildLayout) -> None:
    if layout.dist_dir.exists():
        shutil.rmtree(layout.dist_dir)
    for path in (layout.dist_dir, layout.runtime_dir, layout.app_dir, layout.cache_dir):
        path.mkdir(parents=True, exist_ok=True)


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
        get_pip_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(GET_PIP_URL, get_pip_path)

    python_exe = config.layout.runtime_dir / "python.exe"
    run_checked([str(python_exe), str(get_pip_path), "--no-warn-script-location"])
    run_checked([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    if config.dependencies:
        run_checked([str(python_exe), "-m", "pip", "install", *config.dependencies])


# ── Native .exe launcher compilation ─────────────────────────────────────


def _find_vcvarsall() -> Path | None:
    """Locate vcvarsall.bat via vswhere (ships with VS 2017+)."""
    program_files = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    vswhere = Path(program_files) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    if not vswhere.is_file():
        return None
    try:
        result = subprocess.run(
            [
                str(vswhere),
                "-latest",
                "-property",
                "installationPath",
                "-requires",
                "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        vcvarsall = Path(result.stdout.strip()) / "VC" / "Auxiliary" / "Build" / "vcvarsall.bat"
        return vcvarsall if vcvarsall.is_file() else None
    except Exception:
        return None


def _compile_native_launcher(
    source: Path,
    output_exe: Path,
    *,
    defines: list[str] | None = None,
    gui: bool = False,
    rc_file: Path | None = None,
) -> bool:
    """Compile *source* to *output_exe* with MSVC.  Returns True on success."""

    def _try_compile(*, use_vcvarsall: Path | None = None) -> bool:
        """Run the compilation.  If *use_vcvarsall* is given, prefix with it."""
        # --- resource compiler -------------------------------------------
        res_file: Path | None = None
        if rc_file and rc_file.is_file():
            res_file = rc_file.with_suffix(".res")
            rc_args = ["rc", "/nologo", f"/fo{res_file}", str(rc_file)]
            if use_vcvarsall:
                rc_cmd = f'"{use_vcvarsall}" amd64 && {subprocess.list2cmdline(rc_args)}'
                r = subprocess.run(
                    rc_cmd, shell=True, capture_output=True, text=True, timeout=60, cwd=str(output_exe.parent)
                )
            else:
                r = subprocess.run(rc_args, capture_output=True, text=True, timeout=60, cwd=str(output_exe.parent))
            if r.returncode != 0:
                res_file = None  # skip linking the resource

        # --- C compiler --------------------------------------------------
        cl_args = ["cl", "/nologo", "/O2", "/W3"]
        for d in defines or []:
            cl_args.append(f"/D{d}")
        cl_args.append(str(source))
        if res_file and res_file.is_file():
            cl_args.append(str(res_file))
        cl_args.append(f"/Fe:{output_exe}")
        link_flags = []
        if gui:
            link_flags += ["/SUBSYSTEM:WINDOWS", "/ENTRY:wmainCRTStartup"]
        if link_flags:
            cl_args += ["/link"] + link_flags

        if use_vcvarsall:
            cl_cmd = subprocess.list2cmdline(cl_args)
            shell_cmd = f'"{use_vcvarsall}" amd64 && {cl_cmd}'
            r = subprocess.run(
                shell_cmd, shell=True, capture_output=True, text=True, timeout=60, cwd=str(output_exe.parent)
            )
        else:
            r = subprocess.run(cl_args, capture_output=True, text=True, timeout=60, cwd=str(output_exe.parent))
        return r.returncode == 0 and output_exe.is_file()

    # Try cl.exe directly (works inside a Developer Command Prompt).
    if shutil.which("cl"):
        try:
            if _try_compile():
                return True
        except (subprocess.TimeoutExpired, OSError):
            pass

    # Fall back: locate vcvarsall, set up MSVC env, then compile.
    vcvarsall = _find_vcvarsall()
    if vcvarsall is None:
        return False
    try:
        return _try_compile(use_vcvarsall=vcvarsall)
    except (subprocess.TimeoutExpired, OSError):
        return False


def _cleanup_compiler_artifacts(directory: Path) -> None:
    """Remove .obj and .res files left behind by cl.exe / rc.exe."""
    for pattern in ("launcher*.obj", "*.res", "*.rc"):
        for f in directory.glob(pattern):
            f.unlink(missing_ok=True)


def compile_native_launchers(config: BuildConfig) -> bool:
    """Compile both .exe launchers.  Returns True if both succeeded."""
    if not LAUNCHER_C_SOURCE.is_file():
        print(f"Launcher C source not found: {LAUNCHER_C_SOURCE}", file=sys.stderr)
        return False

    version_str = "0.2.0"
    rc_path = config.layout.dist_dir / "launcher.rc"
    rc_path.write_text(
        _render_rc(version_str=version_str, ico_path=LAUNCHER_ICO),
        encoding="utf-8",
    )

    app_ok = _compile_native_launcher(
        LAUNCHER_C_SOURCE,
        config.layout.launcher_exe,
        defines=[f'APP_MODULE="{config.app_module}"', "NO_CONSOLE"],
        gui=True,
        rc_file=rc_path,
    )
    script_ok = _compile_native_launcher(
        LAUNCHER_C_SOURCE,
        config.layout.script_launcher_exe,
        defines=["SCRIPT_MODE"],
        gui=False,
    )
    _cleanup_compiler_artifacts(config.layout.dist_dir)
    return app_ok and script_ok


def write_launchers(config: BuildConfig) -> None:
    exe_ok = compile_native_launchers(config)
    if exe_ok:
        print("Compiled native .exe launchers.")
    else:
        print("MSVC not available — falling back to .bat launchers.", file=sys.stderr)
        config.layout.launcher_bat.write_text(
            render_launcher_bat(app_module=config.app_module),
            encoding="ascii",
        )
        config.layout.script_launcher_bat.write_text(
            render_launcher_bat(script_mode=True),
            encoding="ascii",
        )


def smoke_test(config: BuildConfig) -> None:
    python_exe = config.layout.runtime_dir / "python.exe"
    run_checked([str(python_exe), "-c", _SMOKE_TEST_SCRIPT], cwd=config.layout.dist_dir)


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
        embed_zip_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(config.embed_url, embed_zip_path)

    with zipfile.ZipFile(embed_zip_path) as archive:
        archive.extractall(config.layout.runtime_dir)
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
    launcher = config.layout.launcher_exe if config.layout.launcher_exe.is_file() else config.layout.launcher_bat
    print(f"Launcher: {launcher}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
