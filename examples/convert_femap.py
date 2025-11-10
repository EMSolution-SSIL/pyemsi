#!/usr/bin/env python3
"""
Example script demonstrating FEMAP to VTU conversion.

This script shows how to convert a FEMAP Neutral file to VTK format
for visualization in ParaView.
"""

import sys
import os

# Add parent directory to path to import pyemsi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyemsi import convert_femap_to_vtu, FEMAPToVTUConverter


def simple_conversion(input_file, output_file):
    """
    Simple one-liner conversion using the convenience function.

    Args:
        input_file: Path to FEMAP Neutral file
        output_file: Path for output VTU file
    """
    print("=" * 60)
    print("Simple Conversion Example")
    print("=" * 60)

    convert_femap_to_vtu(input_file, output_file, validate=True)

    print(f"\nDone! Open '{output_file}' in ParaView to visualize.")


def detailed_conversion(input_file, output_file):
    """
    Detailed conversion showing intermediate steps and data inspection.

    Args:
        input_file: Path to FEMAP Neutral file
        output_file: Path for output VTU file
    """
    print("=" * 60)
    print("Detailed Conversion Example")
    print("=" * 60)

    # Create converter
    converter = FEMAPToVTUConverter(input_file)

    # Parse FEMAP file
    print("\n1. Parsing FEMAP file...")
    converter.parse_femap()

    # Display parsed data summary
    print(f"\n2. Data Summary:")
    print(f"   - Nodes: {len(converter.nodes)}")
    print(f"   - Elements: {len(converter.elements)}")
    print(f"   - Properties: {len(converter.properties)}")
    print(f"   - Materials: {len(converter.materials)}")

    if converter.header:
        print(f"   - FEMAP Version: {converter.header.get('version')}")
        if converter.header.get('title'):
            print(f"   - Title: {converter.header.get('title')}")

    # Display element types
    print(f"\n3. Element Types:")
    topology_counts = {}
    for elem in converter.elements:
        topo = elem['topology']
        topology_counts[topo] = topology_counts.get(topo, 0) + 1

    topology_names = {
        0: "Line2", 2: "Tri3", 3: "Tri6", 4: "Quad4", 5: "Quad8",
        6: "Tetra4", 7: "Wedge6", 8: "Brick8", 9: "Point",
        10: "Tetra10", 11: "Wedge15", 12: "Brick20"
    }

    for topo, count in sorted(topology_counts.items()):
        name = topology_names.get(topo, f"Unknown({topo})")
        print(f"   - {name}: {count} elements")

    # Display property information
    print(f"\n4. Properties:")
    for prop_id, prop_data in sorted(converter.properties.items()):
        title = prop_data.get('title', '<no title>')
        mat_id = prop_data.get('material_id', 'N/A')
        print(f"   - Property {prop_id}: '{title}' (Material {mat_id})")

    # Validate
    print(f"\n5. Validating...")
    messages = converter.validate()
    if messages:
        print("   Validation messages:")
        for msg in messages:
            print(f"   {msg}")
    else:
        print("   No validation issues found")

    # Build VTK grid
    print(f"\n6. Building VTK Unstructured Grid...")
    ug = converter.build_unstructured_grid()
    print(f"   - VTK Points: {ug.GetNumberOfPoints()}")
    print(f"   - VTK Cells: {ug.GetNumberOfCells()}")

    # Add cell data
    print(f"\n7. Adding cell data arrays...")
    converter.add_cell_data(ug)

    # Write output
    print(f"\n8. Writing VTU file: {output_file}")
    from vtk import vtkXMLUnstructuredGridWriter
    writer = vtkXMLUnstructuredGridWriter()
    writer.SetFileName(output_file)
    writer.SetInputData(ug)
    writer.Write()

    print(f"\nConversion complete!")
    print(f"\nTo visualize in ParaView:")
    print(f"  1. Open ParaView")
    print(f"  2. File > Open > {output_file}")
    print(f"  3. Click 'Apply' in the Properties panel")
    print(f"  4. Color by 'PropertyID' or 'MaterialID'")


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python convert_femap.py <input.neu> <output.vtu> [--detailed]")
        print("\nOptions:")
        print("  --detailed    Show detailed conversion steps")
        print("\nExample:")
        print("  python convert_femap.py mesh.neu mesh.vtu")
        print("  python convert_femap.py mesh.neu mesh.vtu --detailed")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    detailed = "--detailed" in sys.argv

    # Check input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    # Run conversion
    try:
        if detailed:
            detailed_conversion(input_file, output_file)
        else:
            simple_conversion(input_file, output_file)
    except Exception as e:
        print(f"\nERROR: Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
