"""
IPython terminal widget factory for embedding in PySide6 applications.

Creates an in-process IPython kernel connected to a RichJupyterWidget,
allowing live interaction with the running application.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from qtconsole.rich_jupyter_widget import RichJupyterWidget
    from qtconsole.inprocess import QtInProcessKernelManager


def create_ipython_terminal(
    namespace: dict[str, Any] | None = None,
) -> tuple[RichJupyterWidget, QtInProcessKernelManager]:
    """
    Create an in-process IPython kernel and a RichJupyterWidget connected to it.

    Parameters
    ----------
    namespace : dict, optional
        Initial namespace to inject into the kernel. Keys become variable names.

    Returns
    -------
    tuple[RichJupyterWidget, QtInProcessKernelManager]
        The terminal widget and the kernel manager (for later shutdown).
    """
    from qtconsole.rich_jupyter_widget import RichJupyterWidget
    from qtconsole.inprocess import QtInProcessKernelManager

    kernel_manager = QtInProcessKernelManager()
    kernel_manager.start_kernel()

    kernel = kernel_manager.kernel
    kernel.gui = "qt"

    if namespace:
        kernel.shell.push(namespace)

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()

    terminal = RichJupyterWidget()
    terminal.banner = "Welcome to the pyemsi IPython terminal!\n"
    terminal.kernel_manager = kernel_manager
    terminal.kernel_client = kernel_client

    kernel_client.execute("%matplotlib inline", silent=True)

    return terminal, kernel_manager
