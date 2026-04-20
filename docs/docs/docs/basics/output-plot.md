---
sidebar_position: 5
title: Output Plot
---

The Output Plot tool is used to create waveform-style plots from EMSolution result files such as `output.json`.

It is intended for plotting scalar result data from EMSolution outputs, previewing the result inside the plot builder, and then opening the final figure in pyemsi.

## Two Ways To Open The Output Plot Builder

There are two ways to open the output-plot dialog.

### From The File Menu Or Toolbar

Use `File -> Output Plot`, or click the graph icon <img src="/pyemsi/img/Graph.svg" alt="Graph icon" width="20" /> on the main toolbar.

This route opens the plot builder for `output.json` in the current workspace.

### From An Open JSON Output Tab

Open `output.json`, or any other JSON file with the same EMSolution output structure, from the Explorer widget.

Then click the `Plot` button in that tab's toolbar. This opens the same output-plot builder dialog for the currently opened file.

This second route is useful when you want to plot a compatible file that is not the default `output.json` in the current workspace.

## Dialog Layout

The EMSolution output plot builder is organized into a left control area and a right preview area.

<img src="/pyemsi/img/output-plot-dialog.png" alt="output-dialog" width="700" />

### Left Side: Series And Subplots

The left side contains:

- a `Subplot` selector
- a `Delete Subplot` button
- a tree of available plot series

The tree is built from the available EMSolution result data and groups series by category. You can expand the tree, check the series you want to plot, and assign different series to different subplots.

When more than one subplot is needed, use the subplot selector to switch between them or choose `Add New Subplot...` to create another subplot.

### Right Side: Live Preview

The right side shows a live Matplotlib preview.

As you check series, change subplot assignments, or update settings, the preview is redrawn so you can inspect the figure before creating the final plot.

## Main Components

### Series Tree

The series tree is the main place where you choose what to draw.

- Check a leaf series to include it in the current subplot.
- Parent items are only used for grouping.
- Checked series can be styled individually.

When a series is checked, a style button appears beside it. That button opens the series-style editor.

### Series Style Editor

Each selected series can be customised with:

- label
- line style
- marker
- line width
- color

This makes it possible to refine the appearance of individual curves without leaving the dialog.

<img src="/pyemsi/img/series-style-dialog.png" alt="output-dialog" width="500" />

### Plot Settings Dialog

The `Plot Settings...` button opens a separate settings dialog for figure-wide options.

It includes:

- X-axis selection
- title and title visibility
- X and Y labels
- style preset
- legend location or disabling the legend
- grid configuration
- log scale for X and Y axes
- shared X-axis for multiple subplots

The style presets include standard Matplotlib styles and SciencePlots-based presets.

<img src="/pyemsi/img/plot-settings-dialog.png" alt="output-dialog" width="500" />

### Script Generation

The `Script...` button generates a Python script for the current plot configuration.

This is useful when you want to reproduce the figure outside the dialog, save the plotting workflow, or adapt it programmatically.

## Notes And Warnings

- If log scale is enabled, series with non-positive values are skipped and a warning is shown.
- If the selected plot style requires LaTeX and LaTeX is not installed, the dialog shows a warning and the figure cannot be plotted with that style until you choose a `(no-latex)` variant or install LaTeX.
- Plot settings are persisted so the dialog can remember previously used options.

## Result

After plotting, pyemsi creates a Matplotlib figure and opens it inside the GUI, so you can review the output plot alongside your other tabs and tools.