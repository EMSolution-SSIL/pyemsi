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


class FEMAPToVTMConverter:
    """
    Converts FEMAP Neutral files to VTK MultiBlock UnstructuredGrid format.
    Elements are organized by property ID into separate UnstructuredGrid blocks.
    """

    def __init__(self, femap_filepath: str):
        """
        Initialize converter with FEMAP file path.

        Args:
            femap_filepath: Path to FEMAP Neutral file
        """
        self.femap_filepath = femap_filepath
        self.parser = FEMAPParser(femap_filepath)
        self.nodes: Dict[int, Tuple[float, float, float]] = {}
        self.elements: List[Dict] = []
        self.properties: Dict[int, Dict] = {}
        self.materials: Dict[int, Dict] = {}
        self.header: Optional[Dict[str, str]] = None
        self._parsed: bool = False  # Track if parsing has been done

    def parse_femap(self):
        """Parse the FEMAP file and extract all data."""
        if self._parsed:
            return  # Already parsed, skip

        self.parser.parse()
        self.header = self.parser.get_header()
        self.nodes = self.parser.get_nodes()
        self.elements = self.parser.get_elements()
        self.properties = self.parser.get_properties()
        self.materials = self.parser.get_materials()
        self._parsed = True

    def validate(self) -> List[str]:
        """
        Validate parsed data and return list of warnings/errors.

        Returns:
            List of validation messages
        """
        messages = []

        if not self.nodes:
            messages.append("ERROR: No nodes found in FEMAP file")

        if not self.elements:
            messages.append("ERROR: No elements found in FEMAP file")

        # Check for unsupported element topologies
        for elem in self.elements:
            topo = elem['topology']
            if topo not in FEMAP_TO_VTK:
                messages.append(
                    f"WARNING: Unsupported topology {topo} in element {elem['id']}"
                )

        # Check for missing nodes in elements
        for elem in self.elements:
            for node_id in elem['nodes']:
                if node_id not in self.nodes:
                    messages.append(
                        f"ERROR: Element {elem['id']} references missing node {node_id}"
                    )

        # Check version
        if self.header and self.header.get('version') != '4.41':
            messages.append(
                f"WARNING: Expected FEMAP version 4.41, got {self.header.get('version')}"
            )

        return messages


    def build_multiblock_by_property(self) -> 'vtkMultiBlockDataSet':
        """
        Build VTK MultiBlock UnstructuredGrid with separate blocks for each property ID.

        Each block is a vtkUnstructuredGrid containing elements with the same property ID.
        All blocks share the same point set.

        Returns:
            vtkMultiBlockDataSet containing one vtkUnstructuredGrid per property
        """
        # Ensure data is parsed before building
        if not self._parsed:
            raise RuntimeError(
                "Data has not been parsed yet. Call parse_femap() before building multiblock."
            )

        # Group elements by property ID
        elements_by_prop = {}
        for elem in self.elements:
            prop_id = elem['prop_id']
            if prop_id not in elements_by_prop:
                elements_by_prop[prop_id] = []
            elements_by_prop[prop_id].append(elem)

        # Create VTK points and ID mapping (shared across all blocks)
        pts = vtkPoints()
        femap_to_vtk_id = {}

        for vtk_idx, femap_id in enumerate(sorted(self.nodes.keys())):
            x, y, z = self.nodes[femap_id]
            pts.InsertNextPoint(x, y, z)
            femap_to_vtk_id[femap_id] = vtk_idx

        # Create multiblock dataset
        mb = vtkMultiBlockDataSet()
        mb.SetNumberOfBlocks(len(elements_by_prop))

        # Create a block for each property
        block_idx = 0
        for prop_id in sorted(elements_by_prop.keys()):
            elements = elements_by_prop[prop_id]

            # Create unstructured grid for this property
            ug = vtkUnstructuredGrid()
            ug.SetPoints(pts)
            ug.Allocate(len(elements))

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
            for elem in elements:
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
                    if elem['prop_id'] in self.properties:
                        mat_id = self.properties[elem['prop_id']].get('material_id', 0)
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
            if prop_id in self.properties:
                prop_title = self.properties[prop_id].get('title', '')
                if prop_title:
                    prop_name = f"{prop_name}_{prop_title}"
            mb.GetMetaData(block_idx).Set(mb.NAME(), prop_name)

            print(f"Block {block_idx}: {prop_name} - {ug.GetNumberOfCells()} cells" +
                  (f" ({skipped} skipped)" if skipped > 0 else ""))

            block_idx += 1

        return mb

    def write_vtm(self, output_filepath: str, validate: bool = True):
        """
        Convert FEMAP file to VTK MultiBlock UnstructuredGrid and write to disk.
        Creates one UnstructuredGrid block per property ID.

        Args:
            output_filepath: Output .vtm file path
            validate: If True, run validation checks before conversion
        """
        # Parse FEMAP file
        print(f"Parsing FEMAP file: {self.femap_filepath}")
        self.parse_femap()

        print(f"Found {len(self.nodes)} nodes, {len(self.elements)} elements")
        print(f"Found {len(self.properties)} properties, {len(self.materials)} materials")

        # Validate if requested
        if validate:
            messages = self.validate()
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
        mb = self.build_multiblock_by_property()
        print(f"Created MultiBlock UnstructuredGrid with {mb.GetNumberOfBlocks()} blocks")

        # Write to file
        print(f"\nWriting VTM file: {output_filepath}")
        writer = vtkXMLMultiBlockDataWriter()
        writer.SetFileName(output_filepath)
        writer.SetInputData(mb)
        writer.SetDataModeToAscii()  # Make VTU files human-readable
        writer.Write()

        print("Conversion complete!")

        return mb
