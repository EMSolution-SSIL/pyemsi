---
sidebar_position: 2
title: General Tools
---

The General Tools toolbar controls scene-wide display aids and plot presentation. These actions do not change the underlying result data. Instead, they help you read, annotate, and manage what is visible in the current viewport.

## Main Actions

| Control | Description |
| --- | --- |
| <img src="/pyemsi/img/Settings.svg" alt="Settings" width="20"/> `Settings` | Open the display settings for the current plot view. |
| <img src="/pyemsi/img/Screenshot.svg" alt="Screenshot" width="20"/> `Screenshot to Clipboard` | Copy the current rendered viewport directly to the system clipboard. |
| <img src="/pyemsi/img/Axes.svg" alt="Axes" width="20"/> `Axes` | Toggle the orientation axes widget. |
| <img src="/pyemsi/img/CenterAxes.svg" alt="Axes at origin" width="20"/> `Axes at Origin` | Toggle an axes actor placed at the model origin. |
| <img src="/pyemsi/img/Grid.svg" alt="Grid" width="20"/> `Grid` | Toggle the grid and labeled axes around the visible scene. |
| <img src="/pyemsi/img/CameraOrientation.svg" alt="Camera orientation" width="20"/> `Camera Orientation` | Toggle the interactive camera orientation widget. |
| <img src="/pyemsi/img/Blocks.svg" alt="Blocks" width="20"/> `Blocks` | Open block-visibility controls for multi-block results. |
| <img src="/pyemsi/img/EditScalarBar.svg" alt="Scalar bars" width="20"/> `Scalar Bars` | Open scalar-bar appearance controls. |
| <img src="/pyemsi/img/EditScalarRange.svg" alt="Scalar bar range" width="20"/> `Scalar Bar Range` | Set or adjust the numeric range used by rendered scalar bars. |

## Screenshot Workflow

`Screenshot to Clipboard` captures the currently rendered viewport and places it on the clipboard so it can be pasted into:

- reports
- presentations
- messages
- issue trackers

This action is intended for quick capture from the live plotter tab. If you need file-based export from Python, use the API-level export workflow instead.

## Scene Aids

The axes, origin axes, grid, and camera-orientation tools are best thought of as reading aids:

- `Axes` helps you stay oriented while rotating the model
- `Axes at Origin` is useful when the physical origin matters for the analysis
- `Grid` adds labeled reference axes around the view
- `Camera Orientation` gives you a compact interactive orientation widget

These toggles are especially useful when you are switching between isometric and orthogonal views.

## Block Visibility

The `Blocks` tool is available for multi-block datasets. It lets you show or hide individual blocks without rebuilding the plot.

This is useful when you want to:

- isolate one part of an assembly
- remove outer geometry temporarily
- compare a subset of blocks without losing the full field plot configuration

## Scalar Bars

The scalar-bar tools help you manage how scalar data is presented:

- `Scalar Bars` focuses on scalar-bar display and organization
- `Scalar Bar Range` focuses on the numeric range used for coloring

Manual range control is useful when you want consistent color interpretation across different time steps or across repeated screenshots.
