#!/usr/bin/env python3
"""PostToolUse hook: auto-format edited Python files with Ruff."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

EDIT_TOOL_NAMES = {
    "apply_patch",
    "create_file",
    "editFiles",
    "replace_string_in_file",
    "vscode_renameSymbol",
}
PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Update|Add|Delete) File:\s+(.+?)(?:\s*->.*)?$")


def _json_out(payload: dict) -> None:
    print(json.dumps(payload), flush=True)


def _iter_patch_paths(text: str) -> Iterable[str]:
    for line in text.splitlines():
        match = PATCH_FILE_RE.match(line.strip())
        if match:
            yield match.group(1).strip()


def _iter_strings(value: object) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return

    if isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)
        return

    if isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)


def _normalize_py_path(raw: str, cwd: Path) -> Path | None:
    text = raw.strip().strip('"').strip("'")
    if not text or text.startswith("{"):
        return None

    path_text = text.replace("\\", "/")
    if not path_text.lower().endswith(".py"):
        return None

    path = Path(text)
    if not path.is_absolute():
        path = cwd / path

    return path.resolve()


def _collect_python_files(payload: dict) -> list[Path]:
    cwd = Path(payload.get("cwd") or os.getcwd())
    tool_name = str(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input", {})

    if tool_name not in EDIT_TOOL_NAMES:
        return []

    files: set[Path] = set()

    for text in _iter_strings(tool_input):
        if "*** Begin Patch" in text:
            for patch_path in _iter_patch_paths(text):
                path = _normalize_py_path(patch_path, cwd)
                if path:
                    files.add(path)
            continue

        path = _normalize_py_path(text, cwd)
        if path:
            files.add(path)

    return sorted(path for path in files if path.exists())


def _run_ruff(files: list[Path]) -> tuple[bool, str]:
    cmd = [sys.executable, "-m", "ruff", "format", *[str(p) for p in files]]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        return True, ""

    stderr = (result.stderr or "").strip()
    stdout = (result.stdout or "").strip()
    details = stderr or stdout or "Ruff exited with a non-zero status."
    return False, details


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # pragma: no cover
        _json_out(
            {
                "continue": True,
                "systemMessage": f"Ruff hook skipped: invalid hook input ({exc}).",
            }
        )
        return 0

    files = _collect_python_files(payload)
    if not files:
        _json_out({"continue": True})
        return 0

    ok, details = _run_ruff(files)
    if ok:
        _json_out({"continue": True})
        return 0

    _json_out(
        {
            "continue": True,
            "systemMessage": f"Ruff format hook warning: {details}",
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
