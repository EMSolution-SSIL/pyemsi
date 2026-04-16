"""Tests for the current FEMAP converter mesh and file-writing pipeline."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pyvista as pv
from vtk import VTK_QUAD, vtkXMLMultiBlockDataReader

from pyemsi.tools.FemapConverter import FEMAP_TO_VTK, FemapConverter


class TestFemapConverter(unittest.TestCase):
    """Test cases for FemapConverter class."""

    def setUp(self):
        """Set up test fixtures path."""
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        self.simple_mesh = os.path.join(self.fixtures_dir, "simple_mesh.neu")
        self.mixed_mesh = os.path.join(self.fixtures_dir, "mixed_elements.neu")

    def _make_output_dir(self) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        return temp_dir.name

    def _make_converter(self, mesh_path: str, **kwargs) -> FemapConverter:
        kwargs.setdefault("input_dir", self.fixtures_dir)
        kwargs.setdefault("output_dir", self._make_output_dir())
        kwargs.setdefault("mesh", mesh_path)
        return FemapConverter(**kwargs)

    def test_converter_initialization(self):
        """Test converter initialization uses the current directory-based API."""
        converter = self._make_converter(self.simple_mesh)

        self.assertEqual(converter.input_dir, Path(self.fixtures_dir))
        self.assertEqual(converter._mesh_file, Path(self.simple_mesh))
        self.assertEqual(converter.output_folder, Path(converter.output_dir) / converter.output_name)
        self.assertIsNone(converter.input_control)
        self.assertIsNone(converter.displacement_file)
        self.assertEqual(converter.vectors, {})

    def test_build_mesh_populates_unstructured_grid(self):
        """Test mesh construction populates the wrapped unstructured grid."""
        converter = self._make_converter(self.simple_mesh)
        converter._build_mesh(converter._mesh_file)

        self.assertEqual(converter.mesh.n_points, 8)
        self.assertEqual(converter.mesh.n_cells, 1)
        self.assertEqual(len(converter.elements_map), 1)
        self.assertEqual(len(converter.femap_to_vtk_id), 8)
        self.assertEqual(converter.unique_props.tolist(), [1])

    def test_build_mesh_tracks_point_id_mapping(self):
        """Test FEMAP node IDs are mapped onto deterministic VTK point IDs."""
        converter = self._make_converter(self.simple_mesh)
        converter._build_mesh(converter._mesh_file)

        self.assertEqual(converter.femap_to_vtk_id[1], 0)
        self.assertEqual(converter.femap_to_vtk_id[2], 1)
        self.assertEqual(converter.femap_to_vtk_id[8], 7)

    def test_force_2d_build_mesh_remaps_supported_topology(self):
        """Test force_2d remaps supported 3D elements to their 2D topology."""
        converter = self._make_converter(self.simple_mesh)
        converter._build_mesh(converter._mesh_file, force_2d=True)

        self.assertEqual(converter.mesh.n_cells, 1)
        self.assertEqual(converter.mesh.GetCellType(0), VTK_QUAD)

    def test_force_2d_rejects_unsupported_topology(self):
        """Test force_2d raises when a topology cannot be projected into 2D."""

        class _StubParser:
            def __init__(self, _path):
                pass

            def get_nodes(self, _force_2d):
                return {1: (0.0, 0.0, 0.0)}

            def get_elements(self):
                return [{"id": 1, "topology": 9, "nodes": [1], "prop_id": 1}]

        converter = self._make_converter(self.simple_mesh)

        with patch("pyemsi.tools.FemapConverter.FEMAPParser", _StubParser):
            with self.assertRaisesRegex(ValueError, "Cannot force 2D"):
                converter._build_mesh("ignored.neu", force_2d=True)

    def test_vtu_to_vtm_groups_cells_by_property(self):
        """Test conversion from unstructured grid to multiblock groups by PropertyID."""
        converter = self._make_converter(self.simple_mesh)
        converter._build_mesh(converter._mesh_file)
        mb = converter._vtu_to_vtm(converter.mesh)

        self.assertIsInstance(mb, pv.MultiBlock)
        self.assertGreater(len(mb), 0)

        block0 = mb[0]
        self.assertEqual(block0.n_points, 8)
        self.assertEqual(block0.n_cells, 1)

    def test_cell_data_in_blocks(self):
        """Test multiblock conversion retains current PropertyID cell data."""
        converter = self._make_converter(self.simple_mesh)
        converter._build_mesh(converter._mesh_file)
        mb = converter._vtu_to_vtm(converter.mesh)

        block0 = mb[0]
        self.assertIn("PropertyID", block0.cell_data)

    def test_write_vtm(self):
        """Test writing a VTM file from the built mesh."""
        converter = self._make_converter(self.simple_mesh)
        converter._build_mesh(converter._mesh_file)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".vtm") as f:
            output_file = f.name

        try:
            converter._write_vtm_file(converter.mesh, output_file)
            self.assertTrue(os.path.exists(output_file))
            self.assertGreater(os.path.getsize(output_file), 0)

            reader = vtkXMLMultiBlockDataReader()
            reader.SetFileName(output_file)
            reader.Update()
            mb = reader.GetOutput()

            self.assertGreater(mb.GetNumberOfBlocks(), 0)
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_mixed_elements_conversion(self):
        """Test conversion of a mixed-element mesh into grouped multiblock output."""
        converter = self._make_converter(self.mixed_mesh)
        converter._build_mesh(converter._mesh_file)
        mb = converter._vtu_to_vtm(converter.mesh)

        self.assertGreater(len(mb), 0)

        total_cells = sum(block.n_cells for block in mb)
        self.assertEqual(total_cells, 3)

    def test_topology_mapping(self):
        """Test FEMAP to VTK topology mapping."""
        # Verify key mappings exist
        self.assertIn(8, FEMAP_TO_VTK)  # Brick8
        self.assertIn(6, FEMAP_TO_VTK)  # Tetra4
        self.assertIn(2, FEMAP_TO_VTK)  # Tri3
        self.assertIn(4, FEMAP_TO_VTK)  # Quad4

        # Verify mapping structure
        vtk_type, num_nodes = FEMAP_TO_VTK[8]
        self.assertEqual(vtk_type, 12)  # VTK_HEXAHEDRON
        self.assertEqual(num_nodes, 8)

    def test_input_control_file_is_loaded_when_present(self):
        """Test optional input-control JSON is loaded through the new constructor."""
        with tempfile.TemporaryDirectory() as input_dir:
            control_path = Path(input_dir) / "input_control.json"
            payload = {
                "2_Analysis_Type": {"STATIC": 2},
                "10_3_Post_Files": {"CURRENT": 2},
            }
            control_path.write_text(json.dumps(payload), encoding="utf-8")

            converter = self._make_converter(
                self.simple_mesh,
                input_dir=input_dir,
                input_control_file="input_control.json",
            )

            self.assertEqual(converter.input_control_file, control_path)
            self.assertEqual(converter.input_control, payload)

    def test_cell_data_values(self):
        """Test that current cell data values are preserved after grouping."""
        converter = self._make_converter(self.simple_mesh)
        converter._build_mesh(converter._mesh_file)
        mb = converter._vtu_to_vtm(converter.mesh)

        block0 = mb[0]
        prop_ids = block0.cell_data["PropertyID"]

        self.assertEqual(int(prop_ids[0]), 1)

    def test_point_coordinates(self):
        """Test that point coordinates are correctly transferred into the mesh."""
        converter = self._make_converter(self.simple_mesh)
        converter._build_mesh(converter._mesh_file)

        points = converter.mesh.points

        coord = tuple(points[0])
        self.assertEqual(coord, (0.0, 0.0, 0.0))

        coord = tuple(points[1])
        self.assertEqual(coord, (1.0, 0.0, 0.0))


class TestTopologyMapping(unittest.TestCase):
    """Test cases for FEMAP to VTK topology mapping."""

    def test_all_topologies_defined(self):
        """Test that all common topologies are defined."""
        expected_topologies = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        for topo in expected_topologies:
            self.assertIn(topo, FEMAP_TO_VTK, f"Topology {topo} not in mapping")

    def test_node_counts(self):
        """Test that node counts are reasonable."""
        for topo, (vtk_type, num_nodes) in FEMAP_TO_VTK.items():
            self.assertGreater(num_nodes, 0, f"Invalid node count for topology {topo}")
            self.assertLessEqual(num_nodes, 20, f"Unexpected node count for topology {topo}")


class TestIntegration(unittest.TestCase):
    """Integration tests for full conversion pipeline."""

    def setUp(self):
        """Set up test fixtures path."""
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        self.simple_mesh = os.path.join(self.fixtures_dir, "simple_mesh.neu")
        self.mixed_mesh = os.path.join(self.fixtures_dir, "mixed_elements.neu")

    def test_run_creates_output_folder_and_pvd_for_mesh_only_input(self):
        """Test the current run() pipeline creates an output folder and PVD file."""
        with tempfile.TemporaryDirectory() as output_dir:
            converter = FemapConverter(input_dir=self.fixtures_dir, output_dir=output_dir, mesh=self.simple_mesh)

            converter.run()

            self.assertTrue(converter.output_folder.exists())
            self.assertTrue(converter.pvd_file.exists())
            content = converter.pvd_file.read_text(encoding="utf-8")
            self.assertIn("<Collection>", content)
            self.assertNotIn("<DataSet", content)

    def test_end_to_end_mixed_mesh_write_and_readback(self):
        """Test mixed-element mesh write and readback through the current writer."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".vtm") as f:
            output_file = f.name

        try:
            converter = FemapConverter(
                input_dir=self.fixtures_dir,
                output_dir=tempfile.mkdtemp(),
                mesh=self.mixed_mesh,
            )
            converter._build_mesh(converter._mesh_file)
            converter._write_vtm_file(converter.mesh, output_file)

            self.assertTrue(os.path.exists(output_file))
            self.assertGreater(os.path.getsize(output_file), 100)

            reader = vtkXMLMultiBlockDataReader()
            reader.SetFileName(output_file)
            reader.Update()
            mb = reader.GetOutput()

            self.assertGreater(mb.GetNumberOfBlocks(), 0)
            total_cells = sum(mb.GetBlock(i).GetNumberOfCells() for i in range(mb.GetNumberOfBlocks()))
            self.assertEqual(total_cells, 3)
            block0 = mb.GetBlock(0)
            self.assertIsNotNone(block0.GetCellData().GetArray("PropertyID"))

        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)


if __name__ == "__main__":
    unittest.main()
