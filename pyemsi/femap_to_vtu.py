"""
FEMAP to VTU Converter

This module converts FEMAP Neutral files to VTK Unstructured Grid (.vtu) format.
"""

from typing import Dict, List, Tuple, Optional
try:
    from vtk import (
        vtkPoints, vtkUnstructuredGrid, vtkIdList,
        vtkFloatArray, vtkIntArray,
        vtkXMLUnstructuredGridWriter
    )
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False

from .femap_parser import FEMAPParser


# FEMAP topology to VTK cell type mapping
# Format: femap_topology_id -> (vtk_cell_type, num_nodes)
FEMAP_TO_VTK = {
    9: (1, 1),      # Point -> VTK_VERTEX
    0: (3, 2),      # Line2 -> VTK_LINE
    2: (5, 3),      # Tri3 -> VTK_TRIANGLE
    3: (22, 6),     # Tri6 -> VTK_QUADRATIC_TRIANGLE
    4: (9, 4),      # Quad4 -> VTK_QUAD
    5: (23, 8),     # Quad8 -> VTK_QUADRATIC_QUAD
    6: (10, 4),     # Tetra4 -> VTK_TETRA
    10: (24, 10),   # Tetra10 -> VTK_QUADRATIC_TETRA
    7: (13, 6),     # Wedge6 -> VTK_WEDGE
    11: (26, 15),   # Wedge15 -> VTK_QUADRATIC_WEDGE
    8: (12, 8),     # Brick8 -> VTK_HEXAHEDRON
    12: (25, 20),   # Brick20 -> VTK_QUADRATIC_HEXAHEDRON
}


class FEMAPToVTUConverter:
    """
    Converts FEMAP Neutral files to VTK Unstructured Grid format.
    """

    def __init__(self, femap_filepath: str):
        """
        Initialize converter with FEMAP file path.

        Args:
            femap_filepath: Path to FEMAP Neutral file
        """
        if not VTK_AVAILABLE:
            raise ImportError(
                "VTK is not available. Install it with: pip install vtk"
            )

        self.femap_filepath = femap_filepath
        self.parser = FEMAPParser(femap_filepath)
        self.nodes: Dict[int, Tuple[float, float, float]] = {}
        self.elements: List[Dict] = []
        self.properties: Dict[int, Dict] = {}
        self.materials: Dict[int, Dict] = {}
        self.header: Optional[Dict[str, str]] = None

    def parse_femap(self):
        """Parse the FEMAP file and extract all data."""
        self.parser.parse()
        self.header = self.parser.get_header()
        self.nodes = self.parser.get_nodes()
        self.elements = self.parser.get_elements()
        self.properties = self.parser.get_properties()
        self.materials = self.parser.get_materials()

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

    def build_unstructured_grid(self) -> 'vtkUnstructuredGrid':
        """
        Build VTK Unstructured Grid from parsed FEMAP data.

        Returns:
            vtkUnstructuredGrid object
        """
        # Create VTK points and ID mapping
        pts = vtkPoints()
        femap_to_vtk_id = {}

        # Sort node IDs for consistent ordering
        for vtk_idx, femap_id in enumerate(sorted(self.nodes.keys())):
            x, y, z = self.nodes[femap_id]
            pts.InsertNextPoint(x, y, z)
            femap_to_vtk_id[femap_id] = vtk_idx

        # Initialize unstructured grid
        ug = vtkUnstructuredGrid()
        ug.SetPoints(pts)
        ug.Allocate(len(self.elements))

        # Insert cells
        skipped_elements = []
        for elem in self.elements:
            topo = elem['topology']

            if topo not in FEMAP_TO_VTK:
                skipped_elements.append(elem['id'])
                continue

            vtk_type, num_nodes_required = FEMAP_TO_VTK[topo]

            # Extract required nodes and convert to VTK IDs
            elem_nodes = elem['nodes'][:num_nodes_required]

            # Skip if not enough nodes
            if len(elem_nodes) < num_nodes_required:
                skipped_elements.append(elem['id'])
                continue

            # Create ID list
            idlist = vtkIdList()
            for femap_node_id in elem_nodes:
                if femap_node_id in femap_to_vtk_id:
                    vtk_idx = femap_to_vtk_id[femap_node_id]
                    idlist.InsertNextId(vtk_idx)
                else:
                    # Node missing, skip this element
                    skipped_elements.append(elem['id'])
                    break
            else:
                # All nodes found, insert cell
                ug.InsertNextCell(vtk_type, idlist)

        if skipped_elements:
            print(f"WARNING: Skipped {len(skipped_elements)} elements: {skipped_elements[:10]}...")

        return ug

    def add_cell_data(self, ug: 'vtkUnstructuredGrid'):
        """
        Add element metadata as cell data arrays.

        Args:
            ug: VTK Unstructured Grid to add data to
        """
        num_cells = ug.GetNumberOfCells()

        # Element IDs
        elem_ids = vtkIntArray()
        elem_ids.SetName("ElementID")
        elem_ids.SetNumberOfComponents(1)
        elem_ids.SetNumberOfTuples(num_cells)

        # Property IDs
        prop_ids = vtkIntArray()
        prop_ids.SetName("PropertyID")
        prop_ids.SetNumberOfComponents(1)
        prop_ids.SetNumberOfTuples(num_cells)

        # Material IDs
        mat_ids = vtkIntArray()
        mat_ids.SetName("MaterialID")
        mat_ids.SetNumberOfComponents(1)
        mat_ids.SetNumberOfTuples(num_cells)

        # Topology IDs (for debugging)
        topo_ids = vtkIntArray()
        topo_ids.SetName("TopologyID")
        topo_ids.SetNumberOfComponents(1)
        topo_ids.SetNumberOfTuples(num_cells)

        # Fill arrays (only for elements that were actually inserted)
        cell_idx = 0
        for elem in self.elements:
            topo = elem['topology']
            if topo not in FEMAP_TO_VTK:
                continue

            vtk_type, num_nodes_required = FEMAP_TO_VTK[topo]
            if len(elem['nodes']) < num_nodes_required:
                continue

            # Check all nodes exist
            all_nodes_exist = all(
                node_id in self.nodes for node_id in elem['nodes'][:num_nodes_required]
            )
            if not all_nodes_exist:
                continue

            # Add data for this cell
            elem_ids.SetValue(cell_idx, elem['id'])
            prop_ids.SetValue(cell_idx, elem['prop_id'])
            topo_ids.SetValue(cell_idx, elem['topology'])

            # Get material ID from property
            mat_id = 0
            if elem['prop_id'] in self.properties:
                mat_id = self.properties[elem['prop_id']].get('material_id', 0)
            mat_ids.SetValue(cell_idx, mat_id)

            cell_idx += 1

        # Add arrays to grid
        ug.GetCellData().AddArray(elem_ids)
        ug.GetCellData().AddArray(prop_ids)
        ug.GetCellData().AddArray(mat_ids)
        ug.GetCellData().AddArray(topo_ids)

    def write_vtu(self, output_filepath: str, validate: bool = True):
        """
        Convert FEMAP file to VTU and write to disk.

        Args:
            output_filepath: Output .vtu file path
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

        # Build VTK unstructured grid
        print("\nBuilding VTK Unstructured Grid...")
        ug = self.build_unstructured_grid()
        print(f"Created grid with {ug.GetNumberOfPoints()} points and {ug.GetNumberOfCells()} cells")

        # Add cell data
        print("Adding cell data...")
        self.add_cell_data(ug)

        # Write to file
        print(f"\nWriting VTU file: {output_filepath}")
        writer = vtkXMLUnstructuredGridWriter()
        writer.SetFileName(output_filepath)
        writer.SetInputData(ug)
        writer.Write()

        print("Conversion complete!")

        return ug


def convert_femap_to_vtu(femap_filepath: str, vtu_filepath: str, validate: bool = True):
    """
    Convenience function to convert FEMAP file to VTU.

    Args:
        femap_filepath: Input FEMAP Neutral file path
        vtu_filepath: Output VTU file path
        validate: If True, run validation checks
    """
    converter = FEMAPToVTUConverter(femap_filepath)
    converter.write_vtu(vtu_filepath, validate=validate)
