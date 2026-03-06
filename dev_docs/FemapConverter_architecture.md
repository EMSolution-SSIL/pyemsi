# FemapConverter Architecture

## Overview

The `FemapConverter` class implements a modular pipeline for converting FEMAP Neutral files to VTK MultiBlock format with support for time-stepped result data.

## Pipeline Strategy

### Manual Execution

The conversion pipeline runs when you explicitly call the `run()` method:

```python
converter = FemapConverter(
    input_dir="project",
    output_dir=".pyemsi",
    output_name="transient_run",
    mesh="post_geom",
    displacement="disp",
    magnetic="magnetic",
    # ... other optional files
)

# Execute the pipeline manually:
converter.run()
# This runs:
# 1. _build_mesh() - loads FEMAP neutral file, builds VTK UnstructuredGrid
# 2. parse_data_files() - parses result files in parallel
# 3. init_pvd() - creates PVD index file
# 4. time_stepping() - writes VTM files for each time step
```

### Stored Parameters

The `FemapConverter` constructor stores mesh file and conversion parameters internally for use by the `run()` method:
- `self._mesh_file` - Path to FEMAP neutral file
- `self._force_2d` - Whether to apply 2D topology mapping

## Pipeline Stages

### 1. `_build_mesh(mesh_file, force_2d=False)`

**Purpose**: Load FEMAP Neutral file and create a PyVista UnstructuredGrid.

**Process**:
- Calls `FEMAPParser` to parse blocks 100/403/404
- Creates VTK points from node coordinates
- Maintains `femap_to_vtk_id` mapping for nodal vector interpolation
- Creates single `vtkUnstructuredGrid` with elements grouped by connectivity
- Applies `force_2d` topology mapping if enabled
- Stores `elements_map` to track FEMAP element ID → VTK cell index
- Extracts unique `PropertyID` values for MultiBlock grouping

**Output**: 
- `self.mesh` - PyVista UnstructuredGrid
- `self.init_points` - Copy of initial node positions (preserved for displacement)
- `self.elements_map` - Dictionary of FEMAP element ID → VTK cell index
- `self.femap_to_vtk_id` - Dictionary of FEMAP node ID → VTK point index
- `self.unique_props` - NumPy array of unique property IDs

### 2. `parse_data_files()`

**Purpose**: Parse all configured FEMAP result files in parallel.

**Process**:
- Iterates over file map: displacement, magnetic, current, force, force_J_B, heat
- Spawns one thread per active file
- Each thread calls `parse_data_file()` which:
  - Calls `FEMAPParser` on the file
  - Extracts output sets (time steps)
  - Caches output vectors with set ID mapping
- Waits for all threads to complete

**Output**:
- `self.sets` - Dictionary of time step ID → {value, title}
- `self.vectors` - Dictionary of channel name → list of vector records

**Thread Safety**: Each parse operation is independent; `self.sets` is populated only from first file with results.

### 3. `init_pvd()`

**Purpose**: Create a PVD (ParaView Data Format) index file.

**Process**:
- Checks if output folder exists; skips if already initialized
- Creates output folder at `self.output_folder`
- Generates XML index file listing each time step and corresponding VTM file
- Writes to `self.pvd_file`

**Output**:
- `<output_name>.pvd` - XML index file
- `<output_dir>/<output_name>/` - Output directory for VTM files

**ParaView Integration**: Open the `.pvd` file in ParaView to animate the time series.

### 4. `time_stepping()`

**Purpose**: Process each time step and write individual VTM files.

**Process**:
- Spawns one thread per time step
- Each thread calls `_process_time_step(step, vtm_path)` which:
  - Creates a mesh copy for thread safety
  - Applies displacement field (updates mesh points)
  - Adds magnetic field data (point & cell data)
  - Adds current field data (point & cell data)
  - Adds force field data (point & cell data)
  - Adds Lorentz force data (point & cell data)
  - Adds heat field data (point & cell data)
  - Writes mesh to VTM file grouped by PropertyID
- Waits for all threads to complete

**Output**:
- `<output_dir>/<output_name>/<sanitized_title>.vtm` - One file per time step

**Thread Safety**: Each thread works on an independent mesh copy; shared read-only data (maps, vectors) are safe to access.

## Key Classes and Data Structures

### `FemapConverter`

**Instance Attributes**:
- `input_dir`, `output_dir`, `output_name` - File paths
- `mesh` - PyVista UnstructuredGrid
- `init_points` - NumPy array of initial node positions
- `sets` - Dictionary: `{step_id: {value: float, title: str}}`
- `vectors` - Dictionary: `{channel_name: [{set_id, ent_type, title, vec_id, results}, ...]}`
- `elements_map` - Dictionary: `{femap_elem_id: vtk_cell_idx}`
- `femap_to_vtk_id` - Dictionary: `{femap_node_id: vtk_point_idx}`
- `unique_props` - NumPy array of unique PropertyID values
- `_mesh_file`, `_force_2d` - Stored parameters for manual `run()` calls

**Methods**:
- `__init__()` - Initialize and run pipeline
- `run()` - Manually execute the full pipeline
- `_build_mesh()` - Load FEMAP file and create mesh
- `parse_data_files()` - Parse result files in parallel
- `init_pvd()` - Create PVD index file
- `time_stepping()` - Process and write time steps
- `_process_time_step()` - Process a single time step
- `_process_*_field()` - Field-specific processing methods
- `get_data_array()` - Extract vectors for a given time step
- `_vtu_to_vtm()` - Convert UnstructuredGrid to MultiBlock by PropertyID
- `_write_vtm_file()` - Write VTM file with optional ASCII mode

## Data Flow Diagram

```
Input Files
    ├── FEMAP Neutral (post_geom)
    │   └── [Block 100, 403, 404, 402, 601]
    │       └── FEMAPParser
    │           └── _build_mesh()
    │               ├── nodes → PyVista Points
    │               ├── elements → VTK UnstructuredGrid
    │               └── property_ids → cell_data["PropertyID"]
    │
    ├── Result Files (magnetic, current, etc.)
    │   ├── [Block 100, 1051, 402, 603, 604]
    │   ├── [Block 100, 1051, 402, 603, 604]
    │   └── ... (in parallel)
    │       └── FEMAPParser
    │           └── parse_data_files()
    │               ├── output_sets → self.sets
    │               └── output_vectors → self.vectors
    │
    └── Processing
        ├── init_pvd()
        │   └── <output_name>.pvd
        │
        └── time_stepping()
            ├── _process_displacement_field()
            │   └── mesh.points += displacement
            ├── _process_magnetic_field()
            │   └── mesh.point_data["B-Vec (T)"] = ...
            ├── _process_current_field()
            │   └── mesh.cell_data["J-Mag (A/m^2)"] = ...
            ├── ... (other fields)
            └── _write_vtm_file()
                └── <output_dir>/<output_name>/<title>.vtm
```

## Threading Model

**File Parsing**: 
- Up to 6 threads (one per data file channel)
- Completely independent operations
- No synchronization needed until all complete

**Time Stepping**:
- Up to N threads (one per time step)
- Each thread works on an independent mesh copy
- Shared read-only data (vectors, maps) are thread-safe

## Performance Considerations

1. **Parallel Parsing**: Result files are parsed in parallel for faster initialization.
2. **Mesh Copy**: Each time step gets its own mesh copy to avoid thread-safety issues.
3. **Point Updates**: Displacement field modifies mesh.points in-place per time step.
4. **Cell Data Grouping**: MultiBlock grouping by PropertyID enables selective rendering in ParaView.

## Future Extensions

- CLI tool for batch conversions
- Streaming output for very large meshes
- Custom field processing callbacks
- Result filtering/decimation for large time series
- HDF5 output format option
