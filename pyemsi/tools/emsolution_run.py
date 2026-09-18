"""Command construction for running EMSolution input files.

Centralizes the cmd/args/cwd choice for both run backends (pyemsol and the
EMSolution.exe executable) so main_window.py has one place to build the
command it hands to ExternalTerminalDock.add_terminal.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class RunCommand:
    cmd: str
    args: list[str]
    cwd: str
    title: str


def build_run_command(
    input_path: str,
    backend: str,
    executable_path: str | None = None,
) -> RunCommand:
    """Build the terminal command that runs *input_path* with the chosen backend."""
    folder = os.path.dirname(input_path)
    filename = os.path.basename(input_path)

    if backend == "pyemsol":
        run_emsol_script = os.path.join(os.path.dirname(__file__), "run_emsol.py")
        return RunCommand(
            cmd=sys.executable,
            args=[run_emsol_script, input_path],
            cwd=folder,
            title=f"pyemsol — {filename}",
        )

    if backend != "executable":
        raise ValueError(f"unknown backend: {backend!r}")
    if not executable_path:
        raise ValueError("executable_path is required for the executable backend")

    # EMSolution's own docs require the run directory to end with a
    # trailing backslash (runWindows.rst: "directory名の最後は\として下さい").
    run_dir = folder + os.sep

    # args must be plain, unquoted argv tokens, never a pre-quoted shell
    # string: XtermWidget spawns via pywinpty's PtyProcess.spawn, which
    # re-quotes every element with subprocess.list2cmdline. Handing it a
    # token that already contains literal '"' characters (meant for cmd.exe's
    # own parsing) makes list2cmdline escape those quotes and wrap the whole
    # token again, corrupting the command cmd.exe actually receives.
    args = [
        "/c",
        "echo",
        "Running",
        "EMSolution.exe.",
        "&&",
        executable_path,
        "-b",
        "-d",
        run_dir,
        "-f",
        filename,
    ]

    return RunCommand(
        cmd="cmd",
        args=args,
        cwd=folder,
        title=f"EMSolution.exe — {filename}",
    )
