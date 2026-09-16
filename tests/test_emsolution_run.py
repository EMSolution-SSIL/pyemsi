import os
import subprocess
import sys

from pyemsi.tools.emsolution_run import build_run_command


def test_build_run_command_pyemsol_matches_existing_behavior(tmp_path):
    input_path = str(tmp_path / "transient.json")

    command = build_run_command(input_path, backend="pyemsol", run_style="background")

    expected_script = os.path.join(os.path.dirname(__file__), os.pardir, "pyemsi", "tools", "run_emsol.py")
    assert command.cmd == sys.executable
    assert command.args[0].endswith(os.path.join("tools", "run_emsol.py"))
    assert command.args[1] == input_path
    assert command.cwd == str(tmp_path)
    assert command.title == "pyemsol — transient.json"


def test_build_run_command_executable_background(tmp_path):
    input_path = str(tmp_path / "transient.json")
    exe_path = str(tmp_path / "EMSolution.exe")

    command = build_run_command(
        input_path, backend="executable", run_style="background", executable_path=exe_path
    )

    run_dir = str(tmp_path) + os.sep
    assert command.cmd == "cmd"
    assert command.args == [
        "/c",
        "echo",
        "Running",
        "EMSolution.exe",
        "in",
        "the",
        "background.",
        "&&",
        exe_path,
        "-b",
        "-d",
        run_dir,
        "-f",
        "transient.json",
    ]
    assert command.cwd == str(tmp_path)
    assert command.title == "EMSolution.exe — transient.json"


def test_build_run_command_executable_window_adds_m_flag_and_note(tmp_path):
    input_path = str(tmp_path / "transient.json")
    exe_path = str(tmp_path / "EMSolution.exe")

    command = build_run_command(
        input_path, backend="executable", run_style="window", executable_path=exe_path
    )

    run_dir = str(tmp_path) + os.sep
    assert command.args == [
        "/c",
        "echo",
        "Running",
        "EMSolution.exe",
        "--",
        "its",
        "own",
        "progress",
        "window",
        "may",
        "also",
        "open.",
        "&&",
        exe_path,
        "-b",
        "-m",
        "-d",
        run_dir,
        "-f",
        "transient.json",
    ]


def test_build_run_command_executable_args_contain_no_manual_quotes(tmp_path):
    """Regression test: pywinpty's PtyProcess.spawn always re-quotes `args` via
    subprocess.list2cmdline before handing them to cmd.exe. A pre-quoted shell
    string (with literal embedded '"' characters) gets its quotes escaped and
    the whole thing re-wrapped, corrupting the command cmd.exe actually sees
    (observed as EMSolution.exe reporting a garbled/wrong -d path). args must
    always be plain, unquoted argv tokens so list2cmdline can quote them
    correctly itself.
    """
    input_path = str(tmp_path / "transient.json")
    exe_path = str(tmp_path / "EMSolution.exe")

    command = build_run_command(
        input_path, backend="executable", run_style="background", executable_path=exe_path
    )

    assert all('"' not in arg for arg in command.args)


def test_build_run_command_executable_run_dir_with_spaces_survives_list2cmdline(tmp_path):
    """The trailing backslash EMSolution requires on -d must survive
    subprocess.list2cmdline's quoting even when the run directory contains a
    space (which forces list2cmdline to quote that token). A bare trailing
    backslash immediately before a closing quote is misparsed by native argv
    parsers (like EMSolution.exe's own) unless list2cmdline doubles it --
    which it only does correctly if we pass the path as its own plain token.
    """
    spacey_dir = tmp_path / "My Run Folder"
    spacey_dir.mkdir()
    input_path = str(spacey_dir / "transient.json")
    exe_path = str(tmp_path / "EMSolution.exe")

    command = build_run_command(
        input_path, backend="executable", run_style="background", executable_path=exe_path
    )

    run_dir_token = str(spacey_dir) + os.sep
    assert run_dir_token in command.args

    quoted_run_dir = subprocess.list2cmdline([run_dir_token])
    assert quoted_run_dir == '"' + str(spacey_dir) + os.sep + '\\"'
    assert quoted_run_dir in subprocess.list2cmdline(command.args)


def test_build_run_command_executable_requires_executable_path(tmp_path):
    input_path = str(tmp_path / "transient.json")

    try:
        build_run_command(input_path, backend="executable", run_style="background", executable_path=None)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_build_run_command_rejects_unknown_backend(tmp_path):
    input_path = str(tmp_path / "transient.json")

    try:
        build_run_command(input_path, backend="bogus", run_style="background")
        assert False, "expected ValueError"
    except ValueError:
        pass
