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

From the IPython terminal, pre-injected locals are also available::

    >>> container.add_tab(QLabel("Hello"), "My Tab")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyemsi.gui.main_window import PyEmsiMainWindow

_window: PyEmsiMainWindow | None = None
_app = None


def launch(
    title: str = "pyemsi",
    size: tuple[int, int] = (1400, 900),
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
    """
    global _window, _app

    from PySide6.QtWidgets import QApplication

    from pyemsi.gui.main_window import PyEmsiMainWindow

    _app = QApplication.instance()
    if _app is None:
        _app = QApplication([])

    _window = PyEmsiMainWindow()
    _window.setWindowTitle(title)
    _window.resize(*size)

    import pyemsi.gui as gui_module

    _window.push_to_namespace(gui=gui_module, window=_window, container=_window.container)

    _window.show()
    _app.exec()


def __getattr__(name: str):
    """Proxy attribute access to the PyEmsiMainWindow instance."""
    if _window is not None and hasattr(_window, name):
        return getattr(_window, name)
    raise AttributeError(f"module 'pyemsi.gui' has no attribute {name!r}")
