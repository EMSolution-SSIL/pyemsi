from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl, Signal
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QFileDialog, QMessageBox

from ..file_sync import DocumentSyncState, FileSyncController
from ._bridge import InputControlEditorBridge

BUNDLE_DIR = Path(__file__).resolve().parent / "editor"

# The adapter exposes window.inputControlEditorHost before editor.js runs and
# holds outgoing messages until the web channel is connected.
_HTML = """<!doctype html>
<html data-theme="light">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="editor.css">
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<script>
(function () {
  const listeners = new Set();
  const pending = [];
  let bridge = null;
  window.inputControlEditorHost = {
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    post(message) {
      const raw = JSON.stringify(message);
      if (bridge) bridge.post(raw);
      else pending.push(raw);
    },
  };
  new QWebChannel(qt.webChannelTransport, (channel) => {
    bridge = channel.objects.bridge;
    bridge.messageToEditor.connect((raw) => {
      const message = JSON.parse(raw);
      listeners.forEach((listener) => listener(message));
    });
    pending.splice(0).forEach((raw) => bridge.post(raw));
  });
})();
</script>
</head>
<body style="margin:0;height:100vh;overflow:hidden">
<div id="input-control-file-editor-root"></div>
<script type="module" src="editor.js"></script>
</body>
</html>
"""


class _SilentPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        pass


class InputControlEditorWidget(QWebEngineView):
    """EMSolutionDocs input control file editor for one file.

    pyemsi owns the file: it reads and writes the disk, tracks dirty state and
    external changes, and sends the text to the page. The page reports edits
    and save requests. The public API mirrors ``MonacoLspWidget``.
    """

    _MAX_BYTES = 5 * 1024 * 1024  # 5 MB

    textChanged = Signal(str)
    dirtyChanged = Signal(bool)
    syncStateChanged = Signal(str)
    externalChangeChanged = Signal(bool)
    fileMissingChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._file_path: str | None = None
        self._saved_text = ""
        self._text = ""
        self._can_save = True
        self._dirty = False
        self._ready = False

        self._file_sync = FileSyncController(self)
        self._file_sync.stateChanged.connect(self._on_sync_state_changed)
        self._file_sync.missingChanged.connect(self.fileMissingChanged.emit)
        self._file_sync.reloadRequested.connect(self._on_reload_requested)

        self.setPage(_SilentPage(self))
        self._bridge = InputControlEditorBridge(self)
        self._channel = QWebChannel(self)
        self._channel.registerObject("bridge", self._bridge)
        self.page().setWebChannel(self._channel)
        self._bridge.messageFromEditor.connect(self._on_editor_message)
        self.setHtml(_HTML, QUrl.fromLocalFile((BUNDLE_DIR / "index.html").as_posix()))

    # -- messages from the page --------------------------------------------

    def _on_editor_message(self, message: dict) -> None:
        kind = message["type"]
        if kind == "ready":
            self._ready = True
            self._send_load()
        elif kind == "changed":
            text = message.get("text")
            if not isinstance(text, str):
                return
            self._can_save = bool(message.get("canSave", True))
            if text != self._text:
                self._text = text
                self.textChanged.emit(text)
            self._update_dirty()
        elif kind == "saveRequested":
            # pyemsi's own Ctrl+S shortcut may already have saved.
            if self._dirty:
                self.save()

    def _send_load(self) -> None:
        if self._ready and self._file_path is not None:
            self._bridge.send({"type": "load", "name": Path(self._file_path).name, "text": self._text})

    # -- dirty and sync state ----------------------------------------------

    def _update_dirty(self) -> None:
        dirty = self._text != self._saved_text or not self._can_save
        if dirty != self._dirty:
            self._dirty = dirty
            self._file_sync.set_dirty(dirty)
            self.dirtyChanged.emit(dirty)

    def _on_sync_state_changed(self, state: str) -> None:
        self.syncStateChanged.emit(state)
        self.externalChangeChanged.emit(
            state in {DocumentSyncState.EXTERNALLY_MODIFIED.value, DocumentSyncState.CONFLICT.value}
        )

    def _on_reload_requested(self, path: str) -> None:
        if not self._dirty:
            self.load_file(path)

    # -- file I/O ----------------------------------------------------------

    def load_file(self, path: str) -> None:
        """Read *path* and show it in the editor."""
        resolved_path = str(Path(path).resolve())
        with open(resolved_path, "r", encoding="utf-8", errors="replace") as stream:
            text = stream.read(self._MAX_BYTES)
        self._file_path = resolved_path
        self._saved_text = text
        self._text = text
        self._can_save = True
        self.textChanged.emit(text)
        self._update_dirty()
        self._file_sync.monitor_file(resolved_path)
        self._send_load()

    def save(self, path: str | None = None) -> None:
        """Write the editor's JSON to *path* (defaults to the loaded file)."""
        target = path or self._file_path
        if target is None:
            raise ValueError("No file path specified for save")
        if not self._can_save:
            QMessageBox.warning(
                self,
                "Cannot Save",
                "Fix or discard the invalid YAML or TOML changes before saving.",
            )
            return
        resolved_target = self._prompt_conflicted_save(str(Path(target).resolve()))
        if resolved_target is None:
            return
        with open(resolved_target, "w", encoding="utf-8") as stream:
            stream.write(self._text)
        self._file_path = resolved_target
        self._saved_text = self._text
        self._update_dirty()
        self._file_sync.mark_saved(resolved_target)

    def _prompt_conflicted_save(self, target: str) -> str | None:
        if not self.has_external_change or target != self._file_path:
            return target

        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("File Changed On Disk")
        dialog.setText("This file changed on disk after you started editing it.")
        dialog.setInformativeText(
            "Choose Overwrite to replace the on-disk file, or Save As to keep your edits in a new file."
        )
        overwrite_button = dialog.addButton("Overwrite", QMessageBox.ButtonRole.AcceptRole)
        save_as_button = dialog.addButton("Save As...", QMessageBox.ButtonRole.ActionRole)
        dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked is overwrite_button:
            return target
        if clicked is save_as_button:
            selected_path, _selected_filter = QFileDialog.getSaveFileName(self, "Save As", target, "JSON (*.json)")
            if selected_path:
                return str(Path(selected_path).resolve())
        return None

    # -- public API --------------------------------------------------------

    def text(self) -> str:
        return self._text

    @property
    def file_path(self) -> str | None:
        return self._file_path

    @property
    def dirty(self) -> bool:
        return self._dirty

    @property
    def sync_state(self) -> str:
        return self._file_sync.state.value

    @property
    def has_external_change(self) -> bool:
        return self._file_sync.has_external_change

    @property
    def file_missing(self) -> bool:
        return self._file_sync.missing
