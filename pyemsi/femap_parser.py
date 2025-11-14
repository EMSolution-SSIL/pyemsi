"""
FEMAP Neutral File Parser

This module parses FEMAP Neutral files and extracts structured data blocks.
FEMAP files contain blocks identified by IDs, and blocks can appear in any order.
"""

from typing import Dict, List, Tuple, Optional


class FEMAPBlock:
    """Represents a single FEMAP data block."""

    def __init__(self, block_id: int, lines: List[str]):
        self.block_id = block_id
        self.lines = lines

    def __repr__(self):
        return f"FEMAPBlock(id={self.block_id}, lines={len(self.lines)})"


class FEMAPParser:
    """
    Parser for FEMAP Neutral files.

    Handles blocks in any order and supports repeated blocks of the same type.
    """

    BLOCK_DELIMITER = "   -1"  # 3 spaces + -1

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.blocks: Dict[int, List[FEMAPBlock]] = {}

    def parse(self) -> Dict[int, List[FEMAPBlock]]:
        """
        Parse the FEMAP file and return blocks grouped by ID.

        Returns:
            Dictionary mapping block IDs to lists of blocks
        """
        with open(self.filepath, 'r') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].rstrip('\n')

            # Check for block delimiter
            if line == self.BLOCK_DELIMITER:
                # Next line should contain block ID
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()

                    # Skip if next line is also a delimiter (double delimiter)
                    if next_line == self.BLOCK_DELIMITER.strip():
                        i += 1
                        continue

                    try:
                        block_id = int(next_line)
                        # Collect block content
                        block_lines = []
                        i += 2  # Skip delimiter and ID line

                        # Read until next delimiter
                        while i < len(lines):
                            line = lines[i].rstrip('\n')
                            if line == self.BLOCK_DELIMITER:
                                # Skip to after this delimiter
                                i += 1
                                break
                            block_lines.append(line)
                            i += 1

                        # Store block
                        block = FEMAPBlock(block_id, block_lines)
                        if block_id not in self.blocks:
                            self.blocks[block_id] = []
                        self.blocks[block_id].append(block)

                    except ValueError:
                        # Not a valid block ID, skip
                        i += 1
                else:
                    i += 1
            else:
                i += 1

        return self.blocks

    @staticmethod
    def parse_csv_line(line: str) -> List[str]:
        """
        Parse a FEMAP line that may be comma or space separated.

        Args:
            line: Input line string

        Returns:
            List of field values as strings
        """
        # Remove trailing comma if present
        line = line.rstrip(',').strip()

        # Try comma separation first
        if ',' in line:
            parts = [p.strip() for p in line.split(',') if p.strip()]
        else:
            # Fall back to space separation
            parts = line.split()

        return parts

    def get_blocks(self, block_id: int) -> List[FEMAPBlock]:
        """Get all blocks with the specified ID."""
        return self.blocks.get(block_id, [])

    def get_header(self) -> Optional[Dict[str, str]]:
        """
        Extract header information from Block 100.

        Returns:
            Dictionary with 'title' and 'version' keys, or None if not found
        """
        blocks = self.get_blocks(100)
        if not blocks:
            return None

        block = blocks[0]
        if len(block.lines) < 2:
            return None

        title = block.lines[0].strip()
        version = block.lines[1].strip()

        return {
            'title': title if title != '<NULL>' else '',
            'version': version
        }

    def get_nodes(self) -> Dict[int, Tuple[float, float, float]]:
        """
        Extract all nodes from Block 403.

        Returns:
            Dictionary mapping node IDs to (x, y, z) coordinates
        """
        nodes = {}

        for block in self.get_blocks(403):
            for line in block.lines:
                parts = self.parse_csv_line(line)
                if len(parts) >= 14:
                    try:
                        node_id = int(parts[0])
                        x = float(parts[11])
                        y = float(parts[12])
                        z = float(parts[13])
                        nodes[node_id] = (x, y, z)
                    except (ValueError, IndexError):
                        continue

        return nodes

    def get_properties(self) -> Dict[int, Dict[str, any]]:
        """
        Extract all properties from Block 402.

        Returns:
            Dictionary mapping property IDs to property metadata
        """
        properties = {}

        for block in self.get_blocks(402):
            i = 0
            while i < len(block.lines):
                # First line has property ID and material ID
                parts = self.parse_csv_line(block.lines[i])
                if len(parts) >= 3:
                    try:
                        prop_id = int(parts[0])
                        mat_id = int(parts[2])

                        # Second line has title
                        title = ''
                        if i + 1 < len(block.lines):
                            title = block.lines[i + 1].strip().rstrip(',')
                            if title == '<NULL>':
                                title = ''

                        properties[prop_id] = {
                            'material_id': mat_id,
                            'title': title
                        }

                        # Skip to next property (7 lines per property)
                        i += 7
                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return properties

    def get_elements(self) -> List[Dict[str, any]]:
        """
        Extract all elements from Block 404.

        Returns:
            List of element dictionaries with id, prop_id, topology, and nodes
        """
        elements = []

        for block in self.get_blocks(404):
            i = 0
            while i < len(block.lines):
                # First line has element ID, property ID, and topology
                parts = self.parse_csv_line(block.lines[i])
                if len(parts) >= 5:
                    try:
                        elem_id = int(parts[0])
                        prop_id = int(parts[2])
                        topology = int(parts[4])

                        # Next two lines have node connectivity (up to 20 nodes)
                        nodes = []
                        if i + 1 < len(block.lines):
                            nodes1 = self.parse_csv_line(block.lines[i + 1])
                            nodes.extend([int(n) for n in nodes1 if n and int(n) != 0])

                        if i + 2 < len(block.lines):
                            nodes2 = self.parse_csv_line(block.lines[i + 2])
                            nodes.extend([int(n) for n in nodes2 if n and int(n) != 0])

                        elements.append({
                            'id': elem_id,
                            'prop_id': prop_id,
                            'topology': topology,
                            'nodes': nodes
                        })

                        # Skip to next element (7 lines per element)
                        i += 7
                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return elements

    def get_materials(self) -> Dict[int, Dict[str, any]]:
        """
        Extract all materials from Block 601.

        Returns:
            Dictionary mapping material IDs to material metadata
        """
        materials = {}

        for block in self.get_blocks(601):
            # Basic material extraction - can be expanded based on actual needs
            i = 0
            while i < len(block.lines):
                parts = self.parse_csv_line(block.lines[i])
                if len(parts) >= 1:
                    try:
                        mat_id = int(parts[0])
                        materials[mat_id] = {'id': mat_id}
                        # Skip material block (structure varies)
                        i += 1
                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return materials
