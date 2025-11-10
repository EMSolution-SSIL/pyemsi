"""
Tests for FEMAP Neutral file parser.
"""

import os
import unittest
from pyemsi.femap_parser import FEMAPParser, FEMAPBlock


class TestFEMAPParser(unittest.TestCase):
    """Test cases for FEMAPParser class."""

    def setUp(self):
        """Set up test fixtures path."""
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.simple_mesh = os.path.join(self.fixtures_dir, 'simple_mesh.neu')
        self.mixed_mesh = os.path.join(self.fixtures_dir, 'mixed_elements.neu')

    def test_parse_simple_mesh(self):
        """Test parsing a simple single-element mesh."""
        parser = FEMAPParser(self.simple_mesh)
        blocks = parser.parse()

        # Check that we have the expected blocks
        self.assertIn(100, blocks)  # Header
        self.assertIn(403, blocks)  # Nodes
        self.assertIn(402, blocks)  # Properties
        self.assertIn(404, blocks)  # Elements
        self.assertIn(601, blocks)  # Materials

    def test_parse_block_structure(self):
        """Test that blocks are parsed correctly."""
        parser = FEMAPParser(self.simple_mesh)
        blocks = parser.parse()

        # Check block types
        self.assertIsInstance(blocks[100][0], FEMAPBlock)
        self.assertEqual(blocks[100][0].block_id, 100)

    def test_get_header(self):
        """Test header extraction."""
        parser = FEMAPParser(self.simple_mesh)
        parser.parse()
        header = parser.get_header()

        self.assertIsNotNone(header)
        self.assertEqual(header['version'], '4.41')
        self.assertEqual(header['title'], '')  # <NULL> becomes empty string

    def test_get_nodes(self):
        """Test node extraction."""
        parser = FEMAPParser(self.simple_mesh)
        parser.parse()
        nodes = parser.get_nodes()

        # Should have 8 nodes (hex element)
        self.assertEqual(len(nodes), 8)

        # Check specific node coordinates
        self.assertEqual(nodes[1], (0.0, 0.0, 0.0))
        self.assertEqual(nodes[2], (1.0, 0.0, 0.0))
        self.assertEqual(nodes[3], (1.0, 1.0, 0.0))
        self.assertEqual(nodes[8], (0.0, 1.0, 1.0))

    def test_get_properties(self):
        """Test property extraction."""
        parser = FEMAPParser(self.simple_mesh)
        parser.parse()
        properties = parser.get_properties()

        self.assertEqual(len(properties), 1)
        self.assertIn(1, properties)
        self.assertEqual(properties[1]['material_id'], 1)
        self.assertEqual(properties[1]['title'], 'Material1')

    def test_get_elements(self):
        """Test element extraction."""
        parser = FEMAPParser(self.simple_mesh)
        parser.parse()
        elements = parser.get_elements()

        self.assertEqual(len(elements), 1)
        elem = elements[0]
        self.assertEqual(elem['id'], 1)
        self.assertEqual(elem['prop_id'], 1)
        self.assertEqual(elem['topology'], 8)  # Brick8
        self.assertEqual(len(elem['nodes']), 8)
        self.assertEqual(elem['nodes'], [1, 2, 3, 4, 5, 6, 7, 8])

    def test_get_materials(self):
        """Test material extraction."""
        parser = FEMAPParser(self.simple_mesh)
        parser.parse()
        materials = parser.get_materials()

        self.assertIn(1, materials)
        self.assertEqual(materials[1]['id'], 1)

    def test_repeated_blocks(self):
        """Test handling of repeated blocks."""
        parser = FEMAPParser(self.mixed_mesh)
        blocks = parser.parse()

        # Mixed mesh has 2 material blocks and 2 property blocks
        self.assertEqual(len(blocks[601]), 2)  # 2 material blocks
        self.assertEqual(len(blocks[402]), 2)  # 2 property blocks
        self.assertEqual(len(blocks[404]), 3)  # 3 element blocks

    def test_mixed_elements(self):
        """Test parsing mesh with mixed element types."""
        parser = FEMAPParser(self.mixed_mesh)
        parser.parse()
        elements = parser.get_elements()

        self.assertEqual(len(elements), 3)

        # Check element types
        topologies = [elem['topology'] for elem in elements]
        self.assertIn(6, topologies)  # Tetra4
        self.assertIn(2, topologies)  # Tri3
        self.assertIn(4, topologies)  # Quad4

    def test_parse_csv_line(self):
        """Test CSV line parsing."""
        # Comma-separated
        result = FEMAPParser.parse_csv_line("1,2,3,4,5,")
        self.assertEqual(result, ['1', '2', '3', '4', '5'])

        # Space-separated
        result = FEMAPParser.parse_csv_line("1 2 3 4 5")
        self.assertEqual(result, ['1', '2', '3', '4', '5'])

        # Mixed (comma is preferred)
        result = FEMAPParser.parse_csv_line("1, 2, 3,4,5")
        self.assertEqual(result, ['1', '2', '3', '4', '5'])

    def test_empty_file(self):
        """Test handling of empty or invalid files."""
        # Create a temporary empty file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.neu') as f:
            empty_file = f.name

        try:
            parser = FEMAPParser(empty_file)
            blocks = parser.parse()
            self.assertEqual(len(blocks), 0)
        finally:
            os.unlink(empty_file)

    def test_multiple_node_blocks(self):
        """Test that multiple node blocks are combined."""
        parser = FEMAPParser(self.mixed_mesh)
        parser.parse()
        nodes = parser.get_nodes()

        # Mixed mesh has 8 nodes total
        self.assertEqual(len(nodes), 8)

    def test_multiple_property_blocks(self):
        """Test that multiple property blocks are combined."""
        parser = FEMAPParser(self.mixed_mesh)
        parser.parse()
        properties = parser.get_properties()

        # Mixed mesh has 2 properties
        self.assertEqual(len(properties), 2)
        self.assertIn(1, properties)
        self.assertIn(2, properties)
        self.assertEqual(properties[1]['title'], 'Steel_Property')
        self.assertEqual(properties[2]['title'], 'Aluminum_Property')


class TestFEMAPBlock(unittest.TestCase):
    """Test cases for FEMAPBlock class."""

    def test_block_creation(self):
        """Test FEMAPBlock creation."""
        lines = ["line1", "line2", "line3"]
        block = FEMAPBlock(403, lines)

        self.assertEqual(block.block_id, 403)
        self.assertEqual(block.lines, lines)
        self.assertEqual(len(block.lines), 3)

    def test_block_repr(self):
        """Test FEMAPBlock string representation."""
        block = FEMAPBlock(403, ["a", "b", "c"])
        repr_str = repr(block)
        self.assertIn("403", repr_str)
        self.assertIn("3", repr_str)


if __name__ == '__main__':
    unittest.main()
