import json

from pyemsi.gui._viewers import _factory


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
