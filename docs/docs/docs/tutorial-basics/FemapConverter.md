---
sidebar_position: 3
title: Convert FEMAP Files
---

After running an EMSolution simulation, the result files need to be converted to VTK format before they can be used in VTK-based visualization workflows.

This conversion is not a one-time step. Each time new simulation results are generated, the converter should be run again so the VTK output matches the latest data.

<img src="/pyemsi/img/femap-converter-dialog.png" alt="femap-converter-dialog" width="300" />

For the programmatic API and the full converter reference, see [FemapConverter](/docs/api/FemapConverter).

## Open The FEMAP Converter

Open the converter from:

- `File -> Convert FEMAP`

The converter opens as a dialog where you choose the input files, output location, and conversion options. When you click `Run`, pyemsi launches the conversion in the External Terminal so progress can be monitored without blocking the rest of the GUI.

Or click on <img src="/pyemsi/img/VTK.svg" alt="Run icon" width="20"/> icon on the main toolbar.

## Dialog Inputs

The FEMAP converter dialog is built around one required input directory and a set of required or optional FEMAP-related files.

| Field | Required | Description |
| --- | --- | --- |
| `Input Directory` | Yes | The folder containing the FEMAP neutral mesh file and the EMSolution result files to convert. Relative paths in the dialog are resolved from this folder. |
| `Output Directory` | Yes | The folder where converted VTK files will be written. The default is `.pyemsi`. If a relative path is used, it is resolved from the input directory. |
| `Output Name` | Yes | The base name of the generated output. The default is `output`. This name is used for the main `.pvd` file and the generated VTK output folder. |
| `Mesh File` | Yes | The FEMAP mesh file to convert. The default is `post_geom`. This file must exist. |
| `Force 2D` | No | Converts supported 3D element types to 2D equivalents. Use this when a 2D-style representation is needed from the source mesh, such as electric machines. |
| `ASCII Mode` | No | Writes VTK output in ASCII format instead of binary. Binary output is usually smaller and faster; ASCII can be useful for inspection or debugging. |
| `Displacement` | Optional | Displacement data file. Enabled by default with the conventional name `disp`. Disable it if displacement data is not available. |
| `Magnetic` | Optional | Magnetic field data file. Enabled by default with the conventional name `magnetic`. |
| `Current` | Optional | Current density data file. Enabled by default with the conventional name `current`. |
| `Force` | Optional | Nodal force data file. Enabled by default with the conventional name `force`. |
| `Force J x B` | Optional | Lorentz force data file. Enabled by default with the conventional name `force_J_B`. |
| `Heat` | Optional | Heat or thermal data file. Enabled by default with the conventional name `heat`. |

### Notes About File Selection

- Required files must exist before the conversion can start.
- Optional files can be disabled if that category of result data is not available.
- Relative file paths are resolved from the selected input directory.
- pyemsi can reuse the last-used converter settings and applies workspace-aware defaults when available.

## What The Converter Produces

The converter generates VTK output that can be used by pyemsi, PyVista, or ParaView.

### Main Output File

The primary output is a PVD collection file:

- `{output_dir}/{output_name}.pvd`

This file represents the converted time series and is typically the main entry point for loading the result set.

### Time-Step Output Folder

The converter also creates a folder containing the time-step datasets:

- `{output_dir}/{output_name}/`

Inside that folder, pyemsi writes the VTK multiblock and unstructured-grid files for the converted mesh and field data.

## Overwriting Existing Output

If converted output with the same output directory and output name already exists, pyemsi asks for confirmation before deleting the old converted files and creating new ones.

This is expected when you rerun the conversion after a new simulation.

## After Conversion

Once conversion finishes, the generated VTK output can be used for visualization workflows such as:

- field plotting inside pyemsi
- loading the generated `.pvd` file in ParaView
- using the [Plotter](/docs/api/Plotter) API for PyVista-based inspection
