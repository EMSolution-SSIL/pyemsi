"""
pyemsi - Python tools for EMSI file format conversions

Main functionality:
- FEMAP Neutral file parsing
- FEMAP to VTK MultiBlock UnstructuredGrid (.vtm) conversion for ParaView visualization
"""

from .femap_to_vtm import (
    read_mesh,
    save,
    validate_femap_data,
)

__version__ = "0.2.0"

__all__ = [
    "read_mesh",
    "save",
    "validate_femap_data",
]
