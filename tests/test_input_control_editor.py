"""Tests for the embedded EMSolutionDocs input control file editor.

The web page is not driven here; tests play the page's side of the bridge by
calling ``bridge.post`` and by listening to ``bridge.messageToEditor``.
"""

import json
from pathlib import Path

from PySide6.QtWidgets import QApplication

from pyemsi.widgets import input_control_editor as ice
from pyemsi.widgets.input_control_editor import InputControlEditorWidget


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _widget():
    _app()
    widget = InputControlEditorWidget()
    sent: list[dict] = []
    widget._bridge.messageToEditor.connect(lambda raw: sent.append(json.loads(raw)))
    return widget, sent


def _post(widget, message: dict) -> None:
    widget._bridge.post(json.dumps(message))


def _input_file(tmp_path: Path, text: str = '{"value": 1}') -> Path:
    path = tmp_path / "transient.json"
    path.write_text(text, encoding="utf-8")
    return path


def test_bundle_is_packaged_next_to_the_widget():
    assert (ice.BUNDLE_DIR / "editor.js").is_file()
    assert (ice.BUNDLE_DIR / "editor.css").is_file()


def test_file_is_sent_to_the_editor_once_it_is_ready(tmp_path):
    widget, sent = _widget()
    path = _input_file(tmp_path)

    widget.load_file(str(path))
    assert sent == []

    _post(widget, {"type": "ready"})
    assert sent == [{"type": "load", "name": "transient.json", "text": '{"value": 1}'}]
    assert widget.file_path == str(path.resolve())
    assert widget.text() == '{"value": 1}'
    assert widget.dirty is False


def test_reloading_after_ready_sends_the_file_immediately(tmp_path):
    widget, sent = _widget()
    _post(widget, {"type": "ready"})
    path = _input_file(tmp_path, '{"value": 2}')

    widget.load_file(str(path))

    assert sent == [{"type": "load", "name": "transient.json", "text": '{"value": 2}'}]


def test_edits_from_the_editor_update_text_and_dirty_state(tmp_path):
    widget, _sent = _widget()
    widget.load_file(str(_input_file(tmp_path)))
    dirty_events: list[bool] = []
    texts: list[str] = []
    widget.dirtyChanged.connect(dirty_events.append)
    widget.textChanged.connect(texts.append)

    _post(widget, {"type": "changed", "text": '{"value": 5}', "canSave": True})
    assert widget.text() == '{"value": 5}'
    assert widget.dirty is True

    _post(widget, {"type": "changed", "text": '{"value": 1}', "canSave": True})
    assert widget.dirty is False
    assert dirty_events == [True, False]
    assert texts == ['{"value": 5}', '{"value": 1}']


def test_invalid_alternate_format_draft_is_dirty_and_blocks_saving(tmp_path, monkeypatch):
    widget, _sent = _widget()
    path = _input_file(tmp_path)
    widget.load_file(str(path))
    warnings = []
    monkeypatch.setattr(ice._widget.QMessageBox, "warning", lambda *args: warnings.append(args[1:]))

    _post(widget, {"type": "changed", "text": '{"value": 1}', "canSave": False})
    assert widget.dirty is True

    widget.save()

    assert warnings
    assert path.read_text(encoding="utf-8") == '{"value": 1}'
    assert widget.dirty is True


def test_save_writes_the_json_payload_and_clears_dirty(tmp_path):
    widget, _sent = _widget()
    path = _input_file(tmp_path)
    widget.load_file(str(path))
    _post(widget, {"type": "changed", "text": '{"value": 9}', "canSave": True})

    widget.save()

    assert path.read_text(encoding="utf-8") == '{"value": 9}'
    assert widget.dirty is False


def test_save_request_from_the_editor_saves_only_when_dirty(tmp_path, monkeypatch):
    widget, _sent = _widget()
    widget.load_file(str(_input_file(tmp_path)))
    saves = []
    monkeypatch.setattr(widget, "save", lambda path=None: saves.append(path))

    _post(widget, {"type": "saveRequested"})
    assert saves == []

    _post(widget, {"type": "changed", "text": '{"value": 3}', "canSave": True})
    _post(widget, {"type": "saveRequested"})
    assert saves == [None]


def test_malformed_messages_are_ignored(tmp_path):
    widget, _sent = _widget()
    widget.load_file(str(_input_file(tmp_path)))

    widget._bridge.post("not json")
    _post(widget, {"type": "unknown"})

    assert widget.text() == '{"value": 1}'


def test_emsolution_input_viewer_embeds_the_input_control_editor(tmp_path):
    _app()
    from pyemsi.gui._viewers._emsolution_input_viewer import EMSolutionInputViewer

    viewer = EMSolutionInputViewer()
    viewer.load_file(str(_input_file(tmp_path)))

    assert isinstance(viewer.editor, InputControlEditorWidget)
    assert viewer.file_path == str((tmp_path / "transient.json").resolve())
