import os
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
        f'echo Running EMSolution.exe in the background. && "{exe_path}" -b -d "{run_dir}" -f "transient.json"',
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
        (
            "echo Running EMSolution.exe -- its own progress window may also open. && "
            f'"{exe_path}" -b -m -d "{run_dir}" -f "transient.json"'
        ),
    ]


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
