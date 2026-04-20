---
sidebar_position: 1
title: Time Control
---

The Time Control toolbar is used to inspect transient results frame by frame. It is most useful when the plotted dataset comes from a time-aware source such as a `.pvd` result collection.

If the loaded result is static, these controls are either inactive in practice or have no meaningful effect on the scene.

## What The Toolbar Does

The toolbar lets you move through the available time steps, start playback, reverse playback, and choose a specific frame directly from the time selector.

| Control | Description |
| --- | --- |
| <img src="/pyemsi/img/First.svg" alt="First frame" width="20"/> `First Frame` | Jump to the first time step. |
| <img src="/pyemsi/img/Back.svg" alt="Back animation" width="20"/> `Back Animation` | Step backward by one frame. |
| <img src="/pyemsi/img/Reverse.svg" alt="Reverse animation" width="20"/> `Reverse Animation` | Start continuous playback in reverse. |
| <img src="/pyemsi/img/Pause.svg" alt="Pause animation" width="20"/> `Pause Animation` | Pause playback and keep the current frame visible. |
| <img src="/pyemsi/img/Play.svg" alt="Play animation" width="20"/> `Play Animation` | Start continuous forward playback. |
| <img src="/pyemsi/img/Forward.svg" alt="Forward animation" width="20"/> `Forward Animation` | Step forward by one frame. |
| <img src="/pyemsi/img/Last.svg" alt="Last frame" width="20"/> `Last Frame` | Jump to the last time step. |
| <img src="/pyemsi/img/Loop.svg" alt="Loop animation" width="20"/> `Loop Animation` | Toggle looping so playback wraps instead of stopping at the end. |
| Time combobox | Select a frame directly by index and time value. |

## Playback Behavior

- Forward and backward stepping stop at the dataset boundaries.
- Continuous playback also stops at the first or last frame unless looping is enabled.
- The toolbar uses a single active transport state, so play, reverse, and pause behave as mutually exclusive playback modes.

This makes it easy to tell whether the plot is currently playing, reversing, or paused.

## Time Selector

The combobox at the end of the toolbar shows each available frame as an index paired with its time value.

Use it when:

- you want to jump to an exact time step instead of stepping repeatedly
- you need to compare a few known frames
- you are reviewing transient behavior at a specific time value

## Typical Uses

Use the time controls when you want to:

- inspect how a scalar field evolves during a simulation
- compare vector or contour behavior across time steps
- stop at a representative frame before taking a screenshot
- scrub through a transient result before running a point, cell, or line sample
