from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path
from typing import Mapping

PY_SEMANTIC_FEATURE_ENV = "PYEMSI_PY_SEMANTIC_TOKENS"
LSP_DEBUG_ENV = "PYEMSI_MONACO_LSP_DEBUG"
PY_TYPE_CHECKING_MODE_ENV = "PYEMSI_PY_TYPE_CHECKING_MODE"

_TRUE_VALUES = {"1", "true", "yes", "on", "enable", "enabled"}
_FALSE_VALUES = {"0", "false", "no", "off", "disable", "disabled"}


def is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in _TRUE_VALUES


def read_bool_env(name: str, default: bool = False, env: Mapping[str, str] | None = None) -> bool:
    scope = os.environ if env is None else env
    raw = scope.get(name)
    if raw is None:
        return default
    return is_truthy(raw)


def read_str_env(name: str, default: str, env: Mapping[str, str] | None = None) -> str:
    scope = os.environ if env is None else env
    raw = scope.get(name)
    if raw is None:
        return default
    value = raw.strip()
    return value or default


def read_bool_env_with_default(
    name: str,
    *,
    default: bool,
    env: Mapping[str, str] | None = None,
) -> bool:
    scope = os.environ if env is None else env
    raw = scope.get(name)
    if raw is None:
        return default

    normalized = raw.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    return default


def build_python_lsp_launch_command(
    port: int,
    *,
    semantic_requested: bool,
    basedpyright_executable: str | None,
    env: Mapping[str, str] | None = None,
) -> tuple[list[str], str]:
    feature_enabled = read_bool_env_with_default(
        PY_SEMANTIC_FEATURE_ENV,
        default=semantic_requested,
        env=env,
    )
    debug_enabled = read_bool_env(LSP_DEBUG_ENV, default=False, env=env)

    if semantic_requested and feature_enabled and basedpyright_executable:
        command = [
            sys.executable,
            "-m",
            "pyemsi.widgets.monaco_lsp._relay",
            "--ws-port",
            str(port),
        ]
        if debug_enabled:
            command.append("--debug")
        command.extend(["--", basedpyright_executable, "--stdio"])
        return command, "relay-basedpyright"

    return [sys.executable, "-m", "pylsp", "--ws", "--port", str(port)], "legacy-pylsp"


def as_js_bool_literal(value: bool) -> str:
    return "true" if value else "false"


def semantic_theme_enabled(
    language: str,
    *,
    semantic_requested: bool,
    env: Mapping[str, str] | None = None,
) -> bool:
    if language != "python":
        return False
    if not semantic_requested:
        return False
    return read_bool_env_with_default(
        PY_SEMANTIC_FEATURE_ENV,
        default=semantic_requested,
        env=env,
    )


def resolve_basedpyright_executable(
    *,
    python_executable: str | None = None,
    env: Mapping[str, str] | None = None,
) -> str | None:
    resolved = shutil.which("basedpyright-langserver", path=(env or os.environ).get("PATH"))
    if resolved:
        return resolved

    py_exe = Path(python_executable or sys.executable)
    candidate = py_exe.parent / ("basedpyright-langserver.exe" if os.name == "nt" else "basedpyright-langserver")
    if candidate.exists():
        return str(candidate)
    return None
