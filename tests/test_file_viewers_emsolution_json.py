import json

from PySide6.QtWidgets import QApplication

from pyemsi.gui._viewers import _factory
from pyemsi.gui._viewers import _emsolution_json


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_classify_emsolution_json_detects_output_files(tmp_path):
    path = tmp_path / "output.json"
    path.write_text(
        json.dumps(
            {
                "metaData": {},
                "postDataList": {},
                "postData": {},
                "timeStep": {},
            }
        ),
        encoding="utf-8",
    )

    assert _factory.classify_emsolution_json(str(path)) == "emsolution-output"


def test_classify_emsolution_json_detects_input_files(tmp_path):
    path = tmp_path / "transient.json"
    path.write_text(
        json.dumps(
            {
                "metaData": {},
                "0_Release_Number": {},
                "1_Execution_Control": {},
                "2_Analysis_Type": {},
            }
        ),
        encoding="utf-8",
    )

    assert _factory.classify_emsolution_json(str(path)) == "emsolution-input"


def test_classify_emsolution_json_uses_loose_matching(tmp_path):
    path = tmp_path / "partial-output.json"
    path.write_text(
        json.dumps(
            {
                "postDataList": {},
                "timeStep": {},
            }
        ),
        encoding="utf-8",
    )

    assert _factory.classify_emsolution_json(str(path)) == "emsolution-output"


def test_classify_emsolution_json_ignores_other_json(tmp_path):
    path = tmp_path / "generic.json"
    path.write_text(json.dumps({"hello": "world", "items": [1, 2, 3]}), encoding="utf-8")

    assert _factory.classify_emsolution_json(str(path)) is None


def test_classify_emsolution_json_ignores_invalid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not valid json", encoding="utf-8")

    assert _factory.classify_emsolution_json(str(path)) is None


def test_create_viewer_uses_output_viewer_for_matching_json(tmp_path, monkeypatch):
    path = tmp_path / "output.json"
    path.write_text(json.dumps({"postDataList": {}, "postData": {}}), encoding="utf-8")

    class StubViewer:
        def __init__(self, parent=None):
            self.parent = parent
            self.loaded_path = None

        def load_file(self, loaded_path: str) -> None:
            self.loaded_path = loaded_path

    monkeypatch.setattr(_factory, "EMSolutionOutputViewer", StubViewer)

    viewer = _factory.create_viewer(str(path), category="text")

    assert isinstance(viewer, StubViewer)
    assert viewer.loaded_path == str(path)


def test_create_viewer_falls_back_to_text_viewer_for_generic_json(tmp_path, monkeypatch):
    path = tmp_path / "generic.json"
    path.write_text(json.dumps({"hello": "world"}), encoding="utf-8")

    class StubMonaco:
        def __init__(self, language: str, parent=None):
            self.language = language
            self.parent = parent
            self.theme = None
            self.loaded_path = None
            self.set_language = None

        def setTheme(self, theme: str) -> None:
            self.theme = theme

        def setLanguage(self, language: str) -> None:
            self.set_language = language

        def load_file(self, loaded_path: str) -> None:
            self.loaded_path = loaded_path

    monkeypatch.setattr(_factory, "MonacoLspWidget", StubMonaco)

    viewer = _factory.create_viewer(str(path), category="text")

    assert isinstance(viewer, StubMonaco)
    assert viewer.language == "json"
    assert viewer.set_language == "json"
    assert viewer.theme == "vs"
    assert viewer.loaded_path == str(path)


def test_emsolution_output_viewer_plot_action_uses_current_editor_text(monkeypatch):
    _app()

    class _Signal:
        def __init__(self):
            self._callbacks = []

        def connect(self, callback):
            self._callbacks.append(callback)

    class StubMonaco(_emsolution_json.QWidget):
        def __init__(self, language: str, parent=None):
            super().__init__(parent)
            self.language = language
            self._text = '{"metaData": {"EMSolutionVersion": "2.0"}}'
            self.textChanged = _Signal()
            self.dirtyChanged = _Signal()

        def setTheme(self, theme: str) -> None:
            self.theme = theme

        def setLanguage(self, language: str) -> None:
            self.set_language = language

        def load_file(self, path: str) -> None:
            self.file_path = path

        def text(self) -> str:
            return self._text

        @property
        def dirty(self) -> bool:
            return False

        def save(self, path: str | None = None) -> None:
            self.saved_path = path

    captured = {}

    class StubOutput:
        @classmethod
        def from_dict(cls, payload):
            captured["payload"] = payload
            return {"parsed": True}

    class StubDialog:
        def __init__(self, result, parent=None):
            captured["result"] = result
            captured["parent"] = parent

        def setAttribute(self, attr, value):
            captured["attribute"] = (attr, value)

        def show(self):
            captured["shown"] = True

        def raise_(self):
            captured["raised"] = True

        def activateWindow(self):
            captured["activated"] = True

    monkeypatch.setattr(_emsolution_json, "MonacoLspWidget", StubMonaco)
    monkeypatch.setattr(_emsolution_json, "EMSolutionOutput", StubOutput)
    monkeypatch.setattr(_emsolution_json, "EMSolutionPlotDialog", StubDialog)

    viewer = _emsolution_json.EMSolutionOutputViewer()
    viewer._plot_action.trigger()

    assert captured["payload"] == {"metaData": {"EMSolutionVersion": "2.0"}}
    assert captured["result"] == {"parsed": True}
    assert captured["parent"] is viewer
    assert captured["shown"] is True


def test_emsolution_output_viewer_plot_action_has_graph_icon():
    _app()

    viewer = _emsolution_json.EMSolutionOutputViewer()

    assert not viewer._plot_action.icon().isNull()


def test_emsolution_output_viewer_plot_action_shows_text_beside_icon():
    _app()

    viewer = _emsolution_json.EMSolutionOutputViewer()

    assert viewer._toolbar.toolButtonStyle() == _emsolution_json.Qt.ToolButtonStyle.ToolButtonTextBesideIcon


def test_emsolution_output_viewer_shows_error_for_invalid_json(monkeypatch):
    _app()

    class _Signal:
        def connect(self, callback):
            self.callback = callback

    class StubMonaco(_emsolution_json.QWidget):
        def __init__(self, language: str, parent=None):
            super().__init__(parent)
            self.textChanged = _Signal()
            self.dirtyChanged = _Signal()

        def setTheme(self, theme: str) -> None:
            self.theme = theme

        def setLanguage(self, language: str) -> None:
            self.set_language = language

        def text(self) -> str:
            return "{invalid json"

        @property
        def file_path(self):
            return None

        @property
        def dirty(self) -> bool:
            return False

        def save(self, path: str | None = None) -> None:
            self.saved_path = path

    errors = []

    monkeypatch.setattr(_emsolution_json, "MonacoLspWidget", StubMonaco)
    monkeypatch.setattr(_emsolution_json.QMessageBox, "critical", lambda *args: errors.append(args[1:]))

    viewer = _emsolution_json.EMSolutionOutputViewer()
    viewer._plot_action.trigger()

    assert errors
    assert errors[0][0] == "Invalid JSON"
