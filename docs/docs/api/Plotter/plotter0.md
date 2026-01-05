---
title: plotter
sidebar_position: 11
---

Underlying plotter instance used for rendering.

- Desktop mode: [`pyvistaqt.QtInteractor`](https://qtdocs.pyvista.org/api_reference.html#pyvistaqt.QtInteractor)
- Notebook mode: [`pyvista.Plotter`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter)

### Type

- [`QtInteractor`](https://qtdocs.pyvista.org/api_reference.html#pyvistaqt.QtInteractor) | [`pyvista.Plotter`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter)

### Notes

- Created during initialization.
- Use it to access PyVista helpers like [`view_xy()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.view_xy) or [`add_mesh()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_mesh).

### Example

```python
from pyemsi import Plotter

p = Plotter("mesh.vtm")
p.plotter.view_xy()
p.show()
```
