---
title: plotter
sidebar_position: 11
---

The underlying plotter instance used for all rendering. Created during `Plotter` initialization.

- Desktop mode: [`pyvistaqt.QtInteractor`](https://qtdocs.pyvista.org/api_reference.html#pyvistaqt.QtInteractor)
- Notebook mode: [`pyvista.Plotter`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter)

:::info[Type]
- [`QtInteractor`](https://qtdocs.pyvista.org/api_reference.html#pyvistaqt.QtInteractor) | [`pyvista.Plotter`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter)
:::

You can use this attribute to access the full PyVista/Qt API directly — anything not exposed by `pyemsi.Plotter` can be done through `p.plotter`.

## Useful PyVista helpers

### Camera

| Method | Description |
|---|---|
| [`view_xy()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.view_xy) | Look down the Z axis (XY plane). Common for 2D cross-sections. |
| [`view_xz()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.view_xz) | Look down the Y axis (XZ plane). |
| [`view_yz()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.view_yz) | Look down the X axis (YZ plane). |
| [`view_isometric()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.view_isometric) | Reset to a default isometric view. |
| [`view_vector(vector)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.view_vector) | Point the camera in an arbitrary direction. |
| [`reset_camera()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.reset_camera) | Reset the camera to fit all visible actors. |
| [`set_position(point)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.set_position) | Set the camera position. |
| [`camera_position`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.camera_position) | Get or set the full camera position. |
| [`enable_parallel_projection()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.enable_parallel_projection) | Switch to orthographic (parallel) projection. |
| [`zoom_camera(value)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.zoom_camera) | Zoom in or out. |

### Rendering & appearance

| Method | Description |
|---|---|
| [`add_mesh(mesh, ...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_mesh) | Add any PyVista/VTK mesh or dataset to the scene. |
| [`remove_actor(actor)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.remove_actor) | Remove an actor from the scene. |
| [`set_background(color)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.set_background) | Set the background color. |
| [`add_scalar_bar(...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_scalar_bar) | Add or customise a scalar bar. |
| [`update_scalar_bar_range(clim)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.update_scalar_bar_range) | Change the color range of the active scalar bar. |
| [`add_text(text, ...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_text) | Add a text annotation to the scene. |
| [`add_axes(...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_axes) | Add an interactive axes orientation widget. |
| [`show_grid()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.show_grid) | Show grid lines and axis labels. |
| [`add_bounding_box(...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_bounding_box) | Add a bounding box outline. |
| [`enable_anti_aliasing()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.enable_anti_aliasing) | Enable anti-aliasing for smoother edges. |
| [`enable_depth_peeling()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.enable_depth_peeling) | Improve rendering of translucent geometry. |

### Export & screenshot

| Method | Description |
|---|---|
| [`screenshot(filename, ...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.screenshot) | Take a screenshot at the current camera position. |
| [`export_html(filename)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.export_html) | Export the scene as an interactive HTML file. |
| [`export_gltf(filename)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.export_gltf) | Export as a glTF 3D file. |
| [`open_movie(filename)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.open_movie) | Open a video file for frame-by-frame recording. |
| [`write_frame()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.write_frame) | Write a single frame to the open video file. |

### Annotations & widgets

| Method | Description |
|---|---|
| [`add_point_labels(points, labels, ...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_point_labels) | Label points with text. |
| [`add_legend(labels, ...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_legend) | Add a legend to the render window. |
| [`add_ruler(pointa, pointb, ...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_ruler) | Add a ruler annotation between two points. |
| [`add_mesh_slice(mesh, ...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_mesh_slice) | Add an interactive slicing plane widget. |
| [`add_mesh_isovalue(mesh, ...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_mesh_isovalue) | Add an interactive isovalue/contour slider. |
| [`enable_point_picking(...)`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.enable_point_picking) | Enable interactive point picking. |

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.ipm_motor_path()
p = Plotter(file_path)
p.set_scalar("B-Mag (T)", scalar_bar_)

# Access the underlying plotter directly
p.plotter.view_xy()
p.plotter.set_background("black")
p.plotter.add_axes()

p.show()
```

<iframe
  src="/pyemsi/demos/plotter.html"
  style={{aspectRatio: "1.5"}}
/>