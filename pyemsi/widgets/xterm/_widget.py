"""XtermWidget – full interactive terminal via xterm.js + pywinpty.

Architecture mirrors :class:`MonacoLspWidget`:

* Inline HTML template loads vendored xterm.js + QWebChannel JS
* ``TerminalBridge`` (QObject) shuttles data between JS and Python
* A ``QThread`` reads PTY output and pushes it through the bridge
* xterm.js renders the terminal in a QWebEngineView
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

from qtpy.QtCore import QUrl, Signal, QObject
from qtpy.QtWebChannel import QWebChannel
from qtpy.QtWebEngineWidgets import QWebEngineView

from ._bridge import TerminalBridge, TerminalPage

_PKG_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# HTML template – loaded into QWebEngineView via setHtml()
# ---------------------------------------------------------------------------

_HTML = r"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <link rel="stylesheet" href="xterm-js/xterm/css/xterm.css" />
    <style>
        * { padding: 0; margin: 0; }
        html, body { height: 100%; overflow: hidden; background: 'white'; }
        #terminal { width: 100%; height: 100%; }
    </style>
</head>
<body>
    <div id="terminal"></div>

    <script src="xterm-js/xterm/lib/xterm.js"></script>
    <script src="xterm-js/addon-fit/lib/addon-fit.js"></script>
    <script src="xterm-js/addon-web-links/lib/addon-web-links.js"></script>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
    'use strict';

    var bridge = null;
    var term = null;
    var fitAddon = null;
    var _bridgeChannel = null;
    var _termReady = false;
    var _bridgeReady = false;

    function _finishInit() {
        if (!_termReady || !_bridgeReady) return;
        bridge = _bridgeChannel.objects.bridge;
        bridge.sendDataChanged.connect(updateFromPython);
        bridge.init();
    }

    // ── Initialise xterm.js ──────────────────────────────────────────────
    term = new Terminal({
        cursorBlink: true,
        fontSize: 12,
        fontFamily: 'Consolas, "Courier New", monospace',
        theme: {
            background: 'white',
            foreground: 'black',
            cursor: '#black',
            selectionBackground: '#ccc',
        },
        allowProposedApi: true,
    });

    fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.loadAddon(new WebLinksAddon.WebLinksAddon());

    term.open(document.getElementById('terminal'));
    fitAddon.fit();

    // Forward user input to Python PTY
    term.onData(function(data) {
        sendToPython('data', data);
    });

    // Notify Python when terminal size changes
    term.onResize(function(size) {
        sendToPython('resize', { cols: size.cols, rows: size.rows });
    });

    // Re-fit on window/container resize
    new ResizeObserver(function() {
        fitAddon.fit();
    }).observe(document.getElementById('terminal'));

    _termReady = true;

    // ── QWebChannel ──────────────────────────────────────────────────────
    function sendToPython(name, value) {
        if (bridge) bridge.receive_from_js(name, JSON.stringify(value));
    }

    function updateFromPython(name, value) {
        var data = JSON.parse(value);
        switch (name) {
            case 'data':
                term.write(data);
                break;
            case 'clear':
                term.clear();
                break;
        }
    }

    window.onload = function() {
        new QWebChannel(qt.webChannelTransport, function(channel) {
            _bridgeChannel = channel;
            _bridgeReady = true;
            _finishInit();
        });
    };
    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# PTY reader – runs in a daemon thread
# ---------------------------------------------------------------------------


class _PtyReaderSignals(QObject):
    """Signals emitted by the PTY reader thread."""

    output = Signal(str)
    finished = Signal(int)


class XtermWidget(QWebEngineView):
    """Full interactive terminal widget using xterm.js + pywinpty.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.
    """

    processFinished = Signal(int)  # exit code

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._pty = None
        self._reader_thread: threading.Thread | None = None
        self._stop_reading = False
        self._signals = _PtyReaderSignals()
        self._signals.output.connect(self._on_pty_output)
        self._signals.finished.connect(self._on_pty_finished)

        # -- web engine setup (mirrors MonacoLspWidget) --
        page = TerminalPage(parent=self)
        self.setPage(page)

        base_url = QUrl.fromLocalFile((_PKG_DIR / "index.html").as_posix())
        self.setHtml(_HTML, base_url)

        self._channel = QWebChannel(self)
        self._bridge = TerminalBridge()
        self.page().setWebChannel(self._channel)
        self._channel.registerObject("bridge", self._bridge)

        # Wire bridge signals
        self._bridge.dataReceived.connect(self._write_to_pty)
        self._bridge.resizeRequested.connect(self._resize_pty)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_process(
        self,
        cmd: str | None = None,
        args: list[str] | None = None,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        """Spawn a process inside the PTY.

        Parameters
        ----------
        cmd : str, optional
            Executable to run. Defaults to ``cmd.exe`` on Windows.
        args : list[str], optional
            Arguments to pass to *cmd*.
        cwd : str, optional
            Working directory.  Defaults to the users home directory.
        env : dict, optional
            Environment variables (inherits system env by default).
        """
        if self._pty is not None:
            return  # already running

        from winpty import PtyProcess

        if cmd is None:
            cmd = os.environ.get("COMSPEC", "cmd.exe")

        argv = [cmd] + (args or [])
        dimensions = (24, 80)  # initial rows, cols – updated by JS fit addon

        spawn_env = os.environ.copy()
        if env:
            spawn_env.update(env)
        # Ensure colour support
        spawn_env.setdefault("TERM", "xterm-256color")

        self._pty = PtyProcess.spawn(
            argv,
            dimensions=dimensions,
            cwd=cwd or os.path.expanduser("~"),
            env=spawn_env,
        )

        self._stop_reading = False
        self._reader_thread = threading.Thread(
            target=self._read_loop,
            daemon=True,
        )
        self._reader_thread.start()

    @property
    def is_alive(self) -> bool:
        """Return ``True`` if the PTY process is still running."""
        return self._pty is not None and self._pty.isalive()

    def kill(self) -> None:
        """Force-kill the PTY process."""
        self._stop_reading = True
        if self._pty is not None:
            try:
                self._pty.terminate(force=True)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Private – PTY I/O
    # ------------------------------------------------------------------

    def _write_to_pty(self, data: str) -> None:
        """Forward user keystrokes from xterm.js to the PTY."""
        if self._pty is not None and self._pty.isalive():
            self._pty.write(data)

    def _resize_pty(self, cols: int, rows: int) -> None:
        """Resize the PTY to match xterm.js dimensions."""
        if self._pty is not None and self._pty.isalive():
            try:
                self._pty.setwinsize(rows, cols)
            except Exception:
                pass

    def _read_loop(self) -> None:
        """Background thread: read PTY output and push to bridge."""
        pty = self._pty
        try:
            while not self._stop_reading and pty.isalive():
                try:
                    data = pty.read(4096)
                    if data:
                        self._signals.output.emit(data)
                except EOFError:
                    break
                except Exception:
                    break
        finally:
            exitcode = -1
            try:
                if not pty.isalive():
                    exitcode = pty.exitstatus or 0
            except Exception:
                pass
            self._signals.finished.emit(exitcode)

    def _on_pty_output(self, data: str) -> None:
        """Slot: receive PTY data on the main thread and push to JS."""
        self._bridge.send_to_js("data", data)

    def _on_pty_finished(self, exitcode: int) -> None:
        """Slot: PTY process has ended."""
        self._pty = None
        self.processFinished.emit(exitcode)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        self.kill()
        super().closeEvent(event)
