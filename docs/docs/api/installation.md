---
sidebar_position: 1
title: Installation
---

# `pyemsi` API Reference

## Installation

### Standard Installation

Download the latest wheel file from the [GitHub Releases page](https://github.com/EMSolution-SSIL/pyemsi/releases/latest) and install it using pip:

```bash
pip install pyemsi-<version>-<platform>.whl
```

Replace `<version>` and `<platform>` with the appropriate values for your downloaded file (e.g., `pyemsi-0.1.0-cp311-cp311-win_amd64.whl`).

### Jupyter Notebook Support

For interactive visualization in Jupyter notebooks, install the additional dependencies after installing the wheel:

```bash
pip install pyvistaqt ipywidgets
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

