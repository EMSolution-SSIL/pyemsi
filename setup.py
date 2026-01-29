"""Minimal setup.py for Cython extension compilation.

All metadata is defined in pyproject.toml.
This file only handles Cython extension building.
"""

from setuptools import setup, Extension
import numpy as np

try:
    from Cython.Build import cythonize

    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

# Define Cython extensions
ext_modules = []
if USE_CYTHON:
    extensions = [
        Extension(
            "pyemsi.femap_parser",
            ["pyemsi/femap_parser.pyx"],
            include_dirs=[np.get_include()],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        )
    ]
    ext_modules = cythonize(
        extensions,
        language_level="3",
        compiler_directives={
            "boundscheck": False,
            "wraparound": False,
            "cdivision": True,
            "initializedcheck": False,
        },
    )
else:
    # Fallback to pre-generated C file when Cython is not available
    ext_modules = [
        Extension(
            "pyemsi.femap_parser",
            ["pyemsi/femap_parser.c"],
            include_dirs=[np.get_include()],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        )
    ]

setup(ext_modules=ext_modules)
