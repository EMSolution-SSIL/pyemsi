"""
FEMAP to VTM Converter

This module converts FEMAP Neutral files to VTK MultiBlock UnstructuredGrid (.vtm) format.
Elements are organized by property ID into separate UnstructuredGrid blocks.
"""

from typing import Dict, List, Tuple, Optional
from vtk import (
    vtkPoints, vtkUnstructuredGrid,
    vtkIntArray,
    vtkMultiBlockDataSet,
    vtkXMLMultiBlockDataWriter,
    VTK_VERTEX, VTK_LINE, VTK_TRIANGLE, VTK_QUAD, VTK_TETRA,
    VTK_HEXAHEDRON, VTK_WEDGE,
    VTK_QUADRATIC_TRIANGLE, VTK_QUADRATIC_QUAD, VTK_QUADRATIC_TETRA,
    VTK_QUADRATIC_HEXAHEDRON, VTK_QUADRATIC_WEDGE
)

from .femap_parser import FEMAPParser


# FEMAP topology to VTK cell type mapping
# Format: femap_topology_id -> (vtk_cell_type, num_nodes)
FEMAP_TO_VTK = {
    9: (VTK_VERTEX, 1),                    # Point -> VTK_VERTEX
    0: (VTK_LINE, 2),                      # Line2 -> VTK_LINE
    2: (VTK_TRIANGLE, 3),                  # Tri3 -> VTK_TRIANGLE
    3: (VTK_QUADRATIC_TRIANGLE, 6),       # Tri6 -> VTK_QUADRATIC_TRIANGLE
    4: (VTK_QUAD, 4),                      # Quad4 -> VTK_QUAD
    5: (VTK_QUADRATIC_QUAD, 8),           # Quad8 -> VTK_QUADRATIC_QUAD
    6: (VTK_TETRA, 4),                     # Tetra4 -> VTK_TETRA
    10: (VTK_QUADRATIC_TETRA, 10),        # Tetra10 -> VTK_QUADRATIC_TETRA
    7: (VTK_WEDGE, 6),                     # Wedge6 -> VTK_WEDGE
    11: (VTK_QUADRATIC_WEDGE, 15),        # Wedge15 -> VTK_QUADRATIC_WEDGE
    8: (VTK_HEXAHEDRON, 8),                # Brick8 -> VTK_HEXAHEDRON
    12: (VTK_QUADRATIC_HEXAHEDRON, 20),   # Brick20 -> VTK_QUADRATIC_HEXAHEDRON
}


def validate_femap_data(
    nodes: Dict[int, Tuple[float, float, float]],
    elements: List[Dict],
    properties: Dict[int, Dict],
    header: Optional[Dict[str, str]] = None
) -> List[str]:
    """
    Validate parsed FEMAP data and return list of warnings/errors.

    Args:
        nodes: Dictionary mapping node IDs to (x, y, z) coordinates
        elements: List of element dictionaries
        properties: Dictionary mapping property IDs to property data
        header: Optional header information

    Returns:
        List of validation messages
    """
    messages = []

    if not nodes:
        messages.append("ERROR: No nodes found in FEMAP file")

    if not elements:
        messages.append("ERROR: No elements found in FEMAP file")

    # Check for unsupported element topologies
    for elem in elements:
        topo = elem['topology']
        if topo not in FEMAP_TO_VTK:
            messages.append(
                f"WARNING: Unsupported topology {topo} in element {elem['id']}"
            )

    # Check for missing nodes in elements
    for elem in elements:
        for node_id in elem['nodes']:
            if node_id not in nodes:
                messages.append(
                    f"ERROR: Element {elem['id']} references missing node {node_id}"
                )

    # Check version
    if header and header.get('version') != '4.41':
        messages.append(
            f"WARNING: Expected FEMAP version 4.41, got {header.get('version')}"
        )

    return messages


def read_mesh(mesh_filepath: str, validate: bool = True) -> vtkMultiBlockDataSet:
    """
    Convert FEMAP Neutral file to VTK MultiBlock UnstructuredGrid.

    Elements are organized by property ID into separate UnstructuredGrid blocks.
    Each block is a vtkUnstructuredGrid containing elements with the same property ID.
    All blocks share the same point set.

    Args:
        mesh_filepath: Path to FEMAP Neutral file
        validate: If True, run validation checks before conversion

    Returns:
        vtkMultiBlockDataSet containing one vtkUnstructuredGrid per property

    Raises:
        ValueError: If validation fails with errors
    """
    # Parse FEMAP mesh file
    print(f"Parsing FEMAP mesh file: {mesh_filepath}")
    parser = FEMAPParser(mesh_filepath)
    parser.parse()

    header = parser.get_header()
    nodes = parser.get_nodes()
    elements = parser.get_elements()
    properties = parser.get_properties()
    materials = parser.get_materials()

    print(f"Found {len(nodes)} nodes, {len(elements)} elements")
    print(f"Found {len(properties)} properties, {len(materials)} materials")

    # Validate if requested
    if validate:
        messages = validate_femap_data(nodes, elements, properties, header)
        if messages:
            print("\nValidation messages:")
            for msg in messages:
                print(f"  {msg}")

            # Check for errors
            errors = [m for m in messages if m.startswith("ERROR")]
            if errors:
                raise ValueError(f"Validation failed with {len(errors)} error(s)")

    # Build multiblock unstructured grid
    print("\nBuilding VTK MultiBlock UnstructuredGrid by Property ID...")

    # Group elements by property ID
    elements_by_prop = {}
    for elem in elements:
        prop_id = elem['prop_id']
        if prop_id not in elements_by_prop:
            elements_by_prop[prop_id] = []
        elements_by_prop[prop_id].append(elem)

    # Create VTK points and ID mapping (shared across all blocks)
    pts = vtkPoints()
    femap_to_vtk_id = {}

    for vtk_idx, femap_id in enumerate(sorted(nodes.keys())):
        x, y, z = nodes[femap_id]
        pts.InsertNextPoint(x, y, z)
        femap_to_vtk_id[femap_id] = vtk_idx

    # Create multiblock dataset
    mb = vtkMultiBlockDataSet()
    mb.SetNumberOfBlocks(len(elements_by_prop))

    # Create a block for each property
    block_idx = 0
    for prop_id in sorted(elements_by_prop.keys()):
        elements_in_prop = elements_by_prop[prop_id]

        # Create unstructured grid for this property
        ug = vtkUnstructuredGrid()
        ug.SetPoints(pts)
        ug.Allocate(len(elements_in_prop))

        # Arrays for cell data
        elem_ids = vtkIntArray()
        elem_ids.SetName("ElementID")
        elem_ids.SetNumberOfComponents(1)

        prop_ids = vtkIntArray()
        prop_ids.SetName("PropertyID")
        prop_ids.SetNumberOfComponents(1)

        mat_ids = vtkIntArray()
        mat_ids.SetName("MaterialID")
        mat_ids.SetNumberOfComponents(1)

        topo_ids = vtkIntArray()
        topo_ids.SetName("TopologyID")
        topo_ids.SetNumberOfComponents(1)

        # Insert cells for this property
        skipped = 0
        for elem in elements_in_prop:
            topo = elem['topology']

            if topo not in FEMAP_TO_VTK:
                skipped += 1
                continue

            vtk_type, num_nodes_required = FEMAP_TO_VTK[topo]
            elem_nodes = elem['nodes'][:num_nodes_required]

            if len(elem_nodes) < num_nodes_required:
                skipped += 1
                continue

            # Create ID list as Python list for the overload
            idlist = []
            valid = True
            for femap_node_id in elem_nodes:
                if femap_node_id in femap_to_vtk_id:
                    vtk_idx = femap_to_vtk_id[femap_node_id]
                    idlist.append(vtk_idx)
                else:
                    valid = False
                    skipped += 1
                    break

            if valid:
                # Insert cell using sequence overload
                ug.InsertNextCell(vtk_type, num_nodes_required, idlist)

                # Add cell data
                elem_ids.InsertNextValue(elem['id'])
                prop_ids.InsertNextValue(elem['prop_id'])
                topo_ids.InsertNextValue(elem['topology'])

                # Get material ID from property
                mat_id = 0
                if elem['prop_id'] in properties:
                    mat_id = properties[elem['prop_id']].get('material_id', 0)
                mat_ids.InsertNextValue(mat_id)

        # Add arrays to grid
        ug.GetCellData().AddArray(elem_ids)
        ug.GetCellData().AddArray(prop_ids)
        ug.GetCellData().AddArray(mat_ids)
        ug.GetCellData().AddArray(topo_ids)

        # Set block in multiblock dataset
        mb.SetBlock(block_idx, ug)

        # Set block name
        prop_name = f"Property_{prop_id}"
        if prop_id in properties:
            prop_title = properties[prop_id].get('title', '')
            if prop_title:
                prop_name = f"{prop_name}_{prop_title}"
        mb.GetMetaData(block_idx).Set(mb.NAME(), prop_name)

        print(f"Block {block_idx}: {prop_name} - {ug.GetNumberOfCells()} cells" +
              (f" ({skipped} skipped)" if skipped > 0 else ""))

        block_idx += 1

    print(f"Created MultiBlock UnstructuredGrid with {mb.GetNumberOfBlocks()} blocks")
    return mb


def save(
    multiblock: vtkMultiBlockDataSet,
    output_filepath: str,
    data_mode: str = "ascii"
):
    """
    Write VTK MultiBlock dataset to .vtm file.

    Args:
        multiblock: vtkMultiBlockDataSet to write
        output_filepath: Output .vtm file path
        data_mode: Data mode - "ascii" (human-readable) or "binary" (default: "ascii")
    """
    print(f"\nWriting VTM file: {output_filepath}")
    writer = vtkXMLMultiBlockDataWriter()
    writer.SetFileName(output_filepath)
    writer.SetInputData(multiblock)

    if data_mode.lower() == "ascii":
        writer.SetDataModeToAscii()
    elif data_mode.lower() == "binary":
        writer.SetDataModeToBinary()
    else:
        raise ValueError(f"Invalid data_mode: {data_mode}. Must be 'ascii' or 'binary'")

    writer.Write()
    print("Write complete!")
