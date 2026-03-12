from matplotlib.figure import Figure
from PySide6.QtWidgets import QApplication

from pyemsi import gui
from pyemsi.widgets.split_container import SplitContainer


class _DummyWindow:
    def __init__(self) -> None:
        self.container = SplitContainer()


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _uses_tight_layout(figure: Figure) -> bool:
    if hasattr(figure, "get_layout_engine"):
        engine = figure.get_layout_engine()
        return engine is not None and engine.__class__.__name__ == "TightLayoutEngine"
    return bool(figure.get_tight_layout())


def test_split_container_add_figure_uses_tight_layout_by_default():
    _app()
    container = SplitContainer()

    viewer = container.add_figure()

    assert _uses_tight_layout(viewer.figure)


def test_split_container_add_figure_can_disable_tight_layout():
    _app()
    container = SplitContainer()

    viewer = container.add_figure(Figure(), tight_layout=False)

    assert not _uses_tight_layout(viewer.figure)


def test_gui_add_figure_forwards_tight_layout_option():
    _app()
    original_window = gui._window
    gui._window = _DummyWindow()
    try:
        viewer = gui.add_figure(Figure(), title="Plot", tight_layout=False)
    finally:
        gui._window = original_window

    assert not _uses_tight_layout(viewer.figure)
