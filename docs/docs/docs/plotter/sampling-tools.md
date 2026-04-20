---
sidebar_position: 4
title: Sampling Tools
---

The Sampling Tools toolbar is used when you need numeric results from the plotted field, not just a visual impression. It combines direct point and cell queries with interactive picking and path-based sampling tools.

This toolbar is shown on the left side of the plotter window.

## Available Tools

| Control | Description |
| --- | --- |
| <img src="/pyemsi/img/QueryCell.svg" alt="Cell query" width="20"/> `Cell Query` | Open the cell-query dialog. |
| <img src="/pyemsi/img/QueryPoint.svg" alt="Point query" width="20"/> `Point Query` | Open the point-query dialog. |
| <img src="/pyemsi/img/PickPoint.svg" alt="Pick point" width="20"/> `Pick Point` | Toggle interactive point-picking mode with result history. |
| <img src="/pyemsi/img/PickCell.svg" alt="Pick cell" width="20"/> `Pick Cell` | Toggle interactive cell-picking mode with result history. |
| <img src="/pyemsi/img/SampleLine.svg" alt="Sample lines" width="20"/> `Sample Lines` | Open the line-sampling dialog. |
| <img src="/pyemsi/img/SampleArc.svg" alt="Sample arcs" width="20"/> `Sample Arcs` | Open the arc-sampling dialog. |

## Point And Cell Queries

Use the query dialogs when you already know which point ID or cell ID you want to inspect.

These tools are appropriate when you want to:

- read values at a specific point or element
- inspect one location across time
- compare exact data between two known mesh entities

The interactive `Pick Point` and `Pick Cell` modes are better when you want to discover values directly from the rendered model instead of typing IDs manually.

<div style={{ width: '100%', aspectRatio: '16 / 9' }}>
	<iframe
		style={{ width: '100%', height: '100%' }}
		src="https://www.youtube.com/embed/vTnrH5lS4hs"
		title="Query Point demo"
		frameBorder="0"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
		allowFullScreen>
	</iframe>
</div>

<div style={{ width: '100%', aspectRatio: '16 / 9', marginTop: '1rem' }}>
	<iframe
		style={{ width: '100%', height: '100%' }}
		src="https://www.youtube.com/embed/NYeOETxjXKE"
		title="Query Cell demo"
		frameBorder="0"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
		allowFullScreen>
	</iframe>
</div>

## Interactive Picking

`Pick Point` and `Pick Cell` turn the viewport into an interactive inspection surface.

These modes are useful when:

- you do not know the point or cell ID in advance
- you want to click through several locations quickly
- you want a history of inspected picks while exploring the scene

Because these tools work directly from the rendered plot, they pair well with the camera controls and scene aids described in the other plotter pages.

<div style={{ width: '100%', aspectRatio: '16 / 9' }}>
	<iframe
		style={{ width: '100%', height: '100%' }}
		src="https://www.youtube.com/embed/xHQvO7twhe4"
		title="Pick Point demo"
		frameBorder="0"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
		allowFullScreen>
	</iframe>
</div>

<div style={{ width: '100%', aspectRatio: '16 / 9', marginTop: '1rem' }}>
	<iframe
		style={{ width: '100%', height: '100%' }}
		src="https://www.youtube.com/embed/qLTrZqtcsGI"
		title="Pick Cell demo"
		frameBorder="0"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
		allowFullScreen>
	</iframe>
</div>

## Sample Lines

`Sample Lines` opens a dedicated non-modal dialog for defining one or more line probes.

The dialog includes:

- an `Add New Line` button
- a table of defined lines
- `Run Sampling`, `Edit Selected`, `Remove Selected`, and `Clear` actions
- a results area that is populated after sampling runs

Each defined line is also visualized in the 3D view, which makes it easier to confirm the sampled path before running the calculation.

When sampling runs, pyemsi shows progress and allows cancellation.

<div style={{ width: '100%', aspectRatio: '16 / 9', marginTop: '1rem' }}>
	<iframe
		style={{ width: '100%', height: '100%' }}
		src="https://www.youtube.com/embed/CUK8ai62bQo"
		title="Sample Lines demo"
		frameBorder="0"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
		allowFullScreen>
	</iframe>
</div>

## Sample Arcs

`Sample Arcs` opens a similar dialog for curved probe paths defined by point A, point B, center, and resolution.

Like the line workflow, the arc dialog:

- lets you add, edit, and remove probe definitions
- visualizes the arc in the 3D scene
- runs sampling across the defined paths
- displays the returned results in a tabbed interface

Arc definitions are validated before acceptance so invalid geometry can be corrected before the sample is run.

<div style={{ width: '100%', aspectRatio: '16 / 9', marginTop: '1rem' }}>
	<iframe
		style={{ width: '100%', height: '100%' }}
		src="https://www.youtube.com/embed/rqM5y8YSZ3k"
		title="Sample Arcs demo"
		frameBorder="0"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
		allowFullScreen>
	</iframe>
</div>

## When To Use Sampling Instead Of Querying

Use querying when you need values at one exact mesh entity.

Use sampling when you need values distributed along a path, for example to inspect:

- variation through a gap or thickness
- changes along a radial or axial direction
- how a field evolves over both time and distance along a defined probe
