---
sidebar_position: 4
title: Plotter
---
The Plotter tab is pyemsi's interactive 3D field-view workspace. It opens after you create a field view from the <img src="/pyemsi/img/Field.svg" alt="Field icon" width="20"/> [Field Plot dialog](../basics/field-plot.md) and is used to inspect geometry, scalar fields, contours, vectors, time-dependent results, and sampled data inside the main application.

If you are looking for the Python API behind this view, see [Plotter](/docs/api/Plotter).

<img src="/pyemsi/img/plotter-screenshot.png" alt="Plotter tab screenshot" width="700" />

## How You Get Here

The Plotter tab is typically the final step in the field-plot workflow:

1. Convert EMSolution or FEMAP results to VTK output.
2. Open the [Field Plot dialog](../basics/field-plot.md).
3. Configure one or more plot stages such as scalar, contour, vector, or feature edges.
4. Click `Plot` to open the interactive view.

Once the tab is open, you can continue inspecting the result without rerunning the plot builder for every camera, display, or sampling change.

## Plotter Layout

The Plotter tab combines the rendered viewport with several toolbars:

- a top animation toolbar for time-step navigation
- a top display toolbar for screenshots, axes, grids, scalar bars, and block visibility
- a left camera toolbar for standard views and camera reset
- a left query toolbar for point and cell queries, picking, and line or arc sampling

This layout keeps the main viewport focused on the model while still exposing the most common inspection tools directly in the tab.

## Common Workflow

1. Use the time controls if the loaded dataset is a transient result such as a `.pvd` time series.
2. Turn on display aids such as axes, grid lines, or camera orientation if they help you read the model.
3. Choose a standard camera direction or reset the camera to reframe the scene.
4. Query or sample the mesh when you need numeric values instead of only visual inspection.
5. Copy a screenshot to the clipboard when you need to paste the current view into notes, reports, or messages.

## Plotter Guides

Use the pages below for the main plotter tool groups:

- [Time Control](./time-control.md) for frame stepping, playback, looping, and direct time-step selection
- [General Tools](./general-tools.md) for screenshots, scene aids, block visibility, and scalar-bar controls
- [Camera Control](./camera-control.md) for reset, isometric, and orthogonal view shortcuts
- [Sampling Tools](./sampling-tools.md) for point and cell queries, pick modes, and line or arc sampling dialogs

## Notes

- Time controls are most relevant for time-aware datasets such as `.pvd` result collections.
- Block visibility controls are only available when the loaded result is a multi-block dataset.
- Sampling and query tools complement the visual plot by giving you direct numeric access to the data behind the rendered scene.

:::note[Suggested screenshots]
Useful follow-up images for this section would be close-up captures of the top toolbars and the left-side toolbars with callouts for each major group.
:::