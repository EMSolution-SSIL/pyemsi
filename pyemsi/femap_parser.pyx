# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: initializedcheck=False
"""
FEMAP Neutral File Parser (Cython Optimized)

This module parses FEMAP Neutral files and extracts structured data blocks.
FEMAP files contain blocks identified by IDs, and blocks can appear in any order.
"""

cimport cython
import numpy as np
cimport numpy as np

np.import_array()

from typing import Dict, List, Tuple, Optional


cdef class FEMAPBlock:
    """Represents a single FEMAP data block."""

    def __init__(self, int block_id, list lines):
        self.block_id = block_id
        self.lines = lines

    def __repr__(self):
        return f"FEMAPBlock(id={self.block_id}, lines={len(self.lines)})"


cdef class FEMAPParser:
    """
    Parser for FEMAP Neutral files.

    Handles blocks in any order and supports repeated blocks of the same type.
    """

    def __init__(self, str filepath):
        self.filepath = filepath
        self.blocks = {}
        self.BLOCK_DELIMITER = "   -1"  # 3 spaces + -1
        self._parse()

    cdef void _parse(self):
        """
        Parse the FEMAP file and populate blocks grouped by ID.
        Internal cdef method for performance.
        """
        cdef list lines
        cdef int i, n_lines, block_id
        cdef str line, next_line
        cdef list block_lines
        cdef FEMAPBlock block

        with open(self.filepath, "r") as f:
            lines = f.readlines()

        n_lines = len(lines)
        i = 0
        
        while i < n_lines:
            line = (<str>lines[i]).rstrip("\n")

            # Check for block delimiter
            if line == self.BLOCK_DELIMITER:
                # Next line should contain block ID
                if i + 1 < n_lines:
                    next_line = (<str>lines[i + 1]).strip()

                    # Skip if next line is also a delimiter (double delimiter)
                    if next_line == "-1":
                        i += 1
                        continue

                    try:
                        block_id = int(next_line)
                        # Collect block content
                        block_lines = []
                        i += 2  # Skip delimiter and ID line

                        # Read until next delimiter
                        while i < n_lines:
                            line = (<str>lines[i]).rstrip("\n")
                            if line == self.BLOCK_DELIMITER:
                                i += 1
                                break
                            block_lines.append(line)
                            i += 1

                        # Store block
                        block = FEMAPBlock(block_id, block_lines)
                        if block_id not in self.blocks:
                            self.blocks[block_id] = []
                        (<list>self.blocks[block_id]).append(block)

                    except ValueError:
                        i += 1
                else:
                    i += 1
            else:
                i += 1

    cpdef dict parse(self):
        """
        Public method to return parsed blocks (for API compatibility).
        
        Returns:
            Dictionary mapping block IDs to lists of blocks
        """
        return self.blocks

    @staticmethod
    cdef list _parse_csv_line_fast(str line):
        """
        Fast internal CSV line parser (cdef for performance).
        """
        cdef str stripped
        cdef list parts
        
        stripped = line.rstrip(",").strip()
        
        if "," in stripped:
            parts = [p.strip() for p in stripped.split(",") if p.strip()]
        else:
            parts = stripped.split()
        
        return parts

    @staticmethod
    def parse_csv_line(str line) -> list:
        """
        Parse a FEMAP line that may be comma or space separated.
        Public API-compatible wrapper.

        Args:
            line: Input line string

        Returns:
            List of field values as strings
        """
        return FEMAPParser._parse_csv_line_fast(line)

    cpdef list get_blocks(self, int block_id):
        """Get all blocks with the specified ID."""
        return self.blocks.get(block_id, [])

    cpdef dict get_header(self):
        """
        Extract header information from Block 100.

        Returns:
            Dictionary with 'title' and 'version' keys, or None if not found
        """
        cdef list blocks = self.get_blocks(100)
        cdef FEMAPBlock block
        cdef str title, version
        
        if not blocks:
            return None

        block = <FEMAPBlock>blocks[0]
        if len(block.lines) < 2:
            return None

        title = (<str>block.lines[0]).strip()
        version = (<str>block.lines[1]).strip()

        return {"title": title if title != "<NULL>" else "", "version": version}

    cpdef dict get_nodes(self):
        """
        Extract all nodes from Block 403.

        Returns:
            Dictionary mapping node IDs to (x, y, z) coordinates
        """
        cdef dict nodes = {}
        cdef list all_blocks, parts
        cdef FEMAPBlock block
        cdef str line
        cdef int node_id
        cdef double x, y, z

        all_blocks = self.get_blocks(403)
        for block in all_blocks:
            for line in block.lines:
                parts = FEMAPParser._parse_csv_line_fast(line)
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

    cpdef tuple get_nodes_arrays(self):
        """
        Extract all nodes from Block 403 as NumPy arrays (high performance).

        Returns:
            Tuple of (node_ids: np.ndarray[int32], coords: np.ndarray[float64, (n,3)])
        """
        cdef list all_blocks, parts, node_list, coord_list
        cdef FEMAPBlock block
        cdef str line
        cdef int node_id
        cdef double x, y, z

        node_list = []
        coord_list = []

        all_blocks = self.get_blocks(403)
        for block in all_blocks:
            for line in block.lines:
                parts = FEMAPParser._parse_csv_line_fast(line)
                if len(parts) >= 14:
                    try:
                        node_id = int(parts[0])
                        x = float(parts[11])
                        y = float(parts[12])
                        z = float(parts[13])
                        node_list.append(node_id)
                        coord_list.append((x, y, z))
                    except (ValueError, IndexError):
                        continue

        cdef np.ndarray[np.int32_t, ndim=1] node_ids = np.array(node_list, dtype=np.int32)
        cdef np.ndarray[np.float64_t, ndim=2] coords = np.array(coord_list, dtype=np.float64)
        
        return (node_ids, coords)

    cpdef dict get_properties(self):
        """
        Extract all properties from Block 402.

        Returns:
            Dictionary mapping property IDs to property metadata
        """
        cdef dict properties = {}
        cdef list all_blocks, parts
        cdef FEMAPBlock block
        cdef int i, prop_id, mat_id, n_lines
        cdef str title

        all_blocks = self.get_blocks(402)
        for block in all_blocks:
            i = 0
            n_lines = len(block.lines)
            while i < n_lines:
                parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                if len(parts) >= 3:
                    try:
                        prop_id = int(parts[0])
                        mat_id = int(parts[2])

                        title = ""
                        if i + 1 < n_lines:
                            title = (<str>block.lines[i + 1]).strip().rstrip(",")
                            if title == "<NULL>":
                                title = ""

                        properties[prop_id] = {"material_id": mat_id, "title": title}
                        i += 7
                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return properties

    cpdef list get_elements(self):
        """
        Extract all elements from Block 404.

        Returns:
            List of element dictionaries with id, prop_id, topology, and nodes
        """
        cdef list elements = []
        cdef list all_blocks, parts, nodes, nodes1, nodes2
        cdef FEMAPBlock block
        cdef int i, elem_id, prop_id, topology, n_lines, n

        all_blocks = self.get_blocks(404)
        for block in all_blocks:
            i = 0
            n_lines = len(block.lines)
            while i < n_lines:
                parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                if len(parts) >= 5:
                    try:
                        elem_id = int(parts[0])
                        prop_id = int(parts[2])
                        topology = int(parts[4])

                        nodes = []
                        if i + 1 < n_lines:
                            nodes1 = FEMAPParser._parse_csv_line_fast(<str>block.lines[i + 1])
                            for nstr in nodes1:
                                n = int(nstr)
                                if n != 0:
                                    nodes.append(n)

                        if i + 2 < n_lines:
                            nodes2 = FEMAPParser._parse_csv_line_fast(<str>block.lines[i + 2])
                            for nstr in nodes2:
                                n = int(nstr)
                                if n != 0:
                                    nodes.append(n)

                        elements.append({
                            "id": elem_id,
                            "prop_id": prop_id,
                            "topology": topology,
                            "nodes": nodes,
                        })
                        i += 7
                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return elements

    cpdef tuple get_elements_arrays(self):
        """
        Extract all elements from Block 404 as NumPy arrays (high performance).

        Returns:
            Tuple of (element_ids, prop_ids, topologies, node_connectivity, offsets)
            - element_ids: np.ndarray[int32] - element IDs
            - prop_ids: np.ndarray[int32] - property IDs
            - topologies: np.ndarray[int32] - topology codes
            - connectivity: np.ndarray[int32] - flat node connectivity
            - offsets: np.ndarray[int32] - offsets into connectivity for each element
        """
        cdef list all_blocks, parts, nodes1, nodes2
        cdef list elem_ids_list = []
        cdef list prop_ids_list = []
        cdef list topo_list = []
        cdef list connectivity_list = []
        cdef list offsets_list = [0]
        cdef FEMAPBlock block
        cdef int i, elem_id, prop_id, topology, n_lines, n, offset

        all_blocks = self.get_blocks(404)
        offset = 0
        
        for block in all_blocks:
            i = 0
            n_lines = len(block.lines)
            while i < n_lines:
                parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                if len(parts) >= 5:
                    try:
                        elem_id = int(parts[0])
                        prop_id = int(parts[2])
                        topology = int(parts[4])

                        elem_ids_list.append(elem_id)
                        prop_ids_list.append(prop_id)
                        topo_list.append(topology)

                        if i + 1 < n_lines:
                            nodes1 = FEMAPParser._parse_csv_line_fast(<str>block.lines[i + 1])
                            for nstr in nodes1:
                                n = int(nstr)
                                if n != 0:
                                    connectivity_list.append(n)
                                    offset += 1

                        if i + 2 < n_lines:
                            nodes2 = FEMAPParser._parse_csv_line_fast(<str>block.lines[i + 2])
                            for nstr in nodes2:
                                n = int(nstr)
                                if n != 0:
                                    connectivity_list.append(n)
                                    offset += 1

                        offsets_list.append(offset)
                        i += 7
                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return (
            np.array(elem_ids_list, dtype=np.int32),
            np.array(prop_ids_list, dtype=np.int32),
            np.array(topo_list, dtype=np.int32),
            np.array(connectivity_list, dtype=np.int32),
            np.array(offsets_list, dtype=np.int32),
        )

    cpdef dict get_materials(self):
        """
        Extract all materials from Block 601.

        Returns:
            Dictionary mapping material IDs to material metadata
        """
        cdef dict materials = {}
        cdef list all_blocks, parts
        cdef FEMAPBlock block
        cdef int i, mat_id, n_lines

        all_blocks = self.get_blocks(601)
        for block in all_blocks:
            i = 0
            n_lines = len(block.lines)
            while i < n_lines:
                parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                if len(parts) >= 1:
                    try:
                        mat_id = int(parts[0])
                        materials[mat_id] = {"id": mat_id}
                        i += 1
                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return materials

    cpdef dict get_output_sets(self):
        """
        Extract all output sets from Block 450.

        Returns:
            Dictionary mapping output set IDs to metadata
        """
        cdef dict output_sets = {}
        cdef list all_blocks, parts, value_parts
        cdef FEMAPBlock block
        cdef int i, set_id, n_lines
        cdef str title
        cdef double value

        all_blocks = self.get_blocks(450)
        for block in all_blocks:
            i = 0
            n_lines = len(block.lines)
            while i < n_lines:
                parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                if len(parts) >= 1:
                    try:
                        set_id = int(parts[0])

                        title = ""
                        if i + 1 < n_lines:
                            title = (<str>block.lines[i + 1]).strip().rstrip(",")
                            if title == "<NULL>":
                                title = ""

                        value = 0.0
                        if i + 3 < n_lines:
                            value_parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i + 3])
                            if len(value_parts) >= 1:
                                value = float(value_parts[0])

                        output_sets[set_id] = {"title": title, "value": value}
                        i += 6
                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return output_sets

    cpdef list get_output_vectors(self):
        """
        Extract all output data vectors from Block 1051.

        Returns:
            List of output vector dictionaries with metadata and results
        """
        cdef list output_vectors = []
        cdef list all_blocks, parts, result_parts, cont_parts, values
        cdef list line6_parts
        cdef FEMAPBlock block
        cdef int i, set_id, vec_id, entity_id, start_id, end_id, entity_count
        cdef int n_lines, offset, ent_type_val
        cdef str title
        cdef double value
        cdef dict results
        cdef bint has_ent_type

        all_blocks = self.get_blocks(1051)
        for block in all_blocks:
            i = 0
            n_lines = len(block.lines)
            while i < n_lines:
                parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                if len(parts) >= 2:
                    try:
                        set_id = int(parts[0])
                        vec_id = int(parts[1])

                        title = ""
                        if i + 1 < n_lines:
                            title = (<str>block.lines[i + 1]).strip().rstrip(",")
                            if title == "<NULL>":
                                title = ""

                        ent_type_val = -1
                        has_ent_type = False
                        if i + 5 < n_lines:
                            line6_parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i + 5])
                            if len(line6_parts) >= 4:
                                ent_type_val = int(line6_parts[3])
                                has_ent_type = True

                        i += 7

                        results = {}
                        while i < n_lines:
                            result_parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])

                            if (len(result_parts) >= 2 and 
                                result_parts[0] == "-1" and 
                                result_parts[1] == "0."):
                                i += 1
                                break

                            if len(result_parts) == 2:
                                entity_id = int(result_parts[0])
                                value = float(result_parts[1])
                                results[entity_id] = value
                                i += 1

                            elif len(result_parts) > 2:
                                start_id = int(result_parts[0])
                                end_id = int(result_parts[1])
                                values = [float(v) for v in result_parts[2:]]

                                entity_count = end_id - start_id + 1
                                i += 1
                                while len(values) < entity_count and i < n_lines:
                                    cont_parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                                    if (len(cont_parts) >= 2 and 
                                        cont_parts[0] == "-1" and 
                                        cont_parts[1] == "0."):
                                        break
                                    values.extend([float(v) for v in cont_parts])
                                    i += 1

                                for offset in range(min(len(values), entity_count)):
                                    results[start_id + offset] = values[offset]
                            else:
                                i += 1

                        output_vectors.append({
                            "set_id": set_id,
                            "vec_id": vec_id,
                            "title": title,
                            "ent_type": ent_type_val if has_ent_type else None,
                            "results": results,
                        })

                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return output_vectors

    cpdef tuple get_output_vectors_arrays(self, int set_id_filter=-1, int vec_id_filter=-1):
        """
        Extract output vectors as NumPy arrays (high performance).
        
        Args:
            set_id_filter: If >= 0, only extract vectors with this set_id
            vec_id_filter: If >= 0, only extract vectors with this vec_id
        
        Returns:
            Tuple of (entity_ids: np.ndarray[int32], values: np.ndarray[float64], 
                      set_id: int, vec_id: int, ent_type: int) for the first matching vector
            Returns (None, None, -1, -1, -1) if no matching vectors found
        """
        cdef list all_blocks, parts, result_parts, cont_parts, values
        cdef list line6_parts
        cdef list entity_ids_list, values_list
        cdef FEMAPBlock block
        cdef int i, set_id, vec_id, entity_id, start_id, end_id, entity_count
        cdef int n_lines, offset, ent_type_val
        cdef double value
        cdef bint has_ent_type

        all_blocks = self.get_blocks(1051)
        for block in all_blocks:
            i = 0
            n_lines = len(block.lines)
            while i < n_lines:
                parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                if len(parts) >= 2:
                    try:
                        set_id = int(parts[0])
                        vec_id = int(parts[1])

                        # Check filters
                        if set_id_filter >= 0 and set_id != set_id_filter:
                            i += 7
                            # Skip to end marker
                            while i < n_lines:
                                result_parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                                i += 1
                                if (len(result_parts) >= 2 and 
                                    result_parts[0] == "-1" and 
                                    result_parts[1] == "0."):
                                    break
                            continue
                            
                        if vec_id_filter >= 0 and vec_id != vec_id_filter:
                            i += 7
                            while i < n_lines:
                                result_parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                                i += 1
                                if (len(result_parts) >= 2 and 
                                    result_parts[0] == "-1" and 
                                    result_parts[1] == "0."):
                                    break
                            continue

                        ent_type_val = -1
                        has_ent_type = False
                        if i + 5 < n_lines:
                            line6_parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i + 5])
                            if len(line6_parts) >= 4:
                                ent_type_val = int(line6_parts[3])
                                has_ent_type = True

                        i += 7

                        entity_ids_list = []
                        values_list = []
                        
                        while i < n_lines:
                            result_parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])

                            if (len(result_parts) >= 2 and 
                                result_parts[0] == "-1" and 
                                result_parts[1] == "0."):
                                i += 1
                                break

                            if len(result_parts) == 2:
                                entity_id = int(result_parts[0])
                                value = float(result_parts[1])
                                entity_ids_list.append(entity_id)
                                values_list.append(value)
                                i += 1

                            elif len(result_parts) > 2:
                                start_id = int(result_parts[0])
                                end_id = int(result_parts[1])
                                values = [float(v) for v in result_parts[2:]]

                                entity_count = end_id - start_id + 1
                                i += 1
                                while len(values) < entity_count and i < n_lines:
                                    cont_parts = FEMAPParser._parse_csv_line_fast(<str>block.lines[i])
                                    if (len(cont_parts) >= 2 and 
                                        cont_parts[0] == "-1" and 
                                        cont_parts[1] == "0."):
                                        break
                                    values.extend([float(v) for v in cont_parts])
                                    i += 1

                                for offset in range(min(len(values), entity_count)):
                                    entity_ids_list.append(start_id + offset)
                                    values_list.append(values[offset])
                            else:
                                i += 1

                        return (
                            np.array(entity_ids_list, dtype=np.int32),
                            np.array(values_list, dtype=np.float64),
                            set_id,
                            vec_id,
                            ent_type_val if has_ent_type else -1
                        )

                    except (ValueError, IndexError):
                        i += 1
                else:
                    i += 1

        return (None, None, -1, -1, -1)
