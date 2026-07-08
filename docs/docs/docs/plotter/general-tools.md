---
sidebar_position: 2
title: General Tools
---

The General Tools toolbar controls scene-wide display aids, export actions, and plot presentation. These actions do not change the underlying result data. Instead, they help you read, capture, annotate, and manage what is visible in the current viewport.

## Main Actions

| Control | Description |
| --- | --- |
| <img src="/pyemsi/img/Settings.svg" alt="Settings" width="20"/> `Settings` | Open the display settings for the current plot view. |
| <img src="/pyemsi/img/Save-as.svg" alt="Export" width="20"/> `Export` | Open the export menu for screenshots and time-step animations. |
| <img src="/pyemsi/img/Axes.svg" alt="Axes" width="20"/> `Axes` | Toggle the orientation axes widget. |
| <img src="/pyemsi/img/CenterAxes.svg" alt="Axes at origin" width="20"/> `Axes at Origin` | Toggle an axes actor placed at the model origin. |
| <img src="/pyemsi/img/Grid.svg" alt="Grid" width="20"/> `Grid` | Toggle the grid and labeled axes around the visible scene. |
| <img src="/pyemsi/img/CameraOrientation.svg" alt="Camera orientation" width="20"/> `Camera Orientation` | Toggle the interactive camera orientation widget. |
| <img src="/pyemsi/img/Blocks.svg" alt="Blocks" width="20"/> `Blocks` | Open block-visibility controls for multi-block results. |
| <img src="/pyemsi/img/EditScalarBar.svg" alt="Scalar bars" width="20"/> `Scalar Bars` | Open scalar-bar appearance controls. |
| <img src="/pyemsi/img/EditScalarRange.svg" alt="Scalar bar range" width="20"/> `Scalar Bar Range` | Set or adjust the numeric range used by rendered scalar bars. |

The `Export` menu contains four actions:

- `Screenshot to Clipboard`
- `Save Screenshot`
- `Save Video`
- `Save GIF`

## Export Actions

The export actions are intended for capture and presentation workflows:

- <img src="/pyemsi/img/Screenshot.svg" alt="Screenshot" width="20"/> `Screenshot to Clipboard` copies the current rendered viewport directly to the system clipboard.
- <img src="/pyemsi/img/Save.svg" alt="Save screenshot" width="20"/> `Save Screenshot` saves the current rendered viewport to a PNG file.
- <img src="/pyemsi/img/Save-as.svg" alt="Save video" width="20"/> `Save Video` exports all available time steps to an MP4 video file.
- <img src="/pyemsi/img/Image.svg" alt="Save GIF" width="20"/> `Save GIF` exports all available time steps to a GIF animation.

`Screenshot to Clipboard` is useful when you want to paste the current view directly into:

- reports
- presentations
- messages
- issue trackers

`Save Screenshot` is useful when you want a file-based image export from the live plotter tab without leaving the viewer.

## Animation Export

`Save Video` and `Save GIF` are available for time-aware datasets that have valid time steps. If the loaded result is static, animation export cannot run.

When you export an animation, the plotter:

- pauses the current playback state
- processes each time step in sequence
- writes one frame for each time step
- restores the original active frame after the export completes

If you omit the file extension, the viewer adds `.mp4` for video export and `.gif` for GIF export automatically.

The suggested output filename is derived from the current plot or tab title. When the file explorer has a current directory, that directory is used as the default save location.

### Save Video

The `Save Video` dialog writes an MP4 animation and includes these fields:

- `Output file`: destination path for the exported video
- `Framerate`: playback rate in frames per second, default `4`
- `Quality`: video quality setting, default `5`

Use video export when you want a presentation-friendly animation or a file that is easy to share outside the application.

### Save GIF

The `Save GIF` dialog writes an animated GIF and includes these fields:

- `Output file`: destination path for the exported GIF
- `FPS`: playback rate in frames per second, default `10.0`
- `Loop count`: number of repeat loops, default `0`
- `Palette size`: maximum palette size used for GIF color reduction, default `256`
- `Subrectangles`: GIF subrectangle optimization, default `off`

With the default `Loop count` of `0`, most GIF viewers will loop the animation continuously.

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

Manual range control is useful when you want consistent color interpretation across different time steps or across repeated screenshot and animation exports.
