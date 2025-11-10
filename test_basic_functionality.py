#!/usr/bin/env python3
"""
Quick test script to demonstrate basic functionality without VTK.
"""

from pyemsi import FEMAPParser
import os

# Test with simple mesh
test_file = r"C:\Users\eskan\OneDrive\Desktop\delme\Trans_Voltage\post_geom"

print("=" * 60)
print("Testing FEMAP Parser")
print("=" * 60)

# Create parser
parser = FEMAPParser(test_file)
print(f"\nParsing file: {test_file}")

# Parse the file
blocks = parser.parse()
print(f"Found {len(blocks)} different block types")

# Extract data
header = parser.get_header()
nodes = parser.get_nodes()
elements = parser.get_elements()
properties = parser.get_properties()
materials = parser.get_materials()

print("\n--- Header ---")
print(f"Version: {header['version']}")
print(f"Title: {header['title'] or '(empty)'}")

print("\n--- Nodes ---")
print(f"Total nodes: {len(nodes)}")
for node_id in sorted(list(nodes.keys()))[:3]:
    x, y, z = nodes[node_id]
    print(f"  Node {node_id}: ({x}, {y}, {z})")
if len(nodes) > 3:
    print(f"  ... and {len(nodes) - 3} more")

print("\n--- Elements ---")
print(f"Total elements: {len(elements)}")
for elem in elements[:3]:
    print(f"  Element {elem['id']}: topology={elem['topology']}, "
          f"prop_id={elem['prop_id']}, nodes={len(elem['nodes'])}")
if len(elements) > 3:
    print(f"  ... and {len(elements) - 3} more")

print("\n--- Properties ---")
print(f"Total properties: {len(properties)}")
for prop_id, prop_data in properties.items():
    print(f"  Property {prop_id}: '{prop_data['title']}' (Material {prop_data['material_id']})")

print("\n--- Materials ---")
print(f"Total materials: {len(materials)}")
for mat_id in materials:
    print(f"  Material {mat_id}")

print("\n" + "=" * 60)
print("Parser test complete!")
print("=" * 60)

# Test with mixed elements
test_file2 = os.path.join('tests', 'fixtures', 'mixed_elements.neu')

print(f"\nParsing file: {test_file2}")
parser2 = FEMAPParser(test_file2)
parser2.parse()

elements2 = parser2.get_elements()
print(f"Found {len(elements2)} elements with mixed types:")

topology_names = {
    0: "Line2", 2: "Tri3", 3: "Tri6", 4: "Quad4", 5: "Quad8",
    6: "Tetra4", 7: "Wedge6", 8: "Brick8", 9: "Point",
    10: "Tetra10", 11: "Wedge15", 12: "Brick20"
}

topology_counts = {}
for elem in elements2:
    topo = elem['topology']
    topology_counts[topo] = topology_counts.get(topo, 0) + 1

for topo, count in sorted(topology_counts.items()):
    name = topology_names.get(topo, f"Unknown({topo})")
    print(f"  {name}: {count} element(s)")

print("\n[OK] All basic functionality tests passed!")
