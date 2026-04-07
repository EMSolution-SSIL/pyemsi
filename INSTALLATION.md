# Installation

Install `pyemsi` from PyPI:

```bash
pip install pyemsi
```

## Notebook Support

For interactive visualization in Jupyter notebooks, install the optional notebook extras:

```bash
pip install pyemsi[jupyter]
```

## Install From Source

For development or the latest repository state:

```bash
git clone https://github.com/EMSolution-SSIL/pyemsi.git
cd pyemsi
pip install -e .
```

Building from source requires Cython >= 3.0.0 and NumPy >= 1.21.0. These are installed automatically during the build.

## Requirements

- Python 3.11
- VTK >= 9.0.0
- PyVista >= 0.43.0
- PySide6 >= 6.5.0
- NumPy >= 1.21.0

## Next Steps

- For developer-oriented build tasks, see [BUILDING.md](./BUILDING.md).
- For wheel and installer packaging, see [PACKAGING.md](./PACKAGING.md).
- For full documentation, visit https://emsolution-ssil.github.io/pyemsi.