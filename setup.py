"""Setup script for pyemsi package."""

from setuptools import setup, find_packages, Extension
import numpy as np
import os

try:
    from Cython.Build import cythonize

    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

# Read version from __init__.py
version = {}
with open(os.path.join("pyemsi", "__init__.py"), "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

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

setup(
    name="pyemsi",
    version=version["__version__"],
    author="SSIL",
    author_email="emsolution@ssil.co.jp",
    description="Python tools for FEMAP Neutral file conversion and VTK visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EMSolution-SSIL/pyemsi",
    packages=find_packages(),
    ext_modules=ext_modules,
    license="GPL-3.0-or-later",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    setup_requires=[
        "Cython>=3.0.0",
        "numpy>=1.21.0",
    ],
    install_requires=[
        "vtk>=9.0.0",
        "numpy>=1.21.0",
        "pyvista>=0.43.0",
        "pyvistaqt>=0.11.0",
        "PySide6>=6.5.0",
    ],
    extras_require={
        "jupyter": [
            "pyvista[jupyter]>=0.43.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "Cython>=3.0.0",
        ],
    },
    zip_safe=False,
)
