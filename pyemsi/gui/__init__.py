"""
pyemsi.gui -- Interactive GUI with embedded IPython terminal.

Usage
-----
    from pyemsi import gui
    gui.launch()

After launch, the module proxies attribute access to the PyEmsiMainWindow
instance, so ``gui`` itself acts like the window::

    >>> gui.container.add_tab(QLabel("Hello"), "My Tab")
    >>> gui.ipython_terminal   # the IPython RichJupyterWidget
    >>> gui.push_to_namespace(x=42)

Convenience helpers are also available directly on the module::

    >>> gui.open_file("/path/to/file.txt")
    >>> gui.add_figure(fig, title="My Plot")
    >>> gui.add_field(plotter, title="Field")

From the IPython terminal, pre-injected locals are also available::

    >>> container.add_tab(QLabel("Hello"), "My Tab")
    >>> open_file("/path/to/file.txt")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyemsi.gui.main_window import PyEmsiMainWindow

_window: PyEmsiMainWindow | None = None
_app = None


def launch(
    title: str = "pyemsi",
    size: tuple[int, int] | None = None,
    workspace_path: str | None = None,
) -> None:
    """
    Create and show the pyemsi main window, then start the Qt event loop.

    This function is blocking -- it returns only after the window is closed.

    Parameters
    ----------
    title : str
        Window title.
    size : tuple of int
        Window size as (width, height).
    workspace_path : str, optional
        Folder to open as the initial workspace.
    """
    global _window, _app

    from PySide6.QtWidgets import QApplication

    from pyemsi.gui.main_window import PyEmsiMainWindow

    _app = QApplication.instance()
    if _app is None:
        _app = QApplication([])

    _window = PyEmsiMainWindow()
    _window.setWindowTitle(title)

    if workspace_path is not None:
        import os

        _window._set_workspace_path(os.path.abspath(workspace_path))

    import pyemsi.gui as gui_module

    _window.push_to_namespace(
        gui=gui_module,
        window=_window,
        container=_window.container,
        open_file=open_file,
        add_figure=add_figure,
        add_field=add_field,
    )

    if size is None:
        if _window.should_show_maximized_on_launch():
            _window.showMaximized()
        else:
            _window.show()
    else:
        _window.resize(*size)
        _window.show()
    _app.exec()


def __getattr__(name: str):
    """Proxy attribute access to the PyEmsiMainWindow instance."""
    if _window is not None and hasattr(_window, name):
        return getattr(_window, name)
    raise AttributeError(f"module 'pyemsi.gui' has no attribute {name!r}")


def open_file(path: str, category: str | None = None):
    """Open *path* in a viewer tab (or focus the existing tab).

    Parameters
    ----------
    path : str
        Absolute path to the file.
    category : str, optional
        Force a viewer category (``"text"``, ``"image"``, ``"audio"``).
        When *None* the category is inferred from the file extension.

    Returns
    -------
    QWidget
        The viewer widget (new or existing).
    """
    if _window is None:
        raise RuntimeError("pyemsi.gui has not been launched yet; call gui.launch() first.")
    return _window.container.open_file(path, category)


def add_figure(figure=None, title: str = "Figure", tight_layout: bool = True):
    """Embed a matplotlib Figure as a new tab.

    Parameters
    ----------
    figure : matplotlib.figure.Figure, optional
        Figure to display.  A blank Figure is created when *None*.
    title : str
        Tab label.  Defaults to ``"Figure"``.
    tight_layout : bool, optional
        Whether to enable matplotlib tight layout on the viewer's figure.
        Defaults to ``True``.

    Returns
    -------
    MatplotlibViewer
        The viewer widget; use ``viewer.figure`` / ``viewer.draw()`` to
        update the plot after creation.
    """
    if _window is None:
        raise RuntimeError("pyemsi.gui has not been launched yet; call gui.launch() first.")
    return _window.container.add_figure(figure, title, tight_layout=tight_layout)


def add_field(plotter, title: str = "Field"):
    """Embed an existing Plotter as a new tab.

    Parameters
    ----------
    plotter : pyemsi.Plotter
        Existing desktop plotter to embed.
    title : str
        Tab label. Defaults to ``"Field"``.

    Returns
    -------
    FieldViewer
        The viewer widget hosting the supplied plotter.
    """
    if _window is None:
        raise RuntimeError("pyemsi.gui has not been launched yet; call gui.launch() first.")
    return _window.container.add_field(plotter, title)
