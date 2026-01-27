# cython: language_level=3
"""
FEMAP Parser Cython Declaration File

This .pxd file allows other Cython modules to cimport the optimized classes
for maximum performance when extending the parser.
"""

cimport numpy as np


cdef class FEMAPBlock:
    cdef public int block_id
    cdef public list lines


cdef class FEMAPParser:
    cdef str filepath
    cdef public dict blocks
    cdef str BLOCK_DELIMITER
    
    cdef void _parse(self)
    
    @staticmethod
    cdef list _parse_csv_line_fast(str line)
    
    cpdef dict parse(self)
    cpdef list get_blocks(self, int block_id)
    cpdef dict get_header(self)
    cpdef dict get_nodes(self, bint force_2d=*)
    cpdef tuple get_nodes_arrays(self)
    cpdef dict get_properties(self)
    cpdef list get_elements(self)
    cpdef tuple get_elements_arrays(self)
    cpdef dict get_materials(self)
    cpdef dict get_output_sets(self)
    cpdef list get_output_vectors(self)
    cpdef tuple get_output_vectors_arrays(self, int set_id_filter=*, int vec_id_filter=*)
