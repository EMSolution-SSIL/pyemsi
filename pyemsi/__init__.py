"""
pyemsi - Python tools for EMSI file format conversions

Main functionality:
- FEMAP Neutral file parsing
- FEMAP to VTK MultiBlock UnstructuredGrid (.vtm) conversion for ParaView visualization
- Qt-based interactive 3D visualization with Plotter
"""

import logging
from typing import Optional

from .FemapConverter import FemapConverter
from .plotter import Plotter
from . import examples

__version__ = "0.1.2"

__all__ = [
    "FemapConverter",
    "Plotter",
    "configure_logging",
    "examples",
]

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
