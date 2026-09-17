import subprocess
import threading
import time

from PySide6.QtWidgets import QApplication

from pyemsi.widgets.xterm._widget import XtermWidget


class _StuckReadFakePty:
    """Simulates a real pywinpty quirk observed with EMSolution.exe: after the
    child process exits, `pty.isalive()` correctly and promptly flips to
    False, but `pty.read()` (a blocking call into winpty's compiled
    extension) never returns -- there is no EOF and no exception, it just
    hangs. Before the `_watch_loop` fallback, `_read_loop`'s only way to
    notice completion was via that same blocked `read()` call, so neither a
    natural process exit nor a forced `kill()` ever reached the UI.
    """

    def __init__(self) -> None:
        self._alive = True
        self._blocked_forever = threading.Event()  # never set

    def isalive(self) -> bool:
        return self._alive

    def read(self, size: int = 4096) -> str:
        self._blocked_forever.wait()
        raise EOFError("unreachable in this test")

    @property
    def exitstatus(self):
        return 0

    def die(self) -> None:
        self._alive = False


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _pump_until(condition, timeout_s: float = 5.0) -> bool:
    app = QApplication.instance()
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        app.processEvents()
        if condition():
            return True
        time.sleep(0.02)
    return False


def test_processFinished_fires_when_read_loop_is_stuck_on_dead_process(monkeypatch):
    """Regression test for the Run/Stop buttons staying stuck: `_watch_loop`
    must report completion via `pty.isalive()` even when `_read_loop` is
    permanently blocked inside `pty.read()`.
    """
    _app()
    fake_pty = _StuckReadFakePty()
    monkeypatch.setattr("winpty.PtyProcess.spawn", staticmethod(lambda *a, **kw: fake_pty))

    xterm = XtermWidget()
    received = {}
    xterm.processFinished.connect(lambda code: received.setdefault("code", code))

    xterm.start_process(cmd="fake-cmd", args=[])
    assert xterm.is_alive is True

    fake_pty.die()

    assert _pump_until(lambda: "code" in received), "processFinished never fired for a dead process"
    assert received["code"] == 0
    assert xterm.is_alive is False


def test_kill_reports_finished_even_when_read_loop_is_stuck(monkeypatch):
    """Regression test for the Stop button doing nothing: `kill()` actually
    terminates the process, but with the old code the UI never learned
    about it because `_read_loop` stayed stuck in `pty.read()`.
    """
    _app()
    fake_pty = _StuckReadFakePty()
    monkeypatch.setattr("winpty.PtyProcess.spawn", staticmethod(lambda *a, **kw: fake_pty))

    def _terminate(force=False):
        fake_pty.die()
        return True

    fake_pty.terminate = _terminate

    xterm = XtermWidget()
    received = {}
    xterm.processFinished.connect(lambda code: received.setdefault("code", code))

    xterm.start_process(cmd="fake-cmd", args=[])
    xterm.kill()

    assert _pump_until(lambda: "code" in received), "processFinished never fired after kill()"


def _ping_pids() -> list[str]:
    out = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq PING.EXE"],
        capture_output=True,
        text=True,
    )
    return [line.split()[1] for line in out.stdout.splitlines() if line.upper().startswith("PING.EXE")]


def test_kill_terminates_grandchild_process_not_just_immediate_child():
    """Regression test: EMSolution.exe is spawned as a grandchild of the PTY's
    tracked process, via `cmd /c echo ... && EMSolution.exe ...` (see
    build_run_command). `PtyProcess.terminate()` only calls TerminateProcess
    on the single pid winpty tracks (cmd.exe) -- it does not touch any
    grandchild process cmd.exe spawned. Once EMSolution.exe is actually
    running mid-simulation, killing only cmd.exe orphans it and the
    simulation keeps running untouched, which is exactly the reported bug
    ("stop button does not halt the process in the middle of the
    simulation"). Uses `ping.exe` (always present on Windows, chained the
    same way EMSolution.exe is) as a fast, portable stand-in for a real
    long-running grandchild -- no dependency on the user's real
    EMSolution.exe binary.
    """
    _app()

    for _ in range(50):
        if not _ping_pids():
            break
        time.sleep(0.1)
    assert not _ping_pids(), "a leftover PING.EXE from a previous run is still alive; aborting"

    xterm = XtermWidget()
    xterm.start_process(cmd="cmd", args=["/c", "echo", "starting", "&&", "ping", "-n", "30", "127.0.0.1"])

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and not _ping_pids():
        time.sleep(0.1)
    pids_before = _ping_pids()
    assert pids_before, "ping.exe (the grandchild process) never started"

    try:
        xterm.kill()

        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and _ping_pids():
            time.sleep(0.1)

        assert not _ping_pids(), (
            "ping.exe (the grandchild process) is still running after kill() -- "
            "the process tree was not actually terminated"
        )
    finally:
        for pid in _ping_pids():
            subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)


def test_write_pushes_text_to_the_terminal_with_crlf_line_endings():
    _app()
    xterm = XtermWidget()
    sent: list[tuple[str, object]] = []
    xterm._bridge.send_to_js = lambda name, value: sent.append((name, value))

    xterm.write("line one\nline two\r\nno newline")

    assert sent == [("data", "line one\r\nline two\r\nno newline")]
    assert xterm.is_alive is False
