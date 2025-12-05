import shutil
from pathlib import Path
import re
import numpy as np

import pyvista as pv
from vtk import (
    VTK_HEXAHEDRON,
    VTK_LINE,
    VTK_QUAD,
    VTK_QUADRATIC_HEXAHEDRON,
    VTK_QUADRATIC_QUAD,
    VTK_QUADRATIC_TETRA,
    VTK_QUADRATIC_TRIANGLE,
    VTK_QUADRATIC_WEDGE,
    VTK_TETRA,
    VTK_TRIANGLE,
    VTK_VERTEX,
    VTK_WEDGE,
    vtkMultiBlockDataSet,
    vtkPoints,
    vtkUnstructuredGrid,
    vtkXMLMultiBlockDataWriter,
)

from pyemsi.femap_parser import FEMAPParser

# FEMAP topology to VTK cell type mapping
# Format: femap_topology_id -> (vtk_cell_type, num_nodes)
FEMAP_TO_VTK = {
    9: (VTK_VERTEX, 1),  # Point -> VTK_VERTEX
    0: (VTK_LINE, 2),  # Line2 -> VTK_LINE
    2: (VTK_TRIANGLE, 3),  # Tri3 -> VTK_TRIANGLE
    3: (VTK_QUADRATIC_TRIANGLE, 6),  # Tri6 -> VTK_QUADRATIC_TRIANGLE
    4: (VTK_QUAD, 4),  # Quad4 -> VTK_QUAD
    5: (VTK_QUADRATIC_QUAD, 8),  # Quad8 -> VTK_QUADRATIC_QUAD
    6: (VTK_TETRA, 4),  # Tetra4 -> VTK_TETRA
    10: (VTK_QUADRATIC_TETRA, 10),  # Tetra10 -> VTK_QUADRATIC_TETRA
    7: (VTK_WEDGE, 6),  # Wedge6 -> VTK_WEDGE
    11: (VTK_QUADRATIC_WEDGE, 15),  # Wedge15 -> VTK_QUADRATIC_WEDGE
    8: (VTK_HEXAHEDRON, 8),  # Brick8 -> VTK_HEXAHEDRON
    12: (VTK_QUADRATIC_HEXAHEDRON, 20),  # Brick20 -> VTK_QUADRATIC_HEXAHEDRON
}


class FemapConverter2:
    """
    Converts EMSolution's FEMAP Neutral files to VTK MultiBlock UnstructuredGrid format.
    """

    def __init__(
        self,
        input_dir: str | Path,
        output_dir: str | Path = "./.pyemsi",
        output_name: str = "output",
        mesh: str | Path = "post_geom",
        magnetic: str | Path | None = "magnetic",
        current: str | Path | None = "current",
        force: str | Path | None = "force",
        force_J_B: str | Path | None = "force_J_B",
        heat: str | Path | None = "heat",
        displacement: str | Path = "disp",
    ):
        self.block_to_elements_map = {}
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_name = output_name
        mesh_file = Path(mesh) if Path(mesh).is_file() else self.input_dir / mesh
        multiblock = self._build_mesh(mesh_file)

        # Clean up existing output files
        pvd_file = self.output_dir / f"{self.output_name}.pvd"
        if pvd_file.exists():
            pvd_file.unlink()
        if self.output_folder.exists():
            shutil.rmtree(self.output_folder)
        # Add magnetic
        if magnetic is not None:
            magnetic_file = Path(magnetic) if Path(magnetic).is_file() else self.input_dir / magnetic
            if magnetic_file.exists():
                self.add_magnetic_field(multiblock, magnetic_file)
        # Add current
        if current is not None:
            current_file = Path(current) if Path(current).is_file() else self.input_dir / current
            if current_file.exists():
                self.add_current_field(multiblock, current_file)
        # Add force
        if force is not None:
            force_file = Path(force) if Path(force).is_file() else self.input_dir / force
            if force_file.exists():
                self.add_force_field(multiblock, force_file)
        # Add force_J_B
        if force_J_B is not None:
            force_J_B_file = Path(force_J_B) if Path(force_J_B).is_file() else self.input_dir / force_J_B
            if force_J_B_file.exists():
                self.add_force_J_B_field(multiblock, force_J_B_file)
        # Add heat
        if heat is not None:
            heat_file = Path(heat) if Path(heat).is_file() else self.input_dir / heat
            if heat_file.exists():
                self.add_heat_field(multiblock, heat_file)
        # Add displacement
        if displacement is not None:
            displacement_file = Path(displacement) if Path(displacement).is_file() else self.input_dir / displacement
            if displacement_file.exists():
                self.add_displacement_field(multiblock, displacement_file)

    @property
    def output_folder(self) -> Path:
        return self.output_dir / self.output_name

    @property
    def pvd_file(self) -> Path:
        return self.output_dir / f"{self.output_name}.pvd"

    def init_pvd(self, multiblock: pv.MultiBlock, sets: dict[int, dict], ascii_mode: bool = False) -> None:
        """
        Initializes the PVD file with the converted mesh and associated vector fields.
        """
        if self.output_folder.exists():
            return

        self.output_folder.mkdir(parents=True, exist_ok=True)

        # Build PVD file content
        pvd_lines = [
            '<?xml version="1.0"?>',
            '<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">',
            "  <Collection>",
        ]
        for ts in sets.values():
            safe_title = re.sub(r'[<>:"/\\|?*!]', "", ts["title"])
            vtm_path = self.output_folder / f"{safe_title}.vtm"
            pvd_lines.append(
                f'    <DataSet timestep="{ts["value"]}" group="" part="0" file="{self.output_name}/{safe_title}.vtm"/>'
            )
            self._write_vtm_file(multiblock, vtm_path, ascii_mode=ascii_mode)
        pvd_lines.append("  </Collection>")
        pvd_lines.append("</VTKFile>")

        with open(self.pvd_file, "w") as f:
            f.write("\n".join(pvd_lines))

    def _write_vtm_file(self, multiblock: pv.MultiBlock, path: str | Path, ascii_mode: bool = False) -> None:
        writer = vtkXMLMultiBlockDataWriter()
        writer.SetFileName(str(path))
        writer.SetInputData(multiblock)
        if ascii_mode:
            writer.SetDataModeToAscii()
        # else:
        #     writer.SetDataModeToBinary()
        writer.Write()

    def _build_mesh(self, mesh_file: str | Path) -> "pv.MultiBlock":
        parser = FEMAPParser(mesh_file)
        nodes = parser.get_nodes()
        elements = parser.get_elements()
        properties = parser.get_properties()

        # Group elements by property ID
        elements_by_prop = {}
        for elem in elements:
            prop_id = elem["prop_id"]
            if prop_id not in elements_by_prop:
                elements_by_prop[prop_id] = []
            elements_by_prop[prop_id].append(elem)

        # Create VTK points and ID mapping (shared across all blocks)
        pts = vtkPoints()
        self.femap_to_vtk_id = {}

        for vtk_idx, femap_id in enumerate(sorted(nodes.keys())):
            x, y, z = nodes[femap_id]
            pts.InsertNextPoint(x, y, z)
            self.femap_to_vtk_id[femap_id] = vtk_idx

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

            # Insert cells for this property
            skipped = 0
            elem_idx_in_block = 0
            block_elements = []  # Collect (elem_id, elem_idx) for this block
            for elem in elements:
                topo = elem["topology"]

                if topo not in FEMAP_TO_VTK:
                    skipped += 1
                    continue

                vtk_type, num_nodes_required = FEMAP_TO_VTK[topo]
                elem_nodes = elem["nodes"][:num_nodes_required]

                if len(elem_nodes) < num_nodes_required:
                    skipped += 1
                    continue

                # Create ID list as Python list for the overload
                idlist = []
                valid = True
                for femap_node_id in elem_nodes:
                    if femap_node_id in self.femap_to_vtk_id:
                        vtk_idx = self.femap_to_vtk_id[femap_node_id]
                        idlist.append(vtk_idx)
                    else:
                        valid = False
                        skipped += 1
                        break

                if valid:
                    # Insert cell using sequence overload
                    ug.InsertNextCell(vtk_type, num_nodes_required, idlist)

                    # Track element mapping for this block
                    block_elements.append((elem["id"], elem_idx_in_block))
                    elem_idx_in_block += 1

            # Store block_to_elements mapping
            self.block_to_elements_map[block_idx] = block_elements

            # Set block in multiblock dataset
            mb.SetBlock(block_idx, ug)

            # Set block name
            prop_name = f"Property_{prop_id}"
            if prop_id in properties:
                prop_title = properties[prop_id].get("title", "")
                if prop_title:
                    prop_name = f"{prop_name}_{prop_title}"
            mb.GetMetaData(block_idx).Set(mb.NAME(), prop_name)

            print(
                f"Block {block_idx}: {prop_name} - {ug.GetNumberOfCells()} cells"
                + (f" ({skipped} skipped)" if skipped > 0 else "")
            )

            block_idx += 1

        return pv.MultiBlock(mb)

    def parse_data_file(self, file_path: str | Path) -> tuple[dict[int, dict], list[dict]]:
        parser = FEMAPParser(str(file_path))
        parser.parse()
        sets = parser.get_output_sets()
        vectors = parser.get_output_vectors()
        return sets, vectors

    def get_data_array(self, multiblock: pv.MultiBlock, step: int, vectors: list[dict]) -> dict[str, dict]:
        matching_vectors = [v for v in vectors if v["set_id"] == step]

        if not matching_vectors:
            raise ValueError(f"No vectors found for step={step}")

        # Get number of blocks
        num_blocks = multiblock.GetNumberOfBlocks()

        results_dict: dict[str, dict] = {}

        for matching_vector in matching_vectors:
            title = matching_vector["title"]
            ent_type = matching_vector["ent_type"]
            results = matching_vector["results"]

            # Sanitize title for use as array name
            safe_title = re.sub(r'[<>:"/\\|?*!]', "_", title) if title else f"Vector_{matching_vector['vec_id']}"

            data_arrays: dict[int, np.ndarray] = {}

            if ent_type == 8:  # Elemental data
                for block_idx in range(num_blocks):
                    block = multiblock.GetBlock(block_idx)
                    if block is None:
                        continue

                    num_cells = block.GetNumberOfCells()
                    if num_cells == 0:
                        continue

                    # Create numpy array filled with zeros
                    arr = np.zeros(num_cells, dtype=np.float64)  # Assign values based on element mapping
                    for elem_id, elem_idx in self.block_to_elements_map[block_idx]:
                        if elem_id in results:
                            arr[elem_idx] = results[elem_id]

                    data_arrays[block_idx] = arr

            elif ent_type == 7:  # Nodal data
                for block_idx in range(num_blocks):
                    block = multiblock.GetBlock(block_idx)
                    if block is None:
                        continue

                    num_points = block.GetNumberOfPoints()
                    if num_points == 0:
                        continue

                    # Create numpy array filled with zeros
                    arr = np.zeros(num_points, dtype=np.float64)

                    # Assign values based on node mapping
                    for femap_node_id, value in results.items():
                        if femap_node_id in self.femap_to_vtk_id:
                            vtk_idx = self.femap_to_vtk_id[femap_node_id]
                            if vtk_idx < num_points:
                                arr[vtk_idx] = value

                    data_arrays[block_idx] = arr

            results_dict[safe_title] = {
                "ent_type": ent_type,
                "data_arrays": data_arrays,
            }

        return results_dict

    def add_magnetic_field(self, multiblock: pv.MultiBlock, magnetic_file: str | Path) -> None:
        sets, vectors = self.parse_data_file(magnetic_file)

        if not self.output_folder.exists() or not self.pvd_file.exists():
            self.init_pvd(multiblock, sets)

        # load the multiblock pvd data
        reader = pv.PVDReader(self.pvd_file)

        for step in range(reader.number_time_points):
            reader.set_active_time_point(step)
            current_dataset = reader.datasets[step]
            vtm_path = self.output_dir / current_dataset.path
            multiblock = reader.read()[0]
            data_arrays = self.get_data_array(multiblock, step + 1, vectors=vectors)
            for index, block in enumerate(multiblock):
                node_1 = data_arrays["BMAG-node-1"]["data_arrays"].get(index)
                node_2 = data_arrays["BMAG-node-2"]["data_arrays"].get(index)
                node_3 = data_arrays["BMAG-node-3"]["data_arrays"].get(index)
                node_vec = np.vstack((node_1, node_2, node_3)).T
                block.point_data["B-Vec (T)"] = node_vec
                node_4 = data_arrays["BMAG-node-4"]["data_arrays"].get(index)
                block.point_data["B-Mag (T)"] = node_4
                if "BMAG-node-5" in data_arrays:
                    node_5 = data_arrays["BMAG-node-5"]["data_arrays"].get(index)
                    block.point_data["Flux (Wb)"] = node_5
                element_1 = data_arrays["BMAG-elem-1"]["data_arrays"].get(index)
                element_2 = data_arrays["BMAG-elem-2"]["data_arrays"].get(index)
                element_3 = data_arrays["BMAG-elem-3"]["data_arrays"].get(index)
                element_vec = np.vstack((element_1, element_2, element_3)).T
                block.cell_data["B-Vec (T)"] = element_vec
                element_4 = data_arrays["BMAG-elem-4"]["data_arrays"].get(index)
                block.cell_data["B-Mag (T)"] = element_4

            self._write_vtm_file(multiblock, vtm_path)

    def add_current_field(self, multiblock: pv.MultiBlock, current_file: str | Path) -> None:
        sets, vectors = self.parse_data_file(current_file)

        if not self.output_folder.exists() or not self.pvd_file.exists():
            self.init_pvd(multiblock, sets)

        # load the multiblock pvd data
        reader = pv.PVDReader(str(self.pvd_file))

        for step in range(reader.number_time_points):
            reader.set_active_time_point(step)
            current_dataset = reader.datasets[step]
            vtm_path = self.output_dir / current_dataset.path
            multiblock = reader.read()[0]
            data_arrays = self.get_data_array(multiblock, step + 1, vectors=vectors)
            for index, block in enumerate(multiblock):
                node_1 = data_arrays["CURR-node-1"]["data_arrays"].get(index)
                node_2 = data_arrays["CURR-node-2"]["data_arrays"].get(index)
                node_3 = data_arrays["CURR-node-3"]["data_arrays"].get(index)
                node_vec = np.vstack((node_1, node_2, node_3)).T
                block.point_data["J-Vec (A/m^2)"] = node_vec
                node_4 = data_arrays["CURR-node-4"]["data_arrays"].get(index)
                block.point_data["J-Mag (A/m^2)"] = node_4
                node_5 = data_arrays["CURR-node-5"]["data_arrays"].get(index)
                block.point_data["Loss (W/m^3)"] = node_5
                element_1 = data_arrays["CURR-elem-1"]["data_arrays"].get(index)
                element_2 = data_arrays["CURR-elem-2"]["data_arrays"].get(index)
                element_3 = data_arrays["CURR-elem-3"]["data_arrays"].get(index)
                element_vec = np.vstack((element_1, element_2, element_3)).T
                block.cell_data["J-Vec (A/m^2)"] = element_vec
                element_4 = data_arrays["CURR-elem-4"]["data_arrays"].get(index)
                block.cell_data["J-Mag (A/m^2)"] = element_4
                element_5 = data_arrays["CURR-elem-5"]["data_arrays"].get(index)
                block.cell_data["Loss (W/m^3)"] = element_5

            self._write_vtm_file(multiblock, vtm_path)

    def add_force_field(self, multiblock: pv.MultiBlock, force_file: str | Path) -> None:
        sets, vectors = self.parse_data_file(force_file)

        if not self.output_folder.exists() or not self.pvd_file.exists():
            self.init_pvd(multiblock, sets)

        # load the multiblock pvd data
        reader = pv.PVDReader(str(self.pvd_file))

        for step in range(reader.number_time_points):
            reader.set_active_time_point(step)
            current_dataset = reader.datasets[step]
            vtm_path = self.output_dir / current_dataset.path
            multiblock = reader.read()[0]
            data_arrays = self.get_data_array(multiblock, step + 1, vectors=vectors)
            for index, block in enumerate(multiblock):
                node_1 = data_arrays["NFOR-node-1"]["data_arrays"].get(index)
                node_2 = data_arrays["NFOR-node-2"]["data_arrays"].get(index)
                node_3 = data_arrays["NFOR-node-3"]["data_arrays"].get(index)
                node_vec = np.vstack((node_1, node_2, node_3)).T
                block.point_data["F Nodal-Vec (N/m^3)"] = node_vec
                node_4 = data_arrays["NFOR-node-4"]["data_arrays"].get(index)
                block.point_data["F Nodal-Mag (N/m^3)"] = node_4
                element_1 = data_arrays["EFOR-elem-1"]["data_arrays"].get(index)
                element_2 = data_arrays["EFOR-elem-2"]["data_arrays"].get(index)
                element_3 = data_arrays["EFOR-elem-3"]["data_arrays"].get(index)
                element_vec = np.vstack((element_1, element_2, element_3)).T
                block.cell_data["F Nodal-Vec (N/m^3)"] = element_vec
                element_4 = data_arrays["EFOR-elem-4"]["data_arrays"].get(index)
                block.cell_data["F Nodal-Mag (N/m^3)"] = element_4

            self._write_vtm_file(multiblock, vtm_path)

    def add_force_J_B_field(self, multiblock: pv.MultiBlock, force_J_B_file: str | Path) -> None:
        sets, vectors = self.parse_data_file(force_J_B_file)

        if not self.output_folder.exists() or not self.pvd_file.exists():
            self.init_pvd(multiblock, sets)

        # load the multiblock pvd data
        reader = pv.PVDReader(str(self.pvd_file))

        for step in range(reader.number_time_points):
            reader.set_active_time_point(step)
            current_dataset = reader.datasets[step]
            vtm_path = self.output_dir / current_dataset.path
            multiblock = reader.read()[0]
            data_arrays = self.get_data_array(multiblock, step + 1, vectors=vectors)
            for index, block in enumerate(multiblock):
                node_1 = data_arrays["LFOR-node-1"]["data_arrays"].get(index)
                node_2 = data_arrays["LFOR-node-2"]["data_arrays"].get(index)
                node_3 = data_arrays["LFOR-node-3"]["data_arrays"].get(index)
                node_vec = np.vstack((node_1, node_2, node_3)).T
                block.point_data["F Lorents-Vec (N/m^3)"] = node_vec
                node_4 = data_arrays["LFOR-node-4"]["data_arrays"].get(index)
                block.point_data["F Lorents-Mag (N/m^3)"] = node_4
                element_1 = data_arrays["ELFOR-elem-1"]["data_arrays"].get(index)
                element_2 = data_arrays["ELFOR-elem-2"]["data_arrays"].get(index)
                element_3 = data_arrays["ELFOR-elem-3"]["data_arrays"].get(index)
                element_vec = np.vstack((element_1, element_2, element_3)).T
                block.cell_data["F Lorents-Vec (N/m^3)"] = element_vec
                element_4 = data_arrays["ELFOR-elem-4"]["data_arrays"].get(index)
                block.cell_data["F Lorents-Mag (N/m^3)"] = element_4

            self._write_vtm_file(multiblock, vtm_path)

    def add_heat_field(self, multiblock: pv.MultiBlock, heat_file: str | Path) -> None:
        sets, vectors = self.parse_data_file(heat_file)

        if not self.output_folder.exists() or not self.pvd_file.exists():
            self.init_pvd(multiblock, sets)

        # load the multiblock pvd data
        reader = pv.PVDReader(str(self.pvd_file))

        for step in range(reader.number_time_points):
            reader.set_active_time_point(step)
            current_dataset = reader.datasets[step]
            vtm_path = self.output_dir / current_dataset.path
            multiblock = reader.read()[0]
            data_arrays = self.get_data_array(multiblock, step + 1, vectors=vectors)
            for index, block in enumerate(multiblock):
                node_1 = data_arrays["HEAT-node-1"]["data_arrays"].get(index)
                block.point_data["Heat Density (W/m^3)"] = node_1
                node_2 = data_arrays["HEAT-node-2"]["data_arrays"].get(index)
                block.point_data["Heat (W)"] = node_2
                element_1 = data_arrays["HEAT-elem-1"]["data_arrays"].get(index)
                block.cell_data["Heat Density (W/m^3)"] = element_1
                element_2 = data_arrays["HEAT-elem-2"]["data_arrays"].get(index)
                block.cell_data["Heat (W)"] = element_2

            self._write_vtm_file(multiblock, vtm_path)

    def add_displacement_field(self, multiblock: pv.MultiBlock, displacement_file: str | Path) -> None:
        sets, vectors = self.parse_data_file(displacement_file)

        if not self.output_folder.exists() or not self.pvd_file.exists():
            self.init_pvd(multiblock, sets)

        # load the multiblock pvd data
        reader = pv.PVDReader(str(self.pvd_file))

        for step in range(reader.number_time_points):
            reader.set_active_time_point(step)
            current_dataset = reader.datasets[step]
            vtm_path = self.output_dir / current_dataset.path
            multiblock = reader.read()[0]
            data_arrays = self.get_data_array(multiblock, step + 1, vectors=vectors)
            for index, block in enumerate(multiblock):
                node_1 = data_arrays["DISP-node-1"]["data_arrays"].get(index)
                node_2 = data_arrays["DISP-node-2"]["data_arrays"].get(index)
                node_3 = data_arrays["DISP-node-3"]["data_arrays"].get(index)
                node_vec = np.vstack((node_1, node_2, node_3)).T
                block.points += node_vec

            self._write_vtm_file(multiblock, vtm_path)
