# pyemsi

Python tools for EMSI file format conversions, specifically for converting FEMAP Neutral files to VTK format for visualization in ParaView.

## Features

- Parse FEMAP Neutral files (`.neu`) with support for:
  - Nodes (Block 403)
  - Elements (Block 404)
  - Properties (Block 402)
  - Materials (Block 601)
  - Header information (Block 100)
- Convert FEMAP meshes to VTK MultiBlock UnstructuredGrid (`.vtm`) format
- Organize elements by property ID into separate UnstructuredGrid blocks
- Support for mixed element types in a single mesh
- Handles repeated blocks and blocks in any order
- Comprehensive validation and error checking
- Preserves element metadata (IDs, properties, materials)

## Supported Element Types

| FEMAP Type | Element | VTK Type | Nodes |
|------------|---------|----------|-------|
| 9 | Point | VTK_VERTEX | 1 |
| 0 | Line2 | VTK_LINE | 2 |
| 2 | Tri3 | VTK_TRIANGLE | 3 |
| 3 | Tri6 | VTK_QUADRATIC_TRIANGLE | 6 |
| 4 | Quad4 | VTK_QUAD | 4 |
| 5 | Quad8 | VTK_QUADRATIC_QUAD | 8 |
| 6 | Tetra4 | VTK_TETRA | 4 |
| 10 | Tetra10 | VTK_QUADRATIC_TETRA | 10 |
| 7 | Wedge6 | VTK_WEDGE | 6 |
| 11 | Wedge15 | VTK_QUADRATIC_WEDGE | 15 |
| 8 | Brick8 | VTK_HEXAHEDRON | 8 |
| 12 | Brick20 | VTK_QUADRATIC_HEXAHEDRON | 20 |

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pyemsi.git
cd pyemsi

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

### Simple Conversion

```python
from pyemsi import convert_femap_to_vtm

# Convert FEMAP file to VTK MultiBlock UnstructuredGrid in one line
convert_femap_to_vtm("input.neu", "output.vtm")
```

### Advanced Usage

```python
from pyemsi import FemapConverter

# Create converter
converter = FemapConverter("input.neu")

# Parse FEMAP file
converter.parse_femap()

# Inspect parsed data
print(f"Nodes: {len(converter.nodes)}")
print(f"Elements: {len(converter.elements)}")
print(f"Properties: {len(converter.properties)}")

# Validate data
messages = converter.validate()
for msg in messages:
    print(msg)

# Convert to VTK MultiBlock UnstructuredGrid (one block per property)
multiblock = converter.write_vtm("output.vtm")
```

### Using the Example Script

```bash
# Simple conversion
python examples/convert_femap.py input.neu output.vtm

# Detailed conversion with intermediate information
python examples/convert_femap.py input.neu output.vtm --detailed
```

## Parsing Only (No VTK Required)

You can parse FEMAP files without VTK installed:

```python
from pyemsi import FEMAPParser

# Parse FEMAP file
parser = FEMAPParser("input.neu")
parser.parse()

# Extract data
nodes = parser.get_nodes()
elements = parser.get_elements()
properties = parser.get_properties()
materials = parser.get_materials()
header = parser.get_header()

# Work with parsed data
for node_id, (x, y, z) in nodes.items():
    print(f"Node {node_id}: ({x}, {y}, {z})")
```

## MultiBlock UnstructuredGrid Organization

The converted VTM file is a MultiBlock dataset containing separate UnstructuredGrid blocks for each property ID, making it easy to work with different parts of your model. Each block includes the following cell data arrays for filtering and visualization:

- **ElementID**: Original FEMAP element ID
- **PropertyID**: Property assignment for each element
- **MaterialID**: Material assignment (via property lookup)
- **TopologyID**: FEMAP topology code for debugging

Blocks are named as `Property_{ID}_{Title}` (e.g., `Property_1_Shell_Part`, `Property_2_Solid_Part`)

## Visualization in ParaView

1. Open ParaView
2. File > Open > select your `.vtm` file
3. Click "Apply" in the Properties panel
4. You'll see separate blocks for each property in the Pipeline Browser
5. Toggle visibility of individual blocks, or select blocks to work with specific parts
6. In the top toolbar, change coloring from "Solid Color" to "PropertyID" or "MaterialID"
7. Use filters like "Threshold" or "Extract Block" to work with specific parts

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=pyemsi --cov-report=html

# Run specific test file
python -m pytest tests/test_femap_parser.py -v
```

## Project Structure

```
pyemsi/
├── pyemsi/
│   ├── __init__.py           # Package initialization
│   ├── femap_parser.py       # FEMAP Neutral file parser
│   └── femap_to_vtm.py       # VTK converter
├── tests/
│   ├── __init__.py
│   ├── test_femap_parser.py  # Parser tests
│   ├── test_femap_to_vtm.py  # Converter tests
│   └── fixtures/             # Test data files
│       ├── simple_mesh.neu
│       ├── post_geom_single_hex.neu
│       └── mixed_elements.neu
├── dev_docs/                 # Development documentation
│   ├── femap_to_vtm_plan.md
│   ├── femap.md
│   └── vtk.md
├── requirements.txt
├── setup.py
└── README.md
```

## API Reference

### FEMAPParser

Parse FEMAP Neutral files and extract structured data.

```python
parser = FEMAPParser(filepath)
blocks = parser.parse()  # Returns dict of block_id -> [FEMAPBlock]

# Extract specific data
header = parser.get_header()           # Returns dict with title, version
nodes = parser.get_nodes()              # Returns {node_id: (x, y, z)}
elements = parser.get_elements()        # Returns list of element dicts
properties = parser.get_properties()    # Returns {prop_id: {...}}
materials = parser.get_materials()      # Returns {mat_id: {...}}
```

### FemapConverter

Convert FEMAP files to VTK MultiBlock UnstructuredGrid format.

```python
converter = FemapConverter(femap_filepath)
converter.parse_femap()                      # Parse the file
messages = converter.validate()              # Validate parsed data
mb = converter.build_mesh()  # Build MultiBlock UnstructuredGrid
converter.write_vtm(output_filepath)         # Write to disk
```

## Requirements

- Python >= 3.7
- VTK >= 9.0.0 (only required for VTU conversion, not for parsing)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Known Limitations

- Node ordering is assumed to match VTK canonical ordering (verify for your specific FEMAP export)
- Some specialized FEMAP element types may not be supported
- Result data (Block 450, 1051) is not yet implemented

## Development Documentation

See [dev_docs/](dev_docs/) for detailed implementation plans and format specifications:
- [femap_to_vtu_plan.md](dev_docs/femap_to_vtu_plan.md) - Implementation plan
- [vtk.md](dev_docs/vtk.md) - VTK Unstructured Grid reference

## Contact

For questions, issues, or contributions, please open an issue on GitHub.