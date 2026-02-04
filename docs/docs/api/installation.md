---
sidebar_position: 1
title: Installation
---

# `pyemsi` API Reference

## Installation

### Standard Installation

Install pyemsi from PyPI:

```bash
pip install pyemsi
```

### Jupyter Notebook Support

For interactive visualization in Jupyter notebooks, install with the jupyter extras:

```bash
pip install pyemsi[jupyter]
```

This enables notebook integration with PyVista.

### From Source

To install the latest development version:

```bash
git clone https://github.com/EMSolution-SSIL/pyemsi.git
cd pyemsi
pip install -e .
```

**Note**: Building from source requires Cython>=3.0.0 and numpy>=1.21.0, which will be installed automatically during the build process.

## Quick Start

```python
from pyemsi import examples, Plotter

file_path = examples.transient_path()

plt = Plotter(filepath=file_path)
plt.set_scalar("B-Mag (T)", "node")
plt.show()
```

