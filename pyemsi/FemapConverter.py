import re
import shutil
import threading
from pathlib import Path

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

FORCE_2D_TOPOLOGY = {
    8: 4,  # Brick8 -> Quad4
    12: 5,  # Brick20 -> Quad8
    7: 2,  # Wedge6 -> Tri3
    11: 3,  # Wedge15 -> Tri6
}


class FemapConverter:
    """
    Converts EMSolution's FEMAP Neutral files to VTK MultiBlock UnstructuredGrid format.
    """

    def __init__(
        self,
        input_dir: str | Path,
        output_dir: str | Path = "./.pyemsi",
        output_name: str = "output",
        force_2d: bool = False,
        mesh: str | Path = "post_geom",
        magnetic: str | Path | None = "magnetic",
        current: str | Path | None = "current",
        force: str | Path | None = "force",
        force_J_B: str | Path | None = "force_J_B",
        heat: str | Path | None = "heat",
        displacement: str | Path = "disp",
    ):
        self.elements_map = {}
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_name = output_name
        mesh_file = Path(mesh) if Path(mesh).is_file() else self.input_dir / mesh
        self.sets: dict[int, dict[int, dict]] = {}
        self.vectors: dict[str, list[dict]] = {}
        self._build_mesh(mesh_file, force_2d=force_2d)

        # Clean up existing output files
        pvd_file = self.output_dir / f"{self.output_name}.pvd"
        if pvd_file.exists():
            pvd_file.unlink()
        if self.output_folder.exists():
            shutil.rmtree(self.output_folder)

        # Add displacement
        self.displacement_file = None
        if displacement is not None:
            displacement_file = Path(displacement) if Path(displacement).is_file() else self.input_dir / displacement
            if displacement_file.exists():
                self.displacement_file = displacement_file

        # Add magnetic
        self.magnetic_file = None
        if magnetic is not None:
            magnetic_file = Path(magnetic) if Path(magnetic).is_file() else self.input_dir / magnetic
            if magnetic_file.exists():
                self.magnetic_file = magnetic_file
        # Add current
        self.current_file = None
        if current is not None:
            current_file = Path(current) if Path(current).is_file() else self.input_dir / current
            if current_file.exists():
                self.current_file = current_file
        # Add force
        self.force_file = None
        if force is not None:
            force_file = Path(force) if Path(force).is_file() else self.input_dir / force
            if force_file.exists():
                self.force_file = force_file
        # Add force_J_B
        self.force_J_B_file = None
        if force_J_B is not None:
            force_J_B_file = Path(force_J_B) if Path(force_J_B).is_file() else self.input_dir / force_J_B
            if force_J_B_file.exists():
                self.force_J_B_file = force_J_B_file
        # Add heat
        self.heat_file = None
        if heat is not None:
            heat_file = Path(heat) if Path(heat).is_file() else self.input_dir / heat
            if heat_file.exists():
                self.heat_file = heat_file

        self.parse_data_files()
        self.init_pvd()
        self.time_stepping()

    @property
    def output_folder(self) -> Path:
        return self.output_dir / self.output_name

    @property
    def pvd_file(self) -> Path:
        return self.output_dir / f"{self.output_name}.pvd"

    def init_pvd(self) -> None:
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
        for ts in self.sets.values():
            safe_title = re.sub(r'[<>:"/\\|?*!]', "", ts["title"])
            # vtm_path = self.output_folder / f"{safe_title}.vtm"
            pvd_lines.append(
                f'    <DataSet timestep="{ts["value"]}" group="" part="0" file="{self.output_name}/{safe_title}.vtm"/>'
            )
        pvd_lines.append("  </Collection>")
        pvd_lines.append("</VTKFile>")

        with open(self.pvd_file, "w") as f:
            f.write("\n".join(pvd_lines))

    def _write_vtm_file(
        self, mesh: pv.MultiBlock | pv.UnstructuredGrid, path: str | Path, ascii_mode: bool = False
    ) -> None:
        if isinstance(mesh, pv.UnstructuredGrid):
            mesh = self._vtu_to_vtm(mesh)
        writer = vtkXMLMultiBlockDataWriter()
        writer.SetFileName(str(path))
        writer.SetInputData(mesh)
        if ascii_mode:
            writer.SetDataModeToAscii()
        writer.Write()

    def _vtu_to_vtm(self, unstructured_grid: pv.UnstructuredGrid) -> pv.MultiBlock:
        # Create a new MultiBlock dataset based on the PropertyID cell data
        # Create a MultiBlock dataset and add the subgrid
        mb = pv.MultiBlock()
        for prop_id in self.unique_props:
            # Extract cells with the current property ID
            cell_indices = np.where(unstructured_grid.cell_data["PropertyID"] == prop_id)[0]
            if len(cell_indices) == 0:
                continue

            # Create a new UnstructuredGrid for this property
            subgrid = unstructured_grid.extract_cells(cell_indices)

            # Set block name
            subgrid_name = str(prop_id)
            mb[subgrid_name] = subgrid

        return mb

    def _build_mesh(self, mesh_file: str | Path, force_2d: bool = False) -> None:
        parser = FEMAPParser(str(mesh_file))
        nodes = parser.get_nodes(force_2d)
        elements = parser.get_elements()

        # Create VTK points and ID mapping
        pts = vtkPoints()
        self.femap_to_vtk_id = {}

        for vtk_idx, femap_id in enumerate(sorted(nodes.keys())):
            x, y, z = nodes[femap_id]
            pts.InsertNextPoint(x, y, z)
            self.femap_to_vtk_id[femap_id] = vtk_idx

        # Create single unstructured grid
        ug = vtkUnstructuredGrid()
        ug.SetPoints(pts)
        ug.Allocate(len(elements))

        # Track property IDs for each cell
        property_ids = []
        vtk_cell_idx = 0

        for elem in elements:
            topo = elem["topology"]
            if force_2d:
                try:
                    topo = FORCE_2D_TOPOLOGY[topo]
                except KeyError as exc:
                    raise ValueError(f"Cannot force 2D for element topology {topo}") from exc

            if topo not in FEMAP_TO_VTK:
                continue

            vtk_type, num_nodes_required = FEMAP_TO_VTK[topo]
            elem_nodes = elem["nodes"][:num_nodes_required]

            if len(elem_nodes) < num_nodes_required:
                continue

            try:
                idlist = [self.femap_to_vtk_id[n] for n in elem_nodes]
            except KeyError:
                continue

            ug.InsertNextCell(vtk_type, num_nodes_required, idlist)
            property_ids.append(elem["prop_id"])
            # Store mapping: FEMAP element ID -> VTK cell index
            self.elements_map[elem["id"]] = vtk_cell_idx
            vtk_cell_idx += 1

        # Convert to PyVista UnstructuredGrid
        self.mesh = pv.wrap(ug)
        self.init_points = self.mesh.points.copy()

        # Add property IDs as cell data
        self.mesh.cell_data["PropertyID"] = np.array(property_ids, dtype=np.int32)

        # uniqe property IDs
        self.unique_props = np.unique(property_ids)

    def parse_data_file(self, name: str, file_path: str | Path):
        print(f"Parsing data file: {file_path}")
        parser = FEMAPParser(str(file_path))
        parser.parse()
        sets = parser.get_output_sets()
        self.vectors[name] = parser.get_output_vectors()
        if not self.sets:
            self.sets = sets

    def parse_data_files(self) -> None:
        file_map = {
            "displacement": self.displacement_file,
            "magnetic": self.magnetic_file,
            "current": self.current_file,
            "force": self.force_file,
            "force_J_B": self.force_J_B_file,
            "heat": self.heat_file,
        }
        threads = []
        for name, file_path in file_map.items():
            if file_path is not None:
                thread = threading.Thread(target=self.parse_data_file, args=(name, file_path))
                thread.start()
                threads.append(thread)
        for thread in threads:
            thread.join()

    def get_data_array(self, step: int, vectors: list[dict]) -> dict[str, np.ndarray]:
        """
        Get data arrays for a single UnstructuredGrid mesh.

        Args:
            mesh: PyVista UnstructuredGrid mesh
            step: Time step / output set ID
            vectors: List of vector dictionaries from parser

        Returns:
            Dictionary mapping sanitized vector titles to numpy arrays
        """
        matching_vectors = [v for v in vectors if v["set_id"] == step]

        if not matching_vectors:
            raise ValueError(f"No vectors found for step={step}")

        results_dict: dict[str, np.ndarray] = {}

        for matching_vector in matching_vectors:
            title = matching_vector["title"]
            ent_type = matching_vector["ent_type"]
            results = matching_vector["results"]

            # Sanitize title for use as array name
            safe_title = re.sub(r'[<>:"/\\|?*!]', "_", title) if title else f"Vector_{matching_vector['vec_id']}"

            if ent_type == 8:  # Elemental data
                num_cells = self.mesh.n_cells
                if num_cells == 0:
                    continue

                # Create numpy array filled with zeros
                arr = np.zeros(num_cells, dtype=np.float32)

                # Assign values based on FEMAP element ID using elements_map
                for elem_id, value in results.items():
                    if elem_id in self.elements_map:
                        vtk_idx = self.elements_map[elem_id]
                        if 0 <= vtk_idx < num_cells:
                            arr[vtk_idx] = value

                results_dict[safe_title] = arr

            elif ent_type == 7:  # Nodal data
                num_points = self.mesh.n_points
                if num_points == 0:
                    continue

                # Create numpy array filled with zeros
                arr = np.zeros(num_points, dtype=np.float32)

                # Assign values based on FEMAP node ID using femap_to_vtk_id
                for node_id, value in results.items():
                    if node_id in self.femap_to_vtk_id:
                        vtk_idx = self.femap_to_vtk_id[node_id]
                        if 0 <= vtk_idx < num_points:
                            arr[vtk_idx] = value

                results_dict[safe_title] = arr

        return results_dict

    def time_stepping(self) -> None:
        threads = []
        for step, ts in self.sets.items():
            print(f"Processing time step {step} - {ts['title']}")
            safe_title = re.sub(r'[<>:"/\\|?*!]', "", ts["title"])
            vtm_path = self.output_dir / self.output_name / f"{safe_title}.vtm"
            thread = threading.Thread(target=self._process_time_step, args=(step, vtm_path))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def _process_time_step(self, step: int, vtm_path: str | Path) -> None:
        # Create a copy of the mesh for thread safety
        mesh_copy = self.mesh.copy()
        mesh_copy.points = self.init_points.copy()

        if "displacement" in self.vectors:
            self._process_displacement_field(step, mesh_copy)
        if "magnetic" in self.vectors:
            self._process_magnetic_field(step, mesh_copy)
        if "current" in self.vectors:
            self._process_current_field(step, mesh_copy)
        if "force" in self.vectors:
            self._process_force_field(step, mesh_copy)
        if "force_J_B" in self.vectors:
            self._process_force_J_B_field(step, mesh_copy)
        if "heat" in self.vectors:
            self._process_heat_field(step, mesh_copy)
        self._write_vtm_file(mesh_copy, vtm_path)

    def _process_displacement_field(self, step: int, mesh: pv.UnstructuredGrid) -> None:
        data_arrays = self.get_data_array(step, self.vectors["displacement"])
        node_1 = data_arrays["DISP-node-1"]
        node_2 = data_arrays["DISP-node-2"]
        node_3 = data_arrays["DISP-node-3"]
        node_vec = np.vstack((node_1, node_2, node_3)).T
        mesh.points = self.init_points + node_vec

    def _process_magnetic_field(self, step: int, mesh: pv.UnstructuredGrid) -> None:
        data_arrays = self.get_data_array(step, self.vectors["magnetic"])
        node_1 = data_arrays["BMAG-node-1"]
        node_2 = data_arrays["BMAG-node-2"]
        node_3 = data_arrays["BMAG-node-3"]
        node_vec = np.vstack((node_1, node_2, node_3)).T
        mesh.point_data["B-Vec (T)"] = node_vec
        node_4 = data_arrays["BMAG-node-4"]
        mesh.point_data["B-Mag (T)"] = node_4
        if "BMAG-node-5" in data_arrays:
            node_5 = data_arrays["BMAG-node-5"]
            mesh.point_data["Flux (A/m)"] = node_5
        element_1 = data_arrays["BMAG-elem-1"]
        element_2 = data_arrays["BMAG-elem-2"]
        element_3 = data_arrays["BMAG-elem-3"]
        element_vec = np.vstack((element_1, element_2, element_3)).T
        mesh.cell_data["B-Vec (T)"] = element_vec
        element_4 = data_arrays["BMAG-elem-4"]
        mesh.cell_data["B-Mag (T)"] = element_4

    def _process_current_field(self, step: int, mesh: pv.UnstructuredGrid) -> None:
        data_arrays = self.get_data_array(step, self.vectors["current"])
        node_1 = data_arrays["CURR-node-1"]
        node_2 = data_arrays["CURR-node-2"]
        node_3 = data_arrays["CURR-node-3"]
        node_vec = np.vstack((node_1, node_2, node_3)).T
        mesh.point_data["J-Vec (A/m^2)"] = node_vec
        node_4 = data_arrays["CURR-node-4"]
        mesh.point_data["J-Mag (A/m^2)"] = node_4
        node_5 = data_arrays["CURR-node-5"]
        mesh.point_data["Loss (W/m^3)"] = node_5
        element_1 = data_arrays["CURR-elem-1"]
        element_2 = data_arrays["CURR-elem-2"]
        element_3 = data_arrays["CURR-elem-3"]
        element_vec = np.vstack((element_1, element_2, element_3)).T
        mesh.cell_data["J-Vec (A/m^2)"] = element_vec
        element_4 = data_arrays["CURR-elem-4"]
        mesh.cell_data["J-Mag (A/m^2)"] = element_4
        element_5 = data_arrays["CURR-elem-5"]
        mesh.cell_data["Loss (W/m^3)"] = element_5

    def _process_force_field(self, step: int, mesh: pv.UnstructuredGrid) -> None:
        data_arrays = self.get_data_array(step, self.vectors["force"])
        node_1 = data_arrays["NFOR-node-1"]
        node_2 = data_arrays["NFOR-node-2"]
        node_3 = data_arrays["NFOR-node-3"]
        node_vec = np.vstack((node_1, node_2, node_3)).T
        mesh.point_data["F Nodal-Vec (N/m^3)"] = node_vec
        node_4 = data_arrays["NFOR-node-4"]
        mesh.point_data["F Nodal-Mag (N/m^3)"] = node_4
        element_1 = data_arrays["NFOR-elem-1"]
        element_2 = data_arrays["NFOR-elem-2"]
        element_3 = data_arrays["NFOR-elem-3"]
        element_vec = np.vstack((element_1, element_2, element_3)).T
        mesh.cell_data["F Nodal-Vec (N/m^3)"] = element_vec
        element_4 = data_arrays["NFOR-elem-4"]
        mesh.cell_data["F Nodal-Mag (N/m^3)"] = element_4

    def _process_force_J_B_field(self, step: int, mesh: pv.UnstructuredGrid) -> None:
        data_arrays = self.get_data_array(step, self.vectors["force_J_B"])
        node_1 = data_arrays["LFOR-node-1"]
        node_2 = data_arrays["LFOR-node-2"]
        node_3 = data_arrays["LFOR-node-3"]
        node_vec = np.vstack((node_1, node_2, node_3)).T
        mesh.point_data["F Lorents-Vec (N/m^3)"] = node_vec
        node_4 = data_arrays["LFOR-node-4"]
        mesh.point_data["F Lorents-Mag (N/m^3)"] = node_4
        element_1 = data_arrays["LFOR-elem-1"]
        element_2 = data_arrays["LFOR-elem-2"]
        element_3 = data_arrays["LFOR-elem-3"]
        element_vec = np.vstack((element_1, element_2, element_3)).T
        mesh.cell_data["F Lorents-Vec (N/m^3)"] = element_vec
        element_4 = data_arrays["LFOR-elem-4"]
        mesh.cell_data["F Lorents-Mag (N/m^3)"] = element_4

    def _process_heat_field(self, step: int, mesh: pv.UnstructuredGrid) -> None:
        data_arrays = self.get_data_array(step, self.vectors["heat"])
        node_1 = data_arrays["HEAT-node-1"]
        mesh.point_data["Heat Density (W/m^3)"] = node_1
        node_2 = data_arrays["HEAT-node-2"]
        mesh.point_data["Heat (W)"] = node_2
        element_1 = data_arrays["HEAT-elem-1"]
        mesh.cell_data["Heat Density (W/m^3)"] = element_1
        element_2 = data_arrays["HEAT-elem-2"]
        mesh.cell_data["Heat (W)"] = element_2
