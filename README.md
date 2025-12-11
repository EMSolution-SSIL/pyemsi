# pyemsi

Python tooling for converting EMSolution FEMAP Neutral exports into VTK data sets that can be inspected in ParaView, PyVista, or downstream post-processing scripts. The project is built around two core pieces:

- A Cython implementation of the FEMAP Neutral parser (`pyemsi.femap_parser`) that reads blocks 100/402/403/404/450/601/1051 and exposes both Python and NumPy-array friendly accessors.
- A PyVista/Vtk powered `pyemsi.FemapConverter` class that creates MultiBlock `.vtm` files grouped by property ID, tracks FEMAP→VTK ID relationships, and decorates the mesh with nodal/elemental result vectors (displacement, magnetic flux, currents, nodal forces, Lorentz forces, and heat).

## Key capabilities

- 12 FEMAP topologies (points through Brick20) are mapped to their VTK counterparts and can be mixed inside a single mesh.
- Property IDs become block boundaries, preserving IDs, properties, materials, and topology metadata as cell data arrays.
- Optional `force_2d` mode flattens 3D solid elements into their 2D equivalents for planar studies.
- Output set post-processing injects nodal or elemental vectors back into the mesh, with helper routines (`parse_data_files`, `get_data_array`, `time_stepping`) to produce one `.vtm` per time step and an accompanying `.pvd` file.
- The parser exposes both dictionary-based helpers (`get_nodes`, `get_elements`, …) and zero-copy NumPy views (`get_nodes_arrays`, `get_elements_arrays`, `get_output_vectors_arrays`) for high-throughput workflows.

## Repository layout

```
pyemsi/
├── pyemsi/
│   ├── __init__.py              # Package exports (FemapConverter)
│   ├── FemapConverter.py        # PyVista/Vtk conversion pipeline
│   ├── femap_parser.pyx         # Cython parser implementation
│   ├── femap_parser.pxd         # Shared declarations
│   ├── femap_parser.c           # Generated C source (checked in for convenience)
│   ├── femap_parser.cp313-*.pyd # Prebuilt wheel for Windows dev
│   └── femap_parser_bak.py      # Pure-Python reference parser
├── tests/
│   ├── fixtures/                # Sample FEMAP Neutral files
│   ├── test_femap_parser.py
│   └── test_femap_to_vtm.py     # Legacy tests kept for reference
├── dev_docs/                    # Format notes and planning docs
├── requirements.txt
├── setup.py
└── README.md
```

## Requirements and installation

- Python 3.8+
- NumPy ≥ 1.21, PyVista, VTK ≥ 9.0
- A C/C++ compiler capable of building Cython extensions

```bash
git clone https://github.com/yourusername/pyemsi.git
cd pyemsi
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .[dev]
```

## Building `femap_parser.pyx`

The `pyemsi.femap_parser` module is implemented in Cython for speed. Rebuild it any time you change `femap_parser.pyx/.pxd`, or when you set up a fresh clone:

```bash
python setup.py build_ext --inplace
```

The command generates `pyemsi/femap_parser.*.pyd` (Windows) or `.so` (Linux/macOS) alongside the sources so that `from pyemsi.femap_parser import FEMAPParser` works without packaging an external wheel. The build uses the NumPy headers declared in `setup.py`; make sure your compiler toolchain is discoverable (MSVC on Windows, clang/gcc elsewhere). Because `setup.py` cythonizes the extension only when Cython is present, keeping `Cython>=3.0` installed is recommended even if you rely on the checked-in C file.

## Preparing a FEMAP case

FemapConverter expects a directory that contains a neutral mesh plus optional result files. A typical export looks like:

```
project/
├── post_geom            # Neutral mesh (Block 403/404/etc.)
├── disp                 # Displacements (Block 1051)
├── magnetic             # Magnetic flux density vectors
├── current              # Current density and Joule loss
├── force                # Mechanical nodal forces
├── force_J_B            # Lorentz forces
└── heat                 # Heat generation
```

File names are configurable via the FemapConverter constructor. If a file is missing or `None`, that data channel is skipped.

## Using `FemapConverter`

```python
from pyemsi import FemapConverter

converter = FemapConverter(
    input_dir="project",
    output_dir=".pyemsi",
    output_name="transient_run",
    mesh="post_geom",        # mesh file or absolute path
    force_2d=False,          # flatten Bricks/Wedges into Quads/Tris when True
    displacement="disp",
    magnetic="magnetic",
    current="current",
    force="force",
    force_J_B="force_J_B",
    heat="heat",
)

# Build a clean mesh grouped by PropertyID; initial_mesh.vtm is written automatically
converter.parse_data_files()   # read optional result files
converter.init_pvd()           # create <output_name>.pvd referencing each time step
converter.time_stepping()      # writes one VTM per set title inside <output_dir>/<output_name>/
```

Key behaviors:

- Nodes are deduplicated by FEMAP ID and stored with a FEMAP→VTK lookup so nodal vectors can be mapped back on demand.
- Elements unsupported by `FEMAP_TO_VTK` are skipped with their IDs logged in-memory so that result arrays only target valid cells.
- `get_data_array(step, vectors)` sanitizes vector titles (illegal filename characters are removed) and supports both nodal (`ent_type == 7`) and elemental (`ent_type == 8`) payloads.
- During `time_stepping` the converter applies displacements (updating mesh points), writes point/cell data arrays such as `B-Vec (T)`, `J-Vec (A/m^2)`, `F Lorents-Vec (N/m^3)` or `Heat Density (W/m^3)`, and exports each sanitized time-step title as `output/<title>.vtm`.
- Use PyVista/ParaView to open `.pyemsi/transient_run/initial_mesh.vtm` for static geometry or `transient_run.pvd` for the full time-series.

### Logging

pyemsi uses Python's standard `logging` module. By default, the library is silent (uses `NullHandler`). Enable logging with the `configure_logging` helper:

```python
import logging
import pyemsi

# Enable INFO level to console
pyemsi.configure_logging(logging.INFO)

# Enable DEBUG level for detailed output (mesh stats, vector counts, file writes)
pyemsi.configure_logging(logging.DEBUG)

# Custom file handler
file_handler = logging.FileHandler("pyemsi.log")
pyemsi.configure_logging(logging.DEBUG, handler=file_handler)

# Custom format string
pyemsi.configure_logging(
    logging.INFO,
    format_string="%(asctime)s - %(message)s"
)
```

The default format includes timestamps and thread names for debugging parallel processing:
```
%(asctime)s [%(levelname)s] %(name)s (%(threadName)s): %(message)s
```

### Visualizing with PyVista

```python
import pyvista as pv

m = pv.read(".pyemsi/transient_run/initial_mesh.vtm")
p = pv.Plotter()
for name, block in m.blocks.items():
    p.add_mesh(block, show_edges=True, opacity=0.4, label=f"Property {name}")
p.add_legend()
p.show()
```

## Working directly with `FEMAPParser`

```python
from pyemsi.femap_parser import FEMAPParser

parser = FEMAPParser("tests/fixtures/simple_mesh.neu")
header = parser.get_header()
nodes = parser.get_nodes()
elements = parser.get_elements()
properties = parser.get_properties()
materials = parser.get_materials()
output_sets = parser.get_output_sets()
output_vectors = parser.get_output_vectors()

node_ids, coords = parser.get_nodes_arrays()
elem_ids, prop_ids, topos, connectivity, offsets = parser.get_elements_arrays()
ids, values, set_id, vec_id, ent_type = parser.get_output_vectors_arrays(set_id_filter=1)
```

These helpers make it easy to plug FEMAP data into other pipelines, perform validation prior to visualization, or prototype new analysis routines without touching VTK.

## Supported topology mapping

| FEMAP topology | Element             | VTK constant                | Nodes |
|----------------|---------------------|-----------------------------|-------|
| 9              | Point               | `VTK_VERTEX`                | 1     |
| 0              | Line2               | `VTK_LINE`                  | 2     |
| 2              | Tri3                | `VTK_TRIANGLE`              | 3     |
| 3              | Tri6                | `VTK_QUADRATIC_TRIANGLE`    | 6     |
| 4              | Quad4               | `VTK_QUAD`                  | 4     |
| 5              | Quad8               | `VTK_QUADRATIC_QUAD`        | 8     |
| 6              | Tetra4              | `VTK_TETRA`                 | 4     |
| 10             | Tetra10             | `VTK_QUADRATIC_TETRA`       | 10    |
| 7              | Wedge6              | `VTK_WEDGE`                 | 6     |
| 11             | Wedge15             | `VTK_QUADRATIC_WEDGE`       | 15    |
| 8              | Brick8              | `VTK_HEXAHEDRON`            | 8     |
| 12             | Brick20             | `VTK_QUADRATIC_HEXAHEDRON`  | 20    |

Elements with fewer nodes than required are skipped to avoid corrupt cells; check `FemapConverter.elements_map` if you need to trace which FEMAP IDs were retained.

## Testing

```bash
python -m pytest
```

The parser tests use the fixtures under `tests/fixtures/` to ensure that repeated blocks, mixed topologies, and CSV parsing edge cases behave consistently. Converter tests currently target the legacy API but still validate the FEMAP→VTK mappings and VTK output structure.

## Contributing & license

MIT License. Issues and pull requests are welcome—particularly around expanded output vector coverage, CLI tooling, or platform-specific build scripts. When modifying the parser, remember to rerun `python setup.py build_ext --inplace` so the compiled extension matches the `.pyx` source.
