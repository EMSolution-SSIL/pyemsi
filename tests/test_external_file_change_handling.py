from __future__ import annotations

from PySide6.QtWidgets import QApplication, QWidget

from pyemsi.gui._viewers import _python as python_viewer_module
from pyemsi.gui._viewers import _unsupported as unsupported_viewer_module
import pyemsi.widgets.monaco_lsp as monaco_module
from pyemsi.widgets.file_sync import DocumentSyncState, FileSyncController
from pyemsi.widgets.monaco_lsp._widget import MonacoLspWidget
from pyemsi.widgets.split_container import SplitContainer


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _SignalRecorder:
    def __init__(self) -> None:
        self.values = []

    def emit(self, value=None) -> None:
        self.values.append(value)


class _StubSignal:
    def __init__(self) -> None:
        self._callbacks = []

    def connect(self, callback) -> None:
        self._callbacks.append(callback)

    def emit(self, value=None) -> None:
        for callback in list(self._callbacks):
            callback(value)


class _FakeBridge:
    def __init__(self) -> None:
        self.value = ""
        self.sent = []

    def send_to_js(self, key, value) -> None:
        self.sent.append((key, value))


class _StubMonaco(QWidget):
    def __init__(self, language: str, parent=None, **_kwargs) -> None:
        super().__init__(parent)
        self.language = language
        self.parent = parent
        self.textChanged = _StubSignal()
        self.dirtyChanged = _StubSignal()
        self.syncStateChanged = _StubSignal()
        self.externalChangeChanged = _StubSignal()
        self.fileMissingChanged = _StubSignal()
        self.file_path = None
        self.dirty = False
        self.sync_state = "clean"
        self.has_external_change = False
        self.file_missing = False

    def setTheme(self, theme: str) -> None:
        self.theme = theme

    def setLanguage(self, language: str) -> None:
        self.set_language = language

    def load_file(self, path: str) -> None:
        self.file_path = path

    def save(self, path: str | None = None) -> None:
        self.saved_path = path


class _FakeMonacoHost:
    def __init__(self) -> None:
        self._MAX_BYTES = MonacoLspWidget._MAX_BYTES
        self._bridge = _FakeBridge()
        self._file_sync = FileSyncController()
        self._language = "plaintext"
        self._python_analysis_paths = []
        self._file_path = None
        self._dirty = False
        self._initial_text = ""
        self.textChanged = _SignalRecorder()
        self.dirtyChanged = _SignalRecorder()
        self.syncStateChanged = _SignalRecorder()
        self.externalChangeChanged = _SignalRecorder()
        self.fileMissingChanged = _SignalRecorder()
        self.updated_analysis_path = None

    def setText(self, text: str) -> None:
        self._bridge.value = text

    def text(self) -> str:
        return self._bridge.value

    @property
    def has_external_change(self) -> bool:
        return self._file_sync.has_external_change

    def _update_python_analysis_paths(self, path: str) -> None:
        self.updated_analysis_path = path

    def _mark_clean(self) -> None:
        MonacoLspWidget._mark_clean(self)

    def _prompt_conflicted_save(self, target: str) -> str | None:
        return target


def test_file_sync_controller_starts_clean_for_existing_file(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")

    controller = FileSyncController()

    state = controller.monitor_file(str(path))

    assert state is DocumentSyncState.CLEAN
    assert controller.file_path == str(path.resolve())
    assert controller.missing is False
    assert controller.has_external_change is False


def test_file_sync_controller_reports_reload_request_for_clean_external_change(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")
    controller = FileSyncController()
    requested = []
    controller.reloadRequested.connect(requested.append)
    controller.monitor_file(str(path))

    path.write_text("hello from disk", encoding="utf-8")
    state = controller.check_now()

    assert state is DocumentSyncState.EXTERNALLY_MODIFIED
    assert requested == [str(path.resolve())]
    assert controller.has_external_change is True


def test_file_sync_controller_reports_conflict_for_dirty_external_change(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")
    controller = FileSyncController()
    conflicts = []
    controller.externalChangeDetected.connect(conflicts.append)
    controller.monitor_file(str(path))
    controller.set_dirty(True)

    path.write_text("hello from disk", encoding="utf-8")
    state = controller.check_now()

    assert state is DocumentSyncState.CONFLICT
    assert conflicts == [str(path.resolve())]
    assert controller.has_external_change is True


def test_file_sync_controller_reports_missing_file(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")
    controller = FileSyncController()
    missing_states = []
    controller.missingChanged.connect(missing_states.append)
    controller.monitor_file(str(path))

    path.unlink()
    state = controller.check_now()

    assert state is DocumentSyncState.MISSING
    assert missing_states == [True]
    assert controller.missing is True


def test_file_sync_controller_reports_missing_dirty_file(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")
    controller = FileSyncController()
    controller.monitor_file(str(path))
    controller.set_dirty(True)

    path.unlink()
    state = controller.check_now()

    assert state is DocumentSyncState.MISSING_DIRTY
    assert controller.missing is True


def test_file_sync_controller_mark_saved_clears_external_state(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")
    controller = FileSyncController()
    controller.monitor_file(str(path))
    controller.set_dirty(True)
    path.write_text("hello from disk", encoding="utf-8")
    controller.check_now()

    path.write_text("hello from editor", encoding="utf-8")
    state = controller.mark_saved(str(path))

    assert state is DocumentSyncState.CLEAN
    assert controller.missing is False
    assert controller.has_external_change is False


def test_monaco_load_file_initializes_file_sync_controller(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")
    host = _FakeMonacoHost()

    MonacoLspWidget.load_file(host, str(path))

    assert host._file_path == str(path.resolve())
    assert host._bridge.value == "hello"
    assert host._file_sync.file_path == str(path.resolve())
    assert host._file_sync.state is DocumentSyncState.CLEAN
    assert host.textChanged.values == ["hello"]


def test_monaco_on_value_changed_updates_file_sync_dirty_state(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")
    host = _FakeMonacoHost()
    MonacoLspWidget.load_file(host, str(path))
    host._bridge.value = "hello world"

    MonacoLspWidget._on_value_changed(host)

    assert host._dirty is True
    assert host._file_sync.state is DocumentSyncState.DIRTY
    assert host.dirtyChanged.values == [True]


def test_monaco_save_updates_controller_baseline(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")
    host = _FakeMonacoHost()
    MonacoLspWidget.load_file(host, str(path))
    host._bridge.value = "hello world"
    host._dirty = True
    host._file_sync.set_dirty(True)

    MonacoLspWidget.save(host)

    assert path.read_text(encoding="utf-8") == "hello world"
    assert host._file_sync.state is DocumentSyncState.CLEAN
    assert host._file_sync.has_external_change is False


def test_monaco_save_uses_save_as_target_when_conflicted(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    save_as_path = tmp_path / "copy.txt"
    path.write_text("hello", encoding="utf-8")
    host = _FakeMonacoHost()
    MonacoLspWidget.load_file(host, str(path))
    host._bridge.value = "hello from editor"
    host._dirty = True
    host._file_sync.set_dirty(True)
    path.write_text("hello from disk", encoding="utf-8")
    host._file_sync.check_now()
    host._prompt_conflicted_save = lambda _target: str(save_as_path)

    MonacoLspWidget.save(host)

    assert path.read_text(encoding="utf-8") == "hello from disk"
    assert save_as_path.read_text(encoding="utf-8") == "hello from editor"
    assert host._file_sync.file_path == str(save_as_path.resolve())
    assert host._file_sync.state is DocumentSyncState.CLEAN


def test_monaco_save_can_cancel_conflicted_save(tmp_path):
    _app()
    path = tmp_path / "example.txt"
    path.write_text("hello", encoding="utf-8")
    host = _FakeMonacoHost()
    MonacoLspWidget.load_file(host, str(path))
    host._bridge.value = "hello from editor"
    host._dirty = True
    host._file_sync.set_dirty(True)
    path.write_text("hello from disk", encoding="utf-8")
    host._file_sync.check_now()
    host._prompt_conflicted_save = lambda _target: None

    MonacoLspWidget.save(host)

    assert path.read_text(encoding="utf-8") == "hello from disk"
    assert host._file_sync.state is DocumentSyncState.CONFLICT


def test_python_viewer_forwards_sync_state_signal(monkeypatch):
    _app()
    monkeypatch.setattr(python_viewer_module, "MonacoLspWidget", _StubMonaco)

    viewer = python_viewer_module.PythonViewer()
    sync_values = []
    external_values = []
    missing_values = []
    viewer.syncStateChanged.connect(sync_values.append)
    viewer.externalChangeChanged.connect(external_values.append)
    viewer.fileMissingChanged.connect(missing_values.append)

    viewer.editor.syncStateChanged.emit("conflict")
    viewer.editor.externalChangeChanged.emit(True)
    viewer.editor.fileMissingChanged.emit(True)

    assert sync_values == ["conflict"]
    assert external_values == [True]
    assert missing_values == [True]


def test_unsupported_viewer_open_as_text_exposes_monaco_sync_properties(monkeypatch, tmp_path):
    _app()
    monkeypatch.setattr(monaco_module, "MonacoLspWidget", _StubMonaco)
    path = tmp_path / "example.dat"
    path.write_text("hello", encoding="utf-8")
    viewer = unsupported_viewer_module.UnsupportedViewer(str(path))

    viewer._open_as_text()
    viewer._monaco.sync_state = "conflict"
    viewer._monaco.has_external_change = True
    viewer._monaco.file_missing = True

    assert viewer.sync_state == "conflict"
    assert viewer.has_external_change is True
    assert viewer.file_missing is True


def test_split_container_formats_combined_document_markers():
    _app()

    class _StateWidget(QWidget):
        def __init__(self) -> None:
            super().__init__()
            self.dirty = True
            self.has_external_change = True
            self.file_missing = True

    widget = _StateWidget()

    title = SplitContainer._format_tab_title("example.txt", widget)

    assert title == "example.txt * ! [missing]"
