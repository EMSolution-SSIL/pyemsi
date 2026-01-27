---
sidebar_position: 1
title: Introduction
---

# `pyemsi` API Reference

## Installation

### Standard Installation

Install pyemsi from PyPI for basic usage:

```bash
pip install pyemsi
```

### Jupyter Notebook Support

For interactive visualization in Jupyter notebooks, install with the jupyter extras:

```bash
pip install pyemsi[jupyter]
```

This includes additional dependencies for notebook integration with PyVista.

### Development Installation

For development work, including testing tools:

```bash
pip install pyemsi[dev]
```

This includes pytest and pytest-cov for running tests, as well as Cython for building extensions.

### From Source

To install the latest development version:

```bash
git clone https://github.com/EMSolution-SSIL/pyemsi.git
cd pyemsi
pip install -e .
```

**Note**: Building from source requires Cython>=3.0.0 and numpy>=1.21.0, which will be installed automatically during the build process.

