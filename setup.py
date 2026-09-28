"""Minimal setup.py for Cython extension compilation.

All metadata is defined in pyproject.toml.
This file only handles Cython extension building.
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension(
        "pyemsi.core.femap_parser",
        ["pyemsi/core/femap_parser.pyx"],
        include_dirs=[np.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )
]

setup(
    ext_modules=cythonize(
        extensions,
        # Generate C into build/ instead of the source tree
        build_dir="build",
        language_level="3",
        compiler_directives={
            "boundscheck": False,
            "wraparound": False,
            "cdivision": True,
            "initializedcheck": False,
        },
    )
)
