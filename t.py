# from pyemsi import FEMAPToVTMConverter

# # Create converter
# # converter = FEMAPToVTMConverter("tests/post_geom_single_hex")
# converter = FEMAPToVTMConverter(r"C:\Users\eskan\OneDrive\Desktop\delme\Trans_Voltage\post_geom")

# # # Parse FEMAP file
# # converter.parse_femap()

# # # Inspect parsed data
# # print(f"Nodes: {len(converter.nodes)}")
# # print(f"Elements: {len(converter.elements)}")
# # print(f"Properties: {len(converter.properties)}")

# # # Validate data
# # messages = converter.validate()
# # for msg in messages:
# #     print(msg)

# # Convert to VTK MultiBlock UnstructuredGrid (one block per property)
# multiblock = converter.write_vtm("output.vtm")


import pyvista as pv

msh = pv.read("output.vtm")
p = pv.Plotter()
for i, block in enumerate(msh):
    p.add_mesh(block, show_edges=True, opacity=0.5, label=f"block_{i}")
p.add_legend()
p.reset_camera()
p.show(title="All blocks in one scene")



# import pyvista as pv
# import numpy as np

# # Create a simple multiblock dataset
# multiblock = pv.MultiBlock()

# # Block 1: A simple cube (hexahedron)
# points_cube = np.array([
#     [0, 0, 0],
#     [1, 0, 0],
#     [1, 1, 0],
#     [0, 1, 0],
#     [0, 0, 1],
#     [1, 0, 1],
#     [1, 1, 1],
#     [0, 1, 1],
# ])
# cells_cube = np.array([8, 0, 1, 2, 3, 4, 5, 6, 7])
# cell_types_cube = np.array([pv.CellType.HEXAHEDRON])
# cube = pv.UnstructuredGrid(cells_cube, cell_types_cube, points_cube)

# # Block 2: A simple tetrahedron
# points_tet = np.array([
#     [2, 0, 0],
#     [3, 0, 0],
#     [2.5, 1, 0],
#     [2.5, 0.5, 1],
# ])
# cells_tet = np.array([4, 0, 1, 2, 3])
# cell_types_tet = np.array([pv.CellType.TETRA])
# tet = pv.UnstructuredGrid(cells_tet, cell_types_tet, points_tet)

# # Block 3: A simple wedge (prism)
# points_wedge = np.array([
#     [0, 2, 0],
#     [1, 2, 0],
#     [0.5, 3, 0],
#     [0, 2, 1],
#     [1, 2, 1],
#     [0.5, 3, 1],
# ])
# cells_wedge = np.array([6, 0, 1, 2, 3, 4, 5])
# cell_types_wedge = np.array([pv.CellType.WEDGE])
# wedge = pv.UnstructuredGrid(cells_wedge, cell_types_wedge, points_wedge)

# # Add blocks to multiblock dataset
# multiblock.append(cube, "Cube")
# multiblock.append(tet, "Tetrahedron")
# multiblock.append(wedge, "Wedge")

# # Save as VTM file
# multiblock.save("simple_multiblock.vtm",binary=False)
# print("Saved multiblock dataset to simple_multiblock.vtm")

# # Visualize the multiblock dataset
# msh = pv.read("simple_multiblock.vtm")
# p = pv.Plotter()

# colors = ["red", "green", "blue"]
# for i, block in enumerate(msh):
#     p.add_mesh(block, show_edges=True, opacity=0.8,
#                label=msh.get_block_name(i), color=colors[i])

# p.add_legend()
# p.reset_camera()
# p.show(title="Simple MultiBlock UnstructuredGrid")