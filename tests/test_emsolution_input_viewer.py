import sys

from PySide6.QtWidgets import QApplication

from pyemsi.gui._viewers._emsolution_input_viewer import EMSolutionInputViewer


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_backend_defaults_to_pyemsol():
    _app()
    viewer = EMSolutionInputViewer()

    assert viewer.backend == "pyemsol"


def test_set_backend_default_updates_combo():
    _app()
    viewer = EMSolutionInputViewer()

    viewer.set_backend_default("executable")

    assert viewer.backend == "executable"


def test_executable_backend_option_hidden_on_non_windows(monkeypatch):
    _app()
    monkeypatch.setattr(sys, "platform", "linux")
    viewer = EMSolutionInputViewer()

    assert viewer._backend_combo.findData("executable") == -1
    assert viewer.backend == "pyemsol"
