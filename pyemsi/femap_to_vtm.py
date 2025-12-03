"""
FEMAP to VTM Converter

This module converts FEMAP Neutral files to VTK MultiBlock UnstructuredGrid (.vtm) format.
Elements are organized by property ID into separate UnstructuredGrid blocks.
"""

from pathlib import Path
import re
from typing import Dict, List, Tuple, Optional
import numpy as np
from vtk import (
    vtkPoints, vtkUnstructuredGrid,
    vtkIntArray, vtkDoubleArray,
    vtkMultiBlockDataSet,
    vtkXMLMultiBlockDataWriter,
    VTK_VERTEX, VTK_LINE, VTK_TRIANGLE, VTK_QUAD, VTK_TETRA,
    VTK_HEXAHEDRON, VTK_WEDGE,
    VTK_QUADRATIC_TRIANGLE, VTK_QUADRATIC_QUAD, VTK_QUADRATIC_TETRA,
    VTK_QUADRATIC_HEXAHEDRON, VTK_QUADRATIC_WEDGE
)
import pyvista as pv

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


class FemapConverter:
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
        self.directory = str(Path(femap_filepath).parent)
        self.parser = FEMAPParser(femap_filepath)
        self.nodes: Dict[int, Tuple[float, float, float]] = {}
        self.elements: List[Dict] = []
        self.properties: Dict[int, Dict] = {}
        self.materials: Dict[int, Dict] = {}
        self.header: Optional[Dict[str, str]] = None
        self._parsed: bool = False  # Track if parsing has been done
        self.multiblock: Optional[pv.MultiBlock] = None
        self.block_to_elements_map: Dict[int, List[Tuple[int, int]]] = {}  # block_idx -> [(elem_id, elem_idx_in_block), ...]
        self.data: Dict[str, Dict] = {}  # Store appended data arrays

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

    def build_mesh(self) -> 'pv.MultiBlock':
        """
        Build VTK MultiBlock UnstructuredGrid with separate blocks for each property ID.

        Each block is a vtkUnstructuredGrid containing elements with the same property ID.
        All blocks share the same point set.

        Returns:
            pv.MultiBlock containing one pv.UnstructuredGrid per property
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

        # Initialize block_to_elements_map
        self.block_to_elements_map = {}

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
            elem_idx_in_block = 0
            block_elements = []  # Collect (elem_id, elem_idx) for this block
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

                    # Track element mapping for this block
                    block_elements.append((elem['id'], elem_idx_in_block))
                    elem_idx_in_block += 1

            # Store block_to_elements mapping
            self.block_to_elements_map[block_idx] = block_elements

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

        self.multiblock = pv.MultiBlock(mb)
        return self.multiblock

    def write_vtm(self, output_filepath: str = ".pyemsi", validate: bool = True) -> 'pv.MultiBlock':
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
        self.build_mesh()
        print(f"Created MultiBlock UnstructuredGrid with {self.multiblock.GetNumberOfBlocks()} blocks")

        # Write to file
        print(f"\nWriting VTM file: {output_filepath}")
        writer = vtkXMLMultiBlockDataWriter()
        writer.SetFileName(output_filepath)
        writer.SetInputData(self.multiblock)
        writer.SetDataModeToAscii()  # Make VTU files human-readable
        writer.Write()

        print("Conversion complete!")

        return self.multiblock

    def _write_vtm_file(self, output_path: Path, ascii_mode: bool = True) -> None:
        """
        Write the multiblock dataset to a VTM file.

        Args:
            output_path: Path to write the VTM file
            ascii_mode: If True, write in ASCII format (human-readable but larger).
                       If False, write in binary format (smaller but not human-readable).
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        writer = vtkXMLMultiBlockDataWriter()
        writer.SetFileName(str(output_path))
        writer.SetInputData(self.multiblock)
        if ascii_mode:
            writer.SetDataModeToAscii()
        else:
            writer.SetDataModeToBinary()
        writer.Write()

    def append_data(self, data_path: str) -> None:
        """
        Append additional data from a VTK file to the multiblock dataset.

        Args:
            data_path: Path to VTK file containing data arrays
        """
        if self.multiblock is None:
            raise RuntimeError("Multiblock dataset not built yet. Call build_mesh() first.")

        parser = FEMAPParser(data_path)
        parser.parse()
        sets = parser.get_output_sets()
        vectors = parser.get_output_vectors()
        self.data[data_path] = {"sets": sets, "vectors": vectors}
    
    def parse_data_file(self, file_name: str) -> Tuple[Dict[int, Dict], List[Dict]]:
        """
        Static method to parse a data file and extract output sets and vectors.

        Args:
            file_name: Path to data file    

        Returns:
            Tuple containing:
                - output sets dictionary
                - list of output vectors
        """
        parser = FEMAPParser(Path(self.directory) / file_name)
        parser.parse()
        sets = parser.get_output_sets()
        vectors = parser.get_output_vectors()
        return sets, vectors

    def init_pvd(
        self,
        sets: Dict[int, Dict],
        vectors: List[Dict],
        name: str = "output",
        force: bool = False,
        output_dir: str = ".pyemsi",
        ascii_mode: bool = True
    ) -> Path:
        """
        Initialize a PVD file structure based on output sets and vectors.

        This method creates the PVD file and its associated folder structure
        for time series data. It validates the sets/vectors to determine
        the time steps that will be written, and writes a VTM file for each timestep.

        Args:
            sets: Dictionary of output sets (step_id -> set_info dict with 'title', 'value', etc.)
            vectors: List of output vector dictionaries
            name: Name for the PVD file and its folder (without extension)
            force: If True, replace existing PVD file and folder. If False, raise error if exists.
            output_dir: Base output directory for the PVD file
            ascii_mode: If True, write VTM files in ASCII format. If False, use binary.

        Returns:
            Path to the created PVD file

        Raises:
            RuntimeError: If multiblock dataset not built yet
            FileExistsError: If PVD file or folder exists and force=False
            ValueError: If no valid time steps found in sets
        """
        if self.multiblock is None:
            raise RuntimeError("Multiblock dataset not built yet. Call build_mesh() first.")

        if not sets:
            raise ValueError("No output sets provided. Cannot determine time steps.")

        # Setup paths
        output_path = Path(output_dir)
        pvd_path = output_path / f"{name}.pvd"
        vtm_folder = output_path / f"{name}_vtms"

        # Check for existing files/folders
        if not force:
            if pvd_path.exists():
                raise FileExistsError(f"PVD file already exists: {pvd_path}. Use force=True to overwrite.")
            if vtm_folder.exists():
                raise FileExistsError(f"VTM folder already exists: {vtm_folder}. Use force=True to overwrite.")
        else:
            # Remove existing files/folders if force=True
            if pvd_path.exists():
                pvd_path.unlink()
            if vtm_folder.exists():
                import shutil
                shutil.rmtree(vtm_folder)

        # Create directories
        output_path.mkdir(parents=True, exist_ok=True)
        vtm_folder.mkdir(parents=True, exist_ok=True)

        # Validate and collect time steps from sets
        time_steps = []
        for step_id, set_info in sorted(sets.items()):
            title = set_info.get("title", f"step_{step_id}")
            value = set_info.get("value", 0.0)
            # Check if there are any vectors for this step
            vectors_for_step = [v for v in vectors if v.get("set_id") == step_id]
            time_steps.append({
                "step_id": step_id,
                "title": title,
                "value": value,
                "num_vectors": len(vectors_for_step)
            })

        if not time_steps:
            raise ValueError("No valid time steps found in output sets.")

        # Build PVD file content
        pvd_lines = [
            '<?xml version="1.0"?>',
            '<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">',
            "  <Collection>",
        ]

        for ts in time_steps:
            # Sanitize filename
            safe_title = re.sub(r'[<>:"/\\|?*!]', '', ts["title"])
            vtm_name = f"{name}_vtms/{safe_title}.vtm"
            pvd_lines.append(
                f'    <DataSet timestep="{ts["value"]}" group="" part="0" file="{vtm_name}"/>'
            )
            
            # Write VTM file for this timestep
            vtm_path = output_path / vtm_name
            self._write_vtm_file(vtm_path, ascii_mode=ascii_mode)

        pvd_lines.extend([
            "  </Collection>",
            "</VTKFile>"
        ])

        # Write PVD file
        with open(pvd_path, "w") as f:
            f.write("\n".join(pvd_lines))

        print(f"Initialized PVD file: {pvd_path}")
        print(f"  - {len(time_steps)} time step(s)")
        print(f"  - VTM folder: {vtm_folder}")

        return pvd_path

    def write_pvd(self, output_filepath: str = ".pyemsi/output.pvd", ascii_mode: bool = True) -> None:
        """
        Write a PVD file referencing the VTM file for time series data.

        Args:
            output_filepath: Output .pvd file path
            ascii_mode: If True, write VTM/VTU files in ASCII format (human-readable but larger).
                       If False, write in binary format (smaller but not human-readable).
        """
        if self.multiblock is None:
            raise RuntimeError("Multiblock dataset not built yet. Call build_mesh() first.")
        
        pvd_path = Path(output_filepath)
        pvd_path.parent.mkdir(parents=True, exist_ok=True)

        pvd_lines = [
        '<?xml version="1.0"?>',
        '<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">',
        "  <Collection>",
        ]

        if self.data == {}:
            # Single time step
            vtm_name = Path(pvd_path.stem + "_vtms") / "t_0.000000e+00.vtm"
            pvd_lines.append(
                f'    <DataSet timestep="0.000000" group="" part="0" file="{vtm_name}"/>'
            )
            self._write_vtm_file(pvd_path.parent / vtm_name, ascii_mode=ascii_mode)
        else:
            # Multiple time steps
            first_data_path = list(self.data.keys())[0]
            vectors = self.data[first_data_path]["vectors"]
            for step, val in self.data[first_data_path]["sets"].items():
                file_name = re.sub(r'[<>:"/\\|?*!]', '', val["title"])
                vtm_name = Path(pvd_path.stem + "_vtms") / f"{file_name}.vtm"
                pvd_lines.append(
                    f'    <DataSet timestep="{val["value"]}" group="" part="0" file="{vtm_name}"/>'
                )
                # self._assign_data_to_multiblock(step)
                # self._write_vtm_file(pvd_path.parent / vtm_name, ascii_mode=ascii_mode)

                data_arrays = self.get_data_array(step, vectors=vectors)
                print(f"Writing VTM for step {step} with data array '{data_arrays}'")
        
        pvd_lines.extend([
            "  </Collection>",
            "</VTKFile>"
        ])

        with open(pvd_path, "w") as f:
            f.write("\n".join(pvd_lines))

    def _assign_data_to_multiblock(self, step: int) -> None:
        """
        Assign output data arrays to the multiblock dataset for a specific output set.

        This method iterates through all output vectors that belong to the specified
        output set (step) and adds them as cell data (elemental) or point data (nodal)
        arrays to the appropriate blocks in the multiblock dataset.

        Args:
            step: The output set ID to assign data for
        """
        if self.multiblock is None:
            raise RuntimeError("Multiblock dataset not built yet. Call build_mesh() first.")

        # Collect all vectors for this step from all data sources
        vectors_for_step = []
        for data_path, data_info in self.data.items():
            for vector in data_info["vectors"]:
                if vector["set_id"] == step:
                    vectors_for_step.append(vector)

        if not vectors_for_step:
            return

        # Get number of blocks
        num_blocks = self.multiblock.GetNumberOfBlocks()

        # Process each vector
        for vector in vectors_for_step:
            title = vector["title"]
            ent_type = vector["ent_type"]
            results = vector["results"]

            # Sanitize title for use as array name
            safe_title = re.sub(r'[<>:"/\\|?*!]', '_', title) if title else f"Vector_{vector['vec_id']}"

            if ent_type == 8:  # Elemental data
                # Add as cell data to each block
                for block_idx in range(num_blocks):
                    block = self.multiblock.GetBlock(block_idx)
                    if block is None:
                        continue

                    num_cells = block.GetNumberOfCells()
                    if num_cells == 0:
                        continue

                    # Create array for this block
                    data_array = vtkDoubleArray()
                    data_array.SetName(safe_title)
                    data_array.SetNumberOfComponents(1)
                    data_array.SetNumberOfTuples(num_cells)

                    # Fill with NaN initially (for missing data)
                    for i in range(num_cells):
                        data_array.SetValue(i, float('nan'))

                    # Assign values based on element mapping
                    for elem_id, elem_idx in self.block_to_elements_map[block_idx]:
                        if elem_id in results:
                            data_array.SetValue(elem_idx, results[elem_id])

                    block.GetCellData().AddArray(data_array)

            elif ent_type == 7:  # Nodal data
                # Add as point data to each block
                # All blocks share the same points, so we only need to build the mapping once
                femap_to_vtk_id = {}
                for vtk_idx, femap_id in enumerate(sorted(self.nodes.keys())):
                    femap_to_vtk_id[femap_id] = vtk_idx

                for block_idx in range(num_blocks):
                    block = self.multiblock.GetBlock(block_idx)
                    if block is None:
                        continue

                    num_points = block.GetNumberOfPoints()
                    if num_points == 0:
                        continue

                    # Create array for this block
                    data_array = vtkDoubleArray()
                    data_array.SetName(safe_title)
                    data_array.SetNumberOfComponents(1)
                    data_array.SetNumberOfTuples(num_points)

                    # Fill with NaN initially (for missing data)
                    for i in range(num_points):
                        data_array.SetValue(i, float('nan'))

                    # Assign values based on node mapping
                    for femap_node_id, value in results.items():
                        if femap_node_id in femap_to_vtk_id:
                            vtk_idx = femap_to_vtk_id[femap_node_id]
                            if vtk_idx < num_points:
                                data_array.SetValue(vtk_idx, value)

                    block.GetPointData().AddArray(data_array)

    def get_data_array(self, step: int, vectors: List[Dict]) -> Dict[str, Dict]:
        """
        Extract data arrays for a specific output set from the provided vectors.

        Similar to _assign_data_to_multiblock but returns the data as numpy arrays
        instead of assigning directly to the multiblock.

        Args:
            step: The output set ID to get data for
            vectors: List of output vector dictionaries to search through

        Returns:
            Dict mapping title to dict with keys:
                - "ent_type": The entity type (7=nodal, 8=elemental)
                - "data_arrays": Dict mapping block_idx to numpy array of values

        Raises:
            RuntimeError: If multiblock dataset not built yet
            ValueError: If no matching vectors found for the given step
        """
        if self.multiblock is None:
            raise RuntimeError("Multiblock dataset not built yet. Call build_mesh() first.")

        # Find all matching vectors for the given step
        matching_vectors = [v for v in vectors if v["set_id"] == step]

        if not matching_vectors:
            raise ValueError(f"No vectors found for step={step}")

        # Get number of blocks
        num_blocks = self.multiblock.GetNumberOfBlocks()

        # Build node mapping once (for nodal data)
        femap_to_vtk_id = {}
        for vtk_idx, femap_id in enumerate(sorted(self.nodes.keys())):
            femap_to_vtk_id[femap_id] = vtk_idx

        results_dict: Dict[str, Dict] = {}

        for matching_vector in matching_vectors:
            title = matching_vector["title"]
            ent_type = matching_vector["ent_type"]
            results = matching_vector["results"]

            # Sanitize title for use as array name
            safe_title = re.sub(r'[<>:"/\\|?*!]', '_', title) if title else f"Vector_{matching_vector['vec_id']}"

            data_arrays: Dict[int, np.ndarray] = {}

            if ent_type == 8:  # Elemental data
                for block_idx in range(num_blocks):
                    block = self.multiblock.GetBlock(block_idx)
                    if block is None:
                        continue

                    num_cells = block.GetNumberOfCells()
                    if num_cells == 0:
                        continue

                    # Create numpy array filled with NaN
                    arr = np.full(num_cells, np.nan, dtype=np.float64)

                    # Assign values based on element mapping
                    for elem_id, elem_idx in self.block_to_elements_map[block_idx]:
                        if elem_id in results:
                            arr[elem_idx] = results[elem_id]

                    data_arrays[block_idx] = arr

            elif ent_type == 7:  # Nodal data
                for block_idx in range(num_blocks):
                    block = self.multiblock.GetBlock(block_idx)
                    if block is None:
                        continue

                    num_points = block.GetNumberOfPoints()
                    if num_points == 0:
                        continue

                    # Create numpy array filled with NaN
                    arr = np.full(num_points, np.nan, dtype=np.float64)

                    # Assign values based on node mapping
                    for femap_node_id, value in results.items():
                        if femap_node_id in femap_to_vtk_id:
                            vtk_idx = femap_to_vtk_id[femap_node_id]
                            if vtk_idx < num_points:
                                arr[vtk_idx] = value

                    data_arrays[block_idx] = arr

            results_dict[safe_title] = {"ent_type": ent_type, "data_arrays": data_arrays}

        return results_dict
    
    def append_magnetic(self, data_path: Optional[str] = None) -> None:
        """
        Append magnetic data from a specified file or default location.

        Args:
            data_path: Path to magnetic data file. If None, uses default path.
        """
        if data_path is None:
            data_path = str(Path(self.directory) / "magnetic")
        
        # load the multiblock pvd data
        reader = pv.PVDReader('.pyemsi/output.pvd')

        sets, vectors = self.parse_data_file("magnetic")

        for step in range(reader.number_time_points):
            reader.set_active_time_point(step)
            current_dataset = reader.datasets[step]
            vtm_path = Path(".pyemsi") / current_dataset.path
            multiblock = reader.read()[0]
            data_arrays = self.get_data_array(step+1, vectors=vectors)
            for index, block in enumerate(multiblock):
                node_1 = data_arrays["BMAG-node-1"]["data_arrays"].get(index)
                node_2 = data_arrays["BMAG-node-2"]["data_arrays"].get(index)
                node_3 = data_arrays["BMAG-node-3"]["data_arrays"].get(index)
                node_vec = np.vstack((node_1, node_2, node_3)).T
                block.point_data["B-Vector"] = node_vec
                node_4 = data_arrays["BMAG-node-4"]["data_arrays"].get(index)
                block.point_data["B-Magnitude"] = node_4
                element_1 = data_arrays["BMAG-elem-1"]["data_arrays"].get(index)
                element_2 = data_arrays["BMAG-elem-2"]["data_arrays"].get(index)
                element_3 = data_arrays["BMAG-elem-3"]["data_arrays"].get(index)
                element_vec = np.vstack((element_1, element_2, element_3)).T
                block.cell_data["B-Vector"] = element_vec
                element_4 = data_arrays["BMAG-elem-4"]["data_arrays"].get(index)
                block.cell_data["B-Magnitude"] = element_4
            
            writer = vtkXMLMultiBlockDataWriter()
            writer.SetFileName(str(vtm_path))
            writer.SetInputData(multiblock)
            if 1:
                writer.SetDataModeToAscii()
            else:
                writer.SetDataModeToBinary()
            writer.Write()

        
        
    