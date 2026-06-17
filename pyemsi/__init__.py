"""
pyemsi - Python tools for EMSI file format conversions

Main functionality:
- FEMAP Neutral file parsing
- FEMAP to VTK MultiBlock UnstructuredGrid (.vtm) conversion for ParaView visualization
- Qt-based interactive 3D visualization with Plotter
"""

from importlib import import_module
import logging
from typing import TYPE_CHECKING, Any, Optional

from . import examples

if TYPE_CHECKING:
    from .io import EMSolutionOutput
    from .plotter import Plotter
    from .tools.FemapConverter import FemapConverter

__version__ = "0.4.0"

_LAZY_EXPORTS = {
    "EMSolutionOutput": ("pyemsi.io", "EMSolutionOutput"),
    "Plotter": ("pyemsi.plotter", "Plotter"),
    "FemapConverter": ("pyemsi.tools.FemapConverter", "FemapConverter"),
}

__all__ = [
    "FemapConverter",
    "Plotter",
    "configure_logging",
    "examples",
    "gui",
    "is_gui_running",
    "EMSolutionOutput",
]


def __getattr__(name: str) -> Any:
    """Resolve selected heavy exports on first access."""
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module 'pyemsi' has no attribute {name!r}")

    module_name, attr_name = target
    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Expose lazy exports to interactive tooling."""
    return sorted(set(globals()) | set(__all__))


def is_gui_running() -> bool:
    """Return True if a QApplication instance is currently active."""
    try:
        from PySide6.QtWidgets import QApplication

        return QApplication.instance() is not None
    except ImportError:
        return False


# Package-level logger setup (library best practice: NullHandler by default)
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def configure_logging(
    level: int = logging.INFO,
    handler: Optional[logging.Handler] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging for the pyemsi package.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO).
        handler: Custom handler. If None, a StreamHandler to stderr is used.
        format_string: Custom format string. If None, a default format is used.

    Returns:
        The configured pyemsi logger.

    Example:
        >>> import logging
        >>> import pyemsi
        >>> pyemsi.configure_logging(logging.DEBUG)
    """
    pkg_logger = logging.getLogger("pyemsi")
    pkg_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates on reconfiguration
    for h in pkg_logger.handlers[:]:
        pkg_logger.removeHandler(h)

    if handler is None:
        handler = logging.StreamHandler()

    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s (%(threadName)s): %(message)s"

    handler.setFormatter(logging.Formatter(format_string))
    handler.setLevel(level)
    pkg_logger.addHandler(handler)

    return pkg_logger
