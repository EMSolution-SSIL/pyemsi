from matplotlib.figure import Figure
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from pyemsi import gui
from pyemsi.gui._viewers._field_viewer import FieldViewer
from pyemsi.widgets.split_container import SplitContainer


class _DummyWindow:
    def __init__(self) -> None:
        self.container = SplitContainer()


class _FakePlotter:
    def __init__(self, notebook: bool = False) -> None:
        from PySide6.QtWidgets import QWidget

        class _FakeInnerPlotter:
            def __init__(inner_self) -> None:
                inner_self.reset_camera_calls = 0
                inner_self.show_axes_calls = 0

            def reset_camera(inner_self) -> None:
                inner_self.reset_camera_calls += 1

            def show_axes(inner_self) -> None:
                inner_self.show_axes_calls += 1

        class _FakeWindow:
            def __init__(window_self) -> None:
                window_self.create_display_toolbar_calls = 0

            def _create_display_toolbar(window_self) -> None:
                window_self.create_display_toolbar_calls += 1

        self.notebook = notebook
        self.widget = QWidget()
        self.plotter = _FakeInnerPlotter()
        self._window = _FakeWindow()
        self.close_calls = 0
        self.render_calls = 0

    def render(self) -> None:
        self.render_calls += 1

    def close(self) -> None:
        self.close_calls += 1


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


def test_split_container_add_field_embeds_plotter():
    app = _app()
    container = SplitContainer()
    plotter = _FakePlotter()

    viewer = container.add_field(plotter, title="Field Plot")

    assert isinstance(viewer, FieldViewer)
    assert viewer.plotter is plotter
    assert container.left_panel.tabText(container.left_panel.currentIndex()) == "Field Plot"

    container.left_panel._close_tab(container.left_panel.currentIndex())
    app.processEvents()
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()

    assert plotter.close_calls == 1


def test_gui_add_field_forwards_plotter():
    app = _app()
    original_window = gui._window
    gui._window = _DummyWindow()
    plotter = _FakePlotter()
    try:
        viewer = gui.add_field(plotter, title="Field")
    finally:
        gui._window = original_window

    assert isinstance(viewer, FieldViewer)
    assert viewer.plotter is plotter


def test_field_viewer_rejects_notebook_plotter():
    _app()

    try:
        FieldViewer(_FakePlotter(notebook=True))
    except ValueError as exc:
        assert "notebook=False" in str(exc)
    else:
        raise AssertionError("FieldViewer should reject notebook plotters.")
