import sys

from PySide6.QtWidgets import QApplication

from pyemsi.gui._viewers._emsolution_input_viewer import EMSolutionInputViewer


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_backend_and_run_style_default_to_pyemsol_and_background():
    _app()
    viewer = EMSolutionInputViewer()

    assert viewer.backend == "pyemsol"
    assert viewer.run_style == "background"


def test_set_backend_defaults_updates_both_combos():
    _app()
    viewer = EMSolutionInputViewer()

    viewer.set_backend_defaults("executable", "window")

    assert viewer.backend == "executable"
    assert viewer.run_style == "window"


def test_style_combo_only_enabled_when_backend_is_executable():
    _app()
    viewer = EMSolutionInputViewer()
    viewer.set_backend_defaults("executable", "window")

    assert viewer._style_combo.isEnabled()

    viewer.set_backend_defaults("pyemsol", "window")

    assert not viewer._style_combo.isEnabled()


def test_executable_backend_option_hidden_on_non_windows(monkeypatch):
    _app()
    monkeypatch.setattr(sys, "platform", "linux")
    viewer = EMSolutionInputViewer()

    assert viewer._backend_combo.findData("executable") == -1
    assert viewer.backend == "pyemsol"
