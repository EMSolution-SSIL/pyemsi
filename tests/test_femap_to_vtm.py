"""
Tests for FEMAP to VTU converter.
"""

import os
import unittest
import tempfile

from vtk import vtkMultiBlockDataSet

from pyemsi.femap_to_vtm import FEMAPToVTMConverter, FEMAP_TO_VTK, convert_femap_to_vtm


class TestFEMAPToVTMConverter(unittest.TestCase):
    """Test cases for FEMAPToVTMConverter class."""

    def setUp(self):
        """Set up test fixtures path."""
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.simple_mesh = os.path.join(self.fixtures_dir, 'simple_mesh.neu')
        self.mixed_mesh = os.path.join(self.fixtures_dir, 'mixed_elements.neu')

    def test_converter_initialization(self):
        """Test converter initialization."""
        converter = FEMAPToVTMConverter(self.simple_mesh)
        self.assertEqual(converter.femap_filepath, self.simple_mesh)
        self.assertIsNotNone(converter.parser)

    def test_parse_femap(self):
        """Test FEMAP file parsing through converter."""
        converter = FEMAPToVTMConverter(self.simple_mesh)
        converter.parse_femap()

        self.assertEqual(len(converter.nodes), 8)
        self.assertEqual(len(converter.elements), 1)
        self.assertEqual(len(converter.properties), 1)
        self.assertIsNotNone(converter.header)

    def test_validate_success(self):
        """Test validation with valid data."""
        converter = FEMAPToVTMConverter(self.simple_mesh)
        converter.parse_femap()
        messages = converter.validate()

        # Should have no errors (may have warnings)
        errors = [m for m in messages if m.startswith("ERROR")]
        self.assertEqual(len(errors), 0)

    def test_validate_missing_nodes(self):
        """Test validation catches missing nodes."""
        converter = FEMAPToVTMConverter(self.simple_mesh)
        converter.parse_femap()

        # Remove a node that's referenced by an element
        del converter.nodes[1]

        messages = converter.validate()
        errors = [m for m in messages if m.startswith("ERROR")]
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("missing node" in m for m in errors))

    def test_build_multiblock_by_property(self):
        """Test VTK multiblock dataset building."""
        converter = FEMAPToVTMConverter(self.simple_mesh)
        converter.parse_femap()
        mb = converter.build_multiblock_by_property()

        self.assertIsInstance(mb, vtkMultiBlockDataSet)
        self.assertGreater(mb.GetNumberOfBlocks(), 0)

        # Check first block
        block0 = mb.GetBlock(0)
        self.assertEqual(block0.GetNumberOfPoints(), 8)
        self.assertEqual(block0.GetNumberOfCells(), 1)

    def test_cell_data_in_blocks(self):
        """Test cell data arrays in multiblock dataset."""
        converter = FEMAPToVTMConverter(self.simple_mesh)
        converter.parse_femap()
        mb = converter.build_multiblock_by_property()

        # Check first block has cell data
        block0 = mb.GetBlock(0)
        cell_data = block0.GetCellData()
        self.assertIsNotNone(cell_data.GetArray("ElementID"))
        self.assertIsNotNone(cell_data.GetArray("PropertyID"))
        self.assertIsNotNone(cell_data.GetArray("MaterialID"))
        self.assertIsNotNone(cell_data.GetArray("TopologyID"))

    def test_write_vtm(self):
        """Test writing VTM file."""
        converter = FEMAPToVTMConverter(self.simple_mesh)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.vtm') as f:
            output_file = f.name

        try:
            converter.write_vtm(output_file)
            self.assertTrue(os.path.exists(output_file))
            self.assertGreater(os.path.getsize(output_file), 0)
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_mixed_elements_conversion(self):
        """Test conversion of mesh with mixed element types."""
        converter = FEMAPToVTMConverter(self.mixed_mesh)
        converter.parse_femap()
        mb = converter.build_multiblock_by_property()

        # Should have at least one block
        self.assertGreater(mb.GetNumberOfBlocks(), 0)

        # Count total cells across all blocks
        total_cells = sum(mb.GetBlock(i).GetNumberOfCells()
                         for i in range(mb.GetNumberOfBlocks()))
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

    def test_convenience_function(self):
        """Test the convenience conversion function."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.vtm') as f:
            output_file = f.name

        try:
            convert_femap_to_vtm(self.simple_mesh, output_file)
            self.assertTrue(os.path.exists(output_file))
            self.assertGreater(os.path.getsize(output_file), 0)
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_cell_data_values(self):
        """Test that cell data values are correct."""
        converter = FEMAPToVTMConverter(self.simple_mesh)
        converter.parse_femap()
        mb = converter.build_multiblock_by_property()

        # Get first block
        block0 = mb.GetBlock(0)
        elem_ids = block0.GetCellData().GetArray("ElementID")
        prop_ids = block0.GetCellData().GetArray("PropertyID")
        mat_ids = block0.GetCellData().GetArray("MaterialID")

        # Check first element in first block
        self.assertEqual(elem_ids.GetValue(0), 1)
        self.assertEqual(prop_ids.GetValue(0), 1)
        self.assertEqual(mat_ids.GetValue(0), 1)

    def test_point_coordinates(self):
        """Test that point coordinates are correctly transferred."""
        converter = FEMAPToVTMConverter(self.simple_mesh)
        converter.parse_femap()
        mb = converter.build_multiblock_by_property()

        # Get points from first block (all blocks share the same points)
        block0 = mb.GetBlock(0)
        points = block0.GetPoints()

        # Check first point (node 1: 0,0,0)
        coord = points.GetPoint(0)
        self.assertEqual(coord, (0.0, 0.0, 0.0))

        # Check second point (node 2: 1,0,0)
        coord = points.GetPoint(1)
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
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.simple_mesh = os.path.join(self.fixtures_dir, 'simple_mesh.neu')
        self.mixed_mesh = os.path.join(self.fixtures_dir, 'mixed_elements.neu')

    def test_end_to_end_simple(self):
        """Test complete conversion pipeline for simple mesh."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.vtm') as f:
            output_file = f.name

        try:
            converter = FEMAPToVTMConverter(self.simple_mesh)
            converter.write_vtm(output_file, validate=True)

            # Verify file exists and has content
            self.assertTrue(os.path.exists(output_file))
            self.assertGreater(os.path.getsize(output_file), 100)

            # Read back and verify
            from vtk import vtkXMLMultiBlockDataReader
            reader = vtkXMLMultiBlockDataReader()
            reader.SetFileName(output_file)
            reader.Update()
            mb = reader.GetOutput()

            self.assertGreater(mb.GetNumberOfBlocks(), 0)
            # Get first block and verify
            block0 = mb.GetBlock(0)
            self.assertEqual(block0.GetNumberOfPoints(), 8)
            self.assertEqual(block0.GetNumberOfCells(), 1)

        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_end_to_end_mixed(self):
        """Test complete conversion pipeline for mixed element mesh."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.vtm') as f:
            output_file = f.name

        try:
            converter = FEMAPToVTMConverter(self.mixed_mesh)
            converter.write_vtm(output_file, validate=True)

            # Verify file exists
            self.assertTrue(os.path.exists(output_file))
            self.assertGreater(os.path.getsize(output_file), 100)

            # Read back and verify
            from vtk import vtkXMLMultiBlockDataReader
            reader = vtkXMLMultiBlockDataReader()
            reader.SetFileName(output_file)
            reader.Update()
            mb = reader.GetOutput()

            self.assertGreater(mb.GetNumberOfBlocks(), 0)

            # Count total cells across all blocks
            total_cells = sum(mb.GetBlock(i).GetNumberOfCells()
                             for i in range(mb.GetNumberOfBlocks()))
            self.assertEqual(total_cells, 3)

            # Verify cell data arrays exist in first block
            block0 = mb.GetBlock(0)
            self.assertIsNotNone(block0.GetCellData().GetArray("ElementID"))
            self.assertIsNotNone(block0.GetCellData().GetArray("PropertyID"))
            self.assertIsNotNone(block0.GetCellData().GetArray("MaterialID"))

        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)


if __name__ == '__main__':
    unittest.main()
