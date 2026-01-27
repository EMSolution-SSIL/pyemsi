# pyemsi

Python tools for FEMAP Neutral file conversion and interactive 3D visualization with VTK.

## Overview

`pyemsi` provides powerful tools for working with FEMAP Neutral (.neu) files, enabling seamless conversion to VTK formats for advanced visualization in ParaView and interactive 3D exploration through Qt-based desktop applications.

### Key Features

- **FEMAP to VTK Conversion**: Convert FEMAP Neutral files to VTK MultiBlock UnstructuredGrid (.vtm) format
- **High-Performance Parsing**: Cython-accelerated parser for fast processing of large models
- **Interactive 3D Visualization**: Desktop Qt and Jupyter notebook visualization with PyVista
- **Comprehensive Data Support**: Handle displacement, magnetic, current, force, and heat data
- **Element Type Mapping**: Support for various element types (hex, tet, quad, tri, beam, etc.)

## Installation

### Standard Installation

```bash
pip install pyemsi
```

### With Jupyter Notebook Support

For interactive visualization in Jupyter notebooks:

```bash
pip install pyemsi[jupyter]
```

### From Source

For development or the latest features:

```bash
git clone https://github.com/EMSolution-SSIL/pyemsi.git
cd pyemsi
pip install -e .
```

**Note**: Building from source requires Cython>=3.0.0 and numpy>=1.21.0. These will be installed automatically during the build process.

## Quick Start

### Converting FEMAP Files

```python
from pyemsi import FemapConverter

# Convert FEMAP Neutral file to VTK MultiBlock format
converter = FemapConverter("model.neu")
multiblock = converter.to_vtm()

# Save for use in ParaView
multiblock.save("output.vtm")
```

### Interactive Visualization

```python
from pyemsi import Plotter

# Create Qt-based 3D plotter
plotter = Plotter()

# Add your VTK data
plotter.add_mesh(multiblock, scalars="displacement")

# Display interactive window
plotter.show()
```

## Development Notes

### Qt Resources

If you're developing pyemsi and need to modify Qt resources (icons, UI files), you'll need to manually compile them:

```bash
cd pyemsi/resources
pyside6-rcc resources.qrc -o resources.py
```

### Cython Extension

The `femap_parser` module is implemented in Cython for performance. When building from source, the extension will be compiled automatically. Pre-generated C files are included in source distributions for users without Cython.

## Documentation

For comprehensive API documentation and tutorials, visit:

https://emsolution-ssil.github.io/pyemsi

## Requirements

- Python >= 3.8
- VTK >= 9.0.0
- PyVista >= 0.43.0
- PySide6 >= 6.5.0
- NumPy >= 1.21.0

## License

MIT License - Copyright (c) 2026 SSIL

## Contact

For questions or support, contact: emsolution@ssil.co.jp
