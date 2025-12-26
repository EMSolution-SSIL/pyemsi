---
sidebar_position: 2
title: FemapConverter
---

`FemapConverter` converts EMSolution's FEMAP Neutral files to VTK MultiBlock UnstructuredGrid format for visualization in ParaView or with PyVista.

### Conversion Pipeline

The converter executes a four-stage pipeline:

1. **Build Mesh** — Parses the FEMAP neutral mesh file and creates a VTK unstructured grid
2. **Parse Data Files** — Reads all configured physics data files (magnetic, current, force, etc.) in parallel
3. **Initialize PVD** — Creates a PVD collection file that references all time steps
4. **Time Stepping** — Generates individual VTM files for each time step with all field data

### Initialization

```python
from pyemsi import FemapConverter

converter = FemapConverter(
    input_dir,
    output_dir="./.pyemsi",
    output_name="output",
    force_2d=False,
    ascii_mode=False,
    mesh="post_geom",
    magnetic="magnetic",
    current="current",
    force="force",
    force_J_B="force_J_B",
    heat="heat",
    displacement="disp"
)
```

#### Parameters

- **`input_dir`** (`str | Path`, required) — Directory containing FEMAP neutral files
- **`output_dir`** (`str | Path`, default: `"./.pyemsi"`) — Directory where VTK output files will be written
- **`output_name`** (`str`, default: `"output"`) — Base name for output files (PVD file and VTM folder)
- **`force_2d`** (`bool`, default: `False`) — Convert 3D elements to 2D equivalents (Hex8→Quad4, Hex20→Quad8, Wedge6→Tri3, Wedge15→Tri6)
- **`ascii_mode`** (`bool`, default: `False`) — Write VTK files in ASCII format instead of binary
- **`mesh`** (`str | Path`, default: `"post_geom"`) — Path to mesh file, relative to `input_dir` or absolute
- **`magnetic`** (`str | Path | None`, default: `"magnetic"`) — Path to magnetic field data file, or `None` to skip
- **`current`** (`str | Path | None`, default: `"current"`) — Path to current density data file, or `None` to skip
- **`force`** (`str | Path | None`, default: `"force"`) — Path to nodal force data file, or `None` to skip
- **`force_J_B`** (`str | Path | None`, default: `"force_J_B"`) — Path to Lorentz force data file, or `None` to skip
- **`heat`** (`str | Path | None`, default: `"heat"`) — Path to heat/thermal data file, or `None` to skip
- **`displacement`** (`str | Path`, default: `"disp"`) — Path to displacement data file, or `None` to skip

### Running the Conversion

Call the `run()` method to execute the complete conversion pipeline:

```python
converter.run()
```

The `run()` method:
- Returns `None`
- Writes all output files to disk at the specified `output_dir`
- Executes all four pipeline stages automatically
- Uses parallel processing for data file parsing and time step generation

### Output Structure

The converter generates the following files:

#### PVD Collection File

Location: `{output_dir}/{output_name}.pvd`

An XML collection file that references all time steps. Open this file in ParaView to view animations and time-series data.

#### VTM Multiblock Files

Location: `{output_dir}/{output_name}/`

Individual VTM (VTK MultiBlock) files for each time step, containing:
- Mesh geometry organized by PropertyID (material/component)
- All physics field data for that time step

#### PVD → VTM → VTU hierarchy (time series + data tree)

`*.pvd` is a lightweight **time-series index** (a VTK “Collection” XML file). It does not contain mesh geometry; instead it lists time steps and the file to load for each time.

In `pyemsi`, each time step points to a `*.vtm` file, and each `*.vtm` file (VTK MultiBlock dataset) references multiple `*.vtu` files (VTK UnstructuredGrid) that contain the actual geometry and field arrays.

**On-disk tree** (what the converter writes):

```
{output_dir}/
    {output_name}.pvd
    {output_name}/
        STEP1 Time ... .vtm
        STEP1 Time ... /
            STEP1 Time ..._0.vtu
            STEP1 Time ..._1.vtu
            ...
        STEP2 Time ... .vtm
        STEP2 Time ... /
            ...
```

**PVD structure** (index of time steps):

```xml
<VTKFile type="Collection" ...>
    <Collection>
        <DataSet timestep="0.01" part="0" file="{output_name}/STEP1 Time 1.00000e-02.vtm"/>
        <DataSet timestep="0.02" part="0" file="{output_name}/STEP2 Time 2.00000e-02.vtm"/>
        ...
    </Collection>
</VTKFile>
```

**VTM structure** (a multiblock “tree” whose leaves are VTU files):

```xml
<VTKFile type="vtkMultiBlockDataSet" ...>
    <vtkMultiBlockDataSet>
        <DataSet index="0" name="10" file="STEP1 Time .../STEP1 Time ..._0.vtu"/>
        <DataSet index="1" name="20" file="STEP1 Time .../STEP1 Time ..._1.vtu"/>
        ...
    </vtkMultiBlockDataSet>
</VTKFile>
```

In this project, the multiblock `name` corresponds to the **PropertyID** used to split the mesh into blocks. In ParaView, those names show up in the *MultiBlock Inspector*, and in PyVista they show up as multiblock keys.

#### ParaView + PyVista support

- **ParaView**: open `{output_name}.pvd` to get the full time series (animation timeline driven by the `timestep=` values). Each time step loads the corresponding `*.vtm`, and the multiblock tree exposes each PropertyID block (each backed by a `*.vtu`).
- **PyVista**: read the time series with `pyvista.get_reader()` (returns a `PVDReader` for `.pvd`). Example:

```python
import pyvista as pv

reader = pv.get_reader(".pyemsi/output.pvd")
print(reader.time_values)          # available time values
reader.set_active_time_value(0.02) # or set_active_time_point(i)
multiblock = reader.read()[0]      # a MultiBlock for that time step

# Access blocks by index/name and plot
print(multiblock.keys())
multiblock.plot()
```

#### Field Data

The converter adds the following field data to meshes based on configured data files:

**Displacement** (modifies mesh geometry):
- Applies displacement vectors to mesh points

**Magnetic** (from `magnetic` file):
- Point data: `B-Vec (T)`, `B-Mag (T)`, `Flux (A/m)` (optional)
- Cell data: `B-Vec (T)`, `B-Mag (T)`

**Current** (from `current` file):
- Point data: `J-Vec (A/m^2)`, `J-Mag (A/m^2)`, `Loss (W/m^3)`
- Cell data: `J-Vec (A/m^2)`, `J-Mag (A/m^2)`, `Loss (W/m^3)`

**Force** (from `force` file):
- Point data: `F Nodal-Vec (N/m^3)`, `F Nodal-Mag (N/m^3)`
- Cell data: `F Nodal-Vec (N/m^3)`, `F Nodal-Mag (N/m^3)`

**Lorentz Force** (from `force_J_B` file):
- Point data: `F Lorents-Vec (N/m^3)`, `F Lorents-Mag (N/m^3)`
- Cell data: `F Lorents-Vec (N/m^3)`, `F Lorents-Mag (N/m^3)`

**Heat** (from `heat` file):
- Point data: `Heat Density (W/m^3)`, `Heat (W)`
- Cell data: `Heat Density (W/m^3)`, `Heat (W)`

### Usage Example

```python
from pyemsi import FemapConverter

# Basic conversion with default settings
converter = FemapConverter(r"C:\path\to\femap\files")
converter.run()

# Skip current density processing
converter = FemapConverter(
    r"C:\path\to\femap\files",
    output_name="my_simulation",
    current=None
)
converter.run()

# Force 2D mode for planar meshes
converter = FemapConverter(
    r"C:\path\to\femap\files",
    force_2d=True
)
converter.run()
```

The output can be visualized with the `Plotter` class or opened directly in ParaView:

```python
from pyemsi import Plotter

# Visualize the results
plotter = Plotter(".pyemsi/output.pvd")
plotter.set_scalar("B-Mag (T)", mode="element", cell2point=True)
plotter.show()
```
