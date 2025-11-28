from pyemsi import FemapConverter
import pyvista as pv

# Create converter
# converter = FemapConverter("tests/post_geom_single_hex")
converter = FemapConverter(r"C:\Users\eskan\OneDrive\Desktop\delme\Trans_Voltage\post_geom")
converter.parse_femap()
converter.build_mesh()
converter.append_data(r"C:\Users\eskan\OneDrive\Desktop\delme\Trans_Voltage\magnetic")
converter.write_pvd()

# # Parse FEMAP file
# converter.parse_femap()

# # Inspect parsed data
# print(f"Nodes: {len(converter.nodes)}")
# print(f"Elements: {len(converter.elements)}")
# print(f"Properties: {len(converter.properties)}")

# # Validate data
# messages = converter.validate()
# for msg in messages:
#     print(msg)

# Convert to VTK MultiBlock UnstructuredGrid (one block per property)
# multiblock = converter.write_vtm(".pyemsi/output.vtm")
# p = pv.Plotter()
# for i, block in enumerate(multiblock):
#     p.add_mesh(block, show_edges=True, opacity=0.5, label=f"block_{i}")
# p.add_legend()
# p.reset_camera()
# p.show(title="All blocks in one scene")


# import pyvista as pv

# msh = pv.read("output.vtm")
# p = pv.Plotter()
# for i, block in enumerate(msh):
#     p.add_mesh(block, show_edges=True, opacity=0.5, label=f"block_{i}")
# p.add_legend()
# p.reset_camera()
# p.show(title="All blocks in one scene")



