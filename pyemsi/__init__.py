"""
pyemsi - Python tools for EMSI file format conversions

Main functionality:
- FEMAP Neutral file parsing
- FEMAP to VTK MultiBlock UnstructuredGrid (.vtm) conversion for ParaView visualization
"""

from .FemapConverter import FemapConverter

__version__ = "0.1.0"

__all__ = [
    "FemapConverter",
]
