from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from qtpy.QtCore import QObject, QFileSystemWatcher, QTimer, Signal


class DocumentSyncState(str, Enum):
    CLEAN = "clean"
    DIRTY = "dirty"
    EXTERNALLY_MODIFIED = "externally_modified"
    CONFLICT = "conflict"
    MISSING = "missing"
    MISSING_DIRTY = "missing_dirty"


@dataclass(frozen=True)
class _FileSnapshot:
    path: str
    exists: bool
    size: int = 0
    mtime_ns: int = 0

    @classmethod
    def capture(cls, path: str) -> _FileSnapshot:
        try:
            stat_result = os.stat(path)
        except OSError:
            return cls(path=path, exists=False)
        return cls(
            path=path,
            exists=True,
            size=stat_result.st_size,
            mtime_ns=stat_result.st_mtime_ns,
        )


class FileSyncController(QObject):
    """Track on-disk changes for a single text document.

    The controller owns a QFileSystemWatcher plus a small debounce timer.
    It does not mutate editor contents directly; instead it emits signals so
    the owning widget can decide whether to reload, keep local edits, or show
    a missing-file state.
    """

    stateChanged = Signal(str)
    reloadRequested = Signal(str)
    externalChangeDetected = Signal(str)
    missingChanged = Signal(bool)

    def __init__(self, parent: QObject | None = None, debounce_ms: int = 150) -> None:
        super().__init__(parent)
        self._debounce_ms = debounce_ms
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._schedule_check)
        self._watcher.directoryChanged.connect(self._schedule_check)

        self._check_timer = QTimer(self)
        self._check_timer.setSingleShot(True)
        self._check_timer.timeout.connect(self.check_now)

        self._file_path: str | None = None
        self._directory_path: str | None = None
        self._baseline: _FileSnapshot | None = None
        self._dirty = False
        self._external_change = False
        self._missing = False

    @property
    def file_path(self) -> str | None:
        return self._file_path

    @property
    def dirty(self) -> bool:
        return self._dirty

    @property
    def has_external_change(self) -> bool:
        return self._external_change

    @property
    def missing(self) -> bool:
        return self._missing

    @property
    def state(self) -> DocumentSyncState:
        if self._missing:
            return DocumentSyncState.MISSING_DIRTY if self._dirty else DocumentSyncState.MISSING
        if self._external_change:
            return DocumentSyncState.CONFLICT if self._dirty else DocumentSyncState.EXTERNALLY_MODIFIED
        return DocumentSyncState.DIRTY if self._dirty else DocumentSyncState.CLEAN

    def monitor_file(self, path: str) -> DocumentSyncState:
        resolved_path = str(Path(path).resolve())
        old_state = self.state
        old_missing = self._missing

        self._file_path = resolved_path
        self._directory_path = str(Path(resolved_path).parent)
        self._baseline = _FileSnapshot.capture(resolved_path)
        self._dirty = False
        self._external_change = False
        self._missing = not self._baseline.exists

        self._rewatch_paths()
        self._emit_missing_if_changed(old_missing)
        self._emit_state_if_changed(old_state)
        return self.state

    def clear(self) -> None:
        old_state = self.state
        old_missing = self._missing
        self._file_path = None
        self._directory_path = None
        self._baseline = None
        self._dirty = False
        self._external_change = False
        self._missing = False
        self._check_timer.stop()
        self._clear_watch_paths()
        self._emit_missing_if_changed(old_missing)
        self._emit_state_if_changed(old_state)

    def set_dirty(self, dirty: bool) -> DocumentSyncState:
        old_state = self.state
        self._dirty = dirty
        self._emit_state_if_changed(old_state)
        return self.state

    def mark_reloaded(self) -> DocumentSyncState:
        if self._file_path is None:
            return self.state

        old_state = self.state
        old_missing = self._missing
        self._baseline = _FileSnapshot.capture(self._file_path)
        self._external_change = False
        self._missing = not self._baseline.exists
        self._rewatch_paths()
        self._emit_missing_if_changed(old_missing)
        self._emit_state_if_changed(old_state)
        return self.state

    def mark_saved(self, path: str | None = None) -> DocumentSyncState:
        old_state = self.state
        old_missing = self._missing

        if path is not None:
            self._file_path = str(Path(path).resolve())
            self._directory_path = str(Path(self._file_path).parent)

        self._dirty = False
        self._external_change = False

        if self._file_path is not None:
            self._baseline = _FileSnapshot.capture(self._file_path)
            self._missing = not self._baseline.exists
            self._rewatch_paths()
        else:
            self._baseline = None
            self._missing = False
            self._clear_watch_paths()

        self._emit_missing_if_changed(old_missing)
        self._emit_state_if_changed(old_state)
        return self.state

    def check_now(self) -> DocumentSyncState:
        if self._file_path is None:
            return self.state

        old_state = self.state
        old_missing = self._missing
        had_external_change = self._external_change
        current = _FileSnapshot.capture(self._file_path)
        baseline = self._baseline

        self._missing = not current.exists
        newly_changed = False

        if current.exists:
            if baseline is None:
                self._baseline = current
            elif current != baseline:
                self._external_change = True
                newly_changed = not had_external_change
        else:
            self._external_change = False

        self._rewatch_paths()
        self._emit_missing_if_changed(old_missing)
        self._emit_state_if_changed(old_state)

        if newly_changed:
            if self._dirty:
                self.externalChangeDetected.emit(self._file_path)
            else:
                self.reloadRequested.emit(self._file_path)

        return self.state

    def _schedule_check(self, *_args: object) -> None:
        self._check_timer.start(self._debounce_ms)

    def _clear_watch_paths(self) -> None:
        watched_files = self._watcher.files()
        if watched_files:
            self._watcher.removePaths(watched_files)
        watched_dirs = self._watcher.directories()
        if watched_dirs:
            self._watcher.removePaths(watched_dirs)

    def _rewatch_paths(self) -> None:
        self._clear_watch_paths()
        if self._directory_path and os.path.isdir(self._directory_path):
            self._watcher.addPath(self._directory_path)
        if self._file_path and os.path.exists(self._file_path):
            self._watcher.addPath(self._file_path)

    def _emit_state_if_changed(self, old_state: DocumentSyncState) -> None:
        new_state = self.state
        if new_state != old_state:
            self.stateChanged.emit(new_state.value)

    def _emit_missing_if_changed(self, old_missing: bool) -> None:
        if self._missing != old_missing:
            self.missingChanged.emit(self._missing)
