"""
pyemsi - Python tools for EMSI file format conversions

Main functionality:
- FEMAP Neutral file parsing
- FEMAP to VTU conversion for ParaView visualization
"""

from .femap_parser import FEMAPParser, FEMAPBlock
from .femap_to_vtu import FEMAPToVTUConverter, convert_femap_to_vtu, FEMAP_TO_VTK

__version__ = "0.1.0"

__all__ = [
    "FEMAPParser",
    "FEMAPBlock",
    "FEMAPToVTUConverter",
    "convert_femap_to_vtu",
    "FEMAP_TO_VTK",
]
