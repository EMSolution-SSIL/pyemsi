"""
pyemsi - Python tools for EMSI file format conversions

Main functionality:
- FEMAP Neutral file parsing
- FEMAP to VTK MultiBlock UnstructuredGrid (.vtm) conversion for ParaView visualization
- Qt-based interactive 3D visualization with Plotter
"""

import logging
from pathlib import Path
from typing import Optional, Union

import pyvista as pv

from .FemapConverter import FemapConverter
from .plotter import Plotter

__version__ = "0.1.0"

__all__ = [
    "FemapConverter",
    "Plotter",
    "configure_logging",
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


def read(filepath: Union[str, Path]) -> pv.DataSet:
    """
    Read a mesh file and return a PyVista mesh object.

    This function uses PyVista's built-in reader to load various mesh formats
    including VTK, VTM, STL, OBJ, PLY, and many others.

    Args:
        filepath: Path to the mesh file to read.

    Returns:
        A PyVista DataSet object (could be UnstructuredGrid, PolyData,
        MultiBlock, or other PyVista mesh types depending on the file format).
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is not supported by PyVista.
    Example:
        >>> import pyemsi
        >>> mesh = pyemsi.read("path/to/mesh.vtk")
        >>> print(mesh)
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Mesh file not found: {filepath}")

    try:
        reader = pv.get_reader(str(filepath))
        mesh = reader.read()
        if isinstance(mesh, pv.MultiBlock):
            return mesh[0]
        return mesh
    except Exception as e:
        raise ValueError(f"Failed to read mesh file '{filepath}': {e}") from e
