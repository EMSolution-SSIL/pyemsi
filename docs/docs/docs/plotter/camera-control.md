---
sidebar_position: 3
title: Camera Control
---

The Camera Control toolbar provides quick view shortcuts for reorienting the scene. It is designed for fast inspection rather than fine-grained manual camera editing.

This toolbar is placed on the left side of the plotter window so you can switch view direction without covering the main viewport.

## Available Views

| Control | Description |
| --- | --- |
| <img src="/pyemsi/img/ResetCamera.svg" alt="Reset camera" width="20"/> `Reset Camera` | Reframe the scene so visible objects fit in view. |
| <img src="/pyemsi/img/IsometricView.svg" alt="Isometric view" width="20"/> `Isometric` | Switch to a standard isometric view. |
| <img src="/pyemsi/img/ZPlus.svg" alt="Plus Z view" width="20"/> `+Z View` | View from the +Z axis. The tooltip labels this as `Right`. |
| <img src="/pyemsi/img/ZMinus.svg" alt="Minus Z view" width="20"/> `-Z View` | View from the -Z axis. The tooltip labels this as `Left`. |
| <img src="/pyemsi/img/YPlus.svg" alt="Plus Y view" width="20"/> `+Y View` | View from the +Y axis. The tooltip labels this as `Front`. |
| <img src="/pyemsi/img/YMinus.svg" alt="Minus Y view" width="20"/> `-Y View` | View from the -Y axis. The tooltip labels this as `Back`. |
| <img src="/pyemsi/img/XPlus.svg" alt="Plus X view" width="20"/> `+X View` | View from the +X axis. The tooltip labels this as `Top`. |
| <img src="/pyemsi/img/XMinus.svg" alt="Minus X view" width="20"/> `-X View` | View from the -X axis. The tooltip labels this as `Bottom`. |

## When To Use Reset Camera

Use `Reset Camera` after:

- hiding or showing blocks
- switching between very different time steps or plot stages
- adding overlays that make the current framing less useful
- losing the model while rotating manually

It is the fastest way to return to a readable full-scene view.

## When To Use Orthogonal Views

The axis-aligned view buttons are useful when you want to:

- inspect a known cross-section direction
- compare symmetry or alignment
- prepare a consistent screenshot series
- reduce perspective ambiguity before sampling or querying

If you are exploring the model for the first time, start from `Isometric`, then move to the orthogonal view that best matches the physical direction you want to inspect.
